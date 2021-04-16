import itertools
import numpy as np
import pandas as pd
from commons.constants import CANDLE_DATETIME_COLUMN, CANDLE_CLOSE_COLUMN, CANDLE_OPEN_COLUMN, SIGNAL_COLUMN, POSITION_COLUMN, EQUITY_CHANGE_COLUMN, \
    EQUITY_CURVE_COLUMN


def transfer_equity_curve_to_trade(equity_curve):
    """
    将资金曲线数据，转化为一笔一笔的交易
    """
    # 选取开仓、平仓条件
    condition1 = equity_curve[POSITION_COLUMN] != 0
    condition2 = equity_curve[POSITION_COLUMN] != equity_curve[POSITION_COLUMN].shift(1)
    open_pos_condition = condition1 & condition2

    # 计算每笔交易的start_time
    if 'start_time' not in equity_curve.columns:
        equity_curve.loc[open_pos_condition, 'start_time'] = equity_curve[CANDLE_DATETIME_COLUMN]
        equity_curve['start_time'].fillna(method='ffill', inplace=True)
        equity_curve.loc[equity_curve[POSITION_COLUMN] == 0, 'start_time'] = pd.NaT

    # 对每次交易进行分组，遍历每笔交易
    trade = pd.DataFrame()  # 计算结果放在trade变量中

    for _index, group in equity_curve.groupby('start_time'):
        # 记录每笔交易
        # 本次交易方向
        trade.loc[_index, SIGNAL_COLUMN] = group[POSITION_COLUMN].iloc[0]

        # 本次交易杠杆倍数
        if 'leverage_rate' in group:
            trade.loc[_index, 'leverage_rate'] = group['leverage_rate'].iloc[0]

        g = group[group[POSITION_COLUMN] != 0]  # 去除pos=0的行
        # 本次交易结束那根K线的开始时间
        trade.loc[_index, 'end_bar'] = g.iloc[-1][CANDLE_DATETIME_COLUMN]
        # 开仓价格
        trade.loc[_index, 'start_price'] = g.iloc[0][CANDLE_OPEN_COLUMN]
        # 平仓信号的价格
        trade.loc[_index, 'end_price'] = g.iloc[-1][CANDLE_CLOSE_COLUMN]
        # 持仓k线数量
        trade.loc[_index, 'bar_num'] = g.shape[0]
        # 本次交易收益
        trade.loc[_index, 'change'] = (group[EQUITY_CHANGE_COLUMN] + 1).prod() - 1
        # 本次交易结束时资金曲线
        trade.loc[_index, 'end_equity_curve'] = g.iloc[-1][EQUITY_CURVE_COLUMN]
        # 本次交易中资金曲线最低值
        trade.loc[_index, 'min_equity_curve'] = g[EQUITY_CURVE_COLUMN].min()

    return trade


