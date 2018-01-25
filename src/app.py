#!/usr/bin/env python2

import logging

import multiprocessing
import os

import signal
import subprocess
import sys

import requests

processes = []
logging.basicConfig()
logger = logging.getLogger('bootstrap')


def bootstrap(_return=0):
    """
    Initialize role of running docker container.
    master: web interface / API.
    slave: node that load test given url.
    controller: node that control the automatic run.
    """
    role = get_or_raise('ROLE')
    logger.info('Role :{role}'.format(role=role))

    if role == 'master':
        target_host = get_or_raise('TARGET_HOST')
        send_user_usage(target_host)
        locust_file = get_locust_file()
        logger.info('target host: {target}, locust file: {file}'.format(target=target_host, file=locust_file))

        s = subprocess.Popen([
            'locust', '-H', target_host, '--loglevel', 'debug', '--master', '-f', locust_file
        ])
        processes.append(s)

    elif role == 'slave':
        try:
            target_host = get_or_raise('TARGET_HOST')
            locust_file = get_locust_file()
            master_host = get_or_raise('MASTER_HOST')
            multiplier = int(os.getenv('SLAVE_MUL', multiprocessing.cpu_count()))
        except ValueError as verr:
            logger.error(verr)

        logger.info('target host: {target}, locust file: {file}, master: {master}, multiplier: {multiplier}'.format(
            target=target_host, file=locust_file, master=master_host, multiplier=multiplier))
        for _ in range(multiplier):
            logger.info('Started Process')
            s = subprocess.Popen([
                'locust', '-H', target_host, '--loglevel', 'debug', '--slave', '-f', locust_file,
                '--master-host', master_host
            ])
            processes.append(s)

    elif role == 'controller':
        automatic = convert_str_to_bool(os.getenv('AUTOMATIC', str(False)))
        logger.info('Automatic run: {auto}'.format(auto=automatic))

        if not automatic:
            return

        try:
            master_host = get_or_raise('MASTER_HOST')
            master_url = 'http://{master}:8089'.format(master=master_host)
            total_slaves = int(os.getenv('TOTAL_SLAVES')) if os.getenv('TOTAL_SLAVES') else int(
                os.getenv('SLAVE_MUL', multiprocessing.cpu_count()))
            # Default time duration to wait all slaves to be connected is 1 minutes / 60 seconds
            slaves_check_timeout = float(os.getenv('SLAVES_CHECK_TIMEOUT', 60))
            # Default sleep time interval is 10 seconds
            slaves_check_interval = float(os.getenv('SLAVES_CHECK_INTERVAL', 5))
            users = int(get_or_raise('USERS'))
            hatch_rate = int(get_or_raise('HATCH_RATE'))
            duration = int(get_or_raise('DURATION'))
            logger.info(
                'master url: {url}, users: {users}, hatch_rate: {rate}, duration: {duration}'.format(
                    url=master_url, users=users, rate=hatch_rate, duration=duration))

            for _ in range(0, 5):
                import time
                time.sleep(3)

                res = requests.get(url=master_url)
                if res.ok:
                    timeout = time.time() + slaves_check_timeout
                    connected_slaves = 0
                    while time.time() < timeout:
                        try:
                            logger.info('Checking if all slave(s) are connected.')
                            stats_url = '/'.join([master_url, 'stats/requests'])
                            res = requests.get(url=stats_url)
                            connected_slaves = res.json().get('slave_count')

                            if connected_slaves >= total_slaves:
                                break
                            else:
                                logger.info('Currently connected slaves: {con}'.format(con=connected_slaves))
                                time.sleep(slaves_check_interval)
                        except ValueError as v_err:
                            logger.error(v_err.message)
                    else:
                        logger.warning('Connected slaves:{con} != defined slaves:{dfn}'.format(
                            con=connected_slaves, dfn=total_slaves))

                    logger.info('All slaves are succesfully connected! '
                                'Start load test automatically for {duration} seconds.'.format(duration=duration))
                    payload = {'locust_count': users, 'hatch_rate': hatch_rate}
                    res = requests.post(url=master_url + '/swarm', data=payload)

                    if res.ok:
                        time.sleep(duration)
                        requests.get(url=master_url + '/stop')
                        logger.info('Load test is stopped.')

                        time.sleep(4)

                        logging.info('Creating report folder.')
                        report_path = os.path.join(os.getcwd(), 'reports')
                        if not os.path.exists(report_path):
                            os.makedirs(report_path)

                        logger.info('Creating reports...')
                        for _url in ['requests', 'distribution']:
                            res = requests.get(url=master_url + '/stats/' + _url + '/csv')
                            with open(os.path.join(report_path, _url + '.csv'), "wb") as file:
                                file.write(res.content)

                            if _url == 'distribution':
                                continue
                            res = requests.get(url=master_url + '/stats/' + _url)
                            with open(os.path.join(report_path, _url + '.json'), "wb") as file:
                                file.write(res.content)

                        res = requests.get(url=master_url + '/htmlreport')
                        with open(os.path.join(report_path, 'reports.html'), "wb") as file:
                            file.write(res.content)
                        logger.info('Reports have been successfully created.')
                    else:
                        logger.error('Locust cannot be started. Please check logs!')

                    break
                else:
                    logger.error('Attempt: {attempt}. Locust master might not ready yet.'
                                 'Status code: {status}'.format(attempt=_, status=res.status_code))
        except ValueError as v_err:
            logger.error(v_err)

    elif role == 'standalone':
        automatic = convert_str_to_bool(os.getenv('AUTOMATIC', str(False)))
        os.environ["MASTER_HOST"] = '127.0.0.1'

        for role in ['master', 'slave']:
            os.environ['ROLE'] = role
            bootstrap(1)

        if automatic:
            os.environ['ROLE'] = 'controller'
            bootstrap(1)
            sys.exit(0)

    else:
        raise RuntimeError('Invalid ROLE value. Valid Options: master, slave, controller.')

    if _return:
        return

    for s in processes:
        s.communicate()


