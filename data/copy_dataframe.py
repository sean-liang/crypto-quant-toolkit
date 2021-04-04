def build(params):
    """
    克隆dataframe，多用于并行计算
    """
    return copy_data_frame


def copy_data_frame(df, **kwargs):
    return df.copy()
