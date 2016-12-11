FLASK_BIN_PATH=$(shell readlink -f ../flask/bin)
FLASK_PYTHON_PATH=$(shell readlink -f ../flask/lib/$(shell ls ../flask/lib/ | grep python)/site-packages)
VENV_HOME=$(shell readlink -f ../flask)
SERVER_URL=www.notariodigital.com
SERVER_PORT=5000
APP_NAME=app
APACHE_USER=apached
CERTPATH=cert

#Make self-signed CA, and certificate with key bundled for client or server
all: cert

cert: dataroot dataserver dataclient
	mkdir -p cert
	openssl genrsa -out $(CERTPATH)/rootkey.pem 2048
	openssl req -config dataroot -new -x509 -key $(CERTPATH)/rootkey.pem -out $(CERTPATH)/rootcert.pem
	openssl genrsa -out $(CERTPATH)/clientkey.pem 2048
	openssl req -config dataclient -new -key $(CERTPATH)/clientkey.pem -out $(CERTPATH)/clientreq.pem
	openssl x509 -in $(CERTPATH)/clientreq.pem -CA $(CERTPATH)/rootcert.pem -CAkey $(CERTPATH)/rootkey.pem -req -CAcreateserial -out $(CERTPATH)/clientcert.pem
	openssl genrsa -out $(CERTPATH)/serverkey.pem 2048
	openssl req -config dataserver -new -key $(CERTPATH)/serverkey.pem -out $(CERTPATH)/serverreq.pem
	openssl x509 -in $(CERTPATH)/serverreq.pem -CA $(CERTPATH)/rootcert.pem -CAkey $(CERTPATH)/rootkey.pem -req -CAcreateserial -out $(CERTPATH)/servercert.pem

##Virtualenv setup
$(VENV_HOME):
	virtualenv $@

app-prerequisites: $(VENV_HOME) cert
	sh venv_setup.sh
	
## Apache setup (v2.4+)
configure-ws: app-prerequisites
	a2dissite $(SERVER_URL)
	python -c "print \"\"\"\
	Listen $(SERVER_PORT)\n\
	LoadModule ssl_module modules/mod_ssl.so\n\n\
	WSGIPythonPath $(shell pwd):$(FLASK_PYTHON_PATH)\n\
	\n\
	<VirtualHost *:$(SERVER_PORT)>\n\
		ServerName $(SERVER_URL)\n\
		ServerAlias $(APP_NAME)\n\
		SSLEngine on\n\
		SSLCertificateFile "$(shell readlink -f $(CERTPATH))/servercert.pem"\n\
		SSLCertificateKeyFile "$(shell readlink -f $(CERTPATH))/serverkey.pem"\n\
	\n\
		WSGIDaemonProcess $(APP_NAME) user=$(APACHE_USER) group=$(APACHE_USER) threads=5 python-path=$(shell pwd):$(FLASK_PYTHON_PATH)\n\
		WSGIScriptAlias / $(shell pwd)/$(APP_NAME).wsgi\n\
	\n\
		CustomLog /home/$(APACHE_USER)/$(SERVER_URL)-log common\n\
		ErrorLog /home/$(APACHE_USER)/$(SERVER_URL)-error-log\n\
		LogLevel info\n\
	\n\
		<Directory $(shell pwd)>\n\
			WSGIProcessGroup $(APP_NAME)\n\
			WSGIApplicationGroup %{GLOBAL}\n\
			WSGIScriptReloading On\n\
			<Files app.wsgi>\n\
				Require all granted\n\
			</Files>\n\
		</Directory>\n\
	</VirtualHost>\"\"\"" > /etc/apache2/sites-available/$(SERVER_URL).conf
	a2ensite $(SERVER_URL)
	service apache2 reload
	
shutdown-ws:
	a2dissite $(SERVER_URL)
	service apache2 reload