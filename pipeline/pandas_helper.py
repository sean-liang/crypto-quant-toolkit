class WrapPandas:

    def __init__(self, pandas_func, **kwargs):
        self._func = pandas_func
        self._kwargs = kwargs

    def func(self, df):
        func = getattr(df, self._func)
        return func(**self._kwargs)


def dropna(df):
    return df.dropna()
