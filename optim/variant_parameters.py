import math
import numpy as np
from itertools import product
import yaml
from commons.math import number_exponent


class VariantParameters:
    """
    优化参数解析与管道模板生成
    """

    def __init__(self, template, variables):
        self._template_context = template.get('context', {})
        self._template_actions = template['actions']
        self._variables, self._total = _parse_variables(self._template_actions, variables)
        self._variable_decimal_places = [number_exponent(v['step']) for v in self._variables]

    def generate_template(self, variables):
        """
        根据传入参数生成管道配置
        """
        self._check_variables(variables)
        template = self._template_actions.copy()
        for i, v in enumerate(variables):
            value = None
            conf = self._variables[i]
            if conf['type'] == 'range':
                value = v
            template[conf['index']]['params'][conf['name']] = value
        return template

    def extended_context(self, another_context):
        """
        覆盖更新策略原上下文
        """
        ctx = self._template_context.copy()
        ctx.update(another_context)
        return ctx

    def auto_round(self, variables):
        """
        自动四舍五入
        """
        self._check_variables(variables)
        return [np.round(v, self._variable_decimal_places[i]) for i, v in enumerate(variables)]

    def _check_variables(self, variables):
        if len(variables) != len(self._variables):
            raise RuntimeError(f'variable number mismatch, expect {len(self._variables)}, got{len(variables)}')

    @property
    def variable_decimal_places(self):
        return self._variable_decimal_places

    @property
    def parameter_names(self):
        return [v['name'] for v in self._variables]

    @property
    def parameter_product(self):
        variables = [v['values'] for v in self._variables]
        return product(*variables)

    @property
    def total(self):
        return self._total

    @property
    def actions(self):
        return self._template_actions

    @staticmethod
    def from_template_file(template_path, variables):
        with open(template_path, 'r') as stream:
            config = yaml.load(stream, Loader=yaml.CLoader)
        return VariantParameters(config, variables)


def _parse_variables(actions, variables):
    """
    解析待优化参数配置
    """
    total = 1 if variables else 0
    var_conf_list = []
    for action in variables:
        for param in action['params']:
            val = action['params'][param]
            conf = {'index': _find_method_index(actions, action['method']), 'method': action['method'], 'name': param, 'value': val}
            if isinstance(val, list):
                conf['type'] = 'range'
                conf['upper'] = val[1]
                conf['lower'] = val[0]
                conf['step'] = val[2]
            else:
                raise RuntimeError(f'variable not supported: {action}')
            conf['count'] = math.floor((conf['upper'] - conf['lower']) / conf['step'] + 1)
            conf['values'] = np.arange(conf['lower'], conf['upper'] + conf['step'], conf['step'])
            total *= conf['count']
            var_conf_list.append(conf)
    return var_conf_list, total


def _find_method_index(actions, action):
    for idx, item in enumerate(actions):
        if action == item['method']:
            return idx
    raise RuntimeError(f'{action} not in template')
