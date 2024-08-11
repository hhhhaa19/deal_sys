import logging
import time
from dao import *

# 配置日志记录器
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')


def deal():
    # 由于只对比特币交易，这里写死，后续可以拓展
    symbol_sell = 'USDT'
    symbol_buy = 'BTCUSDT'

    # 数据获取，后续数据组代码替换
    # todo
    while True:
        # 具体算法,输出应该是action,1为买,2为卖,0为hold
        # todo
        action = 2
        # 实际交易
        trade_deal(symbol_sell, symbol_buy, action)

        # 存储当前账户余额
        store_info()
        time.sleep(3600)


from trade_controller import *
from retrieve_controller import *
from decimal import Decimal, getcontext


def truncate_float(number, decimal_places):
    str_number = str(number)
    if '.' in str_number:
        integer_part, decimal_part = str_number.split('.')
        truncated_number = integer_part + '.' + decimal_part[:decimal_places]
    else:
        truncated_number = str_number
    return float(truncated_number)


def trade_deal(symbol_sell, symbol_buy, action=None):
    # 一旦出现问题，直接退出，等待下次命令

    if action == 1:  # 买比特币
        logging.info("开始购买")
        # 得到比特币价格
        BTC_price = get_price_by_symbol(symbol_buy)
        if BTC_price == None:
            return
        # 检查ustd余额
        USDT_balabce = get_balance(symbol_sell)
        if USDT_balabce == None:
            return
        BTC_number = Decimal(USDT_balabce) / Decimal(BTC_price)
        if BTC_number - Decimal(0.00001) < 0:
            logging.warning("创建订单失败，购买数目小于最小数目，可购买数目%f", BTC_number)
            return
        # 创建订单
        oreder_info = create_buy_order('BUY', truncate_float(BTC_number, 5))
        if oreder_info == None:
            return

    if action == 2:  # 卖比特币
        logging.info("开始出售")
        # 得到比特币价格
        BTC_price = get_price_by_symbol(symbol_buy)
        if BTC_price == None:
            return
        # 检查比特币余额
        BTC_balabce = get_balance('BTC')
        if BTC_balabce == None:
            return
        BTC_number = Decimal(BTC_balabce)
        if BTC_number - Decimal(0.00001) < 0:
            logging.warning("创建订单失败，可出售数目小于最小数目，可出售数目%f", BTC_number)
            return
        # 创建订单
        oreder_info = create_sell_order('SELL', truncate_float(BTC_number, 5))
        if oreder_info == None:
            return


def store_info():
    BTC_balance = get_balance('BTC')
    USDT_balance = get_balance('USDT')
    BTC_price = get_price_by_symbol("BTCUSDT")
        # 当前时间戳
    timestamp = datetime.now()
    free = Decimal(BTC_balance) * Decimal(BTC_price) + Decimal(USDT_balance)
    logging.info("当前账户余额%s",free)
    result = {"timestamp": timestamp, "asset": "USDT", "free": free}
    insert_data(result)


if __name__ == '__main__':
    deal()
