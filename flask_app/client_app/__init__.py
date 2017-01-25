from OpenSSL import crypto
import mypdfsigner
import os
import json
from cryptotools import getX509FromFile, getPKeyFromFile

#In case a configuration file is not provided, this function
#can produce segfaults on crowded stacks due to to length of its
#return argument (see the pkcs12 object dump)
	
def get_conf(conf_location = None, pfx_password = None,
	pfx_location = None, pkey_location = None, cert_location = None,
	cacerts_locations = None):
	
	if conf_location is None:
		if pfx_location is None:
			if (pkey_location and cert_location) is None:
				raise Exception('Not enough arguments')
			pfx = create_pfx(pkey_location, cert_location,
				cacerts = cacerts_locations, passphrase = pfx_password)
		else:
			with open(pfx_location, 'rb') as f:
				pfx = f.read()
		
		#(g, conf_location) = mkstemp(text=True)
		#g.close()
		if pfx_password is None:
			raise Exception('Password needed for PFX')
		
		return json.dumps({'certstore' : 'PKCS12 KEYSTORE FILE',
			'tsaurl' : 'http://adobe-timestamp.geotrust.com/tsa',
			'certfile' : pfx.encode('base64'),
			'certpasswd' : pfx_password})
	return conf_location

#Missing attributes in the p12 compared to the test p12 (see RFC 3280 for insight on these)
#	Certificate extension: 'authorityKeyIdentifier' (keyid, Dirname, serial) (omissible only for self-signed CAs)

#Check notAfter (expiration) date and update if outdated

		
def create_pfx(pkey_location, cert_location, cacerts = None,
	friendlyname = None, passphrase = None):
	
	p12 = crypto.PKCS12()
	
	p12.set_certificate(getX509FromFile(cert_location))
	p12.set_privatekey(getPKeyFromFile(pkey_location))
	if cacerts:
		x509s = [getX509FromFile(i) for i in cacerts]
		p12.set_ca_certificates(x509s)
	p12.set_friendlyname(friendlyname)
	
	return p12.export(passphrase)

def sign_pdf(src_location, dst_location, conf):
	
	if os.path.realpath(src_location) == os.path.realpath(dst_location):
		raise ValueError('Source and destination must be different')
	
	return mypdfsigner.sign(src_location, dst_location, '', '', '', False, False, True,
		conf)
	