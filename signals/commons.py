def merge_long_short_signal(df, *, drop_original=False):
    """
    合并多空信号
    """

    # 合并多空信号
    df['signal'] = df[['signal_long', 'signal_short']].sum(axis=1, min_count=1, skipna=True)

    # 去除重复信号
    tmp_df = df[df['signal'].notnull()][['signal']]
    tmp_df = tmp_df[tmp_df['signal'] != tmp_df['signal'].shift(1)]

    df['signal'] = tmp_df['signal']
    if drop_original:
        df = df.drop(columns=['signal_long', 'signal_short'])
    return df
