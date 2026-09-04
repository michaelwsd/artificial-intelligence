# FIT3080 Assignment 1 - Pacman Search and Adversarial Agents

Search and adversarial-search agents built on the UC Berkeley Pacman framework, written for
FIT3080 (Intelligent Systems) Assignment 1 at Monash.

Three agents are implemented:

| Question | Task | Technique | Files |
| --- | --- | --- | --- |
| **Q1a** | Reach a single food dot | A\* with Manhattan heuristic | `problems/q1a_problem.py`, `solvers/q1a_solver.py` |
| **Q1b** | Eat dots to maximise score | Repeated A\* to nearest dot, returning the best-scoring prefix | `problems/q1b_problem.py`, `solvers/q1b_solver.py` |
| **Q2** | Play full Pacman against ghosts | Minimax with alpha-beta pruning and a hand-tuned evaluation | `agents/q2Agent.py` |

Q1c was not part of this assignment. `solvers/q1c_solver.py` and `problems/q1c_problem.py`
do not exist, though the `q1c_*.lay` layouts ship with the framework. See
[Batch evaluation](#batch-evaluation) for why that matters.

---

## Contents

- [Quick start](#quick-start)
- [How the framework fits together](#how-the-framework-fits-together)
- [Command-line reference](#command-line-reference)
- [Q1a - single-dot search](#q1a---single-dot-search)
- [Q1b - score-maximising dot collection](#q1b---score-maximising-dot-collection)
- [Q2 - adversarial agent](#q2---adversarial-agent)
- [Batch evaluation](#batch-evaluation)
- [Known limitations](#known-limitations)
- [Repository layout](#repository-layout)
- [Attribution](#attribution)

---

## Quick start

Requires Python 3.10+ (developed and tested on 3.14). The game needs only the standard
library, plus `tkinter` for the graphical display.

```bash
python -m venv .venv
source .venv/bin/activate          # Windows: .venv\Scripts\activate
pip install pandas tqdm            # only needed for evaluator.py
```

```bash
# Q1a - single dot
python pacman.py -l q1a_mediumMaze.lay -p SearchAgent -a fn=q1a_solver,prob=q1a_problem

# Q1b - eat all dots
python pacman.py -l q1b_mediumCorners.lay -p SearchAgent -a fn=q1b_solver,prob=q1b_problem

# Q2 - play against ghosts
python pacman.py -l q2_smallClassic.lay -p Q2_Agent -f
```

Add `-q` to disable graphics, which is much faster and required for meaningful timings.

### Scoring

Every layout scores the same way, which is worth internalising because it drives the whole
Q1b design:

```
score = 10 * (dots eaten) + 500 (if won) - (ticks elapsed) - 500 (if eaten by a ghost)
```

Each step costs exactly 1 point. `q1a_tinyMaze` scores 502 because it eats one dot and wins
in 8 steps: `10 + 500 - 8`.

---

## How the framework fits together

The three moving parts are deliberately decoupled:

- **A problem** (`problems/`) defines the state space: `getStartState()`, `isGoalState(state)`
  and `getSuccessors(state)`, the last returning `(successor, action, stepCost)` triples.
  It knows nothing about how it will be searched.
- **A solver** (`solvers/`) is a function taking a problem and returning a list of actions.
  It knows nothing about Pacman specifically.
- **An agent** (`agents/`) is what the game actually drives. `SearchAgent` is a generic
  adapter: it resolves a solver and a problem by name, runs the search once up front in
  `registerInitialState`, and then just replays the resulting action list.

`SearchAgent` wires them together via `util.import_by_name`, which scans a directory for a
module defining the requested name:

```python
function = util.import_by_name('./solvers', fn)     # e.g. q1a_solver
problem  = util.import_by_name('./problems', prob)  # e.g. q1a_problem
```

That is why the CLI takes `-a fn=q1a_solver,prob=q1a_problem` rather than an import path,
and why a missing solver surfaces as `ImportError: q1c_solver not found in ./solvers`.

Q2 skips this layer entirely. `Q2_Agent` is a real-time agent: rather than planning once, it
runs a fresh search from the current state on every tick inside `getAction`.

### Solvers are split into initialise/loop-body

Both solvers are structured as `astar_initialise` plus `astar_loop_body` rather than a single
loop, so the driver can count node expansions:

```python
while not terminate:
    num_expansions += 1
    terminate, result = astar_loop_body(problem, astarData)
```

`log_function` decorates the problem methods to write input/output traces to `logs/` for
grading, capped at 1000 calls.

---

## Command-line reference

| Flag | Effect |
| --- | --- |
| `-l <layout>` | Layout to play. See the note below |
| `-p <agent>` | Pacman agent class, resolved from `agents/` |
| `-a <k=v,...>` | Arguments passed to the agent constructor |
| `-q` | No graphics. Much faster; use this for timing |
| `-t` | ASCII graphics instead of the Tk window |
| `-f` | Fix the random seed. Ghosts move randomly, so use this for reproducible runs |
| `-n <k>` | Play `k` games and report average score and win rate |
| `-k <k>` | Number of ghosts |
| `-g <type>` | Ghost agent, e.g. `RandomGhost`, `DirectionalGhost` |
| `--timeout=<s>` | Per-game time limit in seconds |
| `-z <float>` | Zoom the graphics window |
| `-r` / `--replay` | Record a game to file / replay one |

**`-l` is not a plain layout name.** `runGames` branches on the suffix:

```python
if layout.endswith('.lay'):
    layoutNames = [layout]
else:
    layoutNames = [f for f in os.listdir(layout) if f.endswith('.lay')]
```

So `-l q1a_mediumMaze.lay` runs that one layout, but `-l q1a_mediumMaze` is treated as a
*directory* and fails with `FileNotFoundError`. Dropping the `.lay` is the most common way to
trip over this. The upside is that `-l layouts/ -n 20` is a legitimate way to cycle through
every layout in a directory.

Layouts are prefixed by question: `q1a_*` (one dot), `q1b_*` (four corner dots),
`q1c_*` (many dots), `q2_*` (dots, capsules and a ghost).

---

## Q1a - single-dot search

### Problem

The simplest possible formulation. State is a bare `(x, y)` position; successors are the four
non-wall neighbours at unit cost; the goal is the single food dot, read once at construction:

```python
foodList = gameState.getFood().asList()
self.goal = foodList[0] if foodList else self.startState
```

### Solver

Textbook A\*, with `costs` and `parents` dictionaries and a `visited` set. `util.PriorityQueue`
does expose an `update` (decrease-key), but it is a linear scan plus a heap rebuild on every
call. The solvers instead push a state again whenever a cheaper path to it is found and skip
stale duplicates on pop, which is the cheaper and more usual choice:

```python
while not astarData.frontier.isEmpty():
    candidate = astarData.frontier.pop()
    if candidate not in astarData.visited:
        state = candidate
        break
```

The action list is reconstructed by walking `parents` backwards from the goal and reversing.

The heuristic is Manhattan distance, which the spec mandated. It is admissible, since walls
can only make the true path longer, never shorter, so A\* remains optimal.

### Results

All 10 layouts, deterministic:

| Layout | Size | Expansions | Path | Time (s) | Score |
| --- | --- | --- | --- | --- | --- |
| `q1a_tinyMaze` | 7x7 | 15 | 8 | 0.00007 | 502 |
| `q1a_testMaze` | 30x3 | 28 | 27 | 0.00010 | 483 |
| `q1a_contoursMaze` | 21x11 | 50 | 13 | 0.00018 | 497 |
| `q1a_smallMaze` | 22x10 | 54 | 19 | 0.00016 | 491 |
| `q1a_trickyMaze` | 20x7 | 60 | 41 | 0.00018 | 469 |
| `q1a_mediumMaze2` | 30x14 | 146 | 50 | 0.00050 | 460 |
| `q1a_bigMaze2` | 37x37 | 155 | 58 | 0.00054 | 452 |
| `q1a_mediumMaze` | 37x18 | 222 | 68 | 0.00071 | 442 |
| `q1a_openMaze` | 37x23 | 536 | 54 | 0.00258 | 456 |
| `q1a_bigMaze` | 37x37 | 550 | 210 | 0.00249 | 300 |

Win rate 10/10. `q1a_openMaze` is the clearest illustration of the heuristic's weakness: it
needs 536 expansions for a 54-step path, nearly ten nodes per step, because an open room gives
Manhattan distance many equally-promising directions to explore.

---

## Q1b - score-maximising dot collection

### Problem

State is `(position, frozenset(remaining_food))`. The frozenset makes states hashable so they
can go in dictionaries and sets, and removing a dot produces a new set rather than mutating a
shared one.

A flood fill from Pacman's start position runs once at construction:

```python
reachable_food = [f for f in all_food if f in reachable_cells]
self.can_clear = len(all_food) == len(reachable_food)
```

Unreachable dots are dropped from the state entirely, and `can_clear` records whether the
500-point win bonus is achievable at all. This matters on `q1b_closed`, covered below.

### Solver

The design turns on one observation about the scoring rule: **the score only ever increases
when a dot is eaten, and decreases by 1 on every other tick.** So every local maximum of the
score occurs immediately after eating a dot, and the optimal plan is always a prefix of some
dot-to-dot path that ends on a dot. There is never a reason to stop mid-corridor.

The solver exploits that directly:

1. Run A\* from the current position toward the nearest remaining dot. The heuristic is the
   minimum Manhattan distance over all remaining dots, which stays admissible because at
   least one dot must be reached.
2. On reaching a dot, append that leg to the running plan, update
   `score = 10 * collected - travelled` (plus 500 if everything is cleared and `can_clear`),
   and record the plan length if this is the best score seen.
3. **Restart the search** from the new position. The frontier cannot be reused: the heuristic
   depends on the remaining-food set, and that set just shrank, so every priority already
   sitting in the queue is stale.
4. When the food runs out or the frontier empties, return `plan[:bestLength]` rather than the
   whole plan.

That truncation is the part that makes it score-maximising rather than merely greedy. It
cannot choose *which* dots to visit, but it can decide *when to stop*, and it stops at the
best point it actually saw.

### Results

All 11 layouts, deterministic:

| Layout | Size | Dots | Expansions | Path | Time (s) | Score | Won |
| --- | --- | --- | --- | --- | --- | --- | --- |
| `q1b_tinyCorners2` | 5x5 | 4 | 16 | 11 | 0.00011 | 529 | yes |
| `q1b_tinyCorners` | 8x8 | 4 | 47 | 32 | 0.00022 | 508 | yes |
| `q1b_closed` | 20x7 | 3 | 55 | 0 | 0.00022 | 0 | no |
| `q1b_trickyCorners` | 20x7 | 4 | 81 | 52 | 0.00036 | 488 | yes |
| `q1b_smallCorners` | 22x10 | 4 | 122 | 81 | 0.00052 | 459 | yes |
| `q1b_openCorners2` | 21x11 | 4 | 205 | 47 | 0.00129 | 493 | yes |
| `q1b_mediumCorners` | 30x14 | 4 | 255 | 106 | 0.00115 | 434 | yes |
| `q1b_mediumCorners2` | 36x18 | 4 | 346 | 164 | 0.00148 | 376 | yes |
| `q1b_bigCorners` | 37x37 | 4 | 364 | 162 | 0.00170 | 378 | yes |
| `q1b_openCorners` | 37x23 | 4 | 656 | 143 | 0.00347 | 397 | yes |
| `q1b_bigCorners2` | 37x37 | 4 | 1176 | 375 | 0.00531 | 165 | yes |

Win rate 10/11, every run finishing three orders of magnitude inside the 10-second limit.

**`q1b_closed` is a deliberate zero, not a failure.** All three of its dots are bricked in:

```
%%%%%%%%%%%%%%%%%%%%
%.%P          %    %
%%%% %% %% %% %% % %
%                % %
%%%%%%%%%%%%%%%%%% %
%.%.               %
%%%%%%%%%%%%%%%%%%%%
```

The flood fill finds no reachable food, so `remaining` is empty from the start and the solver
returns an empty plan. Since no dot can be eaten and every tick costs a point, standing
perfectly still scores 0, and 0 is the maximum achievable score on this layout. The 0/1 win
rate is unavoidable, not a bug.

---

## Q2 - adversarial agent

### Search

Standard minimax with alpha-beta pruning at depth 3. Pacman (agent 0) is the max node; each
ghost is its own min node, and the depth counter advances only after the *last* ghost has
moved, so one "depth" is a full round of the game rather than a single agent's move:

```python
last_ghost = agentIdx == state.getNumAgents() - 1
if last_ghost:
    depth += 1
```

Depth was chosen empirically: depth 2 scored measurably worse, depth 4 exceeded the time limit
on the larger layouts. Depth 3 is the balance point.

### Evaluation function

`betterScoreEvaluation` was built one feature at a time, each retained only where it produced a
measurable improvement:

| Term | Weight | Rationale |
| --- | --- | --- |
| Game score | `1.5x` | The dominant signal, deliberately amplified |
| Win / loss | `±1e10 + value` | Large but **finite**, so that among winning states the faster win still ranks higher. `±inf` would flatten that distinction and make all wins equal |
| Food remaining | `-10` each | Direct pressure to keep eating |
| Distance to nearest dot | `+1 / (d + 1)` | Deliberately capped below 1 so it can never outweigh the 1-point-per-tick time penalty. It acts purely as a tie-breaker between otherwise equal states |
| Non-scared ghost within 2 | `-300` | Contact is death. Beyond distance 2 the term is zero: fleeing a distant ghost has no value and only wastes ticks |
| Scared ghost | `+300 / (d + 1)` | Worth more than a dot, but only if close enough to reach before the timer runs out |
| Capsule, ghost within 8 | `+30 / (d + 1)` | Only rewarded when a ghost is nearby, so Pacman grabs a capsule and immediately cashes it in on a scared ghost rather than wasting it |

The keeping-it-below-1 detail on the food term is the subtlest part. A larger weight would let
Pacman gain more by hovering next to a dot than it loses to the clock, which stalls it.

Distance to the nearest dot uses **BFS through the maze** (`get_closest_food`), so walls are
respected. Ghost and capsule distances stay on Manhattan, which is cheap and accurate enough at
the short ranges where those terms are non-zero.

### Results

All 12 layouts with `-f` (fixed seed), one game each:

| Layout | Size | Dots | Capsules | Score | Result | Time |
| --- | --- | --- | --- | --- | --- | --- |
| `q2_originalClassic` | 28x27 | 229 | 4 | 3008 | win | 2.6s |
| `q2_mediumClassic2` | 36x18 | 243 | 4 | 2387 | win | 2.8s |
| `q2_trickyClassic` | 20x13 | 114 | 6 | 2034 | win | 1.0s |
| `q2_contestClassic` | 20x9 | 69 | 6 | 1683 | win | 0.3s |
| `q2_dangerClassic` | 31x8 | 101 | 4 | 1659 | win | 0.8s |
| `q2_mediumClassic` | 20x11 | 95 | 2 | 1480 | win | 0.6s |
| `q2_openClassic` | 25x9 | 86 | 1 | 1400 | win | 2.5s |
| `q2_smallClassic` | 20x7 | 55 | 2 | 1153 | win | 0.3s |
| `q2_testClassic` | 5x10 | 8 | 0 | 562 | win | 0.1s |
| `q2_minimaxClassic` | 10x5 | 2 | 0 | 516 | win | 0.0s |
| `q2_capsuleClassic` | 20x7 | 23 | 3 | -5 | loss | 0.2s |
| `q2_trappedClassic` | 8x5 | 4 | 0 | -496 | loss | 0.1s |

10/12 on this seed. Both losses are worth reading carefully, because only one is a real
weakness:

- **`q2_capsuleClassic` is seed noise, not a defect.** Over 10 games on random seeds it wins
  9/10 with an average score of **864.5** (`1068, 808, 841, 852, 956, 1067, -260, 1050, 1002,
  1261`). The single fixed seed happened to land on the bad run. This is the clearest argument
  for judging Q2 with `-n 10` rather than a single `-f` game.
- **`q2_trappedClassic` is unwinnable by construction.** 0/10 over random seeds, always -500:

  ```
  %%%%%%%%
  %   P  %
  %G%%%%%%
  %....  %
  %%%%%%%%
  ```

  The only route from Pacman to the dots runs through the single gap the ghost occupies. No
  policy wins here; the agent correctly recognises every branch loses and takes one.

Self-recorded score on the grading portal: **21.99 / 24**.

---

## Batch evaluation

`evaluator.py` runs every layout for every question and prints a markdown results table.

```bash
python evaluator.py --q1c
```

Three things will bite you:

1. **The flags are inverted.** Each `--qXX` option is declared `action='store_false'` with
   `default=True`, so passing `--q1c` *disables* Q1c. Bare `python evaluator.py` runs
   everything, which is the opposite of what the flag names suggest.
2. **You must pass `--q1c`.** Q1c is unimplemented here, so including it makes `pacman.py`
   raise `ImportError: q1c_solver not found in ./solvers`. The evaluator treats a non-zero
   subprocess exit as fatal and calls `exit(1)`, killing the whole run.
3. **It needs `pandas` and `tqdm`**, which the framework itself does not require.

It also clears `logs/*.log` on startup and prompts for a confirmation before running.

For quick checks, driving `pacman.py` directly with `-n` is usually faster than the full sweep.

---

## Known limitations

- **Manhattan distance ignores walls.** In twisty mazes A\* expands far more states than
  necessary before it can confirm optimality, most visibly on `q1a_openMaze` (536 expansions
  for a 54-step path). Precomputing a maze-distance table would make the heuristic exact,
  which is the tightest admissible heuristic possible, and would cut expansions substantially.
  It was never worth doing here: solve times are three orders of magnitude inside the limit,
  so the extra expansions cost nothing that is actually being marked.
- **Q1b is greedy about ordering.** It can decide when to stop but never which dots to skip or
  in what order to take them. A lone nearby dot beats a slightly more distant cluster, which is
  the wrong call. True optimality needs a TSP-style ordering over reachable dots, which grows
  as `n!` and would blow the time limit on anything but the tiny layouts.
- **Q2's evaluation only ever sees one dot.** It has no notion of a route, so on layouts like
  `q2_mediumClassic2` Pacman walks straight past an isolated dot and pays the time penalty to
  come back for it later. Rewarding the nearest *k* dots, or specifically rewarding isolated
  ones, would likely help.
- **Ghost movement is random**, so single-game scores are noisy, as `q2_capsuleClassic`
  demonstrates. Use `-f` for reproducibility or `-n` to average.
- **Depth 3 is a hard ceiling.** Depth 4 exceeds the time limit on larger layouts. Move
  ordering, or caching evaluations across ticks, would be the route to searching deeper.

---

## Repository layout

```
agents/
  q2Agent.py           Assignment work: alpha-beta agent and evaluation function
  searchAgents.py      Generic SearchAgent adapter (do not modify)
  ghostAgents.py, randomGhost.py, directionalGhost.py
  keyboardAgents.py, greedyAgent.py, goWestAgent.py, pacmanAgents.py
problems/
  q1a_problem.py       Positional search problem
  q1b_problem.py       Position + remaining-food search problem
solvers/
  q1a_solver.py        A*
  q1b_solver.py        Repeated A* with best-scoring prefix
layouts/               Maze definitions, prefixed by question
logs/
  search_logger.py     @log_function decorator producing grading traces
pacman.py              Game driver and CLI entry point
game.py                Core engine: agents, directions, game loop
util.py                PriorityQueue, distance helpers, import_by_name
layout.py              Layout file parsing
evaluator.py           Batch runner across all layouts
graphicsDisplay.py     Tk display
graphicsUtils.py       Tk primitives
textDisplay.py         ASCII and null displays
testParser.py          Test-case file parsing
```

### Files the grader reads

The automatic grading system only picks up these five. Everything else in the repository,
including this README, is ignored by it:

- `agents/q2Agent.py`
- `problems/q1a_problem.py`
- `problems/q1b_problem.py`
- `solvers/q1a_solver.py`
- `solvers/q1b_solver.py`

---

## Attribution

Built on the Pacman AI projects developed at UC Berkeley. The core projects and autograders
were created by John DeNero and Dan Klein, with student-side autograding added by Brad Miller,
Nick Hay and Pieter Abbeel. See http://ai.berkeley.edu.

Course scaffolding and the `q1*`/`q2*` layouts and logging harness were provided by FIT3080.
