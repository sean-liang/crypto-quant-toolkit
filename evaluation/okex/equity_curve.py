import numpy as np
import pandas as pd
from commons.constants import CANDLE_DATETIME_COLUMN, CANDLE_OPEN_COLUMN, CANDLE_CLOSE_COLUMN, CANDLE_LOW_COLUMN, \
    CANDLE_HIGH_COLUMN, POSITION_COLUMN
from commons.math import np_floor_to_precision
from evaluation.slippage import price_with_slippage


class OKExEquityCurve:
    """
    计算OKEx合约交易资金曲线
    """

    def __init__(self, eval_cash=10000, eval_face_value=0.01, eval_min_trade_precision=0, eval_leverage_rate=1,
                 eval_slippage_mode='ratio', eval_slippage=0.001, eval_commission=0.0002, eval_min_margin_ratio=0.01,
                 **kwargs):
        self._cash = float(eval_cash)
        self._face_value = float(eval_face_value)
        self._min_trade_precision = float(eval_min_trade_precision)
        self._leverage_rate = float(eval_leverage_rate)
        self._slippage_mode = eval_slippage_mode
        self._slippage = float(eval_slippage)
        self._commission = float(eval_commission)
        self._min_margin_ratio = float(eval_min_margin_ratio)

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
        df['open_pos_price'] = price_with_slippage(self._slippage, self._slippage_mode, df[CANDLE_OPEN_COLUMN],
                                                   df[POSITION_COLUMN], open_pos_cond)

        # 保证金（扣减手续费）
        df['cash'] = self._cash - df['open_pos_price'] * self._face_value * df['contract_num'] * self._commission

        # 买入之后，contract_num, open_pos_price, cash不再发生变动
        cols = ['contract_num', 'open_pos_price', 'cash']
        for col in cols:
            df[col].fillna(method='ffill', inplace=True)
        df.loc[df[POSITION_COLUMN] == 0, cols] = np.NaN

        # 根据滑点计算实际平仓价格
        df['close_pos_price'] = price_with_slippage(self._slippage, self._slippage_mode, df['next_open'],
                                                    -1 * df[POSITION_COLUMN], close_pos_cond)
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
        # 平仓时扣除手续费
        df.loc[close_pos_cond, 'net_value'] -= df['close_pos_fee']

        # 计算爆仓
        df.loc[df[POSITION_COLUMN] == 1, 'price_min'] = df[CANDLE_LOW_COLUMN]
        df.loc[df[POSITION_COLUMN] == -1, 'price_min'] = df[CANDLE_HIGH_COLUMN]
        df['profit_min'] = self._face_value * df['contract_num'] * (df['price_min'] - df['open_pos_price']) * df[
            POSITION_COLUMN]
        df['net_value_min'] = df['cash'] + df['profit_min']  # 账户净值最小值
        df['margin_ratio'] = df['net_value_min'] / (self._face_value * df['contract_num'] * df['price_min'])  # 计算最低保证金率
        df.loc[df['margin_ratio'] <= (self._min_margin_ratio + self._commission), 'blow_up'] = 1  # 计算是否爆仓

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

        # df.to_parquet('../data/course/equity_curve.parquet')

        # 删除不必要的数据
        df.drop(columns=['next_open', 'contract_num', 'open_pos_price', 'cash', 'close_pos_price', 'close_pos_fee',
                         'profit', 'net_value', 'price_min', 'profit_min', 'net_value_min', 'margin_ratio', 'blow_up'],
                inplace=True)

        return df

    def _contract_num(self, series):
        """
        计算合约数
        """
        return np_floor_to_precision(self._cash * self._leverage_rate / (self._face_value * series),
                                     self._min_trade_precision)
