class Coords():
  '''
  This class is for storing x, y coordinates of WumpusWorld game board
  '''  
  def __init__(self, x, y):
    self.x = x
    self.y = y
    
  def __eq__(self, coords):
    '''
    Checks whether two coordinates point to the same place on the board
    '''
    return coords.x == self.x and coords.y == self.y