VENV_HOME=$(shell readlink -f ../flask)
SERVER_URL=www.notariodigital.com
SERVER_PORT=5000
APP_NAME=app
APACHE_USER=apached
PY_EXEC=python3
export SERVER_PORT
export SERVER_URL
export APP_NAME
export APACHE_USER


cert:
	mkdir -p cert
	
req:
	openssl genrsa -out cert/serverkey.pem 2048
	openssl req -config config/dataserver -new -key cert/serverkey.pem -extensions v3_ext -out cert/serverreq.pem
	
client-req:
	openssl genrsa -out cert/clientkey.pem 2048
	openssl req -config config/dataclient -new -key cert/clientkey.pem -extensions v3_ext -out cert/clientreq.pem

#Require sysadmin to get a certificate from the CA
cert/servercert.pem: cert
	#Alert only if non-existent (and make files required to get one)
	test ! -e cert/servercert.pem && echo "A certificate must be issued from a third party to continue" && make req && exit 1 || true 

##Virtualenv and app setup
$(VENV_HOME):
	virtualenv -p $(PY_EXEC) --system-site-packages $@
	
~$(APACHE_USER):
	sudo useradd $(APACHE_USER)
	sudo passwd $(APACHE_USER)
	sudo mkdir -p ~$(APACHE_USER)/uploads
	sudo mkdir -p ~$(APACHE_USER)/certs
	sudo mkdir -p ~$(APACHE_USER)/group_keys
	sudo chown -R $(APACHE_USER) ~$(APACHE_USER)
	
app-setup: venv_setup.sh $(VENV_HOME) ~$(APACHE_USER) cert/servercert.pem
	test -e ~$(APACHE_USER)/app.db || su -c "$(PY_EXEC) db_create.py" $(APACHE_USER)
	
~$(APACHE_USER)/db_repository:
	sudo mkdir $@
	sudo chown -R $(APACHE_USER) $@

~$(APACHE_USER)/db_repository/current_version: ~$(APACHE_USER)/db_repository $(APP_NAME)/models.py
	su -c "$(PY_EXEC) db_migrate.py" $(APACHE_USER)

app-prerequisites: app-setup ~$(APACHE_USER)/db_repository/current_version /etc/apache2/sites-available/$(SERVER_URL).conf

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

##Testing
server.p12: cert/servercert.pem cert/serverkey.pem
	openssl pkcs12 -export -inkey cert/serverkey.pem -in $< -out $@
	
client.p12: cert/clientcert.pem cert/clientkey.pem
	openssl pkcs12 -export -inkey cert/clientkey.pem -in $< -out $@
	
root.p12: cert/rootcert.pem cert/rootkey.pem
	openssl pkcs12 -export -inkey cert/rootkey.pem -in $< -out $@