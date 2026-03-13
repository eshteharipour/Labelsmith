import json
import os

import dash
import dash_bootstrap_components as dbc
import pandas as pd
from dash import ALL, Input, Output, State, ctx, dcc, html, no_update
from flask import abort, send_from_directory
from prod2vec.dataset.settings import LCSCIseeCLip

# Constants
DATA_FILE = LCSCIseeCLip.tr
STATE_FILE = "artifacts/state.json"
PAGE_SIZE = 100

# Load dataset
if os.path.exists(DATA_FILE):
    df = pd.read_csv(DATA_FILE, sep="\t", dtype=object, keep_default_na=False)
else:
    raise FileNotFoundError(f"Dataset file '{DATA_FILE}' not found.")

# Load previous state
if os.path.exists(STATE_FILE):
    with open(STATE_FILE, "r") as f:
        state = json.load(f)
        selected_images = set(state.get("selected_images", []))
        last_page = state.get("last_page", 0)
else:
    selected_images = set()
    last_page = 0

# App setup with Bootstrap
app = dash.Dash(
    __name__,
    external_stylesheets=[dbc.themes.FLATLY],
    suppress_callback_exceptions=True,
)
app.title = "Image Cleaner"
server = app.server


# Flask route to serve images
@server.route("/images/<int:image_id>")
def serve_image(image_id):
    try:
        if image_id < 0 or image_id >= len(df):
            return abort(404, description="Invalid image ID")

        image_path = df.loc[image_id, "path"]
        full_path = os.path.abspath(image_path)

        if not os.path.exists(full_path):
            return abort(404, description="File not found")

        directory = os.path.dirname(full_path)
        filename = os.path.basename(full_path)
        return send_from_directory(directory, filename)

    except Exception as e:
        return abort(500, description=f"Server error: {str(e)}")


# Main page layout
def create_main_layout():
    return dbc.Container(
        [
            # View Controls
            dbc.Row(
                [
                    dbc.Col(
                        [
                            dbc.ButtonGroup(
                                [
                                    dbc.Button(
                                        "Row View",
                                        id="row-view-btn",
                                        color="primary",
                                        n_clicks=0,
                                    ),
                                    dbc.Button(
                                        "Grid View",
                                        id="grid-view-btn",
                                        color="primary",
                                        n_clicks=0,
                                    ),
                                ]
                            ),
                            html.A(
                                dbc.Button(
                                    "View Selected Images",
                                    id="view-selected-btn",
                                    color="info",
                                    className="ms-3",
                                ),
                                href="/selected",
                            ),
                        ],
                        width={"size": 6, "offset": 3},
                        className="text-center",
                    )
                ],
                className="mb-3",
            ),
            # Navigation Controls
            dbc.Row(
                [
                    dbc.Col(
                        dbc.ButtonGroup(
                            [
                                dbc.Button(
                                    "Previous", id="prev-page-btn", color="secondary"
                                ),
                                dbc.Button(
                                    f"Page {last_page + 1}/{len(df) // PAGE_SIZE + 1}",
                                    id="page-info",
                                    disabled=True,
                                ),
                                dbc.Button(
                                    "Next", id="next-page-btn", color="secondary"
                                ),
                            ]
                        ),
                        width={"size": 4, "offset": 4},
                        className="text-center",
                    )
                ],
                className="mb-4",
            ),
            # Image Container
            dbc.Row(id="image-container"),
        ],
        fluid=True,
    )


# Selected images page layout
def create_selected_layout():
    return dbc.Container(
        [
            dbc.Row(
                [
                    dbc.Col(
                        [
                            html.A(
                                dbc.Button(
                                    "Back to Main View",
                                    color="primary",
                                    className="mb-4",
                                ),
                                href="/",
                            ),
                            html.H4("Selected Images", className="mb-4"),
                        ]
                    )
                ]
            ),
            dbc.Row(id="selected-images-view"),
        ],
        fluid=True,
    )


# App layout with global stores
app.layout = html.Div(
    [
        # Global stores that need to be available everywhere
        dcc.Store(id="selected-images", data=list(selected_images)),
        dcc.Store(id="state-selected-images", data=list(selected_images)),
        dcc.Store(id="current-page", data=last_page),
        dcc.Store(id="view-state", data="grid"),
        dcc.Location(id="url", refresh=False),
        # Content div that gets replaced based on URL
        html.Div(id="page-content"),
    ]
)


# URL Router callback
@app.callback(Output("page-content", "children"), Input("url", "pathname"))
def display_page(pathname):
    if pathname == "/selected":
        return create_selected_layout()
    return create_main_layout()


# Callback to update view state
@app.callback(
    Output("view-state", "data"),
    Input("row-view-btn", "n_clicks"),
    Input("grid-view-btn", "n_clicks"),
    State("view-state", "data"),
    prevent_initial_call=True,
)
def update_view(row_clicks, grid_clicks, current_view):
    triggered_id = ctx.triggered_id
    if triggered_id == "row-view-btn":
        return "row"
    elif triggered_id == "grid-view-btn":
        return "grid"
    return current_view


