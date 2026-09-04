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
    try:
        boto_request_dict = boto_client._convert_to_request_dict({}, boto_operation_model, endpoint_url=boto_endpoint.host)
    except TypeError:
        # Older versions of botocore don't require the endpoint_url
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

    res = requests.get(
        f'{vault_addr}/v1/secret/splunk/oncall_api',
        json={'ttl': '15m'},
        headers={'Authorization': f'Bearer {vault_token}'},
    ).json()['data']
    return res['id'], res['key']


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        '--api-host',
        default='https://api.victorops.com',
        help='Splunk On-Call API endpoint',
    )
    parser.add_argument(
        '--api-id',
        help='Splunk On-Call API ID',
    )
    parser.add_argument(
        '--api-key',
        help='Splunk On-Call API key',
    )
    parser.add_argument(
        '--days',
        default=7,
        type=int,
        help='Number of days of alerts to retrieve',
    )
    parser.add_argument(
        '--routing-key',
        default='zabbix-prod-core-apps',
        help='Routing key for filtering incidents'
    )
    args = parser.parse_args()

    api_id = args.api_id
    api_key = args.api_key
    if not api_key and 'VAULT_ADDR' in os.environ:
        if not HAS_BOTOCORE:
            print('botocore is required for Vault login and is not available', file=sys.stderr)
            sys.exit(1)
        api_id, api_key = get_vaulted_api_key()

    if not api_key:
        print('--api-key is required if Vault is not available', file=sys.stderr)
        sys.exit(1)

    victorops = requests.Session()
    victorops.headers.update({
        'X-VO-Api-Id': api_id,
        'X-VO-Api-Key': api_key,
    })

    # Build the list of alerts
    start_time = (datetime.now() - timedelta(days=args.days)).isoformat()
    search_params = {
        'routingKey': args.routing_key,
        'startedAfter': start_time,
        'currentPhase': 'resolved,triggered,acknowledged',
        'limit': 100,
    }

    incidents = []
    res = None
    while (res is None) or (res['offset'] + res['limit'] < res['total']):
        res = victorops.get(
            f'{args.api_host}/api-reporting/v2/incidents',
            params=search_params,
        ).json()
        incidents.extend(res['incidents'])
        search_params['offset'] = res['offset'] + res['limit']
        if res['offset'] + res['limit'] < res['total']:
            # "This API may be called a maximum of once a minute."
            print(f'{len(incidents)} of {res["total"]} fetched, waiting 60 seconds before fetching the next page...', file=sys.stderr)
            time.sleep(61)

    print(f'Alerts: {len(incidents)}\n')
    for inc in incidents:
        inc_number = inc['incidentNumber']
        inc_start = parse_date(inc['startTime'])
        if inc['currentPhase'] == 'resolved':
            inc_end = parse_date(inc['transitions'][-1]['at'])
            duration = inc_end - inc_start
            duration -= timedelta(microseconds=duration.microseconds)
            duration = f'for {duration}'
        else:
            duration = '(still open)'

        print(f'{inc_start.strftime("%a %d %b %H:%M")} {duration} - {inc["entityDisplayName"]}')
        notes = victorops.get(
            f'{args.api_host}/api-public/v1/chat',
            params={'incidentId': inc_number},
        ).json()
        for note in notes['messages']:
            text = note['text'].replace(f' #incident{inc_number}', '')
            print(f'    {note["username"]}: {text}')
        # "This API may be called a maximum of 2 times per second."
        time.sleep(0.6)

if __name__ == '__main__':
    main()
