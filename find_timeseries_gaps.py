import argparse
import pandas as pd
from commons.constants import CANDLE_DATETIME_COLUMN


def find_time_series_gaps(file, threshold):
    df = pd.read_parquet(file)
    df.sort_values(CANDLE_DATETIME_COLUMN, inplace=True)
    df = df[[CANDLE_DATETIME_COLUMN]]
    df['begin'] = df[CANDLE_DATETIME_COLUMN].shift(1)
    df.rename(columns={CANDLE_DATETIME_COLUMN: 'end'}, inplace=True)
    df.dropna(inplace=True)
    df = df[['begin', 'end']]
    df['gap_seconds'] = df['end'] - df['begin']
    df['gap_minutes'] = df['gap_seconds'].dt.total_seconds() / 60
    df['gap_hours'] = df['gap_minutes'] / 60

    gaps = df[df['gap_minutes'] >= threshold]
    gaps = gaps.sort_values('gap_minutes', ascending=False, ignore_index=True)
    print(gaps[['begin', 'end', 'gap_hours']])


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='find gaps in time series data')
    parser.add_argument('file', help='parquet file')
    parser.add_argument('-t', '--threshold', type=int, default=60, help='gap threshold in minutes, default: 60')
    args = parser.parse_args()

    find_time_series_gaps(args.file, args.threshold)
