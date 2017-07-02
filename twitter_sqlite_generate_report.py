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
from abc import ABCMeta, abstractmethod
from timeit import timeit
from pprint import pprint
import pygal
from mako.template import Template


class Output(object):
    """ Abstract class base for output classes """
    __metaclass__ = ABCMeta

    @abstractmethod
    def render(self, data):
        """ Render passed data """
        pass


class HTMLOutput(Output):
    """ HTML output renderer, using Mako templates """

    def render(self, data):
        """ Render HTML file """
        mako_template = Template(filename='html_template.mako', module_directory='tmp/')
        return mako_template.render_unicode(**data)


class TwitterStatsGenerator(object):
    """ Class which generates statistics from Twitter SQLite file """
    def __init__(self, database_filename='tweets.sqlite', output_renderer_cls=HTMLOutput):
        self.database = sqlite3.connect(database_filename)
        self.database_cursor = self.database.cursor()
        self.output_renderer_cls = output_renderer_cls
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
        first_year = None
        last_year = None

        for row in self.database_cursor.fetchall():
            if not first_year:
                first_year = int(row[1])
            last_year = int(row[1])

            to_return[int(row[1])] = row[0]

        # if year is not found, we need to fill its data with zeros
        for year in xrange(first_year, last_year + 1):
            if year not in to_return:
                to_return[year] = 0

        return to_return

    def _query_total_tweets_per_year_month(self):
        self.database_cursor.execute("""SELECT COUNT(*) AS count, year, month
                                        FROM tweets_parsed_time
                                        GROUP BY year, month""")
        to_return = {}
        first_year = None
        last_year = None

        for row in self.database_cursor.fetchall():
            if not first_year:
                first_year = int(row[1])
            last_year = int(row[1])

            if int(row[1]) not in to_return:
                to_return[int(row[1])] = {}
            to_return[int(row[1])][int(row[2])] = row[0]

        # if year is not found, we need to fill its data with zeros for each month
        for year in xrange(first_year, last_year + 1):
            if year not in to_return:
                to_return[year] = {}
            for month in xrange(1, 13):
                if month not in to_return[year]:
                    to_return[year][month] = 0


        return to_return

    def query(self):
        """ Generate dictionary with query output """
        to_return = {}
        to_return['tweet_count_total'] = self._query_total_tweets()
        to_return['tweet_count_per_year'] = self._query_total_tweets_per_year()
        to_return['tweet_count_per_year_month'] = self._query_total_tweets_per_year_month()
        return to_return

    def render(self):
        """ Render output statistics file using chosen renderer """
        data = self.query()
        pprint(data) # debug only
        render_op = getattr(self.output_renderer_cls, "render", None)
        if callable(render_op):
            output = self.output_renderer_cls().render(data)
            # debug only
            print output
            with open('output.html', 'w') as output_file:
                output_file.write(output)


def main():
    """ Main method """
    print timeit(lambda: TwitterStatsGenerator(output_renderer_cls=HTMLOutput).render(), number=1)

if __name__ == "__main__":
    sys.exit(main())
