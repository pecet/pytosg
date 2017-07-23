#!/usr/bin/env python

"""
Generate statistics from previously generated twitter SQLite file
Typically you want to run twitter_json_to_sqlite.py script first
License : MIT
Author  : Piotr Czarny
"""

import sys
from timeit import timeit
from TwitterStatsLib import TwitterStatsGenerator, HTMLOutput

def main():
    """ Main method """
    # TODO: add unit tests
    # dtest = LazyDict()
    # dtest["A"] = lambda: 10
    # dtest["B"] = lambda: 20
    # pprint(dtest)
    # print(dtest)
    # pprint(dtest["B"])
    # pprint(dtest["B"])
    # pprint(dtest)
    # sys.exit(0)

    #print timeit(lambda: TwitterStatsGenerator().render(output_renderer_cls=HTMLOutput), number=1)
    print TwitterStatsGenerator()._select_query('tweets_parsed_time', ['count(*)', 'year'], 'year')

if __name__ == "__main__":
    sys.exit(main())
