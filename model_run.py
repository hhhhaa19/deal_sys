import pickle
import pandas as pd
from sklearn.preprocessing import StandardScaler
import torch
from stock_env import stock
import io
#本代码仅用于测试

class CPU_Unpickler(pickle.Unpickler):
    def find_class(self, module, name):
        if module == 'torch.storage' and name == '_load_from_bytes':
            # 当遇到 _load_from_bytes 时，重定向到自定义的加载函数
            return lambda b: torch.load(io.BytesIO(b), map_location='cpu')
        else:
            return super().find_class(module, name)


def load_model_from_file(file_path):
    with open(file_path, 'rb') as f:
        # 使用自定义的 Unpickler
        unpickler = CPU_Unpickler(f)
        model = unpickler.load()
    return model


def model_run():
    device = torch.device("cpu")
    model = load_model_from_file('test_max_model.pkl')
    model.to(device)
    file_path = 'historical_bars_data_1h_bian_final.xlsx'
    df = pd.read_excel(file_path)
    df = df.reset_index(drop=True)  # 去除前几天没有均线信息
    df["Real_close"] = df["close"]

    df_train = df.iloc[20000:40000]
    df_test = df.iloc[40000:42500]
    env_test = stock(df_test)
    scaler = StandardScaler()
    columns_to_normalize = ['open', 'high', 'low', 'close', 'volume']
    df_train[columns_to_normalize] = scaler.fit_transform(df_train[columns_to_normalize])
    df_test[columns_to_normalize] = scaler.fit_transform(df_test[columns_to_normalize])
    h_out = (torch.zeros([1, 1, 128], dtype=torch.float).to(device),
             torch.zeros([1, 1, 128], dtype=torch.float).to(device))
    h_in = h_out

    # 获取环境的初始观察
    observation = env_test.reset()
    observation_tensor = torch.from_numpy(observation).float().to(device)  # 转换为张量并移至正确的设备

    # 模型推断
    prob, h_out = model.pi(observation_tensor, h_in)
    prob = prob.view(-1)
    action = torch.argmax(prob).item()

    # 输出动作
    return action


if __name__ == '__main__':
    model_run()
