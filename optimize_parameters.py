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
from run_back_testing import run_back_testing


def optimize(input_file, output_folder, pipes, method, size_pop, max_iter, config, *, begin, end, offset, test_begin, tz):
    # 时区
    config['tz'] = tz

    # 载入数据
    df = load_candle_by_ext(input_file)
    # 按时间过滤
    opt_end = end if not test_begin else test_begin
    df = filter_candle_dataframe_by_begin_end_offset_datetime(df, begin, opt_end, offset, tz=tz)

    # 优化参数
    optimizer = Optimizer(method, size_pop, max_iter, config)
    opt_pipes = ['data.copy_dataframe', *pipes]
    best_x, best_y, hist, conf = optimizer.run(df, opt_pipes, run_mode='multiprocessing')
    print(f'parameters: {best_x}, {EQUITY_CURVE_COLUMN}: {best_y}')
    conf_arr = [f'{k}={conf[k]}' for k in conf]
    print('config: ', ' '.join(conf_arr))

    # 输出路径
    config['output_folder'] = output_folder = Path(output_folder) / datetime.now().strftime('%Y%m%d_%H%M%S')
    output_folder.mkdir(parents=True, exist_ok=True)
    # 保存数据
    result_file = output_folder / 'result.csv'
    print('save result to: ', result_file)
    hist.to_csv(result_file)

    # 运行回测
    print('run back testing...')
    back_test_output = output_folder / 'test'
    test_begin = begin if not test_begin else test_begin
    run_back_testing(input_file, output_folder.__str__(), [*opt_pipes, 'evaluation.report'], conf, begin=test_begin, end=end, offset=offset, tz=tz.zone,
                     output_path=back_test_output.__str__())


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='optimize parameters')
    parser.add_argument('input', help='history candle file')
    parser.add_argument('-m', '--method', default='GA', help='method, support: GA, PSO, DE, default: GA')
    parser.add_argument('-s', '--population', type=int, default=50, help='population, default: 50')
    parser.add_argument('-i', '--max-iteration', type=int, default=100, help='max iteration, default: 100')
    parser.add_argument('-o', '--output', default='../runs/optimize/',
                        help='result output folder, default: ../runs/optimize/')
    parser.add_argument('-p', '--pipes', nargs='+', required=True, help='pipelines')
    parser.add_argument('-b', '--begin', help='begin date')
    parser.add_argument('-d', '--end', help='end date')
    parser.add_argument('--skip-days', default=0, help='skip days from data begin time, default: 0')
    parser.add_argument('--test-begin', help='back testing begin date')
    parser.add_argument('-z', '--timezone', default='UTC',
                        help='begin, end date timezone(not for candle begin time), default: UTC')
    parser.add_argument('-c', '--config', nargs='*', action=ParseKwargs)
    args = parser.parse_args()

    start_time = timeit.default_timer()
    optimize(args.input, args.output, args.pipes, args.method, args.population, args.max_iteration, args.config, begin=args.begin, end=args.end,
             offset=args.skip_days, test_begin=args.test_begin, tz=str_to_timezone(args.timezone))
    end_time = timeit.default_timer()
    elapse = (end_time - start_time) / 60 / 60
    print(f'done, takes {elapse:.4f} hours')
