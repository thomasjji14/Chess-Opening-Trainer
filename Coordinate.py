BOX_LEN = 95
X_INDEX = 0
Y_INDEX = 1

def getBoardX(event):
    return int(event.y/BOX_LEN)

def getBoardY(event):
    return int(event.x/BOX_LEN)

def getCanvasX(boardCoordinate):
    return boardCoordinate[Y_INDEX]*BOX_LEN

def getCanvasY(boardCoordinate):
    return boardCoordinate[X_INDEX]*BOX_LEN

def getNextCanvasX(boardCoordinate):
    return (boardCoordinate[Y_INDEX] + 1) * BOX_LEN

def getNextCanvasY(boardCoordinate):
    return (boardCoordinate[X_INDEX] + 1) * BOX_LEN