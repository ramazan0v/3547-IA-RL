import random
import networkx as nx
import copy

from wumpusWorld.environment.Agent import *
from wumpusWorld.environment.Action import *
from wumpusWorld.environment.Percept import *
from wumpusWorld.environment.Coords import *


class BeelineEscape():
    
    @staticmethod
    def direction(start: Coords, end: Coords):
        if start.x == end.x:
            return 'North' if start.y < end.y else 'South'
        else:
            return 'East' if start.x < end.x else 'West'
    
    @staticmethod
    def angle(orientation):
        if orientation == 'East':
            return 0
        elif orientation == 'North':
            return 90
        elif orientation == 'West':
            return 180
        elif orientation == 'South':
            return 270
    
    
    def rotate(self, agent_orient, node_orient):
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
        node_orient = self.direction(agent_loc, Coords(path[1][0], path[1][1]))
        if node_orient == agent_orient:
            print('Forward')
            return path[1:], Forward()
        else:
            return path, self.rotate(agent_orient, node_orient)
        

class BeelineAgent(BeelineEscape):
  def __init__(self):
    super().__init__()
    self.DG = nx.DiGraph()
    self.agentVisitList = []
    self.escapePlanBuilt = False
    
  @staticmethod
  def create():
    return Agent()
  
  @staticmethod
  def coords2tup(coords: Coords):
    return (coords.x, coords.y)
  
  def buildSafeGraph(self):
    locs = self.agentVisitList
    curr_loc = locs[-1]
    for i in range(len(locs)-1):
        if locs[i+1] != locs[i] and not \
           self.DG.has_edge(self.coords2tup(locs[i]), self.coords2tup(locs[i+1])):
            self.DG.add_edge(self.coords2tup(locs[i+1]), self.coords2tup(locs[i])) 
    return nx.shortest_path(self.DG, source=(curr_loc.x, curr_loc.y), target=(0,0))
    
  def nextAction(self, percept: Percept, agent: Agent):
    
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