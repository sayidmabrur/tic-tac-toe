// Transport for GitHub Pages: no server. The project's own Python (api.py,
// mcts_agent*.py, game.py) runs in the browser with Pyodide, and call() invokes
// game.handle_json() directly. Smaller limits because Pyodide is slower than
// native Python and MCTS blocks the page while it thinks.
window.LIMITS = {size: 6, iterations: 3000};

const PYODIDE_URL = "https://cdn.jsdelivr.net/pyodide/v0.27.2/full/";
const PY_FILES = ["api.py", "mcts_agent.py", "mcts_agent_xoxo.py", "game.py"];

const ready = (async () => {
  const {loadPyodide} = await import(PYODIDE_URL + "pyodide.mjs");
  const pyodide = await loadPyodide({indexURL: PYODIDE_URL});
  await pyodide.loadPackage("numpy");
  for (const file of PY_FILES) {
    const res = await fetch(file);
    if (!res.ok) throw new Error(`could not load ${file}`);
    pyodide.FS.writeFile("/home/pyodide/" + file, await res.text());
  }
  pyodide.runPython(`
import sys
sys.path.insert(0, "/home/pyodide")
import game
game.MAX_SIZE = ${window.LIMITS.size}
game.MAX_ITERATIONS = ${window.LIMITS.iterations}
`);
  return pyodide.pyimport("game");
})();

async function call(path, body) {
  const game = await ready;
  const out = JSON.parse(game.handle_json(path, JSON.stringify(body ?? {})));
  if (out.status >= 400) throw new Error(out.data.error);
  return out.data;
}
