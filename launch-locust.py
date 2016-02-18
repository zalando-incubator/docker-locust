#!/usr/bin/env python2

import os
import logging
import multiprocessing
import subprocess
import sys

logging.basicConfig(level=logging.INFO)

filename = os.getenv('LOCUST_FILE')

if not filename:
    logging.error('No locust file')
    sys.exit(1)

if filename.startswith('s3://'):
    _, _, bucket, path = filename.split('/', 3)

    import boto3
    s3 = boto3.client('s3')
    filename = os.path.join('/tmp/', os.path.basename(filename))
    logging.info('Downloading Locust file {} from S3 bucket {}..'.format(path, bucket))
    s3.download_file(bucket, path, filename)



cmd = ['locust', '-f', filename]

target_host = os.getenv('LOCUST_TARGET_HOST')
if target_host:
    cmd.extend(['--host', target_host.rstrip('/')])

master_host = os.getenv('LOCUST_MASTER_HOST')
if master_host:
    cmd.extend(['--slave', '--master-host', master_host])
else:
    if os.getenv('LOCUST_MASTER'):
        cmd.extend(['--master'])
    clients = os.getenv('LOCUST_CLIENTS')
    hatch_rate = os.getenv('LOCUST_HATCH_RATE')
    if clients and hatch_rate:
        cmd.extend(['--no-web', '--clients', clients, '--hatch-rate', hatch_rate])

slave_count = int(os.getenv('LOCUST_SLAVE_COUNT', multiprocessing.cpu_count()))


def spawn_slave(n):
    sys.exit(subprocess.call(cmd))


if not master_host:
    logging.info('Starting Locust master..')
    sys.exit(subprocess.call(cmd))
else:
    slaves = []
    for i in range(slave_count):
        logging.info('Spawning Locust slave {}..'.format(i))
        p = multiprocessing.Process(target=spawn_slave, args=(i,))
        slaves.append(p)
        p.start()
    for slave in slaves:
        slave.join(5)
