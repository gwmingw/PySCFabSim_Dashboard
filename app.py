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
from src.i18n import t, translate_error, translate_note
from src.layout import build_layout, lot_table_columns, machine_table_columns
from src.metrics import build_dashboard_payload
from src.result_loader import ResultLoadError, list_result_files, load_result, load_uploaded_result


def _result_options() -> list[dict[str, str]]:
    return [{"label": name, "value": name} for name in list_result_files()]


RESULT_OPTIONS = _result_options()
DEFAULT_FILE = RESULT_OPTIONS[0]["value"] if RESULT_OPTIONS else None

dash_app = Dash(__name__, title="PySCFabSim 결과 대시보드", update_title="Loading results...")
dash_app.layout = build_layout(RESULT_OPTIONS, DEFAULT_FILE, "ko")

# Vercel's Python runtime expects a WSGI application named `app`.
app = dash_app.server
server = app

dash_app.clientside_callback(
    """
    function(language) {
        document.title = language === "en"
            ? "PySCFabSim Results Dashboard"
            : "PySCFabSim 결과 대시보드";
        return language;
    }
    """,
    Output("document-title-sync", "data"),
    Input("language-store", "data"),
)


def _format(value, digits: int = 2, suffix: str = "", unknown: str = "미상") -> str:
    if value is None:
        return unknown
    try:
        return f"{float(value):,.{digits}f}{suffix}"
    except (TypeError, ValueError):
        return unknown


def _metric_card(label: str, value: str, caption: str = "") -> html.Div:
    return html.Div(
        [html.Div(label, className="metric-label"), html.Div(value, className="metric-value"), html.Div(caption, className="metric-caption")],
        className="metric-card",
    )


@dash_app.callback(
    Output("language-store", "data"),
    Input("language-ko", "n_clicks"),
    Input("language-en", "n_clicks"),
    State("language-store", "data"),
    prevent_initial_call=True,
)
def select_language(_ko_clicks, _en_clicks, current_language):
    if ctx.triggered_id == "language-ko":
        return "ko"
    if ctx.triggered_id == "language-en":
        return "en"
    return current_language or "ko"


@dash_app.callback(
    Output("language-ko", "className"),
    Output("language-en", "className"),
    Input("language-store", "data"),
)
def mark_active_language(language):
    return (
        "language-button language-active" if language != "en" else "language-button",
        "language-button language-active" if language == "en" else "language-button",
    )


@dash_app.callback(
    Output("header-title", "children"),
    Output("header-description", "children"),
    Output("file-label", "children"),
    Output("result-select", "placeholder"),
    Output("upload-button", "children"),
    Output("upload-hint", "children"),
    Output("tab-overview", "label"),
    Output("tab-lots", "label"),
    Output("tab-equipment", "label"),
    Output("panel-overview-lots", "children"),
    Output("panel-overview-equipment", "children"),
    Output("priority-label", "children"),
    Output("lot-priority", "options"),
    Output("lot-metric-label", "children"),
    Output("lot-metric", "options"),
    Output("panel-lot-metric", "children"),
    Output("panel-lot-detail", "children"),
    Output("lot-table", "columns"),
    Output("equipment-metric-label", "children"),
    Output("equipment-metric", "options"),
    Output("panel-equipment-metric", "children"),
    Output("panel-equipment-scatter", "children"),
    Output("panel-equipment-detail", "children"),
    Output("machine-table", "columns"),
    Output("equipment-footnote", "children"),
    Output("app-footer", "children"),
    Input("language-store", "data"),
)
def translate_static_ui(language):
    language = language if language in {"ko", "en"} else "ko"
    priority_options = [
        {"label": t(language, key), "value": value}
        for key, value in [
            ("all_priorities", "전체 유형"),
            ("regular", "Regular"),
            ("hot", "Hot"),
            ("superhot", "SuperHot"),
            ("unknown", "Unknown"),
        ]
    ]
    lot_metric_options = [
        {"label": t(language, label), "value": value}
        for label, value in [
            ("metric_throughput", "throughput"),
            ("metric_cycle", "act_days"),
            ("metric_on_time", "on_time_pct"),
            ("metric_mean_tardiness", "mean_tardiness_days"),
            ("metric_late_tardiness", "late_lot_tardiness_days"),
            ("metric_waiting", "waiting_days"),
        ]
    ]
    equipment_metric_options = [
        {"label": t(language, label), "value": value}
        for value, label in [
            ("util_pct", "equipment_util"),
            ("waiting_days", "equipment_waiting"),
            ("avail_pct", "equipment_avail"),
            ("pm_pct", "equipment_pm"),
            ("breakdown_pct", "equipment_breakdown"),
            ("setup_pct", "equipment_setup"),
        ]
    ]
    return (
        t(language, "page_title"),
        t(language, "header_description"),
        t(language, "file_label"),
        t(language, "file_placeholder"),
        t(language, "upload_button"),
        t(language, "upload_hint"),
        t(language, "tab_overview"),
        t(language, "tab_lots"),
        t(language, "tab_equipment"),
        t(language, "panel_overview_lots"),
        t(language, "panel_overview_equipment"),
        t(language, "priority_label"),
        priority_options,
        t(language, "lot_metric_label"),
        lot_metric_options,
        t(language, "panel_lot_metric"),
        t(language, "panel_lot_detail"),
        lot_table_columns(language),
        t(language, "equipment_metric_label"),
        equipment_metric_options,
        t(language, "panel_equipment_metric"),
        t(language, "panel_equipment_scatter"),
        t(language, "panel_equipment_detail"),
        machine_table_columns(language),
        t(language, "footnote"),
        t(language, "footer"),
    )


