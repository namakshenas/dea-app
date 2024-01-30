import pandas as pd


def get_data_info(uploadDataFrame):
    n_inputs = uploadDataFrame.columns.str.contains("input").sum()
    n_outputs = uploadDataFrame.columns.str.contains("output").sum()
    n_dmu = len(uploadDataFrame)

    return n_inputs, n_outputs, n_dmu
