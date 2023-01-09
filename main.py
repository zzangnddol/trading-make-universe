import time
from datetime import datetime

import schedule

from database.db import db
from database.stock_model import StockInfo, StockPrice
from database.strategy_model import UniverseTest


@db.atomic()
def make_universe(strategy_id=1):
    try:
        now = datetime.now()
        print(f'[{now}] 유니버스 생성 필요 체크')
        today = now.strftime("%Y%m%d")

        last_price: StockPrice = StockPrice.select().limit(1).order_by(StockPrice.date_string.desc())[0]
        print(f'Today: {today}, last date in DB: {last_price.date_string}')
        # 최종 데이터가 오늘 날짜가 아니면 휴일로 가정하고 종료
        if today != last_price.date_string:
            return

        __make_universe(strategy_id)
    except (Exception,) as e:
        print(e)


@db.atomic()
def __make_universe(strategy_id=1, without_insert=False):
    print(f'[{datetime.now()}] 유니버스 생성 작업 시작')
    UniverseTest.delete().where(UniverseTest.stragegy_id == strategy_id).execute()

    count = 0
    stock: StockInfo
    for stock in StockInfo.select():
        query = StockPrice.select().where(StockPrice.stock_code == stock.code).order_by(StockPrice.date_string.desc()).limit(1)
        if query.count() == 0:
            continue
        last_stock_price: StockPrice = query[0]

        if '스팩' in stock.name:
            continue
        if stock.par_price is None or stock.par_price == 0:
            continue
        if last_stock_price.rsi10 is None or last_stock_price.vma20 is None:
            continue
        if last_stock_price.rsi10 >= 30 or last_stock_price.vma20 < 100000:
            continue
        if last_stock_price.close < stock.par_price or last_stock_price.close < 1000:
            continue

        # 종목 이름에 '스팩'이 없어야 함
        # 액면가 - 0 혹은 None이 아닌 경우
        # RSI(10) < 30
        # V_MA(20) >= 10만
        # PRICE >= 액면가, >= 1000

        print(f'날짜: {last_stock_price.date_string}, 종목코드: {stock.code}, 액면가: {stock.par_price} 종목명: {stock.name}')
        if not without_insert:
            UniverseTest.create(stragegy_id=strategy_id, stock_code=stock.code, stock_name=stock.name, date_string=last_stock_price.date_string)

        count += 1
    print(f'[{datetime.now()}] 유니버스 생성 작업 종료 - saved count: {count}')


if __name__ == '__main__':
    print(f'[{datetime.now()}] 유니버스 생성 프로세스 시작')

    # 한줄만 가져오기
    # last_price: StockPrice = UniverseTest.select().limit(1).order_by(UniverseTest.date_string.desc())[0]
    # print(last_price.date_string)

    is_test = False
    if is_test:
        # test
        __make_universe(without_insert=False)
    else:
        # 매일 밤 10시에 작업 수행
        schedule.every().day.at("22:00").do(make_universe)
        print(f'[{datetime.now()}] 스케쥴러 시작')
        while True:
            schedule.run_pending()
            time.sleep(1)