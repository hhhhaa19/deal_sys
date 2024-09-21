import logging

import numpy as np
import torch
from RL_brain2 import DQN
import mysql.connector
import pandas as pd
from stock_env import *
from RL_brain2 import DeepQNetwork
from model_run import *
from dao import *

# 配置日志记录器
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')


def get_last_24_hours_close_prices(db_config, trading_pair):
    connection = mysql.connector.connect(**db_config)
    cursor = connection.cursor()
    query = """
    SELECT close_price, volume, high_price, low_price, open_price
    FROM historical_bars_data3_1h_bian_new
    WHERE symbol = %s
    ORDER BY utctime DESC
    LIMIT 25
    """
    cursor.execute(query, (trading_pair,))
    result = cursor.fetchall()
    df = pd.DataFrame(result, columns=['close', 'volume', 'high', 'low', 'open'])
    df = df.astype(float)
    df = df.iloc[::-1].reset_index(drop=True)
    cursor.close()
    connection.close()
    return df


# wjt修改
def load_model(model_path, n_features, n_actions, device):
    model = load_model_from_file(model_path)
    model.to(device)
    return model


def get_action(host, user, password, database, model_path, h_in, trading_pair):
    db_config = {
        'host': host,
        'user': user,
        'password': password,
        'database': database
    }

    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

    n_features = 24  # 使用过去24小时的close价格
    n_actions = 3  # 动作数

    # 加载模型
    model = load_model(model_path, n_features, n_actions, device)
    logging.info("模型加载成功")
    scaler = StandardScaler()
    file_path = 'Data/BTC_cleaned_s6.6.csv'
    df = pd.read_csv(file_path)
    df = df.reset_index(drop=True)  # 去除前几天没有均线信息
    df["Real_close"] = df["close"]
    df_train = df.iloc[0:50000]
    # 从数据库中获取数据
    df1 = pd.DataFrame(get_last_24_hours_close_prices(db_config, trading_pair))
    df2 = pd.DataFrame(get_impact_data_news(trading_pair))
    df3 = pd.DataFrame(generate_mock_data(25))
    df_test = pd.concat([df1, df2, df3], axis=1)
    df_test["Real_close"] = df_test["close"]
    columns_to_normalize = ['open', 'high', 'low', 'close', 'volume', "Regulatory Impact_news",
                            "Technological Impact_news",
                            "Market Adoption Impact_news", "Macroeconomic Implications_news", "Overall Sentiment_news",
                            "Virality potential_x", "Informative value_x", "Sentiment polarity_x", "Impact duration_x",
                            "Regulatory Impact_x", "Technological Impact_x", "Market Adoption Impact_x",
                            "Macroeconomic Implications_x", "Overall Sentiment_x"]
    df_train[columns_to_normalize] = scaler.fit_transform(df_train[columns_to_normalize])
    df_test[columns_to_normalize] = scaler.transform(df_test[columns_to_normalize])
    env = stock(df_test)
    logging.info("输入模型的数据加载成功")
    # 获取初始状态
    observation = env.reset()
    observation_tensor = torch.from_numpy(observation).float().to(device)

    # 将状态转换为 PyTorch tensor
    prob, h_out = model.pi(observation_tensor, h_in)
    prob = prob.view(-1)
    action = torch.argmax(prob).item()
    logging.info("当前action {}".format(action))
    return action, h_out


from config import *

if __name__ == '__main__':
    device = torch.device("cpu")
    h_in = (torch.zeros([1, 1, 128], dtype=torch.float).to(device),
            torch.zeros([1, 1, 128], dtype=torch.float).to(device))
    get_action(db_config.get('host'),
               db_config.get('user'),
               db_config.get('password'),
               db_config.get('database'),
               Config.MODEL_LOCATION,
               h_in,
               'BTCUSDT')
