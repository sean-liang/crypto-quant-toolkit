import numpy as np
import pandas as pd
from commons.constants import CANDLE_DATETIME_COLUMN, SIGNAL_COLUMN, POSITION_COLUMN


def position_from_signal(df, **kwargs):
    """
    通过信号计算持仓情况
    """
    # 信号发出后，当前K线已经接近结束，从下一根K线开始时间变更持仓
    df[POSITION_COLUMN] = df[SIGNAL_COLUMN].shift(1)
    df[POSITION_COLUMN].fillna(value=0, inplace=True)
    return df


def disallowed_transaction_daily_time(df, utc_hour=8, utc_minute=0, **kwargs):
    """
    针对每天特定时刻不允许交易的情况，调整持仓
    :param df: dataframe
    :param utc_hour: UTC时
    :param utc_minute: UTC分钟
    :return: 调整后的dataframe
    """
    hour_cond = df[CANDLE_DATETIME_COLUMN].dt.hour == utc_hour
    minute_cond = df[CANDLE_DATETIME_COLUMN].dt.minute == utc_minute
    df[POSITION_COLUMN] = np.where(hour_cond & minute_cond, pd.NaT, df[POSITION_COLUMN])
    df[POSITION_COLUMN].fillna(method='ffill', inplace=True)
    return df
