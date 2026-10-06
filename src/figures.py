"""Plotly figure builders for the first dashboard version."""

from __future__ import annotations

from typing import Any

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

from src.i18n import t


COLORS = {
    "navy": "#17365D",
    "blue": "#3973AC",
    "teal": "#2A9D8F",
    "orange": "#E68632",
    "red": "#C65353",
    "grid": "#E8EDF2",
    "text": "#25313C",
}
PRIORITY_COLORS = {"Regular": "#3973AC", "Hot": "#E68632", "SuperHot": "#C65353", "Unknown": "#7C8794"}
METRIC_LABEL_KEYS = {
    "util_pct": "equipment_util",
    "waiting_days": "equipment_waiting",
    "avail_pct": "equipment_avail",
    "pm_pct": "equipment_pm",
    "breakdown_pct": "equipment_breakdown",
    "setup_pct": "equipment_setup",
}


def _priority_label(value: str, language: str) -> str:
    return t(language, "unknown") if value == "Unknown" else value


def empty_figure(message: str = "표시할 결과가 없습니다.") -> go.Figure:
    figure = go.Figure()
    figure.add_annotation(text=message, x=0.5, y=0.5, xref="paper", yref="paper", showarrow=False, font={"color": "#667482", "size": 14})
    figure.update_layout(template="plotly_white", height=330, margin={"l": 30, "r": 20, "t": 40, "b": 30})
    return figure


def _base_layout(figure: go.Figure, title: str, height: int = 360) -> go.Figure:
    figure.update_layout(
        title={"text": title, "x": 0.02, "xanchor": "left", "font": {"size": 16, "color": COLORS["navy"]}},
        template="plotly_white",
        height=height,
        margin={"l": 28, "r": 24, "t": 58, "b": 48},
        font={"family": "Arial, sans-serif", "color": COLORS["text"]},
        paper_bgcolor="white",
        plot_bgcolor="white",
    )
    figure.update_xaxes(showgrid=False, linecolor=COLORS["grid"])
    figure.update_yaxes(gridcolor=COLORS["grid"], zerolinecolor=COLORS["grid"])
    return figure


def overview_lot_figure(lots: list[dict[str, Any]], language: str = "ko") -> go.Figure:
    frame = pd.DataFrame(lots)
    if frame.empty:
        return empty_figure(t(language, "empty_equipment"))
    frame["display_product"] = frame["product"].replace({"기타 그룹": t(language, "other_group")})
    frame["display_priority"] = frame["priority"].map(lambda value: _priority_label(value, language))
    frame["group_label"] = frame["display_product"].astype(str) + " · " + frame["display_priority"].astype(str)
    fig = go.Figure()
    fig.add_trace(go.Bar(name=t(language, "fig_completed_lots"), x=frame["group_label"], y=frame["throughput"], marker_color=COLORS["blue"], yaxis="y"))
    fig.add_trace(go.Scatter(name=t(language, "fig_cycle_days"), x=frame["group_label"], y=frame["act_days"], mode="lines+markers", marker_color=COLORS["orange"], line={"width": 2}, yaxis="y2"))
    fig.update_layout(
        barmode="group",
        yaxis={"title": t(language, "fig_completed_lot_count"), "rangemode": "tozero", "gridcolor": COLORS["grid"]},
        yaxis2={"title": t(language, "fig_cycle_days"), "overlaying": "y", "side": "right", "showgrid": False},
        legend={"orientation": "h", "y": 1.12, "x": 1, "xanchor": "right"},
        xaxis={"tickangle": -35},
    )
    return _base_layout(fig, t(language, "panel_overview_lots"), 420)


