import os
from sys import executable

cwd = os.sep.join(os.path.abspath(__file__).split(os.sep)[:-2])	#../
print cwd
url = os.environ['SERVER_URL']
port = os.environ['SERVER_PORT']
target = os.path.join(cwd, url + '.conf')
app = os.environ['APP_NAME']
cert_dir = os.path.join(cwd, 'cert')
user = os.environ['APACHE_USER']

with open(target, 'w') as f:
	f.write('''
Listen {0}
LoadModule ssl_module modules/mod_ssl.so

WSGIPythonPath {1}:{2}

<VirtualHost *:{0}>
	ServerName {3}
	ServerAlias {4}
	SSLEngine on
	SSLCertificateFile {5}
	SSLCertificateKeyFile {6}

	WSGIDaemonProcess {4} user={7} group={7} threads=5 python-path={1}:{2}
	WSGIScriptAlias / {8}

	CustomLog {9} common
	ErrorLog {10}
	LogLevel info

	<Directory {1}>
		WSGIProcessGroup {4}
		WSGIApplicationGroup %{GLOBAL}
		WSGIScriptReloading On
		<Files {4}.wsgi>
			Require all granted
		</Files>
	</Directory>
</VirtualHost>'''.format(port, cwd, executable, url, app,					#0..4
		os.path.join(cert_dir, 'servercert.pem'),							#5
		os.path.join(cert_dir, 'serverkey.pem'),							#6
		user,																#7
		os.path.join(cwd, app + '.wsgi'),									#8
		os.path.join(os.path.expanduser('~' + user), url + '-log'),			#9
		os.path.join(os.path.expanduser('~' + user), url + '-error-log'),	#10
		GLOBAL='{GLOBAL}'))													#Pesky