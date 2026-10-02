"""Builds docs/ for GitHub Pages: the same page + Python files, running in the
browser with Pyodide instead of the local server.

    python build_pages.py
"""
import shutil
from pathlib import Path

HERE = Path(__file__).parent
DOCS = HERE / "docs"

FILES = {
    "page.html": "index.html",
    "transport_pyodide.js": "transport.js",
    "api.py": "api.py",
    "mcts_agent.py": "mcts_agent.py",
    "mcts_agent_xoxo.py": "mcts_agent_xoxo.py",
    "game.py": "game.py",
}

DOCS.mkdir(exist_ok=True)
for source, target in FILES.items():
    shutil.copyfile(HERE / source, DOCS / target)
    print(f"docs/{target}")
