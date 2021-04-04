import argparse
from commons.io import load_candle_by_ext
from commons.constants import CANDLE_DATETIME_COLUMN
from commons.datetime_utils import timezone_offset_delta, str_to_timezone


def find_time_series_gaps(file, column, threshold, timezone):
    print('file: ', file)
    print('column: ', column)
    print(f'threshold: {threshold} days')
    print(f'output timezone: {timezone.zone}')

    df = load_candle_by_ext(file)
    df = df[[column]]
    df['begin'] = df[column].shift(1)
    df.rename(columns={column: 'end'}, inplace=True)
    df.dropna(inplace=True)
    df = df[['begin', 'end']]
    df['gap_seconds'] = df['end'] - df['begin']
    df['gap_minutes'] = df['gap_seconds'].dt.total_seconds() / 60
    df['gap_hours'] = df['gap_minutes'] / 60

    gaps = df[df['gap_minutes'] >= threshold]
    gaps = gaps.sort_values('gap_minutes', ascending=False, ignore_index=True)
    gaps['begin'] += timezone_offset_delta(timezone)
    gaps['end'] += timezone_offset_delta(timezone)
    print(gaps[['begin', 'end', 'gap_hours']])


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='find gaps in time series data')
    parser.add_argument('file', help='input file')
    parser.add_argument('-c', '--column', default=CANDLE_DATETIME_COLUMN, help=f'datetime column name, default: {CANDLE_DATETIME_COLUMN}')
    parser.add_argument('-t', '--threshold', type=int, default=60, help='gap threshold in minutes, default: 60')
    parser.add_argument('-z', '--timezone', default='UTC', help='output timezone, default: UTC')
    args = parser.parse_args()

    find_time_series_gaps(args.file, args.column, args.threshold, timezone=str_to_timezone(args.timezone))
