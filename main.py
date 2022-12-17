import time
from datetime import datetime

import schedule

from database.db import db
from database.stock_model import StockInfo, StockPrice
from database.strategy_model import UniverseTest


@db.atomic()
def make_universe(strategy_id=1):
    now = datetime.now()
    print(f'[{now}] 유니버스 생성 필요 체크')
    today = now.strftime("%Y%m%d")

    last_price: StockPrice = StockPrice.select().limit(1).order_by(StockPrice.date_string.desc())[0]
    print(f'Today: {today}, last date in DB: {last_price.date_string}')
    # 최종 데이터가 오늘 날짜가 아니면 휴일로 가정하고 종료
    if today != last_price.date_string:
        return

    __make_universe(strategy_id)


@db.atomic()
def __make_universe(strategy_id=1):
    print(f'[{datetime.now()}] 유니버스 생성 작업 시작')
    UniverseTest.delete().where(UniverseTest.stragegy_id == strategy_id).execute()

    count = 0
    for stock in StockInfo.select():
        query = StockPrice.select().where(StockPrice.stock_code == stock.code).order_by(StockPrice.date_string.desc()).limit(1)
        if query.count() == 0:
            continue
        last_stock_price: StockPrice = query[0]
        if last_stock_price.rsi10 is None or last_stock_price.vma20 is None:
            continue
        if last_stock_price.rsi10 >= 30 or last_stock_price.vma20 < 100000:
            continue

        print(f'종목코드: {stock.code}, 날짜: {last_stock_price.date_string}')
        universe = UniverseTest()
        universe.stragegy_id = strategy_id
        universe.stock_code = stock.code
        universe.stock_name = stock.name
        universe.date_string = last_stock_price.date_string
        universe.save()

        count += 1
    print(f'[{datetime.now()}] 유니버스 생성 작업 종료 - saved count: {count}')


if __name__ == '__main__':
    print(f'[{datetime.now()}] 유니버스 생성 프로세스 시작')
    # 한줄만 가져오기
    # last_price: StockPrice = UniverseTest.select().limit(1).order_by(UniverseTest.date_string.desc())[0]
    # print(last_price.date_string)

    # test
    # __make_universe()

    # 매일 밤 10시에 작업 수행
    schedule.every().day.at("22:00").do(make_universe)
    print(f'[{datetime.now()}] 스케쥴러 시작')
    while True:
        schedule.run_pending()
        time.sleep(1)
