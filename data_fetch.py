from binance_interface.app import BinanceSPOT
from binance_interface.app.utils import eprint
import time, csv
from alpaca.data.historical import CryptoHistoricalDataClient

# No keys required for crypto Data
client = CryptoHistoricalDataClient()

from config import Config

proxy_host = None
key = Config.BIAN_KEY
secret = Config.BIAN_SECRET

binanceSPOT = BinanceSPOT(
    key=key,
    secret=secret,
    proxy_host=proxy_host,
    timezone='Asia/Shanghai',
)
market = binanceSPOT.market


def fetch_data_in_batches(symbol, interval, start_time_str, end_time_str):
    # 转换时间为Unix时间戳（毫秒）
    start_time_unix = int(time.mktime(time.strptime(start_time_str, '%Y-%m-%d %H:%M:%S')) * 1000)
    end_time_unix = int(time.mktime(time.strptime(end_time_str, '%Y-%m-%d %H:%M:%S')) * 1000)

    csv_data = []

    while start_time_unix < end_time_unix:
        # 调用get_history_candle API获取数据
        candle_result = market.get_history_candle(
            symbol=symbol,
            start=time.strftime('%Y-%m-%d %H:%M:%S', time.gmtime(start_time_unix / 1000)),
            end=time.strftime('%Y-%m-%d %H:%M:%S', time.gmtime(end_time_unix / 1000)),
            bar='1h'
        )
        eprint(candle_result)
        data = candle_result['Data']

        if data.size == 0:
            break

        for row in data:
            utc_time = time.strftime('%d/%m/%Y %H:%M:%S', time.gmtime(row[0] / 1000))
            unix_time = int(row[0] / 1000)
            open_price = float(row[1])
            high_price = float(row[2])
            low_price = float(row[3])
            close_price = float(row[4])
            volume = float(row[5])  # Assuming this is a numeric value that needs to be included in the CSV

            csv_data.append([symbol, utc_time, unix_time, open_price, high_price, low_price, close_price, volume])

        # 更新起始时间以获取下一批数据
        start_time_unix = int(data[-1][0]) + 1  # 移动到最后一个数据时间点之后的下一个时间点

    return csv_data


from alpaca.data.requests import CryptoBarsRequest
from alpaca.data.timeframe import TimeFrame
import yfinance as yf
import pandas as pd

# 设置参数
symbol = 'DOGE-USD'  # 例如，比特币对美元的代号是 'BTC-USD'
start_time = '2022-08-17'
end_time = '2022-08-25'
interval = '1h'

if __name__ == '__main__':
    # header = ['symbol', 'utctime', 'unixtime', 'open', 'high', 'low', 'close', 'volume']
    # Data = yf.download(tickers=symbol, start=start_time, end=end_time, interval=interval)
    # print(Data)
    # # Creating request object
    # request_params = CryptoBarsRequest(
    #     symbol_or_symbols=["ETH/USD"],
    #     timeframe=TimeFrame.Hour,
    #     start="2020-09-01",
    #     end="2020-10-02"
    # )
    # btc_bars = client.get_crypto_bars(request_params)
    # print(btc_bars.df)
    # Write to CSV
    # output_file = './' + symbol + '.csv'
    # with open(output_file, 'w', newline='') as file:
    #     writer = csv.writer(file)
    #     writer.writerow(header)
    #
    #
    # print(f"CSV file has been created: {output_file}")
    symbol_buy = 'BTCUSDT'.replace("USDT", '')
    print(symbol_buy)