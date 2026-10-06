"""Local, read-only dashboard for PySCFabSim aggregate result JSON files."""

from __future__ import annotations

from dash import Dash, Input, Output, State, ctx, html, no_update

from config import DEFAULT_RESULTS_DIR, HOST, PORT
from src.figures import (
    empty_figure,
    equipment_metric_figure,
    equipment_scatter_figure,
    lot_metric_figure,
    overview_lot_figure,
)
from src.layout import build_layout
from src.metrics import build_dashboard_payload
from src.result_loader import ResultLoadError, list_result_files, load_result, load_uploaded_result


def _result_options() -> list[dict[str, str]]:
    return [{"label": name, "value": name} for name in list_result_files()]


RESULT_OPTIONS = _result_options()
DEFAULT_FILE = RESULT_OPTIONS[0]["value"] if RESULT_OPTIONS else None

dash_app = Dash(__name__, title="PySCFabSim 결과 대시보드", update_title="결과를 불러오는 중...")
dash_app.layout = build_layout(RESULT_OPTIONS, DEFAULT_FILE)

# Vercel's Python runtime expects a WSGI application named `app`.
app = dash_app.server
server = app


def _format(value, digits: int = 2, suffix: str = "") -> str:
    if value is None:
        return "미상"
    try:
        return f"{float(value):,.{digits}f}{suffix}"
    except (TypeError, ValueError):
        return "미상"


def _metric_card(label: str, value: str, caption: str = "") -> html.Div:
    return html.Div(
        [html.Div(label, className="metric-label"), html.Div(value, className="metric-value"), html.Div(caption, className="metric-caption")],
        className="metric-card",
    )


@dash_app.callback(
    Output("result-data", "data"),
    Output("load-message", "children"),
    Output("load-message", "className"),
    Input("result-select", "value"),
    Input("result-upload", "contents"),
    State("result-upload", "filename"),
)
def load_selected_result(filename: str | None, upload_contents: str | None, upload_filename: str | None):
    is_upload = ctx.triggered_id == "result-upload"
    if is_upload and not upload_contents:
        return no_update, no_update, no_update
    if not is_upload and not filename:
        return None, f"JSON 결과 파일을 찾지 못했습니다. 결과 폴더: {DEFAULT_RESULTS_DIR}", "status-message status-warning"
    try:
        if is_upload:
            result = load_uploaded_result(upload_filename, upload_contents)
            selected_name = f"업로드 · {result['filename']}"
        else:
            result = load_result(filename)
            selected_name = filename
        payload = build_dashboard_payload(result)
        if payload["notes"]:
            message = f"{selected_name} 로드 완료 · 확인할 참고 항목 {len(payload['notes'])}개"
            class_name = "status-message status-warning"
        else:
            message = f"{selected_name} 로드 완료"
            class_name = "status-message status-ok"
        return payload, message, class_name
    except ResultLoadError as exc:
        return None, f"결과를 불러오지 못했습니다: {exc}", "status-message status-error"


@dash_app.callback(Output("run-meta", "children"), Input("result-data", "data"))
def show_run_metadata(payload):
    if not payload:
        return html.Div("결과 메타데이터 없음", className="meta-chip")
    meta = payload.get("metadata", {})
    items = [
        ("Dataset", meta.get("dataset", "미상")),
        ("Dispatcher", meta.get("dispatcher", "미상")),
        ("Seed", meta.get("seed", "미상")),
        ("기간", f"{meta.get('days')}일" if meta.get("days") is not None else "미상"),
        ("JSON", payload.get("filename", "")),
    ]
    if meta.get("runtime") and meta["runtime"] != "미상":
        items.append(("실행시간", meta["runtime"]))
    return [html.Div([html.Span(label, className="meta-label"), html.Span(str(value), className="meta-value")], className="meta-chip") for label, value in items]


@dash_app.callback(
    Output("overview-cards", "children"),
    Output("overview-lot-chart", "figure"),
    Output("overview-equipment-chart", "figure"),
    Output("overview-notes", "children"),
    Input("result-data", "data"),
)
def render_overview(payload):
    if not payload:
        return [], empty_figure("결과 JSON을 선택해 주세요."), empty_figure("결과 JSON을 선택해 주세요."), []
    overview = payload["overview"]
    cards = [
        _metric_card("완료 lot", _format(overview["completed_lots"], 0), f"lot 그룹 {overview['lot_group_count']}개"),
        _metric_card("일평균 처리량", _format(overview["daily_throughput"], 2, " lot/일"), f"시뮬레이션 { _format(overview['days'], 2, '일') }"),
        _metric_card("가중 평균 Cycle Time", _format(overview["mean_cycle_days"], 2, "일"), "완료 lot 수 가중 평균"),
        _metric_card("정시 완료율", _format(overview["on_time_pct"], 2, "%"), f"정시 {overview['on_time_lots']:,} / 지연 {overview['late_lots']:,}"),
        _metric_card("Tool Group", _format(overview["tool_group_count"], 0), "최종 집계 설비 그룹 수"),
    ]
    notes = [html.Div(note, className="note-item") for note in payload.get("notes", [])]
    if not notes:
        notes = [html.Div("현재 결과에서 별도 데이터 주의 항목이 없습니다.", className="note-item note-ok")]
    if overview["days"] is None:
        notes.append(html.Div("실행 기간을 확인하지 못해 일평균 처리량은 미상입니다.", className="note-item note-warning"))
    return cards, overview_lot_figure(payload["lots"]), equipment_metric_figure(payload["machines"], "util_pct", 10), notes


@dash_app.callback(
    Output("lot-metric-chart", "figure"),
    Output("lot-table", "data"),
    Input("result-data", "data"),
    Input("lot-priority", "value"),
    Input("lot-metric", "value"),
)
def render_lot_results(payload, priority, metric):
    if not payload:
        return empty_figure("결과 JSON을 선택해 주세요."), []
    lots = payload["lots"]
    selected = lots if priority == "전체 유형" else [row for row in lots if row["priority"] == priority]
    return lot_metric_figure(lots, priority or "전체 유형", metric or "act_days"), selected


@dash_app.callback(
    Output("equipment-metric-chart", "figure"),
    Output("equipment-scatter-chart", "figure"),
    Output("machine-table", "data"),
    Output("equipment-limit-label", "children"),
    Input("result-data", "data"),
    Input("equipment-metric", "value"),
    Input("equipment-limit", "value"),
)
def render_equipment_results(payload, metric, limit):
    if not payload:
        return empty_figure("결과 JSON을 선택해 주세요."), empty_figure("결과 JSON을 선택해 주세요."), [], "표시 개수"
    machines = payload["machines"]
    return (
        equipment_metric_figure(machines, metric or "util_pct", limit or 15),
        equipment_scatter_figure(machines),
        machines,
        f"상위 Tool Group 수: {limit or 15}",
    )


if __name__ == "__main__":
    dash_app.run(host=HOST, port=PORT, debug=False)
