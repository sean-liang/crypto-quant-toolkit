from functools import partial
import pandas as pd
from optim.variant_parameters import VariantParameters
from optim.optimizer import optimize_func, multiprocessing_optimize


def optimize(df, target_template, variables, column, target='maximize', verbose=False):
    """枚举搜索最优参数"""
    parameters = VariantParameters.from_template_file(target_template, variables)
    context = parameters.extended_context(optimize.pipeline_context)
    opt_fun = partial(optimize_func, context=context, parameters=parameters, df=df, column=column, verbose=verbose)
    result = multiprocessing_optimize(opt_fun, parameters.parameter_product)
    res_df = pd.DataFrame(result, columns=[*parameters.parameter_names, column])
    res_df.sort_values(column, ascending=(target == 'maximize'), ignore_index=True, inplace=True)
    return res_df
