import argparse
import time
from pathlib import Path
from datetime import datetime, timedelta, timezone
import pytz
import pandas as pd
from tqdm import tqdm
import ccxt


def find_symbols(exchange, trade_type, patterns):
    columns = ['symbol', 'type', 'taker', 'maker', 'amount_precision', 'price_precision']
    print('load markets...')
    markets = exchange.load_markets()
    print(f'{len(markets)} symbols found')
    data = [[v['symbol'], v['type'], v['taker'], v['maker'], v['precision']['amount'], v['precision']['price']] for v in
            markets.values()]
    df = pd.DataFrame(data, columns=columns)
    if trade_type:
        df = df[df['type'].str.contains(trade_type)]
    if patterns:
        conds = None
        for pat in patterns:
            c = df['symbol'].str.contains(pat) | df['symbol'].str.match(pat, case=False)
            conds = conds | c if conds is not None else c
        df = df[conds]
    df.reset_index(inplace=True, drop=True)
    print(df)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='find symbols in market')
    parser.add_argument('exchange', help='ccxt supported exchange, default: binance')
    parser.add_argument('type', help='type: spot, future, option, margin, delivery')
    parser.add_argument('-p', '--patterns', nargs='+', help=f'symbol string or regex patterns')
    args = parser.parse_args()

    # 交易所
    exchange_name = args.exchange.strip().lower()
    exchange = getattr(ccxt, exchange_name)({
        'options': {
            'defaultType': args.type
        }
    })
    print(f'exchange: {exchange_name}')

    # 交易对
    patterns = None
    if args.patterns:
        patterns = [pat.strip() for pat in args.patterns]
        print(f'patterns: ', ', '.join(patterns))

    # 交易类型
    if args.type:
        print('trade type: ', args.type)

    # 查找
    find_symbols(exchange, args.type, patterns)
