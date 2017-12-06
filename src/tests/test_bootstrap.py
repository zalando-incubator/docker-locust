"""Unit test for bootstrap."""
import os
from unittest import TestCase

import mock

import requests_mock

from src.wrapper import bootstrap


class TestBootstrap(TestCase):
    """Unit test class to test method bootstrap."""

    @mock.patch('subprocess.Popen')
    def test_valid_master(self, popen):
        os.environ['ROLE'] = 'master'
        os.environ['TARGET_HOST'] = 'https://test.com'

        with mock.patch('src.wrapper.get_locust_file') as file:
            bootstrap()
            self.assertTrue(file.called)
            self.assertTrue(popen.called)

    @mock.patch('subprocess.Popen')
    def test_valid_slave(self, mocked_popen):
        os.environ['ROLE'] = 'slave'
        os.environ['TARGET_HOST'] = 'https://test.com'
        os.environ['MASTER_HOST'] = '127.0.0.1'
        os.environ['SLAVE_MUL'] = '3'

        with mock.patch('src.wrapper.get_locust_file') as file:
            bootstrap()
            self.assertTrue(file.called)
            self.assertTrue(mocked_popen.called)

    @mock.patch('time.sleep')
    def test_valid_controller_manual(self, mocked_timeout):
        os.environ['ROLE'] = 'controller'
        os.environ['AUTOMATIC'] = str(False)

        bootstrap()
        self.assertFalse(mocked_timeout.called)

    @mock.patch('subprocess.Popen')
    @mock.patch('sys.exit')
    def test_standalone(self, mocked_popen, mocked_exit):
        os.environ['ROLE'] = 'standalone'
        os.environ['TARGET_HOST'] = 'https://test.com'
        os.environ['AUTOMATIC'] = '1'
        os.environ['LOC'] = '1'

        with mock.patch('src.wrapper.get_locust_file'):
            bootstrap()
            self.assertTrue(mocked_popen.called)

            os.environ['AUTOMATIC'] = '0'
            bootstrap()
            self.assertTrue(mocked_popen.called)
            self.assertTrue(mocked_exit.called)

    @mock.patch('time.sleep')
    @mock.patch('os.makedirs')
    @mock.patch('__builtin__.open')
    @requests_mock.Mocker()
    def test_valid_controller_automatic(self, mocked_timeout, mocked_dir, mocked_open, mocked_request):
        os.environ['ROLE'] = 'controller'
        os.environ['AUTOMATIC'] = str(True)
        os.environ['MASTER_HOST'] = '127.0.0.1'
        os.environ['SLAVE_MUL'] = '3'
        os.environ['USERS'] = '100'
        os.environ['HATCH_RATE'] = '5'
        os.environ['DURATION'] = '10'

        mocked_request.get(url='http://127.0.0.1:8089', text='ok')
        mocked_request.post(url='http://127.0.0.1:8089/swarm', text='ok')
        mocked_request.get(url='http://127.0.0.1:8089/stop', text='ok')
        mocked_request.get(url='http://127.0.0.1:8089/stats/requests', text='ok')
        mocked_request.get(url='http://127.0.0.1:8089/stats/requests/csv', text='ok')
        mocked_request.get(url='http://127.0.0.1:8089/stats/distribution/csv', text='ok')
        mocked_request.get(url='http://127.0.0.1:8089/htmlreport', text='ok')
        self.assertFalse(mocked_timeout.called)
        self.assertFalse(mocked_request.called)
        self.assertFalse(mocked_dir.called)
        self.assertFalse(mocked_open.called)
        bootstrap()
        self.assertTrue(mocked_timeout.called)
        self.assertTrue(mocked_request.called)
        self.assertTrue(mocked_dir.called)
        self.assertTrue(mocked_open.called)

    def test_invalid_role(self):
        os.environ['ROLE'] = 'unknown'
        with self.assertRaises(RuntimeError):
            bootstrap()

    def test_missing_env_variables(self):
        roles = ['master', 'slave']

        for role in roles:
            os.environ['ROLE'] = role
            with self.assertRaises(RuntimeError):
                bootstrap()

    def test_invalid_env_variables(self):
        os.environ['ROLE'] = 'controller'
        os.environ['AUTOMATIC'] = str(True)
        os.environ['MASTER_HOST'] = '127.0.0.1'
        os.environ['USERS'] = 'test'

        bootstrap()
        self.assertRaises(ValueError)
