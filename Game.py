import copy
import sys
import os
from Chessboard import Chessboard
from tkinter import *
from Coordinate import *
from playsound import playsound
import time

class Game:
    BROWN = "#B58863"
    LIGHT_BROWN = "#F0D9B5"
    BOX_LEN = 95
    BOARD_LEN = 8
    X_INDEX = 0
    Y_INDEX = 1
    WHITE_INDEX = 0
    BLACK_INDEX = 1
    STALEMATE = "Stalemate"
    CHECKMATE = "Checkmate"
    CHECK = "Check"
    DRAW  = "Draw"
    DEFAULT_FEN = 'rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1'

    def __init__(self, base, FENCode, asWhite = True):
        """ Inits the Chessboard object from a Tkinter Base """

        # Tkinter object initailizers        
        self.__base = base
        self.__canvas = Chessboard(self.__base)
        self.__canvas.pack(side = LEFT)

        # Marks the movetext number and moves
        self.__blackText = StringVar("")
        self.__blackLabel = Label(base, textvariable = self.__blackText,
                                  justify = LEFT)
        self.__blackLabel.pack(side = RIGHT, anchor = NW)

        self.__whiteText = StringVar("")
        self.__whiteLabel = Label(base, textvariable = self.__whiteText,
                                  justify = LEFT)
        self.__whiteLabel.pack(side = RIGHT, anchor = NW)       

        self.__moveText = StringVar("")
        self.__moveLabel = Label(base, textvariable = self.__moveText,
                                 justify = LEFT)
        self.__moveLabel.pack(side = RIGHT, anchor = NW)

        # Tracks the board with characters (logic)
        self.__textBoard = [[None for i in range(self.BOARD_LEN)]
                            for i in range(self.BOARD_LEN)]
        # Tracks the board with image objects (image referencing)
        self.__imageBoard = [[None for i in range(self.BOARD_LEN)]
                             for i in range(self.BOARD_LEN)]
        # Tracks the board with references (drawn image references)
        self.__recordBoard = [[None for i in range(self.BOARD_LEN)]
                              for i in range(self.BOARD_LEN)]

        self.__promotionText = ""
        self.__promotionImages = []
        self.__promotionButtons = []

        # Bindings
        self.__base.bind('<B1-Motion>', self.__move)
        self.__base.bind('<Button-1>', self.__selectPiece)
        self.__base.bind('<ButtonRelease-1>', self.__deselectPiece)
        self.__base.bind('<Button-3>', self.__rightClickEvent)
        self.__base.bind('<ButtonRelease-3>', self.__finishShape)
        self.__base.bind('<Right>', self.__advancePGN)
        self.__base.bind('<Left>', self.__backtrackPGN)

        # Trackers for when pieces are moved
        self.__activePieceText = '-'
        self.__activePieceRecord = None
        self.__activePieceText = None
        self.__originalPosition = [-1,-1]

        # Boards 
        self.__moveHistory = []
        self.__boardHistory = []

        self.__isGameActive = True

        # FENCode fields
        self.__isWhite = True
        self.__moveCounter = 0
        self.__halfMoveCounter = 0
        self.__positionToEnPassant = None

        self.__whiteKingCastle = False
        self.__blackKingCastle = False
        self.__whiteQueenCastle = False
        self.__blackQueenCastle = False
    
        self.__isPlayerWhite = asWhite

        self.__activeArrows = {}
        self.__activeCircles = {}
        self.__originalArrowCoordinate = ()

        self.__readFEN(FENCode, asWhite)
        
        self.__drawPieces()

        sting = ""
        with open("test.txt", "rb") as f:
            sting = f.read()
        # print(sting)
        sting = str(sting)
        sting = sting.replace(".", ". ")
        moves = sting.split(" ")
        self.__newMoves = []
        for move in moves:
            if not "." in move:
                self.__newMoves.append(move.replace("'", ""))
        # print(self.__newMoves)

        self.__pgnMemory = []
        self.__pgnIndex = 0

    def __advancePGN(self, event):
        # print("Current index: "+str(self.__pgnIndex))

        # Board position needs to be saved
        # Every FEN field needs to be saved
        # Board history and if the game is active needs to be recorded
        self.__pgnMemory.append([copy.deepcopy(self.__textBoard),
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
        self.pushMove(self.__newMoves[self.__pgnIndex])
        
        self.__pgnIndex += 1
    
    def __backtrackPGN(self, event):
        newState = copy.deepcopy(self.__pgnMemory.pop())
        newBoard = newState.pop(0)
        for row in range(self.BOARD_LEN):
            for col in range(self.BOARD_LEN):
                if not newBoard[row][col] == self.__textBoard[row][col]:
                    coordinatePair = [row,col]
                    self.__imageBoard[row][col] =self.__getPieceFromText(newBoard[row][col])
                    self.__recordBoard[row][col] = self.__canvas.create_image(
                        getCanvasX(coordinatePair), 
                        getCanvasY(coordinatePair), 
                        image = self.__imageBoard[row][col], 
                        anchor = NW
                    )
        self.__textBoard = copy.deepcopy(newBoard)
        self.__pgnIndex -= 1

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
    def __drawPieces(self):
        """ Draws the pieces when ran after readFEN or defaultBoard """

        # Reads from the imageboard to draw
        for row in range(self.BOARD_LEN):
            for col in range(self.BOARD_LEN):
                coordinatePair = [row, col]
                if not self.__imageBoard[row][col] is None:    
                    self.__recordBoard[row][col] = self.__canvas.create_image(
                        getCanvasX(coordinatePair), 
                        getCanvasY(coordinatePair), 
                        image = self.__imageBoard[row][col], 
                        anchor = NW
                    )

    def __readFEN(self, FENCode, asWhite):
        """ Takes in a FENCode and initializes the board """
        boardInfo = FENCode.split(' ')

        # Splits the FENCode into relevant information
        boardCode = boardInfo[0]
        currentColor = boardInfo[1]
        castlingRights = boardInfo[2]
        enPassantSquare = boardInfo[3]
        halfMoveCount = boardInfo[4]
        fullMoveCount = boardInfo[5]

        if not asWhite:
            boardCode = boardCode[::-1]
        self.__isPlayerWhite = asWhite

        cleanedCode = ""
        numberList = ['1','2','3','4','5','6','7','8']

        # Converts numbers into dashes
        for index in range(len(boardCode)):
            if boardCode[index] in numberList:
                for repeats in range(int(boardCode[index])):
                    cleanedCode += '-'
            else:
                cleanedCode += boardCode[index]
        
        self.__textBoard = [list(row) for row in cleanedCode.split('/')]
        self.__createImages()

        # Assigns FEN fields to the class
        self.__isWhite = currentColor == 'w'

        if 'K' in castlingRights:
            self.__whiteKingCastle = True
        if 'Q' in castlingRights:
            self.__whiteQueenCastle = True
        if 'k' in castlingRights:
            self.__blackKingCastle = True
        if 'q' in castlingRights:
            self.__blackQueenCastle = True
        
        if not enPassantSquare == '-':
            letter = enPassantSquare[0]
            number = enPassantSquare[1]

            x_index = 8 - int(number)
            y_index = self.letterToNum(letter)

            self.__positionToEnPassant = [x_index, y_index]
        else:
            self.__positionToEnPassant = None

        self.__halfMoveCounter = int(halfMoveCount)
        self.__moveCounter = int(fullMoveCount)

    def __createImages(self):
        # Finds the images that is required to display
        for row in range(self.BOARD_LEN):
            for col in range(self.BOARD_LEN):
                pieceText = self.__textBoard[row][col]
                self.__imageBoard[row][col] =self.__getPieceFromText(pieceText)

    # Photoimages can only be created AFTER declaring a tkinter object
    def __getPieceFromText(self, pieceText):
        """ Maps the piece character to the piece's image """
        PIECE_IMAGE_MAP = {
            'p' : PhotoImage(file = self.resource_path('cpieces/bpawn.png')),
            'r' : PhotoImage(file = self.resource_path('cpieces/brook.png')),
            'b' : PhotoImage(file = self.resource_path('cpieces/bbishop.png')),
            'n' : PhotoImage(file = self.resource_path('cpieces/bknight.png')),
            'k' : PhotoImage(file = self.resource_path('cpieces/bking.png')),
            'q' : PhotoImage(file = self.resource_path('cpieces/bqueen.png')),

            'P' : PhotoImage(file = self.resource_path('cpieces/wpawn.png')),
            'R' : PhotoImage(file = self.resource_path('cpieces/wrook.png')),
            'B' : PhotoImage(file = self.resource_path('cpieces/wbishop.png')),
            'N' : PhotoImage(file = self.resource_path('cpieces/wknight.png')),
            'K' : PhotoImage(file = self.resource_path('cpieces/wking.png')),
            'Q' : PhotoImage(file = self.resource_path('cpieces/wqueen.png')),

            '-' : None
        }
        return PIECE_IMAGE_MAP[pieceText]

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

        # Gets the box that the mouse is in
        x_index = getBoardX(event)
        y_index = getBoardY(event)

        # Records the old position
        self.__originalPosition = [x_index, y_index]

        # Assigns the active piece to the piece that was clicked
        self.__activePieceRecord = copy.deepcopy(self.__recordBoard[x_index]
                                                                   [y_index])
        self.__activePieceText = copy.copy(self.__textBoard[x_index][y_index])
        self.__activePieceImage = self.__imageBoard[x_index][y_index]

    def __move(self, event):
        """ Updates the piece to the mouse's position """
        # Makes sure that a piece has been selected
        if not self.__activePieceRecord is None:
            # Centers the piece on the mouse's center
            self.__canvas.moveto(
                self.__activePieceRecord, 
                event.x-int(self.BOX_LEN/2), 
                event.y-int(self.BOX_LEN/2))
            self.__canvas.tag_raise(self.__activePieceRecord)

    def __deselectPiece(self, event):
        """ Puts down the piece and marks its completion """

        # Gets the box that the mouse is in
        x_index = getBoardX(event)
        y_index = getBoardY(event)

        # Calculates the distances being moved by a piece
        # deltaX represents horizontal move, and deltaY represents vertical
        deltaX = x_index - self.__originalPosition[X_INDEX]
        deltaY = y_index - self.__originalPosition[Y_INDEX]
        if self.__isPlayerWhite:
            deltaX *= -1
            deltaY *= -1

        # Checks if an actual piece is being pressed
        if not self.__activePieceRecord is None:

            # Converts K over R castling to a two-square king movement
            if self.__activePieceText.upper() == 'K' and abs(deltaY) > 1:
                if deltaY == -3:
                    deltaY = -2
                    y_index = ((y_index - 1) if self.__isPlayerWhite else (y_index+1))
                elif deltaY == 4:
                    deltaX = 2
                    y_index = ((y_index + 2) if self.__isPlayerWhite else (y_index-2))


            # Chesks if the move is valid
            if self.__isLegalMove(
                    self.__activePieceText, 
                    self.__originalPosition, 
                    [x_index, y_index], 
                    self.__textBoard):
                self.__endMove(x_index, y_index)
            else:
                self.__rightClickEvent(None)

    def __endMove(self, finalX, finalY):
        # Records the piece being moved
        moveText = self.__moveToBasicAN(self.__originalPosition,
                                        [finalX, finalY])

        # Calculates the distances being moved by a piece
        # deltaX represents horizontal move, and deltaY represents vertical
        deltaX = finalX - self.__originalPosition[X_INDEX]
        deltaY = finalY - self.__originalPosition[Y_INDEX]
        if self.__isPlayerWhite:
            deltaX *= -1
            deltaY *= -1

        # Only pawn moves or captures reset the board position
        if (self.__activePieceText.upper() == "P"
            or not self.__textBoard[finalX][deltaY] == '-'):
            self.__halfMoveCounter = 0
            self.__moveHistory = []
        else:
            self.__halfMoveCounter += 1

        # Centers the object onto the square it landed on
        self.__canvas.moveto(
            self.__activePieceRecord,
            getCanvasX([finalX, finalY]),
            getCanvasY([finalX, finalY]))

        # Removes old piece images on capture
        self.__canvas.delete(self.__recordBoard[finalX][finalY])
        # Removes the pawn during an en passant
        if (abs(deltaX) == 1 
                and abs(deltaY) == 1 
                and [finalX, finalY] == self.__positionToEnPassant):
            pawn_x_index = finalX + (-1 if self.__isWhite ^ self.__isPlayerWhite else 1)
            
            self.__canvas.delete(self.__recordBoard
                [finalX+ (1 if self.__isWhite else -1)][finalY])
            self.__recordBoard[pawn_x_index][deltaY] = None
            self.__textBoard[pawn_x_index][deltaY] = '-'
            self.__imageBoard[pawn_x_index][deltaY] = None
            
        # Records the new position
        self.__recordBoard[finalX][finalY] = copy.deepcopy(
            self.__activePieceRecord)
        self.__textBoard[finalX][finalY] = self.__activePieceText[:]

        # Remove the old position of the piece
        self.__recordBoard[self.__originalPosition[0]][
            self.__originalPosition[1]] = None
        self.__textBoard[self.__originalPosition[0]][
            self.__originalPosition[1]] = '-'
        
        # Copies reference of image and deletes the oriignal
        self.__imageBoard[finalX][finalY] = self.__activePieceImage
        del self.__imageBoard[self.__originalPosition[0]][
            self.__originalPosition[1]]
        self.__imageBoard[self.__originalPosition[X_INDEX]].insert(
            self.__originalPosition[Y_INDEX], None)

        # Manually assigns rook displacement
        if self.__activePieceText.upper() == "K" and abs(deltaY) > 1:
            rookX = 0
            rookY = 0
            newRookY = 0

            # New rook positions
            if deltaY == -2:
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

            rookRecord =copy.deepcopy(self.__recordBoard[rookX][rookY])

            # Moves the rook
            self.__canvas.moveto(
                rookRecord,getCanvasX([rookX, newRookY])
                ,getCanvasY([rookX, newRookY]))

            # Records the new position
            self.__recordBoard[rookX][newRookY] = rookRecord
            self.__textBoard[rookX][newRookY] = rookText

            # Remove the old position of the piece
            self.__recordBoard[rookX][rookY] = None
            self.__textBoard[rookX][rookY] = '-'

            # Copies the rook image alias
            self.__imageBoard[rookX][newRookY] = self.__imageBoard[
                rookX][rookY]
            del self.__imageBoard[rookX][rookY]
            self.__imageBoard[rookX].insert(rookY, None)

            # Removes castling rights after castling
            if self.__isWhite:
                self.__whiteKingCastle = False
                self.__whiteQueenCastle = False
            else:
                self.__blackKingCastle = False
                self.__blackQueenCastle = False             

        # Promotion updates
        if finalX in [0, 7] and self.__activePieceText.upper() == 'P':
            initalText = self.__activePieceText
            self.__promotionPopup(deltaY)
            while len(self.__promotionText) == 0:
                for button in self.__promotionButtons:
                    button.update()
            self.__canvas.delete(self.__testWindow)

            # Needs to reassign because of mixing between canvas and
            # buttons
            self.__activePieceText = initalText
    
            self.__textBoard[finalX][finalY] = (
                self.__promotionText)
            self.__imageBoard[finalX][finalY] = self.\
                __getPieceFromText(self.__promotionText)
            self.__recordBoard[finalX][finalY] = self.\
                __canvas.create_image(getCanvasX([finalX,finalY]),
                getCanvasY([finalX,finalY]),  
                image = self.__imageBoard[finalX][finalY],
                anchor = NW)


        # Records when the oponnent can take en passant
        self.__positionToEnPassant = None
        if self.__activePieceText.upper() == 'P':
            if abs(self.__originalPosition[self.X_INDEX] 
                    - finalX) == 2:
                self.__positionToEnPassant = [
                    (1 if (self.__isWhite ^ self.__isPlayerWhite) else -1) + \
                    self.__originalPosition[self.X_INDEX], 
                    self.__originalPosition[self.Y_INDEX]]
        
        
        gameState = self.__checkGameState()
        
        # Adds the last bit of the AN
        if finalX in [0,7] and self.__activePieceText.upper() == 'P':
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
        if self.__activePieceText == "R":
            if self.__originalPosition[Y_INDEX] == (7 if self.__isPlayerWhite else 0):
                self.__whiteKingCastle = False
            elif self.__originalPosition[Y_INDEX] == (0 if self.__isPlayerWhite else 7):
                self.__whiteQueenCastle = False
        elif self.__activePieceText == 'r':
            if self.__originalPosition[Y_INDEX] == (7 if self.__isPlayerWhite else 0):
                self.__blackKingCastle = False
            elif self.__originalPosition[Y_INDEX] == (0 if self.__isPlayerWhite else 7):
                self.__blackQueenCastle = False
        
        if self.__activePieceText == "K":
            self.__whiteKingCastle = False
            self.__whiteQueenCastle = False
        if self.__activePieceText == 'k':
            self.__blackKingCastle = False
            self.__blackQueenCastle = False

        # Forget the active piece
        self.__activePieceRecord = None
        self.__activePieceText = '-'
        self.__activePieceImage = None

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
        self.__boardHistory.append(copy.deepcopy(self.__textBoard))

        path = "sfx/Move.mp3"

        if gameState in [self.DRAW, self.CHECKMATE]:
            path = "sfx/GenericNotify.mp3"
        elif 'x' in moveText:
            path = "sfx/Capture.mp3"
        
        playsound(self.resource_path(path), False)


    def __rightClickEvent(self, event):
        """ Restores the board prior to clicking anything """
        if self.__activePieceRecord is not None:

            # Centers the piece back to its original position
            self.__canvas.moveto(
                self.__activePieceRecord, 
                getCanvasX(self.__originalPosition), 
                getCanvasY(self.__originalPosition))

            # Forget the active piece
            self.__activePieceRecord = None
            self.__activePieceText = '-'
            self.__activePieceImage = None
        else:
            self.__beginShapeDrawing(event)

    def __beginShapeDrawing(self, event):
        """ Records the inital coordinate that was right-clicked """
        x = event.x
        y = event.y

        self.__originalArrowCoordinate = (
            (int(x/self.BOX_LEN)+0.5)*self.BOX_LEN,
            (int(y/self.BOX_LEN)+0.5)*self.BOX_LEN
        )
        
    def __finishShape(self, event):
        """ Completes the shape if possible, erases any duplicates """
        # This blocks if you right click and then left click
        if not len(self.__originalArrowCoordinate) == 0:
            x = event.x
            y = event.y    

            final = (
                (int(x/self.BOX_LEN)+0.5)*self.BOX_LEN,
                (int(y/self.BOX_LEN)+0.5)*self.BOX_LEN
            )

            # Checks if the original and final square is the same
            if final[X_INDEX] == self.__originalArrowCoordinate[X_INDEX] and \
               final[Y_INDEX] == self.__originalArrowCoordinate[Y_INDEX]:
                # Checks and removes a duplicate circle
                if final in list(self.__activeCircles.keys()):
                    self.__canvas.delete(self.__activeCircles[final])
                    del self.__activeCircles[final]
                # Draws the circle, indexing the selected box
                else:
                    self.__activeCircles[final] = \
                        self.__canvas.drawCircleHighlight(final)
            # Arrow
            else:
                # Checks and removes a duplicate arrow
                if (self.__originalArrowCoordinate, final) in list(
                    self.__activeArrows.keys()):
                    self.__canvas.delete(
                        self.__activeArrows[
                            (self.__originalArrowCoordinate, final)]
                        )
                    del self.__activeArrows[
                        (self.__originalArrowCoordinate, final)]
                # Draws the arrow, indexing the original and final box
                else:
                    self.__activeArrows[
                        (self.__originalArrowCoordinate, final)] = \
                         self.__canvas.drawArrow(
                            self.__originalArrowCoordinate, final)

            self.__originalArrowCoordinate = ()

    def __resetShapes(self):
        for arrow in list(self.__activeArrows.values()):
            self.__canvas.delete(arrow)
        for circle in list(self.__activeCircles.values()):
            self.__canvas.delete(circle)
        self.__activeArrows = {}
        self.__activeCircles = {}
        self.__originalArrowCoordinate = ()


    def __promotionPopup(self, y_index):
        x_pixel = 0
        y_pixel = 0

        def makePromotionTextFunction(text):
            def promotionText():
                self.__promotionText = text
            return promotionText

        self.__frame = Frame(self.__base)

        # Top of the board, white
        promotionList = ['Q','N','R','B'] if self.__isWhite else ['q','n','r','b']

        # Bottom screen
        if self.__isWhite ^ self.__isPlayerWhite:
            promotionList.reverse()
            y_pixel = self.BOX_LEN * 4
        x_pixel = self.BOX_LEN*y_index
        
        for i in range(4):
            self.__promotionImages.append(self.__getPieceFromText(promotionList[i]))
            self.__promotionButtons.append(
                Button(self.__frame, bg = "White", borderwidth = 0,
                       highlightthickness = 0, image = self.__promotionImages[i],
                       command = makePromotionTextFunction(promotionList[i])
                )
            )
            self.__promotionButtons[i].pack()
        self.__testWindow = self.__canvas.create_window(
            x_pixel,
            y_pixel,
            anchor = NW, 
            window = self.__frame
        )
        self.__canvas.update_idletasks()

    def __isLegalMove(self, 
                      pieceText, 
                      oldPosition, 
                      newPosition, 
                      board, 
                      isTheorhetical = False, 
                      color = None):
        """ Checks the legality of a given move """
        if color is None:
            color = self.__isWhite

        # Calculates how far the piece has moved
        deltaX = newPosition[X_INDEX] - oldPosition[X_INDEX]
        deltaY = newPosition[Y_INDEX] - oldPosition[Y_INDEX]
        if not self.__isPlayerWhite:
            deltaX *= -1
            deltaY *= -1


        # Makes sure that the person is moving on their own turn
        if not isTheorhetical:
            if not color == pieceText.isupper():
                return False

        # Bounds detection
        if (newPosition[X_INDEX] > 7 or newPosition[X_INDEX] < 0 or 
                newPosition[Y_INDEX] > 7 or newPosition[Y_INDEX] < 0):
            return False 
        
        
        # Makes sure you can't capture your own pieces
        if not isTheorhetical:
            if (pieceText.isupper() == 
                    board[newPosition[X_INDEX]][newPosition[Y_INDEX]].isupper() 
                and not self.__textBoard[newPosition[X_INDEX]]
                                        [newPosition[Y_INDEX]] == '-'):
                    return False

        # Can't move onto the same square
        if oldPosition == newPosition:
            return False
        
        # -------------------- Piece movement --------------------
        # Diagonal on bishop
        if pieceText.upper() in 'B' and not abs(deltaX) == abs(deltaY):
            return False

        # Horizontal of rook
        if pieceText.upper() == 'R' and not deltaX * deltaY == 0:
            return False
            
        # L-Shape of knight
        if pieceText.upper() == 'N' and not abs(deltaX) * abs(deltaY) == 2:
            return False
        
        # 1 square movement of king
        if pieceText.upper() == "K":
            if abs(deltaX) > 1:
                return False
            # Kingside
            if deltaY == 2 and not (self.__whiteKingCastle 
                    if self.__isWhite else self.__blackKingCastle):
                return False
            
            # Queenside knight manually checked for rook movement
            knightX = 7 if self.__isWhite else 0
            knightY = 1
            if not self.__isPlayerWhite:
                knightX = 7-knightX
                knightY = 6

            if deltaY == -2 and not (
                    (self.__whiteQueenCastle 
                    if self.__isWhite else self.__blackQueenCastle) 
                    and board[knightX][knightY] == '-'):
                return False 
            if abs(deltaY) > 2:
                return False
            
            if abs(deltaY) == 2 and self.__inCheck(self.__isWhite,
                                                   self.__textBoard):
                return False

        # Hybrid diagonal and horizontal of queen
        if pieceText.upper() == 'Q' and not (abs(deltaX) == abs(deltaY) 
                                             or deltaX * deltaY == 0):
            return False

        # WHITE PAWN
        if pieceText == 'P':
            whitePawnHome = 6 if self.__isPlayerWhite else 1

            # Cannot move to a position that already has a piece on
            if ((deltaX == -1 or deltaX == -2) and deltaY == 0
                    and not board[newPosition[X_INDEX]][newPosition[Y_INDEX]] 
                    == '-'):
                return False
            # Captures
            if ((deltaX == -1 and abs(deltaY) == 1) and not 
                (board[newPosition[X_INDEX]]
                        [newPosition[Y_INDEX]].islower() 
                or (oldPosition[X_INDEX]==(3 if self.__isPlayerWhite else 4) 
                        and newPosition == self.__positionToEnPassant))):
                return False    
            # On home row, can move only 1 or 2 spaces
            if deltaX <-1 and not (
                oldPosition[X_INDEX] == whitePawnHome and deltaX == -2):
                return False
            if deltaX == -2 and not deltaY == 0:
                return False
            if abs(deltaY) > 1 or deltaX <-2:
                return False
            if deltaX >= 0:
                return False

        # BLACK PAWN
        if pieceText == 'p':
            blackPawnHome = 1 if self.__isPlayerWhite else 6

            # Cannot move to a position that already has a piece on
            if ((deltaX == 1 or deltaX == 2) and deltaY == 0
                    and not board[newPosition[X_INDEX]]
                                 [newPosition[Y_INDEX]] == '-'):
                return False

            # Captures
            if ((deltaX == 1 and abs(deltaY) == 1) and not 
                (board[newPosition[X_INDEX]]
                        [newPosition[Y_INDEX]].isupper() 
                or (oldPosition[X_INDEX]== (4 if self.__isPlayerWhite else 3) 
                        and newPosition == self.__positionToEnPassant))):
                return False    
            # On home row, can move only 1 or 2 spaces
            if deltaX > 1 and not (
                oldPosition[X_INDEX] == blackPawnHome and deltaX == 2):
                return False
            if deltaX == 2 and not deltaY == 0:
                return False
            if abs(deltaY) > 1 or deltaX > 2:
                return False
            if deltaX <= 0:
                return False

        # Checks for collisions on the way
        if not pieceText.upper() == 'N':

            # Determines which direction to move towards
            xinc = 0 if deltaX == 0 else int(deltaX/(abs(deltaX)))
            yinc = 0 if deltaY == 0 else int(deltaY/(abs(deltaY)))

            # Increments need to reverse signs because the logic is
            # messed up with reverse FENs
            if not self.__isPlayerWhite:
                xinc *= -1
                yinc *= -1

            tempPosition = copy.deepcopy(oldPosition)

            # Looks for if there's a piece in the way
            tempPosition[X_INDEX] += xinc
            tempPosition[Y_INDEX] += yinc
            while not tempPosition == newPosition:
                if not board[tempPosition[X_INDEX]][
                        tempPosition[Y_INDEX]] == '-':
                    return False

                tempPosition[X_INDEX] += xinc
                tempPosition[Y_INDEX] += yinc
        
        # Checks for legalities after a move
        if not isTheorhetical:
            # Checks what it might look like if the move were made
            theoryBoard = copy.deepcopy(board)
            theoryBoard[oldPosition[X_INDEX]][oldPosition[Y_INDEX]] = "-"
            theoryBoard[newPosition[X_INDEX]][newPosition[Y_INDEX]] = pieceText
            #TODO TODO TODO
            # Manually has to remove the en passanted pawn 
            if (pieceText.upper() == 'P' and abs(deltaX) == 1 
                    and abs(deltaY) == 1 
                    and newPosition == self.__positionToEnPassant):
                theoryBoard[newPosition[X_INDEX] + (
                    -1 if color ^ self.__isPlayerWhite else 1)
                    ][newPosition[Y_INDEX]] = "-"

            # Makes sure you don't self-discovered check yourself
            if self.__inCheck(color, theoryBoard):
                return False

            # Makes sure you can't castle through check
            if pieceText.upper() == "K" and abs(deltaY) == 2:
                theoryBoard = copy.deepcopy(board)
                theoryBoard[oldPosition[X_INDEX]][oldPosition[Y_INDEX]] = "-"
                theoryBoard[newPosition[X_INDEX]
                    ][int((oldPosition[Y_INDEX]+newPosition[Y_INDEX])/2)] = \
                                                                    pieceText

                if self.__inCheck(color, theoryBoard):
                    return False

        return True

    def __inCheck(self, isWhite, board):
        """ Determines on a board if there is a check """

        # Locates where your king is
        kingPosition = []
        for row in range(self.BOARD_LEN):
            for col in range(self.BOARD_LEN):
                if board[row][col] == ("K" if isWhite else 'k'):
                    kingPosition = [row, col]

        # Sees if any piece can take the king
        for row in range(self.BOARD_LEN):
            for col in range(self.BOARD_LEN):
                # Checks for opponent piece
                if (isWhite and board[row][col].islower()) or (
                    not isWhite and board[row][col].isupper()):   
                    # Checks if a capture of a king is possible    
                    if self.__isLegalMove(board[row][col], [row, col],
                            kingPosition, board, True):
                        return True
        return False

    def __checkGameState(self):
        """ Gets the state of the game """

        abilityToMove = self.__canMove()
        inCheck = self.__inCheck(not self.__isWhite, self.__textBoard)

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
        for row in self.__textBoard:
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
        for board in self.__boardHistory:
            if self.__textBoard == board:
                occurences +=1
        if occurences == 2:
            return self.DRAW

    def __canMove(self):
        """ Determines if a player is able to move """
        color = not self.__isWhite

        # Checks if any legal move is able to be made
        for row in range(self.BOARD_LEN):
            for col in range(self.BOARD_LEN):
                pieceLetter = self.__textBoard[row][col]
                if not pieceLetter == '-' and pieceLetter.isupper() == color:
                        for testRow in range(self.BOARD_LEN):
                            for testCol in range(self.BOARD_LEN):
                                if self.__isLegalMove(pieceLetter, [row, col],
                                        [testRow, testCol],
                                        self.__textBoard, color = color):
                                    return True
        return False

    def __moveToBasicAN(self, oldPosition, newPosition):
        """ Gets the base moves """

        pieceText = self.__textBoard[oldPosition[X_INDEX]][
                                     oldPosition[Y_INDEX]]
        moveString = pieceText.upper() if not pieceText.upper() == 'P' else ""

        # is castling basically
        deltaY = newPosition[Y_INDEX] - oldPosition[Y_INDEX]

        if abs(deltaY) > 1 and self.__activePieceText.upper() == "K":
            if (deltaY > 0 and self.__isPlayerWhite) or (
                deltaY < 0 and not self.__isPlayerWhite):
                return "O-O"
            return "O-O-O"
        if pieceText.upper() in ["B", "R", "Q", "N"]:
            # Checking for the row number, letter
            for i in range(self.BOARD_LEN):
                #Exclude current column
                if not i == oldPosition[Y_INDEX]:
                    if self.__textBoard[oldPosition[X_INDEX]][i] == pieceText:
                        # If it finds a legal move that can be done on
                        # another file, then the letter must be appended
                        if self.__isLegalMove(pieceText, 
                                              [oldPosition[X_INDEX], i],
                                              newPosition,
                                              self.__textBoard):
                            num = oldPosition[Y_INDEX] if self.__isPlayerWhite else 7-oldPosition[Y_INDEX]
                            moveString += self.numToLetter(num)
                            break

            # Checking for the row number,letter
            for i in range(self.BOARD_LEN):
                if not i == oldPosition[X_INDEX]:
                    # Exclude current row
                    if self.__textBoard[i][oldPosition[Y_INDEX]] == pieceText:
                        # If it finds a legal move that can be done on
                        # another rank, then the number must be appended
                        if self.__isLegalMove(pieceText, 
                                              [i, oldPosition[Y_INDEX]], 
                                              newPosition, 
                                              self.__textBoard):
                            letter = str(8-oldPosition[X_INDEX]) if self.__isPlayerWhite else str(1+oldPosition[X_INDEX])
                            moveString += letter
                            break
            
            # Manual addition to knight's ambiguous moves, defaults to
            # file if another knight can move to the same spot but is
            # not on the same file/rank to begin with
            if pieceText.upper() == "N" and len(moveString) == 1:
                for row in range(self.BOARD_LEN):
                    for col in range(self.BOARD_LEN):
                        if not row == oldPosition[X_INDEX] and not col == oldPosition[Y_INDEX]:
                            if self.__textBoard[row][col] == pieceText:
                                if self.__isLegalMove(pieceText, [row,col], newPosition, self.__textBoard):
                                    num = oldPosition[Y_INDEX] if self.__isPlayerWhite else 7-oldPosition[Y_INDEX]
                                    moveString += self.numToLetter(num)
                                    break


        # Capturing with pawns
        if (pieceText.upper() == "P" and 
                abs(newPosition[Y_INDEX] - oldPosition[Y_INDEX]) == 1):
            moveString += self.numToLetter(oldPosition[Y_INDEX] if self.__isPlayerWhite else 7-oldPosition[Y_INDEX]) + 'x'
        # Captures with anything else
        if (not self.__textBoard[newPosition[X_INDEX]][newPosition[Y_INDEX]] 
                == '-' and not pieceText.upper() == 'P'):
            if self.__isWhite ^ self.__textBoard[newPosition[X_INDEX]][
                    newPosition[Y_INDEX]].isupper():
                moveString += 'x'

        # Add new position to the text
        moveString += self.numToLetter(newPosition[Y_INDEX] if self.__isPlayerWhite else 7-newPosition[Y_INDEX])
        moveString += str(8 - newPosition[X_INDEX] if self.__isPlayerWhite else 1+newPosition[X_INDEX])

        return moveString

    def pushMove(self, moveText):


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


        pieceText = "P"
        if moveText[0].isupper():
            pieceText = moveText[0]
            moveText = moveText[1:]
        if not self.__isWhite:
            pieceText = pieceText.lower()

        self.__activePieceText = pieceText

        endPosX = 8-int(moveText[-1])
        endPosY = self.letterToNum(moveText[-2])
        if not self.__isPlayerWhite:
            endPosX = 7-endPosX
            endPosY = 7-endPosY
        
        # if rank amd/or file was specified
        if len(moveText) > 2:
            if len(moveText) == 4: #full AN
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
                    if self.__textBoard[startPosX][i] == pieceText:
                        if self.__isLegalMove(pieceText, [startPosX, i], [endPosX, endPosY], self.__textBoard):
                            startPosY = i

            else : # letter, file, check across x
                startPosY = self.letterToNum(moveText[0])
                if not self.__isPlayerWhite:
                    startPosY = 7-self.letterToNum(moveText[0])
                for i in range(8):
                    if self.__textBoard[i][startPosY] == pieceText:
                        if self.__isLegalMove(pieceText, [i, startPosY], [endPosX, endPosY], self.__textBoard):
                            startPosX = i         
        else:
            for row in range(self.BOARD_LEN):
                for col in range(self.BOARD_LEN):
                    if self.__textBoard[row][col] == pieceText:
                        if self.__isLegalMove(pieceText, [row, col], [endPosX, endPosY], self.__textBoard):
                            startPosX = row
                            startPosY = col

        self.__originalPosition = [startPosX, startPosY]

        # Assigns the active piece to the piece that was clicked
        self.__activePieceRecord = copy.deepcopy(self.__recordBoard[startPosX]
                                                                    [startPosY])
        self.__activePieceImage = self.__imageBoard[startPosX][startPosY]                
        
        self.__endMove(endPosX, endPosY)

    @staticmethod
    def numToLetter(num):
        """ Converts a number from 0-7 to a letter, A-H """
        return chr(num+97)

    @staticmethod
    def letterToNum(chr):
        """ Converts a letter, A-H, to a number from 0-7 """
        return ord(chr) - 97

    # CREDITS TO max OF Stackoverflow
    @staticmethod
    def resource_path(relative_path):
        """ Get absolute path for PyInstaller """
        try:
            # PyInstaller creates a temp folder and stores path in _MEIPASS
            base_path = sys._MEIPASS
        except Exception:
            base_path = os.path.abspath(".")

        return os.path.join(base_path, relative_path)

base = Tk()

base.title("Chess")


board = Game(base, Game.DEFAULT_FEN, True)




# board = Game(base, "k7/8/8/8/5Q2/8/3Q1Q2/K7 w - - 0 1")
# board = Game(base, "rnbqkbnr/pp3ppp/3p4/2p1p3/3PP3/5N2/PPP2PPP/RNBQKB1R w KQkq - 0 4")

# board.pushMove("e2e4")
# board.pushMove("Ng8f6")

# board.pushMove("Q4d4")

base.mainloop()