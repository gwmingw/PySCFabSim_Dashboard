"""Convert PySCFabSim aggregates to display-ready tables and KPIs."""

from __future__ import annotations

import re
from typing import Any

import pandas as pd


SECONDS_PER_DAY = 86_400
PRIORITY_ORDER = {"Regular": 0, "Hot": 1, "SuperHot": 2, "Unknown": 3}


def _safe(value: Any) -> float | None:
    if value is None:
        return None
    try:
        return float(value)
    except (TypeError, ValueError, OverflowError):
        return None


def lot_dataframe(lots: list[dict[str, Any]]) -> pd.DataFrame:
    rows: list[dict[str, Any]] = []
    pattern = re.compile(r"^(?:(SuperHot|Hot))?Lot_(\d+)$", flags=re.IGNORECASE)
    for lot in lots:
        name = str(lot.get("name", ""))
        match = pattern.match(name)
        prefix, product = match.groups() if match else (None, None)
        if prefix and prefix.lower() == "superhot":
            priority = "SuperHot"
        elif prefix and prefix.lower() == "hot":
            priority = "Hot"
        else:
            priority = "Regular" if product else "Unknown"

        throughput_value = _safe(lot.get("throughput"))
        on_time_value = _safe(lot.get("on_time"))
        throughput = throughput_value if throughput_value is not None else 0.0
        on_time = on_time_value if on_time_value is not None else 0.0
        late_count = max(throughput - on_time, 0.0) if throughput_value is not None and on_time_value is not None else None
        tardiness = _safe(lot.get("tardiness"))
        def mean_days(field: str) -> float | None:
            value = _safe(lot.get(field))
            return value / throughput / SECONDS_PER_DAY if value is not None and throughput > 0 else None

        rows.append({
            "name": name,
            "product": f"Product {int(product)}" if product else "기타 그룹",
            "product_number": int(product) if product else 999,
            "priority": priority,
            "priority_order": PRIORITY_ORDER[priority],
            "throughput": throughput,
            "on_time": on_time,
            "late_count": late_count,
            "on_time_pct": on_time / throughput * 100 if throughput_value is not None and on_time_value is not None and throughput > 0 else None,
            "act_days": _safe(lot.get("ACT")),
            "mean_tardiness_days": tardiness / throughput / SECONDS_PER_DAY if tardiness is not None and throughput_value is not None and throughput > 0 else None,
            "late_lot_tardiness_days": tardiness / late_count / SECONDS_PER_DAY if tardiness is not None and late_count is not None and late_count > 0 else (0.0 if late_count == 0 else None),
            "waiting_days": mean_days("waiting_time"),
            "processing_days": mean_days("processing_time"),
            "transport_days": mean_days("transport_time"),
            "batch_waiting_days": mean_days("waiting_time_batching"),
        })

    frame = pd.DataFrame(rows)
    if frame.empty:
        return frame
    return frame.sort_values(["product_number", "priority_order", "name"], kind="stable").reset_index(drop=True)


def machine_dataframe(machines: list[dict[str, Any]]) -> pd.DataFrame:
    rows = []
    for machine in machines:
        rows.append({
            "tool_group": str(machine.get("name", "")),
            "avail_pct": _as_percent(machine.get("avail")),
            "util_pct": _as_percent(machine.get("util")),
            "pm_pct": _as_percent(machine.get("pm")),
            "breakdown_pct": _as_percent(machine.get("br")),
            "setup_pct": _as_percent(machine.get("setup")),
            "waiting_days": _safe(machine.get("waiting_time")),
        })
    frame = pd.DataFrame(rows)
    if frame.empty:
        return frame
    return frame.sort_values(["util_pct", "tool_group"], ascending=[False, True], na_position="last").reset_index(drop=True)


def _as_percent(value: Any) -> float | None:
    number = _safe(value)
    return number * 100 if number is not None else None


def _json_records(frame: pd.DataFrame) -> list[dict[str, Any]]:
    if frame.empty:
        return []
    clean = frame.astype(object).where(pd.notna(frame), None)
    return clean.to_dict("records")


def build_dashboard_payload(result: dict[str, Any]) -> dict[str, Any]:
    lots = lot_dataframe(result.get("lots", []))
    machines = machine_dataframe(result.get("machines", []))
    total_throughput = float(lots["throughput"].sum()) if not lots.empty else 0.0
    valid_on_time = lots["on_time_pct"].notna() & (lots["throughput"] > 0) if not lots.empty else pd.Series(dtype=bool)
    on_time_denominator = float(lots.loc[valid_on_time, "throughput"].sum()) if not lots.empty else 0.0
    total_on_time = float(lots.loc[valid_on_time, "on_time"].sum()) if not lots.empty else 0.0
    cycle_time = None
    valid_act = lots["act_days"].notna() & (lots["throughput"] > 0) if not lots.empty else pd.Series(dtype=bool)
    cycle_denominator = float(lots.loc[valid_act, "throughput"].sum()) if not lots.empty else 0.0
    if cycle_denominator > 0:
        cycle_time = float((lots.loc[valid_act, "act_days"] * lots.loc[valid_act, "throughput"]).sum() / cycle_denominator)

    raw_days = result.get("metadata", {}).get("simulated_days")
    if raw_days is None:
        raw_days = result.get("metadata", {}).get("days")
    days = _safe(raw_days)
    over_util = machines[machines["util_pct"] > 100] if not machines.empty else machines
    notes = list(result.get("notes", []))
    if not machines.empty and not over_util.empty:
        names = ", ".join(over_util["tool_group"].astype(str).tolist())
        notes.append(f"Utilization이 100%를 넘는 Tool Group {len(over_util)}개: {names}. 병목으로 단정하기 전에 지표 산식을 확인하세요.")

    overview = {
        "completed_lots": int(round(total_throughput)),
        "on_time_lots": int(round(total_on_time)),
        "on_time_pct": total_on_time / on_time_denominator * 100 if on_time_denominator > 0 else None,
        "mean_cycle_days": cycle_time,
        "days": days,
        "daily_throughput": total_throughput / days if days and days > 0 else None,
        "lot_group_count": len(lots),
        "tool_group_count": len(machines),
        "late_lots": int(round(max(on_time_denominator - total_on_time, 0))),
        "cost": _safe(result.get("plugins", {}).get("cost")),
    }
    return {
        "filename": result.get("filename", ""),
        "metadata": result.get("metadata", {}),
        "overview": overview,
        "lots": _json_records(lots),
        "machines": _json_records(machines),
        "notes": list(dict.fromkeys(notes)),
    }
