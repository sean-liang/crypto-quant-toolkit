from functools import partial
import numpy as np
import pandas as pd
import sko
from sko.tools import set_run_mode
from pipeline.pipeline import Pipeline
from commons.constants import EQUITY_CURVE_COLUMN


class Optimizer:

    def __init__(self, method, size_pop, max_iter, config):
        self._method = method
        self._params = Parameters(config)
        self._engine_builder = self._build_engine(method, size_pop, max_iter, self._params)

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
        wrap_func = partial(optimize_func, df=df, pipes=pipes, params=self._params)
        set_run_mode(wrap_func, run_mode)
        engine = self._engine_builder(wrap_func)
        best_x, best_y = engine.run()

        if self._method in ['GA', 'DE']:
            gen_best_x = np.array(engine.generation_best_X)
            gen_best_y = np.array(engine.generation_best_Y).T.reshape(len(engine.generation_best_Y), 1)
        elif self._method == 'PSO':
            gen_best_x = np.array(engine.pbest_x)
            gen_best_y = np.array(engine.pbest_y).T.reshape(len(engine.pbest_y), 1)

        hist_array = np.hstack((gen_best_x, -1 * gen_best_y))
        hist_df = pd.DataFrame(hist_array, columns=[*self._params.variant_names, EQUITY_CURVE_COLUMN])
        hist_df.sort_values(EQUITY_CURVE_COLUMN, ignore_index=True, inplace=True)
        return best_x, -1 * best_y, hist_df


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

        return variants, lower_bound, upper_bound, precision

    def generate_config(self, variants):
        conf = self._config.copy()
        for i, v in enumerate(variants):
            key = self.variants[i]['key']
            if self.variants[i]['type'] == 'range':
                step = self.variants[i]['step']
                conf[key] = v if step < 1 else round(v)
        return conf


def optimize_func(x, df, pipes, params):
    config = params.generate_config(x)
    pipeline = Pipeline.build(pipes, config, silent=True)
    df = pipeline.process(df)
    y = df.iloc[-1][EQUITY_CURVE_COLUMN]
    print(f'parameters: {x}, {EQUITY_CURVE_COLUMN}: {y}')
    return -1 * y
