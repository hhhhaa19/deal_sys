# 项目安装和运行指南

## 步骤 1: 安装火狐浏览器
本项目需要使用火狐浏览器（Firefox），请确保你的计算机上已安装。如果尚未安装，你可以从[火狐官网](https://www.mozilla.org/en-US/firefox/new/)下载并安装。

## 步骤 2: 配置代理或VPN
由于国内环境访问某些资源可能受限，建议在运行项目前配置代理或VPN以确保网络通畅。

## 步骤 3: 下载并配置MySQL
确保你的系统上安装了MySQL。如果还没有安装，可以从[MySQL官方网站](https://dev.mysql.com/downloads/mysql/)下载适合你操作系统的版本。安装后，根据项目需求配置MySQL数据库，并确保在项目的`Config`文件中正确设置数据库连接参数。

## 步骤 3: 安装Python依赖
项目运行前需要安装必要的Python库。打开命令行工具，切换到项目目录下，运行以下命令安装依赖：

pip install -r requirements.txt
步骤 4: 运行项目
依赖安装完成后，可以通过以下命令运行项目：

python deal.py
确保在项目根目录下运行上述命令。
