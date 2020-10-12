BOX_LEN = 95
X_INDEX = 0
Y_INDEX = 1

def getBoardX(event):
    """ Retrieves the board x-coordinate from a click event """
    return int(event.y/BOX_LEN)

def getBoardY(event):
    """ Retrieves the board y-coordinate from a click event """
    return int(event.x/BOX_LEN)

def getCanvasX(boardCoordinate):
    """ Retrieves canvas x-coordinate from board coordinates """
    return boardCoordinate[Y_INDEX]*BOX_LEN

def getCanvasY(boardCoordinate):
    """ Retrieves canvas y-coordinate from board coordinates """
    return boardCoordinate[X_INDEX]*BOX_LEN

def getNextCanvasX(boardCoordinate):
    """ Retrieves next canvas X-coordinate from board coordinates """
    return (boardCoordinate[Y_INDEX] + 1) * BOX_LEN

def getNextCanvasY(boardCoordinate):
    """ Retrieves next canvas Y-coordinate from board coordinates """
    return (boardCoordinate[X_INDEX] + 1) * BOX_LEN