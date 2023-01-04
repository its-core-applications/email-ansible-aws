#!/usr/bin/env python3

import argparse
import json
import os
import sys
import time

import requests

from base64 import b64encode
from datetime import datetime, timedelta, timezone

HAS_BOTOCORE = True
try:
    import botocore.session
except ImportError:
    HAS_BOTOCORE = False


def parse_date(date_string):
    # fromisoformat() doesn't support full ISO format until Python 3.11,
    # so we need to mangle it
    dt = datetime.fromisoformat(date_string[0:19])
    # convert to local timezone
    return dt.replace(tzinfo=timezone.utc).astimezone()


def get_vaulted_api_key():
    vault_addr = os.environ['VAULT_ADDR']
    # Logging into Vault is a little messy...
    boto_client = botocore.session.get_session().create_client('sts')
    boto_endpoint = boto_client._endpoint
    boto_operation_model = boto_client._service_model.operation_model('GetCallerIdentity')
    boto_request_dict = boto_client._convert_to_request_dict({}, boto_operation_model)
    sts_request = boto_endpoint.create_request(boto_request_dict, boto_operation_model)

    vault_login = {
        'role': 'umcollab_bastion',
        'iam_http_request_method': sts_request.method,
        'iam_request_url': b64encode(sts_request.url.encode('utf-8')).decode('utf-8'),
        'iam_request_body': b64encode(sts_request.body.encode('utf-8')).decode('utf-8'),
        'iam_request_headers': json.dumps({x[0]: (x[1] if isinstance(x[1], str) else x[1].decode('utf-8')) for x in sts_request.headers.items()}),
    }
    vault_token = requests.post(
        f'{vault_addr}/v1/auth/aws/login',
        json=vault_login,
    ).json()['auth']['client_token']

    return requests.get(
        f'{vault_addr}/v1/secret/opsgenie/api',
        json={'ttl': '15m'},
        headers={'Authorization': f'Bearer {vault_token}'},
    ).json()['data']['apikey']


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--api-host', default='https://api.opsgenie.com')
    parser.add_argument('--api-key')
    parser.add_argument('--days', default=7, type=int)
    parser.add_argument('--include-empty-periods', action='store_true')
    parser.add_argument('--schedule')
    args = parser.parse_args()

    api_key = args.api_key
    if not api_key and 'VAULT_ADDR' in os.environ:
        if not HAS_BOTOCORE:
            print('botocore is required for Vault login and is not available', file=sys.stderr)
            sys.exit(1)
        api_key = get_vaulted_api_key()

    if not api_key:
        print('--api-key is required if Vault is not available', file=sys.stderr)
        sys.exit(1)

    # Build the list of alerts
    opsgenie = requests.Session()
    opsgenie.headers.update({'Authorization': f'GenieKey {api_key}'})

    alerts = []
    start_time = int((datetime.now() - timedelta(days=args.days)).timestamp() * 1000)
    res = opsgenie.get(
        f'{args.api_host}/v2/alerts',
        params={
            'query': f'createdAt > {start_time}',
            'limit': 100,
        },
    ).json()
    alerts.extend(res['data'])
    while 'next' in res['paging']:
        res = opsgenie.get(res['paging']['next']).json()
        alerts.extend(res['data'])

    # Fetch the schedule
    schedule = args.schedule
    if not schedule:
        schedule = opsgenie.get(f'{args.api_host}/v2/schedules').json()['data'][0]['id']

    raw_periods = opsgenie.get(
        f'{args.api_host}/v2/schedules/{schedule}/timeline',
        params={
            'interval': args.days,
            'intervalUnit': 'days',
            'date': (datetime.now() - timedelta(days=args.days)).astimezone().replace(microsecond=0).isoformat(),
        },
    ).json()['data']['finalTimeline']['rotations'][0]['periods']

    periods = []
    for period in raw_periods:
        periods.append({
            'person': period['recipient']['name'].replace('@umich.edu', ''),
            'start_time': parse_date(period['startDate']),
            'end_time': parse_date(period['endDate']),
            'alerts': [],
        })

    # Iterate over the alerts and assign them to periods
    for alert in reversed(alerts):
        alert_details = opsgenie.get(f'{args.api_host}/v2/alerts/{alert["id"]}').json()['data']
        alert_start = parse_date(alert['createdAt'])

        # find the correct period
        period = None
        for p in periods:
            if alert_start > p['start_time'] and alert_start < p['end_time']:
                period = p

        alert_start = alert_start.strftime('%a %d %b %H:%M')

        # Pretty alert duration
        if 'closeTime' in alert['report']:
            alert_duration = timedelta(milliseconds=alert['report']['closeTime'])
            alert_duration -= timedelta(microseconds=alert_duration.microseconds)
            alert_duration = f'for {alert_duration}'
        else:
            alert_duration = '(still open)'

        # Grab potential output fields in order of preference
        output = ''
        for key in ['output', 'service_output', 'host_output']:
            if not output:
                output = alert_details['details'].get(key, '')
        output = output.splitlines()[0]

        period['alerts'].append(f'{alert_start} {alert_duration} - {alert["alias"]} - {output}')
        # Crude request rate throttling
        time.sleep(0.1)

    for period in periods:
        if len(period['alerts']) == 0 and not args.include_empty_periods:
            continue

        interval = period['start_time'].strftime('%A, %B %d')
        interval_end = period['end_time'].strftime('%A, %B %d')
        if interval != interval_end:
            interval = f'{interval} to {interval_end}'

        print(f'\n{period["person"]} - {interval} (alerts: {len(period["alerts"])})\n')
        for alert in period['alerts']:
            print(alert)


if __name__ == '__main__':
    main()
