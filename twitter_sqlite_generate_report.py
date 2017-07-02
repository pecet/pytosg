#!/usr/bin/env python

"""
Generate statistics from previously generated twitter SQLite file
Typically you want to run twitter_json_to_sqlite.py script first
License : MIT
Author  : Piotr Czarny
"""

import sys
import sqlite3
import json
import glob
import time
import collections
import mako
import pygal
from timeit import timeit
from pprint import pprint

class TwitterStatsGenerator(object):
    """ Class which generates statistics from Twitter SQLite file """
    def __init__(self, database_filename='tweets.sqlite'):
        self.database = sqlite3.connect(database_filename)
        self.database_cursor = self.database.cursor()
        if not self._check_if_tables_exists():
            raise Exception('Required database tables are not present in {0} file'.
                            format(database_filename))

    def __del__(self):
        if self.database:
            self.database.close()
            self.database = None

    def _check_if_tables_exists(self):
        """ Basic check if required tables exists in SQLite file,
        does not care about table structure though """
        required_tables = ['tweets', 'tweet_replies', 'tweet_hashtags',
                           'tweet_words', 'tweets_parsed_time']
        for table in required_tables:
            self.database_cursor.execute("""SELECT name FROM sqlite_master
                                            WHERE name=? AND tbl_name=?""", (table, table))
            if not self.database_cursor.fetchone():
                return False

        return True

    def _query_total_tweets(self):
        self.database_cursor.execute("""SELECT COUNT(*) AS count FROM tweets""")
        return self.database_cursor.fetchone()[0]

    def _query_total_tweets_per_year(self):
        self.database_cursor.execute("""SELECT COUNT(*) AS count, year
                                        FROM tweets_parsed_time
                                        GROUP BY year""")
        to_return = {}
        for row in self.database_cursor.fetchall():
            to_return[int(row[1])] = row[0]
        return to_return

    def _query_total_tweets_per_year_month(self):
        self.database_cursor.execute("""SELECT COUNT(*) AS count, year, month
                                        FROM tweets_parsed_time
                                        GROUP BY year, month""")
        to_return = {}
        for row in self.database_cursor.fetchall():
            if int(row[1]) not in to_return:
                to_return[int(row[1])] = {}
            to_return[int(row[1])][int(row[2])] = row[0]
        return to_return

    def query(self):
        """ Do queries and stuff """
        to_return = {}
        to_return['tweet_count_total'] = self._query_total_tweets()
        to_return['tweet_count_per_year'] = self._query_total_tweets_per_year()
        to_return['tweet_count_per_year_moth'] = self._query_total_tweets_per_year_month()
        return to_return


def main():
    """ Main method """
    print timeit(lambda: pprint(TwitterStatsGenerator().query()), number=1)

if __name__ == "__main__":
    sys.exit(main())
