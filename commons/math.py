import numpy as np
import math


def np_floor_to_precision(data, precision=0):
    """
    向下取整到指定位数
    """
    return np.floor(data * (10 ** precision)) / (10 ** precision)


def auto_round(data, precision, *, min_precision=2):
    """
    四舍五入
    """
    if isinstance(data, np.ndarray):
        return np.round(data) if precision >= 1 else np.round(data * (10 ** min_precision)) / (10 ** min_precision)
    elif isinstance(data, float):
        return round(data) if precision >= 1 else round(data * (10 ** min_precision)) / (10 ** min_precision)
