import numpy as np
import pandas as pd
from commons.constants import CANDLE_DATETIME_COLUMN, CANDLE_OPEN_COLUMN, CANDLE_CLOSE_COLUMN, CANDLE_LOW_COLUMN, \
    CANDLE_HIGH_COLUMN, POSITION_COLUMN
from commons.math import np_floor_to_precision


class FuturePnL:
    """
    计算合约交易资金曲线
    """

    def __init__(self, pnl_cash=10000, pnl_face_value=0.01, pnl_min_trade_precision=0, pnl_leverage_rate=1,
                 pnl_slippage_mode='ratio', pnl_slippage=0.001, pnl_commission=0.0002, pnl_min_margin_ratio=0.01,
                 **kwargs):
        self._cash = float(pnl_cash)
        self._face_value = float(pnl_face_value)
        self._min_trade_precision = float(pnl_min_trade_precision)
        self._leverage_rate = float(pnl_leverage_rate)
        self._slippage_mode = pnl_slippage_mode
        self._slippage = float(pnl_slippage)
        self._commission = float(pnl_commission)
        self._min_margin_ratio = float(pnl_min_margin_ratio)

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
        df.loc[open_pos_cond, 'start_time'] = df[CANDLE_DATETIME_COLUMN]
        df['start_time'].fillna(method='ffill', inplace=True)
        df.loc[df[POSITION_COLUMN] == 0, 'start_time'] = pd.NaT

        # 买入合约数 = 固定资金 * 杠杆 / (合约面值 * 开盘价)
        df.loc[open_pos_cond, 'contract_num'] = self._contract_num(df[CANDLE_OPEN_COLUMN])
        # 根据滑点计算实际开仓价格
        df.loc[open_pos_cond, 'open_pos_price'] = self._price_with_slippage(df[CANDLE_OPEN_COLUMN], df[POSITION_COLUMN],
                                                                            open_pos_cond)
        # 保证金（扣减手续费）
        df['cash'] = self._cash - df['open_pos_price'] * self._face_value * df['contract_num'] * self._commission

        # 买入之后，contract_num, open_pos_price, cash不再发生变动
        cols = ['contract_num', 'open_pos_price', 'cash']
        for col in cols:
            df[col].fillna(method='ffill', inplace=True)
        df.loc[df[POSITION_COLUMN] == 0, cols] = np.NaN

        # 根据滑点计算实际平仓价格
        df.loc[close_pos_cond, 'close_pos_price'] = df['next_open'] * (1 - self._slippage * df[POSITION_COLUMN])
        # 平仓手续费
        df.loc[close_pos_cond, 'close_pos_fee'] = df['close_pos_price'] * self._face_value * df[
            'contract_num'] * self._commission

        # 持仓盈亏
        df['profit'] = self._face_value * df['contract_num'] * (df[CANDLE_CLOSE_COLUMN] - df['open_pos_price']) * df[
            POSITION_COLUMN]
        df.loc[close_pos_cond, 'profit'] = self._face_value * df['contract_num'] * (
                df['close_pos_price'] - df['open_pos_price']) * df[POSITION_COLUMN]

        # 账户净值
        df['net_value'] = df['cash'] + df['profit']

        # 计算爆仓
        df.loc[df[POSITION_COLUMN] == 1, 'price_min'] = df[CANDLE_LOW_COLUMN]
        df.loc[df[POSITION_COLUMN] == -1, 'price_min'] = df[CANDLE_HIGH_COLUMN]
        df['profit_min'] = self._face_value * df['contract_num'] * (df['price_min'] - df['open_pos_price']) * df[
            POSITION_COLUMN]
        df['net_value_min'] = df['cash'] + df['profit_min']  # 账户净值最小值
        df['margin_ratio'] = df['net_value_min'] / (self._face_value * df['contract_num'] * df['price_min'])  # 计算最低保证金率
        df.loc[df['margin_ratio'] <= (self._min_margin_ratio + self._commission), 'blow_up'] = 1  # 计算是否爆仓

        # 平仓时扣除手续费
        df.loc[close_pos_cond, 'net_value'] -= df['close_pos_fee']
        # 当下一根K线价格突变，在平仓的时候爆仓，要做相应处理。此处处理有省略，不精确。
        df.loc[close_pos_cond & (df['net_value'] < 0), 'blow_up'] = 1

        # 对爆仓进行处理
        df['blow_up'] = df.groupby('start_time')['blow_up'].fillna(method='ffill')
        df.loc[df['blow_up'] == 1, 'net_value'] = 0

        # 计算资金曲线
        df['equity_change'] = df['net_value'].pct_change()
        df.loc[open_pos_cond, 'equity_change'] = df.loc[open_pos_cond, 'net_value'] / self._cash - 1  # 开仓日的收益率
        df['equity_change'].fillna(value=0, inplace=True)
        df['equity_curve'] = (1 + df['equity_change']).cumprod()

        # 删除不必要的数据
        df.drop(['next_open', 'contract_num', 'open_pos_price', 'cash', 'close_pos_price', 'close_pos_fee',
                 'profit', 'net_value', 'price_min', 'profit_min', 'net_value_min', 'margin_ratio', 'blow_up'],
                axis=1, inplace=True)

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
            return np.where(cond, fixed_slippage(price_series, self._slippage), np.NaN)
        elif self._slippage_mode is 'ratio':
            # 比例滑点
            return np.where(cond, ratio_slippage(price_series, direction_series, self._slippage), np.NaN)
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
