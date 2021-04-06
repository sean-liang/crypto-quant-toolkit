import matplotlib.pyplot as plt
from commons.constants import CANDLE_DATETIME_COLUMN, EQUITY_CURVE_COLUMN, CANDLE_CLOSE_COLUMN


def draw_equity_curve(df, path):
    # 保存结果
    print(f'saving equity curve image to {path}')
    ec_df = df[[EQUITY_CURVE_COLUMN, CANDLE_CLOSE_COLUMN]]
    ec_df.index = df[CANDLE_DATETIME_COLUMN]

    plt.figure(figsize=(20, 10))
    ec_df[EQUITY_CURVE_COLUMN].plot(style='r', legend=True)
    ec_df[CANDLE_CLOSE_COLUMN].plot(secondary_y=True, style="b", legend=True)
    plt.savefig(path)
    return df
