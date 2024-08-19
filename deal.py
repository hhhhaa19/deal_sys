import logging
import time
from dao import *

# 配置日志记录器
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')


def deal():
    # 由于只对比特币交易，这里写死，后续可以拓展
    symbol_sell = 'USDT'#结算货币
    trading_pair = 'DOGEUSDT'
    symbol_buy = 'DOGE'
    # 数据获取，后续数据组代码替换
    # todo
    while True:
        # 具体算法,输出应该是action,1为买,2为卖,0为hold
        # todo
        action = 2
        # 实际交易
        trade_deal(symbol_sell, trading_pair, symbol_buy,action)

        # 存储当前账户余额
        store_info(symbol_sell)
        time.sleep(3600)


from trade_controller import *
from retrieve_controller import *
from decimal import Decimal, getcontext


def truncate_float(number, tick_size):
    """
    将数字截断到满足 tick_size 要求的精度。

    :param number: 要处理的浮点数
    :param tick_size: 价格的最小变化单位，字符串格式，例如 "0.001000"
    :return: 满足 tick_size 要求的浮点数
    """
    # 确定小数位数
    if '.' in tick_size:
        decimal_places = len(tick_size.split('.')[1].rstrip('0'))
    else:
        decimal_places = 0

    # 将数字转换为字符串并截断到指定的小数位数
    str_number = str(number)
    if '.' in str_number:
        integer_part, decimal_part = str_number.split('.')
        truncated_number = integer_part + '.' + decimal_part[:decimal_places]
    else:
        truncated_number = str_number

    # 将截断后的字符串转换回浮点数
    truncated_float = float(truncated_number)

    # 确保结果是 tick_size 的倍数
    truncated_float = (truncated_float // float(tick_size)) * float(tick_size)

    return truncated_float

def trade_deal(symbol_sell, trading_pair,symbol_buy, action=None):
    # 一旦出现问题，直接退出，等待下次命令
    accuracy = get_market_lot_size_step_size(trading_pair)

    if action == 1:  # 买比特币
        logging.info("开始购买")
        # 得到用USDT 目标币种结算的价格
        Buyer_price = get_price_by_symbol(trading_pair)
        if Buyer_price == None:
            return
        # 检查ustd余额
        USDT_balance = get_balance(symbol_sell)
        if USDT_balance == None:
            return
        Buyer_number = (Decimal(USDT_balance) / Decimal(Buyer_price)) * Decimal('0.999')  # 考虑0.1%手续费
        logging.info("试图购买的%s的数目为%s",symbol_buy,Buyer_number)
        if Buyer_number - Decimal(accuracy) < 0:
            logging.warning("创建订单失败，购买数目小于最小数目，可购买数目%f", Buyer_number)
            return
        # 创建订单
        oreder_info = create_buy_order(trading_pair,'BUY', truncate_float(Buyer_number, accuracy))
        if oreder_info == None:
            return

    if action == 2:  # 卖比特币
        logging.info("开始出售")
        # 得到比特币价格
        Buyer_price = get_price_by_symbol(trading_pair)
        if Buyer_price == None:
            return
        # 检查余额
        Seller_balance = get_balance(symbol_buy)
        if Seller_balance == None:
            return
        Buyer_number = Decimal(Seller_balance)
        if Buyer_number - Decimal(accuracy) < 0:
            logging.warning("创建订单失败，可出售数目小于最小数目，可出售数目%f", Buyer_number)
            return
        # 创建订单
        oreder_info = create_sell_order(trading_pair,'SELL', truncate_float(Buyer_number, accuracy))
        if oreder_info == None:
            return


def store_info(symbol_sell):
    # 当前时间戳
    timestamp = datetime.now()
    free = get_total_account_value_in_usdt()
    result = {"timestamp": timestamp, "asset": symbol_sell, "free": free}
    insert_data(result)


if __name__ == '__main__':
    deal()
