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

data = open(os.path.normpath('../dist/alerts.json')).read()
ALERTS = json.loads(data)
ALERT_IDS = ALERTS.keys()

COMPLETED_ALERT_IDS = []  #json.loads('/var/cache/antergos-alerts/completed.json')


def setup_gettext()-> None:
    gettext.textdomain(APP_NAME)
    gettext.bindtextdomain(APP_NAME, LOCALE_DIR)

    try:
        locale_code, encoding = locale.getdefaultlocale()
        lang = gettext.translation(APP_NAME, LOCALE_DIR, [locale_code], None, True)
        lang.install()
    except Exception:
        pass


def print_notice_to_stdout(alert_slug: str) -> None:
    prefix = colored('*', color='red', attrs=['bold', 'blink'])
    subject = _('ATTENTION: Antergos System Message')

    part1 = _('A new Antergos Alert has been issued.')
    part2 = _('Alerts contain important information regarding your system.')
    part3 = _('You can view the alert at the following URL')

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


if __name__ == '__main__':
    doing_install = os.environ.get('CNCHI_RUNNING', False)
    is_graphical_session = os.environ.get('DISPLAY', False)

    # Filter out completed alerts
    ALERT_IDS = list(set(ALERT_IDS) - set(COMPLETED_ALERT_IDS))
    # Sort by date
    ALERT_IDS.sort()

    setup_gettext()

    for alert_id in ALERT_IDS:
        alert = ALERTS[alert_id]

        print_notice_to_stdout(alert)

        if is_graphical_session and not doing_install:
            # Display desktop notification.
            try:
                subprocess.check_call(['./antergos-notify.sh', alert])
            except subprocess.CalledProcessError:
                pass
