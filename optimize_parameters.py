import argparse
from pathlib import Path
from datetime import datetime
import timeit
from commons.io import load_candle_by_ext
from commons.datetime_utils import str_to_timezone
from commons.dataframe_utils import filter_candle_dataframe_by_begin_end_offset_datetime
from commons.argparse_commons import ParseKwargs
from pipeline.pipeline import Pipeline


def optimize(input_file, output_folder, pipes, config, *, begin, end, offset, tz):
    # 输出路径
    config['output_folder'] = output_folder = Path(output_folder) / datetime.now().strftime('%Y%m%d_%H%M%S')
    output_folder.mkdir(parents=True, exist_ok=True)

    # 时区
    config['tz'] = tz = str_to_timezone(args.timezone)

    # 载入策略
    pipeline = Pipeline.build(pipes, config)

    # 载入数据
    df = load_candle_by_ext(input_file)
    # 安时间过滤
    df = filter_candle_dataframe_by_begin_end_offset_datetime(df, begin, end, offset, tz=tz)

    # 运行回测
    pipeline.process(df)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='optimize parameters')
    parser.add_argument('input', help='history candle file')
    parser.add_argument('-o', '--output', default='../runs/optimize/',
                        help='result output folder, default: ../runs/optimize/')
    parser.add_argument('-p', '--pipes', nargs='+', required=True, help='pipelines')
    parser.add_argument('-b', '--begin', help='begin date')
    parser.add_argument('-d', '--end', help='end date')
    parser.add_argument('--skip-days', default=0, help='skip days from data begin time, default: 0')
    parser.add_argument('-z', '--timezone', default='UTC',
                        help='begin, end date timezone(not for candle begin time), default: UTC')
    parser.add_argument('--pipe-config', nargs='*', action=ParseKwargs)
    args = parser.parse_args()

    start_time = timeit.default_timer()
    optimize(args.input, args.output, args.pipes, args.pipe_config, begin=args.begin, end=args.end,
             offset=args.skip_days, tz=str_to_timezone(args.timezone))
    end_time = timeit.default_timer()
    elapse = int((end_time - start_time) / 60 / 60)
    print(f'done, takes {elapse:.2f} hours')
