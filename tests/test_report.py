"""Unit test for Report generator."""
import json
import os
from unittest import TestCase

import requests_mock

from src.report import HTML_TEMPLATE, STAT_URL
from src.report import generate_report

WORK_DIR = os.path.dirname(__file__)
MOCKED_DISTRIBUTION = os.path.join(WORK_DIR, 'mocked_distribution.csv')
MOCKED_STATISTIC = os.path.join(WORK_DIR, 'mocked_statistic.json')
TEST_REPORT = os.path.join(WORK_DIR, 'test-report.html')


class ReportGeneratorTests(TestCase):

    @requests_mock.mock()
    def test_generate_report(self, mocked_request):
        response = json.load(open(MOCKED_STATISTIC))
        mocked_request.get(STAT_URL, json=response)
        generate_report(MOCKED_DISTRIBUTION, HTML_TEMPLATE, TEST_REPORT)
        with open(TEST_REPORT, 'r') as tr:
            content = tr.read()
            self.assertTrue('Load Test Report' in content)
            self.assertTrue(content.count('HTTPError'), 2)
        os.remove(TEST_REPORT)

    @requests_mock.mock()
    def test_stat_url_inaccessible(self, mocked_request):
        mocked_request.get(STAT_URL, status_code=500)
        generate_report(MOCKED_DISTRIBUTION, HTML_TEMPLATE, TEST_REPORT)
        self.assertFalse(os.path.isfile(TEST_REPORT))
