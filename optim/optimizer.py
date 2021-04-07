from multiprocessing.pool import Pool
from tqdm import tqdm
from pipeline.pipeline import Pipeline
from commons.math import auto_round


def optimize_func(variables, context, parameters, df, column):
    """
    单次参数优化
    """
    template = parameters.generate_template(variables)
    pipeline = Pipeline.build(template, context)
    df = df.copy()
    df = pipeline.process(df, scopes=['optimize'])
    result = df.iloc[-1][column]
    return variables, result


def multiprocessing_optimize(func, parameters, total, variable_precisions=[], result_precision=0.01):
    """
    多进程优化
    """
    if not variable_precisions:
        variable_precisions = result_precision
    results = []
    with Pool() as pool:
        with tqdm(total=total) as pbar:
            for variables, result in pool.imap_unordered(func, parameters):
                variables = auto_round(variables, variable_precisions)
                result = auto_round(result, result_precision)
                results.append([*variables, result])
                pbar.update()
                pbar.set_description(f'parameters: {variables}, result: {result}')

    return results
