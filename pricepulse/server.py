from __future__ import annotations

import json
import mimetypes
from http import HTTPStatus
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import parse_qs, urlparse

from pricepulse.db import init_db
from pricepulse.services import (
    build_product_payload,
    bulk_import_products,
    list_custom_products,
    list_products,
    save_admin_product,
    search_payload,
)


BASE_DIR = Path(__file__).resolve().parent.parent
STATIC_DIR = BASE_DIR / "static"
TEMPLATE_PATH = BASE_DIR / "templates" / "index.html"
ADMIN_TEMPLATE_PATH = BASE_DIR / "templates" / "admin.html"


class PricePulseHandler(BaseHTTPRequestHandler):
    server_version = "PricePulse/1.0"

    def do_GET(self) -> None:
        parsed = urlparse(self.path)
        path = parsed.path

        if path == "/":
            self._serve_index()
            return
        if path == "/admin":
            self._serve_admin()
            return
        if path == "/api/search":
            query = parse_qs(parsed.query).get("q", [""])[0]
            self._send_json(search_payload(query))
            return
        if path == "/api/products":
            self._send_json({"products": list_products()})
            return
        if path == "/api/admin/products":
            self._send_json({"products": list_custom_products()})
            return
        if path.startswith("/api/products/") and path.endswith("/offers"):
            product_id = path.split("/")[3]
            payload = build_product_payload(product_id)
            if not payload:
                self._send_json({"error": "Product not found"}, status=HTTPStatus.NOT_FOUND)
                return
            self._send_json({"product_id": product_id, "offers": payload["offers"]})
            return
        if path.startswith("/api/products/"):
            product_id = path.split("/")[3]
            payload = build_product_payload(product_id)
            if not payload:
                self._send_json({"error": "Product not found"}, status=HTTPStatus.NOT_FOUND)
                return
            self._send_json(payload)
            return
        if path.startswith("/static/"):
            self._serve_static(path.removeprefix("/static/"))
            return

        self._send_json({"error": "Not found"}, status=HTTPStatus.NOT_FOUND)

    def do_POST(self) -> None:
        parsed = urlparse(self.path)
        path = parsed.path

        if path == "/api/admin/products":
            try:
                payload = self._read_json_body()
                product = save_admin_product(payload)
                self._send_json({"ok": True, "product": product}, status=HTTPStatus.CREATED)
            except ValueError as error:
                self._send_json({"error": str(error)}, status=HTTPStatus.BAD_REQUEST)
            return

        if path == "/api/admin/import":
            try:
                payload = self._read_json_body()
                if not isinstance(payload, list):
                    raise ValueError("Bulk import expects a JSON array of products")
                products = bulk_import_products(payload)
                self._send_json({"ok": True, "count": len(products)}, status=HTTPStatus.CREATED)
            except ValueError as error:
                self._send_json({"error": str(error)}, status=HTTPStatus.BAD_REQUEST)
            return

        self._send_json({"error": "Not found"}, status=HTTPStatus.NOT_FOUND)

    def log_message(self, fmt: str, *args: object) -> None:
        return

    def _serve_index(self) -> None:
        html = TEMPLATE_PATH.read_text(encoding="utf-8")
        self.send_response(HTTPStatus.OK)
        self.send_header("Content-Type", "text/html; charset=utf-8")
        self.end_headers()
        self.wfile.write(html.encode("utf-8"))

    def _serve_admin(self) -> None:
        html = ADMIN_TEMPLATE_PATH.read_text(encoding="utf-8")
        self.send_response(HTTPStatus.OK)
        self.send_header("Content-Type", "text/html; charset=utf-8")
        self.end_headers()
        self.wfile.write(html.encode("utf-8"))

    def _serve_static(self, relative_path: str) -> None:
        file_path = STATIC_DIR / relative_path
        if not file_path.exists() or not file_path.is_file():
            self.send_error(HTTPStatus.NOT_FOUND)
            return
        content_type = mimetypes.guess_type(file_path.name)[0] or "application/octet-stream"
        self.send_response(HTTPStatus.OK)
        self.send_header("Content-Type", content_type)
        self.end_headers()
        self.wfile.write(file_path.read_bytes())

    def _send_json(self, payload: dict, status: HTTPStatus = HTTPStatus.OK) -> None:
        body = json.dumps(payload).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def _read_json_body(self) -> dict:
        content_length = int(self.headers.get("Content-Length", "0"))
        body = self.rfile.read(content_length).decode("utf-8") if content_length else "{}"
        return json.loads(body)


def run(host: str = "127.0.0.1", port: int = 8000) -> None:
    init_db()
    server = ThreadingHTTPServer((host, port), PricePulseHandler)
    print(f"PricePulse running at http://{host}:{port}")
    server.serve_forever()
