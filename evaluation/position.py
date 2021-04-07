import numpy as np
import pandas as pd
from commons.constants import CANDLE_DATETIME_COLUMN, SIGNAL_COLUMN, POSITION_COLUMN


def position_from_signal(df):
    """
    通过信号计算持仓情况
    """
    # 信号发出后，当前K线已经接近结束，从下一根K线开始时间变更持仓
    df[POSITION_COLUMN] = df[SIGNAL_COLUMN].shift()
    df[POSITION_COLUMN].fillna(value=0, inplace=True)

    return df


def disallow_transaction_daily(df, time):
    """
    针对每天特定时刻不允许交易的情况，调整持仓
    """
    hour, minute = [int(v) for v in time.split(':')]
    hour_cond = df[CANDLE_DATETIME_COLUMN].dt.hour == hour
    minute_cond = df[CANDLE_DATETIME_COLUMN].dt.minute == minute
    df[POSITION_COLUMN] = np.where(hour_cond & minute_cond, pd.NaT, df[POSITION_COLUMN])
    df[POSITION_COLUMN].fillna(method='ffill', inplace=True)

    return df


def _open_close_position_condition(df):
    """
    找出开、平仓的K线
    """
    hold_pos_cond = df[POSITION_COLUMN] != 0  # 持仓
    open_pos_cond = df[POSITION_COLUMN] != df[POSITION_COLUMN].shift(1)  # 当前周期和上个周期持仓发生变化为开仓
    open_pos_cond = hold_pos_cond & open_pos_cond
    close_pos_cond = df[POSITION_COLUMN] != df[POSITION_COLUMN].shift(-1)  # 当前周期和下个周期持仓发生变化为平仓
    close_pos_cond = hold_pos_cond & close_pos_cond

    return open_pos_cond, close_pos_cond
