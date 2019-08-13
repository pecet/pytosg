from peewee import Model, SqliteDatabase, DatabaseProxy

database_proxy = DatabaseProxy()

class BaseModel(Model):
    class Meta:
        database = database_proxy
