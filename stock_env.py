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

    def __init__(self, df, init_money=1000000, window_size=24):

        self.n_actions = 3  # 动作数量
        self.n_features = (window_size - 1) * 6  # 特征数量

        self.trend = df['Real_close'].values  # 收盘数据
        self.close = df['close'].values
        self.volume = df['volume'].values
        self.high = df['high'].values
        self.low = df['low'].values
        self.open = df['open'].values
        self.df = df  # 数据的DataFrame
        self.init_money = init_money  # 初始化资金

        self.window_size = window_size  # 滑动窗口大小
        self.t = self.window_size - 1
        self.buy_rate = 0.0003  # 买入费率
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

        self.profit_rate_account = []  # 账号盈利
        self.profit_rate_stock = []  # 股票波动情况

    def reset(self, init_money=1000000):
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
        block = list(itertools.chain.from_iterable(block))

        res = []
        for i in range(window_size - 1):
            res.append((block[i + 1] - block[i]) / (block[i] + 0.0001) * 1000)  # 每步收益
            res.append(block[i + 1 + window_size])
            res.append(block[i + 1 + window_size * 2])
            res.append(block[i + 1 + window_size * 3])
            res.append(block[i + 1 + window_size * 4])
            res.append(block[i + 1 + window_size * 5])

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
        self.buy_num = self.hold_money / self.trend[self.t]  # 买入手数
        self.buy_num = self.buy_num

        # 计算手续费等
        # tmp_money = self.trend[self.t] * self.buy_num
        # service_change = tmp_money * self.buy_rate
        # if service_change < self.buy_min:
        #     service_change = self.buy_min
        # # 如果手续费不够，就少买100股
        # if service_change + tmp_money > self.hold_money:
        #     self.buy_num = self.buy_num - 100
        # tmp_money = self.trend[self.t] * self.buy_num
        # service_change = tmp_money * self.buy_rate
        # if service_change < self.buy_min:
        #     service_change = self.buy_min

        self.hold_num += self.buy_num
        # self.stock_value += self.trend[self.t] * self.buy_num
        # self.hold_money = self.hold_money - self.trend[self.t] * \
        #     self.buy_num - service_change
        self.stock_value += self.trend[self.t] * self.buy_num
        self.hold_money = self.hold_money - self.trend[self.t] * self.buy_num
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

        if action == 1 and self.hold_money >= (self.trend[self.t] / 100):
            buy_ = True
            if my_trick and not self.trick():
                # 如果使用自己的触发器并不能出发买入条件，就不买
                buy_ = False
            if buy_:
                self.buy_stock()
                if show_log:
                    print('day:%d, buy price:%f, buy num:%d, hold num:%d, hold money:%.3f' % \
                          (self.t, self.trend[self.t], self.buy_num, self.hold_num, self.hold_money))

        elif action == 2 and self.hold_num > 0:
            # 卖出股票
            self.sell_stock(self.hold_num)
            if show_log:
                print(
                    'day:%d, sell price:%f, total balance %f,'
                    % (self.t, self.trend[self.t], self.hold_money)
                )
        else:
            if my_trick and self.hold_num > 0 and not self.trick():
                self.sell_stock(self.hold_num)
                if show_log:
                    print(
                        'day:%d, sell price:%f, total balance %f,'
                        % (self.t, self.trend[self.t], self.hold_money)
                    )

        self.stock_value = self.trend[self.t] * self.hold_num

        self.market_value = self.stock_value + self.hold_money
        self.total_profit = self.market_value - self.init_money

        # self.reward = (self.maket_value - self.last_value) / self.last_value
        reward = (self.trend[self.t + 1] - self.trend[self.t]) / self.trend[self.t]
        if np.abs(reward) <= 0.015:
            self.reward = reward * 0.2
        elif np.abs(reward) <= 0.03:
            self.reward = reward * 0.7
        elif np.abs(reward) >= 0.05:
            if reward < 0:
                self.reward = (reward + 0.05) * 0.1 - 0.05
            else:
                self.reward = (reward - 0.05) * 0.1 + 0.05

        # reward = (self.trend[self.t + 1] - self.trend[self.t]) / self.trend[self.t]
        if self.hold_num > 0 or action == 2:
            self.reward = reward
            if action == 2:
                self.reward = -self.reward
        else:
            self.reward = -self.reward * 0.1
            # self.reward = 0

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


