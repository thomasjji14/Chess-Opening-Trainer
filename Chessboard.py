from tkinter import *
from Coordinate import *

class Chessboard(Canvas):
    BOARD_LEN = 8
    BOX_LEN = 95
    BROWN = "#B58863"
    LIGHT_BROWN = "#F0D9B5"
    SHORT_DISTANCE = 3/38*BOX_LEN 
    LONG_DISTANCE = BOX_LEN*0.34
    ARROW_BASE_DISTANCE = BOX_LEN/2.5
    CIRCLE_OUTLINE_LENGTH = 7.5

    def __init__(self, base):
        super(Chessboard,self).__init__(base, width = 760, height = 760, bg = 'White', highlightthickness=0)
        
        # Used to aternate colors
        lightBrownFlag = True

        for row in range(self.BOARD_LEN):
            for col in range(self.BOARD_LEN):
                coordinatePair = [row, col]
                super().create_rectangle(
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

    def drawArrow(self, point1, point2):
        deltaX = point2[X_INDEX]-point1[X_INDEX]
        deltaY = point2[Y_INDEX]-point1[Y_INDEX]
        hypotnuse = (deltaX ** 2 + deltaY ** 2) ** 0.5
        cosineVal = deltaX/hypotnuse
        sineVal = deltaY/hypotnuse 

        arrowBase = [point2[X_INDEX]-cosineVal*self.ARROW_BASE_DISTANCE, point2[Y_INDEX]-sineVal*self.ARROW_BASE_DISTANCE]
        points = [
            point1[X_INDEX]-self.SHORT_DISTANCE*sineVal, point1[Y_INDEX]+self.SHORT_DISTANCE*cosineVal,
            arrowBase[X_INDEX]-self.SHORT_DISTANCE*sineVal, arrowBase[Y_INDEX]+self.SHORT_DISTANCE*cosineVal,
            arrowBase[X_INDEX]-self.LONG_DISTANCE*sineVal, arrowBase[Y_INDEX]+self.LONG_DISTANCE*cosineVal,
            point2[X_INDEX], point2[Y_INDEX],
            arrowBase[X_INDEX]+self.LONG_DISTANCE*sineVal, arrowBase[Y_INDEX]-self.LONG_DISTANCE*cosineVal,
            arrowBase[X_INDEX]+self.SHORT_DISTANCE*sineVal, arrowBase[Y_INDEX]-self.SHORT_DISTANCE*cosineVal,
            point1[X_INDEX]+self.SHORT_DISTANCE*sineVal, point1[Y_INDEX]-self.SHORT_DISTANCE*cosineVal,
            ]

        return super().create_polygon(points, fill = "#6D9F58", stipple = "gray75")       
    
    def drawCircleHighlight(self, point, customWidth = 7.5):
        return super().create_oval(
                        point[X_INDEX]-0.5*self.BOX_LEN+customWidth/2,
                        point[Y_INDEX]-0.5*self.BOX_LEN+customWidth/2,
                        point[X_INDEX]+0.5*self.BOX_LEN-customWidth/2, 
                        point[Y_INDEX]+0.5*self.BOX_LEN-customWidth/2,
                        outline = "#6D9F58", width = customWidth)
