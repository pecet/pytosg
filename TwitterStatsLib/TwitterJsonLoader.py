from peewee import * # pylint: disable=W0614
from .Tweets import Tweets
import TwitterStatsLib.BaseModel as BaseModel
import ijson
import sys
from pprint import pprint

class TwitterJsonLoader(object):
    ITEMS_TO_INSERT_AT_ONCE = 10

    def __init__(self):
        self.db = SqliteDatabase('tweets.sqlite')
        BaseModel.database_proxy.initialize(self.db)

    def create_db(self) -> None:
        self.db.create_tables([Tweets])

    def _parse_source(self, full_source: str) -> str:
        # source is written like this:
        # <a href="http://twitter.com/download/android" rel="nofollow">Twitter for Android</a>s
        # simplest way to parse it is to find > and < and cut text inside of its
        first_token = full_source.find('>')
        source_part = full_source[first_token + 1:]
        last_token = source_part.find('<')
        return source_part[:last_token]

    def read_json_to_db(self, file_handle):
        # TODO: Manually removed 'window.YTD.tweet' from file to make it actually parse as JSON.
        # This needs to be done automatically
        json_iterator = ijson.items(file_handle, 'item')
        json_keys_to_use = []
        item_buffer_insert_counter = 0
        item_buffer = []
        for item in json_iterator:
            item_to_insert = {
                'tweet_id': item['id'],
                'text': item['full_text'],
                'source': item['source'],
                'source_parsed': self._parse_source(item['source']),
                'created_at': item['created_at']
            }
            # to reduce number of write operations to DB, we actually insert more than one item at once
            # items are stored in buffer
            item_buffer.append(item_to_insert)
            item_buffer_insert_counter += 1
            if item_buffer_insert_counter >= TwitterJsonLoader.ITEMS_TO_INSERT_AT_ONCE:
                with self.db.atomic():
                    Tweets.insert_many(item_buffer).execute()
                item_buffer_insert_counter = 0
                item_buffer = []

        # insert remaining items
        if item_buffer_insert_counter > 0:
            with self.db.atomic():
                Tweets.insert_many(item_buffer).execute()

