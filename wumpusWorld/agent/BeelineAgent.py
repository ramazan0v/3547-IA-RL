import random
import networkx as nx
import copy

from wumpusWorld.environment.Agent import *
from wumpusWorld.environment.Action import *
from wumpusWorld.environment.Percept import *
from wumpusWorld.environment.Coords import *


class BeelineEscape():
    '''
    This is the parent class of BeelineAgent class
    Has helper methods to guide the agent from the gold to the escape
    '''
    
    @staticmethod
    def coords2tup(coords: Coords):
        '''
        This function converts coords object into (x,y) tuple
        for NetworkX graph
        '''
        return (coords.x, coords.y)

    def buildSafeGraph(self):
        '''
        Takes locations visited by the agent as a list of Coords
        Returns shortest path (NetworkX package) based on the safe locations
        '''
        
        locs = self.agentVisitList
        curr_loc = locs[-1] #agent is at the last element of the list
        
        for i in range(len(locs)-1):
            '''
            ignore two consecutive locations when an agent did not move
            ignore if those two nodes already have a connecting edge: this is 
             to make sure agent always traces its steps back (unidirectional graph)
            '''
            if locs[i+1] != locs[i] and not \
               self.DG.has_edge(self.coords2tup(locs[i]), self.coords2tup(locs[i+1])):
                #assign the direction of the graph from the current to the previous location
                self.DG.add_edge(self.coords2tup(locs[i+1]), self.coords2tup(locs[i])) 
        return nx.shortest_path(self.DG, source=(curr_loc.x, curr_loc.y), target=(0,0))
        
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


class BeelineAgent(BeelineEscape):

  def __init__(self):
    super().__init__()
    self.DG = nx.DiGraph() #start a graph
    self.agentVisitList = [] #keep track of the locations visited
    self.escapePlanBuilt = False
    
  @staticmethod
  def create():
    return Agent()
  
    
  def nextAction(self, percept: Percept, agent: Agent):
    
    #At each step, keep track where the agent is
    #This will be the list of all SAFE locations
    self.agentVisitList.append(agent.location)
    
    actions = {
          0: Forward(),
          1: TurnLeft(),
          2: TurnRight(),
          3: Shoot()
    }
    actions_str = {
          0: 'Forward',
          1: 'TurnLeft',
          2: 'TurnRight',
          3: 'Shoot'
    }
    
    if percept.glitter and not agent.hasGold:
        print('Grab')
        chosen_act = Grab()
    elif agent.hasGold and agent.location == Coords(0,0):
        print('Climb')
        chosen_act = Climb()
    elif agent.hasGold and agent.location != Coords(0,0):
        #The first time the agent finds and grabs gold, build an escape route
        if not self.escapePlanBuilt:
            self.path = self.buildSafeGraph()
            print(self.path)
            self.escapePlanBuilt = True
            
        self.path, chosen_act = self.nextStep(self.path, agent.location, agent.orientation)
    else:
        randm_int = random.randint(0, 3)
        print(actions_str.get(randm_int))
        chosen_act = actions.get(randm_int)    
    
    return chosen_act