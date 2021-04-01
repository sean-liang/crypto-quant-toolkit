from datetime import datetime, timezone


def dt_to_str(dt: datetime):
    """
    日期时间对象转字符串
    """
    return dt.strftime('%Y-%m-%d %H:%M:%S')


def ts_to_str(mills, tz):
    """
    毫秒转日期时间字符串
    """
    return dt_to_str(datetime.fromtimestamp(mills / 1000., tz=tz))


def dt_to_mills(dt: datetime):
    """
    日期时间对象转毫秒
    """
    return int(dt.timestamp() * 1000)


def begin_of_day(dt: datetime, tz: timezone):
    """
    将时间设置为当日开始(00:00:00)
    """
    return dt.replace(hour=0, minute=0, second=0, microsecond=0, tzinfo=tz)


def end_of_day(dt: datetime, tz: timezone):
    """
    将时间设置为当日结束(23:59:59)
    """
    return dt.replace(hour=23, minute=59, second=59, microsecond=0, tzinfo=tz)
