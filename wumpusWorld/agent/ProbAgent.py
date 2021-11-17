import random
import networkx as nx
import copy
from scipy.spatial.distance import euclidean

from wumpusWorld.environment.Agent import *
from wumpusWorld.environment.Action import *
from wumpusWorld.environment.Percept import *
from wumpusWorld.environment.Coords import *


class BeelineEscape():
    '''
    This is the parent class of ProbAgent class
    Has helper methods to guide the agent from the current cell to the target
    '''
    
    @staticmethod
    def coords2tup(coords: Coords):
        '''
        This function converts coords object into (x,y) tuple
        for NetworkX graph
        '''
        return (coords.x, coords.y)
    
    def listAllCells(self):
        '''
        Generates list of all cells in the grid
        '''
        cells = []
        for i in range(0, self.gridWidth):
            for j in range(0, self.gridHeight):
               cells.append(Coords(i,j))
        return cells
    
    def adjacentCells(self, coords: Coords):
        '''
        Given certain x,y coordinates, return a list of all adjacent cells (no diagonal cells)
        '''    
        toLeft = [Coords(coords.x - 1, coords.y)] if coords.x > 0 else []
        toRight = [Coords(coords.x + 1, coords.y)] if (coords.x < self.gridWidth - 1) else []
        below = [Coords(coords.x, coords.y - 1)] if (coords.y > 0) else []
        above = [Coords(coords.x, coords.y + 1)] if coords.y < self.gridHeight - 1 else []
        return toLeft + toRight + below + above
    
    
    def cellsInFront(self, agent_loc, orientation):
        '''
        Helper function to determine which cells lie in the direction the agent is facing
        To determine which cells will be affected by agent's arrow
        '''
        cells = []
        i = 0
        if orientation == 'East':
            while i < self.gridWidth - agent_loc.x - 1:
                i += 1
                cells.append(Coords(agent_loc.x + i, agent_loc.y))
        elif orientation == 'North':
            while i < self.gridHeight - agent_loc.y - 1:
                i += 1
                cells.append(Coords(agent_loc.x, agent_loc.y + i))
        elif orientation == 'West':
            while i < agent_loc.x:
                i += 1
                cells.append(Coords(agent_loc.x - i, agent_loc.y))
        elif orientation == 'South':
            while i < agent_loc.y:
                i += 1
                cells.append(Coords(agent_loc.x, agent_loc.y - i))
            
        return cells
    
    def buildSafeGraph(self, targetCell):
        '''
        Takes locations visited by the agent as a list of Coords
        Updates the shortest path (NetworkX package) based on the safe locations
        '''
        
        locs = self.agentVisitList
        curr_loc = locs[-1] #agent is at the last element of the list
        
        for i in range(len(locs)-1):
            '''
            ignore two consecutive locations when an agent did not move
            ignore if those two nodes already have a connecting edge
            '''
            if locs[i+1] != locs[i] and not \
               self.G.has_edge(self.coords2tup(locs[i]), self.coords2tup(locs[i+1])):
                #assign the direction of the graph from the current to the previous location
                self.G.add_edge(self.coords2tup(locs[i+1]), self.coords2tup(locs[i]))   
        
        #Sometimes the target cell might not have a node in the graph:
        # connect existing adjacent nodes to the target node
        if not self.G.has_node(self.coords2tup(targetCell)):
            for cell in self.adjacentCells(targetCell):
                cell = self.coords2tup(cell)
                if self.G.has_node(cell): self.G.add_edge(cell, self.coords2tup(targetCell))
                
        self.path = nx.shortest_path(self.G, source=(curr_loc.x, curr_loc.y), 
                                                target=self.coords2tup(targetCell))
        
    @staticmethod
    def direction(start: Coords, end: Coords):
        '''
        Compare 2 Locations
        Return the direction the agent should be facing
        '''
        
        if start.x == end.x:
            return 'North' if start.y < end.y else 'South'
        else:
            return 'East' if start.x < end.x else 'West'
    
    @staticmethod
    def angle(orientation):
        '''
        Assign angle for each direction for easier turning logic
        '''
        
        if orientation == 'East':
            return 0
        elif orientation == 'North':
            return 90
        elif orientation == 'West':
            return 180
        elif orientation == 'South':
            return 270
    
    
    def rotate(self, agent_orient, node_orient):
        '''
        Based on the angle definition above: 
        If the agent needs to turn -90 or 270 degrees => Means Left Turn
        If the agent needs to turn 90 or -270 degrees => Means Right Turn
        If the agent is facing the opposite direction (180 degrees) => Turn Left
         this will force the agent to turn left again in the next round
        '''
        
        if self.angle(agent_orient) - self.angle(node_orient) == -90 or \
           self.angle(agent_orient) - self.angle(node_orient) == 270:
           print('TurnLeft')
           return TurnLeft()
        elif self.angle(agent_orient) - self.angle(node_orient) == 90 or \
             self.angle(agent_orient) - self.angle(node_orient) == -270:
            print('TurnRight')
            return TurnRight()
        else:
            print('TurnLeft')
            return TurnLeft()
    
    
    def nextStep(self, path, agent_loc, agent_orient):
        '''
        if the agent is facing the direction of the next node => Move Forward
         and remove this step from the path list
        if not, turn in the direction it needs to go
        '''
        
        node_orient = self.direction(agent_loc, Coords(path[1][0], path[1][1]))
        if node_orient == agent_orient:
            print('Forward')
            return path[1:], Forward()
        else:
            return path, self.rotate(agent_orient, node_orient)