def lot_metric_figure(lots: list[dict[str, Any]], priority: str, metric: str, language: str = "ko") -> go.Figure:
    frame = pd.DataFrame(lots)
    if frame.empty:
        return empty_figure(t(language, "empty_equipment"))
    if priority != "전체 유형":
        frame = frame[frame["priority"] == priority]
    if frame.empty:
        return empty_figure(t(language, "empty_priority"))
    labels = {
        "throughput": ("fig_completed_lots", "fig_completed_lots"),
        "act_days": ("fig_mean_cycle", "fig_cycle_days"),
        "on_time_pct": ("fig_on_time", "fig_on_time_pct"),
        "mean_tardiness_days": ("fig_mean_tardiness", "fig_mean_tardiness_days"),
        "late_lot_tardiness_days": ("fig_late_tardiness", "fig_late_tardiness_days"),
        "waiting_days": ("fig_waiting", "fig_waiting_days"),
    }
    title_key, y_title_key = labels.get(metric, labels["act_days"])
    title, y_title = t(language, title_key), t(language, y_title_key)
    frame["display_product"] = frame["product"].replace({"기타 그룹": t(language, "other_group")})
    frame["display_priority"] = frame["priority"].map(lambda value: _priority_label(value, language))
    hover_labels = {
        "name": t(language, "fig_lot_group"),
        "throughput": t(language, "fig_completed_lots"),
        "on_time_pct": t(language, "fig_on_time_pct"),
        "act_days": t(language, "fig_cycle_days"),
        "mean_tardiness_days": t(language, "fig_mean_tardiness_days"),
        "late_lot_tardiness_days": t(language, "fig_late_tardiness_days"),
        "waiting_days": t(language, "fig_waiting_days"),
        "display_product": t(language, "fig_product"),
        "display_priority": t(language, "fig_priority"),
    }
    fig = px.bar(
        frame,
        x="display_product",
        y=metric,
        color="display_priority",
        barmode="group",
        category_orders={"display_priority": [_priority_label(value, language) for value in ["Regular", "Hot", "SuperHot", "Unknown"]]},
        color_discrete_map={_priority_label(value, language): color for value, color in PRIORITY_COLORS.items()},
        hover_data={"name": True, "throughput": ":.0f", "on_time_pct": ":.2f", metric: ":.2f"},
        labels=hover_labels,
    )
    fig.update_layout(legend_title_text=t(language, "fig_priority"), xaxis_title=t(language, "fig_product"), yaxis_title=y_title)
    fig.update_xaxes(categoryorder="array", categoryarray=frame["display_product"].drop_duplicates().tolist())
    return _base_layout(fig, t(language, "figure_lot_title", title), 390)


def equipment_metric_figure(machines: list[dict[str, Any]], metric: str, limit: int, language: str = "ko") -> go.Figure:
    frame = pd.DataFrame(machines)
    if frame.empty or metric not in frame.columns:
        return empty_figure(t(language, "empty_equipment"))
    frame = frame.dropna(subset=[metric]).nlargest(max(1, int(limit)), metric).sort_values(metric, ascending=True)
    if frame.empty:
        return empty_figure(t(language, "empty_metric"))
    label = t(language, METRIC_LABEL_KEYS[metric])
    bar_color = [COLORS["red"] if metric == "util_pct" and value > 100 else COLORS["blue"] for value in frame[metric]]
    fig = go.Figure(go.Bar(
        x=frame[metric],
        y=frame["tool_group"],
        orientation="h",
        marker_color=bar_color,
        customdata=frame[["avail_pct", "util_pct", "pm_pct", "breakdown_pct", "setup_pct", "waiting_days"]],
        hovertemplate=(
            f"<b>%{{y}}</b><br>{t(language, 'hover_selected_metric')}: %{{x:.2f}}<br>"
            f"{t(language, 'hover_availability')}: %{{customdata[0]:.2f}}%<br>"
            f"{t(language, 'hover_utilization')}: %{{customdata[1]:.2f}}%<br>"
            f"{t(language, 'hover_pm')}: %{{customdata[2]:.2f}}%<br>"
            f"{t(language, 'hover_breakdown')}: %{{customdata[3]:.2f}}%<br>"
            f"{t(language, 'hover_setup')}: %{{customdata[4]:.2f}}%<br>"
            f"{t(language, 'hover_waiting')}: %{{customdata[5]:.2f}}{t(language, 'days_suffix')}<extra></extra>"
        ),
    ))
    fig.update_layout(xaxis_title=label, yaxis_title=t(language, "table_tool_group"), xaxis={"rangemode": "tozero"})
    if metric == "util_pct":
        fig.add_vline(x=100, line_dash="dash", line_color=COLORS["red"], annotation_text="100%", annotation_position="top")
    return _base_layout(fig, t(language, "figure_top_equipment", label, len(frame)), max(390, min(780, 22 * len(frame) + 130)))


def equipment_scatter_figure(machines: list[dict[str, Any]], language: str = "ko") -> go.Figure:
    frame = pd.DataFrame(machines)
    if frame.empty:
        return empty_figure(t(language, "empty_equipment"))
    frame = frame.dropna(subset=["util_pct", "waiting_days"])
    if frame.empty:
        return empty_figure(t(language, "empty_scatter"))
    fig = px.scatter(
        frame,
        x="util_pct",
        y="waiting_days",
        color="breakdown_pct",
        size="pm_pct",
        hover_name="tool_group",
        hover_data={"avail_pct": ":.2f", "util_pct": ":.2f", "breakdown_pct": ":.2f", "waiting_days": ":.2f"},
        color_continuous_scale="YlOrRd",
        labels={
            "tool_group": t(language, "table_tool_group"),
            "avail_pct": t(language, "equipment_avail"),
            "util_pct": t(language, "equipment_util"),
            "waiting_days": t(language, "equipment_waiting"),
            "breakdown_pct": t(language, "equipment_breakdown"),
            "pm_pct": t(language, "equipment_pm"),
        },
    )
    fig.add_vline(x=100, line_dash="dash", line_color=COLORS["red"], opacity=0.7)
    return _base_layout(fig, t(language, "fig_util_wait"), 420)
