"""Unit test for method get_locust_file."""
import os
from unittest import TestCase

import mock

from src import wrapper


class TestGetLocustFile(TestCase):
    """Unit test class to test method get_locust_file."""

    def setUp(self):
        self.file_input = 'LOCUST_FILE'
        self.s3_link = 's3://bucket/path'
        self.github_link = 'https://raw.github.com/org/repo/master'
        self.file_name = 'file.py'
        self.json_name = 'payloads.json'

    def tearDown(self):
        if os.getenv(self.file_input):
            del os.environ[self.file_input]

    @mock.patch('boto3.resource')
    def test_valid_s3_link(self, mocked_boto):
        os.environ[self.file_input] = '/'.join([self.s3_link, self.file_name])
        mocked_boto.return_value.Bucket.return_value.download_file.return_value = self.file_name
        self.assertEqual(self.file_name, wrapper.get_locust_file())

    @mock.patch('boto3.resource')
    def test_valid_multiple_s3_links(self, mocked_boto):
        lt_script = '/'.join([self.s3_link, self.file_name])
        payload = '/'.join([self.s3_link, self.json_name])
        os.environ[self.file_input] = ','.join([lt_script, payload])
        mocked_boto.return_value.Bucket.return_value.download_file.return_value = self.file_name
        self.assertEqual(self.file_name, wrapper.get_locust_file())

    @mock.patch('boto3.resource')
    def test_download_failure_in_s3(self, mocked_boto):
        with mock.patch('botocore.exceptions.ClientError') as boto_core:
            os.environ[self.file_input] = '/'.join([self.s3_link, self.file_name])
            mocked_boto.return_value.Bucket.return_value.download_file.return_value = None
            wrapper.get_locust_file()
            self.assertFalse(boto_core.called)

    @mock.patch('wget.download')
    def test_valid_https_link(self, mocked_wget):
        os.environ[self.file_input] = '/'.join([self.github_link, self.file_name])
        mocked_wget.return_value = self.file_name
        self.assertEqual(self.file_name, wrapper.get_locust_file())

    @mock.patch('wget.download')
    def test_valid_multiple_https_links(self, mocked_wget):
        lt_script = '/'.join([self.github_link, self.file_name])
        payload = '/'.join([self.github_link, self.json_name])
        os.environ[self.file_input] = ','.join([lt_script, payload])
        mocked_wget.return_value = self.file_name
        self.assertEqual(self.file_name, wrapper.get_locust_file())

    def test_valid_local_file(self):
        os.environ[self.file_input] = self.file_name
        FILE_PATH_IN_CONTAINER = '/'.join(['script', self.file_name])
        self.assertEquals(FILE_PATH_IN_CONTAINER, wrapper.get_locust_file())

    @mock.patch('boto3.resource')
    @mock.patch('wget.download')
    def test_cross_ressources(self, mocked_boto, mocked_wget):
        lt_script = '/'.join([self.s3_link, self.file_name])
        payload = '/'.join([self.github_link, self.json_name])
        os.environ[self.file_input] = ','.join([lt_script, payload])
        mocked_boto.return_value.Bucket.return_value.download_file.return_value = self.file_name
        self.assertEqual(self.file_name, wrapper.get_locust_file())

    def test_no_python_file(self):
        os.environ[self.file_input] = '/'.join([self.github_link, 'wrong_file.xml'])
        with self.assertRaises(SystemExit) as exit_code:
            wrapper.get_files()
        self.assertEqual(exit_code.exception.code, 1)

    def test_multipe_python_files(self):
        lt_script = '/'.join([self.github_link, self.file_name])
        other_python_script = '/'.join([self.github_link, 'second.py'])
        os.environ[self.file_input] = ','.join([lt_script, other_python_script])
        with self.assertRaises(SystemExit) as exit_code:
            wrapper.get_files()
        self.assertEqual(exit_code.exception.code, 1)
