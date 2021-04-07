from functools import partial
import pandas as pd


def wrap(df, method, columns=[], strip_column=True, **kwargs):
    """包装pandas_ta的方法为pipeline形式"""
    series = [df[col] for col in columns]
    func = partial(method, **kwargs)
    res = func(*series)
    if strip_column:
        res = res.rename(columns={col: col.split('_')[0] for col in res.columns})
    return pd.concat((df, res), axis=1)
