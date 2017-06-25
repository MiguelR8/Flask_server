from OpenSSL import crypto
from os import sep
import subprocess
#import requests
#from datetime import datetime, timedelta
from cryptography.hazmat.primitives import serialization
from hashlib import sha512
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.asymmetric import padding
from cryptography.hazmat.backends import default_backend
from cryptography import x509
import base64

from charm.schemes.pksig.pksig_boyen import Boyen
from charm.core.engine.util import objectToBytes, bytesToObject
from charm.toolbox.pairinggroup import PairingGroup


##X.509 utilities
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

## Standard hash

'''
Returns the a string representing the hash of the specified object in ASCII85 format.
If isFile is True and the passed object is a string, treats it like a file path
and hashes the file's bytes
'''
def hash_object(path_or_bytes, isFile=False):
	if isFile and type(path_or_bytes) == str:
		with open(path_or_bytes, 'rb') as f:
			obj_bytes = f.read()
	elif type(path_or_bytes) == str:
		obj_bytes = path_or_bytes.encode()
	else:
		obj_bytes = path_or_bytes
	return base64.a85encode(sha512(obj_bytes).digest()).decode()

##Public key schemes

#RSA

#With PEM key and SHA512 hashing and padding only
def encrypt_hash(message, k_path, password = None):
	#load pkey
	with open(k_path, 'rb') as key_file:
		private_key = serialization.load_pem_private_key(
			key_file.read(),
			password = password,
			backend = default_backend()
		)
	
	#encrypt hash
	signer = private_key.signer (
		padding.PSS (
			mgf = padding.MGF1(hashes.SHA512()),
			salt_length = padding.PSS.MAX_LENGTH
		),
		hashes.SHA512()
	)
	signer.update(message.encode())
	return base64.a85encode(signer.finalize()).decode()
	
#With PEM key and SHA512 hashing and padding only
#raises InvalidSignature on validation failure
#Note: expects an ascii85 string as digest, not bytes
def verify_hash(digest, signature, k_bytes):
	#load pkey
	public_key = serialization.load_pem_public_key(
		k_bytes,
		backend = default_backend()
	)
	#verify signature
	verifier = public_key.verifier (
		base64.a85decode(signature.encode()),
		padding.PSS (
			mgf = padding.MGF1(hashes.SHA512()),
			salt_length = padding.PSS.MAX_LENGTH
		),
		hashes.SHA512()
	)
	verifier.update(digest.encode())
	try:
		verifier.verify()
		return True
	except:
		return False
   
#With PEM certificate and SHA512 hashing and padding only
#raises InvalidSignature on validation failure
#Note: expects an ascii85 string as digest, not bytes
def verify_hash_with_certificate(digest, signature, cert_path_or_bytes):
	if (type(cert_path_or_bytes) == str):
		with open(cert_path_or_bytes, 'rb') as f:
			cert_bytes = f.read()
	else:
		cert_bytes = cert_path_or_bytes
	#get pkey
	public_key = x509.load_pem_x509_certificate(
		cert_bytes,
		backend = default_backend()
	).public_key()
	#verify signature
	verifier = public_key.verifier (
		base64.a85decode(signature.encode()),
		padding.PSS (
			mgf = padding.MGF1(hashes.SHA512()),
			salt_length = padding.PSS.MAX_LENGTH
		),
		hashes.SHA512()
	)
	verifier.update(digest.encode())
	try:
		verifier.verify()
		return True
	except:
		return False
	
#Boyen mesh
#TODO: argument sanity check
#Note to self: public_keys must be a hash of numeric keys, not necessarily in order, but must be non-negative and less than the hash's length
#	the hash can contain any number of generated public keys, including one, but it's probably best to use as many as available
#In order to both obfuscate and ease transfer by humans,
#all complex objects are serialized into strings before returning

def encode(obj):
	return objectToBytes(obj, PairingGroup('MNT224')).decode()

#Patch for int keys, which are originally left as strings during decoding
#Changes all keys to in the dictionary tree (if any) to ints when possible
def coerce_int_keys(dct):
	if type(dct) == dict:
		ret = {}
		for k in dct.keys():
			v = coerce_int_keys(dct[k])
			try:
				k = int(k)
			except ValueError:
				pass
			ret[k] = v
		dct = ret
	return dct
		

def decode(obj):
	ret = bytesToObject(obj.encode(), PairingGroup('MNT224'))
	return coerce_int_keys(ret)

'''
Generates a group public key useful for adding members,
encrypting on behalf of the group and verifying a signature belongs to the group.
'''
def generate_master_key():
	boyen = Boyen(PairingGroup('MNT224'))
	master_key = boyen.setup()
	return encode(master_key)

'''
Generates pair of public and private keys, the former suitable
for compilation with other public keys, encryption and verification,
and the latter useful only in encryption.
They're distinguished from one another with the tags 'public' and 'private'
'''
def generate_key_pair(master_key):
	boyen = Boyen(PairingGroup('MNT224'))
	boyen.setup()
	master_key = decode(master_key)
	pair = boyen.keygen(master_key)
	return {'public' : encode(pair[0]), 'private': encode(pair[1])}

'''
From a list of public keys, generate a public key list suitable for use
in encrypt and verify functions.
Indices of this list go from 1 to the number of arguments provided,
and are assigned in the same order of the arguments
'''
def compile_public_key_array(*args):
	ret = {}
	for i in range(len(args)):
		ret[i+1] = decode(args[i])
	return encode(ret)

'''
Return the provided array of public keys and append the provided key last,
associated with an index next after the highest index within this list
'''
def push_public_key(array, key):
	array = decode(array)
	array[1 + max([i for i in array.keys()])] = decode(key)
	return encode(array)

'''
Returns the provided array of public keys with the provided key removed,
or False if the key is not in the array.
The indices of all other elements are maintained
'''
def pop_public_key(array, key):
	array = decode(array)
	key = decode(key)
	found  = False
	for i in array.keys():
		if array[i] == key:
			key = i
			found = True
			break
	if found:
		del array[key]
	return encode(array) if found else found

def encrypt_boyen(index, master_key, public_keys, private_key, message):
	master_key = decode(master_key)
	public_keys = decode(public_keys)
	private_key = decode(private_key)
	boyen = Boyen(PairingGroup('MNT224'))
	boyen.setup()
	return encode(boyen.sign(index, master_key, public_keys, private_key, message))

'''
Returns False if the signature does not correspond to a member of the group
defined by the master key, or to the provided object,
or to any of the public keys provided, otherwise returns True
'''
def verify_boyen(master_key, public_keys, message, signature):
	master_key = decode(master_key)
	public_keys = decode(public_keys)
	boyen = Boyen(PairingGroup('MNT224'))
	boyen.setup()
	return boyen.verify(master_key, public_keys, message, decode(signature))
	
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