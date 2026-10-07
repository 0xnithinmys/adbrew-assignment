from unittest import TestCase

from todos.exceptions import TodoValidationError
from todos.validators import MAX_DESCRIPTION_LENGTH, validate_new_todo, validate_todo_update


class ValidateNewTodoTests(TestCase):

    def test_returns_trimmed_description(self):
        self.assertEqual(validate_new_todo({"description": "  Learn Docker  "}), "Learn Docker")

    def test_accepts_description_at_max_length(self):
        description = "x" * MAX_DESCRIPTION_LENGTH
        self.assertEqual(validate_new_todo({"description": description}), description)

    def test_rejects_invalid_payloads(self):
        invalid_payloads = [
            None,
            ["description"],
            {},
            {"description": None},
            {"description": 42},
            {"description": "   "},
            {"description": "x" * (MAX_DESCRIPTION_LENGTH + 1)},
        ]
        for payload in invalid_payloads:
            with self.subTest(payload=payload), self.assertRaises(TodoValidationError):
                validate_new_todo(payload)


class ValidateTodoUpdateTests(TestCase):

    def test_returns_only_given_fields(self):
        self.assertEqual(validate_todo_update({"completed": True}), {"completed": True})

    def test_cleans_description(self):
        self.assertEqual(
            validate_todo_update({"description": " New text ", "completed": False}),
            {"description": "New text", "completed": False},
        )

    def test_rejects_invalid_payloads(self):
        invalid_payloads = [
            {},
            {"completed": "yes"},
            {"completed": 1},
            {"description": ""},
            {"_id": "abc"},
            {"completed": True, "owner": "me"},
        ]
        for payload in invalid_payloads:
            with self.subTest(payload=payload), self.assertRaises(TodoValidationError):
                validate_todo_update(payload)
