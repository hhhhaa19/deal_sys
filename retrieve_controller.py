# 所有函数用于发送请求,获取数据，这里的接口的调用不需要API_KEY
import time
from binance_interface.api import SPOT
from binance_interface.app import BinanceSPOT
from binance_interface.app.utils import eprint
import logging
from config import Config

# 配置日志记录器
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# 不设置代理
proxy_host = Config.BIAN_PROXY
proxy_host = proxy_host
spot = SPOT(
)
market = spot.market
binanceSPOT = BinanceSPOT(
    key=Config.BIAN_KEY, secret=Config.BIAN_SECRET,
    proxy_host=proxy_host
)
binance_market = binanceSPOT.market


# 获取当前交易规范，在发送交易前做一个验证


def get_market_lot_size_step_size(symbol):
    """
    根据交易对名称从MARKET_LOT_SIZE中获取市价单交易量的最小变动单位。
    :param symbol: 交易对名称，例如'BTCUSDT'
    :return: 市价单交易量的最小变动单位，如果未找到则返回None
    """
    exchangeInfo_result = binance_market.get_exchangeInfo(symbol)
    data = exchangeInfo_result.get('data', {})
    if data.get('symbol') == symbol:
        for filter in data.get('filters', []):
            if filter.get('filterType') == 'LOT_SIZE':
                logging.info(f"The step size for {symbol} in MARKET_LOT_SIZE is: {filter.get('stepSize')}")
                return filter.get('stepSize')
    # 如果未找到交易对或MARKET_LOT_SIZE过滤器，返回None
    return None




def get_price_by_symbol(symbol):
    spot_goods_price = market.get_ticker_price(symbol=symbol)
    if spot_goods_price.get('code') != 200:
        logging.warning("获取数据失败: %s", spot_goods_price.get('msg'))
        return None
    price = spot_goods_price.get('data')['price']
    logging.info("当前%s价格: %s", symbol, price)
    return price


def get_kline(trading_pair, startTime, endTime):
    kline_result = market.get_klines(
        symbol=trading_pair,
        interval='1m',
        startTime=startTime,
        endTime=endTime
    )

    if kline_result['code'] != 200:
        logging.warning("获取K线数据失败,失败原因 %s", kline_result['msg'])
        return None

    kline_data = kline_result['data']

    categories = [time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(item[0] / 1000)) for item in kline_data]
    values = [[item[1], item[2], item[3], item[4]] for item in kline_data]

    data = {
        "categories": categories,
        "values": values
    }
    logging.info("获取K线数据成功")
    return data


import pandas as pd
import mplfinance as mpf
import logging


def generate_kline_chart(data):
    if not data or 'categories' not in data or 'values' not in data:
        logging.warning("k线数据不完整或格式不正确")
        return None

    # 创建DataFrame
    df = pd.DataFrame(data['values'], columns=['Open', 'High', 'Low', 'Close'])
    df['Date'] = pd.to_datetime(data['categories'])
    df.set_index('Date', inplace=True)
    # 添加移动平均线
    apds = [
        mpf.make_addplot(df['Close'].rolling(window=3).mean(), color='r', width=1.5),  # 短期平均线
        mpf.make_addplot(df['Close'].rolling(window=7).mean(), color='b', width=1.5)  # 长期平均线
    ]

    # 配置图表风格
    mpf_style = mpf.make_mpf_style(base_mpf_style='charles', rc={'font.size': 8},
                                   mavcolors=['red', 'blue'])

    # 将数据类型转换为float，mplfinance需要float类型
    df = df.apply(pd.to_numeric)

    # 设置图表大小和分辨率
    fig, axes = mpf.plot(df, type='candle', style=mpf_style, addplot=apds, volume=False, returnfig=True,
                         figsize=(10, 6),
                         title='Bitcoin K-Line', ylabel='Price (USD)')
    # 调整子图布局
    fig.subplots_adjust(left=0.05, right=0.95, bottom=0.2, top=0.9)
    # 保存图像
    fig.savefig('static/img/bitcoin_kline_chart.png', dpi=300)
    logging.info("K线图生成并保存成功")


if __name__ == '__main__':
    # startTime = int(time.time() - 48000) * 1000  # 10小时之前
    # endTime = int(time.time()) * 1000  # 当前时间
    # generate_kline_chart(get_kline(startTime, endTime))
    print(get_kline('BTCUSDT',))
