import numpy as np


def floor_to_precision(data, decimal_place=0):
    """
    向下取整到指定位数
    """
    return np.floor(data * (10 ** decimal_place)) / (10 ** decimal_place)


def auto_round(data, step=1):
    """
    根据步长自动四舍五入
    """
    is_list = isinstance(data, (list, tuple))
    data = np.array(data) if is_list else data
    rounds = np.round(data / step) * step
    rounds = rounds.tolist() if is_list else rounds
    return rounds
