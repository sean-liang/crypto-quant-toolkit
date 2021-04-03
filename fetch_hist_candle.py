import argparse
import time
from pathlib import Path
import pandas as pd
from tqdm import tqdm
import ccxt
from commons.time_interval import TimeInterval
from commons.datetime_utils import dt_to_str, ts_to_str, dt_to_mills, str_to_timezone
from commons.argparse_commons import parse_period_arguments
from commons.daily_candle_csv_writer import DailyCandleCSVWriter


def fetch_hist_ohlc(exchange, symbols, intervals, begin_dt, end_dt, output_folder, *, market='spot', npr=1000,
                    sleep=0.1, tz):
    """
    使用ccxt抓取并保存指定交易所、多组交易对、指定时间段的K线历史数据
    :param exchange: ccxt交易所
    :param symbols: 交易对列表，如: ['BTC/USDT', 'ETH/USDT']
    :param intervals: K线的时长，如: ['5m', '15m']
    :param begin_dt: 抓取起始时间，datetime对象
    :param end_dt: 抓取终止时间，datetime对象
    :param output_folder: csv数据保存路径，路径及文件名规则为：<output_folder>/<exchange>/<date>/<symbol>_<interval>.csv，如：./data/spot/binance/20210327/BTC-USDT_5m.csv
    :param market: 交易市场，现货 spot, 期货 future
    :param npr: 每次请求的返回的最大数据条数，不能大于交易所限制
    :param sleep: 两次请求之间的休息时间（秒），防止请求过于频繁而被阻止
    :param tz: 时区
    """
    # 按交易所保存
    output_folder = output_folder / args.exchange / market
    mills_per_second = 1000  # 1秒 = 1000毫秒
    end_ts = dt_to_mills(end_dt)  # 终止时间毫秒
    total_steps = len(intervals) * len(symbols)
    current_step = 0
    error_list = []
    for interval in intervals:
        # 计算抓取切片的开始时间
        interval = TimeInterval(interval)
        delta_millis = mills_per_second * interval.delta.total_seconds()  # 每一根K线的毫秒数
        step = int(delta_millis * npr)  # 两次请求开始时间间隔（毫秒）
        begin_ts_points = range(dt_to_mills(begin_dt), end_ts, step)  # 每一次请求的开始时间（毫秒）列表

        for sym in symbols:
            current_step += 1
            print(f'[{current_step} / {total_steps}] fetch {sym} {interval.s} candle data ...')
            writer = DailyCandleCSVWriter(output_folder, sym, interval.s, tz)
            pbar = tqdm(begin_ts_points, desc=dt_to_str(begin_dt))
            for begin_ts in pbar:
                # 计算当次抓取记录数
                end = min(end_ts, begin_ts + step - mills_per_second)
                limit = int((end + mills_per_second - begin_ts) / delta_millis)
                # 更新状态条
                period_str = f'{ts_to_str(begin_ts, tz)} - {ts_to_str(end, tz)}'
                pbar.set_description(period_str)
                # 获取数据
                try:
                    payload = exchange.fetch_ohlcv(symbol=sym, timeframe=interval.s, since=begin_ts, limit=limit)
                    writer.append(payload)
                except Exception as e:
                    print(e)
                    error_list.append('_'.join([sym, interval.s, period_str]))
                # 歇一会
                time.sleep(sleep)
            # 将缓存数据写入磁盘
            writer.save()
    if error_list:
        print(f'Errors: {error_list}')


def get_matched_symbols(exchange, symbols):
    """
    在交易所的所有交易对中进行匹配
    :param exchange: ccxt交易所
    :param symbols: 待匹配的交易对列表
    :return: 交易所中所有匹配的交易对列表
    """
    exchange.load_markets()
    markets = pd.DataFrame(exchange.markets.keys(), columns=['symbol'])
    results = []
    for sym in symbols:
        results.extend(markets[markets['symbol'].str.match(sym, case=False)]['symbol'].tolist())
    return results


if __name__ == '__main__':
    default_symbols = ['BTC/USDT', 'ETH/USDT', 'EOS/USDT', 'LTC/USDT']
    default_intervals = ['5m', '15m']

    parser = argparse.ArgumentParser(description='fetch history candle data')
    parser.add_argument('-e', '--exchange', default='binance', help='ccxt supported exchange, default: binance')
    parser.add_argument('-s', '--symbols', nargs='+', default=default_symbols,
                        help=f'symbols, default: {" ".join(default_symbols)}')
    parser.add_argument('-i', '--intervals', nargs='+', default=default_intervals,
                        help=f'candle intervals, default: {" ".join(default_intervals)}')
    parser.add_argument('-b', '--begin', help='begin date, default: date of 31 days ago')
    parser.add_argument('-d', '--end', help='end date, default: date of yesterday')
    parser.add_argument('-p', '--periods', type=int,
                        help='fetch period in days, works when only one of begin or end is specified')
    parser.add_argument('-z', '--timezone', default='UTC',
                        help='begin, end date timezone(not for candle begin time), default: UTC')
    parser.add_argument('-o', '--output', default='../data', help='output folder, default: ../data')
    parser.add_argument('--market', default='spot', help='market, default: spot')
    parser.add_argument('--items-per-request', type=int, default=1000,
                        help='candle items per request, default: 1000')
    parser.add_argument('--sleep', type=float, default=1, help='seconds to sleep between requests, default: 1')
    parser.add_argument('--match-symbols', action='store_true', help='extract symbols by matching market symbols')
    args = parser.parse_args()

    # 交易所
    exchange_name = args.exchange.strip().lower()
    exchange = getattr(ccxt, exchange_name)()
    print(f'exchange: {exchange_name}')

    # 交易对
    symbols = [sym.strip().upper() for sym in args.symbols]
    if args.match_symbols:
        symbols = get_matched_symbols(exchange, symbols)
    print(f'symbols: {(", ").join(symbols)}')

    # K线时长
    candle_intervals = [interval.strip().lower() for interval in args.intervals]
    print(f'candle intervals: {(", ").join(candle_intervals)}')

    # 时区
    tz = str_to_timezone(args.timezone)
    begin, end = parse_period_arguments(args.begin, args.end, args.periods, tz=tz)
    print(f'fetch period: {dt_to_str(begin)} ~ {dt_to_str(end)}, timezone: {tz.zone}')

    # 输出文件夹
    output_folder = Path(args.output)
    print(f'output folder: {output_folder}')

    # 开始抓取
    fetch_hist_ohlc(exchange, symbols, candle_intervals, begin, end, output_folder, market=args.market,
                    npr=args.items_per_request, sleep=args.sleep, tz=tz)
