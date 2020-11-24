#!/bin/make -f

DESTDIR ?= /

all: install

install:
	# Alerts Data
	mkdir -p $(DESTDIR)/var/lib/pacman-alerts
	cp dist/alerts.json $(DESTDIR)/var/lib/pacman-alerts

	# ALPM Hook
	mkdir -p $(DESTDIR)/usr/share/libalpm/hooks
	cp dist/pacman-alerts.hook $(DESTDIR)/usr/share/libalpm/hooks/pacman-alerts.hook

	# Logo for desktop notification
	mkdir -p $(DESTDIR)/usr/share/icons
	cp dist/onosendai.png $(DESTDIR)/usr/share/icons/onosendai.png

	# Pacman Alerts
	install -Dm755 src/pacman-alerts.py $(DESTDIR)/usr/bin/pacman-alerts

	# Utility script for desktop notifications
	install -Dm755 src/pacman-notify.sh $(DESTDIR)/usr/bin/pacman-notify

uninstall:
	# Alerts Data
	rm -f $(DESTDIR)/var/lib/pacman-alerts/alerts.json

	# ALPM Hook
	rm -f $(DESTDIR)/usr/share/libalpm/hooks/pacman-alerts.hook

	# Logo for desktop notification
	rm -f $(DESTDIR)/usr/share/icons/onosendai.png

	# Pacman Alerts
	rm -f $(DESTDIR)/usr/bin/pacman-alerts

	# Utility script for desktop notifications
	rm -f $(DESTDIR)/usr/bin/pacman-notify


.PHONY: all install uninstall
