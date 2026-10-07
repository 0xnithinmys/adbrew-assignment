"""Persistence for todos (Repository pattern).

``TodoRepository`` is the contract the rest of the app depends on.
``MongoTodoRepository`` is the only code that knows todos live in MongoDB,
so swapping the database, or using an in-memory fake in tests, touches
nothing else.
"""
import logging
from abc import ABC, abstractmethod
from contextlib import contextmanager
from datetime import datetime, timezone
from typing import List, Optional

from bson import ObjectId
from bson.errors import InvalidId
from pymongo import DESCENDING, ReturnDocument
from pymongo.errors import PyMongoError

from .domain import Todo
from .exceptions import StorageError

logger = logging.getLogger(__name__)


class TodoRepository(ABC):
    """Storage contract for todos."""

    @abstractmethod
    def list_all(self) -> List[Todo]:
        """Return every todo, newest first."""

    @abstractmethod
    def create(self, description: str) -> Todo:
        """Persist a new, not yet completed todo and return it."""

    @abstractmethod
    def update(self, todo_id: str, changes: dict) -> Optional[Todo]:
        """Apply ``changes`` and return the updated todo, or None if it does not exist."""

    @abstractmethod
    def delete(self, todo_id: str) -> bool:
        """Delete the todo. Return False if it did not exist."""


class MongoTodoRepository(TodoRepository):
    """TodoRepository backed by a MongoDB collection."""

    def __init__(self, collection):
        self._collection = collection

    def list_all(self) -> List[Todo]:
        with _storage_errors("list todos"):
            documents = self._collection.find().sort("created_at", DESCENDING)
            return [_to_todo(document) for document in documents]

    def create(self, description: str) -> Todo:
        document = {
            "description": description,
            "completed": False,
            "created_at": _utc_now(),
        }
        with _storage_errors("create a todo"):
            result = self._collection.insert_one(document)
        return _to_todo({**document, "_id": result.inserted_id})

    def update(self, todo_id: str, changes: dict) -> Optional[Todo]:
        object_id = _parse_object_id(todo_id)
        if object_id is None:
            return None
        with _storage_errors("update a todo"):
            document = self._collection.find_one_and_update(
                {"_id": object_id},
                {"$set": changes},
                return_document=ReturnDocument.AFTER,
            )
        return _to_todo(document) if document else None

    def delete(self, todo_id: str) -> bool:
        object_id = _parse_object_id(todo_id)
        if object_id is None:
            return False
        with _storage_errors("delete a todo"):
            result = self._collection.delete_one({"_id": object_id})
        return result.deleted_count == 1


@contextmanager
def _storage_errors(action: str):
    """Translate driver errors into StorageError so callers never see pymongo types."""
    try:
        yield
    except PyMongoError as exc:
        logger.exception("MongoDB failed to %s", action)
        raise StorageError("The todo database is unavailable. Please try again shortly.") from exc


def _parse_object_id(todo_id: str) -> Optional[ObjectId]:
    """Ids come from the URL as strings; anything that is not a valid ObjectId cannot exist."""
    try:
        return ObjectId(todo_id)
    except (InvalidId, TypeError):
        return None


def _to_todo(document: dict) -> Todo:
    """Map a MongoDB document to the domain model (ObjectId -> str)."""
    return Todo(
        id=str(document["_id"]),
        description=document["description"],
        completed=document.get("completed", False),
        created_at=document["created_at"],
    )


def _utc_now() -> datetime:
    """Current UTC time truncated to milliseconds, the precision MongoDB stores."""
    now = datetime.now(timezone.utc)
    return now.replace(microsecond=now.microsecond // 1000 * 1000)
