# import requests
# import time
# from datetime import datetime
# import mysql.connector
# import pytz
#
# def fetch_history_klines(symbol, start, end, interval):
#     url = 'https://api.binance.com/api/v3/klines'
#     params = {
#         'symbol': symbol,
#         'interval': interval,
#         'startTime': start,
#         'endTime': end,
#         'limit': 500
#     }
#     response = requests.get(url, params=params)
#
#
#     return response.json()
#
# db_config = {
#     'host': 'localhost',
#     'user': 'root',
#     'password': '123456',
#     'database': 'alpacadata'
# }
#
# def connect_db():
#     # print('Connecting with the following credentials:', db_config)
#     connection = mysql.connector.connect(**db_config)
#     return connection
#
# def insert_bars_data(database, symbol, time, open_price, high_price, low_price, close_price, volume):
#     connection = connect_db()
#     cursor = connection.cursor()
#
#     unix_timestamp = int(int(time) / 1000)
#     utc_dt = datetime.utcfromtimestamp(unix_timestamp)
#
#     query = f'INSERT INTO {database} (symbol, utctime, unixtime, open_price, high_price, low_price, close_price, volume) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)'
#     values = (symbol, utc_dt, unix_timestamp, open_price, high_price, low_price, close_price, volume)
#     cursor.execute(f'SELECT * FROM {database} WHERE unixtime = %s', (unix_timestamp,))
#     exists = cursor.fetchall()
#     if not exists:
#         cursor.execute(query, values)
#     else:
#         print(f"Data already exists for {utc_dt}")
#     connection.commit()
#     cursor.close()
#     connection.close()
#
#
# symbol = 'BTCUSDT'
# interval = '1h'
# start_time = int(time.mktime(time.strptime('2017-08-16', '%Y-%m-%d')) * 1000)
# now = datetime.now(pytz.utc)
# print(now)
# end_time = int(now.timestamp() * 1000)
# print(end_time)
# current = start_time
#
# while current < end_time:
#     next_time = min(current + 30*24*60*60*1000, end_time)
#     print(next_time)
#     data = fetch_history_klines(symbol, current, next_time, interval)
#     current = next_time + 1
#     for kline in data:
#         # print(kline)
#         insert_bars_data('historical_bars_data3_1h_bian_new', symbol, kline[0], kline[1], kline[2], kline[3], kline[4], kline[5])
# # time.sleep(60)
import requests
import time
from datetime import datetime
import mysql.connector
import pytz
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')


def fetch_history_klines(symbol, start, end, interval):
    url = 'https://api.binance.com/api/v3/klines'
    params = {
        'symbol': symbol,
        'interval': interval,
        'startTime': start,
        'endTime': end,
        'limit': 500
    }
    response = requests.get(url, params=params)
    return response.json()


def connect_db(db_config):
    connection = mysql.connector.connect(**db_config)
    return connection


def insert_bars_data(database, symbol, time, open_price, high_price, low_price, close_price, volume, db_config):
    connection = connect_db(db_config)
    cursor = connection.cursor()

    unix_timestamp = int(int(time) / 1000)
    utc_dt = datetime.utcfromtimestamp(unix_timestamp)

    query = f'INSERT INTO {database} (symbol, utctime, unixtime, open_price, high_price, low_price, close_price, volume) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)'
    values = (symbol, utc_dt, unix_timestamp, open_price, high_price, low_price, close_price, volume)
    cursor.execute(f'SELECT * FROM {database} WHERE unixtime = %s', (unix_timestamp,))
    exists = cursor.fetchall()
    if not exists:
        cursor.execute(query, values)
    else:
        logging.warning(f"Data already exists for {utc_dt}")
    connection.commit()
    cursor.close()
    connection.close()


def update_database(start_date, db_config):
    symbol = 'BTCUSDT'
    interval = '1h'
    start_time = int(time.mktime(time.strptime(start_date, '%Y-%m-%d')) * 1000)
    now = datetime.now(pytz.utc).replace(minute=0, second=0, microsecond=0)
    end_time = int(now.timestamp() * 1000)
    current = start_time
    logging.info(f"Current UTC time rounded to the previous hour: {now}")

    while current < end_time:
        next_time = min(current + 30 * 24 * 60 * 60 * 1000, end_time)  # 每次获取30天的数据
        data = fetch_history_klines(symbol, current, next_time, interval)
        current = next_time + 1
        for kline in data:
            insert_bars_data('historical_bars_data3_1h_bian_new', symbol, kline[0], kline[1], kline[2], kline[3],
                             kline[4], kline[5], db_config)
        # 根据API速率限制，可适当增加延时
        time.sleep(1)


if __name__ == "__main__":
    db_config = {
        'host': 'localhost',
        'user': 'root',
        'password': 'WJT164673!',
        'database': 'deal_sys'
    }
    start_date = "2024-08-26"  # 起始日期
    update_database(start_date, db_config)
