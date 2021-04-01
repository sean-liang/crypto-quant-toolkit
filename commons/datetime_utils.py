from datetime import datetime, timezone


def dt_to_str(dt: datetime):
    return dt.strftime('%Y-%m-%d %H:%M:%S')


def ts_to_str(mills, tz):
    return dt_to_str(datetime.fromtimestamp(mills / 1000., tz=tz))


def dt_to_mills(dt: datetime):
    return int(dt.timestamp() * 1000)


def begin_of_day(dt: datetime, tz: timezone):
    return dt.replace(hour=0, minute=0, second=0, microsecond=0, tzinfo=tz)


def end_of_day(dt: datetime, tz: timezone):
    return dt.replace(hour=23, minute=59, second=59, microsecond=0, tzinfo=tz)
