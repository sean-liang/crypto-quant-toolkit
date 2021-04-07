import numpy as np
import pandas as pd


def print_dataframe(df_or_series_list, *, max_rows=5000, expand_frame_repr=False, force_exit=True):
    pd.options.display.expand_frame_repr = expand_frame_repr  # 当列太多时不换行
    pd.options.display.min_rows = max_rows
    pd.options.display.max_rows = max_rows  # 最多显示数据的行数

    df = pd.DataFrame()

    for idx, item in enumerate(df_or_series_list):
        if isinstance(item, pd.Series):
            df[item.name] = item
        elif isinstance(item, np.ndarray) and len(item.shape) == 1:
            df[f'col_{idx}'] = item

    print(df)

    if force_exit:
        exit()
