from tkinter import *
import copy
from Coordinate import *
import sys
import os

class Chessboard:
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

    def __init__(self, base):
        """ Inits the Chessboard object from a Tkinter Base """
        
        self.__base = base
        self.__canvas = Canvas(base, width = 760, height = 760, 
                               bg = 'White')
        self.__canvas.pack(side = LEFT)


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

        # Bindings
        self.__base.bind('<B1-Motion>', self.__move)
        self.__base.bind('<Button-1>', self.__selectPiece)
        self.__base.bind('<ButtonRelease-1>', self.__deselectPiece)
        self.__base.bind('<Button-3>', self.__cancelMove)

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


    def drawBoard(self):
        """ Draws an 8x8 board with alternating colors """
        
        # Used to aternate colors
        lightBrownFlag = True

        for row in range(self.BOARD_LEN):
            for col in range(self.BOARD_LEN):
                coordinatePair = [row, col]
                self.__canvas.create_rectangle(
                    getCanvasX(coordinatePair), 
                    getCanvasY(coordinatePair), 
                    getNextCanvasX(coordinatePair),
                    getNextCanvasY(coordinatePair), 
                    fill = (self.LIGHT_BROWN if lightBrownFlag 
                        else self.BROWN), 
                    width = 0)

                # Color shifts on every column
                lightBrownFlag = not lightBrownFlag
            
            # Color shifts on every row
            lightBrownFlag = not lightBrownFlag

    def drawPieces(self):
        """ Draws the pieces when ran after readFEN or defaultBoard """
        for row in range(self.BOARD_LEN):
            for col in range(self.BOARD_LEN):
                coordinatePair = [row, col]
                if not self.__imageBoard[row][col] is None:    
                    self.__recordBoard[row][col] = self.__canvas.create_image(
                        getCanvasX(coordinatePair), 
                        getCanvasY(coordinatePair), 
                        image = self.__imageBoard[row][col], 
                        anchor = NW)



    def readFEN(self, FENCode):
        """ Takes in a FENCode and initializes the board """

        boardInfo = FENCode.split(' ')

        # Splits the FENCode into relevant information
        boardCode = boardInfo[0]
        currentColor = boardInfo[1]
        castlingRights = boardInfo[2]
        enPassantSquare = boardInfo[3]
        halfMoveCount = boardInfo[4]
        fullMoveCount = boardInfo[5]

        cleanedCode = ""
        numberList = ['1','2','3','4','5','6','7','8']

        # Converts numbers into dashes
        for index in range(len(boardCode)):
            if boardCode[index] in numberList:
                for repeats in range(int(boardCode[index])):
                    cleanedCode += '-'
            else:
                cleanedCode += FENCode[index]
        

        self.__textBoard = [list(row) for row in cleanedCode.split('/')]

        self.__createImages()

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






    def defaultBoard(self):
        self.readFEN('rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1')

    def __createImages(self):
        # Finds the images that is required to display
        for row in range(self.BOARD_LEN):
            for col in range(self.BOARD_LEN):
                pieceText = self.__textBoard[row][col]
                self.__imageBoard[row][col] = self.__getPieceFromText(pieceText)

    # Note, photoimages can only be created AFTER declaring a tkinter object
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


    def __move(self, event):
        """ Updates the piece to the mouse's position """
        if not self.__activePieceRecord is None:
            # Centers the piece on the mouse's center
            self.__canvas.moveto(
                self.__activePieceRecord, 
                event.x-int(self.BOX_LEN/2), 
                event.y-int(self.BOX_LEN/2))

    def __selectPiece(self, event):
        """ Determines the piece pressed, and marks the original position """

        if not self.__isGameActive:
            return

        # Gets the box that the mouse is in
        x_index = getBoardX(event)
        y_index = getBoardY(event)

        # Records the old position
        self.__originalPosition = [x_index, y_index]

        # Assigns the active piece to the piece that was clicked
        self.__activePieceRecord = copy.deepcopy(self.__recordBoard[x_index][y_index])
        self.__activePieceText = copy.copy(self.__textBoard[x_index][y_index])

        # This actually needs to be aliased
        self.__activePieceImage = self.__imageBoard[x_index][y_index]


    def __deselectPiece(self, event):
        """ Puts down the piece and marks its completion """

        # Gets the box that the mouse is in
        x_index = getBoardX(event)
        y_index = getBoardY(event)

        # Calculates the distances being moved by a piece
        # Note that deltaX is horizontal move, and deltaY is a vertial move
        deltaX = x_index - self.__originalPosition[X_INDEX]
        deltaY = y_index - self.__originalPosition[Y_INDEX]

        # Records the piece being moved
        moveText = self.__moveToBasicAN(self.__originalPosition, [x_index, y_index])

        # Checks if an actual piece is being pressed
        if not self.__activePieceRecord is None:

            # This converts castling with K over R, just converting the move to
            # K moving over two spaces horizontally
            if self.__activePieceText.upper() == 'K' and abs(deltaY) > 1:
                if deltaY == 3:
                    deltaY = 2
                    y_index = y_index - 1
                elif deltaY == -4:
                    deltaX = -2
                    y_index = y_index + 2

            
            # Chesks if the move is valid
            if self.__isLegalMove(self.__activePieceText, self.__originalPosition, [x_index, y_index], self.__textBoard):

                # Oly pawn moves or captures reset the board position
                if self.__activePieceText.upper() == "P" or not self.__textBoard[x_index][y_index] == '-':
                    self.__halfMoveCounter = 0
                    self.__moveHistory = []
                else:
                    self.__halfMoveCounter += 1

                # Centers the object onto the square it landed on
                self.__canvas.moveto(self.__activePieceRecord,getCanvasX([x_index, y_index]),getCanvasY([x_index, y_index]))

                # Visaually removes the old piece's image if it moved onto one 
                self.__canvas.delete(self.__recordBoard[x_index][y_index])
                # Removes the pawn during an en passant
                if abs(deltaX) == 1 and abs(deltaY) == 1 and [x_index, y_index] == self.__positionToEnPassant:
                    self.__canvas.delete(self.__recordBoard[x_index+ (1 if self.__isWhite else -1)][y_index])
                    self.__recordBoard[x_index + (1 if self.__isWhite else -1)][y_index] = None
                    self.__textBoard[x_index + (1 if self.__isWhite else -1)][y_index] = '-'
                    self.__imageBoard[x_index + (1 if self.__isWhite else -1)][y_index] = None
                    
                # Records the new position
                self.__recordBoard[x_index][y_index] = copy.deepcopy(
                    self.__activePieceRecord)
                self.__textBoard[x_index][y_index] = self.__activePieceText[:]

                # Remove the old position of the piece
                self.__recordBoard[self.__originalPosition[0]] \
                    [self.__originalPosition[1]] = None
                self.__textBoard[self.__originalPosition[0]] \
                    [self.__originalPosition[1]] = '-'
                
                # Imageboard copyies the reference of the image and deletes
                # the orignal
                self.__imageBoard[x_index][y_index] = self.__activePieceImage
                del self.__imageBoard[self.__originalPosition[0]][self.__originalPosition[1]]
                self.__imageBoard[self.__originalPosition[X_INDEX]].insert(self.__originalPosition[Y_INDEX], None)

                # When castling, the rook also has to move
                if self.__activePieceText.upper() == "K" and abs(deltaY) > 1:
                    rookX = 0
                    rookY = 0
                    newRookY = 0
                    rookText = 'r'

                    if deltaY == 2:
                        rookY = 7
                        newRookY = 5
                    else:
                        rookY = 0
                        newRookY = 3
                    if self.__isWhite:
                        rookX = 7
                        rookText = "R"
                    else:
                        rookX = 0
                        rookText = 'r'

                    rookRecord = copy.deepcopy(self.__recordBoard[rookX][rookY])

                    # moves the rook
                    self.__canvas.moveto(rookRecord,getCanvasX([rookX, newRookY]),getCanvasY([rookX, newRookY]))

                    # Records the new position
                    self.__recordBoard[rookX][newRookY] = rookRecord
                    self.__textBoard[rookX][newRookY] = rookText

                    # Remove the old position of the piece
                    self.__recordBoard[rookX][rookY] = None
                    self.__textBoard[rookX][rookY] = '-'

                    # Copies the rook image alias
                    self.__imageBoard[rookX][newRookY] = self.__imageBoard[rookX][rookY]
                    del self.__imageBoard[rookX][rookY]
                    self.__imageBoard[rookX].insert(rookY, None)

                    # Removes castling rights after castling
                    if self.__isWhite:
                        self.__whiteKingCastle = False
                        self.__blackKingCastle = False
                    else:
                        self.__blackKingCastle = False
                        self.__blackQueenCastle = False             

                # When promoting, mit has to create a new queen image and
                # change the visuals to match it
                if x_index in [0, 7] and self.__activePieceText.upper() == 'P':
                    self.__textBoard[x_index][y_index] = 'Q' if self.__isWhite else 'q' 
                    self.__imageBoard[x_index][y_index] = self.__getPieceFromText('Q' if self.__isWhite else 'q')
                    self.__recordBoard[x_index][y_index] = self.__canvas.create_image(getCanvasX([x_index,y_index]), getCanvasY([x_index,y_index]), image = self.__imageBoard[x_index][y_index], anchor = NW)


                # When a pawn moves two spaces, it records where the oponnent
                # can take en passant
                self.__positionToEnPassant = None
                if self.__activePieceText.upper() == 'P':
                    if abs(self.__originalPosition[self.X_INDEX] - x_index) == 2:
                        self.__positionToEnPassant = [(-1 if self.__isWhite else 1) + self.__originalPosition[self.X_INDEX], self.__originalPosition[self.Y_INDEX]]
                
                
                gameState = self.__checkGameState()
                
                # Adds the last bit of the AN
                if x_index in [0,7] and self.__activePieceText.upper() == 'P':
                    moveText += "=Q"
                
                # Game end states
                if gameState == self.CHECK:
                    moveText += '+'
                elif gameState == self.CHECKMATE:
                    moveText += "#"
                    print("CHECKMATE")
                    self.__isGameActive = False
                elif gameState == self.DRAW:
                    print("DRAWN")
                    self.__isGameActive = False                    

                # Removes more castling rights if the king/rook move
                # Rooks
                if self.__activePieceText == "R":
                    if self.__originalPosition[Y_INDEX] == 7:
                        self.__whiteKingCastle = False
                    elif self.__originalPosition[Y_INDEX] == 0:
                        self.__whiteQueenCastle = False
                elif self.__activePieceText == 'r':
                    if self.__originalPosition[Y_INDEX] == 7:
                        self.__blackKingCastle = False
                    elif self.__activePieceText == 0:
                        self.__blackQueenCastle = False
                
                # King
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
            else:
                self.__cancelMove(None)
                print("illogal move")

    def __cancelMove(self, event):
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

    def __isLegalMove(self, pieceText, oldPosition, newPosition, board, isTheorhetical = False, color = None):
        if color is None:
            color = self.__isWhite

        # Calculates how far the piece has moved
        deltaX = newPosition[X_INDEX] - oldPosition[X_INDEX]
        deltaY = newPosition[Y_INDEX] - oldPosition[Y_INDEX]



        # Makes sure that the person is moving on their own turn
        if not isTheorhetical:
            if not color == pieceText.isupper():
                # print("Illegal move: Not your turn")
                return False

        # Bounds detection
        if newPosition[X_INDEX] > 7 or newPosition[X_INDEX] < 0 or newPosition[Y_INDEX] > 7 or newPosition[Y_INDEX] < 0:
            # print("Illegal move: Out of bounds move")
            return False 
        
        
        # Makes sure you can't capture your own pieces
        if not isTheorhetical:
            if pieceText.isupper() == board[newPosition[X_INDEX]][newPosition[Y_INDEX]].isupper() and not self.__textBoard[newPosition[X_INDEX]][newPosition[Y_INDEX]] == '-':
                    return False

        # Doesn't count as a turn if you don't move your piece to another square
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
            if deltaY in [2, 3] and not (self.__whiteKingCastle if self.__isWhite else self.__blackKingCastle):
                return False
            # Queenside

            # Note that this is the queenside knight square which has to be checked
            if deltaY in [-2, -4] and not ((self.__whiteQueenCastle if self.__isWhite else self.__blackQueenCastle) and board[7 if self.__isWhite else 0][1] == '-'):
                return False 
            if deltaY in [-3, 4] or abs(deltaY) > 4:
                return False



        
        # Hybrid diagonal and horizontal of queen
        if pieceText.upper() == 'Q' and not (abs(deltaX) == abs(deltaY) or deltaX * deltaY == 0):
            return False

        # WHITE PAWN
        if pieceText == 'P':
            # Cannot move to a position that already has a piece on
            if ((deltaX == -1 or deltaX == -2) and deltaY == 0) and not board[newPosition[X_INDEX]][newPosition[Y_INDEX]] == '-':
                return False
            # Captures
            
            if (deltaX == -1 and abs(deltaY) == 1) and not (board[newPosition[X_INDEX]][newPosition[Y_INDEX]].islower() or (oldPosition[X_INDEX]== 3 and newPosition == self.__positionToEnPassant)):
                return False    

            # On home row, can move only 1 or 2 spaces
            if deltaX < -1 and not (oldPosition[X_INDEX] == 6 and deltaX == -2):
                return False
            if deltaX == -2 and not deltaY == 0:
                return False
            if abs(deltaY) > 1 or deltaX <-2:
                return False
            if deltaX >= 0:
                return False

        # BLACK PAWN
        if pieceText == 'p':
            # Cannot move to a position that already has a piece on
            if ((deltaX == 1 or deltaX == 2) and deltaY == 0) and not board[newPosition[X_INDEX]][newPosition[Y_INDEX]] == '-':
                return False
            if (deltaX == 1 and abs(deltaY) == 1) and not (board[newPosition[X_INDEX]][newPosition[Y_INDEX]].isupper() or (oldPosition[X_INDEX]== 4 and newPosition == self.__positionToEnPassant)):
                return False    
            # On home row, can move only 1 or 2 spaces
            if deltaX > 1 and not (oldPosition[X_INDEX] == 1 and deltaX == 2):
                return False
            if deltaX == 2 and not deltaY == 0:
                return False
            if abs(deltaY) > 1 or deltaX > 2:
                return False
            if deltaX <= 0:
                return False
            
      

        # Checks if the movement of the piece collides with anything on the way
        if pieceText.upper() in ['B', 'Q', 'R', 'K']:

            # Determines which direction to move towards
            xinc = 0 if deltaX == 0 else int(deltaX/(abs(deltaX)))
            yinc = 0 if deltaY == 0 else int(deltaY/(abs(deltaY)))
            tempPosition = copy.deepcopy(oldPosition)

            # Iterates from the old position to the new position to see if there
            # is a piece in the way
            tempPosition[X_INDEX] += xinc
            tempPosition[Y_INDEX] += yinc
            while not tempPosition == newPosition:
                if not board[tempPosition[X_INDEX]][tempPosition[Y_INDEX]] == '-':
                    return False

                tempPosition[X_INDEX] += xinc
                tempPosition[Y_INDEX] += yinc
        
        if not isTheorhetical:

            #Evaluates what the board might look like if the move is done
            theoryBoard = copy.deepcopy(board)
            theoryBoard[oldPosition[X_INDEX]][oldPosition[Y_INDEX]] = "-"
            theoryBoard[newPosition[X_INDEX]][newPosition[Y_INDEX]] = pieceText

            # Manually has to remove the en passanted pawn 
            if pieceText.upper() == 'P' and abs(deltaX) == 1 and abs(deltaY) == 1 and newPosition == self.__positionToEnPassant:
                theoryBoard[newPosition[X_INDEX] + (1 if color else - 1)][newPosition[Y_INDEX]] = "-"


            if self.__inCheck(color, theoryBoard):
                return False

            if pieceText.upper() == "K" and abs(deltaY) == 2:
                theoryBoard = copy.deepcopy(board)
                theoryBoard[oldPosition[X_INDEX]][oldPosition[Y_INDEX]] = "-"
                theoryBoard[newPosition[X_INDEX]][int(oldPosition[Y_INDEX]+deltaY/2)] = pieceText

                if self.__inCheck(color, theoryBoard):
                    return False

        return True

    def __inCheck(self, isWhite, board):
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
                if (isWhite and board[row][col].islower()) or (not isWhite and board[row][col].isupper()):   

                    # Checks if a capture of a king is possible    
                    if self.__isLegalMove(board[row][col], [row, col], kingPosition, board, True):
                        return True

        return False

    def __checkGameState(self):
        # Definitions:
        # Stalemate: Cannot make any moves but not in check
        # Checkmate: Cannot amke any moves and in check
        # 50 move: 50 moves without a capture or advance
        # 3fold: 3 identical baord states, including en passant differenences
        # resignation/draw agreements
        # insufficient
        # timeout???
        abilityToMove = self.__canMove()
        inCheck = self.__inCheck(not self.__isWhite, self.__textBoard)

        if not abilityToMove:
            if inCheck:
                return self.CHECKMATE
            return self.STALEMATE
        
        if inCheck:
            return self.CHECK

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

        return None

    def __canMove(self):
        color = not self.__isWhite
        for row in range(self.BOARD_LEN):
            for col in range(self.BOARD_LEN):
                pieceLetter = self.__textBoard[row][col]
                if not pieceLetter == '-' and pieceLetter.isupper() == color:
                        for testRow in range(self.BOARD_LEN):
                            for testCol in range(self.BOARD_LEN):
                                # if pieceLetter.upper() == 'P' and row == 3 and col == 7 and testRow == 2 and testCol == :
                                #     print('rb')
                                if self.__isLegalMove(pieceLetter, [row, col], [testRow, testCol], self.__textBoard, color = color):
                                    return True
        return False

    def __moveToBasicAN(self, oldPosition, newPosition):
        # for row in self.__textBoard:
        #     print(row)
        # print('\n')

        pieceText = self.__textBoard[oldPosition[X_INDEX]][oldPosition[Y_INDEX]]
        # moveString = chr(oldPosition[Y_INDEX]+41)
        moveString = pieceText.upper() if not pieceText.upper() == 'P' else ""

        # is castling basically
        deltaY = newPosition[Y_INDEX] - oldPosition[Y_INDEX]

        if abs(deltaY) > 1 and self.__activePieceText.upper() == "K":
            if deltaY > 0:
                return "O-O"
            return "O-O-O"
        if not pieceText.upper() == 'P':
            # Checking for the row number, mnumber
            for i in range(self.BOARD_LEN):
                #Exclude current column
                if not i == oldPosition[Y_INDEX]:
                    if self.__textBoard[oldPosition[X_INDEX]][i] == pieceText:
                        if self.__isLegalMove(pieceText, [oldPosition[X_INDEX], i], newPosition, self.__textBoard):
                            moveString += self.numToLetter(oldPosition[Y_INDEX])
                            break

            # Checking for the row number,letter
            for i in range(self.BOARD_LEN):
                if not i == oldPosition[X_INDEX]:
                    if self.__textBoard[i][oldPosition[Y_INDEX]] == pieceText:
                        if self.__isLegalMove(pieceText, [i, oldPosition[Y_INDEX]], newPosition, self.__textBoard):
                            moveString += str(8-oldPosition[X_INDEX])
                            break

        # Capturing with pawns
        if pieceText.upper() == "P" and abs(newPosition[Y_INDEX] - oldPosition[Y_INDEX]) == 1:
            moveString += self.numToLetter(oldPosition[Y_INDEX]) + 'x'
        # Captures with anything else
        if not self.__textBoard[newPosition[X_INDEX]][ newPosition[Y_INDEX]] == '-' and not pieceText.upper() == 'P':
            if self.__isWhite ^ self.__textBoard[newPosition[X_INDEX]][newPosition[Y_INDEX]].isupper():
                moveString += 'x'

        # Add new position to the text
        moveString += self.numToLetter(newPosition[Y_INDEX])
        moveString += str(8 - newPosition[X_INDEX])

        return moveString


# Checks are indicated by +
# Pawns don't use a symbol, unless they take, in which case the number is stated


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
        """ Get absolute path to resource, works for dev and for PyInstaller """
        try:
            # PyInstaller creates a temp folder and stores path in _MEIPASS
            base_path = sys._MEIPASS
        except Exception:
            base_path = os.path.abspath(".")

        return os.path.join(base_path, relative_path)

base = Tk()

base.title("Chess")


board = Chessboard(base)
board.drawBoard()

board.defaultBoard()

# board.readFEN('bk6/8/8/8/8/8/8/BK6 w KQkq - 90 1')

board.drawPieces()

base.mainloop()