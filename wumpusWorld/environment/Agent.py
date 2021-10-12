import copy
from wumpusWorld.environment.Coords import *

class Orientation():
  '''
  This class keeps track of agent's orientation
  Has a child class -> Agent
  If turnLeft -> switch into the previous orientation in the list
  If turnRight -> switch into the next orientation in the list
  '''
  def __init__(self, orientation = "East"):
    self.orient_list = ["North", "East", "South", "West", "North", "West"]
    self.orientation = orientation

  def turnLeft(self):
    ind = self.orient_list.index(self.orientation)
    self.orientation = self.orient_list[ind-1]

  def turnRight(self):
    ind = self.orient_list.index(self.orientation)
    self.orientation = self.orient_list[ind+1]
    
    
class Agent(Orientation):
    '''
    Keeps track of Agent's state within the environment - hidden from the agent itself
    
    '''
    def __init__(self, 
                 orientation = "East",
                 location = Coords(0, 0),
                 hasBumped = False,
                 hasGold = False,
                 hasArrow = True,
                 isAlive = True):
      super().__init__()
      self.location = location
      self.hasBumped = hasBumped
      self.hasGold = hasGold
      self.hasArrow = hasArrow
      self.isAlive = isAlive
    
    def forward(self, gridWidth: int, gridHeight: int):
      '''
      Depending on the orientation and initial location, move the agent into the next cell
      If the agent hits the wall, the agent hasBumped
      '''  
      prev_location = copy.copy(self.location)

      if self.orientation == "West":
        self.location = Coords(max(0, self.location.x - 1), self.location.y)
      elif self.orientation == "East":
        self.location = Coords(min(gridWidth - 1, self.location.x + 1), self.location.y)
      elif self.orientation == "South":
        self.location = Coords(self.location.x, max(0, self.location.y - 1), )
      elif self.orientation == "North":
        self.location = Coords(self.location.x, min(gridHeight - 1, self.location.y + 1), )

      self.hasBumped = prev_location == self.location
      
    def show(self):
      print("arrow: ", self.hasArrow, ", gold: ", self.hasGold, ", alive: ", 
            self.isAlive, ", orientation: ", self.orientation, sep="")