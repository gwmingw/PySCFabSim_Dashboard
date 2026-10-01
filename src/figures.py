"""Plotly figure builders for the first dashboard version."""

from __future__ import annotations

from typing import Any

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go


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
METRIC_LABELS = {
    "util_pct": "Utilization (%)",
    "waiting_days": "평균 대기시간 (일)",
    "avail_pct": "가용률 (%)",
    "pm_pct": "PM 시간 비율 (%)",
    "breakdown_pct": "고장 시간 비율 (%)",
    "setup_pct": "Setup 시간 비율 (%)",
}


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


def overview_lot_figure(lots: list[dict[str, Any]]) -> go.Figure:
    frame = pd.DataFrame(lots)
    if frame.empty:
        return empty_figure()
    frame["group_label"] = frame["product"].astype(str) + " · " + frame["priority"].astype(str)
    fig = go.Figure()
    fig.add_trace(go.Bar(name="완료 lot", x=frame["group_label"], y=frame["throughput"], marker_color=COLORS["blue"], yaxis="y"))
    fig.add_trace(go.Scatter(name="Cycle Time (일)", x=frame["group_label"], y=frame["act_days"], mode="lines+markers", marker_color=COLORS["orange"], line={"width": 2}, yaxis="y2"))
    fig.update_layout(
        barmode="group",
        yaxis={"title": "완료 lot 수", "rangemode": "tozero", "gridcolor": COLORS["grid"]},
        yaxis2={"title": "Cycle Time (일)", "overlaying": "y", "side": "right", "showgrid": False},
        legend={"orientation": "h", "y": 1.12, "x": 1, "xanchor": "right"},
        xaxis={"tickangle": -35},
    )
    return _base_layout(fig, "Lot 그룹별 처리량과 Cycle Time", 420)


def lot_metric_figure(lots: list[dict[str, Any]], priority: str, metric: str) -> go.Figure:
    frame = pd.DataFrame(lots)
    if frame.empty:
        return empty_figure()
    if priority != "전체 유형":
        frame = frame[frame["priority"] == priority]
    if frame.empty:
        return empty_figure("선택한 유형에 표시할 lot 그룹이 없습니다.")
    labels = {
        "throughput": ("완료 lot 수", "완료 lot 수"),
        "act_days": ("평균 Cycle Time", "Cycle Time (일)"),
        "on_time_pct": ("정시 완료율", "정시 완료율 (%)"),
        "mean_tardiness_days": ("평균 지연시간", "완료 lot 기준 평균 지연 (일)"),
        "late_lot_tardiness_days": ("지연 lot 평균 지연시간", "지연 lot 평균 지연 (일)"),
        "waiting_days": ("평균 대기시간", "평균 대기시간 (일)"),
    }
    title, y_title = labels.get(metric, labels["act_days"])
    fig = px.bar(
        frame,
        x="product",
        y=metric,
        color="priority",
        barmode="group",
        category_orders={"priority": ["Regular", "Hot", "SuperHot", "Unknown"]},
        color_discrete_map=PRIORITY_COLORS,
        hover_data={"name": True, "throughput": ":.0f", "on_time_pct": ":.2f", metric: ":.2f"},
    )
    fig.update_layout(legend_title_text="우선순위", xaxis_title="제품", yaxis_title=y_title)
    fig.update_xaxes(categoryorder="array", categoryarray=frame["product"].drop_duplicates().tolist())
    return _base_layout(fig, f"제품별 {title}", 390)


def equipment_metric_figure(machines: list[dict[str, Any]], metric: str, limit: int) -> go.Figure:
    frame = pd.DataFrame(machines)
    if frame.empty or metric not in frame.columns:
        return empty_figure()
    frame = frame.dropna(subset=[metric]).nlargest(max(1, int(limit)), metric).sort_values(metric, ascending=True)
    if frame.empty:
        return empty_figure("선택한 지표에 값이 없습니다.")
    label = METRIC_LABELS.get(metric, metric)
    bar_color = [COLORS["red"] if metric == "util_pct" and value > 100 else COLORS["blue"] for value in frame[metric]]
    fig = go.Figure(go.Bar(
        x=frame[metric],
        y=frame["tool_group"],
        orientation="h",
        marker_color=bar_color,
        customdata=frame[["avail_pct", "util_pct", "pm_pct", "breakdown_pct", "setup_pct", "waiting_days"]],
        hovertemplate=(
            "<b>%{y}</b><br>선택 지표: %{x:.2f}<br>가용률: %{customdata[0]:.2f}%<br>"
            "Utilization: %{customdata[1]:.2f}%<br>PM: %{customdata[2]:.2f}%<br>"
            "고장: %{customdata[3]:.2f}%<br>Setup: %{customdata[4]:.2f}%<br>"
            "평균 대기: %{customdata[5]:.2f}일<extra></extra>"
        ),
    ))
    fig.update_layout(xaxis_title=label, yaxis_title="Tool Group", xaxis={"rangemode": "tozero"})
    if metric == "util_pct":
        fig.add_vline(x=100, line_dash="dash", line_color=COLORS["red"], annotation_text="100%", annotation_position="top")
    return _base_layout(fig, f"{label} 상위 {len(frame)}개", max(390, min(780, 22 * len(frame) + 130)))


def equipment_scatter_figure(machines: list[dict[str, Any]]) -> go.Figure:
    frame = pd.DataFrame(machines)
    if frame.empty:
        return empty_figure()
    frame = frame.dropna(subset=["util_pct", "waiting_days"])
    if frame.empty:
        return empty_figure("Utilization과 평균 대기시간이 모두 있는 설비가 없습니다.")
    fig = px.scatter(
        frame,
        x="util_pct",
        y="waiting_days",
        color="breakdown_pct",
        size="pm_pct",
        hover_name="tool_group",
        hover_data={"avail_pct": ":.2f", "util_pct": ":.2f", "breakdown_pct": ":.2f", "waiting_days": ":.2f"},
        color_continuous_scale="YlOrRd",
        labels={"util_pct": "Utilization (%)", "waiting_days": "평균 대기시간 (일)", "breakdown_pct": "고장 비율 (%)", "pm_pct": "PM 비율 (%)"},
    )
    fig.add_vline(x=100, line_dash="dash", line_color=COLORS["red"], opacity=0.7)
    return _base_layout(fig, "Utilization과 대기시간", 420)
