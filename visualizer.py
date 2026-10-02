"""Browser visualizer for the tic-tac-toe / XOXO MCTS agents.

    python visualizer.py [port]     ->  http://127.0.0.1:8000

Standard library + numpy only. The game logic lives in game.py and the page in
page.html; build_pages.py packages the same files for GitHub Pages (Pyodide).
"""
import json
import sys
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

import game

HERE = Path(__file__).parent
STATIC = {
    "/": ("page.html", "text/html; charset=utf-8"),
    "/transport.js": ("transport_http.js", "text/javascript; charset=utf-8"),
}


class Handler(BaseHTTPRequestHandler):
    def log_message(self, *args):
        pass

    def send_body(self, body, content_type, status=200):
        self.send_response(status)
        self.send_header("Content-Type", content_type)
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def send_json(self, payload, status=200):
        self.send_body(json.dumps(payload).encode(), "application/json", status)

    def do_GET(self):
        if self.path in STATIC:
            name, content_type = STATIC[self.path]
            return self.send_body((HERE / name).read_bytes(), content_type)
        status, payload = game.handle(self.path)
        self.send_json(payload, status)

    def do_POST(self):
        length = int(self.headers.get("Content-Length", 0))
        try:
            data = json.loads(self.rfile.read(length) or b"{}")
        except ValueError:
            return self.send_json({"error": "invalid JSON"}, 400)
        status, payload = game.handle(self.path, data)
        self.send_json(payload, status)


if __name__ == "__main__":
    port = int(sys.argv[1]) if len(sys.argv) > 1 else 8000
    server = ThreadingHTTPServer(("127.0.0.1", port), Handler)
    print(f"MCTS visualizer running at http://127.0.0.1:{port} (Ctrl+C to stop)")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
