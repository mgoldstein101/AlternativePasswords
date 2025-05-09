import os
import json
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from base64 import b64decode, b64encode

STORAGEFILE = 'data.json' # In place of a database, I'm using a JSON file for now
ITERATIONS = 200_000 
SALTSIZE = 16

# Loading JSON file into memory
try:
	with open(STORAGEFILE, 'r') as f:
		userData = json.load(f)
except FileNotFoundError:
	quit("Error: Data file not found. Ensure data.json in proper location")

def saveData():
	with open(STORAGEFILE, 'w') as f:
		json.dump(userData, f, indent=2)

def pbkdf2Hash(key, value, salt):
	'''
	This is the main hashing function I'm using for this program. I went with hashing and not signing because I want
	security here, not necessarily integrity (though signing would also be good). While something like SHA-512 would work here,
	I choose pbkdf2 because of the built in longer computation time which makes it harder to bruteforce with a dictionary attack,
	which is the main vulnerability of this kind of authentication. Since the associations come from a possible dict of 2000 words, salting 
	also helps with uniqueness.
	'''
	kvp = f"{key}:{value}".encode('utf-8')
	# I don't think it's strictly neccessary to encode the kvps this way because the key is its own field in the JSON database
	# But this keeps the hashing function generic in case I want to use it for other applications in scaling this up

	kdf = PBKDF2HMAC(
		algorithm=hashes.SHA256(),
		length = 32,
		salt = salt,
		iterations = ITERATIONS
	)

	return kdf.derive(kvp)

def createNewUser(username, assocDict):
	
	hashedAssocs = []
	for key, value in assocDict.items(): # Provided by client
		salt=os.urandom(SALTSIZE)
		hash = pbkdf2Hash(key, value, salt) # Generate hash of key and associated word

		# b64 for easy JSON dumping
		hashedAssocs.append({"key": key, "salt": b64encode(salt).decode('utf-8'), "hash": b64encode(hash).decode('utf-8')})

	userData[username] = hashedAssocs
	saveData()
	return True

def getWords(username):
	#Returns a list of words the user will have to give associations for
	return [item['key'] for item in userData[username]]

def authenticateUser(username, assocs):
	
	data = userData[username] # Load all data associated with a specific user
	
	for item in data:
		key = item['key'] # Key word
		assoc = assocs.get(key, "") # Associated word

		salt = b64decode(item['salt'])
		expectedHash = b64decode(item['hash'])

		testHash = pbkdf2Hash(key, assoc, salt) # Generate a hash using the user-provided word

		if testHash != expectedHash: # Check if the user-provided association is correct
			return False

	return True

def userExists(username):
	return username in userData

def resetJSON():
	with open(STORAGEFILE, 'w') as f:
		json.dump({}, f, indent=2)
	saveData()

if __name__ == '__main__':
	with open("./data.json", 'r') as f:
		print(f.read())
			







