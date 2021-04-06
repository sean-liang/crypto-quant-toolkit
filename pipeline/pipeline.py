import importlib
from functools import partial
import yaml
from commons.logging import log


class Pipeline:
    """处理管道"""

    def __init__(self, context={}):
        self.context = context
        self.actions = []

    def load(self, module_name, method_name, params={}):
        module = importlib.import_module(module_name)
        method = getattr(module, method_name)
        params = params
        func = partial(method, **params)
        func.__dict__['_context'] = self.context
        self.actions.append(func)

    def process(self, df):
        for action in self.actions:
            df = action(df)
        return df

    @staticmethod
    def build_from_template(path, *, verbose=False):
        """从yaml配置文件构建管道"""
        with open(path, 'r') as stream:
            config = yaml.load(stream, Loader=yaml.CLoader)
            if verbose:
                log.info(f'load pipeline template: {config}')
        return Pipeline.build(config, verbose=verbose)

    @staticmethod
    def build(template, *, verbose=False):
        """从配置字典构建管道"""
        pipeline = Pipeline(template.get('context', {}))
        for conf in template['actions']:
            module_name, method_name = conf['method'].rsplit('.', 1)
            params = conf.get('params', {})
            pipeline.load(module_name, method_name, params)
            if verbose:
                log.info(f'Load {module_name}.{method_name} <- {params}')
        return pipeline
