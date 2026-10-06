"""Dash page layouts for summary, lot, and equipment results."""

from dash import dash_table, dcc, html

from src.i18n import t


COLORS = {"navy": "#17365D", "blue": "#3973AC", "text": "#25313C", "muted": "#667482", "bg": "#F4F7FA", "border": "#E3E9EF"}


def _card(label: str, component_id: str) -> html.Div:
    return html.Div(
        [html.Div(label, className="metric-label"), html.Div(id=component_id, className="metric-value")],
        className="metric-card",
    )


def _panel(title: str, children, class_name: str = "panel", title_id: str | None = None) -> html.Div:
    heading = html.H3(title, id=title_id)
    return html.Div([heading, *children] if isinstance(children, list) else [heading, children], className=class_name)


def lot_table_columns(language: str) -> list[dict]:
    return [
        {"name": t(language, "table_product"), "id": "product"},
        {"name": t(language, "table_priority"), "id": "priority"},
        {"name": t(language, "table_completed_lots"), "id": "throughput", "type": "numeric", "format": {"specifier": ",.0f"}},
        {"name": t(language, "table_on_time"), "id": "on_time_pct", "type": "numeric", "format": {"specifier": ".2f"}},
        {"name": t(language, "table_cycle_time"), "id": "act_days", "type": "numeric", "format": {"specifier": ".2f"}},
        {"name": t(language, "table_mean_tardiness"), "id": "mean_tardiness_days", "type": "numeric", "format": {"specifier": ".2f"}},
        {"name": t(language, "table_waiting"), "id": "waiting_days", "type": "numeric", "format": {"specifier": ".2f"}},
        {"name": t(language, "table_processing"), "id": "processing_days", "type": "numeric", "format": {"specifier": ".2f"}},
        {"name": t(language, "table_transport"), "id": "transport_days", "type": "numeric", "format": {"specifier": ".2f"}},
    ]


def machine_table_columns(language: str) -> list[dict]:
    columns = [
        (t(language, "table_tool_group"), "tool_group", None),
        (t(language, "equipment_util"), "util_pct", ".2f"),
        (t(language, "equipment_avail"), "avail_pct", ".2f"),
        (t(language, "table_pm"), "pm_pct", ".2f"),
        (t(language, "table_breakdown"), "breakdown_pct", ".2f"),
        (t(language, "table_setup"), "setup_pct", ".2f"),
        (t(language, "table_waiting"), "waiting_days", ".3f"),
    ]
    return [{"name": name, "id": key, **({"type": "numeric", "format": {"specifier": fmt}} if fmt else {})} for name, key, fmt in columns]


def _lot_table(language: str) -> dash_table.DataTable:
    return dash_table.DataTable(
        id="lot-table",
        columns=lot_table_columns(language),
        data=[],
        sort_action="native",
        filter_action="native",
        page_action="native",
        page_size=15,
        style_table={"overflowX": "auto"},
        style_cell={"fontFamily": "Arial, sans-serif", "fontSize": 13, "padding": "9px", "textAlign": "left", "minWidth": "110px"},
        style_header={"backgroundColor": "#17365D", "color": "white", "fontWeight": 700, "whiteSpace": "normal"},
        style_data_conditional=[{"if": {"row_index": "odd"}, "backgroundColor": "#F7F9FB"}],
    )


def _machine_table(language: str) -> dash_table.DataTable:
    return dash_table.DataTable(
        id="machine-table",
        columns=machine_table_columns(language),
        data=[],
        sort_action="native",
        filter_action="native",
        page_action="native",
        page_size=20,
        style_table={"overflowX": "auto"},
        style_cell={"fontFamily": "Arial, sans-serif", "fontSize": 13, "padding": "9px", "textAlign": "right", "minWidth": "110px"},
        style_cell_conditional=[{"if": {"column_id": "tool_group"}, "textAlign": "left", "minWidth": "180px"}],
        style_header={"backgroundColor": "#17365D", "color": "white", "fontWeight": 700, "whiteSpace": "normal"},
        style_data_conditional=[
            {"if": {"filter_query": "{util_pct} > 100", "column_id": "util_pct"}, "color": "#A33A32", "fontWeight": 700},
            {"if": {"row_index": "odd"}, "backgroundColor": "#F7F9FB"},
        ],
    )


