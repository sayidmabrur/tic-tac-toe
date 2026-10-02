"""Browser visualizer for the tic-tac-toe / XOXO MCTS agents.

    python visualizer.py [port]     ->  http://127.0.0.1:8000

Standard library only. The board classes in tictactoe_board.py / xoxo_board.py
start a game when imported, so a small board class lives here instead; the win
rules (api.py) and the agents (mcts_agent*.py) are reused as they are.
"""
import json
import sys
import threading
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

import numpy as np

from api import check_win_conditions, check_win_conditions_xoxo, get_xoxo_lines, get_xoxo_scores
import mcts_agent
import mcts_agent_xoxo


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


class Handler(BaseHTTPRequestHandler):
    def log_message(self, *args):
        pass

    def send_json(self, payload, status=200):
        body = json.dumps(payload).encode()
        self.send_response(status)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def do_GET(self):
        if self.path == "/state":
            with lock:
                return self.send_json(game.to_dict())
        if self.path != "/":
            return self.send_json({"error": "not found"}, 404)
        body = PAGE.encode()
        self.send_response(200)
        self.send_header("Content-Type", "text/html; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def do_POST(self):
        global game
        length = int(self.headers.get("Content-Length", 0))
        try:
            data = json.loads(self.rfile.read(length) or b"{}")
            with lock:
                if self.path == "/new":
                    game = Game(
                        kind=data.get("kind", "tictactoe"),
                        size=max(3, min(int(data.get("size", 3)), 8)),
                        human=int(data.get("human", 1)),
                        iterations=max(10, min(int(data.get("iterations", 1000)), 20000)),
                    )
                elif self.path == "/move":
                    game.human_move(int(data["row"]), int(data["col"]))
                elif self.path == "/agent":
                    game.agent_move()
                else:
                    return self.send_json({"error": "not found"}, 404)
                self.send_json(game.to_dict())
        except (ValueError, KeyError) as error:
            self.send_json({"error": str(error)}, 400)


PAGE = """<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>MCTS Visualizer</title>
<style>
  :root { --bg:#f6f5f1; --panel:#fff; --ink:#1d1d1f; --muted:#6b6b70; --line:#d9d7cf;
          --x:#d6451f; --o:#1f6fd6; --accent:#1d1d1f; }
  @media (prefers-color-scheme: dark) {
    :root { --bg:#16161a; --panel:#202026; --ink:#f0f0f2; --muted:#9a9aa3; --line:#3a3a44;
            --x:#ff7a59; --o:#6aa6ff; --accent:#f0f0f2; }
  }
  * { box-sizing: border-box; }
  body { margin:0; padding:24px 16px; background:var(--bg); color:var(--ink);
         font:16px/1.4 system-ui, sans-serif; display:flex; justify-content:center; }
  main { width:100%; max-width:520px; }
  h1 { font-size:20px; margin:0 0 16px; }
  .panel { background:var(--panel); border:1px solid var(--line); border-radius:12px; padding:16px; }
  .controls { display:grid; grid-template-columns:1fr 1fr; gap:10px; margin-bottom:16px; }
  .controls button.primary { cursor:pointer; }
  label { display:flex; flex-direction:column; gap:4px; font-size:12px; color:var(--muted); }
  select, input, button { font:inherit; color:var(--ink); background:var(--bg);
         border:1px solid var(--line); border-radius:8px; padding:8px; }
  button.primary { background:var(--accent); color:var(--bg); border-color:var(--accent); }
  #status { margin:16px 0 8px; font-weight:600; min-height:1.4em; }
  #scores { color:var(--muted); min-height:1.4em; margin-bottom:12px; }
  #board { display:grid; gap:6px; margin:0 auto; width:100%; max-width:440px; position:relative; }
  #strikes { position:absolute; inset:0; width:100%; height:100%; pointer-events:none; }
  #strikes line { stroke-width:6; stroke-linecap:round; opacity:.8; }
  #strikes line.x { stroke:var(--x); } #strikes line.o { stroke:var(--o); }
  .cell { aspect-ratio:1; background:var(--panel); border:1px solid var(--line);
          border-radius:8px; font-size:clamp(20px, 7vw, 44px); font-weight:700; padding:0;
          cursor:pointer; display:flex; align-items:center; justify-content:center; }
  .cell:disabled { cursor:default; }
  .cell.x { color:var(--x); } .cell.o { color:var(--o); }
  .cell.last { outline:3px solid var(--accent); outline-offset:-3px; }
  .cell.open:not(:disabled):hover { background:var(--bg); }
</style>
</head>
<body>
<main>
  <h1>MCTS Visualizer</h1>
  <div class="panel">
    <div class="controls">
      <label>Game
        <select id="kind"><option value="tictactoe">Tic-tac-toe</option><option value="xoxo">XOXO</option></select>
      </label>
      <label>Board size
        <input id="size" type="number" min="3" max="8" value="3">
      </label>
      <label>You play
        <select id="human">
          <option value="1">X (first)</option><option value="2">O (second)</option>
          <option value="0">Nobody (agent vs agent)</option>
        </select>
      </label>
      <label>MCTS iterations
        <input id="iterations" type="number" min="10" max="20000" step="100" value="1000">
      </label>
      <button class="primary" id="new">New game</button>
      <button class="primary" id="simulate">Simulate MCTS vs MCTS</button>
    </div>
    <div id="status"></div>
    <div id="scores"></div>
    <div id="board"></div>
  </div>
</main>
<script>
const $ = id => document.getElementById(id);
const MARK = {1:"X", 2:"O"};
let busy = false, run = 0, prev = null, last = null;

async function call(path, body) {
  const res = await fetch(path, body === undefined ? {} :
    {method:"POST", headers:{"Content-Type":"application/json"}, body:JSON.stringify(body)});
  const data = await res.json();
  if (!res.ok) throw new Error(data.error);
  return data;
}

// draw a line through every scoring 3-in-a-row (XOXO), centred on the cells
function drawStrikes(s) {
  if (!s.lines || !s.lines.length) return;
  const board = $("board");
  const cells = board.querySelectorAll(".cell");
  const NS = "http://www.w3.org/2000/svg";
  const svg = document.createElementNS(NS, "svg");
  svg.id = "strikes";
  const centre = ([r, c]) => {
    const el = cells[r * s.size + c];
    return [el.offsetLeft + el.offsetWidth / 2, el.offsetTop + el.offsetHeight / 2];
  };
  s.lines.forEach(l => {
    const [x1, y1] = centre(l.from), [x2, y2] = centre(l.to);
    const line = document.createElementNS(NS, "line");
    line.setAttribute("class", MARK[l.player].toLowerCase());
    line.setAttribute("x1", x1); line.setAttribute("y1", y1);
    line.setAttribute("x2", x2); line.setAttribute("y2", y2);
    svg.appendChild(line);
  });
  board.appendChild(svg);
}

function render(s) {
  // highlight the cell that changed since the last state
  if (s !== prev) {
    last = null;
    if (prev && prev.size === s.size) {
      s.board.forEach((row, r) => row.forEach((v, c) => { if (v !== prev.board[r][c]) last = [r, c]; }));
    }
    prev = s;
  }

  const humanTurn = !s.finished && s.current === s.human;
  const board = $("board");
  board.style.gridTemplateColumns = `repeat(${s.size}, 1fr)`;
  board.innerHTML = "";
  s.board.forEach((row, r) => row.forEach((v, c) => {
    const b = document.createElement("button");
    b.className = "cell" + (v ? " " + MARK[v].toLowerCase() : " open") +
      (last && last[0] === r && last[1] === c ? " last" : "");
    b.textContent = v ? MARK[v] : "";
    b.disabled = !humanTurn || v !== 0 || busy;
    b.onclick = () => humanMove(r, c);
    board.appendChild(b);
  }));
  drawStrikes(s);

  $("scores").textContent = s.scores ? `Score  X: ${s.scores[0]}   O: ${s.scores[1]}` : "";
  if (s.finished) {
    $("status").textContent = s.winner === 0 ? "Draw" :
      (s.human === 0 ? `${MARK[s.winner]} wins` : (s.winner === s.human ? "You win!" : "MCTS wins"));
  } else if (s.human === 0) {
    $("status").textContent = `${MARK[s.current]} (MCTS) is thinking...`;
  } else {
    $("status").textContent = humanTurn ? `Your turn (${MARK[s.human]})` : "MCTS is thinking...";
  }
}

async function advance(s, myRun) {
  // let the agent move while it is the agent's turn
  while (!s.finished && s.current !== s.human && myRun === run) {
    busy = true; render(s);
    await new Promise(r => setTimeout(r, s.human === 0 ? 400 : 50));
    if (myRun !== run) return;
    s = await call("/agent", {});
  }
  busy = false;
  if (myRun === run) render(s);
}

async function humanMove(r, c) {
  if (busy) return;
  try {
    busy = true;
    const s = await call("/move", {row:r, col:c});
    render(s);
    await advance(s, run);
  } catch (e) { busy = false; $("status").textContent = e.message; }
}

async function newGame(human = +$("human").value) {
  run += 1; prev = null;
  try {
    const s = await call("/new", {
      kind: $("kind").value, size: +$("size").value, human: human,
      iterations: +$("iterations").value });
    await advance(s, run);
  } catch (e) { busy = false; $("status").textContent = e.message; }
}

window.addEventListener("resize", () => { if (prev) render(prev); });
$("new").onclick = () => newGame();
// agent vs agent with the current game / size / iterations settings
$("simulate").onclick = () => newGame(0);
newGame();
</script>
</body>
</html>
"""


if __name__ == "__main__":
    port = int(sys.argv[1]) if len(sys.argv) > 1 else 8000
    server = ThreadingHTTPServer(("127.0.0.1", port), Handler)
    print(f"MCTS visualizer running at http://127.0.0.1:{port} (Ctrl+C to stop)")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
