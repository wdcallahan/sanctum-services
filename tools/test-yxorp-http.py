#!/usr/bin/env python3
"""Loopback-only HTTP test of the real Services Nginx template.

The upstreams are synthetic local Python HTTP servers. No Sanctum hosts,
DNS, credentials, proxy instances or production services are contacted.
"""
from __future__ import annotations

from http.client import HTTPConnection, RemoteDisconnected
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
import json
from pathlib import Path
import shutil
import socket
import subprocess
import tempfile
import threading
import time

from jinja2 import Environment, FileSystemLoader, StrictUndefined


class SyntheticBackend(BaseHTTPRequestHandler):
    server_version = "SyntheticUpstream/1"

    def do_GET(self):
        if self.path in ("/redirect", "/relative-redirect"):
            self.send_response(302)
            self.send_header(
                "Location",
                "/dashboard?test=1#section"
                if self.path == "/relative-redirect"
                else f"http://127.0.0.1:{self.server.server_port}/dashboard?test=1#section"
            )
            self.send_header("Content-Length", "0")
            self.end_headers()
            return
        if self.headers.get("Upgrade", "").lower() == "websocket":
            self.send_response(101)
            self.send_header("Upgrade", "websocket")
            self.send_header("Connection", "Upgrade")
            self.end_headers()
            return
        payload = json.dumps({
            "identity": self.server.identity,
            "host": self.headers.get("Host"),
            "forwarded_proto": self.headers.get("X-Forwarded-Proto"),
            "forwarded_scheme": self.headers.get("X-Forwarded-Scheme"),
            "forwarded_for": self.headers.get("X-Forwarded-For"),
        }).encode("utf-8")
        self.send_response(200)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(payload)))
        self.end_headers()
        self.wfile.write(payload)

    def log_message(self, fmt, *args):
        return


def new_backend(name):
    server = ThreadingHTTPServer(("127.0.0.1", 0), SyntheticBackend)
    server.identity = name
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    return server, thread


def free_port():
    with socket.socket() as sock:
        sock.bind(("127.0.0.1", 0))
        return sock.getsockname()[1]


def request(port, hostname, upgrade=False):
    connection = HTTPConnection("127.0.0.1", port, timeout=2)
    headers = {"Host": hostname}
    if upgrade:
        headers.update({"Connection": "Upgrade", "Upgrade": "websocket"})
    try:
        connection.request("GET", "/", headers=headers)
        response = connection.getresponse()
        return response.status, response.read()
    finally:
        connection.close()


def redirect_request(port, hostname, path="/redirect"):
    """Retrieve the original Location header from actual synthetic Nginx."""
    connection = HTTPConnection("127.0.0.1", port, timeout=2)
    try:
        connection.request("GET", path, headers={"Host": hostname})
        response = connection.getresponse()
        status, location = response.status, response.getheader("Location")
        response.read()
        return status, location
    finally:
        connection.close()


def wait_for_ready(port):
    end = time.monotonic() + 8
    while time.monotonic() < end:
        try:
            connection = HTTPConnection("127.0.0.1", port, timeout=1)
            connection.request("GET", "/__yxorp_health")
            response = connection.getresponse()
            result = (response.status, response.read())
            connection.close()
            if result[0] == 200 and b"yxorp-ready" in result[1]:
                return
        except (OSError, RemoteDisconnected):
            pass
        time.sleep(.08)
    raise AssertionError("isolated Nginx did not become healthy")


def render(template_path, output, pid_file, port, routes):
    source = Path(template_path)
    template = Environment(
        loader=FileSystemLoader(str(source.parent)),
        undefined=StrictUndefined,
    ).get_template(source.name)
    config = template.render(yxorp_routes=routes)
    if "listen 80 default_server;" not in config or "listen 80;" not in config:
        raise AssertionError("Nginx template listener pattern changed")
    if "pid /tmp/nginx.pid;" not in config:
        raise AssertionError("Nginx pid pattern changed")
    config = config.replace("listen 80 default_server;",
                            f"listen 127.0.0.1:{port} default_server;")
    config = config.replace("listen 80;", f"listen 127.0.0.1:{port};")
    config = config.replace("pid /tmp/nginx.pid;", f"pid {pid_file};")
    output.write_text(config, encoding="utf-8")
    subprocess.run(["nginx", "-t", "-c", str(output)],
                   check=True, capture_output=True, timeout=6)


