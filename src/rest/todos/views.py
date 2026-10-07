"""HTTP layer: turn requests into service calls and results into responses.

Views hold no business logic and never touch MongoDB. Errors raised by the
service are converted to JSON responses by ``exception_handler.py``.
"""
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from .dependencies import get_todo_service


class TodoAPIView(APIView):
    # Overridable through as_view(service_factory=...), which is how tests
    # inject a fake service without touching MongoDB.
    service_factory = staticmethod(get_todo_service)

    @property
    def service(self):
        return self.service_factory()


class TodoListView(TodoAPIView):
    """/todos/  GET: list all todos.  POST: create a todo."""

    def get(self, request):
        todos = self.service.list_todos()
        return Response([todo.to_dict() for todo in todos])

    def post(self, request):
        todo = self.service.create_todo(request.data)
        return Response(todo.to_dict(), status=status.HTTP_201_CREATED)


class TodoDetailView(TodoAPIView):
    """/todos/<id>/  PATCH: update a todo.  DELETE: remove it."""

    def patch(self, request, todo_id):
        todo = self.service.update_todo(todo_id, request.data)
        return Response(todo.to_dict())

    def delete(self, request, todo_id):
        self.service.delete_todo(todo_id)
        return Response(status=status.HTTP_204_NO_CONTENT)
