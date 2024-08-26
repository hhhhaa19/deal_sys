# from maze_env import Maze
import pickle

from stock_env import stock
from RL_brain import PPO
import pandas as pd
import matplotlib.pyplot as plt
from sklearn.preprocessing import StandardScaler
import torch
from torch.distributions import Categorical
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")


def BackTest(env, model, show_log=True, my_trick=False):
    model.eval()
    observation = env.reset()
    rewards = 0
    h_out = (torch.zeros([1, 1, 128], dtype=torch.float).to(device), torch.zeros([1, 1, 128], dtype=torch.float).to(device))
    step = 0
    while True:
        h_in = h_out
        prob, h_out = model.pi(torch.from_numpy(observation).float(), h_in)
        prob = prob.view(-1)
        action = torch.argmax(prob).item()
        observation_, reward, done = env.step(action, show_log=False)
        rewards = rewards + reward
        observation = observation_
        # break while loop when end of this episode
        if done:
            break
        step += 1
    print('total_profit:%.3f' % (env.total_profit))
    model.train()
    return env, rewards


if __name__ == "__main__":
    max_round = 10001

    file_path = 'historical_bars_data_1h_bian_final.xlsx'
    df = pd.read_excel(file_path)
    df = df.reset_index(drop=True)  # 去除前几天没有均线信息
    df["Real_close"] = df["close"]

    df_train = df.iloc[20000:40000]
    df_test = df.iloc[40000:42500]

    scaler = StandardScaler()
    columns_to_normalize = ['open', 'high', 'low', 'close', 'volume']
    df_train[columns_to_normalize] = scaler.fit_transform(df_train[columns_to_normalize])  # 对选定的列应用 Z得分归一化
    df_test[columns_to_normalize] = scaler.fit_transform(df_test[columns_to_normalize])

    env_train = stock(df_train)
    env_test = stock(df_test)

    model = PPO(env_train.n_features, env_train.n_actions)
    step = 0
    training_profit = []
    testing_profit = []

    training_reward = []
    testing_reward = []

    train_max = 0
    test_max = 0

    for episode in range(max_round):
        # initial observation
        rewards = 0
        h_out = (torch.zeros([1, 1, 128], dtype=torch.float).to(device), torch.zeros([1, 1, 128], dtype=torch.float).to(device))
        observation = env_train.reset()
        # step = 0
        while True:
            h_in = h_out
            prob, h_out = model.pi(torch.from_numpy(observation).float(), h_in)
            prob = prob.view(-1)

            m = Categorical(prob)
            action = m.sample().item()
            observation_, reward, done = env_train.step(action, show_log=False)
            rewards = rewards + reward
            model.put_data((observation, action, reward, observation_, prob[action].item(), h_in, h_out, done))
            observation = observation_
            # break while loop when end of this episode
            step += 1
            # if step % 5 == 0 or done:
            #     model.train_net()
            if done:
                break
        if episode >= 10:
            model.train_net()
        print('epoch:%d, total_profit:%.3f' % (episode, env_train.total_profit))
        training_profit.append(env_train.total_profit)
        training_reward.append(rewards)

        if episode % 10 == 0:
            model_name = 'model/' + str(episode) + '.pkl'
            plt.clf()
            pickle.dump(model, open(model_name, 'wb'))

        env_test, test_rewards = BackTest(env_test,model, show_log=False)
        testing_profit.append(env_test.total_profit)
        testing_reward.append(test_rewards)

        if env_train.total_profit > train_max:
            train_max = env_train.total_profit
            model_name = 'model/train_max_model.pkl'
            plt.clf()
            pickle.dump(model, open(model_name, 'wb'))

        if env_test.total_profit > test_max:
            test_max = env_test.total_profit
            model_name = 'model/test_max_model.pkl'
            plt.clf()
            pickle.dump(model, open(model_name, 'wb'))

        if episode % 10 == 0:
            plt.plot(training_profit)
            plt.title('DQN_Episode_train_profits')
            plt.xlabel('Episode')
            plt.ylabel('train_profits')
            plt.savefig('Reward/training_profits')
            plt.close()

            plt.plot(testing_profit)
            plt.title('DQN_Episode_test_profits')
            plt.xlabel('Episode')
            plt.ylabel('test_profits')
            plt.savefig('Reward/testing_profits')
            plt.close()

            plt.plot(training_reward)
            plt.title('Train Reward')
            plt.xlabel('Episode')
            plt.ylabel('Reward')
            plt.savefig('Reward/Training Reward')
            plt.close()

            plt.plot(testing_reward)
            plt.title('Test Reward')
            plt.xlabel('Episode')
            plt.ylabel('Reward')
            plt.savefig('Reward/Testing Reward')
            plt.close()

            env_train, test_rewards = BackTest(env_train, model, show_log=False)
            env_train.draw('Trade/trade_train.png', 'Trade/profit_train.png')

            env_test, test_rewards_2 = BackTest(env_test, model, show_log=False)
            env_test.draw('Trade/trade_test.png', 'Trade/profit_test.png')

    # env_train = stock(df_train)
    # env_train, test_rewards = BackTest(env_train, show_log=False)
    # env_train.draw('Trade/trade_train.png', 'Trade/profit_train.png')
    #
    # env_test = stock(df_test)
    # env_test, test_rewards_2 = BackTest(env_test, show_log=True)
    # env_test.draw('Trade/trade_test.png', 'Trade/profit_test.png')

