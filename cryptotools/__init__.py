from OpenSSL import crypto
#import mypdfsigner
from os import sep
import subprocess
#import requests
#from datetime import datetime, timedelta

def getCryptoExt(file_ext):
	if file_ext.lower() == 'der':
		return crypto.FILETYPE_ASN1
	elif file_ext.lower() == 'pem':
		return crypto.FILETYPE_PEM
	return None

def getX509FromFile(location):
	ext = getCryptoExt(location.split(sep)[-1].split('.')[-1])
	
	with open(location) as c:
		cert = crypto.load_certificate(ext, c.read())
	return cert
	
def getPKeyFromFile(location, passphrase=None):
	ext = getCryptoExt(location.split(sep)[-1].split('.')[-1])

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
	Throws ValueError if it's not an X509 certificate
	'''
	
	cert = getX509FromFile(location)
	return cert.get_subject().CN if not issuer else cert.get_issuer().CN

#~ def parseX509ConfigOpt(line):
	#~ ret = []
	#~ for val in text.split('=')[1].split(','):
		#~ d = val.split(':')
		#~ ret.append({d[0]:d[1]} if len (d) > 1 else d[0])

#~ def loadFromBytes(file_bytes, file_ext, obj_type='cert'):
	#~ ext = getCryptoExt(file_ext)
	#~ if ext is None:
		#~ return None
	
	#~ try:
		#~ if obj_type == 'cert':
			#~ return crypto.load_certificate(ext, file_bytes)
		#~ if obj_type == 'req':
			#~ return crypto.load_certificate_request(ext, file_bytes)
	#~ except:
		#~ pass
	#~ return None

#~ def isValidReq(req, file_ext):
	#~ ok = True	#allow for extra validation on the req object in the future
	#~ if ok:
		#~ for e in req.get_extensions():
			#~ l = parseX509ConfigOpt(e.get_data())
			#~ for val in l:
				#~ try:	#Validators for options with values
					#~ k = val.keys()[0]	#option name
					#~ v = val[k]			#value
					#~ if k == 'CA' and v.lower() == 'true':
						#~ return False
				#~ except AttributeError:
					#~ pass
	#~ return ok

def getX509FromReq(req_location, CA_cert_location, CA_key_location, dest_location):
	ext = getCryptoExt(dest_location.split('.')[-1])
	
	command = ['openssl', 'x509', '-in', req_location, '-CA', CA_cert_location,
			'-CAkey', CA_key_location, '-req', '-CAcreateserial',
			'-out', dest_location]
		
	try:
		subprocess.check_output(command, stderr= subprocess.STDOUT)
	except subprocess.CalledProcessError as e:
		from getpass import getuser
		raise ValueError(e.output)
	with open(dest_location) as f:
		return crypto.load_certificate(ext, f.read())
	
	#rootCert = getX509FromFile(CA_cert_location)
	#
	#cert = crypto.X509()
	#cert.set_issuer(rootCert.get_issuer())
	#today = datetime.now()
	#cert.set_notBefore(today.strftime('%Y%m%d%H%M%SZ'))						#Must be YYYYMMDDhhmmssZ
	#cert.set_notAfter((today + timedelta(60)).strftime('%Y%m%d%H%M%SZ'))
	
#See: http://requests.readthedocs.io/en/master/user/advanced/#advanced
#~ def do_request(method, url, CA_cert=None, client_cert=None, client_key=None):
	#~ method_dict = {'GET': requests.get, 'POST': requests.post}
	
	#~ if client_cert:
		#~ if client_key:
			#~ cert = (client_cert, client_key)
		#~ else:
			#~ cert = client_cert
	#~ else:
		#~ cert = None
	
	#~ verify = CA_cert if CA_cert else False
	
	#~ if cert == None:
		#~ return method_dict[method.upper()](url, cert=cert)
	#~ else:
		#~ return method_dict[method.upper()](url, verify=verify, cert=cert )
