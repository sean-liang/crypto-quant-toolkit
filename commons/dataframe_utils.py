from datetime import datetime
import pytz
import pandas as pd
from commons.constants import CANDLE_DATETIME_COLUMN
from commons.datetime_utils import begin_of_day, end_of_day


def filter_candle_dataframe_by_begin_end_offset_datetime(df, begin, end, offset, *, tz=pytz.utc):
    candle_date = df[CANDLE_DATETIME_COLUMN].dt.date
    if begin:
        begin = begin_of_day(datetime.strptime(begin, '%Y-%m-%d'), tz=tz)
        df = df[candle_date >= begin.date()]
    elif offset > 0:
        begin = df.iat[0, 0] + pd.Timedelta(days=offset)
        df = df[candle_date >= begin.date()]
    if end:
        end = end_of_day(datetime.strptime(end, '%Y-%m-%d'), tz=tz)
        df = df[candle_date <= end.date()]
    return df
