import os
import string

def activate_venv():
	script_file = os.path.realpath(__file__).split(os.sep)[:-2]							#../
	script_file = os.sep.join(script_file + ['CA_flask', 'bin', 'activate_this.py']) 	#../CA_flask/bin...

	with open(script_file) as file_:
		exec(file_.read(), dict(__file__=script_file))

#def import_cryptotools():
#	script_file = os.path.realpath(__file__).split(os.sep)[:-2]							#../
#	script_file = os.sep.join(script_file + ['cryptotools', 'cryptotools.py'])	  		#../cryptotools/cryptotools.py
#
#	execfile (script_file)

WTF_CSRF_ENABLED = True
from getpass import getuser

STORAGE_ROOT = os.path.expanduser('~' + getuser())
#one-liner to get random secret key of 20 printable characters
SECRET_KEY = ''.join([(string.letters + string.digits + string.punctuation)[ord(os.urandom(1)) % 94] for i in range(20)])
CERT_PATH = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'cert', 'rootcert.pem')
PKEY_PATH = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'cert', 'rootkey.pem')
REQ_UPLOAD_FOLDER = os.path.join(STORAGE_ROOT, 'reqs')
CERT_UPLOAD_FOLDER = os.path.join(STORAGE_ROOT, 'certs')
