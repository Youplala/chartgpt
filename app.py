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
                    label="Plot your data ",
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
            id="logo",
            src="/assets/logo_light.svg",
            alt="ChartGPT Logo",
            width=300,
            m=20,
        ),
        href="https://github.com/chatgpt/chart",
        style={"textDecoration": "none"},
    )
)

theme_toggle = dmc.Switch(
    id="theme-toggle",
    size="lg",
    onLabel="",
    offLabel="",
    checked=False,
    mb=20,
    style={"position": "absolute", "top": "10px", "right": "10px"},
)


socials = dmc.Affix(
    dmc.Stack(
        [
            dmc.ActionIcon(
                html.A(
                    DashIconify(icon="mdi:github", width=25),
                    href="https://github.com/chatgpt/chart",
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
            theme_toggle,
            dmc.Stack(
                [
                    socials,
                    header,
                    dmc.Alert(
                        "",
                        title="Error",
                        id="alert-error",
                        color="red",
                        withCloseButton=True,
                        hide=True
                    ),
                    body,
                ]
            ),
        ]
    ),
]

# Define theme colors globally
CUSTOM_COLORS = {
    "custom": ["#FFFFFF", "#F2F2F2", "#E5E5E5", "#D9D9D9", "#BFBFBF", "#8C8C8C", "#595959", "#3D3D3D", "#1E1E1E", "#000000"],
}

LIGHT_THEME = {
    "colorScheme": "light",
    "primaryColor": "custom",
    "colors": CUSTOM_COLORS,
    "fontFamily": "'Inter', sans-serif",
    "defaultRadius": "md",
    "white": "#fff",
    "black": "#1E1E1E",
    "primaryShade": 8,  # This will make it use #1E1E1E
}

DARK_THEME = {
    **LIGHT_THEME,
    "colorScheme": "dark",
}

app.layout = dmc.MantineProvider(
    id="mantine-provider",
    theme=LIGHT_THEME,
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
        df = pd.read_json(io.StringIO(dataset), orient="split")
        table_preview = dag.AgGrid(
            id="data-preview",
            rowData=df.to_dict("records"),
            style={"height": "275px"},
            columnDefs=[{"field": i} for i in df.columns],
            dashGridOptions={"defaultColDef": {"resizable": True, "sortable": True, "filter": True}},
            className="ag-theme-alpine",
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
    if id_clicked == "stepper-next.n_clicks" and current < 2:
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
    Input("dataset-store", "data"),
)
def update_stepper_buttons(current, data):
    if current == 0 and data is not None:
        return (
            False,
            False,
            "block",
            "block",
            "Next",
            "ic:round-arrow-forward",
        )
    elif current == 0 and data is None:
        return (
            True,
            False,
            "block",
            "block",
            "Next",
            "ic:round-arrow-forward",
        )
    elif current == 1:
        return (
            False,
            False,
            "block",
            "block",
            "Ask ChartGPT",
            "ph:flask-bold",
        )
    elif current == 2:
        return (False, False, "block", "block", "Ask again", "ic:refresh")


@app.callback(
    [Output("mantine-provider", "theme"), Output("logo", "src"), Output("data-preview", "className")],
    [Input("theme-toggle", "checked")],
)
def toggle_theme(is_dark_mode):
    if is_dark_mode:
        return DARK_THEME, "/assets/logo_light.svg", "ag-theme-alpine-dark"
    return LIGHT_THEME, "/assets/logo_dark.svg", "ag-theme-alpine"


@app.callback(
    Output("input-text-retry", "value"),
    Output("output-card", "children"),
    Output("alert-error", "hide"),
    Output("alert-error", "children"),
    Input("stepper-next", "n_clicks"),
    State("stepper", "active"),
    State("dataset-store", "data"),
    State("input-text", "value"),
    State("input-text-retry", "value"),
    prevent_initial_call=True,
)
def update_graph(n_clicks, active, df, prompt, prompt_retry):
    if n_clicks is not None and active == 1:
        try:
            return prompt, predict(df, prompt), True, ""
        except Exception as e:
            return no_update, no_update, False, str(e)
    elif n_clicks is not None and active == 2:
        try:
            return prompt_retry, predict(df, prompt_retry), True, ""
        except Exception as e:
            return no_update, no_update, False, str(e)
    return no_update


def predict(df, prompt):
    df = pd.read_json(df, orient="split")
    chart = cg.Chart(df, model="huggingface/Qwen/Qwen2.5-Coder-32B-Instruct")
    fig = chart.plot(prompt, return_fig=True)
    output = show_graph_card(graph=dcc.Graph(figure=fig), code=chart.last_run_code)
    return output


if __name__ == "__main__":
    app.run_server()
