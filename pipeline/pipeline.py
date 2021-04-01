import importlib


class Pipeline:
    """
    处理管道
    """

    def __init__(self, config, *func_list):
        self._config = config
        self._func_list = func_list if func_list else []

    def extend(self, func_list):
        self._func_list.extend(func_list)

    def append(self, func):
        self._func_list.append(func)

    def process(self, df):
        for func in self._func_list:
            df = func(df, **self._config)
        return df

    @staticmethod
    def build(modules, config):
        """
        构建处理管道
        :param modules: 管道方法列表
        :param config: 命令行传入参数
        :return: 管道
        """
        print('pipeline parameters: ', config)
        pipeline = Pipeline(config)
        for m in modules:
            pipe = importlib.import_module(m)
            ps = pipe.build(config)
            if isinstance(ps, (list, tuple)):
                pipeline.extend(ps)
            else:
                pipeline.append(ps)
            print(f'load pipe: {pipe.__name__}')

        return pipeline
