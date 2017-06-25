import sys
if sys.version[0] < '3':
	print("Error: must use python3 to continue")
	exit(1)

import os
#allow import from cryptotools path
sys.path.insert(0, os.sep.join(os.path.abspath(__file__).split(os.sep)[:-2]))
from cryptotools import *
import re


	
def help(sub = None):
	if sub is 'hash':
		print ('''Usage: {0} hash [-f|--file] [-h|--hash] protocol [file_path|string] args...
If -f is provided, treat argument as a file path, otherwise a string,
If -h is provided, hash first (sha512)

Protocols:
	RSA [path|string] private_key_path [password]
	Boyen [path|string] master_key_path public_keys_path private_key_path key_index
'''.format(sys.argv[0]))
	else:
		print('''Usage: {0} hash protocol [-f|--file] [-h|--hash] path_or_string credentials...
           --boyen-make-group [numMembers] (default is one member)
           --boyen-add-members master_key_path public_keys_path [numMembers] (default is one member)
'''.format(sys.argv[0]))
	
	exit(1)

def _hash(*args):
	if len(args) < 2:
		help('hash')
	
	isFile = doHash = False
	protocol = args[0]
	drop = 1
	opts = [['-f', '--file'], ['-h', '--hash']]
	if args[1] in opts[0] or args[2] in opts[0]:
		isFile = True
		drop += 1
	if args[1] in opts[1] or args[2] in opts[1]:
		doHash = True
		drop += 1
	args = args[drop:]
	
	if protocol == 'RSA':
		RSA_hash(*args, isFile = isFile, doHash = doHash)
	elif protocol == 'Boyen':
		Boyen_hash(*args, isFile = isFile, doHash = doHash)
	else:
		print("Unrecognized protocol: " + protocol)
		help('hash')
   
def RSA_hash(txt, pkey_path, password = None, isFile = True, doHash = True):
	if isFile:
		with open(txt, 'rb') as f:
			txt = f.read()
	if doHash:
		txt = hash_object(txt, isFile)
	
	signed_digest = encrypt_hash(txt, pkey_path, password)
	print('''Document: {}

Signed hash: {}

'''.format(txt, signed_digest))

def Boyen_hash(txt, master_key_path, public_keys_path, private_key_path,
		index, isFile = True, doHash = True):
	if isFile:
		with open(txt, 'rb') as f:
			txt = f.read()
	if doHash:
		txt = hash_object(txt, isFile)
	
	with open(master_key_path) as f:
		master_key = f.read().strip()
	with open(public_keys_path) as f:
		public_keys = f.read().strip()
	with open(private_key_path) as f:
		private_key = f.read().strip()
	try:
		i = int(index)
	except ValueError:
		print('Error: index must be a base 10 integer')
		help('hash')
	sig = encrypt_boyen(i, master_key, public_keys, private_key, txt)
	print('''Document: {}

Signed hash: {}

'''.format(txt, sig))

def Boyen_create_group(members='1'):
	mkey = generate_master_key()
	try:
		i = int(members)
		if i < 1:
			raise ValueError
	except ValueError:
		print('Error: numMembers must be a positive base 10 integer')
		help()
	keys = [generate_key_pair(mkey) for d in range(i)]
	array = compile_public_key_array(*[k['public'] for k in keys])
	print("New group created\n")
	print("Master key: {}\n".format(mkey))
	j = 1
	for k in keys:
		print('Key pair index {}:'.format(j))
		print("\tPublic key: {}\n".format(k['public']))
		print("\tPrivate key: {}\n".format(k['private']))
		j += 1
		
	print("Compressed list of public keys:\n{}\n".format(array))
	
def Boyen_add_members(master_key_path, public_keys_path, members='1'):
	with open(master_key_path) as f:
		master_key = f.read().strip()
	with open(public_keys_path) as f:
		public_keys = f.read().strip()
	try:
		i = int(members)
		if i < 1:
			raise ValueError
	except ValueError:
		print('Error: numMembers must be a positive base 10 integer')
		help()
	array = push_public_key(public_keys, generate_key_pair(master_key))
	print("New compressed list of public keys:\n{}\n".format(array))

if len(sys.argv) < 2:
	help()
opt = sys.argv[1]

try:
	if re.compile("--?(h|help)$").match(opt):
		help()
	elif opt == 'hash':
		_hash(*sys.argv[2:])
	elif opt == '--boyen-sign-text':
		Boyen_hash_string(*sys.argv[2:])
	elif opt == '--boyen-make-group':
		Boyen_create_group(*sys.argv[2:])
	elif opt == '--boyen-add-members':
		Boyen_add_members(*sys.argv[2:])
	else:
		print('Unrecognized option {}'.format(opt))
except TypeError as e:
	print('Invalid number of arguments')
	help()
	raise e