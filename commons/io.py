from pathlib import Path
import pandas as pd
from commons.constants import CANDLE_COLUMNS, CANDLE_DATETIME_COLUMN

DEFAULT_HDF_KEY = '/df'


def extension(path):
    return path.name.split('.')[-1].strip().lower()


def load_by_ext(path, **kwargs):
    if isinstance(path, str):
        path = Path(path)
    ext = extension(path)
    if ext == 'csv':
        return pd.read_csv(path, **kwargs)
    elif ext == 'h5':
        if 'key' not in kwargs:
            store = pd.HDFStore(path)
            print('specify hdf key from this list: ', store.keys())
            store.close()
        else:
            return pd.read_hdf(path, **kwargs)
    elif ext in ['par', 'parquet']:
        return pd.read_parquet(path, **kwargs)

    raise RuntimeError(f'not supported: ', path)


def load_candle_by_ext(path, **kwargs):
    df = load_by_ext(path, **kwargs)
    df = df[CANDLE_COLUMNS]
    df.sort_values(CANDLE_DATETIME_COLUMN, inplace=True)
    df.drop_duplicates(subset=[CANDLE_DATETIME_COLUMN], inplace=True)
    df.reset_index(inplace=True, drop=True)
    df[CANDLE_DATETIME_COLUMN] = pd.to_datetime(df[CANDLE_DATETIME_COLUMN])
    return df


def save_by_ext(path, df: pd.DataFrame, **kwargs):
    if isinstance(path, str):
        path = Path(path)
    ext = extension(path)

    if ext is 'csv':
        df.to_csv(path, **kwargs)
    elif ext is 'h5':
        df.to_hdf(path, **kwargs)
    elif ext in ['par', 'parquet']:
        df.to_parquet(path, **kwargs)
