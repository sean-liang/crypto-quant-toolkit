import numpy as np
import pandas as pd
from commons.constants import CANDLE_CLOSE_COLUMN
from commons.debug import print_dataframe


def boll_trend(df):
    """
    布林线趋势信号，破上轨做多，下穿均线平多，破下轨做空，上穿均线平多
    """
    df_s1 = df.shift(1)

    # 做多
    long_cond1 = df[CANDLE_CLOSE_COLUMN] > df['BBU']  # 收盘价 > 上轨
    long_cond2 = df_s1[CANDLE_CLOSE_COLUMN] <= df_s1['BBU']  # 前收盘价 <= 前上轨
    df['signal_long'] = np.where(long_cond1 & long_cond2, 1, np.NaN)  # 破上轨做多

    # 平多
    cover_long_cond1 = df[CANDLE_CLOSE_COLUMN] < df['BBM']  # 收盘价 < 均线
    cover_long_cond2 = df_s1[CANDLE_CLOSE_COLUMN] >= df_s1['BBM']  # 前收 >= 均线
    df['signal_long'] = np.where(cover_long_cond1 & cover_long_cond2, 0, df['signal_long'])  # 下破均线，平多

    # 做空
    short_cond1 = df[CANDLE_CLOSE_COLUMN] < df['BBL']  # 收盘价 < 下轨
    short_cond2 = df_s1[CANDLE_CLOSE_COLUMN] >= df_s1['BBL']  # 前收盘价 >= 前下轨
    df['signal_short'] = np.where(short_cond1 & short_cond2, -1, np.NaN)  # 破下轨，做空

    # 平空
    cover_short_cond1 = df[CANDLE_CLOSE_COLUMN] > df['BBM']  # 收盘价 > 均线
    cover_short_cond2 = df_s1[CANDLE_CLOSE_COLUMN] <= df_s1['BBM']  # 前收 <= 均线
    df['signal_short'] = np.where(cover_short_cond1 & cover_short_cond2, 0, df['signal_short'])  # 上穿均线，平空

    return df


def boll_trend_with_safe_distance(df, safe_distance_pct):
    """
    布林趋势，加入价格与均线距离，在安全距离内开仓
    """
    # 计算标准布林趋势指标
    df = boll_trend(df)

    # 填充信号
    df['signal_long'].fillna(method='ffill', inplace=True)
    df['signal_short'].fillna(method='ffill', inplace=True)

    # 计算持仓时收盘价与均线的距离（绝对值百分比）
    distance_pct = np.where((df['signal_long'] == 1) | (df['signal_short'] == -1), np.abs(df[CANDLE_CLOSE_COLUMN] - df['BBM']) / df['BBM'], np.NaN)

    # 安全距离之内开仓
    signal_long_safe = np.where((df['signal_long'] == 1) & (distance_pct <= safe_distance_pct), 1, np.NaN)
    signal_short_safe = np.where((df['signal_short'] == -1) & (distance_pct <= safe_distance_pct), -1, np.NaN)
    # 复制平仓信号
    signal_long_safe = np.where((df['signal_long'] == 0) & (df['signal_long'] != df['signal_long'].shift(1)), 0, signal_long_safe)
    signal_short_safe = np.where((df['signal_short'] == 0) & (df['signal_short'] != df['signal_short'].shift(1)), 0, signal_short_safe)
    # 转为series
    signal_long_safe = pd.Series(signal_long_safe, name='signal_long_safe')
    signal_short_safe = pd.Series(signal_short_safe, name='signal_short_safe')
    # 填充信号
    signal_long_safe.fillna(method='ffill', inplace=True)
    signal_short_safe.fillna(method='ffill', inplace=True)
    # 仅保留仓位变化的点
    signal_long_safe = np.where((signal_long_safe == 0) & (signal_long_safe.shift(1).isnull()) | (signal_long_safe == signal_long_safe.shift(1)), np.NaN,
                                signal_long_safe)
    signal_short_safe = np.where((signal_short_safe == 0) & (signal_short_safe.shift(1).isnull()) | (signal_short_safe == signal_short_safe.shift(1)), np.NaN,
                                 signal_short_safe)
    # print_dataframe([distance_pct, df['signal_long'], signal_long_safe, df['signal_short'], signal_short_safe])
    # 替换原信号
    df['signal_long'] = signal_long_safe
    df['signal_short'] = signal_short_safe

    return df
