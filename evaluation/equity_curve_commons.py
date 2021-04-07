import numpy as np
import pandas as pd
from commons.constants import CANDLE_DATETIME_COLUMN, POSITION_COLUMN, CANDLE_LOW_COLUMN, CANDLE_HIGH_COLUMN
from commons.math import np_floor_to_precision
from evaluation.slippage import price_with_slippage


def _group_trade(df, open_cond, col='start_time'):
    """
    设置每组交易的开仓时间
    """
    df['start_time'] = np.where(open_cond, df[CANDLE_DATETIME_COLUMN], pd.NaT)
    df['start_time'].fillna(method='ffill', inplace=True)
    df['start_time'] = np.where(df[POSITION_COLUMN] == 0, pd.NaT, df['start_time'])
    df['start_time'] = pd.to_datetime(df['start_time'])


def _contract_number(price, cash, leverage_rate, face_value, min_trade_precision):
    """
    买入合约数 = 固定资金 * 杠杆 / (合约面值 * 开盘价)
    """
    return np_floor_to_precision(cash * leverage_rate / (face_value * price), min_trade_precision)


def _future_margin(price, contract_num, cash, face_value, commission):
    """
    保证金（扣减手续费）
    """
    return cash - price * face_value * contract_num * commission


def _fill_unchanged_columns(df, *cols):
    """
    填充仓位变化后不再改变的列
    """
    for col in cols:
        df[col].fillna(method='ffill', inplace=True)
    df.loc[df[POSITION_COLUMN] == 0, cols] = np.NaN


def _net_value(open_price, close_price, position, next_open, contract_num, margin, close_cond, slippage, slippage_mode, face_value, commission):
    """
    计算账户净值
    """
    # 根据滑点计算实际平仓价格
    close_pos_price = price_with_slippage(slippage, slippage_mode, next_open, -1 * position, close_cond)
    # 平仓手续费
    close_pos_fee = np.where(close_cond, close_pos_price * face_value * contract_num * commission, np.NaN)

    # 持仓盈亏
    profit = face_value * contract_num * (close_price - open_price) * position
    profit = np.where(close_cond, face_value * contract_num * (close_pos_price - open_price) * position, profit)

    # 账户净值
    net_value = margin + profit
    # 平仓时扣除手续费
    net_value = np.where(close_cond, net_value - close_pos_fee, net_value)

    return net_value


def _blow_up(df, close_cond, face_value, min_margin_ratio, commission, *, col='blow_up'):
    """
    计算爆仓
    """
    # 计算爆仓
    price_min = np.where(df[POSITION_COLUMN] == 1, df[CANDLE_LOW_COLUMN], np.NaN)
    price_min = np.where(df[POSITION_COLUMN] == -1, df[CANDLE_HIGH_COLUMN], price_min)
    profit_min = face_value * df['contract_num'] * (price_min - df['open_pos_price']) * df[POSITION_COLUMN]
    net_value_min = df['margin'] + profit_min  # 账户净值最小值
    margin_ratio = net_value_min / (face_value * df['contract_num'] * price_min)  # 计算最低保证金率
    df[col] = np.where(margin_ratio <= (min_margin_ratio + commission), 1, np.NaN)  # 计算是否爆仓

    # 当下一根K线价格突变，在平仓的时候爆仓，要做相应处理。此处处理有省略，不精确。
    df[col] = np.where(close_cond & (df['net_value'] < 0), 1, df[col])

    # 对爆仓进行处理
    df[col] = df.groupby('start_time')[col].fillna(method='ffill')
    df.loc[df[col] == 1, 'net_value'] = 0


def _equity_curve(net_value, open_cond, cash):
    """
    计算资金曲线
    """
    equity_change = net_value.pct_change()
    equity_change.loc[open_cond] = net_value.loc[open_cond] / cash - 1  # 开仓日的收益率
    equity_change.fillna(value=0, inplace=True)
    return (1 + equity_change).cumprod()
