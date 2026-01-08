import json
import os
from typing import List, Optional

from models import Task


class TaskRepository:
    def __init__(self, file_path: str = "tasks.json") -> None:
        self.file_path = file_path
        self._ensure_storage()

    def _ensure_storage(self) -> None:
        if not os.path.exists(self.file_path):
            self._write_raw([])

    def _read_raw(self) -> List[dict]:
        try:
            with open(self.file_path, "r", encoding="utf-8") as f:
                data = json.load(f)
                if not isinstance(data, list):
                    raise ValueError("Storage format invalid: expected list")
                return data
        except FileNotFoundError:
            self._write_raw([])
            return []
        except json.JSONDecodeError as exc:
            raise ValueError(
                f"Storage file '{self.file_path}' is corrupted. Remove or fix the file to continue."
            ) from exc

    def _write_raw(self, data: List[dict]) -> None:
        with open(self.file_path, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)

    def load_all(self) -> List[Task]:
        records = self._read_raw()
        tasks: List[Task] = []
        for record in records:
            try:
                tasks.append(Task.from_dict(record))
            except Exception as exc:  # noqa: BLE001
                raise ValueError(f"Invalid task data in storage: {record}") from exc
        return tasks

    def get_by_id(self, task_id: int) -> Optional[Task]:
        for task in self.load_all():
            if task.id == task_id:
                return task
        return None

    def save_all(self, tasks: List[Task]) -> None:
        payload = [task.to_dict() for task in tasks]
        self._write_raw(payload)

    def _next_id(self, tasks: List[Task]) -> int:
        if not tasks:
            return 1
        return max(task.id for task in tasks if task.id is not None) + 1

    def add(self, task: Task) -> Task:
        tasks = self.load_all()
        task.id = self._next_id(tasks)
        tasks.append(task)
        self.save_all(tasks)
        return task

    def update(self, updated_task: Task) -> Task:
        tasks = self.load_all()
        found = False
        for idx, task in enumerate(tasks):
            if task.id == updated_task.id:
                tasks[idx] = updated_task
                found = True
                break
        if not found:
            raise ValueError(f"Task with id {updated_task.id} not found.")
        self.save_all(tasks)
        return updated_task

    def delete(self, task_id: int) -> None:
        tasks = self.load_all()
        new_tasks = [task for task in tasks if task.id != task_id]
        if len(new_tasks) == len(tasks):
            raise ValueError(f"Task with id {task_id} not found.")
        self.save_all(new_tasks)

    def replace_all(self, tasks: List[Task]) -> None:
        self.save_all(tasks)
