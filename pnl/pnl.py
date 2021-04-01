import numpy as np
import pandas as pd
from commons.constants import CANDLE_DATETIME_COLUMN, CANDLE_OPEN_COLUMN, CANDLE_CLOSE_COLUMN, POSITION_COLUMN
from commons.math import np_floor_to_precision


class ContractPnL:
    """
    计算合约交易资金曲线
    """

    def __init__(self, cash=10000, face_value=0.01, min_trade_precision=0, leverage_rate=1, slippage_mode='ratio',
                 slippage=0.001, commission=0.0002):
        self._cash = float(cash)
        self._face_value = float(face_value)
        self._min_trade_precision = float(min_trade_precision)
        self._leverage_rate = float(leverage_rate)
        self._slippage_mode = slippage_mode
        self._slippage = float(slippage)
        self._commission = float(commission)

    def calculate(self, df, **kwargs):
        # 找出下根K线的开盘价
        df['next_open'] = df[CANDLE_OPEN_COLUMN].shift(-1)
        df['next_open'].fillna(value=df[CANDLE_CLOSE_COLUMN], inplace=True)

        # 找出开、平仓的K线
        hold_pos_cond = df[POSITION_COLUMN] != 0  # 持仓
        open_pos_cond = df[POSITION_COLUMN] != df[POSITION_COLUMN].shift(1)  # 当前周期和上个周期持仓发生变化为开仓
        open_pos_cond = hold_pos_cond & open_pos_cond
        close_pos_cond = df[POSITION_COLUMN] != df[POSITION_COLUMN].shift(-1)  # 当前周期和下个周期持仓发生变化为平仓
        close_pos_cond = hold_pos_cond & close_pos_cond

        # 对每次交易进行分组
        df['start_time'] = np.where(open_pos_cond, df[CANDLE_DATETIME_COLUMN], pd.NaT)
        df['start_time'].fillna(method='ffill', inplace=True)
        df['start_time'] = np.where(df[POSITION_COLUMN] == 0, pd.NaT, df['start_time'])
        df['start_time'] = pd.to_datetime(df['start_time'])

        # 买入合约数 = 固定资金 * 杠杆 / (合约面值 * 开盘价)
        df['contract_num'] = np.where(open_pos_cond, self._contract_num(df['next_open']), pd.NaT)
        df['contract_num'].fillna(method='ffill', inplace=True)
        # 根据滑点计算实际开仓价格
        df['open_pos_price'] = self._price_with_slippage(df['next_open'], df[POSITION_COLUMN], open_pos_cond)
        df['open_pos_price'].fillna(method='ffill', inplace=True)
        # 根据滑点计算实际平仓价格
        df['close_pos_price'] = self._price_with_slippage(df['next_open'], -1 * df[POSITION_COLUMN],
                                                          close_pos_cond)
        # 平仓手续费
        df['close_pos_fee'] = df['close_pos_price'] * self._face_value * df['contract_num'] * self._commission
        # 资金（扣减手续费）
        df['cash'] = self._cash - df['open_pos_price'] * self._face_value * df['contract_num'] * self._commission
        df['cash'].fillna(method='ffill', inplace=True)
        # 持仓盈亏
        df['profit'] = np.where(close_pos_cond,
                                self._face_value * df['contract_num'] * (df['close_pos_price'] - df['open_pos_price']) * df[POSITION_COLUMN],
                                pd.NaT)
        df['net_value'] = df['cash'] + df['profit'] - df['close_pos_fee']

        return df

    def _contract_num(self, series):
        """
        计算合约数
        """
        return np_floor_to_precision(self._cash * self._leverage_rate / (self._face_value * series),
                                     self._min_trade_precision)

    def _price_with_slippage(self, price_series, direction_series, cond):
        """
        计算滑点
        """
        # 根据滑点计算实际开仓价格
        if self._slippage_mode is 'fixed':
            # 固定滑点
            return np.where(cond, fixed_slippage(price_series, self._slippage), pd.NaT)
        elif self._slippage_mode is 'ratio':
            # 比例滑点
            return np.where(cond, ratio_slippage(price_series, direction_series, self._slippage), pd.NaT)
        else:
            # 无滑点
            return price_series


def fixed_slippage(price_series, slippage):
    """
    固定滑点
    """
    return price_series + slippage


def ratio_slippage(price_series, direction_series, slippage):
    """
    比例滑点
    """
    return price_series * (1 + slippage * direction_series)
