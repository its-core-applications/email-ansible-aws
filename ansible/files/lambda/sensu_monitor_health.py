#!/usr/bin/env python

from __future__ import (absolute_import, division, print_function)

import json
import os

import boto3
import requests


def health_check(sensu_backend):
    status = 'CRITICAL'
    msg = None

    try:
        response = requests.get(sensu_backend.rstrip('/') + '/health', timeout=12)
    except Exception as e:
        msg = 'Exception: {}'.format(e)
    else:
        if not response.ok:
            msg = 'HTTP {}'.format(response.status_code)
        else:
            health = response.json()
            print(health)
            if not all(x['Healthy'] for x in health['ClusterHealth']):
                msg = ','.join([x['Err'] for x in health['ClusterHealth']])

    if msg == None:
        status = 'OK'
        msg = 'All checks passed'

    return (status, msg)


def handler(event, context):
    for req in ('SENSU_BACKEND', 'SNS_ARNS', 'SNS_ROLE'):
        if not os.environ.get(req):
            print('{} not set'.format(req))
            return

    sensu_backend = os.environ.get('SENSU_BACKEND')
    sensu_region = os.environ.get('SENSU_REGION', 'us-west-2')
    sensu_status = os.environ.get('SENSU_STATUS', 'prod')
    arns = os.environ.get('SNS_ARNS').split(',')
    sns_region = os.environ.get('SNS_REGION', 'us-east-2')
    sns_role = os.environ.get('SNS_ROLE')

    status = None
    sts = boto3.client('sts')
    creds = sts.assume_role(
        RoleArn=sns_role,
        RoleSessionName='sensu_monitor_health',
    )
    client = boto3.client(
        'sns',
        region_name=sns_region,
        aws_access_key_id=creds['Credentials']['AccessKeyId'],
        aws_secret_access_key=creds['Credentials']['SecretAccessKey'],
        aws_session_token=creds['Credentials']['SessionToken'],
    )

    attempt = 0
    status = None
    msg = None

    while status != 'OK' and attempt < 3:
        attempt += 1
        status, msg = health_check(sensu_backend)
        print('{}: {}'.format(status, msg))

    if status == 'OK':
        return

    subject = '{}/{} - ALERT - {}/sensu-monitor-health {}'.format(sensu_status, sensu_region, sensu_backend.split(':')[1][2:], status)

    lambda_msg = {
        'sourcetype': 'sensu_monitor_health',
        'source': 'lambda',
        'message': msg,
    }

    sns_msg = {
        'default': msg,
        'sms': '{} - {}'.format(subject, msg),
        'lambda': json.dumps(lambda_msg),
    }

    for arn in arns:
        response = client.publish(
            TopicArn = arn,
            Message = json.dumps(sns_msg),
            MessageStructure = 'json',
            Subject = subject,
        )
        print(response)


if __name__ == '__main__':
    handler({}, None)
