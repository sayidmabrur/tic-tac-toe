import math
import numpy as np



# tic-tac-toe win condition check
def check_win_conditions(board_state):
    n_rows, n_cols = board_state.shape

    win_conditions = []
    # rows
    for row in range(n_rows):
        win_conditions.append({(row, col) for col in range(n_cols)})
    # columns
    for col in range(n_cols):
        win_conditions.append({(row, col) for row in range(n_rows)})
    # diagonals 
    if n_rows == n_cols:
        win_conditions.append({(i, i) for i in range(n_rows)})
        win_conditions.append({(i, n_cols - 1 - i) for i in range(n_rows)})

    p1_trajectory = get_trajectory(board_state, 1)
    p2_trajectory = get_trajectory(board_state, 2)
    # print('p1 traj:', p1_trajectory)
    # print('p2 traj:', p2_trajectory)

    for condition in win_conditions:
        if condition.issubset(p1_trajectory):
            return True, 1, 1
        elif condition.issubset(p2_trajectory):
            return True, 2, -1
    return False, 0, 0 #0 means game draw

# every scoring 3-in-a-row as (player, (row, col) start, (row, col) end)
def get_xoxo_lines(board_state):
    n_rows, n_cols = board_state.shape

    lines = []
    directions = [(0, 1), (1, 0), (1, 1), (1, -1)]
    for row in range(n_rows):
        for col in range(n_cols):
            player = int(board_state[row, col])
            if player == 0:
                continue
            for d_row, d_col in directions:
                end_row, end_col = row + 2 * d_row, col + 2 * d_col
                if not (0 <= end_row < n_rows and 0 <= end_col < n_cols):
                    continue
                if (board_state[row + d_row, col + d_col] == player
                        and board_state[end_row, end_col] == player):
                    lines.append((player, (row, col), (end_row, end_col)))

    return lines

def get_xoxo_scores(board_state):
    lines = get_xoxo_lines(board_state)
    p1_score = sum(1 for player, _, _ in lines if player == 1)
    p2_score = sum(1 for player, _, _ in lines if player == 2)

    return p1_score, p2_score

def check_win_conditions_xoxo(board_state):
    p1_score, p2_score = get_xoxo_scores(board_state)

    board_terminal = not (board_state == 0).any()

    if board_terminal and p1_score > p2_score:
        return True, 1, 1
    elif board_terminal and p2_score > p1_score:
        return True, 2, -1
    elif board_terminal:
        return True, 0, 0 

    return False, 0, 0 


def get_trajectory(board_state, player_index=1):
    rows, cols = np.where(board_state == player_index)
    return set(zip(rows.tolist(), cols.tolist()))


def ucb(child, c=1.4, visits=0):
    exploit = child.wins / child.visits
    explore = c * math.sqrt(math.log(visits) / child.visits)
    # print("ucb:", exploit + explore)
    return exploit + explore
