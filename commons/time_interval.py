from datetime import timedelta


class TimeInterval:
    """
    对时间频率的封装
    """

    def __init__(self, interval):
        self.s = interval.strip().lower()
        self.unit = interval[-1]
        self.num = int(interval[:-1])

        if self.unit is 'm':
            # 分钟
            self.delta = timedelta(minutes=self.num)
        elif self.unit is 'h':
            # 小时
            self.delta = timedelta(hours=self.unit)
        elif self.unit is 'd':
            # 日
            self.delta = timedelta(days=self.num)
        else:
            raise RuntimeError(f'illegal interval unit: {self.unit}')

    def __str__(self):
        return self.s
