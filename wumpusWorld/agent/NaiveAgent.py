import random
from wumpusWorld.environment.Agent import *
from wumpusWorld.environment.Action import *


class NaiveAgent():
  def __init__(self):
    pass

  @staticmethod
  def create():
    return Agent()
  
  @staticmethod
  def nextAction():
    actions = {
          0: Forward(),
          1: TurnLeft(),
          2: TurnRight(),
          3: Shoot(),
          4: Grab(),
          5: Climb()
    }
    actions_str = {
          0: 'Forward',
          1: 'TurnLeft',
          2: 'TurnRight',
          3: 'Shoot',
          4: 'Grab',
          5: 'Climb'
    }
    
    randm_int = random.randint(0, 5)
    print(actions_str.get(randm_int))
    return actions.get(randm_int)