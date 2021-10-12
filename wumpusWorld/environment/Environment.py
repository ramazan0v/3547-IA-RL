import random
from wumpusWorld.environment.Agent import *
from wumpusWorld.environment.Percept import *
from wumpusWorld.environment.Action import *

class Environment():
  '''
  This class builds the board: generates a random wumpus location, gold location,
  pit locations, and keeps track of the state of the game
  '''  
  def __init__(self,
               pitLocations: list,
               wumpusLocation: Coords,
               goldLocation: Coords,
               gridWidth: int = 4,
               gridHeight: int = 4,
               pitProb: float = 0.2,
               allowClimbWithoutGold: bool = True,
               terminated: bool = False,
               wumpusAlive: bool = True):
    
    self.gridWidth = gridWidth
    self.gridHeight = gridHeight
    self.pitProb = pitProb
    self.allowClimbWithoutGold = allowClimbWithoutGold
    self.pitLocations = pitLocations
    self.terminated = terminated
    self.wumpusLocation = wumpusLocation
    self.wumpusAlive = wumpusAlive
    self.goldLocation = goldLocation

  def isPitAt(self, coords : Coords):
    return coords in self.pitLocations

  def isWumpusAt(self, coords: Coords):
    return self.wumpusLocation == coords

  def isAgentAt(self, agent: Agent, coords: Coords):
    return agent.location == coords

  def isGlitter(self, coords: Coords):
    return self.goldLocation == coords

  def isGoldAt(self, coords: Coords):
    return self.goldLocation == coords

  def killAttemptSuccessful(self, agent: Agent):
    '''
    Depending on the agent's location and orientation, check if the wumpus in in line of fire
    '''    
    if agent.orientation == "West":
      wumpusInLineOfFire = agent.location.x > self.wumpusLocation.x and agent.location.y == self.wumpusLocation.y
    elif agent.orientation == "East":
      wumpusInLineOfFire = agent.location.x < self.wumpusLocation.x and agent.location.y == self.wumpusLocation.y
    elif agent.orientation == "South":
      wumpusInLineOfFire = agent.location.x == self.wumpusLocation.x and agent.location.y > self.wumpusLocation.y
    elif agent.orientation == "North":
      wumpusInLineOfFire = agent.location.x == self.wumpusLocation.x and agent.location.y < self.wumpusLocation.y

    return wumpusInLineOfFire and agent.hasArrow and self.wumpusAlive

  def adjacentCells(self, coords: Coords):
    '''
    Given certain x,y coordinates, return a list of all adjacent cells (no diagonal cells)
    '''    
    toLeft = [Coords(coords.x - 1, coords.y)] if coords.x > 0 else []
    toRight = [Coords(coords.x + 1, coords.y)] if (coords.x < self.gridWidth - 1) else []
    below = [Coords(coords.x, coords.y - 1)] if (coords.y > 0) else []
    above = [Coords(coords.x, coords.y + 1)] if coords.y < self.gridHeight - 1 else []
    return toLeft + toRight + below + above

  def isPitAdjacent(self, coords: Coords):
    return any(cell in self.pitLocations for cell in self.adjacentCells(coords))

  def isWumpusAdjacent(self, coords: Coords):
    return self.wumpusLocation in self.adjacentCells(coords)

  def isBreeze(self, coords: Coords):
    return self.isPitAdjacent(coords)

  def isStench(self, coords: Coords):
    return self.isWumpusAdjacent(coords) or self.isWumpusAt(coords)
    
  def applyAction(self, percept: Percept, action: Action, agent: Agent):
    '''
    Lets the agent act only if the game is not terminated
    '''
    if self.terminated:
      percept = Percept(False, False, False, False, False, True, 0)
    else:
      self, percept, agent = action(self, percept, agent)
    return percept, agent

  def visualize(self, agent: Agent):
    '''
    Simple visualization of the game - show where are the pits, gold, wumpus and the agent
    If the wumpus is alive, show capital "W", if not, lower case "w"
    '''    
    wumpusSymbol = "W" if self.wumpusAlive else "w"
    s = ""
    for j in range(self.gridHeight-1, -1, -1):
      for i in range(self.gridWidth):
        s = s + "A" if self.isAgentAt(agent, Coords(i,j)) else s + " "
        s = s + "P" if self.isPitAt(Coords(i,j)) else s + " "
        s = s + "G" if self.isGoldAt(Coords(i,j)) else s + " "
        s = s + wumpusSymbol if self.isWumpusAt(Coords(i,j)) else s + " "
        s += "|"
      s += "\n"
    print(s)
  
  '''
  initialize the environment
  '''
  @staticmethod
  def create(gridWidth: int = 4,
             gridHeight: int = 4,
             pitProb: float = 0.2,
             allowClimbWithoutGold: bool = True):

    def randomLocationExceptOrigin():
      x = random.randint(0, gridWidth-1)
      y = random.randint(0, gridHeight-1)
      if x == 0 and y == 0:
        return randomLocationExceptOrigin()
      else:
        return Coords(x, y)
    
    def pitLocations():
      '''
      loops through each cell on the board (except the origin)
      puts the pit in the cell if the randomly generated
      number exceeds a given probability
      '''
      pitList = []
      for i in range(0, gridWidth):
        for j in range(0, gridHeight):
          if random.random() < pitProb and not (i==0 and j == 0):
           pitList.append(Coords(i,j))
      return pitList
    
    return Environment(gridWidth = gridWidth,
                        gridHeight = gridHeight,
                        pitProb = pitProb,
                        allowClimbWithoutGold = allowClimbWithoutGold,
                        pitLocations = pitLocations(),
                        terminated = False,
                        wumpusLocation = randomLocationExceptOrigin(),
                        wumpusAlive = True,
                        goldLocation = randomLocationExceptOrigin())