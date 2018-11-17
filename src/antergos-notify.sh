#!/bin/bash
#
# antergos-notify.sh
#
# Copyright © 2016-2017 Antergos
#
# antergos-notify is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# antergos-notify is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with antergos-notify; if not, see <http://www.gnu.org/licenses/>.

_msg="${ALERT_MESSAGE}"

if [[ -n "${ALERT_URL}" ]]; then
	_msg="${_msg}:\n\n${ALERT_URL}"
fi


maybe_display_desktop_alert() {
	if [[ -e '/usr/bin/pacman-boot' ]]; then
		# We're running on antergos-iso
		return
	fi

	_icon='/usr/share/antergos/new-logo-square32.png'
	_command="/usr/bin/notify-send -u critical -a Antergos -i ${_icon} \"${ALERT_SUBJECT}\" \"${_msg}\""
	_addr='DBUS_SESSION_BUS_ADDRESS'

	_processes=($(ps aux | grep '[d]bus-daemon --session' | awk '{print $2}' | xargs))

	for _i in $(seq 1 ${#_processes[@]}); do
		_pid="${_processes[(_i - 1)]}"
		_user=$(ps axo user:32,pid | grep "${_processes[(_i - 1)]}" | awk '{print $1}' | xargs)
		_dbus="$(grep -z ${_addr} /proc/${_pid}/environ 2>/dev/null | tr '\0' '\n' | sed -e s/${_addr}=//)"

		[[ -z "${_dbus}" ]] && continue

		DBUS_SESSION_BUS_ADDRESS="${_dbus}" DISPLAY=":0" su "${_user}" -c "${_command}"
	done
}

maybe_display_desktop_alert

exit 0
