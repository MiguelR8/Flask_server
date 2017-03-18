VENV_HOME=$(shell readlink -f ../CA_flask)
SERVER_URL=www.omnisign.com
SERVER_PORT=5001
APP_NAME=cert_app
APACHE_USER=certd
PY_EXEC=python3
export SERVER_PORT
export SERVER_URL
export APP_NAME
export APACHE_USER

##Virtualenv and app setup
$(VENV_HOME):
	virtualenv -p $(PY_EXEC) $@
	
~$(APACHE_USER):
	sudo useradd $(APACHE_USER)
	sudo passwd $(APACHE_USER)
	sudo mkdir -p ~$(APACHE_USER)/reqs
	sudo mkdir -p ~$(APACHE_USER)/certs
	sudo chown -R $(APACHE_USER) ~$(APACHE_USER)
	
app-setup: venv_setup.sh $(VENV_HOME) ~$(APACHE_USER)
	sudo -H sh venv_setup.sh
	
~$(APACHE_USER)/%:
	sudo mkdir $@
	sudo chown -R $(APACHE_USER) $@

app-prerequisites: app-setup /etc/apache2/sites-available/$(SERVER_URL).conf

/etc/apache2/sites-available/$(SERVER_URL).conf: config/get_apache_conf.py
	$(PY_EXEC) config/get_apache_conf.py
	sudo mv $(SERVER_URL).conf /etc/apache2/sites-available/$(SERVER_URL).conf
	
## Apache setup (v2.4+)
configure-ws: app-prerequisites start-ws
	sudo service apache2 reload

start-ws:
	sudo a2ensite $(SERVER_URL)
	sudo service apache2 reload
shutdown-ws:
	sudo a2dissite $(SERVER_URL)
	sudo service apache2 reload