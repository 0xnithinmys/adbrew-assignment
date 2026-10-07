"""Input validation for todo payloads.

Each function takes the raw request body and returns clean values, or raises
TodoValidationError with a message that is safe to show to the user.
"""
from .exceptions import TodoValidationError

MAX_DESCRIPTION_LENGTH = 200
UPDATABLE_FIELDS = ("description", "completed")


def validate_new_todo(payload) -> str:
    """Return the cleaned description for a todo that is about to be created."""
    _require_object(payload)
    if "description" not in payload:
        raise TodoValidationError("'description' is required.", {"field": "description"})
    return _clean_description(payload["description"])


def validate_todo_update(payload) -> dict:
    """Return the cleaned subset of fields that may be changed on a todo."""
    _require_object(payload)

    unknown_fields = sorted(set(payload) - set(UPDATABLE_FIELDS))
    if unknown_fields:
        raise TodoValidationError(
            f"Unknown field(s): {', '.join(unknown_fields)}.",
            {"fields": unknown_fields},
        )
    if not payload:
        raise TodoValidationError(f"Provide at least one of: {', '.join(UPDATABLE_FIELDS)}.")

    changes = {}
    if "description" in payload:
        changes["description"] = _clean_description(payload["description"])
    if "completed" in payload:
        if not isinstance(payload["completed"], bool):
            raise TodoValidationError("'completed' must be true or false.", {"field": "completed"})
        changes["completed"] = payload["completed"]
    return changes


def _require_object(payload) -> None:
    if not isinstance(payload, dict):
        raise TodoValidationError("Request body must be a JSON object.")


def _clean_description(value) -> str:
    if not isinstance(value, str):
        raise TodoValidationError("'description' must be text.", {"field": "description"})

    description = value.strip()
    if not description:
        raise TodoValidationError("'description' must not be empty.", {"field": "description"})
    if len(description) > MAX_DESCRIPTION_LENGTH:
        raise TodoValidationError(
            f"'description' must be at most {MAX_DESCRIPTION_LENGTH} characters.",
            {"field": "description", "max_length": MAX_DESCRIPTION_LENGTH},
        )
    return description
