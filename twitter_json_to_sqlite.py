#!/usr/bin/env python

"""
Simple script converting twitter json export to sqlite database, with some basic post processing
License : MIT
Author  : Piotr Czarny

TODO: Store parsed files in db, so next time parsing is started, we only parse new files
TODO: Also store db version or something in db, so we will force parsing if DB format is not current
      (after confirmation), or maybe in future we will migrate old db tables to new db format,
      via ALTER etc.
"""
import sys
import sqlite3
import json
import glob
import time
import collections

class TwitterJsonToSqliteConverter(object):
    """ Class which allows you to convert JSON files to SQlite db """
    def __init__(self, database_filename='tweets.sqlite'):
        self.database = sqlite3.connect(database_filename)
        self.database_cursor = self.database.cursor()
        self._create_database_tables()

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

            -- reply? - store replies got directly from JSON
            -- note that, if there are multiple users in reply only one will be included
            -- that is why we need separate tweet_replies table
            -- and that is why we need to parse tweet text itself
            -- however we still include what JSON directly returns in SQLite because why not?
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

        self.database_cursor.execute(""" CREATE TABLE IF NOT EXISTS tweet_replies(

            -- ids
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            tweet_id INTEGER NOT NULL,

            -- reply to?
            screen_name TEXT NOT NULL

        )
        """)

        self.database_cursor.execute(""" CREATE TABLE IF NOT EXISTS tweet_hashtags(

            -- ids
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            tweet_id INTEGER NOT NULL,
            hashtag TEXT NOT NULL

        )
        """)

        self.database_cursor.execute(""" CREATE TABLE IF NOT EXISTS tweet_words(

            -- ids
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            word TEXT NOT NULL,
            count INTEGER NOT NULL

        )
        """)

        self.database_cursor.execute(""" CREATE UNIQUE INDEX IF NOT EXISTS word_idx ON
        tweet_words(word) """)

        self.database_cursor.execute(""" CREATE VIEW IF NOT EXISTS tweets_parsed_time AS
        SELECT *,
            strftime('%Y', created_at) AS year,
            strftime('%m', created_at) AS month,
            strftime('%d', created_at) AS day,
            strftime('%H', created_at) AS hour,
            strftime('%M', created_at) AS minute,
            strftime('%w', created_at) AS day_of_week,
            strftime('%W', created_at) AS week_of_year,
            strftime('%j', created_at) AS day_of_year
        FROM tweets;
        """)


    @classmethod
    def _remove_interpunction(cls, input_str):
        chars_to_remove = '.,:;/'
        output_str = input_str
        for char in chars_to_remove:
            output_str = output_str.replace(char, '')
        return output_str

    @classmethod
    def _deep_parse_text(cls, input_str):
        mentions = []
        hashtags = []
        words = [] # regular words, excluding mentioned above
        for word in input_str.split(' '):
            word = cls._remove_interpunction(word.lower())
            if len(word) >= 2: # ignore very short words
                if word[0] == '@':
                    mentions.append(word[1:])
                elif word[0] == '#':
                    hashtags.append(word[1:])
                else:
                    words.append(word)

        return_type = collections.namedtuple('ParsedText', ['mentions', 'hashtags', 'words'])
        return return_type(mentions=mentions, hashtags=hashtags, words=words)

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
            if counter % 104 == 1 or counter == len(json_obj):
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
                          data.get('created_at').replace(' +0000', ''),
                          data.get('in_reply_to_status_id'),
                          data.get('in_reply_to_status_id_str'),
                          data.get('in_reply_to_user_id'),
                          data.get('in_reply_to_user_id_str'),
                          data.get('in_reply_to_screen_name'),
                          data.get('source'),
                          source_parsed
                         )

            parsed_text = self._deep_parse_text(data.get('text'))

            self.database_cursor.execute(""" INSERT INTO tweets (
                id, id_str, text, created_at, in_reply_to_status_id, in_reply_to_status_id_str, in_reply_to_user_id, in_reply_to_user_id_str, in_reply_to_screen_name, source, source_parsed
            )
            VALUES(?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""", tweets_obj)

            for mention in parsed_text.mentions:
                self.database_cursor.execute(""" INSERT INTO tweet_replies (
                    tweet_id, screen_name
                )
                VALUES (?, ?)
                """, (data.get('id'), mention))

            for hashtag in parsed_text.hashtags:
                self.database_cursor.execute(""" INSERT INTO tweet_hashtags (
                    tweet_id, hashtag
                )
                VALUES (?, ?)
                """, (data.get('id'), hashtag))

            # we cannot have all words in db, it does not make sense
            # instead we store word and word count
            # note that, because of that only getting word count from whole
            # parsing period is supported
            # TODO: maybe, separate word count for months, years etc?
            for word in parsed_text.words:
                self.database_cursor.execute(""" INSERT OR IGNORE INTO tweet_words (
                    word, count
                )
                VALUES (?, ?)
                """, (word, 0))

                self.database_cursor.execute(""" UPDATE OR IGNORE tweet_words
                SET count = count + 1 WHERE word = ?
                """, (word,))

            try:
                self.database.commit()
            except sqlite3.Error:
                print 'Possible sqlite database.commit exception, sleeping and continuing.'
                time.sleep(1)
                continue

    def parse_dir(self, dir_name):
        """ Iterate through JSON files in chosen directory and parse them """
        for file_name in glob.glob(dir_name + '*.js'):
            file_name = file_name.replace('\\', '/')
            print 'Parsing ' + file_name
            self.parse_file(file_name)

def main():
    """ Main method """
    data_dir = 'tweets/data/js/tweets/'
    TwitterJsonToSqliteConverter().parse_dir(data_dir)
    #TwitterJsonToSqliteConverter().parse_file('tweets/data/js/tweets/2016_11.js') #just for testing
    #TwitterJsonToSqliteConverter().parse_file('tweets/data/js/tweets/2008_04.js') #just for testing

if __name__ == "__main__":
    sys.exit(main())