def strategy_evaluate(dfs):
    """
    统计回测结果
    """
    # equity_curve: 带资金曲线的df, trade: transfer_equity_curve_to_trade的输出结果，每笔交易的df
    equity_curve, trade = dfs

    # 新建一个dataframe保存回测指标
    results = pd.DataFrame()

    # 计算累积净值
    results.loc[0, 'Cumulative Net Value'] = round(equity_curve[EQUITY_CURVE_COLUMN].iloc[-1], 2)

    # 计算年化收益
    annual_return = (equity_curve[EQUITY_CURVE_COLUMN].iloc[-1] / equity_curve[EQUITY_CURVE_COLUMN].iloc[0]) ** (
            '1 days 00:00:00' / (equity_curve[CANDLE_DATETIME_COLUMN].iloc[-1] - equity_curve[CANDLE_DATETIME_COLUMN].iloc[0]) * 365) - 1
    results.loc[0, 'CAGR'] = round(annual_return, 2)

    # 计算最大回撤
    # 计算当日之前的资金曲线的最高点
    equity_curve['max2here'] = equity_curve[EQUITY_CURVE_COLUMN].expanding().max()
    # 计算到历史最高值到当日的跌幅，drawdown
    equity_curve['dd2here'] = equity_curve[EQUITY_CURVE_COLUMN] / equity_curve['max2here'] - 1

    # 年化收益/平均回撤比
    results.loc[0, 'CAGR / Mean DD'] = round(abs(annual_return / equity_curve['dd2here'].mean()), 2)

    # 计算最大回撤，以及最大回撤结束时间
    end_date, max_draw_down = tuple(equity_curve.sort_values(by=['dd2here']).iloc[0][[CANDLE_DATETIME_COLUMN, 'dd2here']])
    # 计算最大回撤开始时间
    start_date = equity_curve[equity_curve[CANDLE_DATETIME_COLUMN] <= end_date].sort_values(by=EQUITY_CURVE_COLUMN, ascending=False).iloc[0][
        CANDLE_DATETIME_COLUMN]
    # 年化收益/回撤比
    results.loc[0, 'CAGR / Max DD'] = round(abs(annual_return / max_draw_down), 2)

    # 皮尔森相关系数
    corr_coef = np.corrcoef(x=equity_curve[CANDLE_DATETIME_COLUMN].values.astype(np.int64), y=equity_curve[EQUITY_CURVE_COLUMN])[0, 1]
    results.loc[0, 'Correlation Coefficient'] = round(corr_coef, 4)

    # 将无关的变量删除
    equity_curve.drop(['max2here', 'dd2here'], axis=1, inplace=True)
    results.loc[0, 'Maximum Drawdown'] = format(max_draw_down, '.2%')
    results.loc[0, 'Maximum Drawdown Begin'] = str(start_date)
    results.loc[0, 'Maximum Drawdown End'] = str(end_date)

    # 统计每笔交易
    results.loc[0, 'Number of Trades'] = trade.shape[0]  # 总交易笔数
    results.loc[0, 'Number of Win'] = len(trade.loc[trade['change'] > 0])  # 盈利笔数
    results.loc[0, 'Number of Loss'] = len(trade.loc[trade['change'] <= 0])  # 亏损笔数
    results.loc[0, 'Win Rate'] = format(results.loc[0, 'Number of Win'] / len(trade), '.2%')  # 胜率

    results.loc[0, 'Average Profit & Loss Per Transaction'] = format(trade['change'].mean(), '.2%')  # 每笔交易平均盈亏
    # 盈亏比
    results.loc[0, 'Profit & Loss Ratio'] = round(trade.loc[trade['change'] > 0]['change'].mean() / trade.loc[trade['change'] < 0]['change'].mean() * (-1), 2)

    results.loc[0, 'Maximum Single Profit'] = format(trade['change'].max(), '.2%')  # 单笔最大盈利
    results.loc[0, 'Maximum Single Loss'] = format(trade['change'].min(), '.2%')  # 单笔最大亏损

    # 统计持仓时间，会比实际时间少一根K线的是距离
    trade['Holding Time'] = trade['end_bar'] - trade.index
    max_days, max_seconds = trade['Holding Time'].max().days, trade['Holding Time'].max().seconds
    max_hours = max_seconds // 3600
    max_minute = (max_seconds - max_hours * 3600) // 60
    results.loc[0, 'Maximum Single Holding Time'] = str(max_days) + ' days ' + str(max_hours) + ' hours ' + str(max_minute) + ' minutes'  # 单笔最长持有时间

    min_days, min_seconds = trade['Holding Time'].min().days, trade['Holding Time'].min().seconds
    min_hours = min_seconds // 3600
    min_minute = (min_seconds - min_hours * 3600) // 60
    results.loc[0, 'Minimum Single Holding Time'] = str(min_days) + ' days ' + str(min_hours) + ' hours ' + str(min_minute) + ' minutes'  # 单笔最短持有时间

    mean_days, mean_seconds = trade['Holding Time'].mean().days, trade['Holding Time'].mean().seconds
    mean_hours = mean_seconds // 3600
    mean_minute = (mean_seconds - mean_hours * 3600) // 60
    results.loc[0, 'Avg. Holding Time'] = str(mean_days) + ' days ' + str(mean_hours) + ' hours ' + str(mean_minute) + ' minutes'  # 平均持仓周期

    # 连续盈利亏算
    results.loc[0, 'Maximum Consecutive Profit'] = max([len(list(v)) for k, v in itertools.groupby(np.where(trade['change'] > 0, 1, np.nan))])  # 最大连续盈利笔数
    results.loc[0, 'Maximum Consecutive Loss'] = max([len(list(v)) for k, v in itertools.groupby(np.where(trade['change'] < 0, 1, np.nan))])  # 最大连续亏损笔数

    return results


def monthly_return(df):
    # 每月收益率
    df.set_index(CANDLE_DATETIME_COLUMN, inplace=True)
    return df[[EQUITY_CHANGE_COLUMN]].resample(rule='M').apply(lambda x: (1 + x).prod() - 1)
