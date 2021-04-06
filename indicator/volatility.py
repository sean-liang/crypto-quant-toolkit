from commons.constants import CANDLE_CLOSE_COLUMN
from indicator.overlap import ma


def bbands(df, col=CANDLE_CLOSE_COLUMN, period=200, width=2, ma_method='sma'):
    period = int(period)
    width = float(width)
    series = df[col]
    df['BBM'] = ma(ma_method, series, period)
    std = series.rolling(period, min_periods=1).std(ddof=0)
    df['BBU'] = df['BBM'] + std * width
    df['BBL'] = df['BBM'] - std * width
    df['BBB'] = 100 * (df['BBM'] - df['BBL']) / df['BBM']
    return df
