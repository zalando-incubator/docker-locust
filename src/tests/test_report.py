"""Unit test for Report generator."""
import json
import os
from unittest import TestCase

import requests_mock

from src.report import HTML_TEMPLATE
from src.report import generate_report

WORK_DIR = os.path.dirname(__file__)
DISTRIBUTION_CSV = os.path.join(WORK_DIR, 'mocked_distribution.csv')
REQUESTS_JSON = os.path.join(WORK_DIR, 'mocked_statistic.json')
HTML_REPORT = os.path.join(WORK_DIR, 'test-report.html')


class ReportGeneratorTests(TestCase):

    @requests_mock.mock()
    def test_generate_report(self, mocked_request):
        generate_report(DISTRIBUTION_CSV, REQUESTS_JSON, HTML_REPORT)
        with open(HTML_REPORT, 'r') as tr:
            content = tr.read()
            self.assertTrue('Load Test Report' in content)
            self.assertTrue(content.count('HTTPError'), 2)
        os.remove(HTML_REPORT)
