from peewee import * # pylint: disable=W0614
from TwitterStatsLib.BaseModel import BaseModel

class Tweets(BaseModel):
    # via official Twitter documentation
    MAX_USERNAME_LENGTH = 15

    id = IntegerField(primary_key=True, unique=True)
    full_text = TextField()
    created_at = DateTimeField()
    source = CharField(max_length=128)  # for some reason this contains whole HTML link and not only Client name
    source_parsed = CharField(max_length=64)

    # replies
    in_reply_to_status_id = IntegerField(null=True)
    in_reply_to_user_id = IntegerField(null=True)
    in_reply_to_screen_name = CharField(max_length=MAX_USERNAME_LENGTH, null=True)
    