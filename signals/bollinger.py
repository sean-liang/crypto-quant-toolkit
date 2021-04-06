import numpy as np
from signals.commons import merge_long_short_signal
from commons.constants import CANDLE_CLOSE_COLUMN


def boll_trend(df):
    """
    布林线趋势信号，破上轨做多，下穿均线平多，破下轨做空，上穿均线平多
    """
    df_s1 = df.shift(1)

    # 做多
    long_cond1 = df[CANDLE_CLOSE_COLUMN] > df['BBU']  # 收盘价 > 上轨
    long_cond2 = df_s1[CANDLE_CLOSE_COLUMN] <= df_s1['BBU']  # 前收盘价 <= 前上轨
    df.loc[long_cond1 & long_cond2, 'signal_long'] = 1

    # 平多
    cover_long_cond1 = df[CANDLE_CLOSE_COLUMN] < df['BBM']  # 收盘价 < 均线
    cover_long_cond2 = df_s1[CANDLE_CLOSE_COLUMN] >= df_s1['BBM']  # 前收 >= 均线
    df.loc[cover_long_cond1 & cover_long_cond2, 'signal_long'] = 0

    # 做空
    short_cond1 = df[CANDLE_CLOSE_COLUMN] < df['BBL']  # 收盘价 < 下轨
    short_cond2 = df_s1[CANDLE_CLOSE_COLUMN] >= df_s1['BBL']  # 前收盘价 >= 前下轨
    df.loc[short_cond1 & short_cond2, 'signal_short'] = -1  # 破下轨，做空

    # 平空
    cover_short_cond1 = df[CANDLE_CLOSE_COLUMN] > df['BBM']  # 收盘价 > 均线
    cover_short_cond2 = df_s1[CANDLE_CLOSE_COLUMN] <= df_s1['BBM']  # 前收 <= 均线
    df.loc[cover_short_cond1 & cover_short_cond2, 'signal_short'] = 0  # 上穿均线，平空

    # 合并多空指标
    df = merge_long_short_signal(df, fill_na=True, drop_original=True)

    return df
