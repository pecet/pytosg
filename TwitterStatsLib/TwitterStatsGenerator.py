import sqlite3
from collections import OrderedDict
from .Output import Output, HTMLOutput
from .LazyDict import LazyDict
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