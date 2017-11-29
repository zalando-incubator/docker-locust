import csv
import datetime
import logging
import os
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
        distribution = [','.join(t) for t in content]

        j2_env = Environment(loader=FileSystemLoader(WORK_DIR), trim_blocks=True)

        res = requests.get(url=STAT_URL)
        logger.info('request code for {url} is {status}'.format(url=STAT_URL, status=res.status_code))
        if res.ok:
            json_res = res.json()
            logger.info('json response : {res}'.format(res=json_res))

            with open(report_file, 'w') as rf:
                s_methods, s_names, s_num_req, s_failures, s_median,  s_avg, s_min, s_max, s_length, s_rps =  \
                    ([] for _ in range(10))

                for stat in json_res['stats']:
                    s_methods.append(stat['method'])
                    s_names.append(stat['name'])
                    s_num_req.append(stat['num_requests'])
                    s_failures.append(stat['num_failures'])
                    s_median.append(stat['median_response_time'])
                    s_avg.append(round(float(stat['avg_response_time']), 1))
                    s_min.append(stat['min_response_time'])
                    s_max.append(stat['max_response_time'])
                    s_length.append(round(float(stat['avg_content_length']), 1))
                    s_rps.append(round(float(stat['current_rps']), 1))

                errors = json_res['errors']
                e_method, e_name, e_occurences, e_description = ([] if errors else '-' for _ in range(4))
                if errors:
                    for error in errors:
                        e_method.append(error['method'])
                        e_name.append(error['name'])
                        e_occurences.append(error['occurences'])
                        e_description.append(error['error'])

                rf.write(j2_env.get_template(template_file).render(
                    datetime=datetime.datetime.now().strftime("%I:%M%p on %B %d, %Y"),
                    slaves=round(float(json_res.get('slave_count')), 1),
                    rps=round(float(json_res.get('total_rps')), 1),
                    fails=round(float(json_res.get('fail_ratio')), 1),
                    stat_methods=s_methods, stat_names=s_names, stat_num_requests=s_num_req,
                    stat_num_failures=s_failures, stat_median_res=s_median, stat_avg_res=s_avg,
                    stat_min_res=s_min, stat_max_res=s_max, stat_content_length=s_length, stat_rps=s_rps,
                    error_method=e_method, error_name=e_name, error_occur=e_occurences, error_description=e_description,
                    distribution_header=distribution[0], distribution_content=distribution[1:]))


def download_report():
    """
    Download report.

    :return: load test report in html format.

    """
    if os.getenv('ROLE') != 'master': return

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
