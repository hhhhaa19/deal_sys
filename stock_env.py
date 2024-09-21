# -*- coding: utf-8 -*-
"""
Created on Tue Feb  4 15:16:28 2020

@author: hcb
"""
import itertools
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt


class stock:

    def __init__(self, df, init_money=10000000, window_size=24):

        self.n_actions = 3  # 动作数量
        self.n_features = (window_size - 1) * 20  # 特征数量

        self.trend = df['Real_close'].values  # 收盘数据
        self.close = df['close'].values
        self.volume = df['volume'].values
        self.high = df['high'].values
        self.low = df['low'].values
        self.open = df['open'].values

        self.Regulatory_Impact_news = df['Regulatory Impact_news'].values
        self.Technological_Impact_news = df['Technological Impact_news'].values
        self.Market_Adoption_Impact_news = df['Market Adoption Impact_news'].values
        self.Macroeconomic_Implications_news = df['Macroeconomic Implications_news'].values
        self.Overall_Sentiment_news = df['Overall Sentiment_news'].values
        self.Virality_potential_x = df['Virality potential_x'].values
        self.Informative_value_x = df['Informative value_x'].values
        self.Sentiment_polarity_x = df['Sentiment polarity_x'].values
        self.Impact_duration_x = df['Impact duration_x'].values
        self.Regulatory_Impact_x = df['Regulatory Impact_x'].values
        self.Technological_Impact_x = df['Technological Impact_x'].values
        self.Market_Adoption_Impact_x = df['Market Adoption Impact_x'].values
        self.Macroeconomic_Implications_x = df['Macroeconomic Implications_x'].values
        self.Overall_Sentiment_x = df['Overall Sentiment_x'].values

        self.df = df  # 数据的DataFrame
        self.init_money = init_money  # 初始化资金

        self.window_size = window_size  # 滑动窗口大小
        self.t = self.window_size - 1
        self.buy_rate = 0.001  # 买入费率
        self.buy_min = 5  # 最小买入费率
        self.sell_rate = 0.001  # 卖出费率
        self.sell_min = 5  # 最大买入费率
        self.stamp_duty = 0.001  # 印花税

        self.hold_money = self.init_money  # 持有资金
        self.buy_num = 0  # 买入数量
        self.hold_num = 0  # 持有股票数量
        self.stock_value = 0  # 持有股票总市值
        self.market_value = 0  # 总市值（加上现金）
        self.last_value = self.init_money  # 上一天市值
        self.total_profit = 0  # 总盈利
        self.reward = 0  # 收益
        self.states_sell = []  # 卖股票时间
        self.states_buy = []  # 买股票时间
        self.no_trade_duration = 0

        self.profit_rate_account = []  # 账号盈利
        self.profit_rate_stock = []  # 股票波动情况

    def reset(self, init_money=10000000):
        self.init_money = init_money  # 初始化资金
        self.hold_money = self.init_money  # 持有资金
        self.buy_num = 0  # 买入数量
        self.hold_num = 0  # 持有股票数量
        self.stock_value = 0  # 持有股票总市值
        self.market_value = 0  # 总市值（加上现金）
        self.last_value = self.init_money  # 上一天市值
        self.total_profit = 0  # 总盈利
        self.reward = 0  # 收益
        self.states_sell = []  # 卖股票时间
        self.states_buy = []  # 买股票时间
        self.t = self.window_size - 1

        self.profit_rate_account = []  # 账号盈利
        self.profit_rate_stock = []  # 股票波动情况
        self.no_trade_duration = 0

        return self.get_state(self.t)


    def get_state(self, t):  # 某t时刻的状态
        window_size = self.window_size
        d = t - window_size + 1

        block = []
        block.append(self.trend[d: t + 1])
        block.append(self.close[d: t + 1])
        block.append(self.volume[d: t + 1])
        block.append(self.high[d: t + 1])
        block.append(self.low[d: t + 1])
        block.append(self.open[d: t + 1])

        block.append(self.Regulatory_Impact_news[d: t + 1])
        block.append(self.Technological_Impact_news[d: t + 1])
        block.append(self.Market_Adoption_Impact_news[d: t + 1])
        block.append(self.Macroeconomic_Implications_news[d: t + 1])
        block.append(self.Overall_Sentiment_news[d: t + 1])
        block.append(self.Virality_potential_x[d: t + 1])
        block.append(self.Informative_value_x[d: t + 1])
        block.append(self.Sentiment_polarity_x[d: t + 1])
        block.append(self.Impact_duration_x[d: t + 1])
        block.append(self.Regulatory_Impact_x[d: t + 1])
        block.append(self.Technological_Impact_x[d: t + 1])
        block.append(self.Market_Adoption_Impact_x[d: t + 1])
        block.append(self.Macroeconomic_Implications_x[d: t + 1])
        block.append(self.Overall_Sentiment_x[d: t + 1])
        block = list(itertools.chain.from_iterable(block))

        res = []
        for i in range(window_size - 1):
            res.append((block[i + 1] - block[i]) / (block[i] + 0.0001) * 1000)  # 每步收益
            res.append(block[i + 1 + window_size])
            res.append(block[i + 1 + window_size * 2])
            res.append(block[i + 1 + window_size * 3])
            res.append(block[i + 1 + window_size * 4])
            res.append(block[i + 1 + window_size * 5])

            res.append(block[i + 1 + window_size * 6])
            res.append(block[i + 1 + window_size * 7])
            res.append(block[i + 1 + window_size * 8])
            res.append(block[i + 1 + window_size * 9])
            res.append(block[i + 1 + window_size * 10])
            res.append(block[i + 1 + window_size * 11])
            res.append(block[i + 1 + window_size * 12])
            res.append(block[i + 1 + window_size * 13])
            res.append(block[i + 1 + window_size * 14])
            res.append(block[i + 1 + window_size * 15])
            res.append(block[i + 1 + window_size * 16])
            res.append(block[i + 1 + window_size * 17])
            res.append(block[i + 1 + window_size * 18])
            res.append(block[i + 1 + window_size * 19])

            # print((block[i + 1] - block[i]) / (block[i] + 0.0001)*100)
            # print(block[i + 1 + window_size])
            # print(block[i + 1 + window_size * 2])
            # print(block[i + 1 + window_size * 3])
            # print(block[i + 1 + window_size * 4])
            # print(block[i + 1 + window_size * 5])
            # print("////////////////////")

        return np.array(res)  # 作为状态编码


    def buy_stock(self):
        # 买入股票
        # print(self.hold_money)

        self.buy_num = self.hold_money / (self.trend[self.t] * 1.001)  # 买入手数

        # a = self.buy_num * self.trend[self.t]
        # print(a)

        # 计算手续费等
        tmp_money = self.trend[self.t] * self.buy_num
        service_change = tmp_money * self.buy_rate
        # if service_change < self.buy_min:
        #     service_change = self.buy_min
        # # 如果手续费不够，就少买100股
        # while service_change + tmp_money > self.hold_money:
        #     self.buy_num = self.buy_num - 0.01
        #     tmp_money = self.trend[self.t] * self.buy_num
        #     service_change = tmp_money * self.buy_rate
        # if service_change < self.buy_min:
        #     service_change = self.buy_min
        self.hold_num += self.buy_num
        # self.stock_value += self.trend[self.t] * self.buy_num
        # self.hold_money = self.hold_money - self.trend[self.t] * \
        #     self.buy_num - service_change
        self.stock_value += self.trend[self.t] * self.buy_num
        self.hold_money = self.hold_money - self.trend[self.t] * self.buy_num - service_change

        self.states_buy.append(self.t)

    def sell_stock(self, sell_num):
        tmp_money = sell_num * self.trend[self.t]
        service_change = tmp_money * self.sell_rate
        # if service_change < self.sell_min:
        #     service_change = self.sell_min
        # stamp_duty = self.stamp_duty * tmp_money
        # self.hold_money = self.hold_money + tmp_money - service_change - stamp_duty
        self.hold_money = self.hold_money + tmp_money - service_change
        self.hold_num = 0
        self.stock_value = 0
        self.states_sell.append(self.t)

    def trick(self):
        if self.df['close'][self.t] >= self.df['ma21'][self.t]:
            return True
        else:
            return False

    def step(self, action, show_log=False, my_trick=False):

        action_state = 0
        # 0: 持有并卖出
        # 1: 持有不卖出
        # 2: 不持有

        if action == 1 and self.hold_money >= self.trend[self.t]:
            buy_ = True
            # 持有不卖出
            action_state = 3
            self.no_trade_duration = 0

            # 买入股票
            self.buy_stock()
            if show_log:
                print('day:%d, buy price:%f, buy num:%d, hold num:%d, hold money:%.3f' % \
                      (self.t, self.trend[self.t], self.buy_num, self.hold_num, self.hold_money))
        elif action == 2 and self.hold_num > 0:
            # 持有并卖出
            action_state = 0
            self.no_trade_duration = 0
            # 卖出股票
            self.sell_stock(self.hold_num)
            if show_log:
                print(
                    'day:%d, sell price:%f, total balance %f,'
                    % (self.t, self.trend[self.t], self.hold_money)
                )
        else:
            # 无事发生
            self.no_trade_duration += 1
            if self.hold_num > 0:
                # 持有不动
                action_state = 1
            else:
                # 不持有不动
                action_state = 2

            # if my_trick and self.hold_num > 0 and not self.trick():
            #     self.sell_stock(self.hold_num)
            #     if show_log:
            #         print(
            #             'day:%d, sell price:%f, total balance %f,'
            #             % (self.t, self.trend[self.t], self.hold_money)
            #         )

        self.stock_value = self.trend[self.t] * self.hold_num
        self.market_value = self.stock_value + self.hold_money
        # print(f"Stock Value: {self.stock_value}, Hold Money: {self.hold_money}, Market Value: {self.market_value}, Initial Money: {self.init_money}")
        self.total_profit = self.market_value - self.init_money

        # reward = self.hold_money + (self.hold_num * self.trend[self.t]) - self.init_money
        # reward = (self.market_value - self.init_money) / self.init_money
        # reward = (self.market_value - self.last_value) / self.last_value

        # reward = (self.trend[self.t + 1] - self.trend[self.t]) / self.trend[self.t]
        # if np.abs(reward) <= 0.015:
        #     self.reward = reward * 0.2
        # elif np.abs(reward) <= 0.03:
        #     self.reward = reward * 0.7
        # elif np.abs(reward) >= 0.05:
        #     if reward < 0:
        #         self.reward = (reward + 0.005) * 0.1 - 0.05
        #     else:
        #         self.reward = (reward - 0.005) * 0.1 + 0.05

        # reward = (self.trend[self.t + 1] - self.trend[self.t]) / self.trend[self.t]

        # if self.hold_num > 0 or action == 2:
        #     self.reward = reward
        #     if action == 2:
        #         self.reward = -self.reward
        # else:
        #     self.reward = -self.reward * 0.1

        price_change_reward = (self.trend[self.t + 1] - self.trend[self.t]) / self.trend[self.t]
        # market_value_change_reward = (self.market_value - self.last_value) / self.last_value
        # long_term_reward = self.total_profit / self.init_money

        # 可以根据策略权重进行调整
        # reward = 0.5 * price_change_reward
        reward = price_change_reward

        # 持有并卖出
        if action_state == 0:
            # self.reward = -reward - 0.01 + 0.5 * long_term_reward
            self.reward = -reward - 0.001
        # 持有不卖出
        elif action_state == 1:
            # self.reward = reward + 0.5 * long_term_reward
            self.reward = reward
        # 不持有买入
        elif action_state == 3:
            # self.reward = reward - 0.01 + 0.5 * long_term_reward
            self.reward = reward - 0.001
        # 不持有
        else:
            self.reward = - reward * 0.1
            # if self.trend[self.t] > self.trend[self.t + 1]:  # 如果市场下跌
            #     self.reward = 0  # 不持有不惩罚
            # else:  # 如果市场上涨
            #     self.reward = - reward * 0.1  # 给予惩罚，鼓励持有

        # if self.no_trade_duration > 12:
        #     self.reward -= 0.001

        # # 假设 trend 是你的价格数据
        # price_changes = np.diff(self.trend)
        # volatility = np.std(price_changes)
        #
        # # 设置阈值，可以根据历史波动性来设置
        # some_threshold = volatility
        #
        # # 设置市场波动的奖励
        # if abs(price_change_reward) > some_threshold:  # 设置价格波动阈值
        #     self.reward += 0.01  # 增加奖励
        #     # self.reward *= 1.5

        self.last_value = self.market_value

        self.profit_rate_account.append((self.market_value - self.init_money) / self.init_money)
        self.profit_rate_stock.append(
            (self.trend[self.t] - self.trend[self.window_size - 1]) / self.trend[self.window_size - 1])
        done = False
        self.t = self.t + 1
        if self.t == len(self.trend) - 1:
            done = True
        s_ = self.get_state(self.t)
        reward = self.reward
        return s_, reward, done

    def get_info(self):
        return self.states_sell, self.states_buy, self.profit_rate_account, self.profit_rate_stock

    def draw(self, save_name1, save_name2):
        # 绘制结果
        states_sell, states_buy, profit_rate_account, profit_rate_stock = self.get_info()
        invest = profit_rate_account[-1]
        total_gains = self.total_profit
        close = self.trend
        fig = plt.figure(figsize=(15, 5))
        plt.plot(close, color='r', lw=2.)
        plt.plot(close, 'v', markersize=8, color='k', label='selling signal', markevery=states_sell)
        plt.plot(close, '^', markersize=8, color='m', label='buying signal', markevery=states_buy)
        plt.title('total gains %f, total investment %f%%' % (total_gains, invest))
        plt.legend()
        plt.savefig(save_name1)
        plt.close()

        fig = plt.figure(figsize=(15, 5))
        plt.plot(profit_rate_account, label='my account')
        plt.plot(profit_rate_stock, label='stock')
        plt.legend()
        plt.savefig(save_name2)
        plt.close()