def send_user_usage(target_host):
    """Send user usage to Google Analytics."""

    try:
        ga_endpoint = 'https://www.google-analytics.com/collect'
        ga_tracking_id = 'UA-110383676-1'
        send_kpi = convert_str_to_bool(os.getenv('SEND_ANONYMOUS_USAGE_INFO', str(False)))

        if send_kpi:
            app_id = os.getenv('APPLICATION_ID')
            build_url = os.getenv('BUILD_URL')
            cdp_target_repository = os.getenv('CDP_TARGET_REPOSITORY')
            image_version = os.getenv('DL_IMAGE_VERSION', 'unknown')

            host_in_array = target_host.split('.')
            if 'zalan.do' in target_host:
                contains_zalando = True
            elif len(host_in_array) >= 2 and 'zalando' in host_in_array[len(host_in_array) - 2]:
                contains_zalando = True
            else:
                contains_zalando = False

            if app_id:
                user_type = 'internal'
                user = app_id.split('-')[0]
                description = 'AWS'
            elif build_url and 'zalan.do' in build_url:
                user_type = 'internal'
                user = build_url.split('/')[2].split('.')[0]
                description = 'Jenkins'
            elif cdp_target_repository and 'github' in cdp_target_repository:
                user_type = 'internal'
                user = cdp_target_repository.split('/')[1]
                description = 'CDP'
            else:
                user_type = 'external/local-machine'
                with open('/proc/version', 'r') as v:
                    user = '_'.join(w for w in v.read().split(' ') if '@' not in w)
                description = '-'

            if contains_zalando:
                description += '; {host}'.format(host=target_host)

            payload = {
                'v': '1',  # API Version.
                'tid': ga_tracking_id,
                'cid': user,
                't': 'event',  # Event hit type.
                'ec': user_type,
                'ea': user,
                'el': description,
                'an': 'docker-locust',
                'av': image_version,
            }

            for attempt in range(1, 4):
                logger.info('attempt: {attempt}'.format(attempt=attempt))
                res = requests.post(ga_endpoint, data=payload)
                if res.ok:
                    logger.info('User usage is successfully sent!')
                    break
            else:
                logger.warning('User usage cannot be sent! response: {res}'.format(res.text))
    except Exception as e:
        logger.warning(e)
        pass


def get_locust_file():
    """
    Find locust file.
    Possible parameters are:
    1. S3 Bucket
    2. Any http or https url e.g. raw url from GitHub
    3. File from 'locust-script' folder

    :return: file_name
    :rtype: str
    """

    files = get_files()
    file_name = None

    for file in files:
        # Download from s3 bucket
        if file.startswith('s3://'):
            if file.endswith('.py'):
                file_name = os.path.basename(file)
            _, _, bucket, path = file.split('/', 3)
            f = os.path.basename(file)

            import boto3
            import botocore
            s3 = boto3.resource('s3')

            try:
                s3.Bucket(bucket).download_file(path, f)
            except botocore.exceptions.ClientError as e:
                if e.response['Error']['Code'] == "404":
                    logger.error('File cannot be found!')
                else:
                    raise
        # Download from http or https
        elif file.startswith('http'):
            logger.info('Load test script from http or https url')
            import wget
            try:
                if file.endswith('.py'):
                    file_name = wget.download(file)
                else:
                    wget.download(file)
            except:
                logger.error('File cannot be downloaded! Please check given url!')
        # Share volume with local machine
        else:
            logger.info('Load test script from local machine')
            if file.endswith('.py'):
                file_name = file if file.startswith('/') else '/'.join(['script', file])
    logger.info('load test file: {f}'.format(f=file_name))
    return file_name


def get_files():
    """
    Check user input and return all valid files.

    :return: files
    :rtype: list
    """
    given_input = get_or_raise('LOCUST_FILE')
    logger.info('Given input: {input}'.format(input=given_input))
    files = [i.strip() for i in given_input.split(',')]
    logger.info('Files: {files}'.format(files=files))

    python_files = [file for file in files if str(file).endswith('py')]
    if not python_files:
        logger.error('There is no python file!')
        sys.exit(1)
    elif python_files.__len__() > 1:
        logger.error('There are more than 1 python files!')
        sys.exit(1)
    else:
        logger.info('Check passed!')
        return files


def convert_str_to_bool(str):
    """
    Convert string to boolean.

    :param str: given string
    :type str: str
    :return: converted string
    :rtype: bool
    """
    if isinstance(str, basestring):
        return str.lower() in ('yes', 'true', 't', '1')
    else:
        return False


def get_or_raise(env):
    """
    Check if needed environment variables are given.

    :param env: key
    :type env: str
    :return: value
    :rtype: str
    """
    env_value = os.getenv(env)
    if not env_value:
        raise RuntimeError('The environment variable {0:s} should be set.'.format(env))
    return env_value


def kill(signal, frame):
    logger.info('Received KILL signal')
    for s in processes:
        s.kill(s)


if __name__ == '__main__':
    logger.setLevel(logging.INFO)
    logger.info('Started main')
    signal.signal(signal.SIGTERM, kill)
    bootstrap()
