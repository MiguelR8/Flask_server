import os
from sys import executable

cwd = os.sep.join(os.path.abspath(__file__).split(os.sep)[:-2])	#../
url = os.environ['SERVER_URL']
port = os.environ['SERVER_PORT']
target = os.path.join(cwd, url + '.conf')
app = os.environ['APP_NAME']
cert_dir = os.path.join(cwd, 'cert')
user = os.environ['APACHE_USER']
home = os.path.expanduser('~' + user)

with open(target, 'w') as f:
	f.write('''
Listen {0}
LoadModule ssl_module modules/mod_ssl.so

WSGIPythonPath {1}:{2}

<VirtualHost *:{0}>
	
	RewriteCond %{{HTTPS}} =off
	RewriteRule ^/?(.*) https://%{{SERVER_NAME}}/$1 [R]

	ServerName {3}
	ServerAlias {4}
	SSLEngine on
	SSLCertificateFile {5}
	SSLCertificateKeyFile {6}
	
	SSLProtocol all -SSLv2 -SSLv3
	SSLHonorCipherOrder On
	SSLCipherSuite ECDH+AES

	WSGIDaemonProcess {4} user={7} group={7} threads=5 python-path={1}:{2}
	WSGIScriptAlias / {8}

	CustomLog {9} common
	ErrorLog {10}
	

	<Directory {1}>
		WSGIProcessGroup {4}
		WSGIApplicationGroup %{{GLOBAL}}
		WSGIScriptReloading On
		<Files {4}.wsgi>
			Require all granted
		</Files>
	</Directory>
	
	Alias "/files" "{11}"
	<Directory {11}>
		Require all granted
	</Directory>
</VirtualHost>'''.format(port, cwd, executable, url, app,	#0..4
		os.path.join(cert_dir, 'servercert.pem'),			#5
		os.path.join(cert_dir, 'serverkey.pem'),			#6
		user,												#7
		os.path.join(cwd, app + '.wsgi'),					#8
		os.path.join(home, url + '-log'),					#9
		os.path.join(home, url + '-error-log'),				#10
		os.path.join(home, 'uploads')))						#11