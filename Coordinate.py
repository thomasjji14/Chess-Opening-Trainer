class Coordinate():
    def __init__(self, x_index, y_index):
        self.x = x_index
        self.y = y_index
    
    def __eq__(self, other):
        if self is None or other is None:
            return False
        return self.x == other.x and self.y == other.y
    
    def toTuple(self):
        return (self.x,self.y)
    
    def inverse(self):
        self.x *= -1
        self.y *= -1

    @staticmethod
    def getDifference(firstCoordinate, secondCoordinate):
        return Coordinate(firstCoordinate.x-secondCoordinate.x, 
                          firstCoordinate.y-secondCoordinate.y)