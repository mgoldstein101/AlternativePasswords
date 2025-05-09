import os
import json
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from base64 import b64decode, b64encode

STORAGEFILE = 'chessdata.json'
ITERATIONS = 200_000
SALTSIZE = 16

try:
	with open(STORAGEFILE, 'r') as f:
		userData = json.load(f)
except FileNotFoundError:
	quit("Error: Data file not found. Ensure chessdata.json in proper location")

def saveData():
	with open(STORAGEFILE, 'w') as f:
		json.dump(userData, f, indent=2)

def pbkdf2Hash(data, salt):
	data = data.encode('utf-8')
	kdf = PBKDF2HMAC(
		algorithm=hashes.SHA256(),
		length = 32,
		salt = salt,
		iterations = ITERATIONS
	)

	return kdf.derive(data)


def userExists(username):
	return username in userData

def compareHashes(data, username):
	salt = b64decode((userData[username][0]["salt"]))
	potentialData = pbkdf2Hash(data, salt)

	return b64encode(potentialData).decode('utf-8') == userData[username][0]['hash']

def debugHashPgns(path): # Debug function to generate json file
	for file in os.listdir(path):
		filepath = os.path.join(path, file)
		with open(filepath, 'r') as f:
			data = f.read()
		salt = os.urandom(16)
		hash = pbkdf2Hash(data, salt)
		pgnData = [{"salt": b64encode(salt).decode('utf-8'), "hash": b64encode(hash).decode('utf-8')}]
		userData[file[:4]] = pgnData
	
	saveData()

if __name__ == '__main__':
	debugHashPgns('PGN Tests')
		
