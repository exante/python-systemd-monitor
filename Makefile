.PHONY: all deb clean

all: deb

deb: clean
	fpm -s python -t deb \
		-d python-dbus \
		-d systemd \
		setup.py

clean:
	rm -rf *.deb build dist src/systemd_monitor.egg-info
	find . -name "*.pyc" -exec rm -rf {} \;
