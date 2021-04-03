from datetime import datetime, timezone
import pytz


def dt_to_str(dt: datetime, *, with_timezone=False):
    """
    日期时间对象转字符串
    """
    return dt.strftime('%Y-%m-%d %H:%M:%S' + ' %z' if with_timezone else '')


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


def begin_of_day(dt: datetime, tz):
    """
    将时间设置为当日开始(00:00:00)
    """
    return dt.replace(hour=0, minute=0, second=0, microsecond=0, tzinfo=tz)


def end_of_day(dt: datetime, tz):
    """
    将时间设置为当日结束(23:59:59)
    """
    return dt.replace(hour=23, minute=59, second=59, microsecond=0, tzinfo=tz)


def timezone_offset_delta(tz):
    """
    计算pytz时区的时间偏移
    """
    return tz.utcoffset(datetime.now())


def str_to_timezone(tz):
    """
    从字符串构建时区
    """
    return pytz.timezone(tz) if tz else pytz.utc
