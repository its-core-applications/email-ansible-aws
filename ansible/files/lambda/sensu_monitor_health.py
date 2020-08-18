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
    
    #sensu_backend = 'http://sensu.us-east-2.x.mail.umich.edu:4567/'
    #sensu_region = 'us-east-2'
    #sensu_status = 'nonprod'
    #arn = 'arn:aws:sns:us-west-2:440653842962:oncall'
    #sns_region = 'us-west-2'
    #sns_role = 'arn:aws:iam::440653842962:role/umcollab_440653842962_SNS'

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

    fail_count = 0
    response = None
    retries = 5

    while fail_count < retries:
        health_result = health_check(sensu_backend, fail_count, response, retries, status)
        fail_count = health_result[0]
        print("Check: ",fail_count)

    msg = health_result[1]
    status = health_result[2]

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

def health_check(sensu_backend, fail_count, response, retries, status):
    msg = None 
    try:
        response = requests.get(sensu_backend.rstrip('/') + '/health', timeout=12)
    except Exception as e:
        status = 'CRITICAL'
        msg = 'Exception: {}'.format(e)
        fail_count = retries

    if response:
        if not response.ok:
            status = 'CRITICAL'
            msg = 'HTTP {}'.format(response.status_code)
            fail_count = retries
        else:
            health = response.json()
            print(health)
            if not all(x['Healthy'] for x in health['ClusterHealth']):
                status = 'CRITICAL'
                msg = ','.join([x['Err'] for x in health['ClusterHealth']])
                fail_count +=1

    if not status:
        fail_count = retries
    
    return (fail_count, msg, status)

if __name__ == '__main__':
    handler({}, None)
