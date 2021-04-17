import argparse
import timeit
import numpy as np
from numba import njit, prange


@njit
def run_sim(systems, trades, edge=0.1, pnl=0.01):
    """
    模拟多个参数组合的资金曲线，策略的胜率从-edge ~ edge
    :param systems: 参数数量
    :param trades: 交易次数
    :param edge: 最优参数的额外胜率
    :param pnl: 每次交易盈亏百分比的标准差
    :return: 实际最优参数的排名，回测结果最好参数的实际edge
    """

    # 参数1～N的盈利笔数
    win_rate_list = 0.5 + np.linspace(-1 * edge, edge, systems)

    res = []
    indexes = np.arange(0, trades)
    for i in range(systems):
        # 当前参数的盈利笔数
        current_win_rate = win_rate_list[i]
        current_win_num = int(current_win_rate * trades)

        # 生成符合正态分布的随机交易盈亏数据，负值
        equity_change = -1 * np.abs(np.random.normal(0, pnl, trades))
        # 按照胜率随机修改为盈利交易
        win_trades = np.random.choice(indexes, current_win_num, replace=False)
        equity_change[win_trades] = np.abs(equity_change[win_trades])

        # 计算资金曲线
        equity_curve = (1 + equity_change).cumprod()

        # 保存结果
        res.append(equity_curve[-1])

    res = np.array(res)
    sorted_res = np.argsort(res)[::-1]
    # 实际最优参数的排名
    max_edge_rank = np.argwhere(sorted_res == systems - 1)[0][0] + 1
    # 回测结果最好参数的实际edge
    best_edge = win_rate_list[sorted_res[0]] - 0.5

    return max_edge_rank, best_edge


@njit(parallel=True)
def run_multi_sim(times, systems, trades, edge, pnl):
    res = np.zeros((times, 2))
    for i in prange(times):
        max_edge_rank, best_edge = run_sim(systems, trades, edge, pnl)
        res[i, 0] = max_edge_rank
        res[i, 1] = best_edge
    return res


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='optimization power simulation')
    parser.add_argument('-n', '--times', type=int, default=10000, help='simulation times, default: 10000')
    parser.add_argument('-s', '--systems', type=int, default=50, help='number of systems, default: 50')
    parser.add_argument('-t', '--trades', type=int, default=200, help='trade times, default: 200')
    parser.add_argument('-e', '--max-edge', type=float, default=0.1, help='max edge, default: 0.1')
    parser.add_argument('-c', '--pnl', type=float, default=0.01, help='standard deviation of profit and loss rate of each trade, default: 0.01')
    args = parser.parse_args()

    print(f'Run simulation with arguments: {args}')
    start_time = timeit.default_timer()
    results = run_multi_sim(args.times, args.systems, args.trades, args.max_edge, args.pnl)

    rank_res = results[:, 0]
    rank_mean = np.mean(rank_res)
    rank_std = np.std(rank_res)
    edge_res = results[:, 1]
    edge_mean = np.mean(edge_res)
    edge_std = np.std(edge_res)
    prob = rank_res[rank_res <= 3].shape[0] / edge_res.shape[0]
    print(f'rank mean: {rank_mean:.2f}, std: {rank_std:.4f}, top 3 probability: {prob * 100:.2f}%')
    print(f'edge mean: {edge_mean:.4f}, std: {edge_std:.4f}')

    elapse = timeit.default_timer() - start_time
    print(f'done, takes {elapse:.2f}s')
