"""HTTP-level tests: status codes and JSON shapes, with a fake repository injected."""
from unittest import TestCase, mock

from rest_framework.test import APIRequestFactory

from todos.exceptions import StorageError
from todos.services import TodoService
from todos.views import TodoDetailView, TodoListView

from .fakes import InMemoryTodoRepository


class TodoViewTests(TestCase):

    def setUp(self):
        self.factory = APIRequestFactory()
        self.service = TodoService(InMemoryTodoRepository())
        self.list_view = TodoListView.as_view(service_factory=lambda: self.service)
        self.detail_view = TodoDetailView.as_view(service_factory=lambda: self.service)

    def post(self, data):
        return self.list_view(self.factory.post("/todos/", data, format="json"))

    def test_get_returns_empty_list(self):
        response = self.list_view(self.factory.get("/todos/"))

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data, [])

    def test_post_creates_todo_and_get_returns_it(self):
        created = self.post({"description": "Learn Docker"})
        listed = self.list_view(self.factory.get("/todos/"))

        self.assertEqual(created.status_code, 201)
        self.assertEqual(created.data["description"], "Learn Docker")
        self.assertFalse(created.data["completed"])
        self.assertEqual(listed.data, [created.data])

    def test_post_with_invalid_body_returns_400_error_shape(self):
        response = self.post({"description": "   "})

        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.data["error"]["code"], "validation_error")
        self.assertEqual(response.data["error"]["details"], {"field": "description"})

    def test_malformed_json_returns_400_error_shape(self):
        request = self.factory.post("/todos/", "{not json", content_type="application/json")

        response = self.list_view(request)

        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.data["error"]["code"], "parse_error")

    def test_patch_updates_todo(self):
        todo_id = self.post({"description": "Learn React"}).data["id"]
        request = self.factory.patch(f"/todos/{todo_id}/", {"completed": True}, format="json")

        response = self.detail_view(request, todo_id=todo_id)

        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.data["completed"])

    def test_delete_returns_204_then_404(self):
        todo_id = self.post({"description": "Temporary"}).data["id"]

        first = self.detail_view(self.factory.delete(f"/todos/{todo_id}/"), todo_id=todo_id)
        second = self.detail_view(self.factory.delete(f"/todos/{todo_id}/"), todo_id=todo_id)

        self.assertEqual(first.status_code, 204)
        self.assertEqual(second.status_code, 404)
        self.assertEqual(second.data["error"]["code"], "not_found")

    def test_database_failure_returns_503(self):
        with mock.patch.object(self.service, "list_todos", side_effect=StorageError("down")):
            response = self.list_view(self.factory.get("/todos/"))

        self.assertEqual(response.status_code, 503)
        self.assertEqual(response.data["error"]["code"], "storage_unavailable")

    def test_unexpected_error_returns_generic_500(self):
        with mock.patch.object(self.service, "list_todos", side_effect=RuntimeError("secret detail")), \
                self.assertLogs("todos", level="ERROR"):
            response = self.list_view(self.factory.get("/todos/"))

        self.assertEqual(response.status_code, 500)
        self.assertEqual(response.data["error"]["code"], "internal_error")
        self.assertNotIn("secret detail", response.data["error"]["message"])
