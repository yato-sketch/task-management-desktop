from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import List, Optional
import uuid


class TaskStatus(Enum):
    PENDING = "pending"
    COMPLETED = "completed"


@dataclass
class Task:
    id: str
    title: str
    description: Optional[str] = None
    due_date: Optional[datetime] = None
    tags: List[str] = field(default_factory=list)
    status: TaskStatus = TaskStatus.PENDING
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "title": self.title,
            "description": self.description,
            "due_date": self.due_date.isoformat() if self.due_date else None,
            "tags": self.tags,
            "status": self.status.value,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat()
        }

    @classmethod
    def from_dict(cls, data: dict) -> 'Task':
        return cls(
            id=data["id"],
            title=data["title"],
            description=data.get("description"),
            due_date=datetime.fromisoformat(data["due_date"]) if data.get("due_date") else None,
            tags=data.get("tags", []),
            status=TaskStatus(data["status"]),
            created_at=datetime.fromisoformat(data["created_at"]),
            updated_at=datetime.fromisoformat(data["updated_at"])
        )

    @classmethod
    def create_new(cls, title: str, description: str = None, due_date: str = None, tags: List[str] = None) -> 'Task':
        task_id = str(uuid.uuid4())
        now = datetime.now()
        
        return cls(
            id=task_id,
            title=title.strip(),
            description=description.strip() if description else None,
            due_date=datetime.fromisoformat(due_date) if due_date else None,
            tags=[tag.strip() for tag in (tags or [])],
            status=TaskStatus.PENDING,
            created_at=now,
            updated_at=now
        )


@dataclass
class TaskFilter:
    status: Optional[TaskStatus] = None
    tags: Optional[List[str]] = None
    search: Optional[str] = None


@dataclass
class TaskSort:
    field: str = "created_at"
    direction: str = "desc"


@dataclass
class ListTasksOptions:
    filter: Optional[TaskFilter] = None
    sort: Optional[TaskSort] = None
    limit: Optional[int] = None
