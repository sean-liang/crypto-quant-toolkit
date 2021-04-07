from decimal import Decimal
import numpy as np


def floor_to_precision(data, decimal_place=0):
    """
    向下取整到指定位数
    """
    return np.floor(data * (10 ** decimal_place)) / (10 ** decimal_place)


def number_exponent(num):
    if isinstance(num, (list, tuple)):
        return [number_exponent(n) for n in number_exponent]
    elif not isinstance(num, str):
        return number_exponent(str(num))
    else:
        return abs(Decimal(num).as_tuple().exponent)
