from peewee import * # pylint: disable=W0614
from .Tweets import Tweets
import TwitterStatsLib.BaseModel as BaseModel

class TwitterJsonLoader(object):
    def do_something(self):
        db = SqliteDatabase('tweets.sqlite')
        BaseModel.database_proxy.initialize(db)
        db.create_tables([Tweets])

        