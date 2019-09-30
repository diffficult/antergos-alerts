#!/bin/python
# -*- coding: utf-8 -*-
#
# antergos-alerts.py
#
# Copyright © 2017-2018 Antergos
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
import subprocess
import gettext
import locale
from termcolor import colored, cprint


class AntergosAlerts(object):
    """ Manages antergos alerts """
    APP_NAME = 'ANTERGOS_NOTIFY'
    LOCALE_DIR = '/usr/share/locale'

    DOING_INSTALL = os.environ.get('CNCHI_RUNNING', False)
    IS_GRAPHICAL_SESSION = os.environ.get('DISPLAY', False)
    HAS_GRAPHICAL_SESSION = os.path.exists('/usr/bin/X')

    ALERTS_DIR = '/var/lib/antergos-alerts'
    ALERTS_JSON = '/var/lib/antergos-alerts/alerts.json'
    COMPLETED_JSON = '/var/lib/antergos-alerts/completed.json'

    def __init__(self):
        """ Initialization """
        if not self.IS_GRAPHICAL_SESSION and 'pamac (Linux x86_64)' in os.environ.values():
            AntergosAlerts.IS_GRAPHICAL_SESSION = True
            os.environ['USER'] = 'root'

        try:
            result = subprocess.run(['uname', '-m'], universal_newlines=True, stdout=subprocess.PIPE)
            self.is_32bit = 'x86_64' not in result.stdout
        except (OSError, subprocess.CalledProcessError) as _err:
            self.is_32bit = False

        try:
            with open(AntergosAlerts.ALERTS_JSON) as data:
                self.alerts = json.loads(data.read())
        except (OSError, json.JSONDecodeError):
            self.alerts = {}

        try:
            with open(AntergosAlerts.COMPLETED_JSON) as data:
                self.completed_alert_ids = json.loads(data.read())
        except (OSError, json.JSONDecodeError):
            self.completed_alert_ids = []

        self.alert_ids = self.alerts.keys()

    def run(self):
        """ Runs program """
        self.setup_gettext()

        if os.environ.get('RECOMMEND_REBOOT', False):
            self.maybe_recommend_reboot()
        else:
            self.do_alerts()
            self.save_completed_alerts()

    @staticmethod
    def setup_gettext()-> None:
        """ Initialize gettext for string translations """
        try:
            gettext.textdomain(AntergosAlerts.APP_NAME)
            gettext.bindtextdomain(AntergosAlerts.APP_NAME, AntergosAlerts.LOCALE_DIR)

            locale_code, _encoding = locale.getdefaultlocale()
            lang = gettext.translation(AntergosAlerts.APP_NAME, AntergosAlerts.LOCALE_DIR, [locale_code], None, True)
            lang.install()
        except Exception:
            pass

    @staticmethod
    def get_localized_alert_message() -> tuple:
        """ Obtain localized version of a generic alert message """
        try:
            _()
        except NameError:
            _ = lambda message: message

        subject = _('ACHTUNG! ONO SENDAI Terminal Message')

        part1 = _('A new Alert has been issued.')
        part2 = _('Alerts contain important information regarding your system.')
        part3 = _('You can view the alert at the following URL')

        return subject, part1, part2, part3

    @classmethod
    def get_localized_reboot_recommended_message(cls) -> tuple:
        """ Obtain localized version of system reboot recommended message """
        try:
            _()
        except NameError:
            _ = lambda message: message

        generic_msg_parts = cls.get_localized_alert_message()
        subject = generic_msg_parts[0]

        part1 = _('At least one core system package has been updated.')
        part2 = _('To ensure system stability, a reboot is recommended.')

        return subject, part1, part2

    @classmethod
    def maybe_recommend_reboot(cls) -> None:
        if cls.DOING_INSTALL or not cls.IS_GRAPHICAL_SESSION:
            return

        subject, part1, part2 = cls.get_localized_reboot_recommended_message()

        environment = os.environ.copy()
        environment['ALERT_SUBJECT'] = subject
        environment['ALERT_MESSAGE'] = f'{part1} {part2}'

        # Display desktop notification.
        try:
            subprocess.run(['/usr/bin/antergos-notify'], env=environment, check=True)
        except subprocess.CalledProcessError:
            pass

    def print_notice_to_stdout(self, alert_slug: str) -> None:
        """ Show alert to the user (stdout) """
        prefix = colored('*', color='red', attrs=['bold', 'blink'])

        subject, part1, part2, part3 = self.get_localized_alert_message()

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

    def do_alerts(self) -> None:
        """ Show alerts to user (stdout and notify) """
        # Filter out completed alerts
        alerts_ids = list(set(self.alert_ids) - set(self.completed_alert_ids))

        alerts_ids.sort()

        subject, part1, part2, part3 = self.get_localized_alert_message()

        environment = os.environ.copy()
        environment['ALERT_SUBJECT'] = subject
        environment['ALERT_MESSAGE'] = f'{part1} {part2} {part3}'

        for alert_id in alerts_ids:
            alert_slug = self.alerts[alert_id]

            if AntergosAlerts.DOING_INSTALL:
                self.completed_alert_ids.append(alert_id)
                continue

            if 'i686' in alert_slug and not self.is_32bit:
                self.completed_alert_ids.append(alert_id)
                continue

            self.print_notice_to_stdout(alert_slug)

            if AntergosAlerts.IS_GRAPHICAL_SESSION:
                # Display desktop notification.
                environment['ALERT_URL'] = f'https://antergos.com/wiki/alerts/{alert_slug}'
                try:
                    subprocess.run(['/usr/bin/antergos-notify'], env=environment, check=True)
                except subprocess.CalledProcessError:
                    pass

            self.completed_alert_ids.append(alert_id)

    def save_completed_alerts(self):
        """ Store already shown alerts """
        try:
            with open(AntergosAlerts.COMPLETED_JSON, 'w') as json_data:
                json_data.write(json.dumps(self.completed_alert_ids))
        except PermissionError as _err:
            print(_("root privileges are needed to store which alerts have already been shown"))


if __name__ == '__main__':
    AntergosAlerts().run()
