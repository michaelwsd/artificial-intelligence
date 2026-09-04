#---------------------#
# DO NOT MODIFY BEGIN #
#---------------------#

import logging

import util
from problems.q1b_problem import q1b_problem

#-------------------#
# DO NOT MODIFY END #
#-------------------#

'''
Design Decisions:
- Scores only ever increase after eating a dot, otherwise it decreases every tick. 
  This tells us every local maximum happens immediately after eating a dot. 
- Knowing this, I return the best-scoring prefix of a greedy path. 
- Again, the heuristics used is the manhattan distance, which may be improved if we use maze distance,
  but this will sacrifice efficiency. 
'''

FOOD_POINTS = 10
WIN_POINTS = 500

def q1b_solver(problem: q1b_problem):
    astarData = astar_initialise(problem)
    num_expansions = 0
    terminate = False
    while not terminate:
        num_expansions += 1
        terminate, result = astar_loop_body(problem, astarData)
    print(f'Number of node expansions: {num_expansions}')
    return result

class AStarData:
    def __init__(self, problem: q1b_problem):
        self.problem = problem
        self.position, self.remaining = problem.getStartState()
        self.totalDots = len(self.remaining)
        self.plan = [] # accumulate all the paths 

        # record the best path
        self.collected = 0
        self.travelled = 0
        self.bestScore = 0
        self.bestLength = 0

        self.start_path()

    def start_path(self):
        self.frontier = util.PriorityQueue()
        self.costs = {self.position: 0} # cost to get to a state
        self.parents = {self.position: None}
        self.visited = set()
        self.frontier.push(self.position, astar_heuristic(self.position, self.remaining))

    # record the total points collected so far
    def record(self):
        score = FOOD_POINTS * self.collected - self.travelled
        if self.collected == self.totalDots and self.problem.can_clear:
            score += WIN_POINTS

        if score > self.bestScore:
            self.bestScore = score 
            self.bestLength = len(self.plan)

def astar_initialise(problem: q1b_problem):
    return AStarData(problem)

def reconstruct_path(astarData: AStarData, state):
    actions = []
    while astarData.parents[state] is not None:
        state, action = astarData.parents[state]
        actions.append(action)

    return actions[::-1]

def astar_loop_body(problem: q1b_problem, astarData: AStarData):
    if not astarData.remaining:
        return True, astarData.plan 

    # pop the closest candidate
    state = None
    while not astarData.frontier.isEmpty():
        candidate = astarData.frontier.pop()
        if candidate not in astarData.visited:
            state = candidate
            break
        
    # no more routes
    if not state: 
        return True, astarData.plan[:astarData.bestLength]

    # this is the next dot to collect
    if state in astarData.remaining:
        astarData.travelled += astarData.costs[state] # accumulate the cost 
        astarData.collected += 1 # accumulate food 
        astarData.plan.extend(reconstruct_path(astarData, state)) # extend path to this state
        astarData.record()

        astarData.position = state 
        astarData.remaining -= {state}
        if not astarData.remaining:
            return True, astarData.plan[:astarData.bestLength]

        astarData.start_path() # resets the initial pos of pacman
        return False, None

    # expand normally
    astarData.visited.add(state)
    cost = astarData.costs[state] # the cost to get to this state

    for successor, action, stepCost in problem.getSuccessors((state, astarData.remaining)):
        nxtState = successor[0]
        if nxtState in astarData.visited:
            continue 

        newCost = cost + stepCost # cost to get to this position
        prevCost = astarData.costs.get(nxtState) # previous cost to get to this position

        # if new state or less cost, add to frontier
        if prevCost is None or newCost < prevCost:
            astarData.costs[nxtState] = newCost
            astarData.parents[nxtState] = (state, action)
            astarData.frontier.push(nxtState, newCost + astar_heuristic(nxtState, astarData.remaining)) # cost to get here + estimated cost to goal

    return False, None 

def astar_heuristic(current, goals):
    if not goals:
        return 0

    # return the shortest manhattan distance out of all dots 
    return min(util.manhattanDistance(current, g) for g in goals)