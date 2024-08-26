import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import logging
from binance_interface.api import SPOT
from binance_interface.app.utils import eprint
from RL_brain2 import DQN
import torch
from Model_Infer import get_action
from decimal import Decimal, getcontext
import bian
from datetime import datetime, timedelta
import time

class StockTestEnv:
    def __init__(self, key, secret, proxy_host=None):
        # 配置日志记录器
        logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

        self.spot = SPOT(
            key=key, secret=secret,
            proxy_host=proxy_host
        )
        self.account = self.spot.account
        self.trade = self.spot.trade
        self.market = self.spot.market
        self.account_result = self._get_account_info()

    def _get_account_info(self):
        try:
            account_result = self.account.get_account()
            if account_result.get('code') != 200:
                print(account_result.get('code'))
                logging.warning("获取账户数据失败: %s", account_result.get('msg'))
                return None
            else:
                return account_result.get('data')
        except Exception as e:
            logging.error(f"获取账户数据时出错: {e}")
            return None

    def check_account(self):
        if self.account_result:
            return self.account_result.get('canTrade')
        return False

    def get_balance(self, symbol):
        if self.account_result is None:
            logging.warning("account_result 为空")
            return None
        balances = self.account_result.get('balances', [])
        for balance in balances:
            if balance['asset'] == symbol:
                symbol_balance = balance['free']
                logging.info("币种%s目前余额为%s", symbol, symbol_balance)
                return symbol_balance
        logging.warning("币种%s未在账户中找到", symbol)
        return None

    def create_buy_order(self, action, quantity):
        set_order_result = self.trade.set_order(
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

    def create_sell_order(self, action, quantity):
        set_order_result = self.trade.set_order(
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

    def get_price_by_symbol(self, symbol):
        spot_goods_price = self.market.get_ticker_price(symbol=symbol)
        print(symbol, spot_goods_price)
        if spot_goods_price.get('code') != 200:
            logging.warning("获取数据失败: %s", spot_goods_price.get('msg'))
            return None
        price = spot_goods_price.get('data')['price']
        logging.info("当前比特币价格: %s", price)
        return price

    def truncate_float(self, number, decimal_places):
        str_number = str(number)
        if '.' in str_number:
            integer_part, decimal_part = str_number.split('.')
            truncated_number = integer_part + '.' + decimal_part[:decimal_places]
        else:
            truncated_number = str_number
        return float(truncated_number)

    def trade_deal(self, symbol_sell, symbol_buy, action=None):
        # 一旦出现问题，直接退出，等待下次命令

        if action == 1:  # 买比特币
            logging.info("开始购买")
            # 得到比特币价格
            BTC_price = self.get_price_by_symbol(symbol_buy)
            if BTC_price is None:
                return
            # 检查USDT余额
            USDT_balance = self.get_balance(symbol_sell)
            if USDT_balance is None:
                return
            BTC_number = Decimal(Decimal(USDT_balance) / Decimal(BTC_price) + Decimal('0.01')) # 避免真实交易
            if BTC_number - Decimal(0.00001) < 0:
                logging.warning("创建订单失败，购买数目小于最小数目，可购买数目%f", BTC_number)
                return
            # 创建订单
            order_info = self.create_buy_order('BUY', self.truncate_float(BTC_number, 5))
            if order_info is None:
                return

        if action == 2:  # 卖比特币
            logging.info("开始出售")
            # 得到比特币价格
            BTC_price = self.get_price_by_symbol(symbol_buy)
            if BTC_price is None:
                return
            # 检查比特币余额
            BTC_balance = self.get_balance('BTC')
            if BTC_balance is None:
                return
            BTC_number = Decimal(BTC_balance) + Decimal('0.01') # 避免真实交易
            if BTC_number - Decimal(0.00001) < 0:
                logging.warning("创建订单失败，可出售数目小于最小数目，可出售数目%f", BTC_number)
                return
            # 创建订单
            order_info = self.create_sell_order('SELL', self.truncate_float(BTC_number, 5))
            if order_info is None:
                return



if __name__ == "__main__":
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

    # 定义数据库连接参数
    host = 'localhost'
    user = 'root'
    password = '123456'
    database = 'alpacadata'

    db_config = {
        'host': host,
        'user': user,
        'password': password,
        'database': database
    }
    # 定义模型路径
    model_path = 'trained_model/600_model.pth'

    start_date = "2024-08-06"  # 数据起始日期
    bian.update_database(start_date, db_config)

    # 定义API密钥和代理主机
    proxy_host = None
    key = 'ugsuQUG1mQfBLDJACLhLkUmlwqtAEPFRHBg7MzKzuTMuBabf2XzlnIoJ31rVIEt6'
    secret = 'YpGfU1TxEdmJnOGvkxo5TUGC8Tg9L2tkkqPLtkwQVTHSf1y80aUEPppofeLU2Lof'

    # 获取预测的动作
    while True:
        # 获取当前时间
        now = datetime.now()

        # 计算距离下一个整点零1分钟的时间
        next_run_time = (now + timedelta(hours=0)).replace(minute=24, second=0, microsecond=0)
        sleep_duration = (next_run_time - now).total_seconds()

        print(f"Current time: {now}. Next run time: {next_run_time}. Sleeping for {sleep_duration} seconds.")

        # 休眠直到下一个整点零1分钟
        time.sleep(sleep_duration)

        start_date = now.strftime("%Y-%m-%d")
        # 更新数据库
        bian.update_database(start_date, db_config)

        # 获取预测的动作
        action = get_action(host, user, password, database, model_path)
        print("Chosen action:", action)

        env = StockTestEnv(key, secret, proxy_host)

        # 打印账户余额
        btc_balance = env.get_balance('BTC')
        print(f'BTC 余额: {btc_balance}')

        usdt_balance = env.get_balance('USDT')
        print(f'USDT 余额: {usdt_balance}')

        # 执行交易动作
        env.trade_deal('USDT', 'BTCUSDT', action)

        # 打印账户余额
        btc_balance = env.get_balance('BTC')
        print(f'BTC 余额: {btc_balance}')

        usdt_balance = env.get_balance('USDT')
        print(f'USDT 余额: {usdt_balance}')