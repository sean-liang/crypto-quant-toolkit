from functools import partial
import pandas as pd


class WrapPandasTa:
    """
    包装pandas_ta的方法为pipeline形式
    """

    def __init__(self, ta_func, columns=[], strip_column=True, **kwargs):
        self._ta_func = partial(ta_func, **kwargs)
        self._columns = columns
        self._strip_column = strip_column

    def func(self, df, **kwargs):
        series = [df[col] for col in self._columns]
        res = self._ta_func(*series)
        if self._strip_column:
            res = res.rename(columns={col: col.split('_')[0] for col in res.columns})
        return pd.concat((df, res), axis=1)
