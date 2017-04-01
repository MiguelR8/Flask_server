import sys
if sys.version[0] < '3':
	print("Error: must use python3 to continue")
	exit(0)

from cryptotools import *
import re


	
def help():
	print(
'''Usage: {0} --pkey-hash file_path private_key_path [password]
           --boyen-hash file_path master_key_path public_keys_path private_key_path index
           --boyen-sign-text string master_key_path public_keys_path private_key_path index
           --boyen-make-group [numMembers] (default is one member)
           --boyen-add-members master_key_path public_keys_path [numMembers] (default is one member)
'''.format(sys.argv[0])) and exit()
   
   
def RSA_hash(file_path, pkey_path, password=None):
	digest = hash_object(file_path, isFile = True)
	signed_digest = encrypt_hash(digest, pkey_path, password)
	print('''Document: {}

Signed hash: {}

'''.format(file_path, signed_digest))

def Boyen_hash_file(file_path, master_key_path, public_keys_path, private_key_path, index):
	with open(file_path, 'rb') as f:
		txt = f.read()
	digest = hash_object(txt)
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
		help()
	sig = encrypt_boyen(i, master_key, public_keys, private_key, digest)
	print('''Document: {}

Signed hash: {}

'''.format(file_path, sig))

def Boyen_hash_string(text, master_key_path, public_keys_path, private_key_path, index):
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
		help()
	sig = encrypt_boyen(i, master_key, public_keys, private_key, text)
	print('''Text: {}

Signed hash: {}

'''.format(text, sig))

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
	elif opt == '--pkey-hash':
		RSA_hash(*sys.argv[2:])
	elif opt == '--boyen-hash':
		Boyen_hash_file(*sys.argv[2:])
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
	raise e
	help()