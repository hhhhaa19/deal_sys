
if __name__ == '__main__':
    trading_pair = 'BTCUSDT'
    symbol_sell = 'USDT'
    symbol_buy = trading_pair.replace(trading_pair, 'USDT')
    print(symbol_sell, symbol_buy, trading_pair)
