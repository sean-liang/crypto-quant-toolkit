import argparse
from pathlib import Path
import pandas as pd
from tqdm import tqdm
from commons.constants import CANDLE_COLUMNS, CANDLE_DATETIME_COLUMN


def merge_daily_csv_files(root_path, names):
    root_path = Path(root_path)

    pbar = tqdm(names)
    for fn in pbar:
        pbar.set_description(fn)
        dfs = []
        for child in root_path.glob('*'):
            f = child / (fn + '.csv')
            if f.exists():
                df = pd.read_csv(f, parse_dates=[CANDLE_DATETIME_COLUMN])
                dfs.append(df)
        if dfs:
            df = pd.concat(dfs, ignore_index=True)
            df = df[CANDLE_COLUMNS]
            df.sort_values(CANDLE_DATETIME_COLUMN, ignore_index=True, inplace=True)
            begin = df[CANDLE_DATETIME_COLUMN].iat[0].strftime('%Y%m%d')
            end = df[CANDLE_DATETIME_COLUMN].iat[-1].strftime('%Y%m%d')
            output_file = f'{fn}_{begin}_{end}.parquet'
            df[CANDLE_DATETIME_COLUMN] = df[CANDLE_DATETIME_COLUMN].astype("datetime64[ms]")
            df.to_parquet(root_path / output_file)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='merge daily candle csv files to single parquet file')
    parser.add_argument('-r', '--root', default='../data/binance/spot/',
                        help='root path, default: ../data/binance/spot/')
    parser.add_argument('-n', '--names', nargs="+",
                        default=['BTC-USDT_5m', 'ETH-USDT_5m', 'LTC-USDT_5m', 'EOS-USDT_5m'],
                        help='file names, default: BTC-USDT_5m ETH-USDT_5m LTC-USDT_5m EOS-USDT_5m')
    args = parser.parse_args()

    print('root: ', args.root)
    print('names: ', ', '.join(args.names))

    merge_daily_csv_files(args.root, args.names)
