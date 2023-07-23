import base64
import io

import chartgpt as cg
import dash
import dash_ag_grid as dag
import dash_mantine_components as dmc
import pandas as pd
from dash import Input, Output, State, dcc, html, no_update
from dash_iconify import DashIconify

app = dash.Dash(
    __name__,
    external_stylesheets=[
        "https://fonts.googleapis.com/css2?family=Inter:wght@100;200;300;400;500;900&display=swap",
    ],
    title="ChartGPT",
    update_title="ChartGPT | Loading...",
    assets_folder="assets",
    include_assets_files=True,
)
server = app.server


body = dmc.Stack(
    [
        dmc.Stepper(
            id="stepper",
            contentPadding=30,
            active=0,
            size="md",
            breakpoint="sm",
            children=[
                dmc.StepperStep(
                    label="Add your OpenAI API key",
                    icon=DashIconify(
                        icon="material-symbols:lock",
                    ),
                    progressIcon=DashIconify(
                        icon="material-symbols:lock",
                    ),
                    completedIcon=DashIconify(
                        icon="material-symbols:lock-open",
                    ),
                    children=[
                        dmc.Stack(
                            [
                                dmc.Stack(
                                    [
                                        dmc.Blockquote(
                                            """Welcome to ChartGPT! To get started, fetch your OpenAI API key and paste it below.\
                                            Then, upload your CSV file and ask ChartGPT to plot your data. Happy charting 🥳""",
                                            icon=DashIconify(
                                                icon="line-md:coffee-half-empty-twotone-loop"
                                            ),
                                        ),
                                        dmc.Center(
                                            dmc.Button(
                                                dmc.Anchor(
                                                    "Get your API key",
                                                    href="https://platform.openai.com/account/api-keys",
                                                    target="_blank",
                                                    style={
                                                        "textDecoration": "none",
                                                        "color": "white",
                                                    },
                                                ),
                                                fullWidth=False,
                                                rightIcon=DashIconify(
                                                    icon="material-symbols:open-in-new"
                                                ),
                                            ),
                                        ),
                                    ],
                                ),
                                dmc.PasswordInput(
                                    id="input-api-key",
                                    label="API Key",
                                    description="Please add your OpenAI API key. It will be used to generate your visualization",
                                    placeholder="Your OpenAI API Key",
                                    icon=DashIconify(icon="material-symbols:key"),
                                    size="sm",
                                    required=True,
                                ),
                            ]
                        )
                    ],
                ),
                dmc.StepperStep(
                    label="Upload your CSV file",
                    icon=DashIconify(icon="material-symbols:upload"),
                    progressIcon=DashIconify(icon="material-symbols:upload"),
                    completedIcon=DashIconify(icon="material-symbols:upload"),
                    children=[
                        dmc.Stack(
                            [
                                dcc.Upload(
                                    id="upload-data",
                                    children=html.Div(
                                        [
                                            "Drag and Drop or",
                                            dmc.Button(
                                                "Select CSV File",
                                                ml=10,
                                                leftIcon=DashIconify(
                                                    icon="material-symbols:upload"
                                                ),
                                            ),
                                        ]
                                    ),
                                    max_size=5 * 1024 * 1024,  # 5MB
                                    style={
                                        "borderWidth": "1px",
                                        "borderStyle": "dashed",
                                        "borderRadius": "5px",
                                        "textAlign": "center",
                                        "padding": "10px",
                                        "backgroundColor": "#fafafa",
                                    },
                                    style_reject={
                                        "borderColor": "red",
                                    },
                                    multiple=False,
                                ),
                                dmc.Title("Preview", order=3, color="primary"),
                                html.Div(id="output-data-upload"),
                            ]
                        )
                    ],
                ),
                dmc.StepperStep(
                    label="Plot your data 🚀",
                    icon=DashIconify(icon="bi:bar-chart"),
                    progressIcon=DashIconify(icon="bi:bar-chart"),
                    completedIcon=DashIconify(icon="bi:bar-chart-fill"),
                    children=[
                        dmc.Stack(
                            [
                                dmc.Textarea(
                                    id="input-text",
                                    placeholder="Write here",
                                    autosize=True,
                                    description="""Type in your questions or requests related to your CSV file. GPT will write the code to visualize the data and find the answers you're looking for.""",
                                    maxRows=2,
                                ),
                                dmc.Title("Preview", order=3, color="primary"),
                                html.Div(id="output-data-upload-preview"),
                            ]
                        )
                    ],
                ),
                dmc.StepperCompleted(
                    children=[
                        dmc.Stack(
                            [
                                dmc.Textarea(
                                    id="input-text-retry",
                                    description="""Type in your questions or requests related to your CSV file. GPT will write the code to visualize the data and find the answers you're looking for.""",
                                    placeholder="Write here",
                                    autosize=True,
                                    icon=DashIconify(icon="material-symbols:search"),
                                    maxRows=2,
                                ),
                                dmc.LoadingOverlay(
                                    id="output-card",
                                    mih=300,
                                    loaderProps={
                                        "variant": "bars",
                                        "color": "primary",
                                        "size": "xl",
                                    },
                                ),
                            ]
                        )
                    ]
                ),
            ],
        ),
        dmc.Group(
            [
                dmc.Button(
                    "Back",
                    id="stepper-back",
                    display="none",
                    size="md",
                    variant="outline",
                    radius="xl",
                    leftIcon=DashIconify(icon="ic:round-arrow-back"),
                ),
                dmc.Button(
                    "Next",
                    id="stepper-next",
                    size="md",
                    radius="xl",
                    rightIcon=DashIconify(
                        icon="ic:round-arrow-forward", id="icon-next"
                    ),
                ),
            ],
            position="center",
            mb=20,
        ),
    ]
)


