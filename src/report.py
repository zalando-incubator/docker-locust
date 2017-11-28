import csv
import datetime
import json
import logging
import os

from jinja2 import Environment, FileSystemLoader

HTML_TEMPLATE = 'report-template.html'
HTML_REPORT = 'reports/reports.html'
DISTRIBUTION_CSV = 'reports/distribution.csv'
REQUESTS_JSON = 'reports/requests.json'

WORK_DIR = os.path.dirname(__file__)

logger = logging.getLogger('reporting')

def generate_report():
    """
    Generate load test result in a format based on the given template and save it into a given report file.

    """

    with open(DISTRIBUTION_CSV, 'r') as dc:
        content = csv.reader(dc)
        distribution = [','.join(t) for t in content]

        j2_env = Environment(loader=FileSystemLoader(WORK_DIR), trim_blocks=True)

        with open(REQUESTS_JSON, 'r') as requests:
            json_res = json.load(requests)
            logger.info('json response : {res}'.format(res=json_res))

            with open(HTML_REPORT, 'w') as rf:
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

                rf.write(j2_env.get_template(HTML_TEMPLATE).render(
                    datetime=datetime.datetime.now().strftime("%I:%M%p on %B %d, %Y"),
                    slaves=round(float(json_res.get('slave_count')), 1),
                    rps=round(float(json_res.get('total_rps')), 1),
                    fails=round(float(json_res.get('fail_ratio')), 1),
                    stat_methods=s_methods, stat_names=s_names, stat_num_requests=s_num_req,
                    stat_num_failures=s_failures, stat_median_res=s_median, stat_avg_res=s_avg,
                    stat_min_res=s_min, stat_max_res=s_max, stat_content_length=s_length, stat_rps=s_rps,
                    error_method=e_method, error_name=e_name, error_occur=e_occurences, error_description=e_description,
                    distribution_header=distribution[0], distribution_content=distribution[1:]))
