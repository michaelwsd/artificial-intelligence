# PacmanValueIterationAgent.py
# -----------------------
# Licensing Information:  You are free to use or extend these projects for
# educational purposes provided that (1) you do not distribute or publish
# solutions, (2) you retain this notice, and (3) you provide clear
# attribution to UC Berkeley, including a link to http://ai.berkeley.edu.
#
# Attribution Information: The Pacman AI projects were developed at UC Berkeley.
# The core projects and autograders were primarily created by John DeNero
# (denero@cs.berkeley.edu) and Dan Klein (klein@cs.berkeley.edu).
# Student side autograding was added by Brad Miller, Nick Hay, and
# Pieter Abbeel (pabbeel@cs.berkeley.edu).

#---------------------#
# DO NOT MODIFY BEGIN #
#---------------------#
import util

from agents.learningAgents import ValueEstimationAgent
from game import Grid, Actions, Directions
import math
from pacman import GameState
import random
import numpy as np
import json


class Q1Agent(ValueEstimationAgent):
    """
    Q1 agent takes a Markov decision process
    (see pacmanMDP.py) on initialization and 
    runs value iteration or policy iteration
    for a given number of iterations using the supplied
    discount factor.
    """

    def __init__(self, mdp="PacmanMDP", discount=0.5, iterations=200, mazeSize=None):
        """
          Your agent should take an mdp on
          construction, run the indicated number of iterations
          and then act according to the resulting policy.

          Some useful mdp methods you will likely use:
              self.MDP.getStates()
              self.MDP.getPossibleActions(state)
              self.MDP.getTransitionStatesAndProbs(state, action)
              self.MDP.getReward(state, action)
              self.MDP.isTerminal(state)
        """
        mdp_func = util.import_by_name('./', mdp)
        self.mdp_func = mdp_func

        print('[Q1Agent] using mdp ' + mdp_func.__name__)
        
        # set discount factor and the number of training iterations
        if mazeSize:
            self.discount = self.getParams(mazeSize, "gamma")
            self.iterations = self.getParams(mazeSize, "iterations")
        else:
            self.discount = float(discount)
            self.iterations = int(iterations)            

        # initialise the values and policy. You will update them in solveMDP
        self.values = None
        self.policy = None

        # flag so we only solve the MDP once no matter how many games we play
        self.mdp_solved = False


    def getAction(self, gameState: GameState):
        """
        Returns the action to take at the a location according to the values

        Note: reaching any positive terminal state is considered winning the game and results in +500 points
        To achieve this we need the ReachedPositiveTerminalStateException because the game wouldn't noramlly end with food remaining
        """

        pacman_location = gameState.getPacmanPosition()
        if pacman_location in self.MDP.getFoodStates():
            raise util.ReachedPositiveTerminalStateException("Reached a Positive Terminal State")
        else:
            best_action = self.deriveActionFromLearntPolicy(pacman_location)
            return self.MDP.applyNoiseToAction(pacman_location, best_action)

    def registerInitialState(self, gameState: GameState):

        # set up the mdp with the agent starting state and solve it
        self.MDP = self.mdp_func(gameState)

        # only attempt to solve the MDP once
        if not self.mdp_solved:
            self.mdp_solved = True
            self.solveMDP()

    #-------------------#
    # DO NOT MODIFY END #
    #-------------------#

    def getParams(self, maze_size, param_name):
        """
        Add your maze parameters here 
        """
        params = {
            "small": {
                "gamma": 0.999,
                "iterations": 1000
                },
            "medium": {
                "gamma": 0.999,
                "iterations": 1000
            },
            "large": {
                "gamma": 0.999,
                "iterations": 1000
            }
        }
        return params[maze_size][param_name]
    

    def solveMDP(self):
        """
        This function will solve the mdp instance the agent received on input.
        This is where you implement either policy iteration or value iteration
        You can access the 
        - mdp with self.mdp
        - discount factor with self.discount
        - num of iteratons with self.iterations
        """
        # "*** YOUR CODE HERE ***"

        # initialize state and values 
        states = list(self.MDP.getStates())
        self.values = {state: 0.0 for state in states}

        # V(s) <- max_a sum_{s'} T(s,a,s') [R(s,a,s') + gamma * V(s')]
        # V(s) <- max_a Q(s, a)
        for _ in range(self.iterations):
            newValues = {}
            maxChange = 0.0

            for state in states: 
                # terminal state has nothing to gain
                if self.MDP.isTerminal(state):
                    newValues[state] = 0.0 
                    continue 

                # get the action with the max q value 
                newValues[state] = max(self.computeQVal(state, action) for action in self.MDP.getPossibleActions(state))    
                # get the change in this iteration
                maxChange = max(maxChange, abs(newValues[state] - self.values[state]))

            self.values = newValues
            # break if max change is too small 
            if maxChange < 1e-6:
                break 

        # extract the greedy 
        self.policy = {}
        for state in states: 
            bestAction = None 
            bestValue = float("-inf")

            for action in self.MDP.getPossibleActions(state):
                q = self.computeQVal(state, action)
                if q > bestValue:
                    bestValue = q 
                    bestAction = action 

            self.policy[state] = bestAction

    
    def deriveActionFromLearntPolicy(self, state: tuple):
        """
        This functions takes an (x,y) tuple representing Pac-Man's location
        and decides how to act using the agent's learnt policy.

        If you used Value Iteration this will be derived from the values you compute
        If you use Policy Iteration this will come directly from the computed policy
        """
        # "*** YOUR CODE HERE ***"
        return self.policy[state]


    ################################ ANY OTHER CODE BELOW HERE ################################

    def computeQVal(self, state, action):
        '''
        Q(s,a) = sum_{s'} T(s,a,s') [R(s,a,s') + gamma * V(s')]
        '''
        qval = 0
        for nextState, prob in self.MDP.getTransitionStatesAndProbs(state, action):
            reward = self.MDP.getReward(state, action, nextState)
            qval += prob * (reward + self.discount * self.values[nextState])

        return qval 
