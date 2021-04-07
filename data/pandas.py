def with_dataframe(df, method, **kwargs):
    """
    包装pandas的dataframe方法为pipeline形式
    """
    func = getattr(df, method)
    new_df = func(**kwargs)
    return df if new_df is None or ('inplace' in kwargs and kwargs['inplace']) else new_df
