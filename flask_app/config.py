import os
from getpass import getuser

STORAGE_ROOT = os.path.expanduser('~' + getuser())

import string

def activate_venv():
	script_file = os.path.realpath(__file__).split(os.sep)[:-2]						#../
	script_file = os.sep.join(script_file + ['flask', 'bin', 'activate_this.py']) 	#../flask/bin...

	with open(script_file) as file_:
		exec(file_.read(), dict(__file__=script_file))


WTF_CSRF_ENABLED = True
#one-liner to get random secret key of 20 printable characters
SECRET_KEY = ''.join([(string.letters + string.digits + string.punctuation)[ord(os.urandom(1)) % 94] for i in range(20)])
SQLALCHEMY_DATABASE_URI = 'sqlite:///' + os.path.join(STORAGE_ROOT, 'app.db')
SQLALCHEMY_MIGRATE_REPO = os.path.join(STORAGE_ROOT, 'db_repository')
DB_CURRENT_VERSION_FILE = os.path.join(SQLALCHEMY_MIGRATE_REPO, 'current_version')
DOCUMENT_UPLOAD_FOLDER = os.path.join(STORAGE_ROOT, 'uploads')
USER_CERTIFICATE_FOLDER = os.path.join(STORAGE_ROOT, 'certs')
#PDF_SIGN_CONF_FILE = os.path.join(os.path.realpath(__file__), 'mypdfsigner.conf')
