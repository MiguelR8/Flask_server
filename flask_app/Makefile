#For now, only for certificates
all: cert

cert:
	mkdir cert
	openssl genrsa -out cert/rootkey.pem 2048
	openssl req -config dataroot -new -x509 -key cert/rootkey.pem -out cert/rootcert.pem
	openssl genrsa -out cert/clientkey.pem 2048
	openssl req -config dataclient -new -key cert/clientkey.pem -out cert/clientreq.pem
	openssl x509 -in cert/clientreq.pem -CA cert/rootcert.pem -CAkey cert/rootkey.pem -req -CAcreateserial -out cert/clientcert.pem
	openssl genrsa -out cert/serverkey.pem 2048
	openssl req -config dataserver -new -key cert/serverkey.pem -out cert/serverreq.pem
	openssl x509 -in cert/serverreq.pem -CA cert/rootcert.pem -CAkey cert/rootkey.pem -req -CAcreateserial -out cert/servercert.pem
