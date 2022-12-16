import time
from datetime import datetime

import schedule

from database.db import db
from database.stock_model import StockInfo, StockPrice, get_stock_price
from database.strategy_model import UniverseTest


@db.atomic()
def make_universe(strategy_id=1):
    today = datetime.now().strftime("%Y%m%d")

    last_price: StockPrice = StockPrice.select().limit(1).order_by(StockPrice.date_string.desc())[0]
    print(f'Today: {today}, last date in DB: {last_price.date_string}')
    # 최종 데이터가 오늘 날짜가 아니면 휴일로 가정하고 종료
    if today != last_price.date_string:
        return

    UniverseTest.delete().where(UniverseTest.stragegy_id == strategy_id)

    count = 0
    for stock in StockInfo.select():
        last_stock_price: StockPrice = get_stock_price(stock.code, today)
        if last_stock_price is None:
            continue
        if last_stock_price.rsi10 is None or last_stock_price.vma20 is None:
            continue
        if last_stock_price.rsi10 >= 30 or last_stock_price.vma20 < 100000:
            continue

        print(stock.code)
        universe = UniverseTest()
        universe.stragegy_id = strategy_id
        universe.stock_code = stock.code
        universe.stock_name = stock.name
        universe.date_string = today
        universe.save()

        count += 1
    print(f'saved count = {count}')


if __name__ == '__main__':
    # 한줄만 가져오기
    # last_price: StockPrice = UniverseTest.select().limit(1).order_by(UniverseTest.date_string.desc())[0]
    # print(last_price.date_string)

    # test
    # make_universe()

    # 매일 밤 10시에 작업 수행
    schedule.every().day.at("22:00").do(make_universe)
    while True:
        schedule.run_pending()
        time.sleep(1)
