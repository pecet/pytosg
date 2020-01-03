from peewee import * # pylint: disable=W0614


class TwitterStatsGenerator(object):
    def __init__(self):
        self.db = SqliteDatabase('tweets.sqlite')
        BaseModel.database_proxy.initialize(self.db)
