from multiprocessing.pool import Pool
from tqdm import tqdm
from pipeline.pipeline import Pipeline
from commons.logging import log


def optimize_func(variables, context, parameters, df, column):
    """
    单次参数优化
    """
    template = parameters.generate_template(variables)
    pipeline = Pipeline.build(template, context)
    df = df.copy()
    df = pipeline.process(df, scopes=['optimize'])
    value = df.iloc[-1][column]
    result = [*variables, value]
    return result


def multiprocessing_optimize(func, parameters, total):
    """
    多进程优化
    """
    results = []
    with Pool() as pool:
        with tqdm(total=total) as pbar:
            for res in pool.imap_unordered(func, parameters):
                res = [float(item) for item in res]
                results.append(res)
                pbar.update()
                res_str = [str(round(v, 2)) for v in res]
                pbar.set_description(f'parameters: {", ".join(res_str[0:-1])}, result: {res_str[-1]}')

    return results