header = dmc.Center(
    html.A(
        dmc.Image(
            src="https://raw.githubusercontent.com/chatgpt/chart/9ff8b9b96f01a5ee7091ee5e69a2795381bf5031/docs/assets/chartgpt_logo.svg",
            alt="ChartGPT Logo",
            width=300,
            m=20,
            caption="Plot your data using GPT",
        ),
        href="https://github.com/chatgpt/chart",
        style={"textDecoration": "none"},
    )
)

socials = dmc.Affix(
    dmc.Stack(
        [
            dmc.ActionIcon(
                html.A(
                    DashIconify(icon="mdi:github", width=25),
                    href="https://github.com/youplala/chartgpt",
                    style={"color": "black"},
                ),
            ),
            dmc.ActionIcon(
                html.A(
                    DashIconify(icon="mdi:linkedin", width=25),
                    href="https://www.linkedin.com/in/eliebrosset/",
                    style={"color": "#0B65C2"},
                ),
            ),
        ],
        spacing="sm",
    ),
    position={"top": 10, "left": 10},
)


def show_graph_card(graph, code):
    return dmc.Card(
        dmc.Stack(
            [
                html.Div(graph),
                dmc.Accordion(
                    variant="separated",
                    chevronPosition="right",
                    radius="md",
                    children=[
                        dmc.AccordionItem(
                            [
                                dmc.AccordionControl(
                                    "Show code",
                                    icon=DashIconify(icon="solar:code-bold"),
                                ),
                                dmc.AccordionPanel(
                                    dmc.Prism(
                                        code,
                                        language="python",
                                        id="output-code",
                                        withLineNumbers=True,
                                    ),
                                ),
                            ],
                            value="customization",
                        )
                    ],
                ),
            ]
        )
    )


page = [
    dcc.Store(id="dataset-store", storage_type="local"),
    dmc.Container(
        [
            dmc.Stack(
                [
                    socials,
                    header,
                    body,
                ]
            ),
        ]
    ),
]

app.layout = dmc.MantineProvider(
    id="mantine-provider",
    theme={
        "fontFamily": "'Inter', sans-serif",
        "colorScheme": "light",
        "primaryColor": "dark",
        "defaultRadius": "md",
        "white": "#fff",
        "black": "#404040",
    },
    withGlobalStyles=True,
    withNormalizeCSS=True,
    children=page,
    inherit=True,
)


def parse_contents(contents, filename):
    content_type, content_string = contents.split(",")
    decoded = base64.b64decode(content_string)
    try:
        if "csv" in filename:
            # Assuming the uploaded file is a CSV, parse it
            df = pd.read_csv(io.StringIO(decoded.decode("utf-8")))
            return df
        else:
            return "Invalid file format, please upload a CSV file."
    except Exception as e:
        print(e)
        return "An error occurred while processing the file."


