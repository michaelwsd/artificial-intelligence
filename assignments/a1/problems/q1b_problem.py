import logging
import time
from typing import Tuple

import util
from game import Actions, Agent, Directions
from logs.search_logger import log_function
from pacman import GameState


class q1b_problem:
    """
    This search problem finds paths through all four corners of a layout.

    You must select a suitable state space and successor function
    """
    def __str__(self):
        return str(self.__class__.__module__)

    def __init__(self, gameState: GameState):
        """
        Stores the start and goal.

        gameState: A GameState object (pacman.py)
        costFn: A function from a search state (tuple) to a non-negative number
        goal: A position in the gameState
        """
        self.startingGameState: GameState = gameState

        self.walls = gameState.getWalls()
        x, y = gameState.getPacmanPosition()
        self.startPos = (int(x), int(y))

        # get only the reachable food
        all_food = gameState.getFood().asList()
        reachable_cells = self.get_reachable_cells(self.startPos)
        reachable_food = [f for f in all_food if f in reachable_cells]
        self.can_clear = len(all_food) == len(reachable_food)

        self.startState = (self.startPos, frozenset(reachable_food))
        self.directions = [
            (Directions.NORTH, (0, 1)),
            (Directions.SOUTH, (0, -1)),
            (Directions.EAST, (1, 0)),
            (Directions.WEST, (-1, 0)),
        ]

    def get_reachable_cells(self, start):
        seen = {start}
        stack = [start]

        while stack:
            x, y = stack.pop()
            for dx, dy in ((0, 1), (0, -1), (1, 0), (-1, 0)):
                nxtCell = (x + dx, y + dy)
                if nxtCell not in seen and not self.walls[nxtCell[0]][nxtCell[1]]:
                    seen.add(nxtCell)
                    stack.append(nxtCell)

        seen.remove(start)
        return seen

    @log_function
    def getStartState(self):
        return self.startState

    @log_function
    def isGoalState(self, state):
        # all food has been eaten 
        return not state[1] 

    @log_function
    def getSuccessors(self, state):
        """
        Returns successor states, the actions they require, and a cost of 1.

         As noted in search.py:
             For a given state, this should return a list of triples,
         (successor, action, stepCost), where 'successor' is a
         successor to the current state, 'action' is the action
         required to get there, and 'stepCost' is the incremental
         cost of expanding to that successor
        """
        (x, y), remaining = state 
        successors = []
        for action, (dx, dy) in self.directions:
            nextx, nexty = x + dx, y + dy
            if self.walls[nextx][nexty]:
                continue 

            nxtPos = (nextx, nexty)
            nxtRemaining = remaining - {nxtPos} if nxtPos in remaining else remaining # remove the food if eaten
            successors.append(((nxtPos, nxtRemaining), action, 1))

        return successors 