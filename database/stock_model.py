from peewee import CharField, IntegerField, FloatField, DoubleField, \
    CompositeKey, DoesNotExist

from database.db import BaseModel


class StockInfo(BaseModel):
    code = CharField(primary_key=True)
    name = CharField()
    par_price = IntegerField()

    class Meta:
        db_table = "stock_info"


class StockPrice(BaseModel):
    stock_code = CharField()
    date_string = CharField()
    open = IntegerField()
    high = IntegerField()
    low = IntegerField()
    close = IntegerField()
    volume = IntegerField()
    change = FloatField()
    ma5 = DoubleField(null=True)
    ma20 = DoubleField()
    ma60 = DoubleField()
    ma120 = DoubleField()
    rsi10 = DoubleField()
    vma20 = DoubleField()

    class Meta:
        db_table = 'stock_price'
        primary_key = CompositeKey('stock_code', 'date_string')


def get_stock_price(stock_code, date_string):
    try:
        return StockPrice.get(StockPrice.stock_code == stock_code, StockPrice.date_string == date_string)
    except DoesNotExist:
        return None


if __name__ == '__main__':
    print('test')
    for stock in StockInfo.select():
        print(stock.code)
    print('end')
