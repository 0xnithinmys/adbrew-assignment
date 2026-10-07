"""Single place that converts exceptions into consistent JSON error responses.

Every error the API returns has the same shape, so the frontend needs only
one error-parsing path:

    {"error": {"code": "...", "message": "...", "details": {...}}}
"""
import logging

from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import exception_handler as drf_exception_handler

from .exceptions import StorageError, TodoError, TodoNotFoundError, TodoValidationError

logger = logging.getLogger(__name__)

STATUS_BY_ERROR = (
    (TodoValidationError, status.HTTP_400_BAD_REQUEST),
    (TodoNotFoundError, status.HTTP_404_NOT_FOUND),
    (StorageError, status.HTTP_503_SERVICE_UNAVAILABLE),
)


def api_exception_handler(exc, context):
    if isinstance(exc, TodoError):
        return _error_response(_status_for(exc), exc.code, exc.message, exc.details)

    # DRF's own errors: malformed JSON, method not allowed, unsupported media type...
    response = drf_exception_handler(exc, context)
    if response is not None:
        detail = response.data.get("detail", "Request failed.") if isinstance(response.data, dict) else response.data
        response.data = _error_body(getattr(exc, "default_code", "error"), str(detail))
        return response

    # Anything else is a bug: log the traceback, but never leak it to the client.
    logger.exception("Unhandled error in %s", type(context.get("view")).__name__, exc_info=exc)
    return _error_response(
        status.HTTP_500_INTERNAL_SERVER_ERROR,
        "internal_error",
        "Something went wrong on our side. Please try again.",
    )


def _status_for(exc: TodoError) -> int:
    for error_type, http_status in STATUS_BY_ERROR:
        if isinstance(exc, error_type):
            return http_status
    return status.HTTP_500_INTERNAL_SERVER_ERROR


def _error_body(code: str, message: str, details: dict = None) -> dict:
    return {"error": {"code": code, "message": message, "details": details or {}}}


def _error_response(http_status: int, code: str, message: str, details: dict = None) -> Response:
    return Response(_error_body(code, message, details), status=http_status)
