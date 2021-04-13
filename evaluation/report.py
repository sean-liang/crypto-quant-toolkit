from pathlib import Path
import matplotlib.pyplot as plt
from commons.constants import CANDLE_DATETIME_COLUMN, EQUITY_CURVE_COLUMN, CANDLE_CLOSE_COLUMN
from evaluation.statistics import transfer_equity_curve_to_trade, strategy_evaluate, monthly_return


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


def common_back_testing_report(df, path, *, equity_curve_data=True, equity_curve_chart=True, trade_data=True, evaluation_data=True, monthly_return_data=True):
    path = Path(path)
    path.mkdir(parents=True, exist_ok=True)

    if equity_curve_data:
        df.to_parquet(path / 'equity_curve.parquet')

    if equity_curve_chart:
        draw_equity_curve(df, path / 'equity_curve.png')

    trades = transfer_equity_curve_to_trade(df)
    if trade_data:
        trades.to_csv(path / 'trade.csv')

    ev = strategy_evaluate((df, trades))
    if evaluation_data:
        ev.T.to_csv(path / 'evaluation_result.csv')

    monthly_rtn = monthly_return(df)
    if monthly_return_data:
        monthly_rtn.to_csv(path / 'monthly_return.csv')

    return {'equity_curve': df, 'trades': trades, 'evaluation_result': ev, 'monthly_return': monthly_rtn}
