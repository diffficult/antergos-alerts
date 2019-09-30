/bin/make -f

DESTDIR ?= /

all: install

install:
	# Alerts Data
	mkdir -p $(DESTDIR)/var/lib/antergos-alerts
	cp dist/alerts.json $(DESTDIR)/var/lib/antergos-alerts

	# ALPM Hook
	mkdir -p $(DESTDIR)/usr/share/libalpm/hooks
	cp dist/antergos-alerts.hook $(DESTDIR)/usr/share/libalpm/hooks/antergos-alerts.hook

	# Logo for desktop notification
	mkdir -p $(DESTDIR)/usr/share/antergos
	cp dist/onosendai.png $(DESTDIR)/usr/share/icons/onosendai.png

	# Antergos Alerts
	install -Dm755 src/antergos-alerts.py $(DESTDIR)/usr/bin/antergos-alerts

	# Utility script for desktop notifications
	install -Dm755 src/antergos-notify.sh $(DESTDIR)/usr/bin/antergos-notify

uninstall:
	# Alerts Data
	rm -f $(DESTDIR)/var/lib/antergos-alerts/alerts.json

	# ALPM Hook
	rm -f $(DESTDIR)/usr/share/libalpm/hooks/antergos-alerts.hook

	# Logo for desktop notification
	rm -f $(DESTDIR)/usr/share/icons/onosendai.png

	# Antergos Alerts
	rm -f $(DESTDIR)/usr/bin/antergos-alerts

	# Utility script for desktop notifications
	rm -f $(DESTDIR)/usr/bin/antergos-notify


.PHONY: all install uninstall
