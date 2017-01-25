import sys

def trace(frame, event, arg):
	if event == 'call':
		try:
			print 'Executing {0} with locals {1}'.format(frame.f_code.co_consts[0], frame.f_locals)
		except:
			pass
#	elif event == 'line':
#		print 'Step in {0}'.format(frame.f_lasti)
#	else:
#		print '{0} at line {1} with {2}'.format(event, frame.f_lineno, arg)
	if event == 'exception' or event == 'c_exception':
		return None
	return trace

#sys.settrace(trace)
from client_app import *
cf = get_conf(pkey_location= 'cert/serverkey.pem', cert_location= 'cert/servercert.pem', pfx_password='12345')
#cf = get_conf(pfx_location = '/usr/local/mypdfsigner/tests/mypdfsigner-test.p12', pfx_password='mypdfsigner')

#~ import mypdfsigner
#~ import os
#~ from json import loads

#~ temp = 'conf.tmp'
#~ conftext = ''
#~ tempp12 = 'temp.p12'
#~ js = loads(cf)
#~ for key in js:
	#~ if key == u'certfile':
		#~ with open(tempp12, 'w') as f:
			#~ f.write(js[key])
		#~ conftext += "{0}={1}\n".format(key, os.path.abspath(tempp12))
	#~ else:
		#~ conftext += "{0}={1}\n".format(key, js[key])

#~ with open(temp, 'w') as f:
	#~ f.write(conftext)

#print conftext
if os.path.exists("/tmp/example-signed-python.pdf"):
	os.remove("/tmp/example-signed-python.pdf")
print sign_pdf('/usr/local/mypdfsigner/tests/example.pdf', "/tmp/example-signed-python.pdf", cf)
import os
os.system('lsof -p {0}'.format(os.getpid()))
#~ import time

#~ t = time.clock()
#~ r = 'progress'
#~ while r.find('progress') > -1 and (t + 0.0001 > time.clock()):
	#~ r =  mypdfsigner.get_signer_info("/tmp/example-signed-python.pdf")
#~ print r

#os.remove(temp)
#os.remove(tempp12)


