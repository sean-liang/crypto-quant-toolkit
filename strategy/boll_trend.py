import pandas_ta as ta
from commons.constants import CANDLE_CLOSE_COLUMN
from pipeline.pandas_ta_helper import WrapPandasTa
from pipeline.pandas_helper import dropna
from signals.bollinger import boll_trend


def build(params):
    bbands = WrapPandasTa(ta.bbands, columns=[CANDLE_CLOSE_COLUMN], strip_column=True,
                          length=int(params['bbands_period']), std=float(params['bbands_std']),
                          mamode=params['bbands_ma']).func

    return bbands, dropna, boll_trend
