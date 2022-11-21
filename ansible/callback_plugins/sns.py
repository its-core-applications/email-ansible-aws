# (C) 2014-2015, Matt Martz <matt@sivel.net>
# (C) 2017 Ansible Project
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import (absolute_import, division, print_function)
__metaclass__ = type

DOCUMENTATION = '''
    callback: sns
    callback_type: notification
    requirements:
      - prettytable (python library)
    short_description: Sends play events to SNS
    description:
        - This is an ansible callback plugin that sends status updates to SNS
    options:
      sns_topic:
        description: SNS topic name or ARN
        env:
          - name: SNS_TOPIC
        ini:
          - section: callback_sns
            key: topic
      sns_region:
        description: Region for SNS
        env:
          - name: SNS_REGION
        ini:
          - section: callback_sns
            key: region
      ara_base_url:
        description: Base URL for ARA reports
        env:
          - name: ARA_BASE_URL
        ini:
          - section: callback_sns
            key: ara_base_url
'''

import json
import os
import socket

import boto3

from ansible.plugins.callback import CallbackBase

try:
    import prettytable
    HAS_PRETTYTABLE = True
except ImportError:
    HAS_PRETTYTABLE = False

try:
    from ara.clients import utils as ara_client_utils
    HAS_ARA = True
except ImportError:
    HAS_ARA = False


class CallbackModule(CallbackBase):
    """This is an ansible callback plugin that sends status
    updates to a Slack channel after playbook execution.
    """
    CALLBACK_VERSION = 2.0
    CALLBACK_TYPE = 'notification'
    CALLBACK_NAME = 'sns'

    def __init__(self, display=None):
        self.disabled = False

        super(CallbackModule, self).__init__(display=display)

        if not HAS_PRETTYTABLE:
            self.disabled = True
            self._display.warning('The `prettytable` python module is not '
                                  'installed. Disabling the SNS callback '
                                  'plugin.')

        try:
            from ansible import context
            self.cli_options = {key: value for key, value in context.CLIARGS.items()}
        except ImportError:
            try:
                from __main__ import cli
                self.cli_options = cli.options.__dict__
            except ImportError:
                self.cli_options = {}

        self.playbook_name = None

    def set_options(self, **kwargs):
        super(CallbackModule, self).set_options(**kwargs)

        self.ara_base = self.get_option('ara_base_url')
        if self.ara_base:
            self.ara_base = self.ara_base.rstrip('/')

        self.sns_topic = self.get_option('sns_topic')
        if self.sns_topic is None:
            self.disabled = True
            self._display.warning('No SNS topic set.')
        self.sns_region = self.get_option('sns_region')

    def v2_playbook_on_start(self, playbook):
        self.playbook_name = os.path.basename(playbook._file_name)
        tags = self.cli_options.get('tags')
        if tags and set(tags) != set(['all']):
            self.playbook_name = '{} --tags {}'.format(self.playbook_name, ','.join(tags))

    def v2_playbook_on_play_start(self, play):
        self.playbook_uuid = play._uuid

    def v2_playbook_on_stats(self, stats):
        hosts = sorted(stats.processed.keys())

        t = prettytable.PrettyTable(['Host', 'Changed', 'Unreachable', 'Failed'])

        failures = False

        for h in hosts:
            s = stats.summarize(h)

            if (s['failures'] > 0) or (s['unreachable'] > 0):
                failures = True

            t.add_row([h] + [s[k] for k in ['changed', 'unreachable',
                                            'failures']])

        if not failures:
            return

        subject = '{}/{} - ALERT - {} FAILED'.format(
            os.environ.get('AWS_STATUS', 'prod'),
            os.environ.get('AWS_DEFAULT_REGION', 'unknown'),
            self.playbook_name,
        )

        msg_default = str(t)
        msg_lambda = '```\n{}\n```'.format(msg_default)

        if HAS_ARA and self.ara_base:
            client = ara_client_utils.active_client()
            play = client.get('/api/v1/plays?uuid={}'.format(self.playbook_uuid))
            playbook_id = play['results'][0]['playbook']
            ara_url = '{}/playbooks/{}.html'.format(
                self.ara_base,
                playbook_id,
            )
            msg_default += '\n{}'.format(ara_url)
            msg_lambda += '\n<{}|Detailed report>'.format(ara_url)

        msg = {
            'default': msg_default,
            'sms': subject,
            'lambda': json.dumps({
              'sourcetype': 'ansible',
              'source': socket.gethostname(),
              'message': msg_lambda,
            })
        }

        boto3.setup_default_session(profile_name='sns')
        client = boto3.client('sns', region_name=self.sns_region)
        if ':' in self.sns_topic:
            arn = self.sns_topic
        else:
            topics = client.list_topics()
            for t in topics['Topics']:
                if t['TopicArn'].endswith(':' + self.sns_topic):
                    arn = t['TopicArn']

        client.publish(
            TopicArn=arn,
            Message=json.dumps(msg),
            MessageStructure='json',
            Subject=subject,
        )