@dash_app.callback(
    Output("result-data", "data"),
    Output("load-state", "data"),
    Input("result-select", "value"),
    Input("result-upload", "contents"),
    State("result-upload", "filename"),
)
def load_selected_result(filename: str | None, upload_contents: str | None, upload_filename: str | None):
    is_upload = ctx.triggered_id == "result-upload"
    if is_upload and not upload_contents:
        return no_update, no_update
    if not is_upload and not filename:
        return None, {"kind": "no_file", "path": str(DEFAULT_RESULTS_DIR)}
    try:
        if is_upload:
            result = load_uploaded_result(upload_filename, upload_contents)
            selected_name = result["filename"]
        else:
            result = load_result(filename)
            selected_name = filename
        payload = build_dashboard_payload(result)
        return payload, {"kind": "loaded", "filename": selected_name, "uploaded": is_upload, "notes": len(payload["notes"])}
    except ResultLoadError as exc:
        return None, {"kind": "error", "message": str(exc)}


@dash_app.callback(
    Output("load-message", "children"),
    Output("load-message", "className"),
    Input("load-state", "data"),
    Input("language-store", "data"),
)
def show_load_status(load_state, language):
    if not load_state:
        return "", "status-message"
    kind = load_state.get("kind")
    if kind == "no_file":
        return t(language, "load_no_file", load_state.get("path", "")), "status-message status-warning"
    if kind == "error":
        return t(language, "load_error", translate_error(load_state.get("message", ""), language)), "status-message status-error"
    filename = load_state.get("filename", "")
    if load_state.get("uploaded"):
        filename = t(language, "load_uploaded", filename)
    note_count = load_state.get("notes", 0)
    if note_count:
        return t(language, "load_success_notes", filename, note_count), "status-message status-warning"
    return t(language, "load_success", filename), "status-message status-ok"


@dash_app.callback(
    Output("run-meta", "children"),
    Input("result-data", "data"),
    Input("language-store", "data"),
)
def show_run_metadata(payload, language):
    if not payload:
        return html.Div(t(language, "no_result_metadata"), className="meta-chip")
    meta = payload.get("metadata", {})
    unknown = t(language, "unknown")
    items = [
        (t(language, "meta_dataset"), meta.get("dataset", unknown)),
        (t(language, "meta_dispatcher"), meta.get("dispatcher", unknown)),
        (t(language, "meta_seed"), meta.get("seed", unknown)),
        (t(language, "meta_period"), f"{meta.get('days')}{t(language, 'days_suffix')}" if meta.get("days") is not None else unknown),
        (t(language, "meta_json"), payload.get("filename", "")),
    ]
    if meta.get("runtime") and meta["runtime"] not in {"미상", "Unknown"}:
        items.append((t(language, "meta_runtime"), meta["runtime"]))
    items = [(label, unknown if value == "미상" else value) for label, value in items]
    return [html.Div([html.Span(label, className="meta-label"), html.Span(str(value), className="meta-value")], className="meta-chip") for label, value in items]


