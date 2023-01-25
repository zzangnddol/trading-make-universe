import logging
import time
from datetime import datetime
from typing import Union

import schedule
from database.db import db
from database.model.process_models import write_process_status, ProcessStatus
from database.model.stock_models import StockInfo, StockPrice
from database.model.strategy_models import UniverseTest
from util.notify import Notifier

logging.basicConfig(format="[%(asctime)s] [%(levelname)-4.4s] [%(threadName)-10.10s] [%(filename)-17.17s:%(lineno)-4.4s] : %(message)s")
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

notifier = Notifier("trading-make-universe")


@db.atomic()
def make_universe(strategy_id=1):
    try:
        now = datetime.now()
        logger.info("유니버스 생성 필요 체크")
        today = now.strftime("%Y%m%d")

        # 전체 종목 조회 시 시간이 오래 걸리므로 삼성전자(005930) 종목의 주가를 이용한다.
        last_price: StockPrice = __get_stock_last_price_data("005930")
        if last_price is None:
            logger.warning("[005930] 종목의 주가 정보가 존재하지 않습니다.")
            return
        logger.info(f"Today: {today}, last date in DB: {last_price.date_string}")
        # 최종 데이터가 오늘 날짜가 아니면 휴일로 가정하고 종료
        if today != last_price.date_string:
            return

        count = __make_universe(strategy_id)
        notifier.send(f"유니버스 생성 완료 - {count}개 종목")
    except (Exception,) as e:
        logger.warning(e)
        notifier.send("유니버스 생성 오류")


@db.atomic()
def __make_universe(strategy_id=1, without_insert=False) -> int:
    print("유니버스 생성 작업 시작")
    UniverseTest.delete().where(UniverseTest.stragegy_id == strategy_id).execute()

    count = 0
    stock: StockInfo
    for stock in StockInfo.select():
        last_stock_price: StockPrice = __get_stock_last_price_data(stock.code)
        if last_stock_price is None:
            continue

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

        logger.info(f'{count + 1:>3d} - '
                    f'날짜: {last_stock_price.date_string}     '
                    f'종목코드: {stock.code}     '
                    f'액면가: {stock.par_price:5,d}     '
                    f'종목명: {stock.name}     ')
        if not without_insert:
            UniverseTest.create(stragegy_id=strategy_id,
                                stock_code=stock.code,
                                stock_name=stock.name,
                                date_string=last_stock_price.date_string)

        count += 1
    print(f'[{datetime.now()}] 유니버스 생성 작업 종료 - saved count: {count}')
    return count


def __get_stock_last_price_data(code) -> Union[StockPrice, None]:
    query = StockPrice.select().where(StockPrice.stock_code == code).order_by(StockPrice.date_string.desc())
    if query.count() == 0:
        return None
    return query[0]


def __process_ping():
    write_process_status("UNIVERSE", True)
    logger.info("프로세스 상태 기록")


if __name__ == '__main__':
    logger.info("유니버스 생성 프로세스 시작")

    # 한줄만 가져오기
    # last_price: StockPrice = __get_stock_last_price_data("005930")
    # print("NONE" if last_price is None else last_price.date_string)

    is_test = False
    if is_test:
        # test
        __make_universe(without_insert=False)
    else:
        # 먼저 UNIVERSE 프로세스를 삭제한다.
        ProcessStatus.delete().where(ProcessStatus.process_type == "UNIVERSE").execute()
        # process 상태 기록
        schedule.every().minutes.do(__process_ping)
        # 매일 밤 10시에 작업 수행
        schedule.every().day.at("22:00").do(make_universe)
        logger.info("스케쥴러 시작")
        while True:
            schedule.run_pending()
            time.sleep(1)
