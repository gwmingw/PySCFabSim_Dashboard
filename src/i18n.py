"""Korean and English labels for the dashboard UI."""

from __future__ import annotations

import re


TEXT = {
    "page_title": ("PySCFabSim 결과 대시보드", "PySCFabSim Results Dashboard"),
    "header_description": (
        "기준 생산운영 결과를 lot 그룹과 설비 관점에서 탐색합니다.",
        "Explore baseline production results by lot group and equipment.",
    ),
    "file_label": ("결과 파일", "Result file"),
    "file_placeholder": ("결과 폴더의 JSON 선택", "Select a JSON from the results folder"),
    "upload_button": ("탐색기에서 JSON 선택", "Choose JSON file"),
    "upload_hint": ("업로드한 파일은 저장하지 않고 현재 화면에서만 읽습니다.", "Uploaded files are read for this view and are not saved."),
    "tab_overview": ("운영 요약", "Operations overview"),
    "tab_lots": ("Lot 그룹 성과", "Lot group performance"),
    "tab_equipment": ("설비 분석", "Equipment analysis"),
    "panel_overview_lots": ("lot 그룹별 처리량과 Cycle Time", "Throughput and cycle time by lot group"),
    "panel_overview_equipment": ("Utilization 상위 Tool Group", "Top Tool Groups by utilization"),
    "priority_label": ("우선순위 유형", "Priority type"),
    "lot_metric_label": ("차트 지표", "Chart metric"),
    "equipment_metric_label": ("설비 지표", "Equipment metric"),
    "all_priorities": ("전체 유형", "All priorities"),
    "regular": ("Regular", "Regular"),
    "hot": ("Hot", "Hot"),
    "superhot": ("SuperHot", "SuperHot"),
    "unknown": ("미상", "Unknown"),
    "metric_throughput": ("완료 lot 수", "Completed lots"),
    "metric_cycle": ("Cycle Time", "Cycle time"),
    "metric_on_time": ("정시 완료율", "On-time completion rate"),
    "metric_mean_tardiness": ("완료 lot 기준 평균 지연", "Average tardiness per completed lot"),
    "metric_late_tardiness": ("지연 lot 평균 지연", "Average tardiness of late lots"),
    "metric_waiting": ("평균 대기시간", "Average waiting time"),
    "table_product": ("제품", "Product"),
    "table_priority": ("우선순위", "Priority"),
    "table_completed_lots": ("완료 lot", "Completed lots"),
    "table_on_time": ("정시율 (%)", "On-time (%)"),
    "table_cycle_time": ("Cycle Time (일)", "Cycle time (days)"),
    "table_mean_tardiness": ("평균 지연 (일)", "Average tardiness (days)"),
    "table_waiting": ("평균 대기 (일)", "Average waiting (days)"),
    "table_processing": ("처리시간 (일)", "Processing time (days)"),
    "table_transport": ("운반시간 (일)", "Transport time (days)"),
    "table_tool_group": ("Tool Group", "Tool Group"),
    "table_pm": ("PM (%)", "PM (%)"),
    "table_breakdown": ("고장 (%)", "Breakdown (%)"),
    "table_setup": ("Setup (%)", "Setup (%)"),
    "equipment_util": ("Utilization (%)", "Utilization (%)"),
    "equipment_waiting": ("평균 대기시간 (일)", "Average waiting time (days)"),
    "equipment_avail": ("가용률 (%)", "Availability (%)"),
    "equipment_pm": ("PM 시간 비율 (%)", "PM time (%)"),
    "equipment_breakdown": ("고장 시간 비율 (%)", "Breakdown time (%)"),
    "equipment_setup": ("Setup 시간 비율 (%)", "Setup time (%)"),
    "panel_lot_metric": ("lot 그룹 지표", "Lot group metrics"),
    "panel_lot_detail": ("Lot 그룹 상세", "Lot group details"),
    "panel_equipment_metric": ("선택 지표 상위 Tool Group", "Top Tool Groups by selected metric"),
    "panel_equipment_scatter": ("Utilization과 대기시간", "Utilization vs. waiting time"),
    "panel_equipment_detail": ("Tool Group 상세 지표", "Tool Group details"),
    "footnote": (
        "Utilization은 100% 초과값이 있을 수 있습니다. 해당 값은 자동 병목 판정이 아니라 원 지표 산식 확인 대상으로 표시합니다.",
        "Utilization can exceed 100%. Such values are flagged for metric-definition review, not automatically classified as bottlenecks.",
    ),
    "footer": (
        "읽기 전용 결과 뷰어 · PySCFabSim 입력 데이터와 원본 결과 파일은 수정하지 않습니다.",
        "Read-only results viewer · PySCFabSim inputs and original result files are not modified.",
    ),
    "kpi_completed": ("완료 lot", "Completed lots"),
    "kpi_lot_groups": ("lot 그룹 {}개", "{} lot groups"),
    "kpi_daily_throughput": ("일평균 처리량", "Average daily throughput"),
    "throughput_suffix": (" lot/일", " lots/day"),
    "kpi_simulation_days": ("시뮬레이션 {}일", "{} simulated days"),
    "kpi_weighted_cycle": ("가중 평균 Cycle Time", "Weighted average cycle time"),
    "kpi_weighted_cycle_caption": ("완료 lot 수 가중 평균", "Weighted by completed lots"),
    "kpi_on_time": ("정시 완료율", "On-time completion rate"),
    "kpi_on_time_caption": ("정시 {} / 지연 {}", "On time {} / late {}"),
    "kpi_tool_groups": ("Tool Group", "Tool Groups"),
    "kpi_tool_groups_caption": ("최종 집계 설비 그룹 수", "Aggregated equipment groups"),
    "other_group": ("기타 그룹", "Other group"),
    "no_result_file": ("결과 JSON을 선택해 주세요.", "Select a result JSON."),
    "no_equipment_limit": ("표시 개수", "Number to display"),
    "top_tool_groups": ("상위 Tool Group 수: {}", "Top Tool Groups: {}"),
    "no_result_metadata": ("결과 메타데이터 없음", "No run metadata"),
    "meta_dataset": ("Dataset", "Dataset"),
    "meta_dispatcher": ("Dispatcher", "Dispatcher"),
    "meta_seed": ("Seed", "Seed"),
    "meta_period": ("기간", "Period"),
    "meta_json": ("JSON", "JSON"),
    "meta_runtime": ("실행시간", "Runtime"),
    "days_suffix": ("일", " days"),
    "load_no_file": ("JSON 결과 파일을 찾지 못했습니다. 결과 폴더: {}", "No JSON result file found. Results folder: {}"),
    "load_uploaded": ("업로드 · {}", "Uploaded · {}"),
    "load_success": ("{} 로드 완료", "{} loaded"),
    "load_success_notes": ("{} 로드 완료 · 확인할 참고 항목 {}개", "{} loaded · {} note(s) to review"),
    "load_error": ("결과를 불러오지 못했습니다: {}", "Could not load result: {}"),
    "default_notes_ok": ("현재 결과에서 별도 데이터 주의 항목이 없습니다.", "No additional data notes for this result."),
    "days_unknown_note": ("실행 기간을 확인하지 못해 일평균 처리량은 미상입니다.", "Simulation duration is unknown, so daily throughput cannot be calculated."),
    "empty_priority": ("선택한 유형에 표시할 lot 그룹이 없습니다.", "No lot groups for the selected priority."),
    "empty_metric": ("선택한 지표에 값이 없습니다.", "No values for the selected metric."),
    "empty_equipment": ("표시할 결과가 없습니다.", "No results to display."),
    "empty_scatter": ("Utilization과 평균 대기시간이 모두 있는 설비가 없습니다.", "No equipment has both utilization and average waiting-time data."),
    "fig_completed_lots": ("완료 lot", "Completed lots"),
    "fig_cycle_days": ("Cycle Time (일)", "Cycle time (days)"),
    "fig_completed_lot_count": ("완료 lot 수", "Completed lots"),
    "fig_lot_group": ("lot 그룹", "Lot group"),
    "fig_mean_cycle": ("평균 Cycle Time", "Average cycle time"),
    "fig_on_time": ("정시 완료율", "On-time completion rate"),
    "fig_on_time_pct": ("정시 완료율 (%)", "On-time completion rate (%)"),
    "fig_mean_tardiness": ("평균 지연시간", "Average tardiness"),
    "fig_mean_tardiness_days": ("완료 lot 기준 평균 지연 (일)", "Average tardiness per completed lot (days)"),
    "fig_late_tardiness": ("지연 lot 평균 지연시간", "Average tardiness of late lots"),
    "fig_late_tardiness_days": ("지연 lot 평균 지연 (일)", "Average tardiness of late lots (days)"),
    "fig_waiting": ("평균 대기시간", "Average waiting time"),
    "fig_waiting_days": ("평균 대기시간 (일)", "Average waiting time (days)"),
    "fig_product": ("제품", "Product"),
    "fig_priority": ("우선순위", "Priority"),
    "fig_util_wait": ("Utilization과 평균 대기시간 (일)", "Utilization vs. average waiting time (days)"),
    "hover_selected_metric": ("선택 지표", "Selected metric"),
    "hover_availability": ("가용률", "Availability"),
    "hover_utilization": ("Utilization", "Utilization"),
    "hover_pm": ("PM", "PM"),
    "hover_breakdown": ("고장", "Breakdown"),
    "hover_setup": ("Setup", "Setup"),
    "hover_waiting": ("평균 대기", "Average waiting"),
    "figure_lot_title": ("제품별 {}", "{} by product"),
    "figure_top_equipment": ("{} 상위 {}개", "Top {}: {} groups"),
    "unavailable_dataset": ("데이터셋", "dataset"),
    "unavailable_dispatcher": ("Dispatcher", "dispatcher"),
    "note_no_log": ("같은 이름의 .log가 없어 실행 설정 일부를 확인할 수 없습니다.", "No matching .log file; some run settings are unavailable."),
    "note_no_field_log": ("{} 정보를 로그에서 찾지 못했습니다.", "Could not find {} information in the log."),
    "note_no_seed": ("JSON에는 seed가 없어 실행 요약 파일이 없으면 seed는 미상으로 표시됩니다.", "The JSON has no seed; without a run summary, the seed is shown as unknown."),
    "note_invalid_lot_group": ("lot 그룹 {}: 결과가 객체가 아니어서 제외했습니다.", "Lot group {} was skipped because its result is not an object."),
    "note_invalid_lot_fields": ("lot 그룹 {}: 값이 없거나 숫자가 아닌 필드({})가 있습니다.", "Lot group {} has missing or non-numeric fields: {}."),
    "note_invalid_tool_group": ("Tool Group {}: 결과가 객체가 아니어서 제외했습니다.", "Tool Group {} was skipped because its result is not an object."),
    "note_invalid_tool_fields": ("Tool Group {}: 값이 없거나 숫자가 아닌 필드({})가 있습니다.", "Tool Group {} has missing or non-numeric fields: {}."),
    "note_no_valid_lots": ("유효한 lot 그룹 데이터가 없습니다.", "No valid lot group data."),
    "note_no_valid_tools": ("유효한 Tool Group 데이터가 없습니다.", "No valid Tool Group data."),
    "note_upload_sidecars": (
        "업로드한 JSON만 읽었습니다. 같은 이름의 .log·요약 파일은 업로드되지 않아 실행 설정이 미상일 수 있습니다.",
        "Only the uploaded JSON was read. Without matching .log and summary files, some run settings may be unknown.",
    ),
    "note_overutil": (
        "Utilization이 100%를 넘는 Tool Group {}개: {}. 병목으로 단정하기 전에 지표 산식을 확인하세요.",
        "{} Tool Group(s) exceed 100% utilization: {}. Review the metric definition before treating them as bottlenecks.",
    ),
    "error_json_extension": ("PySCFabSim 결과 JSON 파일을 선택해 주세요.", "Select a PySCFabSim result JSON file."),
    "error_upload_content": ("업로드 파일 내용을 읽지 못했습니다.", "Could not read the uploaded file."),
    "error_upload_encoding": ("지원하지 않는 업로드 인코딩입니다.", "Unsupported upload encoding."),
    "error_upload_size": ("JSON 파일은 3 MB 이하만 업로드할 수 있습니다.", "JSON files must be 3 MB or smaller."),
    "error_top_level": ("JSON 최상위 값은 객체여야 합니다.", "The top-level JSON value must be an object."),
    "error_missing_keys": ("필수 키가 없습니다: {}", "Required keys are missing: {}"),
    "error_lots_machines_types": ("lots와 machines는 JSON 객체여야 합니다.", "lots and machines must be JSON objects."),
    "error_select_folder_json": ("결과 폴더 안의 JSON 파일을 선택해 주세요.", "Select a JSON file from the results folder."),
    "error_outside_folder": ("선택한 파일이 결과 폴더 밖에 있습니다.", "The selected file is outside the results folder."),
    "error_file_missing": ("결과 파일을 찾을 수 없습니다: {}", "Result file not found: {}"),
    "error_json_read": ("JSON을 읽을 수 없습니다: {}", "Could not read JSON: {}"),
    "error_uploaded_json_read": ("JSON 업로드를 읽을 수 없습니다: {}", "Could not read uploaded JSON: {}"),
}


