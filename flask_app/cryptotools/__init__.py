from OpenSSL import crypto
import mypdfsigner
from os import sep

def getX509FromFile(location):
	ext = location.split(sep)[-1].split('.')[-1]
	ext = crypto.FILETYPE_PEM if ext.lower() == 'pem' else crypto.FILETYPE_ASN1
	with open(location) as c:
		cert = crypto.load_certificate(ext, c.read())
	return cert
	
def getPKeyFromFile(location, passphrase=None):
	ext = location.split(sep)[-1].split('.')[-1]
	ext = crypto.FILETYPE_PEM if ext.lower() == 'pem' else crypto.FILETYPE_ASN1
	with open(location) as c:
		if passphrase:
			pkey = crypto.load_privatekey(ext, c.read(), passphrase)
		else:
			pkey = crypto.load_privatekey(ext, c.read())
	return pkey

def getCommonName(location, issuer=False):
	'''
	Given a certiticate location (in PEM or DER format), returns the CN
	corresponding with the certified public key of this document.
	If issuer is set to True, returns the issuer's common name instead
	Throws ValueError if extension is neither .der nor .pem (case insensitive),
	or if it's not an X509 certificate
	'''
	
	cert = getX509FromFile(location)
	return cert.get_subject().CN if not issuer else cert.get_issuer().CN
	


#Can only verify pdf, would need to try certificates one by one or store as metadata	
#def getPDFSigner(pdf_file):
#	