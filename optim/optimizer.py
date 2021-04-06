from multiprocessing.pool import Pool
from pipeline.pipeline import Pipeline


def optimize_func(variables, context, parameters, df, column, verbose=False):
    template = parameters.generate_template(variables)
    pipeline = Pipeline.build(template, context)
    df = df.copy()
    df = pipeline.process(df, scopes=['optimize'])
    value = df.iloc[-1][column]
    result = [*variables, value]
    if verbose:
        print(f'variables: {variables}, {column}: {value:.2f}')
    return result


def multiprocessing_optimize(func, parameters):
    with Pool() as pool:
        result = pool.map(func, parameters)

    return result
