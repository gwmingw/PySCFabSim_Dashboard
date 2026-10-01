"""Dash page layouts for summary, lot, and equipment results."""

from dash import dash_table, dcc, html


COLORS = {"navy": "#17365D", "blue": "#3973AC", "text": "#25313C", "muted": "#667482", "bg": "#F4F7FA", "border": "#E3E9EF"}


def _card(label: str, component_id: str) -> html.Div:
    return html.Div(
        [html.Div(label, className="metric-label"), html.Div(id=component_id, className="metric-value")],
        className="metric-card",
    )


def _panel(title: str, children, class_name: str = "panel") -> html.Div:
    return html.Div([html.H3(title), *children] if isinstance(children, list) else [html.H3(title), children], className=class_name)


def _lot_table() -> dash_table.DataTable:
    return dash_table.DataTable(
        id="lot-table",
        columns=[
            {"name": "제품", "id": "product"},
            {"name": "우선순위", "id": "priority"},
            {"name": "완료 lot", "id": "throughput", "type": "numeric", "format": {"specifier": ",.0f"}},
            {"name": "정시율 (%)", "id": "on_time_pct", "type": "numeric", "format": {"specifier": ".2f"}},
            {"name": "Cycle Time (일)", "id": "act_days", "type": "numeric", "format": {"specifier": ".2f"}},
            {"name": "평균 지연 (일)", "id": "mean_tardiness_days", "type": "numeric", "format": {"specifier": ".2f"}},
            {"name": "평균 대기 (일)", "id": "waiting_days", "type": "numeric", "format": {"specifier": ".2f"}},
            {"name": "처리시간 (일)", "id": "processing_days", "type": "numeric", "format": {"specifier": ".2f"}},
            {"name": "운반시간 (일)", "id": "transport_days", "type": "numeric", "format": {"specifier": ".2f"}},
        ],
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


def _machine_table() -> dash_table.DataTable:
    columns = [
        ("Tool Group", "tool_group", None),
        ("Utilization (%)", "util_pct", ".2f"),
        ("가용률 (%)", "avail_pct", ".2f"),
        ("PM (%)", "pm_pct", ".2f"),
        ("고장 (%)", "breakdown_pct", ".2f"),
        ("Setup (%)", "setup_pct", ".2f"),
        ("평균 대기 (일)", "waiting_days", ".3f"),
    ]
    return dash_table.DataTable(
        id="machine-table",
        columns=[{"name": name, "id": key, **({"type": "numeric", "format": {"specifier": fmt}} if fmt else {})} for name, key, fmt in columns],
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


def build_layout(result_options: list[dict], selected_file: str | None):
    return html.Div(
        [
            html.Header(
                [
                    html.Div([html.Div("FAB OPERATIONS", className="eyebrow"), html.H1("PySCFabSim 결과 대시보드"), html.P("기준 생산운영 결과를 lot 그룹과 설비 관점에서 탐색합니다.")]),
                    html.Div(
                        [
                            html.Label("결과 파일", htmlFor="result-select"),
                            dcc.Dropdown(id="result-select", options=result_options, value=selected_file, clearable=False, placeholder="결과 폴더의 JSON 선택"),
                            dcc.Upload(
                                id="result-upload",
                                children=html.Button("탐색기에서 JSON 선택", type="button", className="upload-button"),
                                accept=".json,application/json",
                                multiple=False,
                                className="upload-control",
                            ),
                            html.Div("업로드한 파일은 저장하지 않고 현재 화면에서만 읽습니다.", className="upload-hint"),
                        ],
                        className="file-picker",
                    ),
                ],
                className="app-header",
            ),
            html.Div(id="load-message", className="status-message", role="status"),
            html.Div(id="run-meta", className="run-meta"),
            dcc.Store(id="result-data"),
            dcc.Tabs(
                id="main-tabs",
                value="overview",
                className="main-tabs",
                children=[
                    dcc.Tab(label="운영 요약", value="overview", children=[
                        html.Div(id="overview-cards", className="metric-grid"),
                        html.Div([_panel("lot 그룹별 처리량과 Cycle Time", dcc.Graph(id="overview-lot-chart", config={"displaylogo": False})), _panel("Utilization 상위 Tool Group", dcc.Graph(id="overview-equipment-chart", config={"displaylogo": False}))], className="two-column"),
                        html.Div(id="overview-notes", className="note-list"),
                    ]),
                    dcc.Tab(label="Lot 그룹 성과", value="lots", children=[
                        html.Div([
                            html.Div([html.Label("우선순위 유형"), dcc.Dropdown(id="lot-priority", options=[{"label": x, "value": x} for x in ["전체 유형", "Regular", "Hot", "SuperHot", "Unknown"]], value="전체 유형", clearable=False)], className="control"),
                            html.Div([html.Label("차트 지표"), dcc.Dropdown(id="lot-metric", options=[{"label": x[0], "value": x[1]} for x in [("완료 lot 수", "throughput"), ("Cycle Time", "act_days"), ("정시 완료율", "on_time_pct"), ("완료 lot 기준 평균 지연", "mean_tardiness_days"), ("지연 lot 평균 지연", "late_lot_tardiness_days"), ("평균 대기시간", "waiting_days")]], value="act_days", clearable=False)], className="control"),
                        ], className="filter-row"),
                        _panel("lot 그룹 지표", dcc.Graph(id="lot-metric-chart", config={"displaylogo": False})),
                        _panel("Lot 그룹 상세", _lot_table()),
                    ]),
                    dcc.Tab(label="설비 분석", value="equipment", children=[
                        html.Div([
                            html.Div([html.Label("설비 지표"), dcc.Dropdown(id="equipment-metric", options=[{"label": label, "value": key} for key, label in [("util_pct", "Utilization (%)"), ("waiting_days", "평균 대기시간 (일)"), ("avail_pct", "가용률 (%)"), ("pm_pct", "PM 시간 비율 (%)"), ("breakdown_pct", "고장 시간 비율 (%)"), ("setup_pct", "Setup 시간 비율 (%)")]], value="util_pct", clearable=False)], className="control"),
                            html.Div([html.Label(id="equipment-limit-label"), dcc.Slider(id="equipment-limit", min=5, max=30, step=5, value=15, marks={5: "5", 10: "10", 15: "15", 20: "20", 25: "25", 30: "30"})], className="control slider-control"),
                        ], className="filter-row"),
                        html.Div([_panel("선택 지표 상위 Tool Group", dcc.Graph(id="equipment-metric-chart", config={"displaylogo": False})), _panel("Utilization과 대기시간", dcc.Graph(id="equipment-scatter-chart", config={"displaylogo": False}))], className="two-column"),
                        _panel("Tool Group 상세 지표", _machine_table()),
                        html.P("Utilization은 100% 초과값이 있을 수 있습니다. 해당 값은 자동 병목 판정이 아니라 원 지표 산식 확인 대상으로 표시합니다.", className="footnote"),
                    ]),
                ],
            ),
            html.Footer("읽기 전용 결과 뷰어 · PySCFabSim 입력 데이터와 원본 결과 파일은 수정하지 않습니다.", className="app-footer"),
        ],
        className="app-shell",
    )
