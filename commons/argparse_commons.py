import argparse
from datetime import datetime, timedelta
import pytz
from commons.datetime_utils import begin_of_day, end_of_day


class ParseKwargs(argparse.Action):
    """
    解析命令行传入的可变字典参数
    """

    def __call__(self, parser, namespace, values, option_string=None):
        setattr(namespace, self.dest, dict())
        for value in values:
            key, value = value.split('=')
            getattr(namespace, self.dest)[key] = value


def parse_period_arguments(begin, end, periods, *, tz=pytz.utc):
    """
    解析开始时间、结束时间、时长三个参数
    """
    if end:
        end = datetime.strptime(end, '%Y-%m-%d') if isinstance(end, str) else end
        end = end_of_day(end, tz)
        if begin:
            begin = datetime.strptime(begin, '%Y-%m-%d')
            begin = begin_of_day(begin, tz)
        elif periods:
            begin = end - timedelta(days=periods) + timedelta(seconds=1)
        else:
            begin = end - timedelta(days=30) + timedelta(seconds=1)  # 默认结束时间向前30天
    elif begin:
        begin = datetime.strptime(begin, '%Y-%m-%d')
        begin = begin_of_day(begin, tz)
        if periods:
            end = begin + timedelta(days=periods) - timedelta(seconds=1)
        else:
            # 只设置开始时间，结束时间默认为昨天
            end = datetime.now(tz=tz) - timedelta(days=1)
            end = end_of_day(end, tz)

    # 没有设置任何参数，默认从昨天开始向前取
    if not (begin and end):
        return parse_period_arguments(None, datetime.now(tz=tz) - timedelta(days=1), periods, tz=tz)

    return begin, end
