import os
from flask import Flask, render_template, request, jsonify

from flaskr.db import get_db

def create_app(test_config=None):
     # Function to create and configure app
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_mapping(
        SECRET_KEY = os.getenv('NIHIRA_SECRET_KEY', default=None),
        DATABASE=os.path.join(app.instance_path, 'flaskr.sqlite'),
    )

    from . import db as db_helper
    db_helper.init_app(app)

    if test_config is None:
        app.config.from_pyfile('config.py', silent=True)
    else:
        app.config.from_mapping(test_config)

    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass


    @app.route('/')
    def index():
        return render_template('index.html')


    @app.route('/portfolio')
    def portfolio():
        return render_template('portfolio.html')


    @app.route('/hobbies')
    def hobbies():
        return render_template('hobbies.html')


    @app.route('/about', methods=['GET', 'POST'])
    def about():
        return render_template('about.html')

    @app.route('/write')
    def write():
        db = get_db()
        text_area = request.args.get('text_area').replace("<br>", "\n")
        file_id = request.args.get('id')
        db.execute("UPDATE entry SET data = ? WHERE id = ?", (text_area, file_id))
        db.commit()

        return jsonify(None)


    @app.route('/update')
    def update():
        def get_current_directory(c_dir, c_id):
            directory = db.execute("SELECT id, parent, name FROM entry WHERE name = ? AND id = ?",
                       (c_dir, c_id)).fetchone()
            return jsonify(list(directory)) if directory else None

        os.system('cls' if os.name == 'nt' else 'clear')

        db = get_db()
        current_directory = request.args.get('currentDirectory')
        user_input = request.args.get('terminalinput').split()
        args_length = len(user_input)
        current_id = request.args.get('currentId')
        command = user_input[0] if user_input else None

        if current_directory == "%2F":
            current_directory = "/"

        if command in ("cd", "mkdir", "touch", "rmdir", "rm", "code", "dl") and args_length == 2:
            return get_current_directory(current_directory, current_id)

        elif command in ("mv", "cp") and args_length == 3:
            return get_current_directory(current_directory, current_id)

        elif command == "ls" and args_length == 1:
            rows = db.execute("SELECT name, type FROM entry WHERE parent = ?",
                              (current_id, )).fetchall()
            rows = [list(row) for row in rows]

            return jsonify(rows)

        elif command == "echo":
            return ["success"]

        return jsonify(None)


    @app.route('/process')
    def process():
        def fetch_entry(args, p_id, c_id, root):
            by_id = "SELECT id, parent, name, type, data FROM entry WHERE id = ?"
            by_parent = "SELECT id, parent, name, type, data FROM entry WHERE name = ? AND parent = ?"

            if root == "/":
                p_id = None
                c_id = 1

            if args:
                if args[0] == "..":
                    query, params = by_id, (p_id,)
                elif args[0] == ".":
                    query, params = by_id, (c_id,)
                else:
                    query, params = by_parent, (args[0], c_id)
            else:
                return db.execute(by_id, (c_id,)).fetchone()

            entry_row = db.execute(query, params).fetchone()

            if len(args) > 1:
                for arg in args[1:]:
                    if not entry_row: break

                    if arg == "..":
                        query, params = by_id, (entry_row[1],)
                    elif arg == ".":
                        query, params = by_id, (entry_row[0],)
                    else:
                        query, params = by_parent, (arg, entry_row[0])

                    entry_row = db.execute(query, params).fetchone()

            return entry_row


        db = get_db()
        user_input = request.args.get('terminalinput').replace("%2F", "/").split()
        current_directory = request.args.get('currentDirectory')
        current_id = request.args.get('currentId')
        parent_id = request.args.get('parentId')
        command = user_input[0] if user_input else None

        arguments = list(filter(None, user_input[1].split("/"))) if len(user_input) == 2\
            else [list(filter(None, argument.split("/"))) for argument in user_input]

        if current_directory == "%2F":
            current_directory = "/"

        if  command == "cd":
            rows = fetch_entry(arguments, parent_id, current_id, user_input[1][0])
            if rows:
                return jsonify(list(rows))

        elif command in ("mkdir", "touch"):
            parent = current_id
            rows = fetch_entry(arguments, parent_id, current_id, user_input[1][0])
            file_type = "DIR" if command == "mkdir" else "FILE"

            if len(arguments) > 1:
                parent = (fetch_entry([arguments[-2]], parent_id, current_id, user_input[1][0]))[0]
                if arguments[-2] == current_directory:
                    parent = current_id

            if not rows and parent:
                db.execute("INSERT INTO entry (parent, name, type)"
                           "VALUES (?, ?, ?)",(parent, arguments[-1], file_type))
                db.commit()
                return jsonify("success")

        elif command == "mv":
            entry_to_move = fetch_entry(arguments[1], parent_id, current_id, user_input[1][0])
            specified_directory = fetch_entry(arguments[2], parent_id, current_id, user_input[1][0])

            if entry_to_move:
                if not specified_directory and len(arguments[2]) == 1:
                    db.execute("UPDATE entry SET name = ? WHERE id = ?", (arguments[2][0], entry_to_move[0]))
                    db.commit()
                    return jsonify("success")

                else:
                    if specified_directory[3] == "DIR":
                        # Checks if name similar exists name first before moving
                        rows = db.execute("SELECT name FROM entry WHERE name = ? AND parent = ?",
                                          (entry_to_move[2], specified_directory[0])).fetchone()
                        # Also check if moving parent to a children
                        if not rows and entry_to_move[0] != specified_directory[1]:
                            db.execute("UPDATE entry SET parent = ? WHERE id = ?",
                                       (specified_directory[0], entry_to_move[0]))
                            db.commit()
                            return jsonify("success")


        elif command == "cp":
            entry_to_copy = fetch_entry(arguments[1], parent_id, current_id, user_input[1][0])
            specified_directory = fetch_entry(arguments[2], parent_id, current_id, user_input[1][0])

            if entry_to_copy and specified_directory:
                if specified_directory[3] == "DIR":
                    # Checks if name similar exists name first before copying
                    rows = db.execute("SELECT name FROM entry WHERE name = ? AND parent = ?",
                                      (entry_to_copy[2], specified_directory[0])).fetchone()
                    if not rows and entry_to_copy[0] != specified_directory[1]:
                        db.execute("INSERT INTO entry (parent, name, type) VALUES (?, ?, ?)",
                                   (specified_directory[0], entry_to_copy[2], entry_to_copy[3]))
                        db.commit()
                        return ["success"]


        elif command in ("rm", "rmdir"):
            rows = fetch_entry(arguments, parent_id, current_id, user_input[1][0])
            file_type = "DIR" if command == "rmdir" else "FILE"

            if rows:
                if (rows[3] == 'DIR' and command == "rm") or (rows[3] == 'FILE' and command == "rmdir"):
                    return jsonify(None)
                db.execute("DELETE FROM entry WHERE id = ? AND type = ?", (rows[0], file_type ))
                db.execute("DELETE FROM entry WHERE parent = ?", (rows[0], ))
                db.commit()
                return ["success"]

        elif command in ("code", "dl"):
            rows = fetch_entry(arguments, parent_id, current_id, user_input[1][0])
            if rows and rows[3] == 'FILE':
                return jsonify(list(rows))

        return jsonify(None)

    return app