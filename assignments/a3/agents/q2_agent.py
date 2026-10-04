# qlearningAgents.py
# ------------------
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


from game import *
from agents.learningAgents import ReinforcementAgent
from pacman import GameState

import random,util,math
import numpy as np
from game import Directions
import json


class Q2Agent(ReinforcementAgent):
    """
      Q-Learning Agent

      Methods you should fill in:
        - __init__
        - registerInitialState
        - update
        - getParams
        - epsilonGreedyActionSelection

      Instance variables you have access to
        - self.epsilon (exploration prob)
        - self.alpha (learning rate)
        - self.discount (discount rate)
    """

    def __init__(self, usePresetParams=False, **args):
        """
        These default parameters can be changed from the pacman.py command line.
        For example, to change the exploration rate, try:
            python pacman.py -p Q2Agent -a epsilon=0.1

        alpha    - learning rate
        epsilon  - exploration rate
        gamma    - discount factor
        numTraining - number of training episodes, i.e. no learning after these many episodes

        usePresetParams - Set to True if you want to use your evaluation parameters
        """

        self.index = 0  # This is always Pacman

        ReinforcementAgent.__init__(self, **args)

        # when maze size is provided use the preset parameters, otherwise values will use those specified at the command line
        if usePresetParams:
            self.epsilon = self.getParams("epsilon")
            self.alpha = self.getParams("alpha")
            self.discount = self.getParams("gamma")

        # *** YOUR CODE STARTS HERE ***

        # maps (key, action) to an estimated q-value
        self.Qtable = util.Counter()
        self.replayBuffer = []
        self.replaySamples = 50

        # *** YOUR CODE ENDS HERE ***
    

    def registerInitialState(self, state: GameState):
        """
        Don't modify this method except in the provided area.
        You can modify this method to do any computation you need at the start of each episode
        """

        # *** YOUR CODE STARTS HERE ***

        

        # *** YOUR CODE ENDS HERE ***

        self.startEpisode()
        if self.episodesSoFar == 0:
            print('Beginning %d episodes of Training' % (self.numTraining))
    
    
    def getAction(self, state: GameState):
        """
        Don't modify this method!
        Uses epsilon greedy to select an action based on the agents Q table.
        """

        action = self.epsilonGreedyActionSelection(state)
        self.doAction(state, action)
        return action

    def update(self, state: GameState, action: str, nextState: GameState, reward):
        """
        The parent class calls this to observe a
        state = action => nextState and reward transition.
        You should do your Q-Value update here using the Q value update equation

        NOTE: You should never call this function,
        it will be called on your behalf
        """

        # *** YOUR CODE HERE ***
        if self.alpha == 0:
            return

        nextActions = self.getActions(nextState)
        nextKey = self.getStateKey(nextState) if nextActions else None
        transition = (self.getStateKey(state), action, reward, nextKey, nextActions)

        self.learn(transition)

        # pick 50 random past moves and learn each one again
        self.replayBuffer.append(transition)
        for _ in range(self.replaySamples):
            self.learn(random.choice(self.replayBuffer))


    def getParams(self, param_name):
        """
        Add your parameters here 
        """
        params = {
            "gamma": 1.0, # discount factor
            "epsilon": 0.1, # 1 in 10 moves is random
            "alpha": 0.1 # the learning rate 
        }
        return params[param_name]


    def epsilonGreedyActionSelection(self, state: GameState):
        """
        Compute the action to take in the current state.  With
        probability self.epsilon, we should take a random action and
        take the best policy action otherwise.  Note that if there are
        no legal actions, which is the case at the terminal state, you
        should choose None as the action.

        HINT: When the agent is no longer in training self.epsilon will be set to 0, 
        so calling this method should always return the best action over the Q values
        HINT: You might want to use util.flipCoin(prob)
        HINT: To pick randomly from a list, use random.choice(list)
        HINT: You might want to use self.getLegalActions(state), 
        but consider whether or not using the STOP action is necessary or beneficial
        """
        
        # *** YOUR CODE HERE ***
        actions = self.getActions(state)
        if not actions:
            return None 

        if util.flipCoin(self.epsilon):
            return random.choice(actions)

        return self.getBestAction(state)

    ################################ ANY OTHER CODE BELOW HERE ################################

    def getStateKey(self, state: GameState):
        '''everything that decides the future reward'''
        pacmanpos = state.getPacmanPosition()
        food = tuple(state.getFood().asList())
        ghosts = tuple((int(x), int(y)) for x, y in state.getGhostPositions())
        ghostDirs = tuple(g.getDirection() for g in state.getGhostStates())
        return (pacmanpos, food, ghosts, ghostDirs)

    def getActions(self, state: GameState):
        '''returns legal actions excluding STOP'''
        return [a for a in self.getLegalActions(state) if a != Directions.STOP]

    def learn(self, transition):
        '''Q(s,a) <- Q(s,a) + alpha * [r + gamma * max_a' Q(s',a') - Q(s,a)]'''
        stateKey, action, reward, nextKey, nextActions = transition
        key = (stateKey, action)
        future = max(self.Qtable[(nextKey, a)] for a in nextActions) if nextActions else 0.0
        target = reward + self.discount * future
        self.Qtable[key] += self.alpha * (target - self.Qtable[key])

    def getBestAction(self, state: GameState):
        '''get the action with the highest Q(s, a)'''
        actions = self.getActions(state)
        stateKey = self.getStateKey(state)
        bestValue = max(self.Qtable[(stateKey, a)] for a in actions)
        return random.choice([a for a in actions if self.Qtable[(stateKey, a)] == bestValue])