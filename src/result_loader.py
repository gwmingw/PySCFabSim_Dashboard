"""Read-only loading and validation for PySCFabSim result files."""

from __future__ import annotations

import json
import math
import re
from pathlib import Path
from typing import Any

from config import DEFAULT_RESULTS_DIR


REQUIRED_TOP_LEVEL = {"lots", "machines"}
LOT_FIELDS = (
    "ACT",
    "throughput",
    "on_time",
    "tardiness",
    "waiting_time",
    "processing_time",
    "transport_time",
    "waiting_time_batching",
)
MACHINE_FIELDS = ("avail", "util", "pm", "br", "setup", "waiting_time")


class ResultLoadError(ValueError):
    """An input file is missing or does not match the expected result schema."""


def list_result_files(results_dir: Path | str = DEFAULT_RESULTS_DIR) -> list[str]:
    """Return JSON result basenames in a directory, newest first."""
    directory = Path(results_dir)
    if not directory.exists():
        return []
    return [p.name for p in sorted(directory.glob("*.json"), key=lambda p: p.stat().st_mtime, reverse=True)]


def _number(value: Any) -> float | None:
    if value is None or isinstance(value, bool):
        return None
    try:
        number = float(value)
    except (TypeError, ValueError, OverflowError):
        return None
    return number if math.isfinite(number) else None


def _decode_text(path: Path) -> str:
    raw = path.read_bytes()
    for encoding in ("utf-8-sig", "utf-16", "cp949"):
        try:
            return raw.decode(encoding)
        except UnicodeError:
            continue
    return raw.decode("utf-8", errors="replace")


def _read_metadata(json_path: Path) -> tuple[dict[str, Any], list[str]]:
    metadata: dict[str, Any] = {
        "dataset": "미상",
        "dispatcher": "미상",
        "days": None,
        "seed": "미상",
        "runtime": "미상",
    }
    notes: list[str] = []

    days_from_name = re.search(r"(?:^|_)(\d+)days(?:_|$)", json_path.stem, flags=re.IGNORECASE)
    if days_from_name:
        metadata["days"] = int(days_from_name.group(1))

    log_path = json_path.with_suffix(".log")
    if log_path.is_file():
        text = _decode_text(log_path)
        match = re.search(r"Loading\s+(\S+)\s+for\s+(\d+)\s+days,\s+using\s+(\S+)", text)
        if match:
            metadata["dataset"], log_days, metadata["dispatcher"] = match.groups()
            metadata["days"] = int(log_days)
        simulated = re.search(r"([\d.]+)\s+days simulated in\s+(.+)", text)
        if simulated:
            metadata["simulated_days"] = _number(simulated.group(1))
            metadata["runtime"] = simulated.group(2).strip()
    else:
        notes.append("같은 이름의 .log가 없어 실행 설정 일부를 확인할 수 없습니다.")

    # The current simulator JSON schema does not include the seed. The sibling
    # summary is used only for run metadata, never for KPI calculations.
    summary_path = json_path.with_name(f"{json_path.stem}_summary.md")
    if summary_path.is_file():
        summary_text = _decode_text(summary_path)
        seed_match = re.search(r"Random seed:\s*([^\r\n]+)", summary_text, flags=re.IGNORECASE)
        if seed_match:
            metadata["seed"] = seed_match.group(1).strip().strip("`")

    for field in ("dataset", "dispatcher"):
        if metadata[field] == "미상":
            notes.append(f"{field} 정보를 로그에서 찾지 못했습니다.")
    if metadata["seed"] == "미상":
        notes.append("JSON에는 seed가 없어 실행 요약 파일이 없으면 seed는 미상으로 표시됩니다.")
    return metadata, notes


def load_result(filename: str, results_dir: Path | str = DEFAULT_RESULTS_DIR) -> dict[str, Any]:
    """Load a result by basename, enforcing that it stays in results_dir."""
    if not filename or Path(filename).name != filename or Path(filename).suffix.lower() != ".json":
        raise ResultLoadError("결과 폴더 안의 JSON 파일을 선택해 주세요.")

    directory = Path(results_dir).resolve()
    json_path = (directory / filename).resolve()
    if json_path.parent != directory:
        raise ResultLoadError("선택한 파일이 결과 폴더 밖에 있습니다.")
    if not json_path.is_file():
        raise ResultLoadError(f"결과 파일을 찾을 수 없습니다: {json_path}")

    try:
        with json_path.open("r", encoding="utf-8-sig") as stream:
            raw = json.load(stream)
    except (OSError, UnicodeError, json.JSONDecodeError) as exc:
        raise ResultLoadError(f"JSON을 읽을 수 없습니다: {exc}") from exc

    if not isinstance(raw, dict):
        raise ResultLoadError("JSON 최상위 값은 객체여야 합니다.")
    missing_top = sorted(REQUIRED_TOP_LEVEL - raw.keys())
    if missing_top:
        raise ResultLoadError(f"필수 키가 없습니다: {', '.join(missing_top)}")
    if not isinstance(raw["lots"], dict) or not isinstance(raw["machines"], dict):
        raise ResultLoadError("lots와 machines는 JSON 객체여야 합니다.")

    notes: list[str] = []
    lots: list[dict[str, Any]] = []
    for name, fields in raw["lots"].items():
        if not isinstance(fields, dict):
            notes.append(f"lot 그룹 {name}: 결과가 객체가 아니어서 제외했습니다.")
            continue
        row = {field: _number(fields.get(field)) for field in LOT_FIELDS}
        missing = [field for field, value in row.items() if value is None]
        if missing:
            notes.append(f"lot 그룹 {name}: 값이 없거나 숫자가 아닌 필드({', '.join(missing)})가 있습니다.")
        row["name"] = str(name)
        lots.append(row)

    machines: list[dict[str, Any]] = []
    for name, fields in raw["machines"].items():
        if not isinstance(fields, dict):
            notes.append(f"Tool Group {name}: 결과가 객체가 아니어서 제외했습니다.")
            continue
        row = {field: _number(fields.get(field)) for field in MACHINE_FIELDS}
        missing = [field for field, value in row.items() if value is None]
        if missing:
            notes.append(f"Tool Group {name}: 값이 없거나 숫자가 아닌 필드({', '.join(missing)})가 있습니다.")
        row["name"] = str(name)
        machines.append(row)

    if not lots:
        notes.append("유효한 lot 그룹 데이터가 없습니다.")
    if not machines:
        notes.append("유효한 Tool Group 데이터가 없습니다.")

    metadata, metadata_notes = _read_metadata(json_path)
    notes.extend(metadata_notes)
    return {
        "filename": json_path.name,
        "metadata": metadata,
        "lots": lots,
        "machines": machines,
        "plugins": raw.get("plugins", {}) if isinstance(raw.get("plugins", {}), dict) else {},
        "notes": list(dict.fromkeys(notes)),
    }
