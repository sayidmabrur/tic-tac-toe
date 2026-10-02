"""Game state + request handling shared by the local server (visualizer.py) and
the in-browser Pyodide build (docs/).

Standard library + numpy only. The board classes in tictactoe_board.py /
xoxo_board.py start a game when imported, so a small board class lives here
instead; the win rules (api.py) and the agents (mcts_agent*.py) are reused as
they are.
"""
import json
import threading

import numpy as np

from api import check_win_conditions, check_win_conditions_xoxo, get_xoxo_lines, get_xoxo_scores
import mcts_agent
import mcts_agent_xoxo

MAX_SIZE = 8
MAX_ITERATIONS = 20000


class Board:
    """Same interface the MCTS agents expect from TicTacToeBoard / XoXoBoard."""

    def __init__(self, size):
        self.board_state = np.zeros((size, size), dtype=np.int8)
        self.current_player_idx = 1

    def get_action_lists(self):
        return [(int(r), int(c)) for r, c in np.argwhere(self.board_state == 0)]

    def apply_action(self, player_idx, action):
        self.board_state[action[0], action[1]] = player_idx
        self.current_player_idx = 2 if player_idx == 1 else 1


class Game:
    def __init__(self, kind="tictactoe", size=3, human=1, iterations=1000):
        self.kind = kind
        self.size = size
        self.human = human  # 1 = X, 2 = O, 0 = agent vs agent
        self.iterations = iterations
        self.board = Board(size)
        self.agent = mcts_agent_xoxo if kind == "xoxo" else mcts_agent

    def result(self):
        """Returns (finished, winner) where winner is 0 for a draw."""
        state = self.board.board_state
        if self.kind == "xoxo":
            finished, winner, _ = check_win_conditions_xoxo(state)
        else:
            finished, winner, _ = check_win_conditions(state)
            if not finished and not self.board.get_action_lists():
                finished = True
        return finished, winner

    def to_dict(self):
        finished, winner = self.result()
        data = {
            "kind": self.kind,
            "size": self.size,
            "human": self.human,
            "board": self.board.board_state.tolist(),
            "current": self.board.current_player_idx,
            "finished": finished,
            "winner": winner,
        }
        if self.kind == "xoxo":
            data["scores"] = list(get_xoxo_scores(self.board.board_state))
            data["lines"] = [
                {"player": player, "from": list(start), "to": list(end)}
                for player, start, end in get_xoxo_lines(self.board.board_state)
            ]
        return data

    def human_move(self, row, col):
        finished, _ = self.result()
        if finished:
            raise ValueError("the game is over")
        if self.board.current_player_idx != self.human:
            raise ValueError("it is not your turn")
        if (row, col) not in self.board.get_action_lists():
            raise ValueError("that cell is not available")
        self.board.apply_action(self.human, (row, col))

    def agent_move(self):
        finished, _ = self.result()
        if finished:
            raise ValueError("the game is over")
        if self.board.current_player_idx == self.human:
            raise ValueError("it is your turn")
        index = self.agent.mcts_search(self.board, self.iterations)
        action = self.board.get_action_lists()[index]
        self.board.apply_action(self.board.current_player_idx, action)


game = Game()
lock = threading.Lock()


def handle(path, data=None):
    """Routes one request. Returns (http_status, payload)."""
    global game
    data = data or {}
    try:
        with lock:
            if path == "/state":
                pass
            elif path == "/new":
                game = Game(
                    kind="xoxo" if data.get("kind") == "xoxo" else "tictactoe",
                    size=max(3, min(int(data.get("size", 3)), MAX_SIZE)),
                    human=int(data.get("human", 1)),
                    iterations=max(10, min(int(data.get("iterations", 1000)), MAX_ITERATIONS)),
                )
            elif path == "/move":
                game.human_move(int(data["row"]), int(data["col"]))
            elif path == "/agent":
                game.agent_move()
            else:
                return 404, {"error": "not found"}
            return 200, game.to_dict()
    except (ValueError, KeyError) as error:
        return 400, {"error": str(error)}


def handle_json(path, body="{}"):
    """Same as handle() with JSON strings in and out (used from Pyodide)."""
    status, payload = handle(path, json.loads(body or "{}"))
    return json.dumps({"status": status, "data": payload})
