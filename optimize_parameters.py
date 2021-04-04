import argparse
from pathlib import Path
from datetime import datetime
import timeit
from commons.constants import EQUITY_CURVE_COLUMN
from commons.io import load_candle_by_ext
from commons.datetime_utils import str_to_timezone
from commons.dataframe_utils import filter_candle_dataframe_by_begin_end_offset_datetime
from commons.argparse_commons import ParseKwargs
from optim.optimizer import Optimizer


def optimize(input_file, output_folder, pipes, method, size_pop, max_iter, config, *, begin, end, offset, tz):
    # 输出路径
    config['output_folder'] = output_folder = Path(output_folder) / datetime.now().strftime('%Y%m%d_%H%M%S')
    output_folder.mkdir(parents=True, exist_ok=True)

    # 时区
    config['tz'] = tz

    # 载入数据
    df = load_candle_by_ext(input_file)
    # 按时间过滤
    df = filter_candle_dataframe_by_begin_end_offset_datetime(df, begin, end, offset, tz=tz)

    # 优化参数
    optimizer = Optimizer(method, size_pop, max_iter, config)
    best_x, best_y, hist = optimizer.run(df, pipes, run_mode='multiprocessing')
    print(f'parameters: {best_x}, {EQUITY_CURVE_COLUMN}: {best_y}')

    result_file = output_folder / 'result.csv'
    print('save result to: ', result_file)
    hist.to_csv(result_file)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='optimize parameters')
    parser.add_argument('input', help='history candle file')
    parser.add_argument('-m', '--method', default='DE', help='method, support: GA, PSO, DE, default: DE')
    parser.add_argument('-s', '--population', type=int, default=50, help='population, default: 50')
    parser.add_argument('-i', '--max-iteration', type=int, default=100, help='max iteration, default: 100')
    parser.add_argument('-o', '--output', default='../runs/optimize/',
                        help='result output folder, default: ../runs/optimize/')
    parser.add_argument('-p', '--pipes', nargs='+', required=True, help='pipelines')
    parser.add_argument('-b', '--begin', help='begin date')
    parser.add_argument('-d', '--end', help='end date')
    parser.add_argument('--skip-days', default=0, help='skip days from data begin time, default: 0')
    parser.add_argument('-z', '--timezone', default='UTC',
                        help='begin, end date timezone(not for candle begin time), default: UTC')
    parser.add_argument('-c', '--config', nargs='*', action=ParseKwargs)
    args = parser.parse_args()

    start_time = timeit.default_timer()
    optimize(args.input, args.output, args.pipes, args.method, args.population, args.max_iteration, args.config, begin=args.begin, end=args.end,
             offset=args.skip_days, tz=str_to_timezone(args.timezone))
    end_time = timeit.default_timer()
    elapse = (end_time - start_time) / 60 / 60
    print(f'done, takes {elapse:.4f} hours')
