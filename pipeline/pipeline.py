class Pipeline:

    def __init__(self, *func_list):
        self._func_list = func_list if func_list else []

    def extend(self, func_list):
        self._func_list.extend(func_list)

    def append(self, func):
        self._func_list.append(func)

    def process(self, df):
        for func in self._func_list:
            df = func(df)
        return df
