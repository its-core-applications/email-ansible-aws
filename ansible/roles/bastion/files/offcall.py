#!/usr/bin/env python3

import botocore.session
import json
import os
import requests
import time

from base64 import b64encode
from datetime import datetime, timedelta, timezone


api_host = 'https://api.opsgenie.com'
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

# Now we can get the API key
api_key = requests.get(
    f'{vault_addr}/v1/secret/opsgenie/api',
    json={'ttl': '15m'},
    headers={'Authorization': f'Bearer {vault_token}'},
).json()['data']['apikey']

# And then we can build the list of alerts
opsgenie = requests.Session()
opsgenie.headers.update({'Authorization': f'GenieKey {api_key}'})

alerts = []
start_time = int((datetime.now() - timedelta(days=7)).timestamp() * 1000)
res = opsgenie.get(
    f'{api_host}/v2/alerts',
    params={
        'query': f'createdAt > {start_time}',
        'limit': 100,
    },
).json()
alerts.extend(res['data'])
while 'next' in res['paging']:
    res = opsgenie.get(res['paging']['next']).json()
    alerts.extend(res['data'])

print(f'Total Alerts: {len(alerts)}\n')

# Iterate over the alerts and print them
for alert in reversed(alerts):
    alert_details = opsgenie.get(f'{api_host}/v2/alerts/{alert["id"]}').json()['data']
    # fromisoformat() doesn't support full ISO format until Python 3.11, so we
    # need to mangle it.
    alert_start = datetime.fromisoformat(alert['createdAt'].split('.')[0])
    alert_start = alert_start.replace(tzinfo=timezone.utc).astimezone().strftime('%a %d %b %H:%M')

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
        if key in alert_details['details']:
            output = alert_details['details'][key]
            break
    output = output.splitlines()[0]

    print(f'{alert_start} {alert_duration} - {alert["alias"]} - {output}')
    time.sleep(0.1)
