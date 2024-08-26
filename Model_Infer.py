import numpy as np
import torch
from RL_brain2 import DQN
import mysql.connector
import pandas as pd
from stock_env import *
from RL_brain2 import DeepQNetwork
from model_run import *


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


def load_model(model_path, n_features, n_actions, device):
    model = DQN(n_features, n_actions).to(device)
    model.load_state_dict(torch.load(model_path))
    model.eval()
    return model


def get_action(host, user, password, database, model_path):
    db_config = {
        'host': host,
        'user': user,
        'password': password,
        'database': database
    }

    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    print(f"Using device: {device}")

    n_features = 24  # 使用过去24小时的close价格
    n_actions = 3  # 动作数

    # 加载模型
    model = load_model(model_path, n_features, n_actions, device)

    # 从数据库中获取数据
    df = get_last_24_hours_close_prices(db_config)
    df["Real_close"] = df["close"]

    env = stock(df)

    # 获取初始状态
    observation = env.get_state(env.window_size)

    # 检查 observation 是否为 numpy 数组
    if not isinstance(observation, np.ndarray):
        raise ValueError("observation is not a numpy array")

    # 将状态转换为 PyTorch tensor
    observation_tensor = torch.tensor(observation[np.newaxis, :], dtype=torch.float32).to(device)

    # 使用模型进行预测
    with torch.no_grad():
        prediction = model(observation_tensor)

    print("Q-values for each action:", prediction)

    action = torch.argmax(prediction).item()
    return action
