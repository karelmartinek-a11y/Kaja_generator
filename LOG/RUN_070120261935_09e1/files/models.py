from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from typing import Any, Dict, Optional


ISO_FORMAT = "%Y-%m-%d"


class Status(str, Enum):
    TODO = "todo"
    IN_PROGRESS = "in-progress"
    DONE = "done"


class Priority(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"


@dataclass
class Task:
    id: int
    title: str
    description: str
    due: Optional[datetime]
    priority: Priority
    status: Status
    created_at: datetime
    updated_at: datetime

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "title": self.title,
            "description": self.description,
            "due": self.due.strftime(ISO_FORMAT) if self.due else None,
            "priority": self.priority.value,
            "status": self.status.value,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
        }

    @staticmethod
    def from_dict(data: Dict[str, Any]) -> "Task":
        due_raw = data.get("due")
        due = datetime.strptime(due_raw, ISO_FORMAT) if due_raw else None

        return Task(
            id=int(data["id"]),
            title=str(data["title"]),
            description=str(data.get("description", "")),
            due=due,
            priority=Priority(str(data.get("priority", Priority.MEDIUM.value))),
            status=Status(str(data.get("status", Status.TODO.value))),
            created_at=_parse_datetime(data.get("created_at")),
            updated_at=_parse_datetime(data.get("updated_at")),
        )


def _parse_datetime(value: Any) -> datetime:
    if isinstance(value, datetime):
        return value
    if not value:
        return datetime.utcnow()
    return datetime.fromisoformat(str(value))
