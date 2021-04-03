import matplotlib.pyplot as plt
from commons.constants import CANDLE_DATETIME_COLUMN, EQUITY_CURVE_COLUMN


def build(params):
    return save_work_data, draw_equity_curve


def save_work_data(df, output_folder, **kwargs):
    # 保存结果
    file = output_folder / 'data.parquet'
    print(f'saving data to {file}')
    df.to_parquet(file)
    return df


def draw_equity_curve(df, output_folder, **kwargs):
    # 保存结果
    file = output_folder / 'equity_curve.png'
    print(f'saving equity curve image to {file}')
    ec_series = df[EQUITY_CURVE_COLUMN]
    ec_series.index = df[CANDLE_DATETIME_COLUMN]
    ec_series.plot(figsize=(20, 10))
    plt.savefig(file)
    return df
