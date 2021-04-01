import argparse


class ParseKwargs(argparse.Action):
    """
    解析命令行传入的可变字典参数
    """
    def __call__(self, parser, namespace, values, option_string=None):
        setattr(namespace, self.dest, dict())
        for value in values:
            key, value = value.split('=')
            getattr(namespace, self.dest)[key] = value