def t(language: str | None, key: str, *values: object) -> str:
    """Return a translated string, defaulting to Korean."""
    index = 1 if language == "en" else 0
    template = TEXT[key][index]
    return template.format(*values) if values else template


def translate_note(note: str, language: str | None) -> str:
    """Translate known result-loader and KPI notes while preserving data values."""
    if language != "en":
        return note

    exact = {
        TEXT[key][0]: TEXT[key][1]
        for key in ("note_no_log", "note_no_seed", "note_no_valid_lots", "note_no_valid_tools", "note_upload_sidecars")
    }
    if note in exact:
        return exact[note]

    match = re.fullmatch(r"(.+?) 정보를 로그에서 찾지 못했습니다\.", note)
    if match:
        field = {"dataset": "dataset", "dispatcher": "dispatcher"}.get(match.group(1), match.group(1))
        return t(language, "note_no_field_log", field)

    patterns = (
        (r"lot 그룹 (.+?): 결과가 객체가 아니어서 제외했습니다\.", "note_invalid_lot_group"),
        (r"lot 그룹 (.+?): 값이 없거나 숫자가 아닌 필드\((.+)\)가 있습니다\.", "note_invalid_lot_fields"),
        (r"Tool Group (.+?): 결과가 객체가 아니어서 제외했습니다\.", "note_invalid_tool_group"),
        (r"Tool Group (.+?): 값이 없거나 숫자가 아닌 필드\((.+)\)가 있습니다\.", "note_invalid_tool_fields"),
        (r"Utilization이 100%를 넘는 Tool Group (\d+)개: (.+)\. 병목으로 단정하기 전에 지표 산식을 확인하세요\.", "note_overutil"),
    )
    for pattern, key in patterns:
        match = re.fullmatch(pattern, note)
        if match:
            return t(language, key, *match.groups())
    return note


def translate_error(message: str, language: str | None) -> str:
    """Translate loader validation errors while retaining technical details."""
    if language != "en":
        return message

    exact = {
        TEXT[key][0]: TEXT[key][1]
        for key in (
            "error_json_extension",
            "error_upload_content",
            "error_upload_encoding",
            "error_upload_size",
            "error_top_level",
            "error_lots_machines_types",
            "error_select_folder_json",
            "error_outside_folder",
        )
    }
    if message in exact:
        return exact[message]

    patterns = (
        (r"필수 키가 없습니다: (.+)", "error_missing_keys"),
        (r"결과 파일을 찾을 수 없습니다: (.+)", "error_file_missing"),
        (r"JSON을 읽을 수 없습니다: (.+)", "error_json_read"),
        (r"JSON 업로드를 읽을 수 없습니다: (.+)", "error_uploaded_json_read"),
    )
    for pattern, key in patterns:
        match = re.fullmatch(pattern, message)
        if match:
            return t(language, key, *match.groups())
    return message
