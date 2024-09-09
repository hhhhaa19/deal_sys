import logging
import time
from dao import *
from Model_Infer import *
from bian import *
from flask import Flask, render_template, request, redirect, url_for, jsonify
import threading
from threading import Lock
from decimal import Decimal, getcontext, ROUND_DOWN

app = Flask(__name__)
trading_pair = "BTCUSDT"
trading_pair_lock = Lock()
log_entries = []
# 定义全局变量用于控制交易
stop_trading = threading.Event()
stop_trading.set()

# 设置日志记录器，将日志保存到log_entries列表中
logging.basicConfig(filename='./logger/app.log', level=logging.INFO)


# 自定义日志处理器，将日志写入log_entries
class ListHandler(logging.Handler):
    def emit(self, record):
        log_entries.append(self.format(record))


# 配置日志记录器
list_handler = ListHandler()
list_handler.setFormatter(logging.Formatter('%(asctime)s - %(levelname)s - %(message)s'))

# 配置日志记录器，将日志保存到文件并添加 ListHandler
logging.basicConfig(
    filename='./logger/app.log',
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logging.getLogger().addHandler(list_handler)


def deal():
    global trading_pair
    device = torch.device("cpu")
    h_in = (torch.zeros([1, 1, 128], dtype=torch.float).to(device),
            torch.zeros([1, 1, 128], dtype=torch.float).to(device))
    while not stop_trading.is_set():
        logging.info("开始交易")
        # 获取当前时间
        current_time = datetime.now()

        # 将时间格式化为字符串
        formatted_time = current_time.strftime('%Y-%m-%d')
        update_database(formatted_time, Config.db_config, trading_pair)
        # 锁定交易对变量以确保线程安全
        with trading_pair_lock:
            current_trading_pair = trading_pair

        # 交易参数
        symbol_sell = 'USDT'
        symbol_buy = trading_pair.replace(symbol_sell, '')

        # 具体算法,输出应该是action,1为买,2为卖,0为hold
        db_config = Config.db_config

        # 调用 get_action 获取动作和更新后的隐藏状态
        action, h_in = get_action(
            db_config.get('host'),
            db_config.get('user'),
            db_config.get('password'),
            db_config.get('database'),
            Config.MODEL_LOCATION,
            h_in,
            trading_pair
        )

        # 实际交易
        trade_deal(symbol_sell, current_trading_pair, symbol_buy, action)

        # 存储当前账户余额
        store_info(symbol_sell)

        # 等待一段时间
        for _ in range(3600):  # 分60次每秒检测一次
            if current_trading_pair != trading_pair or stop_trading.is_set():
                break
            time.sleep(1)


from trade_controller import *
from retrieve_controller import *
from decimal import Decimal, getcontext

import logging


def truncate_float(number, tick_size):
    """
    将数字截断到满足 tick_size 要求的精度。

    :param number: 要处理的浮点数
    :param tick_size: 价格的最小变化单位，字符串格式，例如 "0.001000"
    :return: 满足 tick_size 要求的浮点数
    """
    # 设置 Decimal 精度上下文
    getcontext().rounding = ROUND_DOWN

    # 将 number 和 tick_size 转换为 Decimal
    number_decimal = Decimal(number)
    tick_size_decimal = Decimal(tick_size)

    # 确定小数位数
    if '.' in tick_size:
        decimal_places = len(tick_size.split('.')[1].rstrip('0'))
    else:
        decimal_places = 0

    # 截断到指定的小数位数
    factor = Decimal('1e{}'.format(decimal_places))
    truncated_number = (number_decimal * factor).to_integral_value(rounding=ROUND_DOWN) / factor

    # 确保结果是 tick_size 的倍数
    truncated_float = (truncated_number // tick_size_decimal) * tick_size_decimal

    logging.info("实际交易数目: %s", truncated_float)
    return float(truncated_float)


def trade_deal(symbol_sell, trading_pair, symbol_buy, action=None):
    # 一旦出现问题，直接退出，等待下次命令
    accuracy = get_market_lot_size_step_size(trading_pair)
    logging.info("当前币种%s的要求数字精确度为%s", trading_pair, accuracy)

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
        logging.info("试图购买的%s的数目为%s", symbol_buy, Buyer_number)
        if Buyer_number - Decimal(accuracy) < 0:
            logging.warning("创建订单失败，购买数目小于最小数目，可购买数目%f", Buyer_number)
            return
        # 创建订单
        oreder_info = create_buy_order(trading_pair, 'BUY', truncate_float(Buyer_number, accuracy))
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
        oreder_info = create_sell_order(trading_pair, 'SELL', truncate_float(Buyer_number, accuracy))
        if oreder_info == None:
            return


def store_info(symbol_sell):
    # 当前时间戳
    timestamp = datetime.now()
    free = get_total_account_value_in_usdt()
    if free == 0:
        logging.warning("未成功注入信息")
        return
    result = {"timestamp": timestamp, "asset": symbol_sell, "free": free}
    insert_data(result)


@app.route('/update_trading_pair', methods=['GET', 'POST'])
def update_trading_pair():
    global trading_pair
    global stop_trading
    data = request.json
    new_trading_pair = data.get('trading_pair')

    if new_trading_pair:
        with trading_pair_lock:
            trading_pair = new_trading_pair
            logging.info(f"Trading pair updated to: {trading_pair}")
        return '', 204  # 无返回值
    else:
        return jsonify({"error": "Invalid trading pair"}), 400


@app.route('/get_logs')
def get_logs():
    return jsonify({"logs": log_entries})


@app.route('/start_trading')
def start_trading():
    if not stop_trading.is_set():
        return jsonify({"status": "Trading already running"}), 400
    stop_trading.clear()
    trading_thread = threading.Thread(target=deal)
    trading_thread.start()
    return jsonify({"status": "Trading started"}), 200


@app.route('/stop_trading')
def stop_trading_function():
    stop_trading.set()  # Set the stop_trading event to stop trading
    return jsonify({"status": "Trading stopped"}), 200


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/kline')
def kline():
    trading_pair = request.args.get('trading_pair')
    # 假设startTime和endTime是定义好的时间戳
    startTime = int(time.time() - 36000) * 1000  # 1小时之前
    endTime = int(time.time()) * 1000  # 当前时间
    BTC_kline = get_kline(trading_pair, startTime, endTime)
    if BTC_kline == None:
        return None
    # generate_kline_chart(BTC_kline)
    return jsonify(BTC_kline)


@app.route('/trade')
def trade():
    return jsonify(get_trade())


@app.route('/account')
def account():
    # 得到当前所有钱包不为0所有币种余额
    return jsonify(get_account_balance())


@app.route('/award')
def award():
    # 得到以usdt结算的历史资产
    return query_data()


if __name__ == '__main__':
    app.run(debug=False, use_reloader=False, host='0.0.0.0', port=5001)  # 设置允许的访问ip
