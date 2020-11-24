#!/bin/bash
#
# pacman-notify.sh
#
#
# pacman-notify is (fork) modified version of Antergos-alerts free software
#
# pacman-notify is for personal use and poorly modified and should not be redistributed
# 
# Check on the original antergos-alerts at https://github.com/Antergos/antergos-alerts

_msg="${ALERT_MESSAGE}"

if [[ -n "${ALERT_URL}" ]]; then
	_msg="${_msg}:\n\n${ALERT_URL}"
fi


maybe_display_desktop_alert() {
	if [[ -e '/usr/bin/pacman-boot' ]]; then
		# We're running on pacman-iso
		return
	fi

	_icon='/usr/share/icons/onosendai.png'
	_command="/usr/bin/notify-send -u critical -a Pacman -i ${_icon} \"${ALERT_SUBJECT}\" \"${_msg}\""
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
