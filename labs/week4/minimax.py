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