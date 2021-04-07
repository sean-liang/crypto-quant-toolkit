import pandas_ta as ta


# def ma(method, series, ma_period):
#     if method.lower() == 'sma':
#         return sma(series, ma_period)
#
#     raise RuntimeError('ma method not supported: ', method)
#
#
# def sma(series, ma_period):
#     return series.rolling(ma_period, min_periods=1).mean()

def ma(method, series, ma_period):
    """MA均线，直接调用pandas_ma的均线方法"""
    return ta.ma(method, series, length=ma_period, min_periods=1)
