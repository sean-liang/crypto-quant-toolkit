from functools import partial
from multiprocessing.pool import Pool
import pandas as pd
from optim.variant_parameters import VariantParameters
from optim.optimizer import optimize_func


def optimize(df, target_template, variables, column, target='maximize', verbose=False):
    parameters = VariantParameters.from_template_file(target_template, variables)
    # context = parameters.extended_context(optimize.pipeline_context)
    opt_fun = partial(optimize_func, context={}, parameters=parameters, df=df, column=column)

    with Pool() as pool:
        result = pool.map(opt_fun, parameters.parameter_product)

    res_df = pd.DataFrame(result, columns=[*parameters.parameter_names, column])
    res_df.sort_values(column, ascending=(target == 'maximize'), ignore_index=True, inplace=True)
    return res_df
