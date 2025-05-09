
import tkinter
from PIL import Image, ImageTk
import chess
import chess.pgn
import io
import random
from chessauthServer import userExists, compareHashes


SIZE = 64
IMAGES_PATH = "Images/"

class ChessAuthClient:
	def __init__(self, root):
		self.root = root
		self.root.title("Chess Authentication v1")
		self.username = None
		self.promptUsername() # sets username

		self.canvas = tkinter.Canvas(root, width=8*SIZE, height=8*SIZE)
		self.canvas.pack()

		self.canvas.bind("<Button-1>", self.onClick)
		self.board = chess.Board()
		self.currentSquare = None
		self.pgn = self.loadPGN(f"PGN Tests/{self.username}.pgn") # As of now, this data is insecure. It simulates what would be another secure server providing this information
		self.index = 0 # PGN pointer
		self.images = self.loadImages()

		self.drawBoard()
	
	def onClick(self, click):
		file = click.x // SIZE
		rank = 7 - (click.y // SIZE)
		square = chess.square(file, rank) # Locate square

		# This code handles clicking the piece to move it
		if self.currentSquare == None: 
			piece = self.board.piece_at(square)

			if piece and piece.color == chess.WHITE:
				self.currentSquare = square
		
		# This code handles moving the piece (clicking the destination square)
		else:
			move = chess.Move(self.currentSquare, square) # Move the piece 
			self.currentSquare = None

			if move in self.board.legal_moves: # Check move legality
				if self.index < len(self.pgn):
					expectedMove = self.pgn[self.index]
				else:
					expectedMove = None

				if move == expectedMove: # Check if the user played the move they're supposed to. If so, reply with black's move
					self.board.push(move)
					self.index += 1

					if self.index < len(self.pgn):
						self.board.push(self.pgn[self.index])
						game = chess.pgn.Game.from_board(self.board)
						self.index += 1
				else: # If the user plays a wrong move, give a random reply
					self.board.push(move)
					self.board.push(random.choice(list(self.board.legal_moves)))
			
			# Code to convert chess.pgn Game object to string of PGN
			game = chess.pgn.Game.from_board(self.board)

			pgn_io = io.StringIO()
			game.accept(chess.pgn.FileExporter(pgn_io))
			pgnString = pgn_io.getvalue().strip()

			if compareHashes(pgnString, self.username): # Check if user has completed proper move order
				self.showAccessScreen()

		self.drawBoard()

	def loadPGN(self, pgnPath):
		with open(pgnPath, "r") as f:
			game = chess.pgn.read_game(f)
		return list(game.mainline_moves())

	def loadImages(self): # Load images from /Images folder
		colors = ['white', 'black']
		pieces = ['pawn', 'rook', 'knight', 'bishop', 'queen', 'king']

		images = {}

		for color in colors:
			for piece in pieces:
				name = f"{color}-{piece}"
				image = Image.open(f"{IMAGES_PATH}{name}.png").convert("RGBA").resize((SIZE, SIZE))
				images[name] = ImageTk.PhotoImage(image)
		
		return images
	
	def drawBoard(self):
	
		self.canvas.delete("all")
		colors = ['#9A7B4F', '#2E1503']
		pieceDict = {'p': 'pawn', 'r': 'rook', 'b': 'bishop', 'n': 'knight', 'q': 'queen', 'k': 'king'}

		for file in range(0, 8):
			for rank in range(0, 8):
				x = file * SIZE
				y = rank * SIZE

				boardRank = 7-rank

				color = colors[(file + rank) % 2]
				self.canvas.create_rectangle(x, y, x + SIZE, y + SIZE, fill=color, outline="")

				square = chess.square(file, boardRank)
				piece = self.board.piece_at(square)

				if piece:
					#DEBUG
					#print(f"Piece {piece.symbol()} at {square}, {color}")

					if piece.color == chess.WHITE:
						c = 'white'
					else:
						c = 'black'
					
					p = piece.symbol().lower()
					
					img = self.images[f"{c}-{pieceDict[p]}"]
					self.canvas.create_image(x, y, anchor='nw', image=img)
	
	def promptUsername(self):
		popup = tkinter.Toplevel(self.root)
		popup.title("Login")
		popup.grab_set()

		tkinter.Label(popup, text="Enter username:").pack(pady=10)

		entry = tkinter.Entry(popup)
		entry.pack(padx=20)

		def submit():
			self.username = entry.get()
			if userExists(self.username):
				popup.destroy()
		
		tkinter.Button(popup, text="Submit", command=submit).pack(pady=10)
		self.root.wait_window(popup)
	
	def showAccessScreen(self): # Basic screen for when the user successfully logs in 
		
		for widget in self.root.winfo_children():
			widget.destroy()

		self.root.title("Authentication Result")

		label = tkinter.Label(
			self.root,
			text="Access Granted",
			font=("Helvetica", 24),
			fg="green",
			pady=50,
			padx=50
		)
		label.pack(expand=True)


if __name__ == '__main__':
	root = tkinter.Tk()
	client = ChessAuthClient(root)
	root.mainloop()

