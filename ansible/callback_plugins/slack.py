# (C) 2014-2015, Matt Martz <matt@sivel.net>
# (C) 2017 Ansible Project
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

# Make coding more python3-ish
from __future__ import (absolute_import, division, print_function)
__metaclass__ = type

DOCUMENTATION = '''
    callback: slack
    callback_type: notification
    requirements:
      - whitelist in configuration
      - prettytable (python library)
    short_description: Sends play events to a Slack channel
    version_added: "2.1"
    description:
        - This is an ansible callback plugin that sends status updates to a Slack channel during playbook execution.
        - Before 2.4 only environment variables were available for configuring this plugin
    options:
      webhook_url:
        description: Slack Webhook URL
        env:
          - name: SLACK_WEBHOOK_URL
        ini:
          - section: callback_slack
            key: webhook_url
      username:
        description: Username to post as.
        env:
          - name: SLACK_USERNAME
        default: ansible
        ini:
          - section: callback_slack
            key: username
      ara_base_url:
        description: Base URL for ARA reports
        env:
          - name: ARA_BASE_URL
        ini:
          - section: callback_slack
            key: ara_base_url
'''

import json
import os
import uuid

try:
    from __main__ import cli
except ImportError:
    cli = None

from ansible.module_utils.parsing.convert_bool import boolean
from ansible.module_utils.urls import open_url
from ansible.plugins.callback import CallbackBase

try:
    import prettytable
    HAS_PRETTYTABLE = True
except ImportError:
    HAS_PRETTYTABLE = False

try:
    from ara import models
    from ara.webapp import create_app
    from flask import current_app
    HAS_ARA = True
except ImportError:
    HAS_ARA = False

class CallbackModule(CallbackBase):
    """This is an ansible callback plugin that sends status
    updates to a Slack channel after playbook execution.
    """
    CALLBACK_VERSION = 2.0
    CALLBACK_TYPE = 'notification'
    CALLBACK_NAME = 'slack'

    def __init__(self, display=None):
        self.disabled = False

        super(CallbackModule, self).__init__(display=display)

        if not HAS_PRETTYTABLE:
            self.disabled = True
            self._display.warning('The `prettytable` python module is not '
                                  'installed. Disabling the Slack callback '
                                  'plugin.')

        if cli:
            self._options = cli.options
        else:
            self._options = None

        self.playbook_name = None

    def set_options(self, task_keys=None, var_options=None, direct=None):
        super(CallbackModule, self).set_options(task_keys=task_keys, var_options=var_options, direct=direct)

        self.webhook_url = self.get_option('webhook_url')
        self.username = self.get_option('username')
        self.ara_base = self.get_option('ara_base_url')

        if self.webhook_url is None:
            self.disabled = True
            self._display.warning('Slack Webhook URL was not provided. The '
                                  'Slack Webhook URL can be provided using '
                                  'the `SLACK_WEBHOOK_URL` environment '
                                  'variable.')

    def send_msg(self, attachments):
        payload = {
            'username': self.username,
            'attachments': attachments,
            'parse': 'none',
            'icon_url': 'https://www.ansible.com/favicon.ico',
        }

        data = json.dumps(payload)
        self._display.debug(data)
        self._display.debug(self.webhook_url)
        try:
            response = open_url(self.webhook_url, data=data, method='POST')
            return response.read()
        except Exception as e:
            self._display.warning('Could not submit message to Slack: %s' %
                                  str(e))

    def v2_playbook_on_start(self, playbook):
        self.playbook_name = os.path.basename(playbook._file_name)
        if self._options and self._options.tags != ['all']:
            self.playbook_name = '{} --tags {}'.format(self.playbook_name, ','.join(self._options.tags))

    def v2_playbook_on_stats(self, stats):
        hosts = sorted(stats.processed.keys())

        t = prettytable.PrettyTable(['Host', 'Changed', 'Unreachable', 'Failed'])

        failures = False
        unreachable = False
        changes = False

        for h in hosts:
            s = stats.summarize(h)

            if s['failures'] > 0:
                failures = True
            if s['unreachable'] > 0:
                unreachable = True
            if s['changed'] > 0:
                changes = True

            t.add_row([h] + [s[k] for k in ['changed', 'unreachable',
                                            'failures']])

        if not unreachable and not failures:
            return

        attachments = []
        msg_items = []

        if failures or unreachable:
            color = 'danger'
            msg_items.append('*PLAYBOOK FAILED* | %s' % (self.playbook_name))
        else:
            color = 'good'
            msg_items.append('*PLAYBOOK SUCCEEDED* | %s' % (self.playbook_name))

        msg_items.append('```\n%s\n```' % t)

        if HAS_ARA and self.ara_base:
            app = create_app()
            if not current_app:
                context = app.app_context()
                context.push()
            playbook_id = current_app._cache['playbook']
            db_file = os.path.basename(current_app.config.get('ARA_DATABASE'))
            db_file = db_file.replace('.sqlite', '')
            msg_items.append('<{}/{}/ara-report/reports/{}.html|Detailed report>'.format(self.ara_base, db_file, playbook_id))

        msg = '\n'.join(msg_items)

        attachments.append({
            'fallback': msg,
            'fields': [
                {
                    'value': msg
                }
            ],
            'color': color,
            'mrkdwn_in': ['text', 'fallback', 'fields']
        })

        self.send_msg(attachments=attachments)
