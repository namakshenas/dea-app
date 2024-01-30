"""
****** Important! *******
A DEA web-app
built and developed by Mohammad Namakshenas
"""
from dash import Dash, dcc, html, dash_table, Input, Output, callback, State, callback_context, no_update
from dash.exceptions import PreventUpdate
import plotly.express as px
import dash_bootstrap_components as dbc
import dash_auth
import pandas as pd
import logging
import model_selection
import data_parser
import data_info
import model_latex_display
from flask import request

logging.basicConfig(format='%(asctime)s - %(message)s', level=logging.INFO)

VALID_USERNAME_PASSWORD_PAIRS = {
    'scigate': 'scigate'
}

# df = pd.DataFrame()
# df["DMU Index"] = []
# df["Value"] = []
# df["Efficiency Status"] = []

app = Dash(__name__,
           external_stylesheets=["./assets/style.css", dbc.themes.ZEPHYR],
           meta_tags=[{"name": "viewport", "content": "width=device-width, initial-scale=1.0"}], )

app.css.config.serve_locally = True
app.scripts.config.serve_locally = True

auth = dash_auth.BasicAuth(
    app,
    VALID_USERNAME_PASSWORD_PAIRS
)
app.title = "Efficiency Analysis"
server = app.server
header = html.Div(
    [
        html.H4("Efficiency Analysis Webapp", className="text-white"),
        html.Code("ver//2.2.1////scigate.org////2023", ),
    ],
    className="shadow p-4 bg-dark rounded mb-4",
)
footer = html.Code("ver//2.2.1////scigate.org////2023", )

table_output_log = html.Div(
    id="table-output",
    className="dbc-row-selectable",
)

upload_data_label = html.Div(
    [dbc.Label("Import Data")]
)

upload_data = html.Div(
    [
        # dbc.Label("Import Data"),
        dcc.Upload(
            id='upload-data',
            children=html.Div([
                'Drag and Drop or ',
                html.B('Select a File')
            ]),
            # ]
            # ),
        )
    ],
    className="border bg-white shadow-sm rounded p-3 text-center",
    style={
        'color': 'blue',
    },

)

upload_data_help = html.Div(
    [html.A("Download Sample Excel File", href='./assets/sample-dea-data.xlsx')],
    className="small border-bottom mb-4 p-2",
    style={
        'color': '#728FCE',
    },
)

checkBox_user_data_upload = html.Div(
    [
        dbc.RadioItems(
            id="data-type",
            options=[
                {"label": "Built-in Sample", "value": "built-in-sample", "disabled": True},
                {"label": "User Data", "value": "user-data"},
            ],
            value="user-data",
            inline=True,
        ),
    ],
    className="small",
)

# {'opacity': '0.5',
#                                      'background': '#CCC'}

dropdown_dea_model = html.Div(
    [
        dbc.Label("Select DEA Model"),
        dcc.Dropdown(
            ["CCR", "BCC"],
            "CCR",
            id="model-type-dea",
            clearable=False,
        ),
    ],
    className="border-bottom mb-4 pb-4",
)

# radio_dea_projection = html.Div(
#     [
#         dbc.Label("Select Projection"),
#         dbc.RadioItems(
#             id="projection-dea",
#             options=["Radial", "Non-radial"],
#             value="Radial",
#             inline=True,
#         ),
#     ],
#     className="mb-4",
# )

radio_dea_orientation = html.Div(
    [
        dbc.Label("Select Orientation"),
        dbc.RadioItems(
            id="orientation-dea",
            options=["Input", "Output"],
            value="Input",
            inline=True,
        ),
    ],
    className="mb-4",
)

radio_dea_form = html.Div(
    [
        dbc.Label("Select Form"),
        dbc.RadioItems(
            id="form-dea",
            options=[
                {"label": "Multiplier", "value": "multiplier"},
                {"label": "Envelopment", "value": "envelopment", "disabled": True},
            ],
            value="multiplier",
            inline=True,

        ),
    ],
    className="mb-4",
)

radio_dea_return2scale = html.Div(
    [
        dbc.Label("Select Return to Scale"),
        dbc.RadioItems(
            id="return2scale-dea",
            options=
            [
                {"label": "CRS", "value": "crs"},
                {"label": "VRS", "value": "vrs", "disabled": True},
                {"label": "NIRS", "value": "nirs", "disabled": True},
                {"label": "NDRS", "value": "ndrs", "disabled": True},
            ],
            value="crs",
            inline=True,
        ),
    ],
    className="border-bottom mb-4 pb-4",
)

button_solve = dbc.Button('S o l v e',
                          id='solve-btn',
                          className="btn btn-primary w-100 mb-2")

alert_solution_status = dbc.Toast(
    "The selected problem is optimally solved.",
    id="alert-solved",
    header="Nailed it!",
    is_open=False,
    dismissable=True,
    duration=4000,
    # icon="bi-shield-check",
    # color="success",
    # top: 66 positions the toast below the navbar
    style={"position": "fixed", "bottom": 66, "right": 10, "width": 350, "opacity": 0.75},
    className="text-bg-success mb-3",
)

