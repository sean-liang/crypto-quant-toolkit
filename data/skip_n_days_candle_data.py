from datetime import timedelta
from functools import partial
from commons.constants import CANDLE_DATETIME_COLUMN


def build(params):
    """
    忽略N天的K线，主要用于生成与课程相同的计算结果
    """
    skip_n_days = partial(skip_n_days_data, days=int(params['data_skip_days']))

    return skip_n_days


def skip_n_days_data(df, days, **kwargs):
    t = df.iloc[0][CANDLE_DATETIME_COLUMN] + timedelta(days=days)
    return df[df[CANDLE_DATETIME_COLUMN] > t]
