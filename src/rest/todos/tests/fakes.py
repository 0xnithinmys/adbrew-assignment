"""Test doubles. Because the service depends on the TodoRepository interface,
tests can swap in this in-memory version and run without MongoDB."""
import itertools
from dataclasses import replace
from datetime import datetime, timedelta, timezone

from todos.domain import Todo
from todos.repository import TodoRepository


class InMemoryTodoRepository(TodoRepository):

    def __init__(self):
        self._todos = {}
        self._ids = itertools.count(1)
        self._clock = datetime(2024, 1, 1, tzinfo=timezone.utc)

    def list_all(self):
        return sorted(self._todos.values(), key=lambda todo: todo.created_at, reverse=True)

    def create(self, description):
        self._clock += timedelta(seconds=1)
        todo = Todo(id=str(next(self._ids)), description=description, completed=False, created_at=self._clock)
        self._todos[todo.id] = todo
        return todo

    def update(self, todo_id, changes):
        if todo_id not in self._todos:
            return None
        self._todos[todo_id] = replace(self._todos[todo_id], **changes)
        return self._todos[todo_id]

    def delete(self, todo_id):
        return self._todos.pop(todo_id, None) is not None
