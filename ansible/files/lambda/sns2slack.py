#!/usr/bin/env python3

import json
import os

import requests


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
        'text': f'*{sns["Subject"]}*',
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

        msg['text'] = f'{cooked["sourcetype"]}@{cooked["source"]}\n{msg["text"]}'

    response = requests.post(webhook, json=msg)

    print(response)
