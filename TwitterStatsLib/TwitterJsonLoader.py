from peewee import *  # pylint: disable=W0614
from .Tweets import Tweets
import TwitterStatsLib.BaseModel as BaseModel
import ijson
import sys
from pprint import pprint
from datetime import datetime
import locale


class TwitterJsonLoader(object):
    ITEMS_TO_INSERT_AT_ONCE = 15

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

    def _parse_datetime(self, datetime_str: str) -> datetime:
        # Because strptime is locale depended we need to change locale do date time operations
        # and then change it back
        saved_locale = locale.getlocale(locale.LC_ALL)
        locale.setlocale(locale.LC_ALL, 'C')
        parsed_datetime = datetime.strptime(datetime_str, '%a %b %d %H:%M:%S %z %Y')
        locale.setlocale(locale.LC_ALL, saved_locale)
        # we need to store date time without timezone, everything will work fine
        # (as in sqlite in datetime any text can be stored) but on runtime and querying this data
        # and e.g. using .day property of peewee DateTimeField where e.g. selecting it will fail on runtime
        return parsed_datetime.replace(tzinfo=None)

    def read_json_to_db(self, file_handle):
        # TODO: Manually removed 'window.YTD.tweet' from file to make it actually parse as JSON.
        # This needs to be done automatically

        # Keys from json to use directly (i.e. without transforming), we do not use all data from JSON in Tweets table
        # but we need to filter unused ones, as peewee will throw exception if dictionary passed to insert_many
        # below will contain keys not present in DB table
        keys_to_use_directly = ('id', 'full_text', 'source', 'in_reply_to_screen_name',
                                'in_reply_to_user_id', 'in_reply_to_status_id', 'in_reply_to_screen_name')

        json_iterator = ijson.items(file_handle, 'item')
        json_keys_to_use = []
        item_buffer_insert_counter = 0
        item_buffer = []
        item: dict
        for item in json_iterator:
            # Filter JSON to get items which can be used as-is
            item_to_insert = {key: value for key, value in item.items() if key in keys_to_use_directly}
            # If there is no such item insert_many still requires item to be present
            for key in keys_to_use_directly:
                if key not in item_to_insert:
                    item_to_insert[key] = None
            # Add items which are results of pre-processing JSON
            item_to_insert.update({
                'source_parsed': self._parse_source(item['source']),
                'created_at': self._parse_datetime(item['created_at'])
            })

            # To reduce number of write operations to DB, we actually insert more than one item at once
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
