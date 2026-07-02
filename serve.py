#!/usr/bin/env python3
"""One-command launcher for the Chainvet web UI.

Starts `chainvet-server`, serves the static UI, waits until the API is healthy,
and opens your browser. Ctrl-C stops both.

    python3 serve.py --root /path/to/your/contracts

Options:
    --root DIR         contracts directory (CHAINVET_SERVER_ROOT). Default: cwd
    --server-bin PATH  chainvet-server binary. Default: `chainvet-server` on PATH
    --api-port N       API port (default 8080)
    --ui-port N        UI port  (default 5173)
    --no-browser       don't open the browser
"""
import argparse
import http.server
import os
import signal
import subprocess
import sys
import threading
import time
import urllib.request
import webbrowser

HERE = os.path.dirname(os.path.abspath(__file__))
ASSETS = os.path.join(HERE, "assets")


def wait_for_health(port, timeout=25):
    url = f"http://127.0.0.1:{port}/health"
    deadline = time.time() + timeout
    while time.time() < deadline:
        try:
            with urllib.request.urlopen(url, timeout=1) as r:
                if r.status == 200:
                    return True
        except Exception:
            time.sleep(0.3)
    return False


def make_handler(api_base):
    """Serve ASSETS, injecting the API base into index.html so the UI targets the
    right port regardless of where the server listens."""
    inject = f'<script>window.CHAINVET_API_BASE="{api_base}";</script>'.encode()

    class Handler(http.server.SimpleHTTPRequestHandler):
        def __init__(self, *a, **k):
            super().__init__(*a, directory=ASSETS, **k)

        def do_GET(self):
            if self.path.split("?", 1)[0] in ("/", "/index.html"):
                try:
                    html = open(os.path.join(ASSETS, "index.html"), "rb").read()
                except OSError:
                    self.send_error(404)
                    return
                html = html.replace(b"</head>", inject + b"</head>", 1)
                self.send_response(200)
                self.send_header("Content-Type", "text/html; charset=utf-8")
                self.send_header("Content-Length", str(len(html)))
                self.end_headers()
                self.wfile.write(html)
                return
            super().do_GET()

        def log_message(self, *args):
            pass  # keep the console quiet

    return Handler


def main():
    ap = argparse.ArgumentParser(description="Launch the Chainvet web UI + API server.")
    ap.add_argument("--root", default=os.getcwd(),
                    help="contracts directory (CHAINVET_SERVER_ROOT). Default: current dir")
    ap.add_argument("--server-bin", default="chainvet-server",
                    help="chainvet-server binary (default: on PATH)")
    ap.add_argument("--api-port", type=int, default=8080)
    ap.add_argument("--ui-port", type=int, default=5173)
    ap.add_argument("--no-browser", action="store_true")
    args = ap.parse_args()

    # Make SIGTERM run the cleanup (finally) blocks too, so the child server
    # isn't orphaned when the launcher is killed rather than Ctrl-C'd.
    signal.signal(signal.SIGTERM, lambda *_: sys.exit(0))

    root = os.path.abspath(args.root)
    if not os.path.isdir(root):
        sys.exit(f"error: --root is not a directory: {root}")

    env = {
        **os.environ,
        "CHAINVET_SERVER_ROOT": root,
        "CHAINVET_SERVER_ADDR": f"127.0.0.1:{args.api_port}",
    }
    print(f"==> starting chainvet-server on 127.0.0.1:{args.api_port}  (root: {root})")
    try:
        server = subprocess.Popen([args.server_bin], env=env)
    except FileNotFoundError:
        sys.exit(
            f"error: '{args.server_bin}' not found on PATH.\n"
            "       install it (https://install.chainvet.dev, CHAINVET_BINS=chainvet-server)\n"
            "       or pass --server-bin /path/to/chainvet-server"
        )

    try:
        if not wait_for_health(args.api_port):
            sys.exit(f"error: chainvet-server never became healthy on 127.0.0.1:{args.api_port} "
                     "(see its output above).")
        print("==> chainvet-server is up")

        api_base = f"http://127.0.0.1:{args.api_port}"
        try:
            httpd = http.server.ThreadingHTTPServer(("127.0.0.1", args.ui_port), make_handler(api_base))
        except OSError as e:
            sys.exit(f"error: could not serve the UI on 127.0.0.1:{args.ui_port}: {e}\n"
                     "       is the port in use? try --ui-port <other>")

        url = f"http://127.0.0.1:{args.ui_port}"
        print(f"==> Chainvet is ready at {url}   (Ctrl-C to stop)")
        if not args.no_browser:
            threading.Timer(0.6, lambda: webbrowser.open(url)).start()

        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            print("\n==> shutting down")
        finally:
            httpd.server_close()
    finally:
        server.terminate()
        try:
            server.wait(timeout=5)
        except Exception:
            server.kill()


if __name__ == "__main__":
    main()
