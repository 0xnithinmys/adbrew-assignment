"""Integration tests against the real Mongo container, in a throwaway database.

Skipped automatically when MongoDB is not reachable.
"""
from unittest import SkipTest, TestCase

from django.conf import settings
from pymongo import MongoClient
from pymongo.errors import PyMongoError

from todos.repository import MongoTodoRepository

TEST_DB_NAME = "test_db_integration"


class MongoTodoRepositoryTests(TestCase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.client = MongoClient(
            host=settings.MONGO_HOST,
            port=settings.MONGO_PORT,
            serverSelectionTimeoutMS=1000,
            tz_aware=True,
        )
        try:
            cls.client.admin.command("ping")
        except PyMongoError:
            cls.client.close()
            raise SkipTest("MongoDB is not reachable")

    @classmethod
    def tearDownClass(cls):
        cls.client.drop_database(TEST_DB_NAME)
        cls.client.close()
        super().tearDownClass()

    def setUp(self):
        collection = self.client[TEST_DB_NAME]["todos"]
        collection.delete_many({})
        self.repository = MongoTodoRepository(collection)

    def test_create_and_list_round_trip(self):
        created = self.repository.create("Learn Mongo")

        self.assertEqual(self.repository.list_all(), [created])

    def test_update_and_delete(self):
        todo = self.repository.create("Learn Django")

        updated = self.repository.update(todo.id, {"completed": True})

        self.assertTrue(updated.completed)
        self.assertTrue(self.repository.delete(todo.id))
        self.assertFalse(self.repository.delete(todo.id))

    def test_unknown_or_malformed_ids_are_not_found(self):
        for todo_id in ("not-an-object-id", "0" * 24):
            with self.subTest(todo_id=todo_id):
                self.assertIsNone(self.repository.update(todo_id, {"completed": True}))
                self.assertFalse(self.repository.delete(todo_id))
