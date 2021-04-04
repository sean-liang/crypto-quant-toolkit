import numpy as np


def price_with_slippage(slippage, mode, price_series, direction_series, cond):
    """
    计算滑点
    """
    # 根据滑点计算实际开仓价格
    if mode == 'fixed':
        # 固定滑点
        return np.where(cond, fixed_slippage(price_series, slippage), np.NaN)
    elif mode == 'ratio':
        # 比例滑点
        return np.where(cond, ratio_slippage(price_series, direction_series, slippage), np.NaN)
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