def main(template_path):
    if shutil.which("nginx") is None:
        raise SystemExit("Nginx binary unavailable: this must run in CI")
    one, thread_one = new_backend("backend_one")
    two, thread_two = new_backend("backend_two")
    process = None
    try:
        with tempfile.TemporaryDirectory(prefix="yxorp-http-smoke-") as root:
            root = Path(root)
            cfg = root / "nginx.conf"
            pid = root / "nginx.pid"
            listen = free_port()
            routes = [
                dict(hostname="example.nexus.sanctum", upstream_scheme="http",
                     upstream_host="127.0.0.1", upstream_port=one.server_port,
                     enabled=True, websocket=False),
                dict(hostname="socket.nexus.sanctum", upstream_scheme="http",
                     upstream_host="127.0.0.1", upstream_port=one.server_port,
                     enabled=True, websocket=True),
                dict(hostname="disabled.nexus.sanctum", upstream_scheme="http",
                     upstream_host="127.0.0.1", upstream_port=one.server_port,
                     enabled=False, websocket=False),
                # Existing NPM host 11 must be distinct from the newly
                # requested Yarn nexus host; each name has its OWN upstream.
                dict(hostname="yarn.inner.sanctum", upstream_scheme="http",
                     upstream_host="127.0.0.1", upstream_port=two.server_port,
                     enabled=True, websocket=False),
                dict(hostname="yarn.nexus.sanctum", upstream_scheme="http",
                     upstream_host="127.0.0.1", upstream_port=one.server_port,
                     enabled=True, websocket=False),
            ]
            render(template_path, cfg, pid, listen, routes)
            process = subprocess.Popen(
                ["nginx", "-c", str(cfg), "-g", "daemon off;"],
                stdout=subprocess.DEVNULL, stderr=subprocess.PIPE,
            )
            wait_for_ready(listen)
            status, payload = request(listen, "example.nexus.sanctum")
            response = json.loads(payload)
            assert status == 200 and response["identity"] == "backend_one", response
            assert response["host"] == "example.nexus.sanctum", response
            assert response["forwarded_proto"] == "http", response
            assert response["forwarded_scheme"] == "http", response
            assert response["forwarded_for"], response
            status, _ = request(listen, "socket.nexus.sanctum", upgrade=True)
            assert status == 101, status
            # Exercise the actual Nginx template with different upstream
            # identities: using the wrong virtual host MUST be detectable.
            status, old_bytes = request(listen, "yarn.inner.sanctum")
            old = json.loads(old_bytes)
            assert status == 200 and old["identity"] == "backend_two", old
            assert old["host"] == "yarn.inner.sanctum", old
            status, new_bytes = request(listen, "yarn.nexus.sanctum")
            new = json.loads(new_bytes)
            assert status == 200 and new["identity"] == "backend_one", new
            assert new["host"] == "yarn.nexus.sanctum", new
            assert old_bytes != new_bytes
            status, location = redirect_request(listen, "yarn.inner.sanctum",
                                                "/relative-redirect")
            assert status == 302 and location == "/dashboard?test=1#section"
            # Actual Kuma GET / returned the SAME relative Location
            # through direct, incumbent, and candidate. Nginx passes such
            # a relative header through without rewriting the authority.
            for host in ("example.nexus.sanctum", "socket.nexus.sanctum"):
                status, location = redirect_request(
                    listen, host, "/relative-redirect")
                assert status == 302, status
                assert location == "/dashboard?test=1#section", location
            # Absolute upstream URLs remain on default proxy_redirect
            # behavior; no Kuma-only rewrite is installed.
            status, location = redirect_request(listen, "example.nexus.sanctum")
            assert status == 302, status
            assert location != "/dashboard?test=1#section", location
            for unknown in ("unknown.nexus.sanctum", "disabled.nexus.sanctum"):
                try:
                    status, _ = request(listen, unknown)
                except (RemoteDisconnected, ConnectionResetError, BrokenPipeError):
                    pass
                else:
                    raise AssertionError(
                        f"host {unknown} unexpectedly returned HTTP {status}"
                    )

            # Exercise a deliberate change in a disposable local Nginx master.
            routes[0]["upstream_port"] = two.server_port
            render(template_path, cfg, pid, listen, routes)
            subprocess.run(["nginx", "-s", "reload", "-c", str(cfg)],
                           check=True, capture_output=True, timeout=6)
            end = time.monotonic() + 4
            while True:
                status, payload = request(listen, "example.nexus.sanctum")
                if status == 200 and json.loads(payload)["identity"] == "backend_two":
                    break
                if time.monotonic() >= end:
                    raise AssertionError("route modification failed")
                time.sleep(.08)

            # Explicitly selected removal must stop routing the old name.
            routes[0]["enabled"] = False
            render(template_path, cfg, pid, listen, routes)
            subprocess.run(["nginx", "-s", "reload", "-c", str(cfg)],
                           check=True, capture_output=True, timeout=6)
            end = time.monotonic() + 4
            while True:
                try:
                    result = request(listen, "example.nexus.sanctum")
                except (RemoteDisconnected, ConnectionResetError, BrokenPipeError):
                    break
                if time.monotonic() >= end:
                    raise AssertionError(f"removed host still routes: {result}")
                time.sleep(.08)
            print("PASS: distinct existing/new Yarn vhosts and upstreams, "
                  "Host forwarding, WebSocket 101, raw relative Location, "
                  "default-deny, route change and removal (real loopback Nginx)")
    finally:
        if process is not None:
            process.terminate()
            try:
                process.communicate(timeout=4)
            except subprocess.TimeoutExpired:
                process.kill()
                process.communicate(timeout=2)
        for server, thread in ((one, thread_one), (two, thread_two)):
            server.shutdown()
            server.server_close()
            thread.join(timeout=2)


if __name__ == "__main__":
    import sys
    if len(sys.argv) != 2:
        raise SystemExit("Usage: test-yxorp-http.py <nginx.conf.j2>")
    main(sys.argv[1])
