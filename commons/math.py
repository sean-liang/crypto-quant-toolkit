import numpy as np


def np_floor_to_precision(data, precision=0):
    """
    向下取整到指定位数
    """
    return np.floor(data * (10 ** precision)) / (10 ** precision)
