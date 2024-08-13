# 这个文件用于发送请求交易,注意保护API_KEY
import math

from binance_interface.api import SPOT
from binance_interface.app.utils import eprint
import logging
from config import Config
# 配置日志记录器
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

proxy_host = None
key = Config.BIAN_KEY
secret = Config.BIAN_SECRET

spot = SPOT(
    key=key, secret=secret,
    proxy_host=proxy_host
)
account = spot.account
trade = spot.trade
# 存的是账户信息
account_result = account.get_account()
if account_result.get('code') != 200:
    print(account_result.get('code'))
    logging.warning("获取账户数据失败: %s", account_result.get('msg'))
    account_result = None
else:
    account_result = account_result.get('data')


# 检查是否可以交易
def check_account():
    return account_result.get('canTrade')


def get_balance(symbol):
    if account_result == None:
        return None
    balances = account_result['balances']
    for balance in balances:
        if balance['asset'] == symbol:
            symbol_balance = balance['free']
            logging.info("币种%s目前余额为%s", symbol, symbol_balance)
            return symbol_balance
    logging.warning("币种%s未在账户中找到", symbol)
    return None


# 输入一个交易信息，判断是否条件是否充足返回创建订单是否成功
def create_buy_order(action, quantity):
    set_order_result = trade.set_order(
        symbol='BTCUSDT',
        quantity=quantity,
        side=action,
        type='MARKET',
    )
    if set_order_result.get('code') != 200:
        logging.error("订单创建失败，错误原因%s", set_order_result.get('msg'))
        return
    logging.info("订单创建成功，订单号为%s,买入数目为%s", set_order_result.get('data')['orderId'], quantity)
    return set_order_result.get('data')


def create_sell_order(action, quantity):
    set_order_result = trade.set_order(
        symbol='BTCUSDT',
        quantity=quantity,
        side=action,
        type='MARKET',
    )
    if set_order_result.get('code') != 200:
        logging.error("订单创建失败，错误原因%s", set_order_result.get('msg'))
        return
    logging.info("订单创建成功，订单号为%s,出售数目为%s", set_order_result.get('data')['orderId'], quantity)
    return set_order_result.get('data')


# 输入symbol，返回当前symbol的所有挂单信息：
def order_by_symbol(symbol):
    result = []
    open_order_result = trade.get_openOrders(symbol='')
    if open_order_result.get('code') != 200:
        print("查询订单错误")
        return result

    for order in open_order_result.get('data'):
        if order.get('symbol') == symbol:
            order_detail = trade.get_order(symbol=symbol, order_id=order.get('orderId'))
            result.append(order_detail)
    return result


def cancel_all_order_by_symbol(symbol):
    return trade.cancel_openOrders(symbol)


def get_trade():
    userTrade_result = account.get_myTrades("BTCUSDT")
    if userTrade_result.get('code') != 200:
        logging.error("查询BTC历史订单失败，错误原因%s", userTrade_result.get('msg'))
        return
    logging.info("订单查询成功")
    return userTrade_result


def get_account_balance():
    account_result = account.get_account()
    if account_result.get('code') != 200:
        logging.error("查询账户余额失败，错误原因%s", account_result.get('msg'))
        return
    account_balance = account_result.get('data')['balances']
    filtered_balance = [asset for asset in account_balance if float(asset['free']) > 0]
    logging.info("查询账户余额成功,当前余额%s", filtered_balance)
    return filtered_balance


if __name__ == '__main__':
    # print(get_balance("USDT"))
    # print(get_account_balance())
    print(key)
