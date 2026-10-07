from unittest import TestCase

from todos.exceptions import TodoNotFoundError, TodoValidationError
from todos.services import TodoService

from .fakes import InMemoryTodoRepository


class TodoServiceTests(TestCase):

    def setUp(self):
        self.service = TodoService(InMemoryTodoRepository())

    def test_create_then_list_returns_newest_first(self):
        self.service.create_todo({"description": "First"})
        self.service.create_todo({"description": "Second"})

        descriptions = [todo.description for todo in self.service.list_todos()]

        self.assertEqual(descriptions, ["Second", "First"])

    def test_new_todo_is_not_completed(self):
        todo = self.service.create_todo({"description": "Learn Mongo"})
        self.assertFalse(todo.completed)

    def test_invalid_todo_is_not_saved(self):
        with self.assertRaises(TodoValidationError):
            self.service.create_todo({"description": ""})
        self.assertEqual(self.service.list_todos(), [])

    def test_update_marks_todo_completed(self):
        todo = self.service.create_todo({"description": "Learn React"})

        updated = self.service.update_todo(todo.id, {"completed": True})

        self.assertTrue(updated.completed)
        self.assertEqual(updated.description, "Learn React")

    def test_update_unknown_todo_raises_not_found(self):
        with self.assertRaises(TodoNotFoundError):
            self.service.update_todo("missing", {"completed": True})

    def test_delete_removes_todo(self):
        todo = self.service.create_todo({"description": "Temporary"})

        self.service.delete_todo(todo.id)

        self.assertEqual(self.service.list_todos(), [])

    def test_delete_unknown_todo_raises_not_found(self):
        with self.assertRaises(TodoNotFoundError):
            self.service.delete_todo("missing")
