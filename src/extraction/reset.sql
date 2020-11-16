DROP TABLE IF EXISTS rand_messages;
DROP TABLE IF EXISTS gen_messages;
DROP TABLE IF EXISTS users;

CREATE TABLE users (
user_id TEXT PRIMARY KEY,
name TEXT NOT NULL,
first_name TEXT,
last_name TEXT);


CREATE TABLE rand_messages (
id INTEGER PRIMARY KEY,
user_id TEXT NOT NULL,
msg_text TEXT NOT NULL,
timestamp REAL NOT NULL, 
FOREIGN KEY (user_id) REFERENCES users(user_id));


CREATE TABLE gen_messages (
id INTEGER PRIMARY KEY,
user_id TEXT NOT NULL,
msg_text TEXT NOT NULL,
timestamp REAL NOT NULL,
FOREIGN KEY (user_id) REFERENCES users(user_id));
