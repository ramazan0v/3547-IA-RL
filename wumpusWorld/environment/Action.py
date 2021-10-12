import copy
from wumpusWorld.environment.Coords import *
from wumpusWorld.environment.Percept import * #change this

action_pt = -1
climb_w_gold = 1000
death_pt = -1000
arrow_pt = -10
total_pt = 0

class Action():
  '''
  Action class has 6 children classes:
  Forward, TurnLeft, TurnRight, Grab, Climb, Shoot
  These are all the moves an agent can make
  It takes environment, percept, agent objects, and returns them with updated states
  '''   
  @staticmethod
  def __call__(environment, percept, agent):
    pass

class Forward(Action):
  '''
  Forward action does the following:
  Calls agent.forward() method to move the agent forward
  Checks if the agent has moved into a pit or wumpus location - death
  Checks if the agent has moved into a gold location
  Returns updated environment, percept, agent objects
  '''
  @staticmethod
  def __call__(environment, percept, agent):
    agent.forward(environment.gridWidth, environment.gridHeight)
    death = (environment.isWumpusAt(agent.location) and environment.wumpusAlive) \
             or environment.isPitAt(agent.location)
    agent.isAlive =  not death
    environment.goldLocation = agent.location if agent.hasGold \
                               else environment.goldLocation
    environment.terminated = death
    
    return environment, Percept(environment.isStench(agent.location), 
                                environment.isBreeze(agent.location), 
                                environment.isGlitter(agent.location), 
                                agent.hasBumped, 
                                False, 
                                not agent.isAlive, 
                                percept.reward + action_pt if (agent.isAlive) \
                                  else percept.reward + action_pt + death_pt) \
                        ,agent

class TurnLeft(Action):
  '''
  TurnLeft action calls agent.turnLeft() method
  Returns updated environment, percept, agent objects
  '''
  @staticmethod
  def __call__(environment, percept, agent):
    agent.turnLeft()
    return environment, Percept(environment.isStench(agent.location), 
                          environment.isBreeze(agent.location), 
                          environment.isGlitter(agent.location), 
                          False, 
                          False, 
                          False, 
                          percept.reward + action_pt) \
                        ,agent

class TurnRight(Action):
  '''
  TurnLeft action calls agent.turnRight() method
  Returns updated environment, percept, agent objects
  '''
  @staticmethod
  def __call__(environment, percept, agent):
    agent.turnRight()
    return environment, Percept(environment.isStench(agent.location), 
                          environment.isBreeze(agent.location), 
                          environment.isGlitter(agent.location), 
                          False, 
                          False, 
                          False, 
                          percept.reward + action_pt) \
                        ,agent
  
class Grab(Action):
  '''
  If the location has Glitter, agent now has gold
  Returns updated environment, percept, agent objects
  '''
  @staticmethod
  def __call__(environment, percept, agent):
    agent.hasGold = environment.isGlitter(agent.location)
    environment.goldLocation = agent.location if agent.hasGold \
                               else environment.goldLocation
    return environment, Percept(environment.isStench(agent.location), 
                        environment.isBreeze(agent.location), 
                        environment.isGlitter(agent.location), 
                        False, 
                        False, 
                        False, 
                        percept.reward + action_pt) \
                        ,agent


class Climb(Action):
  '''
  The agent can only climb if it's in start location
  Also checks if climbing without gold is allowed
  Returns updated environment, percept, agent objects
  '''  
  @staticmethod
  def __call__(environment, percept, agent):
    inStartLocation = agent.location == Coords(0,0)
    success = agent.hasGold and inStartLocation
    isTerminated = success or (environment.allowClimbWithoutGold and inStartLocation)
    environment.terminated = isTerminated
    
    return environment, Percept(False, 
                          False, 
                          environment.isGlitter(agent.location), 
                          False, 
                          False, 
                          isTerminated, 
                          percept.reward + action_pt + climb_w_gold if success else percept.reward + action_pt) \
                        ,agent

class Shoot(Action):
  '''
  Calls environment.killAttemptSuccessful() to check if wumpus was on line of fire
  Updates the agent to have no arrows
  Returns updated environment, percept, agent objects
  '''  
  @staticmethod
  def __call__(environment, percept, agent):
    hadArrow = copy.copy(agent.hasArrow)
    wumpusKilled = environment.killAttemptSuccessful(agent)
    agent.hasArrow = False
    environment.wumpusAlive = environment.wumpusAlive and not wumpusKilled

    return environment, Percept(environment.isStench(agent.location), 
                          environment.isBreeze(agent.location), 
                          environment.isGlitter(agent.location), 
                          False, 
                          wumpusKilled, 
                          False, 
                          percept.reward + action_pt + arrow_pt if hadArrow else percept.reward + action_pt) \
                        ,agent