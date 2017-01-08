from OpenSSL import crypto
import mypdfsigner
from os import sep

def getCommonName(location, issuer=False):
	'''
	Given a certiticate location (in PEM or DER format), returns the CN
	corresponding with the certified public key of this document.
	If issuer is set to True, returns the issuer's common name instead
	Throws ValueError if extension is neither .der nor .pem (case insensitive),
	or if it's not an X509 certificate
	'''
	ext = location.split(sep)[-1].split('.')[-1]
	if ext.lower() == 'der':
		ext = crypto.FILETYPE_ASN1
	elif ext.lower() == 'pem':
		ext = crypto.FILETYPE_PEM
	else:
		raise ValueError
	cn = None
	with open(location) as c:
		cert = crypto.load_certificate(ext, c.read())
		cn = cert.get_subject().CN if not issuer else cert.get_issuer().CN
	return cn