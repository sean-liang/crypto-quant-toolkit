import importlib
from functools import partial

import pandas as pd
import yaml
from commons.logging import log


class Pipeline:
    """
    处理管道
    """

    def __init__(self, context={}):
        self.context = context
        self.actions = []

    def load(self, module_name, method_name, scopes, multi=False, params={}):
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
        func.pipeline_multi = method.pipeline_multi = multi
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
                if isinstance(df, (tuple, list)):
                    df = action(*df)
                else:
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
            multi = conf.get('multi', False)
            params = conf.get('params', {})
            pipeline.load(module_name, method_name, scopes, multi, params)
            if verbose:
                log.info(f'load action: {module_name}.{method_name}, scopes: {scopes}, multi: {multi}, params: {params}')
        return pipeline


def pass_through(df):
    """
    直接返回参数Dataframe
    """
    return df


def flat_map(df, pipelines):
    """
    使用不同的pipe分别处理dataframe，返回结果dict
    """
    results = {}
    for key in pipelines:
        actions = pipelines[key]
        pipeline = Pipeline.build(actions, flat_map.pipeline_context)
        results[key] = pipeline.process(df)
    return
