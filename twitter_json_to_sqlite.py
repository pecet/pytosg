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
from TwitterStatsLib import TwitterJsonToSqliteConverter


def main():
    """ Main method """
    data_dir = 'tweets/data/js/tweets/'
    TwitterJsonToSqliteConverter().parse_dir(data_dir)
    #TwitterJsonToSqliteConverter().parse_file('tweets/data/js/tweets/2016_11.js') #just for testing
    #TwitterJsonToSqliteConverter().parse_file('tweets/data/js/tweets/2008_04.js') #just for testing

if __name__ == "__main__":
    sys.exit(main())
