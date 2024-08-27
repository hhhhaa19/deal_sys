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


def get_last_24_hours_close_prices(db_config):
    connection = mysql.connector.connect(**db_config)
    cursor = connection.cursor()
    query = """
    SELECT close_price, volume, high_price, low_price, open_price
    FROM historical_bars_data3_1h_bian_new
    ORDER BY utctime DESC
    LIMIT 25
    """
    cursor.execute(query)
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


def get_action(host, user, password, database, model_path,h_in):
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


    # 从数据库中获取数据
    df = get_last_24_hours_close_prices(db_config)
    df["Real_close"] = df["close"]
    env = stock(df)
    scaler = StandardScaler()
    columns_to_normalize = ['open', 'high', 'low', 'close', 'volume']
    df[columns_to_normalize] = scaler.fit_transform(df[columns_to_normalize])
    logging.info("输入模型的数据加载成功")
    # 获取初始状态
    observation = env.reset()
    observation_tensor = torch.from_numpy(observation).float().to(device)

    # 将状态转换为 PyTorch tensor
    prob, h_out = model.pi(observation_tensor, h_in)
    prob = prob.view(-1)
    action = torch.argmax(prob).item()
    logging.info("当前action")
    return action, h_out
