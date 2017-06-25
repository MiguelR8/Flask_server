import os
import sys
from app import models, app
#allow import from cryptotools path
sys.path.insert(0, os.sep.join(os.path.abspath(__file__).split(os.sep)[:-3]))
from cryptotools import verify_boyen, verify_hash_with_certificate
from cryptotools.signscheme import SignScheme

class BoyenScheme(SignScheme):
	#either the specified group exists or public_keys is not empty and the master_key is provided
	@staticmethod
	def is_signature_valid(challenge, answer, group_name, public_keys = None, master_key = None):
		g = models.Group.query.filter_by(name = group_name).first()
		if public_keys is None or len(public_keys) == 0:
			if g is not None:		#load saved keys instead
				with open(os.path.join(app.config['GROUP_KEYS_FOLDER'],
						str(g.id) + '.pkeys')) as f:
					public_keys = f.read()
			else:
				return False
		if master_key is None:
			if g is not None:		#load saved master key instead
				with open(os.path.join(app.config['GROUP_KEYS_FOLDER'], str(g.id) + '.mkey')) as f:
					master_key = f.read()
			else:
				return False
		return verify_boyen(master_key, public_keys, challenge, answer)
		
class RSAScheme(SignScheme):
	@staticmethod
	def is_signature_valid(challenge, answer, author_name):
		try:
			certpath = os.path.join(app.config['USER_CERTIFICATE_FOLDER'],
							author_name + '.pem')
		except IOError:
			return False
		return verify_hash_with_certificate(challenge, answer, certpath)