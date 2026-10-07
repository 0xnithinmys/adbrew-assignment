"""Errors raised by the todo feature.

They describe *what* went wrong in domain terms. Translating them into HTTP
status codes is the job of ``exception_handler.py``, so the business layer
never needs to know about HTTP.
"""


class TodoError(Exception):
    """Base class for every error raised by the todos package."""

    code = "todo_error"

    def __init__(self, message: str, details: dict = None):
        super().__init__(message)
        self.message = message
        self.details = details or {}


class TodoValidationError(TodoError):
    """The client sent data that breaks a business rule."""

    code = "validation_error"


class TodoNotFoundError(TodoError):
    """No todo exists with the requested id."""

    code = "not_found"

    def __init__(self, todo_id: str):
        super().__init__(f"Todo '{todo_id}' was not found.", {"id": todo_id})


class StorageError(TodoError):
    """The database could not complete the operation."""

    code = "storage_unavailable"
