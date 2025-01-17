DROP TABLE IF EXISTS entry;

CREATE TABLE entry (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    parent INTEGER DEFAULT NULL,
    name TEXT NOT NULL,
    type TEXT NOT NULL,
    data TEXT
);

INSERT INTO entry (name, type)
VALUES ('/', 'DIR');