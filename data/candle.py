from datetime import timedelta
from commons.constants import CANDLE_COLUMNS, CANDLE_DATETIME_COLUMN, CANDLE_OPEN_COLUMN, CANDLE_CLOSE_COLUMN, CANDLE_HIGH_COLUMN, CANDLE_LOW_COLUMN, \
    CANDLE_VOLUME_COLUMN


def resample_candle_time_window(df, period, drop_zero_volume=True, drop_zero_open=True):
    """
    合成长时间K线
    """
    period_df = df.resample(rule=period, on=CANDLE_DATETIME_COLUMN, label='left', closed='left').agg(
        {
            CANDLE_OPEN_COLUMN: 'first',
            CANDLE_HIGH_COLUMN: 'max',
            CANDLE_LOW_COLUMN: 'min',
            CANDLE_CLOSE_COLUMN: 'last',
            CANDLE_VOLUME_COLUMN: 'sum',
        })

    # 去除没有交易的K线
    if drop_zero_open:
        period_df.dropna(subset=[CANDLE_OPEN_COLUMN], inplace=True)
    if drop_zero_volume:
        period_df = period_df[period_df[CANDLE_VOLUME_COLUMN] > 0]

    period_df.reset_index(inplace=True)
    df = period_df[CANDLE_COLUMNS]

    return df


def skip_days(df, days):
    """
    忽略n天的k线
    """
    t = df.iloc[0][CANDLE_DATETIME_COLUMN] + timedelta(days=days)
    df.drop(df[df[CANDLE_DATETIME_COLUMN] <= t].index, inplace=True)
    return df


def add_next_open(df, col='next_open'):
    """
    找出下根K线的开盘价
    """
    df[col] = df[CANDLE_OPEN_COLUMN].shift(-1)
    df[col].fillna(value=df[CANDLE_CLOSE_COLUMN], inplace=True)
    return df
