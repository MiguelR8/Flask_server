VENV_HOME=$(shell readlink -f ../flask)
SERVER_URL=www.notariodigital.com
SERVER_PORT=5000
APP_NAME=app
APACHE_USER=apached

#Make self-signed CA, and certificate with key bundled for client or server
cert: config/dataroot config/dataserver config/dataclient
	mkdir -p cert
	openssl genrsa -out cert/rootkey.pem 2048
	openssl req -config config/dataroot -new -x509 -key cert/rootkey.pem -out cert/rootcert.pem
	openssl genrsa -out cert/clientkey.pem 2048
	openssl req -config config/dataclient -new -key cert/clientkey.pem -out cert/clientreq.pem
	openssl x509 -in cert/clientreq.pem -CA cert/rootcert.pem -CAkey cert/rootkey.pem -req -CAcreateserial -extfile config/dataclient -extensions v3_ext -out cert/clientcert.pem
	openssl genrsa -out cert/serverkey.pem 2048
	openssl req -config config/dataserver -new -key cert/serverkey.pem -out cert/serverreq.pem
	openssl x509 -in cert/serverreq.pem -CA cert/rootcert.pem -CAkey cert/rootkey.pem -req -CAcreateserial -extfile config/dataserver -extensions v3_ext -out cert/servercert.pem

##Virtualenv and app setup
$(VENV_HOME):
	virtualenv --system-site-packages $@
	
~$(APACHE_USER):
	sudo useradd $(APACHE_USER)
	sudo passwd $(APACHE_USER)
	sudo mkdir -p ~$(APACHE_USER)/uploads
	sudo mkdir -p ~$(APACHE_USER)/certs
	sudo chown -R apached ~apached
	
app-setup: venv_setup.sh additional_config.sh $(VENV_HOME) ~$(APACHE_USER) cert
	sudo sh venv_setup.sh
	sh additional_config.sh ~$(APACHE_USER) $(APACHE_USER)

~$(APACHE_USER)/db_repository/current_version: $(APP_NAME)/models.py
	su -c "python db_migrate.py" $(APACHE_USER)

app-prerequisites: app-setup ~$(APACHE_USER)/db_repository/current_version

/etc/apache2/sites-available/$(SERVER_URL).conf:
	python config/get_apache_conf.py
	sudo mv $(SERVER_URL).conf /etc/apache2/sites-available/$(SERVER_URL).conf
	
## Apache setup (v2.4+)
configure-ws: app-prerequisites start-ws
	sudo a2dissite $(SERVER_URL)
	export SERVER_PORT
	export SERVER_URL
	export APP_NAME
	export APACHE_USER
	make /etc/apache2/sites-available/$(SERVER_URL).conf
	sudo a2ensite $(SERVER_URL)
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
