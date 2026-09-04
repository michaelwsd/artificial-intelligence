#---------------------#
# DO NOT MODIFY BEGIN #
#---------------------#

import logging

import util
from problems.q1a_problem import q1a_problem

#-------------------#
# DO NOT MODIFY END #
#-------------------#

'''
Implementation of the A* algorithm. 
- A* always finds the most optimal path. 
- Manhattan distance would sometimes lead pacman to explore directions that were blocked, 
  using BFS to find the maze distance would perhaps be an improvement. 
- This solution was designed to be reusable for q1b solver.  
'''

def q1a_solver(problem: q1a_problem):
    astarData = astar_initialise(problem)
    num_expansions = 0
    terminate = False
    while not terminate:
        num_expansions += 1
        terminate, result = astar_loop_body(problem, astarData)
    print(f"Number of node expansions: {num_expansions}")
    return result

class AStarData:
    def __init__(self, problem: q1a_problem):
        self.start = problem.getStartState()
        self.goal = problem.goal
        self.frontier = util.PriorityQueue()
        self.costs = {self.start: 0} # the cost to get to the current state 
        self.parents = {self.start: None} # used to reconstruct the path
        self.visited = set()

        # initialize frontier
        self.frontier.push(self.start, astar_heuristic(self.start, self.goal))

def astar_initialise(problem: q1a_problem):
    return AStarData(problem)

def astar_loop_body(problem: q1a_problem, astarData: AStarData):
    # pop the closest candidate
    state = None
    while not astarData.frontier.isEmpty():
        candidate = astarData.frontier.pop()
        if candidate not in astarData.visited:
            state = candidate
            break

    # unreachable
    if not state: 
        return True, []

    # found goal
    if problem.isGoalState(state):
        return True, reconstruct_path(astarData, state)

    # add to pqueue
    astarData.visited.add(state)
    cost = astarData.costs[state] # the cost to get to this state

    for nei, action, stepCost in problem.getSuccessors(state):
        if nei in astarData.visited:
            continue 

        newCost = cost + stepCost # cost to get to the next position

        # if new state or less cost, add to frontier
        if nei not in astarData.costs or newCost < astarData.costs[nei]:
            astarData.costs[nei] = newCost
            astarData.parents[nei] = (state, action)
            astarData.frontier.push(nei, newCost + astar_heuristic(nei, astarData.goal)) # cost to get here + estimated cost to goal

    return False, None 
    
def reconstruct_path(astarData: AStarData, state):
    actions = []
    while astarData.parents[state] is not None:
        state, action = astarData.parents[state]
        actions.append(action)

    return actions[::-1]

def astar_heuristic(current, goal):
    return util.manhattanDistance(current, goal)