@dash_app.callback(
    Output("overview-cards", "children"),
    Output("overview-lot-chart", "figure"),
    Output("overview-equipment-chart", "figure"),
    Output("overview-notes", "children"),
    Input("result-data", "data"),
    Input("language-store", "data"),
)
def render_overview(payload, language):
    if not payload:
        empty_message = t(language, "no_result_file")
        return [], empty_figure(empty_message), empty_figure(empty_message), []
    overview = payload["overview"]
    unknown = t(language, "unknown")
    cards = [
        _metric_card(t(language, "kpi_completed"), _format(overview["completed_lots"], 0, unknown=unknown), t(language, "kpi_lot_groups", overview["lot_group_count"])),
        _metric_card(t(language, "kpi_daily_throughput"), _format(overview["daily_throughput"], 2, t(language, "throughput_suffix"), unknown), t(language, "kpi_simulation_days", _format(overview["days"], 2, unknown=unknown))),
        _metric_card(t(language, "kpi_weighted_cycle"), _format(overview["mean_cycle_days"], 2, t(language, "days_suffix"), unknown), t(language, "kpi_weighted_cycle_caption")),
        _metric_card(t(language, "kpi_on_time"), _format(overview["on_time_pct"], 2, "%", unknown), t(language, "kpi_on_time_caption", f"{overview['on_time_lots']:,}", f"{overview['late_lots']:,}")),
        _metric_card(t(language, "kpi_tool_groups"), _format(overview["tool_group_count"], 0, unknown=unknown), t(language, "kpi_tool_groups_caption")),
    ]
    notes = [html.Div(translate_note(note, language), className="note-item") for note in payload.get("notes", [])]
    if not notes:
        notes = [html.Div(t(language, "default_notes_ok"), className="note-item note-ok")]
    if overview["days"] is None:
        notes.append(html.Div(t(language, "days_unknown_note"), className="note-item note-warning"))
    return cards, overview_lot_figure(payload["lots"], language), equipment_metric_figure(payload["machines"], "util_pct", 10, language), notes


@dash_app.callback(
    Output("lot-metric-chart", "figure"),
    Output("lot-table", "data"),
    Input("result-data", "data"),
    Input("lot-priority", "value"),
    Input("lot-metric", "value"),
    Input("language-store", "data"),
)
def render_lot_results(payload, priority, metric, language):
    if not payload:
        return empty_figure(t(language, "no_result_file")), []
    lots = payload["lots"]
    selected = lots if priority == "전체 유형" else [row for row in lots if row["priority"] == priority]
    selected = [
        {
            **row,
            "product": t(language, "other_group") if row["product"] == "기타 그룹" else row["product"],
            "priority": t(language, "unknown") if row["priority"] == "Unknown" else row["priority"],
        }
        for row in selected
    ]
    return lot_metric_figure(lots, priority or "전체 유형", metric or "act_days", language), selected


@dash_app.callback(
    Output("equipment-metric-chart", "figure"),
    Output("equipment-scatter-chart", "figure"),
    Output("machine-table", "data"),
    Output("equipment-limit-label", "children"),
    Input("result-data", "data"),
    Input("equipment-metric", "value"),
    Input("equipment-limit", "value"),
    Input("language-store", "data"),
)
def render_equipment_results(payload, metric, limit, language):
    if not payload:
        empty_message = t(language, "no_result_file")
        return empty_figure(empty_message), empty_figure(empty_message), [], t(language, "no_equipment_limit")
    machines = payload["machines"]
    return (
        equipment_metric_figure(machines, metric or "util_pct", limit or 15, language),
        equipment_scatter_figure(machines, language),
        machines,
        t(language, "top_tool_groups", limit or 15),
    )


if __name__ == "__main__":
    dash_app.run(host=HOST, port=PORT, debug=False)
