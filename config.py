class Config:
    # 简化的数据库配置
    db_config = {
        'host': 'localhost',
        'user': 'root',
        'password': 'WJT164673!',
        'database': 'deal_sys'
    }
    # 保留其他配置项
    BIAN_KEY = 'cmDLLoAJEtez3TpzNspBkwwIsCwAA7s8fweeFLBap2kbefUYxor0NASJWhi3IruR'
    BIAN_SECRET = '4QVE8V1OSWRZAGzwo2xo4GCDTKvZw6ByMCE6qxReTc6IhCTvHuTDWTnVNtFKgG7x'
    BIAN_PROXY = None
    Trading_pair = {'BTCUSDT', 'DOGEUSDT', 'EOSUSDT', 'XRPUSDT'}  # 目标交易对
    MODEL_LOCATION = 'test_max_model.pkl'

if __name__ == '__main__':
    print(Config.db_config.get('host'))
