class WrapPandas:
    """
    包装pandas的dataframe方法为pipeline形式
    """

    def __init__(self, pandas_func, **kwargs):
        self._func = pandas_func
        self._kwargs = kwargs

    def func(self, df, **kwargs):
        func = getattr(df, self._func)
        return func(**self._kwargs)


def drop_na(df, **kwargs):
    return df.dropna()


def drop_column(df, **kwargs):
    return df.drop(columns=kwargs['columns'])
