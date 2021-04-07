import importlib
from functools import partial
import yaml
from commons.logging import log


class Pipeline:
    """
    处理管道
    """
    def __init__(self, context={}):
        self.context = context
        self.actions = []

    def load(self, module_name, method_name, scopes, params={}):
        """
        动态载入管道方法
        """
        module = importlib.import_module(module_name)
        method = getattr(module, method_name)
        params = params
        func = partial(method, **params)
        func.pipeline_context = method.pipeline_context = self.context
        if scopes:
            func.pipeline_scopes = method.pipeline_scopes = scopes
        self.actions.append(func)

    def process(self, df, scopes=None):
        """
        处理数据
        """
        if scopes and not isinstance(scopes, (set, list, tuple)):
            scopes = [scopes]
        if scopes and not isinstance(scopes, set):
            scopes = set(scopes)
        for action in self.actions:
            if not scopes or (scopes and action.pipeline_scopes and set.intersection(scopes, action.pipeline_scopes)):
                df = action(df)
        return df

    @staticmethod
    def build_from_template(path, *, verbose=False):
        """
        从yaml配置文件构建管道
        """
        with open(path, 'r') as stream:
            config = yaml.load(stream, Loader=yaml.CLoader)
        return Pipeline.build(config['actions'], config.get('context', {}), verbose=verbose)

    @staticmethod
    def build(actions, context={}, *, verbose=False):
        """
        从配置字典构建管道
        """
        pipeline = Pipeline(context)
        for conf in actions:
            module_name, method_name = conf['method'].rsplit('.', 1)
            scopes = conf.get('scopes', None)
            scopes = set([scopes] if isinstance(scopes, str) else scopes) if scopes else None
            params = conf.get('params', {})
            pipeline.load(module_name, method_name, scopes, params)
            if verbose:
                log.info(f'load action: {module_name}.{method_name}, scopes: {scopes}, params: {params}')
        return pipeline