alert_upload_status = dbc.Toast(
    "The dataset is successfully uploaded.",
    id="alert-upload",
    header="Success!",
    is_open=False,
    dismissable=True,
    duration=3000,
    # icon="success",
    # color="success",
    # top: 66 positions the toast below the navbar
    style={"position": "fixed", "bottom": 50, "right": 10, "opacity": 0.75},
    className="text-bg-info mb-3",
)

button_export = dbc.Button('Export',
                           id='btn-export',
                           className="btn btn-primary mt-4")


# accordion = html.Div(
#     dbc.Accordion(
#         [
#             dbc.AccordionItem(
#                 "This is the content of the first section",
#                 title="Item 1",
#             ),
#             dbc.AccordionItem(
#                 "This is the content of the second section",
#                 title="Item 2",
#             ),
#             dbc.AccordionItem(
#                 "This is the content of the third section",
#                 title="Item 3",
#             ),
#         ],
#         always_open=True,
#     )
# )

controls = dbc.Card(
    [upload_data_label, checkBox_user_data_upload, upload_data, upload_data_help, dropdown_dea_model,
     radio_dea_orientation, radio_dea_form, radio_dea_return2scale, button_solve],
    body=True,
    # style={'height': '100vh'}
    className="bg-light"
    # style={'backgroundColor': '#728FCE'}
)

# display indicator

indicator_n_inputs = dbc.Col(
    [html.P("No. Inputs", className="text-white"), html.H4("?", className="text-white", id="indicator-n-inputs"), ],
    className="border bg-primary rounded p-3",
)

indicator_n_outputs = dbc.Col(
    [html.P("No. Outputs", className="text-white"), html.H4("?", className="text-white", id="indicator-n-outputs"), ],
    className="border bg-primary rounded p-3",

)

indicator_n_dmus = dbc.Col(
    [html.P("No. DMUs", className="text-white"), html.H4("?", className="text-white", id="indicator-n-dmus"), ],
    className="border bg-primary rounded p-3",

)

indicator_runtime = dbc.Col(
    [html.P("Runtime (sec.)"), html.H4("?", id="indicator-runtime"), ],
    className="border border-2 border-danger rounded p-3",

)

indicator_problem_status = dbc.Row([indicator_n_inputs,
                                    indicator_n_outputs,
                                    indicator_n_dmus,
                                    indicator_runtime, ], className="row row-cols-md-4 g-0 g-lg-0 mb-4")

# problem_load_info = html.Div(
#     id="problem-load-info-dea",
#     className="dbc-row-selectable",
#
# )

fig_output = html.Div(id="graph-container",
                      children=[dcc.Graph(id="fig-bar-efficiency", animate=False, )],
                      )

# tab4 = dbc.Tab([problem_load_info], label="Problem Info", className="p-4", )
tab1 = dbc.Tab(fig_output, label="Bar Chart", className="p-2", )
tab3 = dbc.Tab([table_output_log, button_export], label="Tabular Result", className="p-4", )
tabs = dbc.Card(dbc.Tabs([tab1, tab3]))


def lazy_serve_layout():
    # time.sleep(5) # for lazing app startup
    layout = html.Div(
        children=[
            # header,
            dbc.Row(
                [
                    dbc.Col(
                        [
                            header,
                            controls,
                        ],
                        width=4,

                    ),
                    # dbc.Col([tabs, colors], width=8),
                    dcc.Store(id='data-frame-uploaded'),
                    dbc.Col([indicator_problem_status, tabs, dcc.Loading(
                        type="default",
                        children=html.Div(id="loading-output-1")
                    ),
                             dcc.Download(id="download-excel"),
                             ],
                            width=8
                            ),
                ],
            ),
            footer,
            alert_upload_status,
            alert_solution_status,
        ],
        # fluid=True,
        className="dbc p-4",
        id='container-button-timestamp',
        # style= {"padding-left":"20px","padding-right":"20px"}
    )
    return layout


app.layout = lazy_serve_layout


