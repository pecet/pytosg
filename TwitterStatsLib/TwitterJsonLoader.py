from peewee import * # pylint: disable=W0614
from TwitterStatsLib.Tweets import Tweets
import TwitterStatsLib.BaseModel as bm

class TwitterJsonLoader(object):
    def do_something(self):
        db = SqliteDatabase('tweets.sqlite')
        bm.database_proxy.initialize(db)
        db.create_tables([Tweets])

        