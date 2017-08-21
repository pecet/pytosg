""" Main module for generating Twitter stats from SQLite file """

import sqlite3
from collections import OrderedDict, MutableMapping
from pprint import pprint
from .Output import HTMLOutput
from .LazyDict import LazyDict

class TwitterStatsGenerator(object):
    """ Class which generates statistics from Twitter SQLite file """
    def __init__(self, database_filename='tweets.sqlite'):
        self.database = sqlite3.connect(database_filename)
        self.database.row_factory = sqlite3.Row # allow access to row values via names
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

    def _map(self, input_dict, values, mapping, use_ordered_dict = True):
        """ Add dictionary values to multi-level dict / OrderedDict """

        dict_key = values[mapping[0]]
        if len(mapping) == 2:
            dict_value = values[mapping[1]]
            input_dict[dict_key] = dict_value
        else:
            if not input_dict.has_key(dict_key):
                input_dict[dict_key] = OrderedDict() if use_ordered_dict else {}
            input_dict[dict_key] = self._map(input_dict[dict_key], values, mapping[1:])

        return input_dict

    def _select_query(self, table_name, to_select, group_by=None, order_by=None, mapping=None):
        # pack strings into tuples, as we will iterate through tuple/list later

        if isinstance(to_select, str):
            to_select = (to_select, )
        if isinstance(group_by, str):
            group_by = (group_by, )
        if isinstance(order_by, str):
            order_by = (order_by, )
        if isinstance(mapping, str):
            mapping = (mapping, )

        to_select_formatted = ','.join(to_select)
        group_by_formatted = ('GROUP BY ' + ','.join(group_by)) if group_by else ''
        order_by_formatted = ('ORDER BY ' + ','.join(order_by)) if order_by else ''

        query_string = """SELECT {to_select} FROM {table_name} {group_by} {order_by}""".format(
            table_name=table_name, to_select=to_select_formatted,
            group_by=group_by_formatted, order_by=order_by_formatted
            )

        to_return = OrderedDict()
        for row in self.database_cursor.execute(query_string):
            to_return = self._map(to_return, dict(row), mapping)

        return to_return


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

    def _query_total_tweets_per_day_of_week(self):
        self.database_cursor.execute("""SELECT COUNT(*) AS count, day_of_week
                                        FROM tweets_parsed_time
                                        GROUP BY day_of_week""")
        to_return = OrderedDict()

        for row in self.database_cursor.fetchall():
            to_return[int(row[1])] = row[0]

        # if day_of_week is not found, we need to fill its data with zeros
        for day_of_week in xrange(0, 7):
            if day_of_week not in to_return:
                to_return[day_of_week] = 0

        return to_return

    def _query_tweet_per_year_week(self):
        self.database_cursor.execute("""SELECT COUNT(*) AS count, year, week_of_year
                                        FROM tweets_parsed_time
                                        GROUP BY year, week_of_year
                                        ORDER BY year, week_of_year""")
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
            for week in xrange(0, 54):
                if week not in to_return[year]:
                    to_return[year][week] = 0

        return to_return

    def _flatten(self, dictionary, parent_key='', separator='_', pad_number_to_size = 2):
        """ Returns flattened version of dictionary """
        items = []
        for key, value in dictionary.items():
            padded_key = str(key).zfill(pad_number_to_size)
            new_key = str(parent_key) + separator + padded_key if parent_key else padded_key
            if isinstance(value, MutableMapping):
                items.extend(self._flatten(value, new_key, separator=separator).items())
            else:
                items.append((new_key, value))
        return OrderedDict(sorted(items))

    def _cumulative_dict(self, dictionary):
        """ Returns cumulative Ordered Dict,
            where value for each key is value for previous keys plus current value """
        return_dict_items = []
        total = 0
        for key, value in dictionary.items():
            total += value
            return_dict_items.append((key, total))
        return OrderedDict(return_dict_items)


    def query(self):
        """ Generate dictionary with query output """
        to_return = LazyDict()
        to_return['tweet_count_total'] = self._query_total_tweets
        to_return['tweet_count_per_year'] = self._query_total_tweets_per_year
        to_return['tweet_count_per_year_month'] = self._query_total_tweets_per_year_month
        to_return['tweet_count_per_month'] = self._query_total_tweets_per_month
        to_return['total_tweets_per_day_of_week'] = self._query_total_tweets_per_day_of_week
        to_return['tweet_count_per_year_week'] = self._query_tweet_per_year_week
        to_return['flat_tweet_count_per_year_week'] = lambda: self._flatten(to_return['tweet_count_per_year_week'])
        to_return['cumulative_flat_tweet_count_per_year_week'] = lambda: self._cumulative_dict(to_return['flat_tweet_count_per_year_week'])
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
                output_file.write(output.encode("utf-8"))

            pprint(data) # debug only, we should have here values used in template computed
            # using lazy loader