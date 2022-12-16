from peewee import CharField, IntegerField

from database.db import BaseModel


class UniverseTest(BaseModel):
    stragegy_id = IntegerField()
    stock_code = CharField()
    stock_name = CharField()
    date_string = CharField()

    class Meta:
        db_table = "universe_test"
        primary_key = False
