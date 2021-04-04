from commons.constants import CANDLE_COLUMNS, CANDLE_DATETIME_COLUMN, CANDLE_OPEN_COLUMN, CANDLE_CLOSE_COLUMN, \
    CANDLE_HIGH_COLUMN, CANDLE_LOW_COLUMN, CANDLE_VOLUME_COLUMN


def build(params):
    return resample_time_window


def resample_time_window(df, resample_period='15T', resample_drop_zero_volume='1', resample_drop_zero_open='1',
                         **kwargs):
    """合成长时间K线"""
    period_df = df.resample(rule=resample_period, on=CANDLE_DATETIME_COLUMN, label='left', closed='left').agg(
        {
            CANDLE_OPEN_COLUMN: 'first',
            CANDLE_HIGH_COLUMN: 'max',
            CANDLE_LOW_COLUMN: 'min',
            CANDLE_CLOSE_COLUMN: 'last',
            CANDLE_VOLUME_COLUMN: 'sum',
        })

    # 去除一天都没有交易的周期
    if resample_drop_zero_open == '1':
        period_df.dropna(subset=[CANDLE_OPEN_COLUMN], inplace=True)

    if resample_drop_zero_volume == '1':
        period_df = period_df[period_df[CANDLE_VOLUME_COLUMN] > 0]

    period_df.reset_index(inplace=True)
    df = period_df[CANDLE_COLUMNS]

    # df.to_parquet('../data/course/BTC-USDT_15m.parquet')

    return df
