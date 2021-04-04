from commons.constants import CANDLE_CLOSE_COLUMN
from indicator.overlap import ma


def bbands(df, col=CANDLE_CLOSE_COLUMN, bbands_period=200, bbands_std=2, bbands_ma='sma', **kwargs):
    period = int(bbands_period)
    width = float(bbands_std)
    series = df[col]
    df['BBM'] = ma(bbands_ma, series, period)
    std = series.rolling(period, min_periods=1).std(ddof=0)
    df['BBU'] = df['BBM'] + std * width
    df['BBL'] = df['BBM'] - std * width
    df['BBB'] = 100 * (df['BBM'] - df['BBL']) / df['BBM']
    return df
