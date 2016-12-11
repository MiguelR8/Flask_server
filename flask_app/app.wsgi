#Source: http://flask.pocoo.org/docs/0.11/deploying/mod_wsgi/

import os

script_file = os.path.realpath(__file__).split(os.sep)[:-2]						#../
script_file = os.sep.join(script_file + ['flask', 'bin', 'activate_this.py']) 	#../flask/bin...

with open(script_file) as file_:
	exec(file_.read(), dict(__file__=script_file))

from app import app as application