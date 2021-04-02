from pathlib import Path
import pandas as pd


def load_candle_by_ext(path):
    if isinstance(path, str):
        path = Path(path)
    ext = path.name.split('.')[-1].strip().lower()
    if ext is 'csv':
        return pd.read_csv(path)
    elif ext is 'h5':
        return pd.read_hdf(path, key='/df')
    elif ext in ['par', 'parquet']:
        return pd.read_parquet(path)