class ProbAgent(BeelineEscape):

  def __init__(self, pitModel, wumpusModel, gridWidth=4, gridHeight=4, tolerance=0.4):
    super().__init__()
    self.G = nx.Graph()
    self.G.add_node((0,0))
    self.gridWidth = gridWidth
    self.gridHeight = gridHeight
    
    self.agentVisitList = [] #keep track of the locations visited
    self.adjCellsNotVisited = [] #keep track of the closeby locations not visited
    
    self.wumpusStenchList = [[None] * (1 + 2 * gridWidth * gridHeight)] #keep track of the wumpus and stench percepts 
    self.pitBreezeList = [[None] * 2 * gridWidth * gridHeight] #keep track of the pit and breeze percepts 
    
    self.pitModel = pitModel
    self.wumpusModel = wumpusModel
    self.tolerance = tolerance #what's the risk tolerance of the agent
    
    self.chosen_act = None
    self.wumpusAlive = True
    self.hasArrow = True
    
  @staticmethod
  def create():
    return Agent()
    
    
  def shotIsLogical(self, agent_loc, agent_orient):
    '''
    Should Agent shoot:
    If the wumpus is dead or it doesn't have arrows -> No
    If the cells in front of the agent has wumpus probability > 49%
     and if this cell likely doesn't have a pit (otherwise it'll be a wasted move) -> Yes
    '''
    if not self.wumpusAlive or not self.hasArrow: return False
    for cell in self.cellsInFront(agent_loc, agent_orient):
        cell = self.coords2tup(cell)
        if self.wumpusBeliefs[cell] > 0.49 and self.pitBeliefs[cell] < 0.49:
            return True
    return False
  
  
  def safeCells(self, agent_loc):
    '''
    Returns listed of safe cells in this order: 
     1) least risky cells, 2) closest cells (Euclidean distance)
    '''
    
    safeCellDict = {}
    
    #Check adjacent cells: keep track of which ones we just discovered
    for cell in self.adjacentCells(agent_loc): 
        if cell not in self.agentVisitList and cell not in self.adjCellsNotVisited:
            self.adjCellsNotVisited.append(cell)
            
    #Remove already visited cells        
    self.adjCellsNotVisited = [x for x in self.adjCellsNotVisited if x not in self.agentVisitList]
    
    #Check if the pit and wumpus probabilities are both < tolerance in the adjacent cells
    #keep track of the probabilities and Euclidean distances for this cell
    for cell in self.adjCellsNotVisited:
        cell = self.coords2tup(cell)
        if max(self.wumpusBeliefs[cell], self.pitBeliefs[cell]) <= self.tolerance:
            safeCellDict[cell] = (max(self.wumpusBeliefs[cell], self.pitBeliefs[cell]),
                                  euclidean(self.coords2tup(agent_loc), cell))
    
    #Create the list from the dictionary above: 
    # sorted by tolerance and proximity to the current cell
    safeCellDict = sorted(safeCellDict, key=lambda k: (safeCellDict[k][0], safeCellDict[k][1]))
    return safeCellDict
  
    
  def generateWumpusBeliefs(self, percept, agent, didAgentShoot, model):
    '''
    generates Wumpus beliefs based on the new experiences
    '''
    wumpusBeliefs = {}
    
    if didAgentShoot:
        if percept.scream:
            #Means the Wumpus is dead: all cells have 0 probability 
            self.wumpusAlive = False
            allCells = self.listAllCells()
            wumpusBeliefs = {self.coords2tup(cell): 0.0 for cell in allCells}
        else:
            #Agent shot the arrow but missed: we can rule out wumpus being in the direction agent is facing
            cellsTested = self.cellsInFront(agent.location, agent.orientation)
            for cell in cellsTested: self.wumpusStenchList[0][1 + self.gridHeight * cell.x + cell.y] = 0 
            #Generate new probabilities given these cells didn't have the Wumpus
            wumpusProbas = model.predict_proba(self.wumpusStenchList)
            wumpusBeliefs = wumpusProbas[0][0].parameters[0]
    else:
        #If we are on a new cell, we can update that this cell has no Wumpus
        # and update if we perceive stench
        self.wumpusStenchList[0][1 + self.gridHeight * agent.location.x + agent.location.y] = 0 #No Wumpus
        self.wumpusStenchList[0][
            1 + self.gridWidth * self.gridHeight + self.gridHeight * agent.location.x + agent.location.y] = 1 if percept.stench else 0 #Breeze/No Breeze
        
        #Generate new probabilities given the new percepts
        wumpusProbas = model.predict_proba(self.wumpusStenchList)
        wumpusBeliefs = wumpusProbas[0][0].parameters[0]
    return wumpusBeliefs
    
    
  def generatePitBeliefs(self, percept, agent, model):
    '''
    generates Pit beliefs based on the new experiences
    '''
    pitBeliefs = {}
    
    #If we are still alive it means this cell didn't have the Pit
    self.pitBreezeList[0][self.gridHeight * agent.location.x + agent.location.y] = 0 #No Pit
    #Breeze/No Breeze
    self.pitBreezeList[0][
        self.gridWidth * self.gridHeight + self.gridHeight * agent.location.x + agent.location.y] = 1 if percept.breeze else 0 
    
    #Calculate new pit probabilities given the new information
    pitProbas = model.predict_proba(self.pitBreezeList)
    allCells = self.listAllCells()
    for i, cell in enumerate(allCells):
        if cell in self.agentVisitList:
            pitBeliefs[self.coords2tup(cell)] = 0
        else:
            pitBeliefs[self.coords2tup(cell)] = pitProbas[0][i].parameters[0][True]
    
    return pitBeliefs
    
    
  def nextAction(self, percept: Percept, agent: Agent):
    '''
    This function determines what should the ProbAgent do next given its belief states
    '''
    
    
    updateWumpusBeliefs = False; updatePitBeliefs = False
    #We only need to update pit beliefs if the agent moved into a brand new cell
    if agent.location not in self.agentVisitList:
        updatePitBeliefs = True
    #We only need to update Wumpus beliefs if the Wumpus is alive, and 
    #the agent has moved into a brand new cell or if it shot the arrow    
    if self.wumpusAlive and (agent.location not in self.agentVisitList or \
                             self.chosen_act.__class__.__name__ == 'Shoot'):
        updateWumpusBeliefs = True                          
    
    self.agentVisitList.append(agent.location)
    
    #Update the belief states if necessary
    if updatePitBeliefs: 
        self.pitBeliefs = self.generatePitBeliefs(percept, agent, self.pitModel)
    if updateWumpusBeliefs: 
        self.wumpusBeliefs = self.generateWumpusBeliefs(percept, agent, self.chosen_act.__class__.__name__ == 'Shoot', self.wumpusModel) 
            
            
    cellsToBeVisited = self.safeCells(agent.location) #generates safe cells and adds them to Graph
    
    if percept.glitter and not agent.hasGold:
        print('Grab')
        self.chosen_act = Grab()
    elif agent.hasGold and agent.location == Coords(0,0):
        print('Climb')
        self.chosen_act = Climb()
    elif agent.hasGold and agent.location != Coords(0,0):
        #If the agent finds and grabs the gold, build an escape route
        self.buildSafeGraph(targetCell=Coords(0,0)) 
        self.path, self.chosen_act = self.nextStep(self.path, agent.location, agent.orientation)
    elif self.shotIsLogical(agent.location, agent.orientation):
        #Agent decided to shoot
        print('Shoot')
        self.hasArrow = False
        self.chosen_act = Shoot()
    elif cellsToBeVisited == [] and agent.location == Coords(0,0):
        #If no safe cells exist at start or after moving around, climb
        print('Climb')
        self.chosen_act = Climb()
    elif cellsToBeVisited == [] and agent.location != Coords(0,0):
        #If no safe cells exist to move, build an escape plan
        self.buildSafeGraph(targetCell=Coords(0,0)) 
        self.path, self.chosen_act = self.nextStep(self.path, agent.location, agent.orientation)
    else:
        #Agent gooes exploring the grid
        self.buildSafeGraph(Coords(*cellsToBeVisited[0]))
        self.path, self.chosen_act = self.nextStep(self.path, agent.location, agent.orientation)
    return self.chosen_act