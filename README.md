# postMark WebPageTerminal
#### Video Demo: [URL HERE](https://youtu.be/95tFD5UlWUw)
### PROBABLY live in here: https://nihira-web-terminal.onrender.com/
#### Description: A terminal in a webpage made using flask, sqlite and javascript

## What this project is about

This project simulates a terminal similar to a bash terminal. The idea was to use flask paired with a data base so that it can save files and directories even after the user leaves. Although the project hasn't fully implemented the full capabilites of a well-built terminal, it does the standard functions needed to be productive in a terminnal.

I implemented all the commands I would need to call it a finished product and those would be the ability to create, read, navigate, and delete. Here are the code snippet for those commands:

```const commands = ["cd", "mkdir", "touch", "mv", "rm", "rmdir", "cp", "code", "dl"]```

```const output_commands = ["", "ls", "echo", "clear", "help"]```

There are alot of features I stll wish to add if given the time, like making multiple elements with 'mkdir' and 'touch'  in a single command and automatically renaming of copied file with the 'cp' command, but I'm very satisfied with what I've initially created as this was the vision I was going for starting out the project.

## Specific Details of Project

Contents of styles.css is completely written by me (UPDATE: NOT ANYMORE HAHA). Bootstrap was used for drop down in smaller sized screens in navigating pages.

This program uses two (2) routes for flask and two (2) fetch api for javascript to process output information.

The commands are processed by: (1) Get user input by fetch
(2) Flask with SQlite reads the command and gives back current directory with 'update' route (3) Retrieves and process with another fetch api (4) Flask and SQlite gives back another result (5) And finally, if Flask gives back something, javascripts output it on the web page.

Function and proper usage of commands can be listed down using help command, spitting out this info;

```
 cd [directory] | Change directory
 mkdir [filename] | Create a directory
 touch [filename] | Create a file
 mv [filename] [directory] | Move or rename a file
 cp [filename] [directory] | Copy a file to another directory
 rm [filename] | Remove a file
 rmdir [directory] | Remove a directory
 code [filename] | Write in a file
 dl [filename] | Download a file locally

 INFO COMMANDS:
 ls | List files of current directory
 echo | Echoes arguments
 clear | Clears
 help | me
```
