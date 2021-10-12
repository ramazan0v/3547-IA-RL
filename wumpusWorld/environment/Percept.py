class Percept():
  '''
  This class keeps track of agent's perceptions
  '''  
  def __init__(self,
               stench: bool, 
               breeze: bool, 
               glitter: bool, 
               bump: bool, 
               scream: bool, 
               isTerminated: bool, 
               reward: int):
    self.stench = stench
    self.breeze = breeze
    self.glitter = glitter
    self.bump = bump
    self.scream = scream
    self.isTerminated = isTerminated
    self.reward = reward

  @staticmethod  
  def create(stench: bool, 
             breeze: bool, 
             glitter: bool):
    return Percept(stench, breeze, glitter, False, False, False, 0)

  def show(self):
    print("stench: ", self.stench, ", breeze: ", self.breeze, ", glitter: ", self.glitter, ", bump: ", self.bump,
          ", scream: ", self.scream, ", isTerminated: ", self.isTerminated, ", reward: ", self.reward, sep="")