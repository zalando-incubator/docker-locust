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
                    logger.info('Start load test automatically for {duration} seconds.'.format(duration=duration))
                    payload = {'locust_count': users, 'hatch_rate': hatch_rate}
                    res = requests.post(url=master_url + '/swarm', data=payload)

                    if res.ok:
                        time.sleep(duration)
                        requests.get(url=master_url + '/stop')
                        logger.info('Load test is stopped.')

                        logger.info('Downloading reports...')
                        report_path = os.path.join(os.getcwd(), 'reports')
                        os.makedirs(report_path)

                        res = requests.get(url=master_url + '/htmlreport')
                        with open(os.path.join(report_path, 'reports.html'), "wb") as file:
                            file.write(res.content)
                        logger.info('Reports have been successfully downloaded.')
                    else:
                        logger.error('Locust cannot be started. Please check logs!')

                    break
                else:
                    logger.error('Attempt: {attempt}. Locust master might not ready yet.'
                                 'Status code: {status}'.format(attempt=_, status=res.status_code))
        except ValueError as v_err:
            logger.error(v_err)

        sys.exit(0)

    elif role == 'standalone':
      os.environ["MASTER_HOST"] = '127.0.0.1'
      for role in ['master', 'slave', 'controller']:
        os.environ['ROLE'] = role
        bootstrap(1)

    else:
        raise RuntimeError('Invalid ROLE value. Valid Options: master, slave, controller.')

    if _return: return

    for s in processes:
        s.communicate()


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
                file_name = '/'.join(['script', file])
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
