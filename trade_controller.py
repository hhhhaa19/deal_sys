# 这个文件用于发送请求交易,注意保护API_KEY
import math

from binance_interface.api import SPOT
from binance_interface.app.utils import eprint
import logging
from config import Config
from retrieve_controller import *

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
def create_buy_order(trading_pair, action, quantity):
    set_order_result = trade.set_order(
        symbol=trading_pair,
        quantity=quantity,
        side=action,
        type='MARKET',
    )
    print(quantity)
    if set_order_result.get('code') != 200:
        logging.error("订单创建失败，错误原因%s", set_order_result.get('msg'))
        return
    logging.info("订单创建成功，订单号为%s,买入数目为%s", set_order_result.get('data')['orderId'], quantity)
    return set_order_result.get('data')


def create_sell_order(trading_pair, action, quantity):
    set_order_result = trade.set_order(
        symbol=trading_pair,
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
    all_trades = []

    for symbol in Config.Trading_pair:
        userTrade_result = account.get_myTrades(symbol=symbol)
        if userTrade_result.get('code') != 200:
            logging.error("查询 %s 交易对历史订单失败，错误原因: %s", symbol, userTrade_result.get('msg'))
            continue  # 继续处理下一个交易对

        trades = userTrade_result.get('data', [])
        if trades:
            all_trades.extend(trades)
            logging.info("查询 %s 交易对成功，共获取到 %d 条交易记录", symbol, len(trades))
        else:
            logging.info("查询 %s 交易对成功，但未获取到任何交易记录", symbol)

    if all_trades:
        logging.info("所有交易对订单查询成功，总共获取到 %d 条交易记录", len(all_trades))
    else:
        logging.warning("未获取到任何交易记录")

    return all_trades


def get_account_balance():
    account_result = account.get_account()
    if account_result.get('code') != 200:
        logging.error("查询账户余额失败，错误原因%s", account_result.get('msg'))
        return
    account_balance = account_result.get('data')['balances']
    filtered_balance = [asset for asset in account_balance if float(asset['free']) > 0]
    logging.info("查询账户余额成功,当前余额%s", filtered_balance)
    return filtered_balance


def get_total_account_value_in_usdt():
    # 获取账户余额
    account_balance = get_account_balance()

    if not account_balance:
        logging.error("获取账户余额失败，无法计算总价值")
        return 0

    total_value_usdt = 0.0

    for asset in account_balance:
        symbol = asset['asset']
        free_balance = float(asset['free'])

        # 跳过 USDT 资产
        if symbol == 'USDT':
            total_value_usdt += free_balance
            continue

        # 获取当前资产相对于 USDT 的交易对价格
        trading_pair = f"{symbol}USDT"

        try:
            price = float(get_price_by_symbol(symbol=trading_pair))
            # 计算该资产的USDT等值
            asset_value_usdt = free_balance * price
            logging.info(f"{symbol} 余额: {free_balance} 价格: {price} USDT价值: {asset_value_usdt}")
            total_value_usdt += asset_value_usdt

        except Exception as e:
            logging.warning(f"获取 {trading_pair} 价格时发生错误: {str(e)}")
            continue

    logging.info(f"账户总价值: {total_value_usdt} USDT")
    return total_value_usdt


if __name__ == '__main__':
    # print(get_balance("USDT"))
    # print(get_account_balance())
    print(get_trade())
