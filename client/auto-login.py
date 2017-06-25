from selenium import webdriver
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.support.ui import WebDriverWait # available since 2.4.0
from selenium.webdriver.support import expected_conditions as EC # available since 2.26.0
import sys
import os
#allow import from cryptotools path
sys.path.insert(0, os.sep.join(os.path.abspath(__file__).split(os.sep)[:-2]))
from cryptotools import *


if sys.version[0] < '3':
	print("Error: must use python3 to continue")
	exit(1)

def help(sub = None):
	if sub == 'RSA':
		print("Usage:\n{} RSA private_key_path [password]".format(sys.argv[0]))
	elif sub == 'Boyen':
		print("Usage:\n{} Boyen master_key_path public_keys_path private_key_path index".format(sys.argv[0]))
	else:
		print('''
Usage: {} username protocol credentials...

Signs in with the specified protocol.

Supported protocols: RSA, Boyen
If the -f option is provided, it will be interpreted as a file, otherwise as a string.
Credentials are protocol-dependent
'''.format(sys.argv[0]))
	exit(1)

if len(sys.argv) < 3:
	help()
uname = sys.argv[1]
opt = sys.argv[2]

#Browse to login and get challenge
driver = webdriver.Firefox()
driver.get("https://localhost:5000/login")
txt = driver.find_element_by_id('challenge').text

args = sys.argv[3:]

if opt == 'RSA':
	
	if len(args) > 1:
		pkey_path = args[1]
		password = args[2] if len(args) > 2 else None
	else:
		help('RSA')
	answer = encrypt_hash(txt, pkey_path, password)
elif opt == 'Boyen':
	if len(args) != 4:
		print ("Invalid number of parameters")
		help('Boyen')
	keys = []
	for i in args[:3]:
		with open(i) as f:
			keys.append(f.read())
	try:
		i = int(args[-1])
	except ValueError:
		print ("index must be an integer")
		help('Boyen')
	answer = encrypt_boyen(i, keys[0], keys[1], keys[2], txt)
else:
	print("Unknown protocol {}".format(opt))
	help()

driver.find_element_by_name('username').send_keys(uname)
driver.find_element_by_name('signtype').send_keys(opt)
driver.find_element_by_name('answer').send_keys(answer)
driver.find_element_by_name('submit').submit()
