import numpy as np

# These are the outcomes of 16 the terminal nodes. States are ordered from left to right as shown in the diagram.
outcomes = {
    'P': 3,
    'Q': 9,
    'R': 1,
    'S': 8,
    'T': 0,
    'U': 13,
    'V': 6,
    'W': 20,
    'X': 2,
    'Y': 4,
    'Z': 7,
    'AA': 5,
    'AB': 11,
    'AC': 14,
    'AD': 8,
    'AE': 13
}

transitions = {
    ('A', 'Left'): 'B',
    ('A', 'Right'): 'C',
    ('B', 'Left'): 'D',
    ('B', 'Right'): 'E',
    ('C', 'Left'): 'F',
    ('C', 'Right'): 'G',
    ('D', 'Left'): 'H',
    ('D', 'Right'): 'I',
    ('E', 'Left'): 'J',
    ('E', 'Right'): 'K',
    ('F', 'Left'): 'L',
    ('F', 'Right'): 'M',
    ('G', 'Left'): 'N',
    ('G', 'Right'): 'O',
    ('H', 'Left'): 'P',
    ('H', 'Right'): 'Q',
    ('I', 'Left'): 'R',
    ('I', 'Right'): 'S',
    ('J', 'Left'): 'T',
    ('J', 'Right'): 'U',
    ('K', 'Left'): 'V',
    ('K', 'Right'): 'W',
    ('L', 'Left'): 'X',
    ('L', 'Right'): 'Y',
    ('M', 'Left'): 'Z',
    ('M', 'Right'): 'AA',
    ('N', 'Left'): 'AB',
    ('N', 'Right'): 'AC',
    ('O', 'Left'): 'AD',
    ('O', 'Right'): 'AE'
}

def alpha_beta_search(state):
    v, move = max_value(state, float('-inf'), float('inf'))
    return v, move 

def max_value(state, alpha, beta):
    if is_terminal(state):
        return outcomes[state], None 

    v, move = float('-inf'), None 
    for a in ('Left', 'Right'):
        nxt_state = transitions[(state, a)]
        v2, _ = min_value(nxt_state, alpha, beta)

        # get the max of the mins
        if v2 > v:
            v, move = v2, a 
            alpha = max(alpha, v) # max we have seen so far

        # beta cut-off 
        if v2 >= beta:
            return v, move

    return v, move 

def min_value(state, alpha, beta):
    if is_terminal(state):
        return outcomes[state], None

    v, move = float('inf'), None 
    for a in ('Left', 'Right'):
        nxt_state = transitions[(state, a)]
        v2, _ = max_value(nxt_state, alpha, beta)

        # get the min of the maxes
        if v2 < v:
            v, move = v2, a 
            beta = min(beta, v)

        # alpha cut-off 
        if v2 <= alpha:
            return v, move 

    return v, move 

def is_terminal(state):
    if state in outcomes:
        return True 

    return False 

if __name__ == "__main__":
    v, move = alpha_beta_search('A')
    print(v, move)