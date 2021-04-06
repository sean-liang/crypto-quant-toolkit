import math
import numpy as np
from itertools import product
import yaml


class VariantParameters:

    def __init__(self, template, variables):
        self._template_context = template.get('context', {})
        self._template_actions = template['actions']
        self._variables, self._total = _parse_variables(self._template_actions, variables)

    def generate_template(self, variables, *, auto_precision=False):
        if len(variables) != len(self._variables):
            raise RuntimeError(f'variable number mismatch, expect {len(self._variables)}, got{len(variables)}')
        template = self._template_actions.copy()
        for i, v in enumerate(variables):
            value = None
            conf = self._variables[i]
            if conf['type'] == 'range':
                value = v
            template[conf['index']]['params'][conf['name']] = value
        return template

    def extended_context(self, another_context):
        ctx = self._template_context.copy()
        ctx.update(another_context)
        return ctx

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
