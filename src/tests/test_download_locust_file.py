"""Unit test for method get_locust_file."""
import os
from unittest import TestCase

import mock

from src import app


class TestGetLocustFile(TestCase):
    """Unit test class to test method get_locust_file."""

    def setUp(self):
        self.url_key = 'LOCUST_FILE_URL'

    def tearDown(self):
        if os.getenv(self.url_key):
            del os.environ[self.url_key]

    @mock.patch('boto3.resource')
    def test_valid_s3(self, boto_client):
        with mock.patch('botocore.exceptions.ClientError') as boto_core:
            boto_client.return_value.Bucket.return_value.download_file.return_value = None

            os.environ[self.url_key] = 's3://bucket/path/file.py'
            app.get_locust_file()
            self.assertFalse(boto_core.called)

    @mock.patch('wget.download')
    def test_valid_https(self, wget):
        FILE_NAME = 'file.py'
        wget.return_value = FILE_NAME
        os.environ[self.url_key] = 'https://raw.githubusercontent.com/org/repo/master/file.py'
        self.assertEqual(FILE_NAME, app.get_locust_file())

    @mock.patch('wget.download')
    def test_no_file(self, wget):
        with self.assertRaises(SystemExit) as exit_code:
            wget.return_value = None
            os.environ[self.url_key] = 'https://raw.githubusercontent.com/org/repo/master/no_file.py'
            app.get_locust_file()
        self.assertEqual(exit_code.exception.code, 1)

    @mock.patch('wget.download')
    def test_no_python_file(self, wget):
        with self.assertRaises(SystemExit) as exit_code:
            wget.return_value = 'wrong_type.json'
            os.environ[self.url_key] = 'https://raw.githubusercontent.com/org/repo/master/wrong_type.json'
            app.get_locust_file()
        self.assertEqual(exit_code.exception.code, 1)
