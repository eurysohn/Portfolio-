"""Minimal HTTP API + static frontend server."""

from __future__ import annotations

import json
import os
from http import HTTPStatus
from http.server import BaseHTTPRequestHandler, HTTPServer
from pathlib import Path
from urllib.parse import parse_qs, urlparse

from observability.tracing import trace_store
from runtime.engine import AgentRuntime

FRONTEND_DIR = Path(__file__).resolve().parents[1] / "frontend"


def _serialize_result(result: object) -> dict:
    payload = result.__dict__
    payload["tool_results"] = [tool.__dict__ for tool in result.tool_results]
    payload["tool_calls"] = [call.__dict__ for call in result.tool_calls]
    return payload


class ApiHandler(BaseHTTPRequestHandler):
    runtime = AgentRuntime()

    def _set_headers(self, status: int, content_type: str) -> None:
        self.send_response(status)
        self.send_header("Content-Type", content_type)
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET,POST,OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
        self.end_headers()

    def _send_json(self, status: int, payload: dict) -> None:
        self._set_headers(status, "application/json")
        self.wfile.write(json.dumps(payload).encode("utf-8"))

    def _send_file(self, path: Path, content_type: str) -> None:
        if not path.exists():
            self._set_headers(HTTPStatus.NOT_FOUND, "text/plain")
            self.wfile.write(b"Not Found")
            return
        self._set_headers(HTTPStatus.OK, content_type)
        self.wfile.write(path.read_bytes())

    def do_OPTIONS(self) -> None:  # noqa: N802
        self._set_headers(HTTPStatus.NO_CONTENT, "text/plain")

    def do_GET(self) -> None:  # noqa: N802
        parsed = urlparse(self.path)
        if parsed.path == "/api/trace":
            params = parse_qs(parsed.query)
            run_id = params.get("run_id", [""])[0]
            if not run_id:
                self._send_json(HTTPStatus.BAD_REQUEST, {"error": "run_id required"})
                return
            events = trace_store.get_run(run_id) or trace_store.load_from_jsonl(run_id)
            self._send_json(HTTPStatus.OK, {"events": [event.__dict__ for event in events]})
            return
        if parsed.path in {"/", "/index.html"}:
            self._send_file(FRONTEND_DIR / "index.html", "text/html; charset=utf-8")
            return
        if parsed.path == "/app.js":
            self._send_file(FRONTEND_DIR / "app.js", "application/javascript")
            return
        if parsed.path == "/styles.css":
            self._send_file(FRONTEND_DIR / "styles.css", "text/css")
            return
        self._set_headers(HTTPStatus.NOT_FOUND, "text/plain")
        self.wfile.write(b"Not Found")

    def do_POST(self) -> None:  # noqa: N802
        if self.path != "/api/run":
            self._set_headers(HTTPStatus.NOT_FOUND, "text/plain")
            self.wfile.write(b"Not Found")
            return
        length = int(self.headers.get("Content-Length", "0"))
        raw = self.rfile.read(length) if length else b"{}"
        try:
            payload = json.loads(raw)
        except json.JSONDecodeError:
            self._send_json(HTTPStatus.BAD_REQUEST, {"error": "invalid_json"})
            return
        ticket = payload.get("ticket", "")
        if not ticket:
            self._send_json(HTTPStatus.BAD_REQUEST, {"error": "ticket required"})
            return
        try:
            result = self.runtime.run(
                ticket,
                correlation_id=payload.get("correlation_id"),
                idempotency_key=payload.get("idempotency_key"),
            )
        except Exception as exc:  # noqa: BLE001
            self._send_json(
                HTTPStatus.INTERNAL_SERVER_ERROR,
                {"error": "runtime_error", "detail": str(exc)},
            )
            return
        self._send_json(HTTPStatus.OK, _serialize_result(result))


def main() -> None:
    port = int(os.getenv("PORT", "8000"))
    server = HTTPServer(("0.0.0.0", port), ApiHandler)
    print(f"Serving UI at http://localhost:{port}")
    server.serve_forever()


if __name__ == "__main__":
    main()
