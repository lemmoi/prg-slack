import json
import os
import sqlite3
import time

import requests

DB_FILE = "../../data/prg_msg.db"

PARAMS = {"limit": 200}

GENERAL_INFO = {"id": "C0L4L8S9Z",
                "table": "gen_messages"}

RANDOM_INFO = {"id": "C0L4NN11P",
               "table": "rand_messages"}


class Processor():
    """
    Base class for a processor. Stores the table and database connection
    """

    def __init__(self, table, conn):
        self.table = table
        self.conn = conn
        self.processed = 0

    def process(self, data):
        raise NotImplemented()


class UserProcessor(Processor):
    """
    Processor for users. Takes a user response dictionary and inserts them into
    the given table and connection. Keeps track of total users processed.
    """

    def process(self, data):
        for user in data['members']:
            self.insert_user(user)

        self.conn.commit()
        self.processed += len(data['members'])
        print(f"{self.processed}/? users processed for {self.table}")

    def insert_user(self, entry):
        # Try using the first/lst name if the set it, otherwise fall back
        # to the username
        if 'first_name' in entry['profile']:
            entry['first_name'] = entry['profile']['first_name']
            
            if 'last_name' in entry['profile']:
                entry['last_name'] = entry['profile']['last_name']
            else:
                entry['last_name'] = "" 

            sql = f"INSERT INTO {self.table} (user_id, name, first_name, last_name) VALUES (:id, :name, :first_name, :last_name);"
        else:
            sql = f"INSERT INTO {self.table} (user_id, name) VALUES (:id, :name);"
        cur = self.conn.cursor()
        cur.execute(sql, entry)


class MsgProcessor(Processor):
    """
    Processor for messages. Takes a message response dictionary and inserts them into
    the given table and connection. Keeps track of total messages processed.
    """

    def process(self, data):
        # insert each message
        for msg in data['messages']:
            self.insert_msg(msg)

        self.conn.commit()

        self.processed += len(data['messages'])
        print(f"{self.processed}/? messages processed for {self.table}")

    def insert_msg(self, entry):
        entry['ts'] = float(entry['ts'])

        # Unfortunately we can't use substitution syntax for table names,
        # so this is a less than ideal solution, but it will do
        sql = f"INSERT INTO {self.table} (user_id, msg_text, timestamp) VALUES (:user, :text, :ts);"

        # These types of messages are weird, so we just ignore them for now
        if 'subtype' not in entry or entry['subtype'] not in ['bot_message',
                                                              'file_comment']:
            cur = self.conn.cursor()
            cur.execute(sql, entry)


def fill_msgs(channel_info, params, conn):
    """
    Setup the url, parameters, and the processor for messages
    """
    url = r"https://slack.com/api/conversations.history"
    params['channel'] = channel_info["id"]

    processor = MsgProcessor(channel_info["table"], conn)
    send_request(url, params, processor)


def fill_users(params, conn):
    """
    Setup the url, parameters, and the processor for users 
    """
    url = r"https://slack.com/api/users.list"
    processor = UserProcessor("users", conn)
    send_request(url, params, processor)


def send_request(url, params, processor):
    """
    Given a url and parameters, keep requesting until no more data is recieved.
    Invoke the processor with the raw data for each individual request.
    """
    # Reset cursor to be safe
    params["cursor"] = ""
    is_more = True
    while is_more:
        # Send the request parameters and 
        r = requests.get(url=url, params=params)
        data = r.json()

        # if something went wrong, try again
        if not data["ok"]:
            continue

        # get the next cursor if there is one
        if "response_metadata" in data \
                and data["response_metadata"]["next_cursor"] != "":
            params["cursor"] = data["response_metadata"]["next_cursor"]
        else:
            is_more = False

        processor.process(data)
        time.sleep(1)


def main():
    # Load the slack token. This should be set in the environment variable
    # SLACK_TOKEN
    PARAMS['token'] = os.environ.get("SLACK_TOKEN")
    conn = sqlite3.connect(DB_FILE)
    fill_users(PARAMS, conn);
    fill_msgs(GENERAL_INFO, PARAMS, conn);
    fill_msgs(RANDOM_INFO, PARAMS, conn);


if __name__ == "__main__":
    main()
