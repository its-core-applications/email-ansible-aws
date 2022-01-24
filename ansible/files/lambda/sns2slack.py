#!/usr/bin/env python

from __future__ import (absolute_import, division, print_function)

import json
import os

import requests

ICON_MAP = {
    'sensu': 'https://cdn-images-1.medium.com/1*qC5lFfMvQd_zci2MBXZZpg.png',
    'ansible': 'https://www.ansible.com/favicon.ico',
    'nagios': 'https://a.slack-edge.com/80588/img/services/nagios_512.png',
}

def handler(event, context):
    print(json.dumps(event))

    webhook = os.getenv('WEBHOOK_URL')

    sns = event['Records'][0]['Sns']

    if 'WARNING' in sns['Subject']:
        color = 'warning'
    elif any(x in sns['Subject'] for x in ['CRITICAL', 'FAILED', 'DOWN']):
        color = 'danger'
    else:
        color = 'good'

    msg = {
        'parse': 'none',
        'username': 'SNS',
        'icon_url': 'https://a.slack-edge.com/66f9/img/avatars/ava_0002-48.png',
        'text': '*{}*'.format(sns['Subject']),
        'attachments': [
            {
                'color': color,
                'text': sns['Message'],
            }
        ],
    }

    try:
        cooked = json.loads(sns['Message'])
    except ValueError:
        pass
    else:
        msg['attachments'][0]['text'] = cooked['message']

        if cooked['sourcetype'] in ICON_MAP:
            msg['icon_url'] = ICON_MAP[cooked['sourcetype']]

        msg['username'] = '{}@{}'.format(cooked['sourcetype'], cooked['source'])

    response = requests.post(webhook, json = msg)

    print(response)
