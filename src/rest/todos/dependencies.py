"""Composition root: the one place where concrete classes are wired together."""
from functools import lru_cache

from django.conf import settings
from pymongo import MongoClient

from .repository import MongoTodoRepository
from .services import TodoService

COLLECTION_NAME = "todos"


@lru_cache(maxsize=None)
def get_todo_service() -> TodoService:
    """Build the service once per process and reuse it.

    MongoClient is thread-safe and keeps its own connection pool, so one
    shared instance is the recommended usage. It connects lazily, on the
    first query.
    """
    client = MongoClient(
        host=settings.MONGO_HOST,
        port=settings.MONGO_PORT,
        serverSelectionTimeoutMS=settings.MONGO_TIMEOUT_MS,
        tz_aware=True,
    )
    collection = client[settings.MONGO_DB_NAME][COLLECTION_NAME]
    return TodoService(MongoTodoRepository(collection))
