import sqlite3

DB_FILE = "../../data/prg_msg.db"

TABLES = ["gen_messages", "rand_messages"]


def replace_name(conn, user, tables):
    """
    Replace all mentions with the form <@user_id> with user_name in 
    both rand_messages and gen_messages
    """
    cur = conn.cursor()
    for table in tables:
        sql = (f"UPDATE {table} "
               "SET msg_text = REPLACE(msg_text, ?, ?);")

        cur.execute(sql, (f"<@{user[0]}>", user[1]))


def remove_all_tags(conn, tables):
    """
    Remove all strings that match  <*> from both rand_messages and gen_messages
    """
    cur = conn.cursor()
    for table in tables:
        sql = (f"UPDATE {table} "
               "SET msg_text = SUBSTR(msg_text, 1, INSTR(msg_text, '<') - 1) || "
               "SUBSTR(msg_text, INSTR(msg_text, '>') + 1) "
               "WHERE msg_text LIKE '%<%>%'")

        cur.execute(sql)


conn = sqlite3.connect(DB_FILE)
with conn:
    cur = conn.cursor()
    cur.execute("SELECT * FROM users")

    rows = cur.fetchall()

    for row in rows:
        replace_name(conn, row, TABLES)

    remove_all_tags(conn, TABLES)
    conn.commit()
