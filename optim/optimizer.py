from pipeline.pipeline import Pipeline


def optimize_func(variables, context, parameters, df, column, verbose=True):
    template = parameters.generate_template(variables)
    pipeline = Pipeline.build(template, context)
    df = df.copy()
    df = pipeline.process(df, scopes=['optimize'])
    value = df.iloc[-1][column]
    result = [*variables, value]
    if verbose:
        print(result)
    return result
