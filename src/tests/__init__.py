"""Unit test for small methods in app."""
import os
from unittest import TestCase

from src import wrapper


class TestApp(TestCase):
    """Unit test class to test small methods in app."""

    def setUp(self):
        self.key = 'key'

    def tearDown(self):
        if os.getenv(self.key):
            del os.environ[self.key]

    def test_valid_env(self):
        os.environ[self.key] = 'test'
        self.assertIsNotNone(wrapper.get_or_raise(self.key))

    def test_empty_env(self):
        with self.assertRaises(RuntimeError):
            wrapper.get_or_raise(self.key)

    def test_str_to_bool(self):
        self.assertEqual(True, wrapper.convert_str_to_bool('TRUE'))
        self.assertEqual(True, wrapper.convert_str_to_bool('tRuE'))
        self.assertEqual(False, wrapper.convert_str_to_bool(1))
