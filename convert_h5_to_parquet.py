import argparse
import pandas as pd
from commons.constants import CANDLE_COLUMNS, CANDLE_DATETIME_COLUMN


def convert_h5_to_parquet(h5_path, key, output_path):
    print('read: ', h5_path)
    if not key:
        store = pd.HDFStore(h5_path)
        print('keys: ', store.keys())
        store.close()
        exit()

    df = pd.read_hdf(h5_path, key=key)
    df = df[CANDLE_COLUMNS]
    df.sort_values(CANDLE_DATETIME_COLUMN, inplace=True)
    df.drop_duplicates(subset=[CANDLE_DATETIME_COLUMN], inplace=True)
    df.reset_index(inplace=True, drop=True)

    if not output_path:
        output_path = h5_path.replace('.h5', '.parquet')
    df.to_parquet(output_path)
    print('write: ', output_path)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='convert h5 to parquet')
    parser.add_argument('input', help='h5 file')
    parser.add_argument('-o', '--output', help='output file')
    parser.add_argument('-k', '--key', help='h5 key')
    args = parser.parse_args()

    convert_h5_to_parquet(args.input, args.key, args.output)
