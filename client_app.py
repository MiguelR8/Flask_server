from cryptography.hazmat.primitives import serialization
from hashlib import sha512
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.asymmetric import padding
from cryptography.hazmat.backends import default_backend
from cryptotools import encrypt_hash

import sys
import re

if len(sys.argv) < 2 and re.compile("--?(h|help)$").match(sys.argv[1]) or len (sys.argv) < 3:
	print "Usage: {} file_path private_key_path [password]".format(sys.argv)
	exit(0)
	
if len(sys.argv) < 4:
	sys.argv.append(None)
	
digest, signed_digest = encrypt_hash(sys.argv[1], sys.argv[2], sys.argv[3])

print '''Document: {}

Signed hash: {}

'''.format(sys.argv[1], signed_digest.encode('base64'))	#base 64 for easier consumption
