import json
import os
from datetime import datetime, date
from typing import Any, List, Optional

ISO_FMT = "%Y-%m-%d"


def parse_date(value: str) -> date:
    try:
        return datetime.strptime(value, ISO_FMT).date()
    except ValueError as exc:
        raise ValueError(f"Neplatný formát data, očekává se YYYY-MM-DD: {value}") from exc


def format_date(value: date) -> str:
    return value.strftime(ISO_FMT)


def iso_now() -> str:
    return datetime.utcnow().isoformat(timespec="seconds")


def validate_priority(value: str) -> str:
    allowed = {"low", "medium", "high"}
    if value not in allowed:
        raise ValueError(f"Neznámá priorita '{value}'. Povolené hodnoty: {sorted(allowed)}")
    return value


def validate_status(value: str) -> str:
    allowed = {"todo", "in-progress", "done"}
    if value not in allowed:
        raise ValueError(f"Neznámý stav '{value}'. Povolené hodnoty: {sorted(allowed)}")
    return value


def ensure_storage_file(path: str) -> None:
    if not os.path.exists(path):
        with open(path, "w", encoding="utf-8") as handle:
            json.dump({"tasks": [], "last_id": 0}, handle, ensure_ascii=False, indent=2)


def load_json(path: str) -> dict:
    ensure_storage_file(path)
    try:
        with open(path, "r", encoding="utf-8") as handle:
            return json.load(handle)
    except json.JSONDecodeError as exc:
        raise ValueError(f"Soubor s úložištěm je poškozen: {path}") from exc


def save_json(path: str, data: dict) -> None:
    tmp_path = f"{path}.tmp"
    with open(tmp_path, "w", encoding="utf-8") as handle:
        json.dump(data, handle, ensure_ascii=False, indent=2)
    os.replace(tmp_path, path)


def filter_by_status(tasks: List[dict], status: Optional[str]) -> List[dict]:
    if not status:
        return tasks
    validate_status(status)
    return [task for task in tasks if task.get("status") == status]


def filter_by_priority(tasks: List[dict], priority: Optional[str]) -> List[dict]:
    if not priority:
        return tasks
    validate_priority(priority)
    return [task for task in tasks if task.get("priority") == priority]


def filter_by_due_before(tasks: List[dict], before: Optional[date]) -> List[dict]:
    if before is None:
        return tasks
    result = []
    for task in tasks:
        due_str = task.get("due")
        if not due_str:
            continue
        try:
            due_date = parse_date(due_str)
        except ValueError:
            continue
        if due_date <= before:
            result.append(task)
    return result


def sort_tasks(tasks: List[dict]) -> List[dict]:
    def sort_key(task: dict) -> Any:
        status_weight = {"todo": 0, "in-progress": 1, "done": 2}.get(task.get("status"), 3)
        priority_weight = {"high": 0, "medium": 1, "low": 2}.get(task.get("priority"), 3)
        due_str = task.get("due")
        due_val = None
        if due_str:
            try:
                due_val = parse_date(due_str)
            except ValueError:
                due_val = None
        return (status_weight, priority_weight, due_val or date.max)

    return sorted(tasks, key=sort_key)
