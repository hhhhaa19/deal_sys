class Config:
    # 简化的数据库配置
    db_config = {
        'host': 'localhost',
        'user': 'root',
        'password': 'WJT164673!',
        'database': 'deal_sys'
    }
    # 保留其他配置项
    BIAN_KEY = 'ugsuQUG1mQfBLDJACLhLkUmlwqtAEPFRHBg7MzKzuTMuBabf2XzlnIoJ31rVIEt6'
    BIAN_SECRET = 'YpGfU1TxEdmJnOGvkxo5TUGC8Tg9L2tkkqPLtkwQVTHSf1y80aUEPppofeLU2Lof'
    BIAN_PROXY = None
    Trading_pair = {'BTCUSDT', 'DOGEUSDT', 'EOSUSDT', 'XRPUSDT'}  # 目标交易对
    MODEL_LOCATION = 'test_max_model.pkl'

if __name__ == '__main__':
    print(Config.db_config.get('host'))
