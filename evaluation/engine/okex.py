import numpy as np
from commons.constants import CANDLE_OPEN_COLUMN, CANDLE_CLOSE_COLUMN, CANDLE_LOW_COLUMN, CANDLE_HIGH_COLUMN, POSITION_COLUMN, EQUITY_CURVE_COLUMN

from data.candle import add_next_open
from evaluation.equity_curve_commons import _group_trade, _contract_number, _future_margin, _fill_unchanged_columns, _net_value, _blow_up, _equity_curve
from evaluation.position import _open_close_position_condition
from evaluation.slippage import price_with_slippage


def future_equity_curve(df, cash=10000, face_value=0.01, min_trade_precision=0, leverage_rate=1, slippage_mode='ratio', slippage=0.001, commission=0.0002,
                        min_margin_ratio=0.01):
    """
    计算OKEx合约交易资金曲线
    """

    # 找出下根K线的开盘价
    df = add_next_open(df, col='next_open')
    # 找出开、平仓的K线
    open_cond, close_cond = _open_close_position_condition(df)
    # 设置每组交易的开仓时间
    _group_trade(df, open_cond, col='start_time')
    # 计算买入合约数
    df['contract_num'] = np.where(open_cond, _contract_number(df[CANDLE_OPEN_COLUMN], cash, leverage_rate, face_value, min_trade_precision), np.NaN)
    # 根据滑点计算实际开仓价格
    df['open_pos_price'] = price_with_slippage(slippage, slippage_mode, df[CANDLE_OPEN_COLUMN], df[POSITION_COLUMN], open_cond)
    # 保证金（扣减手续费）
    df['margin'] = _future_margin(df['open_pos_price'], df['contract_num'], cash, face_value, commission)
    # 买入之后，contract_num, open_pos_price, margin不再发生变动
    _fill_unchanged_columns(df, 'contract_num', 'open_pos_price', 'margin')
    # 账户净值
    df['net_value'] = _net_value(df['open_pos_price'], df[CANDLE_CLOSE_COLUMN], df[POSITION_COLUMN], df['next_open'], df['contract_num'], df['margin'],
                                 close_cond, slippage, slippage_mode, face_value, commission)
    # 计算爆仓
    _blow_up(df, close_cond, face_value, min_margin_ratio, commission, col='blow_up')
    # 计算资金曲线
    df[EQUITY_CURVE_COLUMN] = _equity_curve(df['net_value'], open_cond, cash)
    # 删除不必要的数据
    df.drop(columns=['next_open', 'margin', 'net_value'], inplace=True)

    return df
