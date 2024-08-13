import mysql.connector
from datetime import datetime
from config import Config
import logging

# 配置日志
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

try:
    # 创建数据库连接
    connection = mysql.connector.connect(
        host=Config.MYSQL_HOST,  # 主机名或IP地址
        user=Config.MYSQL_USER,  # 用户名
        password=Config.MYSQL_PASSWORD,  # 密码
        database=Config.MYSQL_DB  # 数据库名
    )
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
