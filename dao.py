import mysql.connector
from datetime import datetime
from config import Config
import logging

# 配置日志
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

try:
    db_config = Config.db_config
    # 创建数据库连接
    connection = mysql.connector.connect(**db_config)
    cursor = connection.cursor()
    logging.info("Successfully connected to the database")


    def insert_data(account_balance):
        try:
            insert_query = """
            INSERT INTO wallet_balances (timestamp, asset, free_balance)
            VALUES (%s, %s, %s)
            """
            data = (account_balance['timestamp'], account_balance['asset'], account_balance['free'])
            cursor.execute(insert_query, data)
            # 提交更改
            connection.commit()
            logging.info(f"Inserted data: {data}")
        except mysql.connector.Error as err:
            logging.error(f"Error: {err}")
            connection.rollback()


    def query_data():
        try:
            select_query = "SELECT * FROM wallet_balances ORDER BY timestamp"
            cursor.execute(select_query)
            data = cursor.fetchall()
            logging.info("Fetched data from wallet_balances")
            return data
        except mysql.connector.Error as err:
            logging.error(f"Error: {err}")

except mysql.connector.Error as err:
    logging.error(f"Error connecting to database: {err}")

import sqlite3


def get_impact_data(trading_pair):
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
        """
        cursor.execute(query)
        results = cursor.fetchall()
        logging.info(f"Data retrieved from {table_name}: {results}")
        return results
    except sqlite3.Error as e:
        logging.error(f"An error occurred in SQLite: {e}")
    finally:
        # 关闭数据库连接
        cursor.close()
        connection.close()


if __name__ == '__main__':
    print(get_impact_data('BTCUSDT'))
