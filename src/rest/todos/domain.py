"""Domain model for a todo item, independent of storage and HTTP."""
from dataclasses import dataclass
from datetime import datetime


@dataclass(frozen=True)
class Todo:
    id: str
    description: str
    completed: bool
    created_at: datetime

    def to_dict(self) -> dict:
        """JSON-ready representation used by the API."""
        return {
            "id": self.id,
            "description": self.description,
            "completed": self.completed,
            "created_at": self.created_at.isoformat(),
        }
