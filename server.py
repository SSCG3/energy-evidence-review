"""Local-only review workbench. No uploads or secrets are persisted."""
from http.server import ThreadingHTTPServer, SimpleHTTPRequestHandler
from pathlib import Path
import argparse
import json
import os
import secrets
from src.engine import review, summary
from src.corpus import ingest
ROOT = Path(__file__).resolve().parent
class Handler(SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=str(ROOT / "web"), **kwargs)
    def end_headers(self):
        self.send_header("X-Content-Type-Options", "nosniff")
        self.send_header("Cache-Control", "no-store")
        super().end_headers()
    def send_json(self, value, status=200):
        data = json.dumps(value, ensure_ascii=False).encode()
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(data)))
        self.end_headers()
        self.wfile.write(data)
    def do_GET(self):
        routes = {"/api/example": "examples/documents.json", "/api/results": "results/comparison.json", "/api/public-results": "results/public-data-comparison.json", "/api/model-results": "results/model-validation.json", "/api/sources": "examples/public_sources/manifest.json"}
        if self.path in routes:
            path = ROOT / routes[self.path]
            return self.send_json(json.loads(path.read_text()) if path.exists() else {})
        if self.path == "/technical-report.pdf":
            path = ROOT / "docs/technical-report.pdf"
            if not path.exists():
                return self.send_json({"error": "Report not generated"}, 404)
            body = path.read_bytes()
            self.send_response(200)
            self.send_header("Content-Type", "application/pdf")
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            self.wfile.write(body)
            return
        if self.path == "/api/config":
            return self.send_json({"version": "0.2.0", "model_configured": all(os.getenv(k) for k in ("MODEL_API_KEY", "MODEL_BASE_URL", "MODEL_NAME")), "csrf": self.server.csrf})
        return super().do_GET()
    def do_POST(self):
        # A local random request token prevents cross-site pages from spending the model key.
        if self.headers.get("X-Review-Token") != self.server.csrf:
            return self.send_json({"error": "Reload workbench to obtain request token"}, 403)
        origin = self.headers.get("Origin")
        if origin and origin not in (f"http://127.0.0.1:{self.server.server_port}", f"http://localhost:{self.server.server_port}"):
            return self.send_json({"error": "Cross-origin request rejected"}, 403)
        try:
            length = int(self.headers.get("Content-Length", "0"))
            if length <= 0 or length > 3000000:
                return self.send_json({"error": "Request must be 1 byte–3 MB"}, 413)
            data = json.loads(self.rfile.read(length))
            if self.path == "/api/ingest":
                return self.send_json(ingest(data.get("filename"), data.get("content")))
            if self.path == "/api/review":
                return self.send_json(review(data["documents"], data.get("question", ""), data.get("role", "public"), data.get("mode", "checked"), data.get("provider", "offline"), data.get("project")))
            if self.path == "/api/summary":
                return self.send_json(summary(data["documents"], data.get("role", "public"), data.get("project")))
            return self.send_json({"error": "Unknown endpoint"}, 404)
        except (ValueError, KeyError, TypeError) as exc:
            self.send_json({"error": str(exc)}, 400)
        except Exception:
            self.send_json({"error": "Processing failed; check local logs and input format"}, 500)
if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--port", type=int, default=8765)
    options = parser.parse_args()
    server = ThreadingHTTPServer(("127.0.0.1", options.port), Handler)
    server.csrf = secrets.token_urlsafe(24)
    print(f"Evidence Review Lab http://127.0.0.1:{options.port}", flush=True)
    server.serve_forever()
