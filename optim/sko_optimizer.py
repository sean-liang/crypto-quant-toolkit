from functools import partial
import numpy as np
import pandas as pd
import sko
from sko.tools import set_run_mode
from pipeline.pipeline import Pipeline
from commons.constants import EQUITY_CURVE_COLUMN
from commons.math import auto_round


class Optimizer:

    def __init__(self, method, size_pop, max_iter, config):
        self._method = method
        self._params = Parameters(config)
        self._engine_builder = self._build_engine(method, size_pop, max_iter, self._params)
        self._tracker = ProgressTracker(size_pop, max_iter)

    def _build_engine(self, method, size_pop, max_iter, params):
        p = params
        if method == 'GA':
            ga = partial(sko.GA.GA, n_dim=p.dim, size_pop=size_pop, max_iter=max_iter, lb=p.lower_bound, ub=p.upper_bound, precision=p.precision)
        elif method == 'PSO':
            ga = partial(sko.PSO.PSO, dim=p.dim, pop=size_pop, max_iter=max_iter, lb=p.lower_bound, ub=p.upper_bound)
        elif method == 'DE':
            ga = partial(sko.DE.DE, n_dim=p.dim, size_pop=size_pop, max_iter=max_iter, lb=p.lower_bound, ub=p.upper_bound)
        else:
            raise RuntimeError('method not supported: ', method)
        return ga

    def run(self, df, pipes, *, run_mode='multiprocessing'):
        wrap_func = partial(optimize_func, df=df, pipes=pipes, params=self._params, tracker=self._tracker)
        set_run_mode(wrap_func, run_mode)
        engine = self._engine_builder(wrap_func)
        best_x, best_y = engine.run()

        if self._method in ['GA', 'DE']:
            gen_best_x = np.array(self._params.true_values(engine.generation_best_X))
            gen_best_y = np.array(engine.generation_best_Y).T.reshape(len(engine.generation_best_Y), 1)
        elif self._method == 'PSO':
            gen_best_x = np.array(self._params.true_values(engine.pbest_x))
            gen_best_y = np.array(engine.pbest_y).T.reshape(len(engine.pbest_y), 1)

        hist_array = np.hstack((gen_best_x, -1 * gen_best_y))
        hist_df = pd.DataFrame(hist_array, columns=[*self._params.variant_names, EQUITY_CURVE_COLUMN])
        hist_df.sort_values(EQUITY_CURVE_COLUMN, ignore_index=True, inplace=True)
        return self._params.true_values([best_x])[0], -1 * best_y, hist_df, self._params.generate_config(best_x)[0]


class Parameters:

    def __init__(self, config):
        self._config = config
        self.variants, self.lower_bound, self.upper_bound, self.precision = self._parse_config(config)
        self.dim = len(self.lower_bound)
        self.variant_names = [v['key'] for v in self.variants]

    def _parse_config(self, config):
        variants = []
        lower_bound = []
        upper_bound = []
        precision = []
        for key in config:
            val = config[key]
            if not isinstance(val, str):
                continue
            val = val.strip()
            if val.startswith('[') and val.endswith(']'):
                # 处理区间变量
                begin, end, step = [float(v.strip()) for v in val[1:-1].split(',')]
                variants.append({'key': key, 'type': 'range', 'begin': begin, 'end': end, 'step': step})
                lower_bound.append(begin)
                upper_bound.append(end)
                precision.append(step)
            elif val.startswith('{') and val.endswith('}'):
                values = [v.strip() for v in val[1:-1].split(',')]
                begin = 0
                end = len(values) - 1
                step = 1
                variants.append({'key': key, 'type': 'option', 'begin': begin, 'end': end, 'step': step, 'values': values})
                lower_bound.append(begin)
                upper_bound.append(end)
                precision.append(step)

        return variants, lower_bound, upper_bound, precision

    def true_values(self, value_list):
        result_list = []
        for values in value_list:
            result = []
            for pos, value in enumerate(values):
                var_def = self.variants[pos]
                if var_def['type'] == 'range':
                    precision = var_def['step']
                    result.append(auto_round(value, precision))
                elif var_def['type'] == 'option':
                    option = var_def['values'][int(value)]
                    result.append(option)
                else:
                    result.append(value)
            result_list.append(result)
        return result_list

    def generate_config(self, variants):
        x_list = []
        conf = self._config.copy()
        for i, v in enumerate(variants):
            key = self.variants[i]['key']
            if self.variants[i]['type'] == 'range':
                step = self.variants[i]['step']
                x = conf[key] = auto_round(v, step)
                x_list.append(x)
            elif self.variants[i]['type'] == 'option':
                val = self.variants[i]['values'][int(v)]
                conf[key] = val
                x_list.append(val)
        return conf, x_list


class ProgressTracker:
    _shared_stats = {'total': 0, 'progress': 0}

    def __init__(self, pop, max_iter):
        self.__dict__ = self._shared_stats
        self.total = max_iter

    def next(self):
        self.progress += 1
        return self.progress


def optimize_func(x, df, pipes, params, tracker):
    config, round_x = params.generate_config(x)
    pipeline = Pipeline.build(pipes, config, silent=True)
    df = pipeline.process(df)
    y = df.iloc[-1][EQUITY_CURVE_COLUMN]
    print(f'[{tracker.next()}/{tracker.total}] parameters: {round_x}, {EQUITY_CURVE_COLUMN}: {y}')
    return -1 * y
