#!/usr/bin/env python

"""
Simple script converting twitter json export to sqlite database, with some basic post processing
License : MIT
Author  : Piotr Czarny
"""
import sys
import sqlite3
import json
import glob
import time

def create_database(database_cursor):
    """ Create database tables to store tweets """

    database_cursor.execute(""" CREATE TABLE IF NOT EXISTS tweets(

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

def parse_file(database, database_cursor, file_name):
    """ Parse JSON file and put parset results into SQLite DB """
    file_name_without_ext = file_name[file_name.rfind('/') + 1:file_name.rfind('.')]

    with file(file_name) as json_file:
        json_str = json_file.read()

    json_str = json_str.replace('Grailbird.data.tweets_' + file_name_without_ext + ' = ', '')
    json_obj = json.loads(json_str)

    for data in json_obj:
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

        database_cursor.execute(""" INSERT INTO tweets (
            id, id_str, text, created_at, in_reply_to_status_id, in_reply_to_status_id_str, in_reply_to_user_id, in_reply_to_user_id_str, in_reply_to_screen_name, source, source_parsed
        )
        VALUES(?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""", tweets_obj)

        try:
            database.commit()
        except sqlite3.Error:
            print 'sqlite database.commit exception, sleeping and continuing'
            time.sleep(1)
            continue

def parse_dir(database, database_cursor, dir_name):
    """ Iterate through json files in chosen directory """
    for file_name in glob.glob(dir_name + '*.js'):
        file_name = file_name.replace('\\', '/')
        print 'Parsing ' + file_name
        parse_file(database, database_cursor, file_name)

def main():
    """ Main method """

    database = sqlite3.connect('tweets.sqlite')
    database_cursor = database.cursor()

    data_dir = 'tweets/data/js/tweets/'

    create_database(database_cursor)
    parse_dir(database, database_cursor, data_dir)
    #parse_file(database, database_cursor, dataDir + '/2012_11.js')




if __name__ == "__main__":
    sys.exit(main())
