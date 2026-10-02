from __future__ import annotations

# TicTacToe
from copy import deepcopy
import random

from api import check_win_conditions_xoxo, ucb


class Policy:

    def action(self, state) -> int:
        action = mcts_search(state, iterations=500)
        return action

    pass


class MCTSNode:
    def __init__(self, state, parent=None, action=None):
        self.state = state
        self.ucb = 0.0
        self.visits = 0
        self.action = action
        self.untried_actions = state.get_action_lists()
        self.children = []
        self.visits = 0
        self.parent = parent
        self.wins = 0.0

    def is_terminal(self):
        return check_win_conditions_xoxo(self.state.board_state)[1] != 0 or len(self.state.get_action_lists()) == 0

    def is_fully_expanded(self):
        return len(self.untried_actions) == 0

    def expand(self):
        action = self.untried_actions.pop()
        new_state = deepcopy(self.state)

        player_to_move = self.state.current_player_idx
        new_state.apply_action(player_to_move, action)

        child = MCTSNode(new_state, parent=self, action=len(self.untried_actions))
        self.children.append(child)
        return child
        pass

    def best_child(self, c=1.4):
        for child in self.children:
            if child.visits == 0:
                return child
        # print("children:")
        return max(self.children, key=lambda child: ucb(child, c, self.visits))

    def rollout(self):
        state = deepcopy(self.state)
        player = state.current_player_idx

        while True:
            _, winner, _ = check_win_conditions_xoxo(state.board_state)

            if winner != 0:
                return winner
            actions = state.get_action_lists()
            if not actions or len(actions) == 0:
                return None
            move = random.choice(actions)
            state.apply_action(player, move)
            player = state.current_player_idx



    def backpropagate(self, winner):
        self.visits += 1

        # credit the player who moved into this node (the one NOT to move here)
        mover = 2 if self.state.current_player_idx == 1 else 1
        if winner is None:
            self.wins += 0.5
        elif winner == mover:
            self.wins += 1.0

        if self.parent:
            self.parent.backpropagate(winner)
        pass


def mcts_search(state, iterations=1000) -> int:
    root = MCTSNode(state)
    for _ in range(iterations):
        node = root
        while not node.is_terminal() and node.is_fully_expanded():
            node = node.best_child()

        if not node.is_terminal() and not node.is_fully_expanded():
            node = node.expand()
        winner = node.rollout()
        node.backpropagate(winner)


    best = max(root.children, key = lambda c: c.visits)
    # print(best)
    return best.action
