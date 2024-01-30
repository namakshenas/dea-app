# from dash import dcc
# import model_dea_ccr
#
# df = model_dea_ccr.run_model()
#
# dcc.Graph(
#     figure={
#         'data': [
#             {'x': df["DMU Index"], 'y': df["Value"], 'type': 'bar', 'name': 'SF'},
#         ],
#         'layout': {
#             'title': 'Sorted Efficiency Visualization'
#         }
#     },
#     id='fig-bar-efficiency'
# )


# import plotly.express as px
# import model_dea_ccr
# df = model_dea_ccr.run_model()
# fig = px.bar(df, x="DMU Index", y="Value")
# fig.show()

import pandas as pd


df = pd.read_excel("sample-dea-data_ss.xlsx")

print(df.columns.str.contains("input").sum())
print(df.columns.str.contains("output").sum())
print(len(df))
