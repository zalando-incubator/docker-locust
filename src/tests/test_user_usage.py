"""Unit test for user usage."""
import os
from unittest import TestCase

import requests_mock

from src.app import send_user_usage


class TestUserUsage(TestCase):
    """Unit test class to test method send_user_usage."""

    TEST_URL = 'https://test.zalan.do'

    @requests_mock.Mocker()
    def test_not_to_send(self, mocked_request):
        os.environ['SEND_ANONYMOUS_USAGE_INFO'] = str(False)
        send_user_usage(self.TEST_URL)
        self.assertFalse(mocked_request.called)

    @requests_mock.Mocker()
    def test_send_usage_usage(self, mocked_request):
        os.environ['SEND_ANONYMOUS_USAGE_INFO'] = str(True)
        os.environ['DL_IMAGE_VERSION'] = '1.0'
        platforms = {
            'APPLICATION_ID': 'tip-locust',
            'BUILD_URL': 'https://tip.ci.zalan.do/job/test-tracker/1/',
            'CDP_TARGET_REPOSITORY': 'github.bus.zalan.do/butomo/test-tracker',
            'Local': 'fakeenv'
        }

        for k, v in platforms.items():
            os.environ[k] = v
            mocked_request.post(url='https://www.google-analytics.com/collect', text='ok')
            send_user_usage(self.TEST_URL)
            self.assertTrue(mocked_request.called)
            del os.environ[k]

    def tearDown(self):
        env_keys = ['SEND_ANONYMOUS_USAGE_INFO', 'DL_IMAGE_VERSION']
        for k in env_keys:
            if os.getenv(k):
                del os.environ[k]
