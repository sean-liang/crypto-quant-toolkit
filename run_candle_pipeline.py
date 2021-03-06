import argparse
import timeit
from pathlib import Path
from commons.io import load_candle_by_ext
from commons.datetime_utils import str_to_timezone
from commons.dataframe_utils import filter_candle_dataframe_by_begin_end_offset_datetime
from pipeline.pipeline import Pipeline

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='run back testing')
    parser.add_argument('pipeline', help='pipeline template file')
    parser.add_argument('input', help='history candle files')
    parser.add_argument('-s', '--scopes', nargs='+', help='pipeline scopes')
    parser.add_argument('-b', '--begin', help='begin date')
    parser.add_argument('-d', '--end', help='end date')
    parser.add_argument('-k', '--skip-days', default=0, help='skip days from data begin time, default: 0')
    parser.add_argument('-z', '--timezone', default='UTC', help='begin, end date timezone(not for candle begin time), default: UTC')
    args = parser.parse_args()

    # 载入管道
    pipeline = Pipeline.build_from_template(args.pipeline, verbose=True)
    # 时区
    pipeline.context['timezone'] = timezone = str_to_timezone(args.timezone)
    # 载入数据
    data = load_candle_by_ext(args.input)
    data = filter_candle_dataframe_by_begin_end_offset_datetime(data, args.begin, args.end, args.skip_days, tz=timezone)

    # 运行回测
    start_time = timeit.default_timer()
    res = pipeline.process(data, scopes=set(args.scopes) if args.scopes else None)
    end_time = timeit.default_timer()
    elapse = end_time - start_time

    if isinstance(res, (tuple, list)):
        for item in res:
            print('-' * 150)
            print(item)
    elif isinstance(res, dict):
        for key in res:
            size = (150 - len(key)) // 2
            print('-' * size, key, '-' * size)
            print(res[key])
    else:
        print('-' * 150)
        print(res)
    print('-' * 150)
    print(f'done, takes {elapse:.2f}s')
