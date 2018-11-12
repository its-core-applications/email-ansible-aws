#!/usr/bin/env python

from __future__ import (absolute_import, division, print_function)

import json
import os

import boto3
import requests

def handler(event, context):
    for req in ('SENSU_BACKEND', 'SNS_ARN', 'SNS_ROLE'):
        if not os.environ.get(req):
            print('{} not set'.format(req))
            return

    sensu_backend = os.environ.get('SENSU_BACKEND')
    sensu_region = os.environ.get('SENSU_REGION', 'us-west-2')
    sensu_status = os.environ.get('SENSU_STATUS', 'prod')
    arn = os.environ.get('SNS_ARN')
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

    response = None
    try:
        response = requests.get(sensu_backend.rstrip('/') + '/health', timeout=12)
    except Exception as e:
        status = 'CRITICAL'
        msg = 'Exception: {}'.format(e)

    if response:
        if not response.ok:
            status = 'CRITICAL'
            msg = 'HTTP {}'.format(result.status_code)
        else:
            health = response.json()
            print(health)
            if not all(x['Healthy'] for x in health['ClusterHealth']):
                status = 'CRITICAL'
                msg = ','.join([x['Err'] for x in health['ClusterHealth']])

    if not status:
        return

    subject = '{}/{} - ALERT - {}/sensu-monitor-health {}'.format(sensu_status, sensu_region, sensu_backend.split(':')[1][2:], status)

    lambda_msg = {
        'sourcetype': 'lambda',
        'source': 'sensu_monitor_health',
        'message': msg,
    }

    sns_msg = {
        'default': msg,
        'sms': '{} - {}'.format(subject, msg),
        'lambda': json.dumps(lambda_msg),
    }

    response = client.publish(
        TopicArn = arn,
        Message = json.dumps(sns_msg),
        MessageStructure = 'json',
        Subject = subject,
    )
    print(response)


if __name__ == '__main__':
    handler({}, None)
