import mysql.connector
from datetime import datetime
import sqlite3
from config import Config
import logging
import pandas as pd

# 配置日志
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

db_config = Config.db_config


def insert_data(account_balance):
    try:
        # 创建数据库连接
        with mysql.connector.connect(**db_config) as connection:
            with connection.cursor() as cursor:
                insert_query = """
                INSERT INTO wallet_balances (timestamp, asset, free_balance)
                VALUES (%s, %s, %s)
                """
                data = (account_balance['timestamp'], account_balance['asset'], account_balance['free'])
                cursor.execute(insert_query, data)
                # 提交更改
                connection.commit()
                logging.info(f"Inserted Data: {data}")
    except mysql.connector.Error as err:
        logging.error(f"Error: {err}")
        if connection.is_connected():
            connection.rollback()


def query_data():
    try:
        # 创建数据库连接
        with mysql.connector.connect(**db_config) as connection:
            with connection.cursor() as cursor:
                select_query = "SELECT * FROM wallet_balances ORDER BY timestamp"
                cursor.execute(select_query)
                data = cursor.fetchall()
                logging.info("Fetched Data from wallet_balances")
                return data
    except mysql.connector.Error as err:
        logging.error(f"Error: {err}")


def get_impact_data_news(trading_pair):
    # 连接 SQLite 数据库
    connection = sqlite3.connect(Config.SQLITE_LOCATION)
    cursor = connection.cursor()
    trading_pair = Config.sqlite_corresponding_argument[trading_pair]
    try:
        # 构建表名
        table_name = f"{trading_pair}_meta_llama_Meta_Llama_3_1_8B_Instruct_Turbo_news"

        # 执行查询
        query = f"""
        SELECT regulatory_impact, technological_impact, market_adoption_impact,
               macroeconomic_implications, overall_sentiment
        FROM {table_name}
        LIMIT 25
        """
        cursor.execute(query)
        results = cursor.fetchall()

        # 创建 DataFrame，并为每列设置适当的名称
        df = pd.DataFrame(results, columns=[
            'Regulatory Impact_news',
            'Technological Impact_news',
            'Market Adoption Impact_news',
            'Macroeconomic Implications_news',
            'Overall Sentiment_news'  # 注意这里移除了前面的空格
        ])

        # 日志记录结果
        logging.info(f"Data retrieved from {table_name}")

        return df
    except sqlite3.Error as e:
        logging.error(f"An error occurred in SQLite: {e}")
    finally:
        # 关闭数据库连接
        cursor.close()
        connection.close()


def get_impact_data_x(trading_pair):
    # 连接 SQLite 数据库
    connection = sqlite3.connect(Config.SQLITE_LOCATION)
    cursor = connection.cursor()
    trading_pair = Config.sqlite_corresponding_argument[trading_pair]
    try:
        # 构建表名
        table_name = f"{trading_pair}_meta_llama_Meta_Llama_3_1_8B_Instruct_Turbo_x"

        # 执行查询
        query = f"""
        SELECT regulatory_impact, technological_impact, market_adoption_impact,
               macroeconomic_implications, overall_sentiment
        FROM {table_name}
        """
        cursor.execute(query)
        results = cursor.fetchall()
        logging.info(f"Data retrieved from {table_name}")
        return results
    except sqlite3.Error as e:
        logging.error(f"An error occurred in SQLite: {e}")
    finally:
        # 关闭数据库连接
        cursor.close()
        connection.close()


def generate_mock_data(num_rows):
    # 定义列名
    columns = [
        'Virality potential_x', 'Informative value_x', 'Sentiment polarity_x',
        'Impact duration_x', 'Regulatory Impact_x', 'Technological Impact_x',
        'Market Adoption Impact_x', 'Macroeconomic Implications_x', 'Overall Sentiment_x'
    ]

    # 生成模拟数据
    # np.random.rand(num_rows, len(columns)) 生成一个0到1之间的随机浮点数矩阵
    # 然后乘以10将范围调整到0到10
    data = np.random.rand(num_rows, len(columns)) * 10

    # 创建 DataFrame
    df = pd.DataFrame(data, columns=columns)

    return df


from Model_Infer import *

if __name__ == '__main__':
    # df1 = pd.DataFrame(get_last_24_hours_close_prices(Config.db_config, 'BTCUSDT'))
    # df2 = pd.DataFrame(get_impact_data_news('BTCUSDT'))
    # df3 = pd.DataFrame(generate_mock_data(25))
    # result = pd.concat([df1, df2,df3], axis=1)
    print(query_data())
    # print(result)
    # print(result.columns.tolist())
