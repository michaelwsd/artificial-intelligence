# FIT3080 - Artificial Intelligence

Coursework for FIT3080 (Artificial Intelligence) at Monash University, Semester 2, 2026.
The unit follows *Artificial Intelligence: A Modern Approach* (Russell & Norvig) and covers
search, logic, probabilistic reasoning, decision making under uncertainty and machine
learning. The programming assignments are built on the
[UC Berkeley Pacman AI framework](http://ai.berkeley.edu).

---

## Contents

- [Repository layout](#repository-layout)
- [Unit topics](#unit-topics)
- [Labs](#labs)
- [Practice questions](#practice-questions)
- [Assignments](#assignments)
- [Setup](#setup)
- [Attribution](#attribution)

---

## Repository layout

```
FIT3080/
├── lectures/              Lecture slides, lec1.pdf - lec12.pdf
├── labs/
│   ├── questions/         Applied class sheets, lab1.pdf - lab11.pdf
│   │   └── lab7_bn_dataset/   Netica network and CSV data for Lab 7
│   └── solutions/         Published solutions (labN_sol.pdf) and my own lab work
├── practice-questions/    Revision questions, one PDF per topic area
└── assignments/
    ├── a1/                Pacman search and adversarial agents (Python)
    ├── a2/                Bayesian networks in Netica (report + .dne models)
    └── a3/                Pacman MDPs, reinforcement learning and classification (Python)
```

---

## Unit topics

| # | Topic | Textbook | Lecture | Lab |
| --- | --- | --- | --- | --- |
| 1 | Introduction to AI | Ch. 1 | `lec1.pdf` | - |
| 2 | Intelligent agents (rationality, PEAS, environment types) | Ch. 2 | `lec2.pdf` | Lab 1 |
| 3 | Search I - problem formulation, uninformed search, backtracking | 3.1-3.4, 5.1, 5.3-5.4 | `lec3.pdf` | Lab 2 |
| 4 | Search II - informed search, A\*, admissible heuristics | 3.5-3.6 | `lec4.pdf` | Lab 3 |
| 5 | Search III - local (irrevocable) and adversarial search, minimax, alpha-beta | 4.1, 6.1-6.3 | `lec5.pdf` | Lab 4 |
| 6 | Propositional and first-order logic | 7.1, 7.3-7.5, 8.1-8.2, 9.1-9.2, 9.5 | `lec6.pdf` | Lab 5 |
| 7 | Probability and Bayesian networks | 14.1-14.4.1 (3rd ed.) | `lec7.pdf` | Lab 6 |
| 8 | Bayesian networks II - d-separation, inference, learning, decision networks | - | `lec8.pdf` | Lab 7 |
| 9 | Markov decision processes - value and policy iteration | - | `lec9.pdf` | Lab 8 |
| 10 | Reinforcement learning - TD learning, Q-learning, exploration | - | `lec10.pdf` | Lab 9 |
| 11 | Introduction to machine learning | 19.1-19.4.1, 19.6, 19.7.1 | `lec11.pdf` | Lab 10 |
| 12 | Machine learning II - artificial neural networks | 19.6.1-19.6.4, 22.1-22.3 | `lec12.pdf` | Lab 11 |

---

## Labs

Lab *N*'s sheet is `labs/questions/labN.pdf` and its published solution is
`labs/solutions/labN_sol.pdf`. Lab 11 has no published solution yet.

`labs/questions/` also holds the starter data for Lab 7 in `lab7_bn_dataset/`: an
unparameterised Netica network (`nfv3_unparameterised.dne`) plus complete, missing-value and
test CSVs for learning its parameters.

`labs/solutions/` also holds my own work:

| File | Lab | Contents |
| --- | --- | --- |
| `lab1-2_answers.ipynb` | 1-2 | Written answers to Labs 1 and 2 |
| `lab3_astar.py` | 3 | A\* on the Romania road map (Arad to Bucharest) with the straight-line-distance heuristic |
| `lab4_minimax.py` | 4 | Minimax and alpha-beta pruning over a 16-leaf game tree, to check which nodes get pruned |
| `lab4_q3b_alpha_beta.html` | 4 | Interactive step-by-step walkthrough of alpha-beta pruning for Q3(b) (open in a browser) |

```bash
python labs/solutions/lab3_astar.py
python labs/solutions/lab4_minimax.py
```

---

## Practice questions

Revision questions in `practice-questions/`, one file per topic area:

| File | Covers |
| --- | --- |
| `PracticeQuestionsFIT3080-Agents-Search.pdf` | Intelligent agents and search (topics 2-5) |
| `PracticeQuestionsFIT3080-KR.pdf` | Knowledge representation and logic (topic 6) |
| `PracticeQuestionsFIT3080-BNs.pdf` | Bayesian networks (topics 7-8) |
| `PracticeQuestionsFIT3080-MDPRL.pdf` | MDPs and reinforcement learning (topics 9-10) |
| `PracticeQuestionsFIT3080-ML.pdf` | Machine learning (topics 11-12) |

---

## Assignments

### A1 - Search and adversarial agents

Pacman agents for single-dot search, score-maximising dot collection and full games against
ghosts.

| Question | Technique |
| --- | --- |
| Q1a | A\* with a Manhattan-distance heuristic |
| Q1b | Repeated A\* to the nearest dot, keeping the best-scoring prefix |
| Q2 | Minimax with alpha-beta pruning and a hand-tuned evaluation function |

See [`assignments/a1/README.md`](assignments/a1/README.md) for run commands, design notes
and evaluation results.

### A2 - Bayesian networks (Netica)

Knowledge representation and reasoning for distinguishing bacterial from viral pneumonia,
worth 10% of the unit grade. Built in [Netica](https://www.norsys.com/netica.html).

| Question | Task | Deliverable |
| --- | --- | --- |
| Q1 | Causal 8-node BN structure | `*_A2_Q1.dne` |
| Q2 | Parameterisation from expert knowledge, literature and data | `*_A2_Q2.dne`, `q2_train/` |
| Q3 | Probabilistic reasoning queries | report |
| Q4 | Sensitivity analysis and performance on test data | report, `q4_test/` |
| Q5 | Decision network structure | `*_A2_Q5.dne` |
| Q6 | Decision making with expected utility | report |

The written answers are in `Wang-33899835-2ndSem2026FIT3080_A2.pdf` (and `.docx`), and the
assignment specification is `a2.pdf`.

### A3 - MDPs, reinforcement learning and classification

Pacman agents that learn or plan under uncertainty. In progress.

| Question | Technique | Files |
| --- | --- | --- |
| Q1 | Value iteration on a Pacman MDP | `agents/q1_agent.py`, `pacmanMDP.py`, `mdp.py` |
| Q2 | Q-learning with epsilon-greedy exploration | `agents/q2_agent.py`, `agents/learningAgents.py` |
| Q3 | Supervised learning of Pacman moves (MIRA / perceptron-style classifier) | `mira.py`, `featureExtraction.py`, `pacmandata/` |

```bash
cd assignments/a3
python pacman.py -l VI_smallMaze1.lay -p Q1Agent -g StationaryGhost
python pacman.py -l QL_small_1.lay -p Q2Agent
python evaluator.py              # batch-evaluate all questions
```

---

## Setup

Requires Python 3.10+ (the local `.venv` uses Python 3.14). The Pacman framework uses only
the standard library plus `tkinter` for graphics. Extra packages are needed for the lab code
and the evaluators.

```bash
python -m venv .venv
source .venv/bin/activate
pip install numpy pandas tqdm tabulate jupyter
```

Add `-q` to any `pacman.py` command to disable graphics, and `-h` to list all options.

A2 requires Netica (the free limited-model version is enough to open the `.dne` files).

---

## Attribution

- The Pacman framework was developed at UC Berkeley by John DeNero, Dan Klein and others,
  and adapted by the FIT3080 teaching team. See the license headers in each source file and
  [ai.berkeley.edu](http://ai.berkeley.edu).
- Lecture slides, lab sheets, published solutions, practice questions and assignment
  specifications are the property of Monash University and the FIT3080 teaching team. They
  are kept here for personal study only.
