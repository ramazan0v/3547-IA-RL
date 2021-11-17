import pomegranate as pm
from wumpusWorld.environment.Environment import *


def createConditProbTbl(adjCellCnt, condit=[0,1], percept=[0,1]):
    # this helped function generates all possible permutations for our model
    conditProbTbl = []
    
    if adjCellCnt == 2:
        for i in range(len(condit)):
            for j in range(len(condit)):
                for k in range(len(percept)):
                    if i == 0 and j == 0:
                        conditProbTbl.append([condit[i], condit[j], percept[k], 1.0 if k==0 else 0.0])
                    else:
                        conditProbTbl.append([condit[i], condit[j], percept[k], 1.0 if k==1 else 0.0])
    elif adjCellCnt == 3:
        for i in range(len(condit)):
            for j in range(len(condit)):
                for l in range(len(condit)):
                    for k in range(len(percept)):
                        if i == 0 and j == 0 and l == 0:
                            conditProbTbl.append([condit[i], condit[j], condit[l], percept[k], 1.0 if k==0 else 0.0])
                        else:
                            conditProbTbl.append([condit[i], condit[j], condit[l], percept[k], 1.0 if k==1 else 0.0])
    elif adjCellCnt == 4:
        for i in range(len(condit)):
            for j in range(len(condit)):
                for l in range(len(condit)):
                    for m in range(len(condit)):
                        for k in range(len(percept)):
                            if i == 0 and j == 0 and l == 0 and m == 0:
                                conditProbTbl.append([condit[i], condit[j], condit[l], condit[m], percept[k], 1.0 if k==0 else 0.0])
                            else:
                                conditProbTbl.append([condit[i], condit[j], condit[l], condit[m], percept[k], 1.0 if k==1 else 0.0])
    
    return conditProbTbl


def listAllCells(gridWidth, gridHeight):                    
    cells = []
    for i in range(0, gridWidth):
        for j in range(0, gridHeight):
           cells.append(Coords(i,j))
    return cells


def createPitModel(environment: Environment):
    allCells = listAllCells(environment.gridWidth, environment.gridHeight)
    
    pitProbDist = {}
    pitStates = {}
    breezeProbDist = {}
    breezeStates = {}

    # Pit Discrete Probability Distributions and States
    for cell in allCells:
        if cell.x == 0 and cell.y == 0:
            pitProbDist[(cell.x, cell.y)] = pm.DiscreteDistribution({True: 0.0, False: 1.0})
        else:
            pitProbDist[(cell.x, cell.y)] = pm.DiscreteDistribution({True: environment.pitProb, False: 1 - environment.pitProb})
        pitStates[(cell.x, cell.y)] = pm.State(pitProbDist[(cell.x, cell.y)])
        
    # Breeze Conditional Probability Distributions and States
    for cell in allCells:
        adjCells = environment.adjacentCells(cell)
        adjCellsPitProbs = [pitProbDist[(adjCell.x, adjCell.y)] for adjCell in adjCells]
        breezeProbDist[(cell.x, cell.y)] = pm.ConditionalProbabilityTable(createConditProbTbl(len(adjCells)), 
                                                                          adjCellsPitProbs) 
        breezeStates[(cell.x, cell.y)] = pm.State(breezeProbDist[(cell.x, cell.y)])

    # Create BayesianNetwork and add pit, breeze states
    pitModel = pm.BayesianNetwork("Pit-Breeze Model")
    pitModel.add_states(*pitStates.values(), *breezeStates.values())
    
    # Add edges to the model
    for cell in allCells:
        adjCells = environment.adjacentCells(cell)
        for adjCell in adjCells:
            pitModel.add_edge(pitStates[(adjCell.x, adjCell.y)], breezeStates[(cell.x, cell.y)])
    
    pitModel.bake()
    return pitModel
    
    
def createWumpusModel(environment: Environment):
    allCells = listAllCells(environment.gridWidth, environment.gridHeight)
    
    wumpusDiscDist = {}
    wumpusCondDist = {}
    wumpusCondStates = {}
    stenchProbDist = {}
    stenchStates = {}

    # Wumpus Discrete Probability Distributions and States
    for cell in allCells:
        if cell.x == 0 and cell.y == 0:
            wumpusDiscDist[(cell.x, cell.y)] = 0.0
        else:
            wumpusDiscDist[(cell.x, cell.y)] = 1 / (environment.gridWidth * environment.gridHeight - 1)
    wumpusDiscDist = pm.DiscreteDistribution(wumpusDiscDist)
    wumpusStates = pm.State(wumpusDiscDist)
    
    # Wumpus Conditional Probability Distributions and States: Wumpus can be only in one location
    for cell in allCells:
        wumpusConds = []
        for cell2 in allCells:
            if cell == cell2:
                wumpusConds.append([(cell2.x, cell2.y), True, 1.0])
                wumpusConds.append([(cell2.x, cell2.y), False, 0.0])
            else:
                wumpusConds.append([(cell2.x, cell2.y), True, 0.0])
                wumpusConds.append([(cell2.x, cell2.y), False, 1.0])         
        wumpusCondDist[(cell.x, cell.y)] = pm.ConditionalProbabilityTable(wumpusConds, [wumpusDiscDist])
        wumpusCondStates[(cell.x, cell.y)] = pm.State(wumpusCondDist[(cell.x, cell.y)])
    
    # Stench Conditional Probability Table
    for cell in allCells:
        adjCells = environment.adjacentCells(cell)
        adjCellsWumpusProbs = [wumpusCondDist[(adjCell.x, adjCell.y)] for adjCell in adjCells]
        stenchProbDist[(cell.x, cell.y)] = pm.ConditionalProbabilityTable(createConditProbTbl(len(adjCells)), 
                                                              adjCellsWumpusProbs)
        stenchStates[(cell.x, cell.y)] = pm.State(stenchProbDist[(cell.x, cell.y)])
    
    # Create BayesianNetwork and add pit, breeze states
    wumpusModel = pm.BayesianNetwork("Wumpus-Stench Model")
    wumpusModel.add_states(wumpusStates, *wumpusCondStates.values(), *stenchStates.values())
    
    # Add edges to the model
    for cell in allCells:
        wumpusModel.add_edge(wumpusStates, wumpusCondStates[(cell.x, cell.y)])
    
    for cell in allCells:
        adjCells = environment.adjacentCells(cell)
        for adjCell in adjCells:
            wumpusModel.add_edge(wumpusCondStates[(adjCell.x, adjCell.y)], stenchStates[(cell.x, cell.y)])
    
    wumpusModel.bake()
    return wumpusModel