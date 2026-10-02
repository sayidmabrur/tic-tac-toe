# Tic-tac-Toe & XOXO Implementation of MCTS

a toy playground to play against agent implemented using Monte Carlo Tree Search (MCTS).

Tic-tac-toe has a small, deterministic action space. Which a good playground to understand how MCTS works.

to expand the game, we implemented MCTS TO XO game as well.


## Running the game

To run the game against MCTS agent. Run the following command:
```
python board.py
```

The system will prompt for legal actions:
```
legal_actions <= 9 
```

## Player Action
1. Flip a coin | Player will be prompted to pick 'HEAD' or 'TAIL' of a coin to decide who moves first.
2. On the player turn, the player would be provided with legal actions, enter only the index of the action which represent the board's position (0 - N) | N <= 9

Example:
```
possible actions:
[(0, 0), (0, 1), ... (row, column)]
please select action (0-N_action): 1 # Player will select board (0, 1)

Board:
[0, x, 0]
[0, 0, 0]
[0, 0, 0]
```


## Project Structure

- api.py ~ helper functions
- board.py ~ game environment
- mcts_agent.py ~ the agent source code

## Results
