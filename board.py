import numpy as np
import random


# tic tac toe is a:
# TicTacToe Environment Class
class TicTacToeBoard:

    board_state: np.ndarray
    player_1: dict
    player_2: dict
    player_turn_idx: dict
    current_player_idx: int
    # size row x columns
    def __init__(self, size: tuple):

        self.current_player_idx = 0
        self.init_board(size)


    # return True if winning false if not
    def check_win_conditions(self) -> bool:
        win_conditions = [
            # rows
            {(0, 0), (0, 1), (0, 2)},
            {(1, 0), (1, 1), (1, 2)},
            {(2, 0), (2, 1), (2, 2)},
            # columns
            {(0, 0), (1, 0), (2, 0)},
            {(0, 1), (1, 1), (2, 1)},
            {(0, 2), (1, 2), (2, 2)},
            # diagonals
            {(0, 0), (1, 1), (2, 2)},
            {(0, 2), (1, 1), (2, 0)},
        ]

        for condition in win_conditions:
            if condition.issubset(self.player_1['traj']):
                print("player 1 wins~congrats!")
                return True
            elif condition.issubset(self.player_2['traj']):
                print("player 2 wins~congrats!")
                return True
        return False




        return False
    def init_board(self, size):
        self.player_1 = {'traj': set()}
        self.player_2 = {'traj': set()}
        row_num, col_num = size
        self.board_state = np.zeros((row_num, col_num), dtype=np.int8)

    # only provide legal action move
    # if board state is filled, it'll return empty list
    # legal action move starts from index 0 ~ N-size
    # example:
    # board state init, legal action moves:
    # [[0, 0], [0, 1], [0, 2], [1,0], [1,1], [1,2] .. [row, col]]

    # if filled, action function won't return the filled index
    # board state:
    # [0, 0, 1]
    # [0, 2, 0]
    # [0, 0, 0]
    # legal actions: [0,0], [0,1], [1,0], [1,2], [2,0], [2,1], [2,2]

    # NOTE: 0 = unfilled, 1= player_1 trajectory, 2= payer_2 trajectory
    def get_action_lists(self, player_idx: int = 0):

        legal_actions = []

        row_idx = 0
        for i in self.board_state:
            row_col = 0
            for j in i:
                # print(row_idx, "~",row_col)
                if not self.board_state[row_idx][row_col]:
                    legal_actions.append((row_idx, row_col))
                row_col = row_col + 1
            row_idx = row_idx+1

        return legal_actions

    def apply_action(self, player_idx: int, action:list):

        # print("action_idx:", action_idx)
        # print("leg:", legal_actions[action_idx])

        # print("player_idx:", player_idx)
        # print("action:", action)
        self.board_state[action[0], action[1]] = player_idx
        if player_idx == 1:
            self.player_1['traj'].add(action)
        elif player_idx == 2:
            self.player_2['traj'].add(action)

        self.current_player_idx = self.current_player_idx +1 if self.current_player_idx <2 else self.current_player_idx -1
        # pass
    def reset(self):
        pass




# action is the index of the legal action
def player_1(state) -> int:
    action = 0

    print("Player 1(AI MCTS) action:", state['actions'][action])
    return action
    pass

def player_2(state) -> int:

    print("your turn, select your action")
    print("board:")
    print(state['board'])
    print("possible actions:")
    print(state['actions'])
    action = int(input(f"please select action (0-{len(state['actions'])-1}):"))
    pass
    return action


board = TicTacToeBoard((3, 3))


def act(p_idx, act_idx, board: TicTacToeBoard):
    legal_actions = board.get_action_lists()
    board.apply_action(p_idx, legal_actions[act_idx])
    pass

# game engine play


# register player
players = ["system", player_1, player_2]

# 
# !!GAME PLAY!!!
player_coin = int(input("turn selection, flip a coin to decide. Choose (HEAD=0, TAIL=1):"))
turns = 0
random_coin = random.randint(0, 1)
print("coin FLIP:", "HEAD" if random_coin == 0 else "TAIL")
board.current_player_idx = 2 if random_coin == player_coin else 1
while  not board.check_win_conditions() and len(board.get_action_lists()) != 0:

    state = {
        "board": board.board_state,
        "actions": board.get_action_lists()
    }
    player_action = players[board.current_player_idx](state)
    act(board.current_player_idx, player_action, board)


    turns += 1
    print("="*20)
    
print(f"game finished with {turns} turn!")
print('final board state:')
print(board.board_state)
