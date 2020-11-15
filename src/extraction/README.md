## Extraction
Scripts for extracting messages from slack and inserting them into a sqlite3 database.

* reset.sql - Use to drop any existing tables and create the required schemas in a 
sqlite database
* get_all - populate the tables by polling the slack api. Expects a file 
`<project root>/data/prg_msg.db` created with reset.sql to insert into. Needs a valid
slack token to be exported into the environment variable `SLACK_TOKEN`.
* clean_messages.py - clean up the gathered messages by replacing @mentions with user names
and deleting all other tag (`<*>`) enclosed text such as web links

## Example Usage:
```
$ pwd
<project_root>
$ touch data/prg_msg.db
$ sqlite3 data/prg_msg.db < src/extraction/reset.sql
$ export SLACK_TOKEN='<my_slack_token>'
$ python src/extraction/get_all.py
$ python src/extraction/clean_messages.py 
```
