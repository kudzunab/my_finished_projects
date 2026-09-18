PYTHON3=../.venv/bin/python3
PROG_NAME=rogulike

.PHONY: uninstall install run

uninstall:
	cd .. && rm -rf .venv/
#	sudo rm -f /usr/local/bin/$(PROG_NAME)
#	sudo rm -rf /opt/rogulike/

install:
	cd .. && python3 -m venv .venv
	cd .. && .venv/bin/pip install -r requirements.txt
	chmod +x $(PROG_NAME)
#	sudo mkdir -p /opt/rogulike/
#	sudo cp ../requirements.txt /opt/rogulike/
#	sudo cp -r ../src /opt/rogulike/
#	sudo cp $(PROG_NAME) /opt/rogulike/src/
#	cd /opt/rogulike/ && sudo python3 -m venv .venv
#	cd /opt/rogulike/ && sudo .venv/bin/pip install -r requirements.txt
#	cd /opt/rogulike/ && sudo chmod +x src/$(PROG_NAME)
#	sudo cp /opt/rogulike/src/$(PROG_NAME) /usr/local/bin/

run:
	PYTHONPATH=.. $(PYTHON3) main.py