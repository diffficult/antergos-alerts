#!/bin/python
# -*- coding: utf-8 -*-
#
# antergos-alerts.py
#
# Copyright © 2017 Antergos
#
# antergos-alerts.py is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# antergos-alerts.py is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# The following additional terms are in effect as per Section 7 of the license:
#
# The preservation of all legal notices and author attributions in
# the material or in the Appropriate Legal Notices displayed
# by works containing it is required.
#
# You should have received a copy of the GNU General Public License
# along with antergos-alerts.py; if not, see <http://www.gnu.org/licenses/>.

import json
import os
import sys
import subprocess
import gettext
import locale
from termcolor import colored, cprint


APP_NAME = 'ANTERGOS_NOTIFY'
LOCALE_DIR = '/usr/share/locale'

DOING_INSTALL = os.environ.get('CNCHI_RUNNING', False)
IS_GRAPHICAL_SESSION = os.environ.get('DISPLAY', False)
HAS_GRAPHICAL_SESSION = os.path.exists('/usr/bin/X')

ALERTS_DIR = '/var/lib/antergos-alerts'
ALERTS_JSON = '/var/lib/antergos-alerts/alerts.json'
COMPLETED_JSON = '/var/lib/antergos-alerts/completed.json'

try:
    with open(ALERTS_JSON) as data:
        ALERTS = json.loads(data.read())
except (OSError, json.JSONDecodeError):
    ALERTS = {}

try:
    with open(COMPLETED_JSON) as data:
        COMPLETED_ALERT_IDS = json.loads(data.read())
except (OSError, json.JSONDecodeError):
    COMPLETED_ALERT_IDS = []


ALERT_IDS = ALERTS.keys()


def setup_gettext()-> None:
    gettext.textdomain(APP_NAME)
    gettext.bindtextdomain(APP_NAME, LOCALE_DIR)

    try:
        locale_code, encoding = locale.getdefaultlocale()
        lang = gettext.translation(APP_NAME, LOCALE_DIR, [locale_code], None, True)
        lang.install()
    except Exception:
        pass


def get_localized_alert_message() -> tuple:
    subject = _('ATTENTION: Antergos System Message')

    part1 = _('A new Antergos Alert has been issued.')
    part2 = _('Alerts contain important information regarding your system.')
    part3 = _('You can view the alert at the following URL')

    return subject, part1, part2, part3


def print_notice_to_stdout(alert_slug: str) -> None:
    prefix = colored('*', color='red', attrs=['bold', 'blink'])

    subject, part1, part2, part3 = get_localized_alert_message()

    cprint(
        f'    =======>>> {subject} <<<=======    ',
        color='white',
        on_color='on_red',
        attrs=['bold', 'blink']
    )
    print('')
    print(f'{prefix} {part1}')
    print(f'{prefix} {part2}')
    print(f'{prefix} {part3}:')
    print('')
    print(f'{prefix} https://antergos.com/wiki/alerts/{alert_slug}')
    print('')
    cprint(
        '                                                                 ',
        color='white',
        on_color='on_red',
        attrs=['bold', 'blink']
    )


def do_alerts() -> None:
    # Filter out completed alerts
    alerts_ids = list(set(ALERT_IDS) - set(COMPLETED_ALERT_IDS))

    alerts_ids.sort()

    subject, part1, part2, part3 = get_localized_alert_message()

    environment = os.environ.copy()
    environment['ALERT_SUBJECT'] = subject
    environment['ALERT_MESSAGE'] = f'{part1} {part2} {part3}'

    for alert_id in alerts_ids:
        alert_slug = ALERTS[alert_id]

        print_notice_to_stdout(alert_slug)

        if IS_GRAPHICAL_SESSION or HAS_GRAPHICAL_SESSION:
            # Display desktop notification.
            environment['ALERT_URL'] = f'https://antergos.com/wiki/alerts/{alert_slug}'
            try:
                subprocess.run(['/usr/bin/antergos-notify.sh'], env=environment, check=True)
            except subprocess.CalledProcessError:
                pass

        COMPLETED_ALERT_IDS.append(alert_id)


if __name__ == '__main__':
    if DOING_INSTALL:
        sys.exit(0)

    setup_gettext()
    do_alerts()

    with open(COMPLETED_JSON, 'w') as data:
        data.write(json.dumps(COMPLETED_ALERT_IDS))

    sys.exit(0)