# Callback to handle image selection
@app.callback(
    Output("selected-images", "data"),
    Input({"type": "select-btn", "index": ALL}, "n_clicks"),
    State("selected-images", "data"),
    prevent_initial_call=True,
)
def update_selection(n_clicks, selected):
    triggered_id = ctx.triggered_id
    if not triggered_id or not isinstance(triggered_id, dict):
        return no_update

    triggered_index = triggered_id.get("index")
    if triggered_index is None:
        return no_update

    img_path = df.loc[int(triggered_index), "path"]

    selected_set = set(selected or [])
    if img_path in selected_set:
        selected_set.remove(img_path)
    else:
        selected_set.add(img_path)

    with open(STATE_FILE, "w", encoding="utf-8") as f:
        json.dump(
            {"selected_images": list(selected_set), "last_page": last_page},
            f,
            ensure_ascii=False,
        )

    return list(selected_set)


# Callback to update page navigation
@app.callback(
    Output("current-page", "data"),
    [Input("prev-page-btn", "n_clicks"), Input("next-page-btn", "n_clicks")],
    [State("current-page", "data")],
    prevent_initial_call=True,
)
def change_page(prev_clicks, next_clicks, current_page):
    if not ctx.triggered_id:
        return no_update

    if current_page is None:
        current_page = 0

    if ctx.triggered_id == "prev-page-btn" and current_page > 0:
        current_page -= 1
    elif ctx.triggered_id == "next-page-btn" and (current_page + 1) * PAGE_SIZE < len(
        df
    ):
        current_page += 1

    return current_page


def create_row_view(page_data, selected_set):
    return [
        dbc.Row(
            [
                dbc.Col(
                    dbc.Card(
                        [
                            dbc.CardBody(
                                [
                                    dbc.Row(
                                        [
                                            dbc.Col(
                                                html.Img(
                                                    src=f"/images/{row.name}",
                                                    className="img-fluid",
                                                    style={"maxHeight": "150px"},
                                                ),
                                                width=2,
                                            ),
                                            dbc.Col(
                                                [
                                                    html.H5(
                                                        row["name"], className="mb-1"
                                                    ),
                                                    html.P(
                                                        (
                                                            f"Source: {row['source']}"
                                                            if row["source"]
                                                            else ""
                                                        ),
                                                        className="text-muted mb-1",
                                                    ),
                                                    html.P(
                                                        (
                                                            f"Site ID: {row['site_id']}"
                                                            if row["site_id"]
                                                            else ""
                                                        ),
                                                        className="text-muted",
                                                    ),
                                                ],
                                                width=8,
                                            ),
                                            dbc.Col(
                                                dbc.Button(
                                                    (
                                                        "Deselect"
                                                        if row["path"] in selected_set
                                                        else "Select"
                                                    ),
                                                    id={
                                                        "type": "select-btn",
                                                        "index": row.name,
                                                    },
                                                    color=(
                                                        "success"
                                                        if row["path"] in selected_set
                                                        else "primary"
                                                    ),
                                                    className="w-100",
                                                ),
                                                width=2,
                                            ),
                                        ],
                                        align="center",
                                    )
                                ]
                            )
                        ],
                        color="success" if row["path"] in selected_set else None,
                        outline=True,
                        className="mb-3",
                    ),
                    width=12,
                )
            ]
        )
        for _, row in page_data.iterrows()
    ]


def create_grid_view(page_data, selected_set):
    return dbc.Row(
        [
            dbc.Col(
                dbc.Card(
                    [
                        dbc.CardImg(
                            src=f"/images/{row.name}",
                            top=True,
                            style={"objectFit": "cover", "height": "200px"},
                        ),
                        dbc.CardBody(
                            [
                                html.H6(
                                    row["name"], className="card-title text-truncate"
                                ),
                                html.P(
                                    f"Source: {row['source']}" if row["source"] else "",
                                    className="text-muted mb-1 small",
                                ),
                                html.P(
                                    (
                                        f"Site ID: {row['site_id']}"
                                        if row["site_id"]
                                        else ""
                                    ),
                                    className="text-muted mb-2 small",
                                ),
                                dbc.Button(
                                    (
                                        "Deselect"
                                        if row["path"] in selected_set
                                        else "Select"
                                    ),
                                    id={"type": "select-btn", "index": row.name},
                                    color=(
                                        "success"
                                        if row["path"] in selected_set
                                        else "primary"
                                    ),
                                    className="w-100",
                                ),
                            ]
                        ),
                    ],
                    color="success" if row["path"] in selected_set else None,
                    outline=True,
                ),
                xs=12,
                sm=6,
                md=4,
                lg=3,
                className="mb-4",
            )
            for _, row in page_data.iterrows()
        ]
    )


# Callback to render main image grid/list
@app.callback(
    Output("image-container", "children"),
    [
        Input("current-page", "data"),
        Input("selected-images", "data"),
        Input("view-state", "data"),
    ],
)
def render_page(page, selected, view_state):
    if page is None:
        page = 0

    start_idx = page * PAGE_SIZE
    end_idx = start_idx + PAGE_SIZE
    page_data = df.iloc[start_idx:end_idx]
    selected_set = set(selected or [])

    if view_state == "row":
        return create_row_view(page_data, selected_set)
    else:
        return create_grid_view(page_data, selected_set)


# Callback to render selected images view
@app.callback(
    Output("selected-images-view", "children"),
    Input("url", "pathname"),
    State("selected-images", "data"),
)
def render_selected_images(pathname, selected):
    if pathname != "/selected":
        return []

    selected_set = set(selected or [])
    selected_data = df[df["path"].isin(selected_set)]

    return create_grid_view(selected_data, selected_set)


if __name__ == "__main__":
    app.run_server(debug=True)
