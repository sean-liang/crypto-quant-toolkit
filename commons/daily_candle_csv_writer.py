import numpy as np
import pandas as pd
from commons.constants import CANDLE_COLUMNS, CANDLE_DATETIME_COLUMN


class DailyCandleCSVWriter:

    def __init__(self, output_folder, symbol, interval, timezone):
        self._output_folder = output_folder
        self._symbol = symbol.replace('/', '-')
        self._interval = interval
        self._timezone = timezone
        self._items = None

    def append(self, payload):
        if not payload:
            return
        arr = np.array(payload)
        if self._items is None:
            self._items = arr
        else:
            self._items = np.concatenate((self._items, arr))

    def save(self, *, columns=CANDLE_COLUMNS, dt_column=CANDLE_DATETIME_COLUMN):
        df = pd.DataFrame(self._items, columns=columns)
        df[dt_column] = pd.to_datetime(df[dt_column], unit='ms')
        df[dt_column].dt.tz_localize(self._timezone)
        df.sort_values(dt_column, inplace=True)
        df.reset_index(inplace=True, drop=True)
        for name, group in df.groupby(pd.Grouper(key=dt_column, freq='D')):
            # 按交易对，日期创建文件夹
            folder = self._output_folder / name.strftime('%Y-%m-%d')
            folder.mkdir(parents=True, exist_ok=True)
            # 保存CSV
            group.to_csv(folder / f'{self._symbol}_{self._interval}.csv', index=False, columns=columns)
