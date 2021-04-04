import argparse
from commons.argparse_commons import ParseKwargs
from commons.io import load_by_ext, save_by_ext
from data.resample_time_window import resample_time_window


def resample(input_path, interval, in_params, *, drop_zero_volume='1', drop_zero_open='1'):
    in_params = in_params if in_params else {}
    print('read: ', input_path)
    df = load_by_ext(input_path, **in_params)
    df = resample_time_window(df, interval, drop_zero_open, drop_zero_open)
    segments = input_path.split('.')
    output_path = '.'.join(segments[0:-1]) + f'_RESAMPLE_{interval}.' + segments[-1]
    print('write: ', output_path)
    save_by_ext(output_path, df, **in_params)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='resample candle data, supported formats: .csv, .h5, .parquet')
    parser.add_argument('input', help='input file')
    parser.add_argument('-i', '--interval', default='15T', help='resample period, default: 15T')
    parser.add_argument('--drop-zero-volume', type=str, default='1', help='drop zero volume')
    parser.add_argument('--drop-zero-open', type=str, default='1', help='drop zero open price')
    parser.add_argument('--input-config', nargs='*', action=ParseKwargs)
    args = parser.parse_args()

    resample(args.input, args.interval, args.input_config, drop_zero_volume=args.drop_zero_volume, drop_zero_open=args.drop_zero_open)
