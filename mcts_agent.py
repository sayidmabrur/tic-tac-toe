# TicTacToe
from board import TicTacToeBoard

class Policy:


    def action(self, state): -> int:

        action = mcts_search(state, iterations=500)


        return action

    pass


class MCTSNode:
    def __init__(self, state, parent=None, action=None, player=None):
        self.state = state
        self.parent = parent
        self.action = action
        self.player = player
        self.children = []
        self.visits = 0
        self.wins = 0.0
        self.untried_actions = state['actions']
        pass

    def is_terminal(self):
        return check_winner_state(self.state) is not None or not available_actions(self.state)
    def expand(self):
        

    def rollout(self):
        pass

    def backpropagate(self):
        pass


def mcts_search(state, iterations=500) -> int:
    for _ in range(iterations):

        node = select(root)
        if not node.is_terminal():
            node = expand(node)
        reward = rollout(node.state)
        backpropagate(node, reward)
        return best_child(root)
