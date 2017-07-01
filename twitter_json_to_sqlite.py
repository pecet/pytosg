#!/usr/bin/env python

"""
Simple script converting twitter json export to sqlite database, with some basic post processing
License : MIT
Author  : Piotr Czarny

TODO: Store parsed files in db, so next time parsing is started, we only parse new files
TODO: Also store db version or something in db, so we will force parsing if DB format is not current
      (after confirmation)
"""
import sys
import sqlite3
import json
import glob
import time

class TwitterJsonToSqliteConverter(object):
    """ Class which allows you to convert JSON files to SQlite db """
    def __init__(self, database_filename='tweets.sqlite'):
        self.database = sqlite3.connect(database_filename)
        self.database_cursor = self.database.cursor()

    def __del__(self):
        if self.database:
            self.database.close()
            self.database = None

    def _create_database_tables(self):
        """ Create database tables to store tweets """

        self.database_cursor.execute(""" CREATE TABLE IF NOT EXISTS tweets(

            -- ids
            id INTEGER PRIMARY KEY NOT NULL,
            id_str TEXT,

            -- main tweet content
            text TEXT,
            created_at TEXT,

            -- reply?
            in_reply_to_status_id INTEGER,
            in_reply_to_status_id_str TEXT,
            in_reply_to_user_id INTEGER,
            in_reply_to_user_id_str TEXT,
            in_reply_to_screen_name TEXT,

            -- link to source application (twitter client) with html tags
            source TEXT,
            -- source app only
            source_parsed TEXT

        )
        """)

    def parse_file(self, file_name):
        """ Parse JSON file and put parset results into SQLite DB """
        file_name_without_ext = file_name[file_name.rfind('/') + 1:file_name.rfind('.')]

        with file(file_name) as json_file:
            json_str = json_file.read()

        json_str = json_str.replace('Grailbird.data.tweets_' + file_name_without_ext + ' = ', '')
        json_obj = json.loads(json_str)

        counter = 0
        for data in json_obj:
            counter += 1
            if counter % 20 == 1 or counter == len(json_obj):
                print '      Parsed {0} of {1} tweets ({2}%)'.format(
                    counter, len(json_obj), round(float(counter) / float(len(json_obj)) * 100, 1)
                    )

            source_parsed = None
            if data.get('source'):
                source = data.get('source')
                source_left = source.find('>')
                source = source[source_left + 1:]
                source_right = source.find('<')
                source_parsed = source[:source_right]

            tweets_obj = (data.get('id'),
                          data.get('id_str'),
                          data.get('text'),
                          data.get('created_at'),
                          data.get('in_reply_to_status_id'),
                          data.get('in_reply_to_status_id_str'),
                          data.get('in_reply_to_user_id'),
                          data.get('in_reply_to_user_id_str'),
                          data.get('in_reply_to_screen_name'),
                          data.get('source'),
                          source_parsed
                         )

            self.database_cursor.execute(""" INSERT INTO tweets (
                id, id_str, text, created_at, in_reply_to_status_id, in_reply_to_status_id_str, in_reply_to_user_id, in_reply_to_user_id_str, in_reply_to_screen_name, source, source_parsed
            )
            VALUES(?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""", tweets_obj)

            try:
                self.database.commit()
            except sqlite3.Error:
                print 'Possible sqlite database.commit exception, sleeping and continuing.'
                time.sleep(1)
                continue

    def parse_dir(self, dir_name):
        """ Iterate through JSON files in chosen directory and parse them """
        self._create_database_tables()
        for file_name in glob.glob(dir_name + '*.js'):
            file_name = file_name.replace('\\', '/')
            print 'Parsing ' + file_name
            self.parse_file(file_name)

def main():
    """ Main method """
    data_dir = 'tweets/data/js/tweets/'
    TwitterJsonToSqliteConverter().parse_dir(data_dir)

if __name__ == "__main__":
    sys.exit(main())
