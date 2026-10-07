"""Todo use cases (Service layer).

The service holds the business rules: validate input, call the repository,
and turn "nothing there" into TodoNotFoundError. It knows nothing about HTTP
or MongoDB, and receives its repository from outside (dependency injection).
"""
import logging
from typing import List

from .domain import Todo
from .exceptions import TodoNotFoundError
from .repository import TodoRepository
from .validators import validate_new_todo, validate_todo_update

logger = logging.getLogger(__name__)


class TodoService:

    def __init__(self, repository: TodoRepository):
        self._repository = repository

    def list_todos(self) -> List[Todo]:
        return self._repository.list_all()

    def create_todo(self, payload) -> Todo:
        description = validate_new_todo(payload)
        todo = self._repository.create(description)
        logger.info("Created todo %s", todo.id)
        return todo

    def update_todo(self, todo_id: str, payload) -> Todo:
        changes = validate_todo_update(payload)
        todo = self._repository.update(todo_id, changes)
        if todo is None:
            raise TodoNotFoundError(todo_id)
        logger.info("Updated todo %s: %s", todo_id, sorted(changes))
        return todo

    def delete_todo(self, todo_id: str) -> None:
        if not self._repository.delete(todo_id):
            raise TodoNotFoundError(todo_id)
        logger.info("Deleted todo %s", todo_id)
