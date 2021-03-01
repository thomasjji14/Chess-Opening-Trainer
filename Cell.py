from tkinter import *
from FileManager import getFile

class Cell():
    def __init__(self):
        self.text = "-"
        self.__image = None
        self.__record = None
    
    # def update
    
    # Photoimages can only be created AFTER declaring a tkinter object
    def __getPieceFromText(self, pieceText):
        """ Maps the piece character to the piece's image """
        PIECE_IMAGE_MAP = {
            'p' : PhotoImage(file = getFile('cpieces/bpawn.png')),
            'r' : PhotoImage(file = getFile('cpieces/brook.png')),
            'b' : PhotoImage(file = getFile('cpieces/bbishop.png')),
            'n' : PhotoImage(file = getFile('cpieces/bknight.png')),
            'k' : PhotoImage(file = getFile('cpieces/bking.png')),
            'q' : PhotoImage(file = getFile('cpieces/bqueen.png')),

            'P' : PhotoImage(file = getFile('cpieces/wpawn.png')),
            'R' : PhotoImage(file = getFile('cpieces/wrook.png')),
            'B' : PhotoImage(file = getFile('cpieces/wbishop.png')),
            'N' : PhotoImage(file = getFile('cpieces/wknight.png')),
            'K' : PhotoImage(file = getFile('cpieces/wking.png')),
            'Q' : PhotoImage(file = getFile('cpieces/wqueen.png')),

            '-' : None
        }
        return PIECE_IMAGE_MAP[pieceText]