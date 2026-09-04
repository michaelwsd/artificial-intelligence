import logging
import random

import util
from game import Actions, Agent, Directions
from logs.search_logger import log_function
from pacman import GameState
from util import manhattanDistance

'''
Design Decisions:
- I decided to use the standard alpha-beta search algorithm with a custom evaluation function. 
- I added more context to the evaluation function over time:
    1. Started with just a simple score of the current state. This is the most important metric 
       in the whole game, but it is not enough as there are other information in the game that 
       we are not taken into account such as the food and ghosts. Regardless, I gave a multipler 
       on this score to indicate significance. 
       
    2. Winning the game should give up an infinite amount of points, and losing the game should give
       the opposite. However, I decided to not use float('inf') or float('-inf') as I also want to take
       the game score into account. As we lose points the longer we take, a higher game score would indicate 
       that we finished the game earlier, and that state should be preferred, using inf doesn't allow this. 

    3. Next up is food. We should both penalize for having food left in the map and being away from the 
       closest food. To achieve this, I gave a penalty on the amount of food left in the current state
       and also reward the pacman for being close to the closest food. 

       I deliberately made the reward smaller than 1 because I don't want it to cancel out with the time penalty. 
       Since we lose 1 point per tick, keeping the reward below one means it can never outweigh a single tick, so
       it purely acts as a tie breaker between states of equal score (and when that happens we prefer to be closer
       to the food), rather than competing with it.  

    4. Next up is ghosts and capsules. Being in contact with the ghost means game over, which means we must prevent 
       this from happening at all costs. However, this depends on the ghost state. 

       If the ghost is not scared and it is close to us (< 2), we penalize it hard and escape from it, if it's not close
       then we don't need to worry about it as being away from it doesn't benefit us, we can just focus on getting the dots. 

       If the ghost is scared, we instead reward it with the rewarded points scaled against the distance, because there's no
       point prioritizing a scared ghost over food if it is far away. 

       For the capsules, I chose to only reward the nearest capsule if there is a ghost nearby (< 8), again scaled by the distance
       from pacman. Because this way if there is a capsule nearby, we can get it then immediately eat the scared ghost. 

    5. For the depth, I tested 2, 3 and 4. I found 3 to be the balance between finishing the game and good performance. 
       Depth 2 has worse performance, and depth 4 crashes in some instances. 

Analysis of Results:
- The best solution achieved a score of 21.99/24. Each addition of feature in the evaluation function had a meaningful increase in 
  the final score. 

- The two feature (distance to nearest dot and remanining dots) were the most important features and was a big step up from the
  baseline evaluation function. 

- Ghost penalty was neutral as at depth 2 the search would have already seen the death. 

- Capsule and scared ghost reward was somewhat a big improvement, as it incentivizes eating a scared ghost which gives more points
  than eating a dot. 

Reflections and Improvement:
- Depth 3 gave the best balance between performance and efficiency. 

- The biggest blocker I found was that when the food was isolated by itself, such as in the maze medium classic 2, the pacman tends 
  to ignore the dot and keeps going straight to collect the dots. This cost a lot of time penalty as pacman has to later go back 
  to collect them. 

  This is because the evaluation only ever sees one dot, so it has no notion of a route. This may be improved if I collected the nearest
  k dots or reward any isolated dots nearby.  

- There is some randomness involved in the ghost movement, which could also attribute to the score losses.  
'''

CAPSULE_REWARD = 30
FOOD_PENALTY = -10
SCARED_GHOST = 300
NEARBY_GHOST = -300

def scoreEvaluationFunction(currentGameState):
    """
      This default evaluation function just returns the score of the state.
      The score is the same one displayed in the Pacman GUI.

      This evaluation function is meant for use with adversarial search agents
      (not reflex agents).
    """
    return currentGameState.getScore()

def get_closest_food(state: GameState, pacmanpos):
    # expand with a limit, give high weight to all close by dots
    '''
    Return the distance from pacman to the closest food
    '''
    walls = state.getWalls()
    food = state.getFood()
    seen = {pacmanpos}
    queue = util.Queue()
    queue.push((pacmanpos, 0))

    while not queue.isEmpty():
        (x, y), d = queue.pop()

        # get the closest food
        if food[x][y]:
            return d

        # expand
        for dx, dy in ((0, 1), (0, -1), (1, 0), (-1, 0)):
            nxt_cell = (x + dx, y + dy)
            if nxt_cell not in seen and not walls[nxt_cell[0]][nxt_cell[1]]:
                seen.add(nxt_cell)
                queue.push((nxt_cell, d + 1))

    return float('inf')

def betterScoreEvaluation(state: GameState) -> float:
    value = 1.5 * scoreEvaluationFunction(state) # give more weight to the score

    # we prefer faster wins over slower wins
    if state.isWin():
        return 1e10 + value
    if state.isLose():
        return -1e10 + value

    food_left = state.getNumFood()
    capsulepos = state.getCapsules()
    pacmanpos = state.getPacmanPosition()
    closest_ghost, closest_ghost_dist = get_nearest_ghost(state, pacmanpos)

    # give a penalty for every food not eaten 
    value += food_left * FOOD_PENALTY

    # penalize for being away from food
    value += award_closest_food(state, pacmanpos, food_left)

    # add penalty or reward according to the nearest ghost's state 
    value += score_nearest_ghost(closest_ghost, closest_ghost_dist)

    # if capsule near by, + points for each nearby ghost
    value += award_capsule_nearby(capsulepos, closest_ghost_dist, pacmanpos)

    return value