# a chained callback trick to share data across multiple callbacks and prevent cpu-intensive callbacks to be initialized
# at the startup of the webapp
@callback(
    # Output('problem-load-info-dea', 'children'),
    Output('data-frame-uploaded', 'data'),
    Output("alert-upload", "is_open"),
    Output("indicator-n-inputs", "children"),
    Output("indicator-n-outputs", "children"),
    Output("indicator-n-dmus", "children"),
    # Output("graph-container", "style"),
    Input("upload-data", "contents"),
    Input('upload-data', 'filename'),
    Input("model-type-dea", "value"),
    # Input("projection-dea", "value"),
    Input("form-dea", "value"),
    Input("orientation-dea", "value"),
    Input("return2scale-dea", "value"),
    State("alert-upload", "is_open"),
    prevent_initial_call=True,
)
def update_problem_info(upload_data_content, upload_data_filename, type_model, form_model, orientation_model,
                        return2scale_model, alert_upload):
    ip_addr = request.environ['REMOTE_ADDR']
    logging.info("########## a new user with ip address " + str(ip_addr))
    output_model_description = "DEA Model ( " + str.upper(type_model) + " , " + str.upper(form_model) + " , " + \
                               str.upper(orientation_model) + " , " + str.upper(return2scale_model) + " ) "

    if upload_data_content:
        contents = upload_data_content
        filename = upload_data_filename
        df_uploaded = data_parser.parse_data(contents, filename)
        num_inputs, num_outputs, num_dmu = data_info.get_data_info(df_uploaded)
        # model_math_latex = model_latex_display.get_model_latex(type_model, orientation_model, form_model)
        # problem_info = dcc.Markdown(r'''
        #                                             **Dataset Structure:**
        #
        #                                             Number of Inputs = **{}**
        #
        #                                             Number of Outputs = **{}**
        #
        #                                             Number of DMUs = **{}**
        #
        #                                             ---
        #
        #                                             Selected Model = **{}**
        #
        #                                             ![alt text]({})
        #                                         '''.format(num_inputs, num_outputs, num_dmu,
        #                                                    output_model_description, model_math_latex)
        #                             )
        return df_uploaded.to_dict(), True, num_inputs, num_outputs, num_dmu
    else:
        raise PreventUpdate


@callback(
    Output("loading-output-1", "children"),
    Output("table-output", "children"),
    # Output("graph-container", "style"),
    Output("fig-bar-efficiency", "figure"),
    Output("alert-solved", "is_open"),
    Output("indicator-runtime", "children"),
    Input('data-frame-uploaded', 'data'),
    Input("model-type-dea", "value"),
    # Input("projection-dea", "value"),
    Input("form-dea", "value"),
    Input("orientation-dea", "value"),
    # Input("return2scale-dea", "value"),
    Input('solve-btn', 'n_clicks'),
    State("alert-solved", "is_open"),
    prevent_initial_call=True,
)
def update_solution(upload_data_frame, type_model, form_model, orientation_model, solve_btn_trigger, alert_solve):
    trigger_listener = [p['prop_id'] for p in callback_context.triggered][0]
    if 'solve-btn' in trigger_listener:
        df, runtime = model_selection.get_model_type(pd.DataFrame.from_dict(upload_data_frame), type_model,
                                                     orientation_model,
                                                     form_model)
        # print(alert_solve)
        table_output = dash_table.DataTable(
            columns=[{"name": i, "id": i, "deletable": False} for i in df.columns],
            data=df.to_dict("records"),
            # page_size = 20,
            editable=True,
            cell_selectable=True,
            style_cell={'textAlign': 'left'},
            style_as_list_view=True,
            # filter_action="native",
            # page_action="native",
            # sort_action="native",
            style_table={
                "overflowX": "auto",
                'height': '500px',
                'overflowY': 'auto'},
            # row_selectable="multi",
            style_header={
                'color': 'blue'},
        )
        logging.info('waiting to create the BAR chart')
        fig_bar_efficiency = px.bar(
            df,
            x="Value",
            y="DMU Index",
            color="Efficiency Status",
            # pattern_shape="Efficiency Status",
            orientation="h",
            template="none",
            text_auto=True,
            title="Efficiency Status",
            height=700,
        )

        # fig_bar_efficiency.update_yaxes(automargin=True)

        fig_bar_efficiency.update_layout(
            yaxis=dict(
                dtick=1,
            ),
            font=dict(
                size=14,  # Set the font size here
            ),
            legend=dict(
                orientation="h",
                yanchor="bottom",
                y=1.02,
                xanchor="right",
                x=1,
                title=None,
            ),
        )
        logging.info('BAR chart created...lets raise the bar!')

        return {}, table_output, fig_bar_efficiency, True, runtime
        # return {}, table_output, {'display': 'block'}, fig_bar_efficiency
    else:
        raise PreventUpdate


@callback(
    Output("download-excel", "data"),
    Input("btn-export", 'n_clicks'),
    Input("table-output", "children"),
    prevent_initial_call=True,
)
def update_export(button_export, table_output):
    trigger_listener = [p['prop_id'] for p in callback_context.triggered][0]
    if 'btn-export' in trigger_listener:
        # print()
        output_dataframe = pd.DataFrame.from_dict(table_output['props']['data'])
        return dcc.send_data_frame(
            output_dataframe.to_excel,
            "export_result.xlsx",
            sheet_name="Result",
            index=False, )
        # return {}, table_output, {'display': 'block'}, fig_bar_efficiency
    else:
        raise PreventUpdate


if __name__ == "__main__":
    app.run_server(debug=True)
