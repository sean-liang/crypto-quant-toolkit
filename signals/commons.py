from commons.constants import SIGNAL_COLUMN


def merge_long_short_signal(df, *, column_name=SIGNAL_COLUMN, fill_na=True, drop_original=False):
    """
    合并多空信号
    """

    # 合并多空信号
    df[column_name] = df[['signal_long', 'signal_short']].sum(axis=1, min_count=1, skipna=True)

    # 去除重复信号
    tmp_df = df[df[column_name].notnull()][[column_name]]
    tmp_df = tmp_df[tmp_df[column_name] != tmp_df[column_name].shift(1)]

    df[column_name] = tmp_df[column_name]

    if drop_original:
        df.drop(columns=['signal_long', 'signal_short'], inplace=True)

    if fill_na:
        df[column_name].fillna(method='ffill', inplace=True)
        df[column_name].fillna(value=0, inplace=True)

    return df
