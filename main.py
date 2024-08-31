from flask import Flask, render_template, request, redirect, url_for, jsonify
from datetime import datetime, timedelta
import threading
import logging
from trade_controller import *
from dao import *

# 配置日志记录器
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
app = Flask(__name__)


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
    # 算法入口函数，这里创建一个线程来防止死循环
    # threading.Thread(target=deal, daemon=True).start()
    # 前端界面显示
    app.run(debug=False, use_reloader=False, host='0.0.0.0', port=5000)  # 设置允许的访问ip
