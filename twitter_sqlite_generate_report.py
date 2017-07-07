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
from collections import OrderedDict
from abc import ABCMeta, abstractmethod
from timeit import timeit
from pprint import pprint
import pygal
from mako.template import Template

class LazyDict(dict):
    """ Simple implementation of dictionary which lazily compute values for its keys
        when they are accessed

        Note: calling repr function on LazyDict object does not compute any values

        Usage:
            mydict = LazyDict()
            mydict['value'] = zero_argument_function
    """

    def __init__(self):
        self._computed_dict = {} # already computed dict keys
        super(LazyDict, self).__init__(self)

    def __setitem__(self, key, value):
        if callable(value):
            super(LazyDict, self).__setitem__(key, value)
        else:
            raise Exception('Supplied dictionary key is not callable')

    def __repr__(self):
        repr_str = '{'
        for key, value in super(LazyDict, self).iteritems():

            value_or_not_computed = 'NOT_COMPUTED' + repr(value)
            if self.is_computed(key):
                value_or_not_computed = repr(self._computed_dict[key])
            repr_str += repr(key) + ": " + value_or_not_computed + ", "

        if len(repr_str) > 2:
            return repr_str[:-2] + '}'
        return '{}'


    def __getitem__(self, key):
        if self.is_computed(key):
            return self._computed_dict[key]
        else:
            func = super(LazyDict, self).__getitem__(key)
            func_value = func() # callability already checked in __setitem__
            self._computed_dict[key] = func_value
            return func_value

    def is_computed(self, key):
        """ Returns True if value for key is already computed
            or False if value for key is not computed """

        return self._computed_dict.has_key(key)


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
        return mako_template.render_unicode(d=data)


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
        to_return = OrderedDict()
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
        to_return = OrderedDict()
        first_year = None
        last_year = None

        for row in self.database_cursor.fetchall():
            if not first_year:
                first_year = int(row[1])
            last_year = int(row[1])

            if int(row[1]) not in to_return:
                to_return[int(row[1])] = OrderedDict()
            to_return[int(row[1])][int(row[2])] = row[0]

        # if year is not found, we need to fill its data with zeros for each month
        for year in xrange(first_year, last_year + 1):
            if year not in to_return:
                to_return[year] = OrderedDict()
            for month in xrange(1, 13):
                if month not in to_return[year]:
                    to_return[year][month] = 0

        return to_return

    def _query_total_tweets_per_month(self):
        self.database_cursor.execute("""SELECT COUNT(*) AS count, month
                                        FROM tweets_parsed_time
                                        GROUP BY month""")
        to_return = OrderedDict()

        for row in self.database_cursor.fetchall():
            to_return[int(row[1])] = row[0]

        # if month is not found, we need to fill its data with zeros
        for month in xrange(1, 13):
            if month not in to_return:
                to_return[month] = 0

        return to_return


    def query(self):
        """ Generate dictionary with query output """
        to_return = LazyDict()
        to_return['tweet_count_total'] = self._query_total_tweets
        to_return['tweet_count_per_year'] = self._query_total_tweets_per_year
        to_return['tweet_count_per_year_month'] = self._query_total_tweets_per_year_month
        to_return['tweet_count_per_month'] = self._query_total_tweets_per_month
        return to_return

    def render(self, output_renderer_cls=HTMLOutput):
        """ Render output statistics file using chosen renderer """
        data = self.query()
        pprint(data) # debug only
        render_op = getattr(output_renderer_cls, "render", None)
        if callable(render_op):
            output = output_renderer_cls().render(data)
            # debug only
            # print output
            with open('output.html', 'w') as output_file:
                output_file.write(output)

            pprint(data) # debug only, we should have here values used in template computed
            # using lazy loader


def main():
    """ Main method """
    # TODO: add unit tests
    #dtest = LazyDict()
    #dtest["A"] = lambda: 10
    #dtest["B"] = lambda: 20
    #pprint(dtest)
    #print(dtest)
    #pprint(dtest["B"])
    #pprint(dtest["B"])
    #pprint(dtest)
    #sys.exit(0)
    print timeit(lambda: TwitterStatsGenerator().render(output_renderer_cls=HTMLOutput), number=1)

if __name__ == "__main__":
    sys.exit(main())
