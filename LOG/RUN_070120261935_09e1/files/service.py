from __future__ import annotations

from datetime import datetime
from typing import List, Optional

import repository
import utils
from models import Priority, Status, Task


class ServiceError(Exception):
    """Základní výjimka pro aplikační vrstvu."""


class ValidationError(ServiceError):
    """Chyba validace vstupních dat."""


class NotFoundError(ServiceError):
    """Entita nebyla nalezena."""


class PersistenceError(ServiceError):
    """Chyba při práci s perzistencí."""


def create_task(
    title: str,
    description: str,
    due: Optional[str],
    priority: str,
) -> Task:
    """Vytvoří novou úlohu a uloží ji do perzistence."""
    normalized_title = _require_text(title, field_name="title")
    normalized_description = description.strip() if description is not None else ""
    normalized_priority = _parse_priority(priority)
    normalized_due = _normalize_due(due)
    now_iso = utils.utcnow_iso()

    tasks = _load_tasks()
    next_id = repository.get_next_id(tasks)
    task = Task(
        id=next_id,
        title=normalized_title,
        description=normalized_description,
        due=normalized_due,
        priority=normalized_priority,
        status=Status.TODO,
        created_at=now_iso,
        updated_at=now_iso,
    )
    tasks.append(task)
    _save_tasks(tasks)
    return task


def list_tasks(
    status: Optional[str] = None,
    priority: Optional[str] = None,
    before: Optional[str] = None,
) -> List[Task]:
    """Vrátí seznam úloh dle filtrů (status, priority, due před datem)."""
    tasks = _load_tasks()
    status_filter = _parse_status(status) if status else None
    priority_filter = _parse_priority(priority) if priority else None
    before_dt = _parse_due_filter(before) if before else None

    def _matches(task: Task) -> bool:
        if status_filter and task.status != status_filter:
            return False
        if priority_filter and task.priority != priority_filter:
            return False
        if before_dt:
            if task.due is None:
                return False
            try:
                task_due = utils.parse_iso_datetime(task.due)
            except ValueError:
                return False
            if task_due >= before_dt:
                return False
        return True

    return [task for task in tasks if _matches(task)]


def update_task_status(task_id: int, status: str) -> Task:
    """Aktualizuje stav úlohy."""
    numeric_id = _validate_id(task_id)
    new_status = _parse_status(status)

    tasks = _load_tasks()
    task = _find_task(tasks, numeric_id)
    if task is None:
        raise NotFoundError(f"Task with id {numeric_id} not found")

    if task.status != new_status:
        task.status = new_status
        task.updated_at = utils.utcnow_iso()
        _save_tasks(tasks)
    return task


def remove_task(task_id: int) -> None:
    """Odstraní úlohu dle identifikátoru."""
    numeric_id = _validate_id(task_id)
    tasks = _load_tasks()
    remaining = [task for task in tasks if task.id != numeric_id]

    if len(remaining) == len(tasks):
        raise NotFoundError(f"Task with id {numeric_id} not found")

    _save_tasks(remaining)


def get_task(task_id: int) -> Task:
    """Vrátí detail úlohy dle identifikátoru."""
    numeric_id = _validate_id(task_id)
    tasks = _load_tasks()
    task = _find_task(tasks, numeric_id)
    if task is None:
        raise NotFoundError(f"Task with id {numeric_id} not found")
    return task


def _find_task(tasks: List[Task], task_id: int) -> Optional[Task]:
    for task in tasks:
        if task.id == task_id:
            return task
    return None


def _load_tasks() -> List[Task]:
    try:
        return repository.load_tasks()
    except repository.RepositoryError as exc:  # type: ignore[attr-defined]
        raise PersistenceError(str(exc)) from exc


def _save_tasks(tasks: List[Task]) -> None:
    try:
        repository.save_tasks(tasks)
    except repository.RepositoryError as exc:  # type: ignore[attr-defined]
        raise PersistenceError(str(exc)) from exc


def _parse_status(value: str) -> Status:
    if value is None:
        raise ValidationError("Status is required")
    try:
        return Status.from_string(value)
    except ValueError as exc:
        raise ValidationError(f"Invalid status '{value}'. Allowed: {Status.allowed_values()}") from exc


def _parse_priority(value: str) -> Priority:
    if value is None:
        raise ValidationError("Priority is required")
    try:
        return Priority.from_string(value)
    except ValueError as exc:
        raise ValidationError(f"Invalid priority '{value}'. Allowed: {Priority.allowed_values()}") from exc


def _normalize_due(value: Optional[str]) -> Optional[str]:
    if value is None or value == "":
        return None
    try:
        parsed = utils.parse_iso_datetime(value)
    except ValueError as exc:
        raise ValidationError("Due date must be valid ISO 8601 datetime (e.g., 2024-12-31 or 2024-12-31T12:00:00)") from exc
    return utils.to_iso_datetime(parsed)


def _parse_due_filter(value: str) -> datetime:
    try:
        parsed = utils.parse_iso_datetime(value)
    except ValueError as exc:
        raise ValidationError("Filter 'before' must be valid ISO 8601 datetime") from exc
    return parsed


def _require_text(value: str, field_name: str) -> str:
    if value is None:
        raise ValidationError(f"{field_name} is required")
    cleaned = value.strip()
    if cleaned == "":
        raise ValidationError(f"{field_name} cannot be empty")
    return cleaned


def _validate_id(task_id: int) -> int:
    if not isinstance(task_id, int):
        raise ValidationError("Task id must be an integer")
    if task_id <= 0:
        raise ValidationError("Task id must be a positive integer")
    return task_id
