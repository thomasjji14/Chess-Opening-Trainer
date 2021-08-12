import copy
import sys
import os
from Chessboard import Chessboard
from Engine import Engine
from tkinter import *
from playsound import playsound
from Coordinate import Coordinate
from CanvasUtility import *
from Cell import Cell
from FileManager import *
from Player import *
import downloader
import time
import datetime
import json


class Game:

    BROWN = '#B58863'
    LIGHT_BROWN = '#F0D9B5'
    BOX_LEN = 95
    BOARD_LEN = 8
    X_INDEX = 0
    Y_INDEX = 1
    WHITE_INDEX = 0
    BLACK_INDEX = 1
    STALEMATE = 'Stalemate'
    CHECKMATE = 'Checkmate'
    CHECK = 'Check'
    DRAW = 'Draw'
    DEFAULT_FEN = 'rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1'

    def __init__(self, base, FENCode, asWhite=True):
        """ Inits the Chessboard object from a Tkinter Base """

        # Tkinter object initailizers
        self.__base = base

        self.__boardFrame = Frame(base)
        self.__boardFrame.grid(row=0, column=0, rowspan=1, columnspan=1)
        self.__board = Chessboard(self.__boardFrame)
        self.__board.grid(row = 0, column = 0)
        

        self.__infoFrame = Frame(base)
        self.__infoFrame.grid(row=0, column=1, sticky = N)

        self.__moveFrame = Frame(self.__infoFrame)
        self.__moveFrame.grid(row=0, column=0, rowspan=1, columnspan=1, sticky = N)

        self.__analysisFrame = Frame(self.__infoFrame)
        self.__analysisFrame.grid(row=0, column=1, rowspan=1, columnspan=1, sticky = N, ipady=280)
        self.__gameProcessingFrame = Frame(self.__infoFrame)
        self.__gameProcessingFrame.grid(row = 1, column= 0, rowspan = 1, columnspan= 2, sticky = S)

        self.__movePlayedText = StringVar('')
        self.__movePlayedLabel = Label(self.__gameProcessingFrame, textvariable=self.__movePlayedText,
                                  anchor='w', justify=LEFT, font = ("Times New Roman", 12))
        self.__movePlayedLabel.grid(row=0, column=0, rowspan=1, columnspan= 2)

        self.__acceptMoveButton = Button(self.__gameProcessingFrame, text = "Yes", command = self.dummyfxn)
        self.__acceptMoveButton.grid(row = 1, column = 0)
        self.__betterMoveEntry = Entry(self.__gameProcessingFrame)
        self.__betterMoveEntry.grid(row = 1, column = 1)
        self.__goFlag = False


        # Buttons for game analysis
        self.__genericButton = Button(self.__analysisFrame, text='Analyze!',
                command=self.__runAnalysis)
        self.__genericButton.grid(row=0, column=0, columnspan=2,
                                  sticky=NSEW)

        # Labels for move numbers and moves by black/white
        self.__moveText = StringVar('')
        self.__moveLabel = Label(self.__moveFrame, textvariable=self.__moveText,
                                 anchor='e', justify=LEFT, width=4,
                                 font = ("Times New Roman", 12))
        self.__moveLabel.grid(row=0, column=0, sticky=N, rowspan=1)
        self.__whiteText = StringVar('')
        self.__whiteLabel = Label(self.__moveFrame, textvariable=self.__whiteText,
                                  anchor='w', justify=LEFT, width=7,
                                  font = ("Times New Roman", 12))
        self.__whiteLabel.grid(row=0, column=1, sticky=N, rowspan=1)
        self.__blackText = StringVar('')
        self.__blackLabel = Label(self.__moveFrame, textvariable=self.__blackText,
                                  anchor='w', justify=LEFT, width=7,
                                  font = ("Times New Roman", 12))
        self.__blackLabel.grid(row=0, column=2, sticky=N, rowspan=1)

        self.__engineMoveText = StringVar('')
        self.__analysisMoveLabel = Label(self.__analysisFrame,
                textvariable=self.__engineMoveText, anchor='w',
                justify=LEFT, width=7)
        self.__analysisMoveLabel.grid(row=1, column=0, rowspan=1,
                sticky=N)

        self.__engineEvalText = StringVar('')
        self.__analysisEvalLabel = Label(self.__analysisFrame,
                textvariable=self.__engineEvalText, anchor='w',
                justify=LEFT, width=6)
        self.__analysisEvalLabel.grid(row=1, column=1, rowspan=1,
                sticky=N)

        self.__gameNavigationFrame = Frame(self.__base)
        self.__genericButton = Button(self.__gameNavigationFrame, text='Retrieve Games',
        command=self.__download)
        self.__genericButton.grid(row=0, column=0, sticky=NSEW)
        self.__genericButton = Button(self.__gameNavigationFrame, text='Next Game',
                command=self.__nextGame)
        self.__genericButton.grid(row=0, column=1, sticky=NSEW)
        self.__gameNavigationFrame.grid(row = 1, column = 0, columnspan= 2, sticky = W)


        self.__promotionText = ''
        self.__promotionImages = []
        self.__promotionButtons = []

        self.__positionToEnPassant = None

        # Bindings
        self.__base.bind('<B1-Motion>', self.__move)
        self.__base.bind('<Button-1>', self.__selectPiece)
        self.__base.bind('<ButtonRelease-1>', self.__deselectPiece)
        self.__base.bind('<Button-3>', self.__rightClickEvent)
        self.__base.bind('<ButtonRelease-3>', self.__finishShape)
        self.__base.bind('<Right>', self.__advancePGN)
        self.__base.bind('<Left>', self.__backtrackPGN)
        self.__base.bind('<space>', self.__printFEN)
        self.__base.bind('<Up>', self.__printPGN)
        self.__base.bind('<Return>', self.__inputGo)

        # Tracker for when pieces are moved
        self.__activeCell = Cell()

        # For the purpose of advancing/backtracking a PGN
        self.__moveHistory = []
        self.__boardHistory = []
        self.__activeGameMoves = []
        self.__pgnMemory = []
        self.__pgnIndex = 0
        self.__isGameActive = True

        self.__isPlayerWhite = asWhite

        self.__activeArrows = {}
        self.__activeCircles = {}
        self.__originalArrowCoordinate = ()

        self.__readFEN(FENCode, asWhite)

        if os.path.exists("user.json"):
           with open("user.json", "r") as f:
                self.__userData = json.load(f)
                self.__playerGameTree = self.__userData["USER_TREE"]
                self.__opponentGameTree = self.__userData["OPPONENT_TREE"]
        else:
            self.__userData = {} # this is just so python doesn't yell at me maybe

    def dummyfxn(self):
        self.__goFlag = True

    def __inputGo(self, event):
        if len(self.__betterMoveEntry.get()) != 0:
            self.__goFlag = True

    def __readFEN(self, FENCode, asWhite):
        """ Takes in a FENCode and initializes the board """
        boardInfo = FENCode.split(" ")

        # Splits the FENCode into relevant information
        boardCode = boardInfo[0]
        currentColor = boardInfo[1]
        castlingRights = boardInfo[2]
        enPassantSquare = boardInfo[3]
        halfMoveCount = boardInfo[4]
        fullMoveCount = boardInfo[5]

        # When the player at the bottom part of the board is black,
        # the position is simply miorred rather than changing indexing.
        # Consequently, when printing out the FEN, this must be reversed
        if not asWhite:
            boardCode = boardCode[::-1]
        self.__isPlayerWhite = asWhite

        cleanedCode = ""
        numberList = ["1", "2", "3", "4", "5", "6", "7", "8"]

        # Converts numbers into dashes
        for index in range(len(boardCode)):
            if boardCode[index] in numberList:
                for repeats in range(int(boardCode[index])):
                    cleanedCode += "-"
            else:
                cleanedCode += boardCode[index]

        textBoard = [list(row) for row in cleanedCode.split("/")]
        for row in range(self.BOARD_LEN):
            for col in range(self.BOARD_LEN):
                self.__board.textUpdate(textBoard[row][col], 
                                        Coordinate(row, col))

        # Assigns FEN fields to the class
        self.__isWhite = currentColor == "w"

        self.__whiteKingCastle = False
        self.__whiteQueenCastle = False
        self.__blackKingCastle = False
        self.__blackQueenCastle = False

        if "K" in castlingRights:
            self.__whiteKingCastle = True
        if "Q" in castlingRights:
            self.__whiteQueenCastle = True
        if "k" in castlingRights:
            self.__blackKingCastle = True
        if "q" in castlingRights:
            self.__blackQueenCastle = True

        if not enPassantSquare == "-":
            letter = enPassantSquare[0]
            number = enPassantSquare[1]

            x_index = 8 - int(number)
            y_index = self.letterToNum(letter)

            self.__positionToEnPassant = Coordinate(x_index, y_index)
        else:
            self.__positionToEnPassant = None

        self.__halfMoveCounter = int(halfMoveCount)
        self.__moveCounter = int(fullMoveCount)

    def __selectPiece(self, event):
        """ Determines the piece pressed, and marks the original position """
        # Blocks moves after game completion
        if not self.__isGameActive:
            return

        # Blocks selections outside of the game board
        if event.x >= 760 or event.y >= 760:
            return

        # Resets the arrows/highlighted boxes
        self.__resetShapes()

        # Records the old position
        self.__originalPos = getBoardCoordinate(event)

        # Remembers the current cell that will be manipulated
        self.__activeCell = \
            copy.copy(self.__board.getCell(self.__originalPos))

    def __move(self, event):
        """ Updates the piece to the mouse's position """
        # Makes sure that a piece has been selected
        if not self.__activeCell.isEmpty():

            # Centers the piece on the mouse's center
            self.__board.moveto(
                self.__activeCell.record, 
                event.x-int(self.BOX_LEN/2), 
                event.y-int(self.BOX_LEN/2)
                )
            
            # Moves the moving piece in front of all other drawn pieces
            self.__board.tag_raise(self.__activeCell.record)

    def __deselectPiece(self, event):
        """ Puts down the piece and marks its completion """

        # Gets the box that the mouse is in
        clickLoc = getBoardCoordinate(event)

        # Calculates the distances being moved by a piece
        delta = Coordinate.getDifference(clickLoc, self.__originalPos)
        if self.__isPlayerWhite:
            delta.inverse()

        # Checks if an actual piece is being pressed
        if not self.__activeCell.isEmpty():

            # Converts K over R castling to a two-square king movement
            if self.__activeCell.text.upper() == 'K' and abs(delta.y) > 1:
                if delta.y == -3:
                    delta.y = -2
                    clickLoc.y += -1 if self.__isPlayerWhite else 1
                elif delta.y == 4:
                    delta.x = 2
                    clickLoc.y += 2 if self.__isPlayerWhite else -2

            # Chesks if the move is valid
            if self.__isLegalMove(self.__activeCell.text, self.__originalPos, 
                                  clickLoc, self.__board.getTextBoard()):
                self.__endMove(clickLoc)
            else:
                self.__rightClickEvent(None)

    def __isLegalMove(self, pieceText, oldPos, newPos, board,
                      isTheorhetical = False, color = None):
        """ Checks the legality of a given move """
        if color is None:
            color = self.__isWhite

        # Calculates how far the piece has moved
        delta = Coordinate.getDifference(newPos, oldPos)
        if not self.__isPlayerWhite:
            delta.inverse()

        # Makes sure that the person is moving on their own turn
        if not isTheorhetical:
            if not color == pieceText.isupper():
                return False

        # Bounds detection
        if (newPos.x > 7 or newPos.x < 0 or 
                newPos.y > 7 or newPos.y < 0):
            return False 
        
        
        # Makes sure you can't capture your own pieces
        if not isTheorhetical:
            if (pieceText.isupper() == board[newPos.x][newPos.y].isupper() \
                    and not board[newPos.x][newPos.y] == '-'):
                return False

        # Can't move onto the same square
        if oldPos == newPos:
            return False
        
        # -------------------- Piece movement --------------------
        # Diagonal on bishop
        if pieceText.upper() in 'B' and not abs(delta.x) == abs(delta.y):
            return False

        # Horizontal of rook
        if pieceText.upper() == 'R' and not delta.x * delta.y == 0:
            return False
            
        # L-Shape of knight
        if pieceText.upper() == 'N' and not abs(delta.x) * abs(delta.y) == 2:
            return False
        
        # 1 square movement of king
        if pieceText.upper() == "K":
            if abs(delta.x) > 1:
                return False
            # Kingside
            if delta.y == 2 and not (self.__whiteKingCastle 
                    if self.__isWhite else self.__blackKingCastle):
                return False
            
            # Queenside knight manually checked for rook movement
            knightX = 7 if self.__isWhite else 0
            knightY = 1
            if not self.__isPlayerWhite:
                knightX = 7-knightX
                knightY = 6

            if delta.y == -2 and not (
                    (self.__whiteQueenCastle 
                    if self.__isWhite else self.__blackQueenCastle) 
                    and board[knightX][knightY] == '-'):
                return False 
            if abs(delta.y) > 2:
                return False
            
            if abs(delta.y) == 2 and self.__inCheck(
                    self.__isWhite, self.__board.getTextBoard()):
                return False

        # Hybrid diagonal and horizontal of queen
        if pieceText.upper() == 'Q' and not (abs(delta.x) == abs(delta.y) 
                                             or delta.x * delta.y == 0):
            return False

        # WHITE PAWN
        if pieceText == 'P':
            whitePawnHome = 6 if self.__isPlayerWhite else 1

            # Cannot move to a position that already has a piece on
            if ((delta.x == -1 or delta.x == -2) and delta.y == 0
                    and not board[newPos.x][newPos.y] 
                    == '-'):
                return False
            # Captures
            if ((delta.x == -1 and abs(delta.y) == 1) and not 
                (board[newPos.x][newPos.y].islower() 
                or (oldPos.x==(3 if self.__isPlayerWhite else 4) 
                        and newPos == self.__positionToEnPassant))):
                return False    
            # On home row, can move only 1 or 2 spaces
            if delta.x <-1 and not (
                oldPos.x == whitePawnHome and delta.x == -2):
                return False
            if delta.x == -2 and not delta.y == 0:
                return False
            if abs(delta.y) > 1 or delta.x <-2:
                return False
            if delta.x >= 0:
                return False

        # BLACK PAWN
        if pieceText == 'p':
            blackPawnHome = 1 if self.__isPlayerWhite else 6

            # Cannot move to a position that already has a piece on
            if ((delta.x == 1 or delta.x == 2) and delta.y == 0
                    and not board[newPos.x][newPos.y] == '-'):
                return False

            # Captures
            if ((delta.x == 1 and abs(delta.y) == 1) and not 
                (board[newPos.x][newPos.y].isupper() 
                or (oldPos.x == (4 if self.__isPlayerWhite else 3) 
                        and newPos == self.__positionToEnPassant))):
                return False    
            # On home row, can move only 1 or 2 spaces
            if delta.x > 1 and not (
                oldPos.x == blackPawnHome and delta.x == 2):
                return False
            if delta.x == 2 and not delta.y == 0:
                return False
            if abs(delta.y) > 1 or delta.x > 2:
                return False
            if delta.x <= 0:
                return False

        # Checks for collisions on the way
        if not pieceText.upper() == 'N':

            # Determines which direction to move towards
            xinc = 0 if delta.x == 0 else int(delta.x/(abs(delta.x)))
            yinc = 0 if delta.y == 0 else int(delta.y/(abs(delta.y)))

            # Increments need to reverse signs because the logic is
            # messed up with reverse FENs
            if not self.__isPlayerWhite:
                xinc *= -1
                yinc *= -1

            tempPosition = copy.copy(oldPos)

            # Looks for if there's a piece in the way
            tempPosition.x += xinc
            tempPosition.y += yinc
            while not tempPosition == newPos:
                if not board[tempPosition.x][tempPosition.y] == '-':
                    return False
                tempPosition.x += xinc
                tempPosition.y += yinc
        
        # Checks for legalities after a move
        if not isTheorhetical:
            # Checks what it might look like if the move were made
            theoryBoard = copy.deepcopy(board)
            theoryBoard[oldPos.x][oldPos.y] = "-"
            theoryBoard[newPos.x][newPos.y] = pieceText

            # Manually has to remove the en passanted pawn 
            if (pieceText.upper() == 'P' and abs(delta.x) == 1 
                    and abs(delta.y) == 1 
                    and newPos == self.__positionToEnPassant):
                theoryBoard[newPos.x + (
                    -1 if color ^ self.__isPlayerWhite else 1)
                    ][newPos.y] = "-"

            # Makes sure you don't self-discovered check yourself
            if self.__inCheck(color, theoryBoard):
                return False

            # Makes sure you can't castle through check
            if pieceText.upper() == "K" and abs(delta.y) == 2:
                theoryBoard = copy.deepcopy(board)
                theoryBoard[oldPos.x][oldPos.y] = "-"
                theoryBoard[newPos.x][int((oldPos.y+newPos.y)/2)] = pieceText

                if self.__inCheck(color, theoryBoard):
                    return False

        return True

    def __endMove(self, finalPos, promotionPiece = None):
        # Records the board state for use of backtracking
        self.__pgnMemory.append([copy.deepcopy(self.__board.getTextBoard()),
                                self.__isWhite,
                                self.__moveCounter,
                                self.__halfMoveCounter,
                                copy.copy(self.__positionToEnPassant),
                                self.__whiteKingCastle,
                                self.__blackKingCastle,
                                self.__whiteQueenCastle,
                                self.__blackQueenCastle,
                                copy.deepcopy(self.__boardHistory),
                                self.__isGameActive,
                                self.__whiteText.get(),
                                self.__blackText.get(),
                                self.__moveText.get()                                
                                ]
        )
        self.__pgnIndex += 1

        textBoard = self.__board.getTextBoard()

        # Records the piece being moved
        moveText = self.__moveToBasicAN(self.__originalPos, finalPos)

        # Calculates how far the piece has moved
        delta = Coordinate.getDifference(self.__originalPos, finalPos)
        if not self.__isPlayerWhite:
            delta.inverse()

        # Only pawn moves or captures reset the board position
        if (self.__activeCell.text.upper() == "P"
            or not textBoard[finalPos.x][delta.y] == '-'):
            self.__halfMoveCounter = 0
            self.__moveHistory = []
        else:
            self.__halfMoveCounter += 1

        # Centers the object onto the square it landed on
        self.__board.moveto(
            self.__activeCell.record,
            getCanvasX(finalPos),
            getCanvasY(finalPos))

        # Removes old piece images on capture
        self.__board.delete(self.__board.getCell(finalPos).record)
        # Removes the pawn during an en passant
        if (abs(delta.x) == 1 
                and abs(delta.y) == 1 
                and finalPos == self.__positionToEnPassant
                and self.__activeCell.text.upper() == "P"
                ):
            pawn_x_index = finalPos.x + (-1 if self.__isWhite ^ 
                                         self.__isPlayerWhite else 1)
            
            self.__board.delete(self.__board.getCell(Coordinate(
                finalPos.x+ (1 if self.__isWhite else -1),finalPos.y)))
            self.__board.textUpdate("-",Coordinate(pawn_x_index,finalPos.y))

        self.__positionToEnPassant = None
        if self.__activeCell.text.upper() == 'P':
            if abs(delta.x) == 2:
                leftSpotPiece = "-"
                rightSpotPiece = "-"
                if not finalPos.y == 0:
                    leftSpotPiece = textBoard[finalPos.x][finalPos.y-1]                    
                if not finalPos.y == 7:
                    rightSpotPiece = textBoard[finalPos.x][finalPos.y+1]
                leftAbleToTake = False
                rightAbleToTake = False
                theoryBoard = copy.deepcopy(textBoard)
                theoryBoard[self.__originalPos.x][self.__originalPos.y] = "-"
                theoryBoard[self.__originalPos.x - int(delta.x/2)][
                    self.__originalPos.y] = \
                        textBoard[self.__originalPos.x][self.__originalPos.y]
                if leftSpotPiece.upper() == "P":
                    # NOTE: Performing an XNOR operation, i.e. seeing if the
                    #       two things equal each other's condition
                    if not (leftSpotPiece.isupper() ^ (not self.__isWhite)):
                        if self.__isLegalMove(
                            leftSpotPiece, 
                            Coordinate(finalPos.x, finalPos.y-1), 
                            Coordinate(self.__originalPos.x - int(delta.x/2),
                                       self.__originalPos.y), 
                            theoryBoard,
                            color = not self.__isWhite):
                            
                            leftAbleToTake = True
                if rightSpotPiece.upper() == "P":
                    if not (rightSpotPiece.isupper() ^ (not self.__isWhite)):
                        if self.__isLegalMove(
                            rightSpotPiece, 
                            Coordinate(finalPos.x, finalPos.y+1),
                            Coordinate(self.__originalPos.x - int(delta.x/2),
                                       self.__originalPos.y),
                            theoryBoard, 
                            color = not self.__isWhite):

                            rightAbleToTake = True
                if leftAbleToTake or rightAbleToTake:
                    self.__positionToEnPassant = Coordinate(
                        self.__originalPos.x - int(delta.x/2), 
                        self.__originalPos.y)

        # Records the new position
        self.__board.textUpdate(self.__activeCell.text, finalPos)

        # Remove the old position of the piece
        self.__board.textUpdate("-", self.__originalPos)

        # Manually assigns rook displacement
        if self.__activeCell.text.upper() == "K" and abs(delta.y) > 1:
            rookX = 0
            rookY = 0
            newRookY = 0

            # New rook positions
            if delta.y == -2:
                rookY = 7
                newRookY = 5
                if not self.__isPlayerWhite:
                    rookY = 0
                    newRookY = 2
            else: # Queenside
                rookY = 0
                newRookY = 3
                if not self.__isPlayerWhite:
                    rookY = 7
                    newRookY = 4
            if self.__isWhite:
                rookX = 7 if self.__isPlayerWhite else 0
                rookText = "R"
            else:
                rookX = 0 if self.__isPlayerWhite else 7
                rookText = 'r'

            # Moves the rook
            self.__board.moveto(
                self.__board.getCell(Coordinate(rookX, rookY)).record,
                getCanvasX(Coordinate(rookX, newRookY)),
                getCanvasY(Coordinate(rookX, newRookY)),
            )

            self.__board.textUpdate(rookText, Coordinate(rookX, newRookY))
            self.__board.textUpdate("-", Coordinate(rookX, rookY))

            # Removes castling rights after castling
            if self.__isWhite:
                self.__whiteKingCastle = False
                self.__whiteQueenCastle = False
            else:
                self.__blackKingCastle = False
                self.__blackQueenCastle = False             

        # Promotion updates
        if finalPos.x in [0, 7] and self.__activeCell.text.upper() == 'P':
            if promotionPiece is None:
                initialCell = self.__activeCell
                self.__promotionPopup(finalPos.y)
                while len(self.__promotionText) == 0:
                    for button in self.__promotionButtons:
                        button.update()

                self.__board.delete(self.__testWindow)

                # Needs to reassign because of mixing between canvas and
                # buttons
                self.__activeCell = initialCell
            else:
                self.__promotionText = promotionPiece

            self.__board.textUpdate(self.__promotionText, finalPos)
        
        gameState = self.__checkGameState(self.__board.getTextBoard())
        
        # Adds the last bit of the AN
        if finalPos.x in [0,7] and self.__activeCell.text.upper() == 'P':
            moveText += "="+self.__promotionText.upper()
            
            # Clears all promotion variables
            self.__promotionText = ""
            self.__promotionButtons = []
            self.__promotionImages = []                
        # Game end states
        if gameState == self.CHECK:
            moveText += '+'
        elif gameState == self.CHECKMATE:
            moveText += "#"
            self.__isGameActive = False
        elif gameState == self.DRAW:
            self.__isGameActive = False                    

        # Removes more castling rights if the king/rook move
        if self.__activeCell.text == "R":
            if self.__originalPos.y == (7 if self.__isPlayerWhite else 0):
                self.__whiteKingCastle = False
            elif self.__originalPos.y == (0 if self.__isPlayerWhite else 7):
                self.__whiteQueenCastle = False
        elif self.__activeCell.text == 'r':
            if self.__originalPos.y == (7 if self.__isPlayerWhite else 0):
                self.__blackKingCastle = False
            elif self.__originalPos.y == (0 if self.__isPlayerWhite else 7):
                self.__blackQueenCastle = False
        
        if self.__activeCell.text == "K":
            self.__whiteKingCastle = False
            self.__whiteQueenCastle = False
        if self.__activeCell.text == 'k':
            self.__blackKingCastle = False
            self.__blackQueenCastle = False

        # Forget the active piece
        self.__activeCell = Cell()

        # Updates the move text on the sidebar
        moveCounterText = self.__moveText.get()

        if self.__isWhite:
            whiteText = self.__whiteText.get()
            whiteText += moveText+"\n"
            self.__whiteText.set(whiteText)
        else:
            # if black starts, white needs to leave a gap
            if len(moveCounterText) == 0:
                self.__whiteText.set("\n") 
            blackText = self.__blackText.get()
            blackText += moveText + "\n"
            self.__blackText.set(blackText)

        if len(moveCounterText) == 0 or self.__isWhite:
            moveCounterText += str(self.__moveCounter) + ".\n"
        self.__moveText.set(moveCounterText)                        

        self.__moveHistory.append(moveText)

        self.__moveCounter += int(not self.__isWhite)

        # Change the color of the move
        self.__isWhite = not self.__isWhite

        # Adds the current board position for 3-fold reptition
        self.__boardHistory.append(copy.deepcopy(textBoard))

        path = "sfx/Move.mp3"

        if gameState in [self.DRAW, self.CHECKMATE]:
            path = "sfx/GenericNotify.mp3"
        elif 'x' in moveText:
            path = "sfx/Capture.mp3"
        
        playsound(getFile(path), False)

        self.__resetShapes()

        if self.__isWhite:
            self.__board.update_idletasks()
            
            # enginePlayer = Engine()
            # move = enginePlayer.getMove(self.__printFEN(None),depth = 23, threads = 4, hashSize = 4096)
            # self.pushMove(move)

            # databasePlayer = lichessPlayer(speeds = ["bullet", "blitz"], ratings=[1600, 1800])
            # move = databasePlayer.getMove(self.__printFEN(None))
            # self.pushMove(move)





    def __inCheck(self, isWhite, board):
        """ Determines on a board if there is a check """

        # Locates where your king is
        kingPosition = []
        for row in range(self.BOARD_LEN):
            for col in range(self.BOARD_LEN):
                if board[row][col] == ("K" if isWhite else 'k'):
                    kingPosition = Coordinate(row,col)

        # Sees if any piece can take the king
        for row in range(self.BOARD_LEN):
            for col in range(self.BOARD_LEN):
                # Checks for opponent piece
                if (isWhite and board[row][col].islower()) or (
                    not isWhite and board[row][col].isupper()):   
                    # Checks if a capture of a king is possible    
                    if self.__isLegalMove(board[row][col], 
                                          Coordinate(row, col),
                                          kingPosition, board, True):
                        return True
        return False

    def __checkGameState(self, board):
        """ Gets the state of the game """
        if board is None:
            board = self.__board.getTextBoard()

        abilityToMove = self.__canMove(board)
        inCheck = self.__inCheck(not self.__isWhite, board)

        if not abilityToMove:
            if inCheck:
                return self.CHECKMATE
            return self.STALEMATE
        
        if inCheck:
            return self.CHECK

        # Counts for insufficient materials
        whiteMinor = 0
        blackMinor = 0
        noOtherPieces = True
        for row in board:
            for piece in row:
                if piece.upper() in ['N', 'B']:
                    if piece.isupper():
                        whiteMinor += 1
                    else:
                        blackMinor += 1
                elif piece.upper() in ['R', 'P', 'Q']:
                    noOtherPieces = False
        if whiteMinor + blackMinor <= 1 and noOtherPieces:
            return self.DRAW

        if self.__halfMoveCounter == 100:
            return self.DRAW
        
        occurences = 0
        for seenBoard in self.__boardHistory:
            if board == seenBoard:
                occurences +=1
        if occurences == 2:
            return self.DRAW

    def __canMove(self, board = None):
        """ Determines if a player is able to move """
        if board is None:
            board = self.__board.getTextBoard()
        color = not self.__isWhite

        # Checks if any legal move is able to be made
        for row in range(self.BOARD_LEN):
            for col in range(self.BOARD_LEN):
                pieceLetter = board[row][col]
                if not pieceLetter == '-' and pieceLetter.isupper() == color:
                        for testRow in range(self.BOARD_LEN):
                            for testCol in range(self.BOARD_LEN):
                                if self.__isLegalMove(
                                    pieceLetter, 
                                    Coordinate(row, col), 
                                    Coordinate(testRow, testCol), 
                                    board, 
                                    color = color):

                                    return True
        return False

    def __moveToBasicAN(self, oldPos, newPos):
        """ Gets the base moves """

        textBoard = self.__board.getTextBoard()

        pieceText = textBoard[oldPos.x][oldPos.y]
        moveString = pieceText.upper() if not pieceText.upper() == 'P' else ""

        # is castling basically
        delta = Coordinate.getDifference(newPos, oldPos)

        if abs(delta.y) > 1 and pieceText.upper() == "K":
            if (delta.y > 0 and self.__isPlayerWhite) or (
                delta.y < 0 and not self.__isPlayerWhite):
                return "O-O"
            return "O-O-O"
        if pieceText.upper() in ["B", "R", "Q", "N"]:
            
            # Originally reserved for knight moves, but better for all
            # Should default to file as a disambiguator if possible
            legalPositions = []
            for row in range(self.BOARD_LEN):
                for col in range(self.BOARD_LEN):
                    if not (row == oldPos.x and col == oldPos.y):
                        if textBoard[row][col] == pieceText:
                            if self.__isLegalMove(pieceText, 
                                                  Coordinate(row, col), 
                                                  newPos, 
                                                  textBoard):
                                legalPositions.append(Coordinate(row, col))
                                colNum = oldPos.y if self.__isPlayerWhite \
                                                    else 7-oldPos.x
            fileText = "" # LETTER
            rankText = "" # NUMBER

            if len(legalPositions) != 0:
                colNum = oldPos.y if self.__isPlayerWhite else 7-oldPos.y
                rowNum = (8-oldPos.x) if self.__isPlayerWhite else (1+oldPos.x)
                xPositions = [position.x for position in legalPositions]
                yPositions = [position.y for position in legalPositions]
                sameRow = oldPos.x in xPositions
                sameCol = oldPos.y in yPositions

                if not sameCol:
                    fileText = self.numToLetter(colNum)
                elif sameRow and sameCol:
                    fileText = self.numToLetter(colNum)
                    rankText = str(rowNum)                    
                else:
                    rankText = str(rowNum)
            
            moveString += fileText + rankText

        # Capturing with pawns
        if (pieceText.upper() == "P" and abs(newPos.y - oldPos.y) == 1):
            moveString += self.numToLetter(
                oldPos.y if self.__isPlayerWhite else 7-oldPos.y) + 'x'
        # Captures with anything else
        if (not textBoard[newPos.x][newPos.y] 
                == '-' and not pieceText.upper() == 'P'):
            if self.__isWhite ^ textBoard[newPos.x][newPos.y].isupper():
                moveString += 'x'

        # Add new position to the text
        moveString += self.numToLetter(
            newPos.y if self.__isPlayerWhite else 7-newPos.y)
        moveString += str(8 - newPos.x if self.__isPlayerWhite else 1+newPos.x)

        return moveString

    def __rightClickEvent(self, event):
        """ Restores the board prior to clicking anything """
        if not self.__activeCell.isEmpty():

            # Centers the piece back to its original position
            self.__board.moveto(
                self.__board.getCell(self.__originalPos).record,
                getCanvasX(self.__originalPos), 
                getCanvasY(self.__originalPos))

            # Forget the active piece
            self.__activeCell = Cell()
        elif event is not None:
            self.__beginShapeDrawing(event)

    def __beginShapeDrawing(self, event):
        """ Records the inital coordinate that was right-clicked """
        x = event.x
        y = event.y

        self.__originalArrowCoordinate = Coordinate(
            (int(x/self.BOX_LEN)+0.5)*self.BOX_LEN,
            (int(y/self.BOX_LEN)+0.5)*self.BOX_LEN
        )
        
    def __finishShape(self, event):
        """ Completes the shape if possible, erases any duplicates """
        # This blocks if you right click and then left click
        if self.__originalArrowCoordinate is not None:
            x = event.x
            y = event.y    

            final = Coordinate(
                (int(x/self.BOX_LEN)+0.5)*self.BOX_LEN,
                (int(y/self.BOX_LEN)+0.5)*self.BOX_LEN
            )

            # Checks if the original and final square is the same
            if final.x == self.__originalArrowCoordinate.x and \
               final.y == self.__originalArrowCoordinate.y:
                # Checks and removes a duplicate circle
                if final.toTuple() in list(self.__activeCircles.keys()):
                    self.__board.delete(self.__activeCircles[final.toTuple()])
                    del self.__activeCircles[final.toTuple()]
                # Draws the circle, indexing the selected box
                else:
                    self.__activeCircles[final.toTuple()] = \
                        self.__board.drawCircleHighlight(final)
            # Arrow
            else:
                # Checks and removes a duplicate arrow
                if (self.__originalArrowCoordinate.toTuple(), final.toTuple())\
                                           in list(self.__activeArrows.keys()):
                    self.__board.delete(
                        self.__activeArrows[(
                            self.__originalArrowCoordinate.toTuple(), 
                            final.toTuple()
                            )]
                        )
                    del self.__activeArrows[
                        (self.__originalArrowCoordinate.toTuple(),
                         final.toTuple())]
                # Draws the arrow, indexing the original and final box
                else:
                    self.__activeArrows[
                        (self.__originalArrowCoordinate.toTuple(), 
                            final.toTuple())] = \
                         self.__board.drawArrow(self.__originalArrowCoordinate, 
                                                final)

            self.__originalArrowCoordinate = ()

    def __resetShapes(self):
        for arrow in list(self.__activeArrows.values()):
            self.__board.delete(arrow)
        for circle in list(self.__activeCircles.values()):
            self.__board.delete(circle)
        self.__activeArrows = {}
        self.__activeCircles = {}
        self.__originalArrowCoordinate = None

    def __promotionPopup(self, y_index):
        x_pixel = 0
        y_pixel = 0

        def makePromotionTextFunction(text):
            def promotionText():
                self.__promotionText = text
            return promotionText

        self.__frame = Frame(self.__base)

        # Top of the board, white
        promotionList = ['Q','N','R','B'] if self.__isWhite else \
                                                            ['q','n','r','b']

        # Bottom screen
        if self.__isWhite ^ self.__isPlayerWhite:
            promotionList.reverse()
            y_pixel = self.BOX_LEN * 4
        x_pixel = self.BOX_LEN * y_index
        for i in range(4):
            self.__promotionImages.append(
                self.__getPieceFromText(promotionList[i]))
            self.__promotionButtons.append(
                Button(self.__frame, bg = "White", borderwidth = 0,
                       highlightthickness=0,image = self.__promotionImages[i],
                       command = makePromotionTextFunction(promotionList[i])
                )
            )
            self.__promotionButtons[i].pack()
        self.__testWindow = self.__board.create_window(
            x_pixel,
            y_pixel,
            anchor = NW, 
            window = self.__frame
        )
        self.__board.update_idletasks()

    def __runAnalysis(self):
        # textBoard = self.__board.getTextBoard()

        if not os.path.exists("engine.exe"):
            self.__genericPopup("No engine found.", titleText="Error", 
                                buttonText="Okay")
        else:
            self.__engineEvalText.set("")
            self.__engineMoveText.set("")

            instance = Engine()
            engineOutput = instance.evaluate_at_position(self.__printFEN(None),
                                                         depth = 24, lines = 5, threads = 4, hashSize = 6144)
              
            for moveSuggestion in engineOutput:
                if len(moveSuggestion) == 0:
                    continue
                moveText = moveSuggestion.split(" ")[0]
                evalText = moveSuggestion.split(" ")[1]
                promotionPiece = None
                if len(moveText) == 5:
                    promotionPiece = moveText[-1]
                    if self.__isWhite:
                        promotionPiece = promotionPiece.upper()
                    moveText = moveText[:-1]

                endPosX = 8-int(moveText[-1])
                endPosY = self.letterToNum(moveText[-2])
                startPosX = 8-int(moveText[1])
                startPosY = self.letterToNum(moveText[0])                
                if not self.__isPlayerWhite:
                    startPosX = int(moveText[1])-1
                    startPosY = 7-self.letterToNum(moveText[0])
                    endPosX = 7-endPosX
                    endPosY = 7-endPosY

                textSAN = self.__getTheorheticalAN(
                    Coordinate(startPosX, startPosY), 
                    Coordinate(endPosX, endPosY), 
                    self.__board.getTextBoard(), 
                    promotionPiece
                    )
                
                if not self.__isWhite:
                    if evalText[0] == "-":
                        evalText = evalText[1:]
                    else:
                        evalText = "-"+evalText
                if "M" not in evalText:
                    evalText = f'{int(evalText)/100:1.2f}'
                
                if "-" not in evalText and "M" not in evalText:
                    evalText = "+"+evalText
            
                self.__engineEvalText.set(
                    self.__engineEvalText.get()+evalText+"\n")
                self.__engineMoveText.set(
                    self.__engineMoveText.get()+textSAN+"\n")
                
    def __printFEN(self, event):
        textBoard = self.__board.getTextBoard()
        if not self.__isPlayerWhite:
            for i in range(len(textBoard)):
                textBoard[i] = textBoard[i][::-1]
            textBoard = textBoard[::-1]

        fenString = ""
        
        positionString = ""
        for row in range(self.BOARD_LEN):
            dashCount = 0
            for col in range(self.BOARD_LEN):
                currentChar = textBoard[row][col]
                if currentChar == "-":
                    dashCount += 1
                elif not dashCount == 0:
                    positionString += str(dashCount) + currentChar
                    dashCount = 0
                else:
                    positionString += currentChar
                    dashCount = 0
            if not dashCount == 0:
                positionString += str(dashCount)
            if not row == 7:
                positionString += "/"
        
        fenString += positionString
        fenString += " "

        fenString += "w" if self.__isWhite else "b"
        fenString += " "

        if self.__whiteKingCastle:
            fenString += "K"
        if self.__whiteQueenCastle:
            fenString += "Q"
        if self.__blackKingCastle:
            fenString += "k"
        if self.__blackQueenCastle:
            fenString += "q"
        fenString += " "
        # Add new position to the text
        if not self.__positionToEnPassant is None:
            fenString += self.numToLetter(
                self.__positionToEnPassant[Y_INDEX] if self.__isPlayerWhite \
                    else 7-self.__positionToEnPassant[Y_INDEX])
            fenString += str(8 - self.__positionToEnPassant[X_INDEX] \
                                    if self.__isPlayerWhite \
                                    else 1+self.__positionToEnPassant[X_INDEX])
        else:
            fenString += "-"
        fenString += " "

        fenString += str(self.__halfMoveCounter)
        fenString += " "

        fenString += str(self.__moveCounter)

        return fenString

    # This is essentially a stripped version of __endMove but without
    # any GUI or actual board updates
    def __getTheorheticalAN(self, origin, final, board, promotionPiece = None):
        activePiece = board[origin.x][origin.y]

        # Records the piece being moved
        moveText = self.__moveToBasicAN(origin, final)

        # Calculates how far the piece has moved
        delta = Coordinate.getDifference(origin, final)
        if not self.__isPlayerWhite:
            delta.inverse()

        # Removes the pawn during an en passant
        if (abs(delta.x) == 1 and abs(delta.y) == 1 and \
        final == self.__positionToEnPassant and activePiece.upper() == "P"):
            pawn_x_index = final.x + (
                -1 if self.__isWhite ^ self.__isPlayerWhite else 1)
            board[pawn_x_index][final.y] = '-'

        board[final.x][final.y] = activePiece[:]
        board[origin.x][origin.y] = '-'

        # Manually assigns rook displacement
        if activePiece.upper() == "K" and abs(delta.y) > 1:

            # New rook positions
            if delta.y == -2:
                rookY = 7
                newRookY = 5
                if not self.__isPlayerWhite:
                    rookY = 0
                    newRookY = 2
            else: # Queenside
                rookY = 0
                newRookY = 3
                if not self.__isPlayerWhite:
                    rookY = 7
                    newRookY = 4
            if self.__isWhite:
                rookX = 7 if self.__isPlayerWhite else 0
                rookText = "R"
            else:
                rookX = 0 if self.__isPlayerWhite else 7
                rookText = 'r'

            board[rookX][newRookY] = rookText
            board[rookX][rookY] = '-'


        if promotionPiece is not None:
            board[final.x][final.y] = promotionPiece

        gameState = self.__checkGameState(board)
        
        # Adds the last bit of the AN
        if promotionPiece is not None:
            moveText += "=" + promotionPiece.upper()
    
        # Game end states
        if gameState == self.CHECK:
            moveText += '+'
        elif gameState == self.CHECKMATE:
            moveText += "#"
        
        return moveText

    def __genericPopup(self, text, titleText = "", buttonText = ""):
        popup = Tk()
        popup.wm_title(titleText)
        label = Label(popup, text = text)
        label.pack()
        b1 = Button(popup, text = buttonText, command = popup.destroy)
        b1.pack()
        popup.mainloop()

    def __download(self):
        self.__activeGames = downloader.downloadGames(self.__userData)        

    def __nextGame(self):
        activeGame = self.__activeGames.pop(0)
        self.__isPlayerWhite = activeGame['white']['username'] == self.__userData["USERNAME"]

        self.__activeGameMoves = downloader.parsePGN(activeGame['pgn'])

        self.__readFEN(self.DEFAULT_FEN, self.__isPlayerWhite)
        
        self.__blackText.set("")
        self.__whiteText.set("")
        self.__moveText.set("")
        self.__pgnIndex = 0
        self.__boardHistory = []

        # moveBranch = self.__whiteGameTree if self.__isPlayerWhite else self.__blackGameTree
        for move in self.__activeGameMoves:

            # Checks if the move is being made by you
            # moves by others will be appended w/o question
            yourMove = not self.__isWhite ^ self.__isPlayerWhite
            activeFEN = self.__printFEN(None)

            # NOTE: Instead of indexing by the full FEN, I'm choosing
            #       to just index by position + castling + en passant,
            #       but I'll just ignore the 50 mr and movecount.
            #       I doubt it matters.
            partialFEN = activeFEN.split(" ")[:4]
            cutFEN = ""
            for item in partialFEN:
                cutFEN += item + " "
            # please fix this later, removes the last space
            cutFEN = cutFEN[:-1]
            
            moveInfo = self.__moveToCoordinate(move)

            if yourMove:
                if cutFEN not in list(self.__playerGameTree.keys()): 
                    self.__playerGameTree[cutFEN] = []
                if move not in self.__playerGameTree[cutFEN]:
                    self.__activeArrows[(moveInfo["startPos"].toTuple(), moveInfo["endPos"].toTuple())] = self.__board.drawArrow(getCanvasFromBoardCoordinate(moveInfo["startPos"]), getCanvasFromBoardCoordinate(moveInfo["endPos"]))
                    self.__movePlayedText.set("Move played here was " + move+". Do you like it?")
                    self.__board.update_idletasks()
                    self.__runAnalysis()
                    self.__board.update_idletasks()
                    
                    while not self.__goFlag:
                        self.__board.update()
                    self.__goFlag = False

                    userRe = self.__betterMoveEntry.get()
                    if len(userRe) == 0:
                        self.__playerGameTree[cutFEN].append(move)
                    else:
                        self.__betterMoveEntry.delete(0, END)
                        # Prevents a duplicate entry
                        if not userRe in self.__playerGameTree[cutFEN]:
                            self.__playerGameTree[cutFEN].append(userRe)
                            
                        gameID = int(activeGame["url"].split("/")[-1])
                        self.__userData["CURRENT_GAME_ID"] = gameID
                        self.__userData["USER_TREE"] = self.__playerGameTree
                        self.__userData["OPPONENT_TREE"] = self.__opponentGameTree
                        with open("user.json", "w") as f:
                            json.dump(self.__userData, f)
                        return
                    
            else: 
                if cutFEN not in list(self.__opponentGameTree.keys()): 
                    self.__opponentGameTree[cutFEN] = []
                if move not in self.__opponentGameTree[cutFEN]:
                    self.__opponentGameTree[cutFEN].append(move)

            self.pushMove(move)
            self.__board.update_idletasks()
            time.sleep(0.5)

        # If the game terminates before you make a bad move,
        # dump everything and finish.            
        gameID = int(activeGame["url"].split("/")[-1])
        self.__userData["CURRENT_GAME_ID"] = gameID
        self.__userData["USER_TREE"] = self.__playerGameTree
        self.__userData["OPPONENT_TREE"] = self.__opponentGameTree
        with open("user.json", "w") as f:
            json.dump(self.__userData, f)
        return
            

    def __printPGN(self, event):
        print("pgn: ", end = " ")
        whiteList = self.__whiteText.get().split("\n")
        blackList = self.__blackText.get().split("\n")
        for i in range(len(whiteList)):
            print(str(i+1)+"."+whiteList[i]+" "+blackList[i], end = " ")
        print(self.__board.getTextBoard())
        print("\n")


    def __advancePGN(self, event):
        if self.__pgnIndex < len(self.__activeGameMoves):
            self.pushMove(self.__activeGameMoves[self.__pgnIndex])
    
    def __backtrackPGN(self, event):
        if self.__pgnIndex > 0:
            self.__pgnIndex -=1
            newState = copy.deepcopy(self.__pgnMemory[self.__pgnIndex])
            newBoard = newState.pop(0)
            currentBoard = self.__board.getTextBoard()
            for row in range(self.BOARD_LEN):
                for col in range(self.BOARD_LEN):
                    if not newBoard[row][col] == currentBoard[row][col]:
                        self.__board.textUpdate(
                            newBoard[row][col], Coordinate(row,col))
            self.__isWhite = newState.pop(0)
            self.__moveCounter = newState.pop(0)
            self.__halfMoveCounter = newState.pop(0)
            self.__positionToEnPassant = newState.pop(0)
            self.__whiteKingCastle = newState.pop(0)
            self.__blackKingCastle = newState.pop(0)
            self.__whiteQueenCastle = newState.pop(0)
            self.__blackQueenCastle = newState.pop(0)
            self.__boardHistory = newState.pop(0)
            self.__isGameActive = newState.pop(0)
            self.__whiteText.set(newState.pop(0))
            self.__blackText.set(newState.pop(0))
            self.__moveText.set(newState.pop(0))

    def pushMove(self, moveText, engineFlag = False):
        coordinates = self.__moveToCoordinate(moveText)

        self.__originalPos = coordinates["startPos"]
        endPos = coordinates["endPos"]
        promotionPiece = coordinates["promotionPiece"]
        self.__activeCell = copy.copy(self.__board.getCell(self.__originalPos))
        
        self.__endMove(endPos, promotionPiece)

    # The point of this is for SAN, LAN provided by engine is elsewhere
    def __moveToCoordinate(self, moveText):
        textBoard = self.__board.getTextBoard()

        # Strips the move of special characters
        moveText = moveText.replace("#","" ).replace("+", "").replace("x", "")

        # Converts castling text into a king move
        if "O-" in moveText:
            newMoveText = "K"
            if self.__isWhite:
                newMoveText += "g" if moveText == "O-O" else "c"
                newMoveText += "1"
            else:
                newMoveText += "g" if moveText == "O-O" else "c"
                newMoveText += "8"            

            moveText = newMoveText
        
        promotionPiece = None
        if "=" in moveText:
            promotionPiece = moveText[moveText.index("=")+1]
            if not self.__isWhite:
                promotionPiece = promotionPiece.lower()            
            moveText = moveText[:moveText.index("=")]
        # # Not actually sure if this is needed, hopefully not
        # moveText = moveText[0:4]

        pieceText = "P"
        if moveText[0].isupper():
            pieceText = moveText[0]
            moveText = moveText[1:]
        if not self.__isWhite:
            pieceText = pieceText.lower()

        self.__activeCell.text = pieceText


        endPosX = 8-int(moveText[-1])
        endPosY = self.letterToNum(moveText[-2])
        if not self.__isPlayerWhite:
            endPosX = 7-endPosX
            endPosY = 7-endPosY
        
        # if rank amd/or file was specified
        if len(moveText) > 2:
            if len(moveText) >= 4: #full AN
                startPosX = 8-int(moveText[1])
                startPosY = self.letterToNum(moveText[0])                
                if not self.__isPlayerWhite:
                    startPosX = int(moveText[1])-1
                    startPosY = 7-self.letterToNum(moveText[0])
                
            
            elif ord(moveText[0]) <= 57: # number, rank, check across y
                startPosX = 8-int(moveText[0])
                if not self.__isPlayerWhite:
                    startPosX = int(moveText[0])-1
                for i in range(self.BOARD_LEN):
                    if textBoard[startPosX][i] == pieceText:
                        if self.__isLegalMove(
                            pieceText, 
                            Coordinate(startPosX, i), 
                            Coordinate(endPosX, endPosY), 
                            textBoard):

                            startPosY = i

            else : # letter, file, check across x
                startPosY = self.letterToNum(moveText[0])
                if not self.__isPlayerWhite:
                    startPosY = 7-self.letterToNum(moveText[0])
                for i in range(8):
                    if textBoard[i][startPosY] == pieceText:
                        if self.__isLegalMove(
                            pieceText, 
                            Coordinate(i, startPosY), 
                            Coordinate(endPosX, endPosY), 
                            textBoard):

                            startPosX = i         
        else:
            for row in range(self.BOARD_LEN):
                for col in range(self.BOARD_LEN):
                    if textBoard[row][col] == pieceText:
                        if self.__isLegalMove(
                            pieceText, 
                            Coordinate(row, col), 
                            Coordinate(endPosX, endPosY), 
                            textBoard):
                            
                            startPosX = row
                            startPosY = col
        return {
            "startPos": Coordinate(startPosX, startPosY),
            "endPos": Coordinate(endPosX, endPosY),
            "promotionPiece": promotionPiece
        }
    
    @staticmethod
    def numToLetter(num):
        """ Converts a number from 0-7 to a letter, A-H """
        return chr(num+97)

    @staticmethod
    def letterToNum(chr):
        """ Converts a letter, A-H, to a number from 0-7 """
        return ord(chr) - 97

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

base = Tk()

base.title("Chess")

board = Game(base, Game.DEFAULT_FEN, True)

base.mainloop()