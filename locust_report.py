import os
import datetime
import logging
import csv

import requests
from flask import make_response
from jinja2 import Environment, FileSystemLoader


WORK_DIR = os.path.dirname(__file__)
CSV_URL = 'http://0.0.0.0:8089/stats/distribution/csv'
STAT_URL = 'http://0.0.0.0:8089/stats/requests'

HTML_TEMPLATE = 'report-template.html'
HTML_REPORT = 'report.html'

logger = logging.getLogger('reporting')


def generate_report(distribution_csv, template_file, report_file):
    """
    Generate load test result in a format based on the given template and save it into a given report file.

    :param distribution_csv: distribution file name.
    :type distribution_csv: str
    :param template_file: template name.
    :type template_file: str
    :param report_file: report file name.
    :type report_file: str

    """
    with open(distribution_csv, 'r') as dc:
        content = csv.reader(dc)
        table = [','.join(t) for t in content]

        j2_env = Environment(loader=FileSystemLoader(WORK_DIR), trim_blocks=True)

        res = requests.get(url=STAT_URL)
        logger.info('request code for {url} is {status}'.format(url=STAT_URL, status=res.status_code))
        if res.ok:
            stats = res.json()
            logger.info('json response : {res}'.format(res=stats))

            with open(report_file, 'w') as rf:
                for stat in stats['stats']:
                    num_requests = stat['num_requests']
                    num_failures = stat['num_failures']
                    median_response_time = stat['median_response_time']
                    avg_response_time = stat['avg_response_time']
                    min_response_time = stat['min_response_time']
                    max_response_time = stat['max_response_time']
                    avg_content_length = stat['avg_content_length']
                    current_rps = stat['current_rps']

                errors = stats['errors']
                error_type, error_occur, error_method, error_name = ([] if errors else '-' for _ in range(4))
                if errors:
                    for error in errors:
                        error_type.append(error['error'])
                        error_occur.append(error['occurences'])
                        error_method.append(error['method'])
                        error_name.append(error['name'])

                t_column = table[0]
                table.pop(0)

                rf.write(j2_env.get_template(template_file).render(
                    users=stats.get('user_count'), date=str(datetime.date.today()),
                    error_type=error_type,
                    error_occur=error_occur,
                    error_method=error_method,
                    error_name=error_name,
                    slaves=round(float(stats.get('slave_count')), 1), rps=round(float(stats.get('total_rps')), 1),
                    fails=round(float(stats.get('fail_ratio')), 1), num_requests=round(float(num_requests), 1),
                    num_failures=round(float(num_failures), 1), method=stats['stats'][0]['method'],
                    name=stats["stats"][0]['name'], median_response_time=round(float(median_response_time), 1),
                    avg_response_time=round(float(avg_response_time), 1),
                    min_response_time=round(float(min_response_time), 1),
                    max_response_time=round(float(max_response_time), 1),
                    avg_content_length=round(float(avg_content_length), 1),
                    current_rps=round(float(current_rps), 1),
                    table_columns=t_column,
                    table_row=table))


def download_report():
    """
    Download report.

    :return: load test report in html format.

    """
    res = requests.get(url=CSV_URL)
    logger.info('request code for {url} is {status}'.format(url=CSV_URL, status=res.status_code))

    if res.ok:
        distribution_file = 'distribution.csv'
        with open(distribution_file, 'wb') as dis_file:
            dis_file.write(res.text)

        generate_report(distribution_file, HTML_TEMPLATE, HTML_REPORT)

        if os.path.isfile(HTML_REPORT):
            headers = {'Content-Disposition': 'attachment; filename={name}'.format(name=HTML_REPORT)}
            with open(HTML_REPORT, 'r') as rf:
                html_report = rf.read()
            return make_response(html_report, headers) if html_report else None