def award_capsule_nearby(capsules, ghost_dist, pacmanpos):
    '''
    Award the closest capsule to pacman if there is a ghost nearby, scaled by the capsule distance
    '''
    if not capsules or ghost_dist > 8:
        return 0 

    dist = min(manhattanDistance(pacmanpos, c) for c in capsules)
    return CAPSULE_REWARD / (dist + 1)

def award_closest_food(state: GameState, pacmanpos, food_left: int):
    '''
    Award the score based on the distance from pacman to the closest food
    The closer it is, the larger the reward
    Keeping it < 1 to give more effect to time penalty
    '''
    # amount to penalize for being away from the closest food
    if food_left <= 0:
        closest_food_dist = 0
    else:
        closest_food_dist = get_closest_food(state, pacmanpos)

    # small value to give more significance to time penalty
    return 1 / (closest_food_dist + 1) # prevent 0 division

def get_nearest_ghost(state: GameState, pacmanpos):
    '''
    Get the nearest ghost and distance to that ghost
    '''
    closest_ghost, closest_ghost_dist = None, float('inf')

    for ghost in state.getGhostStates():
        dist = manhattanDistance(pacmanpos, ghost.getPosition()) 
        if dist < closest_ghost_dist:
            closest_ghost, closest_ghost_dist = ghost, dist 

    return closest_ghost, closest_ghost_dist

def score_nearest_ghost(closest_ghost, closest_ghost_dist):
    '''
     Modify the score based on the distance and state of the nearest ghost
    - Add to the score if ghost is scared and close to pacman
    - Subtract from the score if ghost is not scared and very close to pacman
    '''
    if closest_ghost:
        scared_timer = closest_ghost.scaredTimer
        if scared_timer > closest_ghost_dist * 1.5:
            return SCARED_GHOST / (closest_ghost_dist + 1)
        else:
            return NEARBY_GHOST if closest_ghost_dist < 2 else 0

    return 0

class Q2_Agent(Agent):

    def __init__(self, evalFn = 'betterScoreEvaluation', depth = '3'):
        self.index = 0 # Pacman is always agent index 0
        self.evaluationFunction = util.lookup(evalFn, globals())
        self.depth = int(depth)

    @log_function
    def getAction(self, gameState: GameState):
        """
            Returns the minimax action from the current gameState using self.depth
            and self.evaluationFunction.

            Here are some method calls that might be useful when implementing minimax.

            gameState.getLegalActions(agentIndex):
            Returns a list of legal actions for an agent
            agentIndex=0 means Pacman, ghosts are >= 1

            gameState.generateSuccessor(agentIndex, action):
            Returns the successor game state after an agent takes an action

            gameState.getNumAgents():/
            Returns the total number of agents in the game
        """
        logger = logging.getLogger('root')
        logger.info('MinimaxAgent')

        def alpha_beta_search(state: GameState) -> str:
            _, move = max_value(state, float('-inf'), float('inf'), 0)
            return move 

        # max node updates alpha and gets cut by ancestor beta
        def max_value(state: GameState, alpha: float, beta: float, depth: int):
            if is_terminal(state, depth):
                return self.evaluationFunction(state), None 

            v, move = float('-inf'), Directions.STOP

            # v2 is what one child returned for one particular action taken by the pacman (max)
            # v is the best v2 seen so far 
            # beta is the best value the minimising ancestor has already secured from a sibling branch it finished exploring. 
            # it's an upper bound on what that ancestor will end up accepting, the ancestor will take at most beta, and it can only go lower.
            # if v is larger than beta, it means pacman will be at least v, so there is no point going further as the ancestor will never take a higher value -> beta cur-off

            for action in state.getLegalPacmanActions():
                successor = state.generatePacmanSuccessor(action) # next state using this action
                v2, _ = min_value(successor, alpha, beta, depth, 1) # minimum value of the opponent 

                # we want the largest value for pacman
                if v2 > v:
                    v, move = v2, action 
                    alpha = max(alpha, v)

                # beta cut-off
                if v >= beta:
                    return v, move 
                
            return v, move 

        # min node updates beta and gets cut by ancestor alpha
        def min_value(state: GameState, alpha: float, beta: float, depth: int, agentIdx):
            if is_terminal(state, depth):
                return self.evaluationFunction(state), None 

            v, move = float('inf'), Directions.STOP 
            last_ghost = agentIdx == state.getNumAgents() - 1

            # go to the next pacman depth
            if last_ghost:
                depth += 1

            for action in state.getLegalActions(agentIdx):
                successor = state.generateSuccessor(agentIdx, action)
                if last_ghost:
                    # move to the next depth
                    v2, _ = max_value(successor, alpha, beta, depth)
                else:
                    # go to the next ghost 
                    v2, _ = min_value(successor, alpha, beta, depth, agentIdx + 1)

                if v2 < v:
                    v, move = v2, action
                    beta = min(beta, v)

                if v <= alpha:
                    return v, move 

            return v, move 

        def is_terminal(state: GameState, depth: int) -> bool:
            return depth == self.depth or state.isWin() or state.isLose()

        return alpha_beta_search(gameState)