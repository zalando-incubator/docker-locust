"""Unit test for bootstrap."""
import os
from unittest import TestCase

import mock

import requests_mock

from src.app import bootstrap


class TestBootstrap(TestCase):
    """Unit test class to test method bootstrap."""

    @mock.patch('subprocess.Popen')
    @mock.patch('src.app.send_usage_statistics')
    def test_valid_master(self, popen, mocked_send_usage):
        os.environ['ROLE'] = 'master'
        os.environ['TARGET_HOST'] = 'https://test.com'

        with mock.patch('src.app.get_locust_file') as file:
            bootstrap()
            self.assertTrue(file.called)
            self.assertTrue(popen.called)
            self.assertTrue(mocked_send_usage.called)

    @mock.patch('subprocess.Popen')
    def test_master_not_ready_in_time(self, popen):
        os.environ['ROLE'] = 'slave'
        os.environ['TARGET_HOST'] = 'https://test.com'
        os.environ['MASTER_HOST'] = '127.0.0.1'
        os.environ['SLAVE_MUL'] = '1'
        os.environ['MASTER_CHECK_TIMEOUT'] = '0.3'
        os.environ['MASTER_CHECK_INTERVAL'] = '0.1'

        with mock.patch('src.app.get_locust_file') as file:
            with self.assertRaises(RuntimeError) as e:
                bootstrap()
                self.assertFalse(file.called)
                self.assertFalse(popen.called)
            self.assertEqual('The master did not start in time.', str(e.exception))


    @mock.patch('subprocess.Popen')
    @requests_mock.Mocker()
    def test_valid_slave(self, mocked_popen, mocked_request):
        os.environ['ROLE'] = 'slave'
        os.environ['TARGET_HOST'] = 'https://test.com'
        os.environ['MASTER_HOST'] = '127.0.0.1'
        os.environ['SLAVE_MUL'] = '3'
        os.environ['SLAVES_CHECK_TIMEOUT'] = '0.3'
        os.environ['SLAVES_CHECK_INTERVAL'] = '0.1'

        MASTER_URL = 'http://127.0.0.1:8089'
        mocked_request.get(url=MASTER_URL, text='ok')
        with mock.patch('src.app.get_locust_file') as file:
            bootstrap()
            self.assertTrue(file.called)
            self.assertTrue(mocked_popen.called)

    @mock.patch('time.sleep')
    def test_valid_controller_manual(self, mocked_timeout):
        os.environ['ROLE'] = 'controller'
        os.environ['AUTOMATIC'] = str(False)

        bootstrap()
        self.assertFalse(mocked_timeout.called)

    @mock.patch('src.app.bootstrap')
    def test_standalone_manual(self, mocked_bootstrap):
        os.environ['ROLE'] = 'standalone'
        with mock.patch('src.app.send_usage_statistics'):
            bootstrap()
        self.assertEqual(mocked_bootstrap.call_count, 2)

    @mock.patch('src.app.bootstrap')
    def test_standalone_automatic(self, mocked_bootstrap):
        os.environ['ROLE'] = 'standalone'
        os.environ['AUTOMATIC'] = str(True)
        with self.assertRaises(SystemExit) as exit_code:
            with mock.patch('src.app.send_usage_statistics'):
                bootstrap()
        self.assertEqual(mocked_bootstrap.call_count, 3)
        self.assertEqual(exit_code.exception.code, 0)

    @mock.patch('time.sleep')
    @mock.patch('os.makedirs')
    @mock.patch('builtins.open')
    @requests_mock.Mocker()
    def test_valid_controller_automatic(self, mocked_timeout, mocked_dir, mocked_open, mocked_request):
        os.environ['ROLE'] = 'controller'
        os.environ['AUTOMATIC'] = str(True)
        os.environ['MASTER_HOST'] = '127.0.0.1'
        os.environ['TOTAL_SLAVES'] = '3'
        os.environ['USERS'] = '100'
        os.environ['HATCH_RATE'] = '5'
        os.environ['DURATION'] = '10'

        MASTER_URL = 'http://127.0.0.1:8089'
        mocked_request.get(url=MASTER_URL, text='ok')
        mocked_request.get(url=MASTER_URL + '/stats/requests', json={'slave_count': 3})
        mocked_request.post(url='/'.join([MASTER_URL, 'swarm']), text='ok')
        for endpoint in ['stop', 'stats/requests/csv', 'stats/distribution/csv', 'htmlreport']:
            mocked_request.get(url='/'.join([MASTER_URL, endpoint]), text='ok')

        bootstrap()
        self.assertTrue(mocked_timeout.called)
        self.assertTrue(mocked_request.called)
        self.assertTrue(mocked_open.called)

    @mock.patch('time.sleep')
    @mock.patch('os.makedirs')
    @mock.patch('builtins.open')
    @requests_mock.Mocker()
    def test_slaves_not_fully_connected(self, mocked_timeout, mocked_dir, mocked_open, mocked_request):
        os.environ['ROLE'] = 'controller'
        os.environ['AUTOMATIC'] = str(True)
        os.environ['MASTER_HOST'] = '127.0.0.1'
        os.environ['TOTAL_SLAVES'] = '3'
        os.environ['USERS'] = '100'
        os.environ['HATCH_RATE'] = '5'
        os.environ['DURATION'] = '10'
        os.environ['SLAVES_CHECK_TIMEOUT'] = '0.3'
        os.environ['SLAVES_CHECK_INTERVAL'] = '0.1'

        MASTER_URL = 'http://127.0.0.1:8089'
        mocked_request.get(url=MASTER_URL, text='ok')
        mocked_request.get(url=MASTER_URL + '/stats/requests', json={'slave_count': 1})
        mocked_request.post(url='/'.join([MASTER_URL, 'swarm']), text='ok')
        for endpoint in ['stop', 'stats/requests/csv', 'stats/distribution/csv', 'htmlreport']:
            mocked_request.get(url='/'.join([MASTER_URL, endpoint]), text='ok')

        with self.assertRaises(RuntimeError):
            bootstrap()
            self.assertFalse(mocked_request.called)
            self.assertFalse(mocked_open.called)

    def test_invalid_role(self):
        os.environ['ROLE'] = 'unknown'
        with self.assertRaises(RuntimeError):
            bootstrap()

    @mock.patch('src.app.send_usage_statistics')
    def test_missing_env_variables(self, mocked_send_usage):
        roles = ['master', 'slave']

        for role in roles:
            os.environ['ROLE'] = role
            with self.assertRaises(RuntimeError):
                bootstrap()
                self.assertTrue(mocked_send_usage.called)

    def test_invalid_env_variables(self):
        os.environ['ROLE'] = 'controller'
        os.environ['AUTOMATIC'] = str(True)
        os.environ['MASTER_HOST'] = '127.0.0.1'
        os.environ['USERS'] = 'test'

        bootstrap()
        self.assertRaises(ValueError)

    def tearDown(self):
        env_keys = ['ROLE', 'TARGET_HOST', 'MASTER_HOST', 'SLAVE_MUL', 'LOC', 'AUTOMATIC', 'USERS', 'HATCH_RATE',
                    'DURATION']
        for k in env_keys:
            if os.getenv(k):
                del os.environ[k]
