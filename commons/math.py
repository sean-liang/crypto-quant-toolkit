import numpy as np


def np_floor_to_precision(data, precision=0):
    """
    向下取整到指定位数
    """
    return np.floor(data * (10 ** precision)) / (10 ** precision)


def auto_round(data, precision):
    """
    四舍五入
    """
    if isinstance(data, np.ndarray):
        return np.round(data) if precision >= 1 else data
    elif isinstance(data, float):
        return round(data) if precision >= 1 else data