@app.callback(
    Output("dataset-store", "data"),
    Input("upload-data", "contents"),
    State("upload-data", "filename"),
    prevent_initial_call=True,
)
def store_data(contents, filename):
    if contents is not None:
        df = parse_contents(contents, filename)
        return df.to_json(orient="split")


@app.callback(
    Output("output-data-upload", "children"),
    Output("output-data-upload-preview", "children"),
    Output("upload-data", "style"),
    Output("upload-data", "children"),
    Input("dataset-store", "data"),
)
def load_data(dataset):
    if dataset is not None:
        df = pd.read_json(dataset, orient="split")
        table_preview = dag.AgGrid(
            id="data-preview",
            rowData=df.to_dict("records"),
            style={"height": "275px"},
            columnDefs=[{"field": i} for i in df.columns],
        )
        return (
            table_preview,
            table_preview,
            {
                "borderWidth": "1px",
                "borderStyle": "dashed",
                "borderRadius": "5px",
                "textAlign": "center",
                "padding": "7px",
                "backgroundColor": "#fafafa",
            },
            dmc.Group(
                [
                    html.Div(
                        [
                            "Drag and Drop or",
                            dmc.Button(
                                "Replace file",
                                ml=10,
                                leftIcon=DashIconify(icon="mdi:file-replace"),
                            ),
                        ]
                    )
                ],
                position="center",
                align="center",
                spacing="xs",
            ),
        )
    return no_update


@app.callback(
    Output("stepper", "active"),
    Input("stepper-next", "n_clicks"),
    Input("stepper-back", "n_clicks"),
    State("stepper", "active"),
    prevent_initial_call=True,
)
def update_stepper(stepper_next, stepper_back, current):
    ctx = dash.callback_context
    id_clicked = ctx.triggered[0]["prop_id"]
    if id_clicked == "stepper-next.n_clicks" and current < 3:
        return current + 1
    elif id_clicked == "stepper-back.n_clicks":
        return current - 1
    return no_update


@app.callback(
    Output("stepper-next", "disabled"),
    Output("stepper-back", "disabled"),
    Output("stepper-next", "display"),
    Output("stepper-back", "display"),
    Output("stepper-next", "children"),
    Output("icon-next", "icon"),
    Input("stepper", "active"),
    Input("input-api-key", "value"),
    Input("dataset-store", "data"),
)
def update_stepper_buttons(current, api_key, data):
    if current == 0 and api_key != "":
        return False, True, "block", "none", "Next", "ic:round-arrow-forward"
    elif current == 0 and api_key == "":
        return True, True, "block", "none", "Next", "ic:round-arrow-forward"
    elif current == 1 and data is not None:
        return (
            False,
            False,
            "block",
            "block",
            "Next",
            "ic:round-arrow-forward",
        )
    elif current == 1 and data is None:
        return (
            True,
            False,
            "block",
            "block",
            "Next",
            "ic:round-arrow-forward",
        )
    elif current == 2:
        return (
            False,
            False,
            "block",
            "block",
            "Ask ChartGPT",
            "ph:flask-bold",
        )
    elif current == 3:
        return (False, False, "block", "block", "Ask again", "ic:refresh")


@app.callback(
    Output("input-text-retry", "value"),
    Output("output-card", "children"),
    Input("stepper-next", "n_clicks"),
    State("stepper", "active"),
    State("input-api-key", "value"),
    State("dataset-store", "data"),
    State("input-text", "value"),
    State("input-text-retry", "value"),
    prevent_initial_call=True,
)
def update_graph(n_clicks, active, api_key, df, prompt, prompt_retry):
    if n_clicks is not None and active == 2:
        return prompt, predict(api_key, df, prompt)
    elif n_clicks is not None and active == 3:
        return prompt_retry, predict(api_key, df, prompt_retry)
    return no_update


def predict(api_key, df, prompt):
    df = pd.read_json(df, orient="split")
    chart = cg.Chart(df, api_key=api_key)
    fig = chart.plot(prompt, return_fig=True)
    output = show_graph_card(graph=dcc.Graph(figure=fig), code=chart.last_run_code)
    return output


if __name__ == "__main__":
    app.run_server(debug=True)