def build_layout(result_options: list[dict], selected_file: str | None, language: str = "ko"):
    return html.Div(
        [
            html.Header(
                [
                    html.Div([html.Div("FAB OPERATIONS", className="eyebrow"), html.H1(t(language, "page_title"), id="header-title"), html.P(t(language, "header_description"), id="header-description")], className="header-copy"),
                    html.Div(
                        [
                            html.Div(
                                [
                                    html.Button("한국어", id="language-ko", n_clicks=0, className="language-button language-active", type="button"),
                                    html.Button("English", id="language-en", n_clicks=0, className="language-button", type="button"),
                                ],
                                className="language-switch",
                                role="group",
                                **{"aria-label": "Language"},
                            ),
                            html.Div(
                                [
                                    html.Label(t(language, "file_label"), id="file-label", htmlFor="result-select"),
                                    dcc.Dropdown(id="result-select", options=result_options, value=selected_file, clearable=False, placeholder=t(language, "file_placeholder")),
                                    dcc.Upload(
                                        id="result-upload",
                                        children=html.Button(t(language, "upload_button"), id="upload-button", type="button", className="upload-button"),
                                        accept=".json,application/json",
                                        multiple=False,
                                        className="upload-control",
                                    ),
                                    html.Div(t(language, "upload_hint"), id="upload-hint", className="upload-hint"),
                                ],
                                className="file-picker",
                            ),
                        ],
                        className="header-tools",
                    ),
                ],
                className="app-header",
            ),
            html.Div(id="load-message", className="status-message", role="status"),
            html.Div(id="run-meta", className="run-meta"),
            dcc.Store(id="language-store", storage_type="local", data=language),
            dcc.Store(id="document-title-sync"),
            dcc.Store(id="load-state"),
            dcc.Store(id="result-data"),
            dcc.Tabs(
                id="main-tabs",
                value="overview",
                className="main-tabs",
                children=[
                    dcc.Tab(label=t(language, "tab_overview"), value="overview", id="tab-overview", children=[
                        html.Div(id="overview-cards", className="metric-grid"),
                        html.Div([_panel(t(language, "panel_overview_lots"), dcc.Graph(id="overview-lot-chart", config={"displaylogo": False}), title_id="panel-overview-lots"), _panel(t(language, "panel_overview_equipment"), dcc.Graph(id="overview-equipment-chart", config={"displaylogo": False}), title_id="panel-overview-equipment")], className="two-column"),
                        html.Div(id="overview-notes", className="note-list"),
                    ]),
                    dcc.Tab(label=t(language, "tab_lots"), value="lots", id="tab-lots", children=[
                        html.Div([
                            html.Div([html.Label(t(language, "priority_label"), id="priority-label"), dcc.Dropdown(id="lot-priority", options=[{"label": t(language, key), "value": value} for key, value in [("all_priorities", "전체 유형"), ("regular", "Regular"), ("hot", "Hot"), ("superhot", "SuperHot"), ("unknown", "Unknown")]], value="전체 유형", clearable=False)], className="control"),
                            html.Div([html.Label(t(language, "lot_metric_label"), id="lot-metric-label"), dcc.Dropdown(id="lot-metric", options=[{"label": t(language, label_key), "value": value} for label_key, value in [("metric_throughput", "throughput"), ("metric_cycle", "act_days"), ("metric_on_time", "on_time_pct"), ("metric_mean_tardiness", "mean_tardiness_days"), ("metric_late_tardiness", "late_lot_tardiness_days"), ("metric_waiting", "waiting_days")]], value="act_days", clearable=False)], className="control"),
                        ], className="filter-row"),
                        _panel(t(language, "panel_lot_metric"), dcc.Graph(id="lot-metric-chart", config={"displaylogo": False}), title_id="panel-lot-metric"),
                        _panel(t(language, "panel_lot_detail"), _lot_table(language), title_id="panel-lot-detail"),
                    ]),
                    dcc.Tab(label=t(language, "tab_equipment"), value="equipment", id="tab-equipment", children=[
                        html.Div([
                            html.Div([html.Label(t(language, "equipment_metric_label"), id="equipment-metric-label"), dcc.Dropdown(id="equipment-metric", options=[{"label": t(language, label_key), "value": key} for key, label_key in [("util_pct", "equipment_util"), ("waiting_days", "equipment_waiting"), ("avail_pct", "equipment_avail"), ("pm_pct", "equipment_pm"), ("breakdown_pct", "equipment_breakdown"), ("setup_pct", "equipment_setup")]], value="util_pct", clearable=False)], className="control"),
                            html.Div([html.Label(id="equipment-limit-label"), dcc.Slider(id="equipment-limit", min=5, max=30, step=5, value=15, marks={5: "5", 10: "10", 15: "15", 20: "20", 25: "25", 30: "30"})], className="control slider-control"),
                        ], className="filter-row"),
                        html.Div([_panel(t(language, "panel_equipment_metric"), dcc.Graph(id="equipment-metric-chart", config={"displaylogo": False}), title_id="panel-equipment-metric"), _panel(t(language, "panel_equipment_scatter"), dcc.Graph(id="equipment-scatter-chart", config={"displaylogo": False}), title_id="panel-equipment-scatter")], className="two-column"),
                        _panel(t(language, "panel_equipment_detail"), _machine_table(language), title_id="panel-equipment-detail"),
                        html.P(t(language, "footnote"), id="equipment-footnote", className="footnote"),
                    ]),
                ],
            ),
            html.Footer(t(language, "footer"), id="app-footer", className="app-footer"),
        ],
        className="app-shell",
    )
