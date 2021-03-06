CA_USER=certd

all: setup-certificates setup-charm
	make -C CA_flask_app configure-ws
	make -C flask_app configure-ws

CA_flask_app/cert:
	mkdir -p $@
	
flask_app/cert:
	mkdir -p $@
	
client/cert:
	mkdir -p $@

CA_flask_app/cert/rootkey.pem: CA_flask_app/cert
	openssl genrsa -out $@ 4096

CA_flask_app/cert/rootcert.pem: CA_flask_app/cert/rootkey.pem CA_flask_app/config/dataroot flask_app/cert client/cert
	#Create certificate
	openssl req -config CA_flask_app/config/dataroot -new -x509 -key $< -out $@
	echo "02" > CA_flask_app/cert/rootcert.srl
	#Install it in applications' servers (place on their cert/ dir)
	cp $@ flask_app/cert/rootcert.pem
	cp $@ client/cert/rootcert.pem
	sudo chown -R $(CA_USER) CA_flask_app/cert/
	chmod a+r flask_app/cert/rootcert.pem
	chmod a+r client/cert/rootcert.pem

setup-certificates: CA_flask_app/cert/rootcert.pem

setup-charm:
	python3 -c "import charm" || (echo "Charm is not installed, go to https://jhuisi.github.io/charm/install_source.html and follow the instructions" && exit 1)
