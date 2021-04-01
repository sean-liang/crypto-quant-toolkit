import argparse
import importlib
import pytz
from datetime import datetime, timezone
import timeit
import pandas as pd
from commons.argparse_commons import ParseKwargs
from commons.datetime_utils import begin_of_day, end_of_day
from commons.constants import CANDLE_DATETIME_COLUMN
from pipeline.pipeline import Pipeline


def run_back_testing(input_file, pipes, config, *, begin, end, tz):
    # 载入策略
    print('pipeline parameters: ', config)
    pipeline = Pipeline()
    for p in pipes:
        pipe = importlib.import_module(p)
        pipeline.extend(pipe.build(config))
        print(f'load pipe: {pipe.__name__}')

    # 载入数据
    df = pd.read_parquet(input_file)
    tz = pytz.timezone(args.timezone) if tz else timezone.utc
    candle_date = df[CANDLE_DATETIME_COLUMN].dt.date
    if begin:
        begin = begin_of_day(datetime.strptime(begin, '%Y-%m-%d'), tz=tz)
        df = df[candle_date >= begin.date()]
    if end:
        end = end_of_day(datetime.strptime(end, '%Y-%m-%d'), tz=tz)
        df = df[candle_date <= end.date()]

    # 运行回测
    start_time = timeit.default_timer()
    df = pipeline.process(df)
    end_time = timeit.default_timer()
    elapse = end_time - start_time
    print(f'calculation takes {elapse:.2f}s')
    print(df[df['signal'].notnull()])


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='run back testing')
    parser.add_argument('input', help='history candle parquet file')
    parser.add_argument('-p', '--pipes', nargs='+', required=True, help='pipelines')
    parser.add_argument('-b', '--begin', help='begin date')
    parser.add_argument('-d', '--end', help='end date')
    parser.add_argument('-z', '--timezone', default='UTC', help='timezone, default: UTC')
    parser.add_argument('-c', '--config', nargs='*', action=ParseKwargs)
    args = parser.parse_args()

    run_back_testing(args.input, args.pipes, args.config, begin=args.begin, end=args.end, tz=args.timezone)
