import random
from AssociativeServer import createNewUser, authenticateUser, getWords, userExists, resetJSON

class authClient:

	def __init__(self):
		self.username = None

	def registerUser(self, username=None):
		'''
		This function can either be called by itself or as a side effect of the login process. If called by itself, it
		prompts for a username, otherwise it uses the one from the login process.
		'''
		
		if username is None:
			username = input("Enter name for new user: ")
			if userExists(username):
				print("User already exists")
				return
		
		confirm = True
		while confirm:
			ans = input(f"User {username} doesn't exist. Create new user (y/n)? ").strip().lower()
			if ans == 'y':
				confirm = False
			elif ans == 'n':
				print("Returning to Menu...")
				return False
			
		self.username = username
		assocDict = self.makeNewAssociations() # Set the word association pair for the user
		registered = createNewUser(username, assocDict) # Returns true if successful
		print(f"Registered new user {self.username}" if registered else print(f"Error creating user {username}"))
		return True
	
	def makeNewAssociations(self):
		assocDict = {}

		# A more fleshed out system would handle this differently, but for now, we're just choosing 5 random words from the list
		with open("Oxford5000.txt", "r") as f:
			data = f.readlines()
		indices = random.sample(range(0, 1995), 5)

		print("Enter a word association for each given word (5 total)")
		for index in indices:
			assoc = input(f"Word {indices.index(index)+1}/5 \t {data[index].strip()}: ")
			assocDict[data[index].strip()] = assoc # Format: {word: associated_word}
		
		return assocDict
	
	def getAssociations(self, keys):
		'''
		This function retrieves the words from the 'server' and then asks the user for the associated words
		'''
		assocs = {}
		shuffledKeys = sorted(keys, key=lambda k: random.random()) # Shuffling helps security minimally, but it is something
		for key in shuffledKeys:
			print(f"Word: {key}")
			answer = input(f"Response: ").strip()
			assocs[key] = answer
		return assocs
	
	def doAuthentication(self): # Main authentication function

		# This code gets the username and creates a new user if the name is unidentified
		self.username = input("\nEnter your username: ").strip()
		if not userExists(self.username):
			self.registerUser(self.username)
			return
		
		words = getWords(self.username) # Gets list words from server
		associations = self.getAssociations(words) # Gets the user's authentication attempt (associated words)

		if authenticateUser(self.username, associations):
			print("Login successful")
		else:
			print("Login failed")
	
	def clearData(self): # DEBUG function for clearing JSON file
		resetJSON()
		


def main():
	client = authClient()
	print("========Word Association Authentication========")
	print("Word Association Authentication is an alternative password system. Users will be prompted to complete a series of 5 word-association promtps to log in.")
	while True:
		print("\t Menu (Type number to choose option)\n1. Log in\n2. Create new user")
		choice = input()
		
		match choice:
			case "1":
				client.doAuthentication()
			case "2":
				client.registerUser()
			case "3": # DEBUG ONLY
				client.clearData()
			case _:
				print("Invalid command")

if __name__ == '__main__':
	main()
		

