"""Serve the SteveDesktop bootstrap over the LAN from Archmagi, and receive its reports.

Runs under WINDOWS python.exe (WSL2 is behind NAT and is not reachable from the LAN).
Launch it with serve_bootstrap.sh from WSL, which stages the files first.

    GET  /b                -> bootstrap.ps1 (so the typed line stays short)
    GET  /<staged file>    -> bootstrap.ps1, bootstrap_wsl.sh, archmagi.pub
    POST /report           -> body saved as reports/<utc>_<reason>.json and reports/latest.json

Only the staged files are served (no directory listing, no path traversal). It exits by itself
after --minutes (default 240) so it never lingers. Stdlib only.
"""
import argparse
import datetime
import json
import os
import sys
import threading
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

FILES = ("bootstrap.ps1", "bootstrap_wsl.sh", "archmagi.pub")
ALIASES = {"/b": "bootstrap.ps1"}
MAX_REPORT = 512 * 1024


def make_handler(serve_dir, reports_dir, log_path):
    def log(msg):
        line = "%s %s\n" % (datetime.datetime.now().isoformat(timespec="seconds"), msg)
        with open(log_path, "a", encoding="utf-8") as fh:
            fh.write(line)
        sys.stdout.write(line)
        sys.stdout.flush()

    class Handler(BaseHTTPRequestHandler):
        def log_message(self, fmt, *args):  # route http.server's own log through ours
            log("%s %s" % (self.client_address[0], fmt % args))

        def do_GET(self):
            path = self.path.split("?", 1)[0]
            name = ALIASES.get(path, path.lstrip("/"))
            if name not in FILES:
                self.send_error(404)
                return
            with open(os.path.join(serve_dir, name), "rb") as fh:
                data = fh.read()
            self.send_response(200)
            self.send_header("Content-Type", "text/plain; charset=utf-8")
            self.send_header("Content-Length", str(len(data)))
            self.send_header("Cache-Control", "no-store")
            self.end_headers()
            self.wfile.write(data)

        def do_POST(self):
            if self.path != "/report":
                self.send_error(404)
                return
            n = int(self.headers.get("Content-Length") or 0)
            if n <= 0 or n > MAX_REPORT:
                self.send_error(413)
                return
            body = self.rfile.read(n)
            try:
                doc = json.loads(body.decode("utf-8-sig"))
            except ValueError:
                self.send_error(400, "not json")
                return
            reason = str(doc.get("facts", {}).get("report_reason", "report"))
            reason = "".join(c for c in reason if c.isalnum() or c == "_")[:40] or "report"
            stamp = datetime.datetime.now(datetime.timezone.utc).strftime("%Y%m%dT%H%M%SZ")
            doc["_received"] = {"utc": stamp, "from": self.client_address[0]}
            text = json.dumps(doc, indent=2, sort_keys=True)
            for fname in ("%s_%s.json" % (stamp, reason), "latest.json"):
                tmp = os.path.join(reports_dir, fname + ".tmp")
                with open(tmp, "w", encoding="utf-8") as fh:
                    fh.write(text)
                os.replace(tmp, os.path.join(reports_dir, fname))
            facts = doc.get("facts", {})
            log("REPORT %s from %s: ip=%s mac=%s user=%s edition=%s phase=%s" % (
                reason, self.client_address[0], facts.get("lan_ip"), facts.get("mac"),
                facts.get("user"), facts.get("edition_id"), doc.get("phase")))
            self.send_response(204)
            self.end_headers()

    return Handler


def main():
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--dir", required=True, help="staged folder (Windows path)")
    ap.add_argument("--port", type=int, default=8765)
    ap.add_argument("--bind", default="0.0.0.0")
    ap.add_argument("--minutes", type=float, default=240)
    a = ap.parse_args()
    missing = [f for f in FILES if not os.path.isfile(os.path.join(a.dir, f))]
    if missing:
        sys.exit("not staged: %s" % ", ".join(missing))
    reports = os.path.join(a.dir, "reports")
    os.makedirs(reports, exist_ok=True)
    log_path = os.path.join(a.dir, "serve.log")
    srv = ThreadingHTTPServer((a.bind, a.port), make_handler(a.dir, reports, log_path))
    timer = threading.Timer(a.minutes * 60, srv.shutdown)
    timer.daemon = True
    timer.start()
    with open(log_path, "a", encoding="utf-8") as fh:
        fh.write("%s serving %s on %s:%d for %.0f min (pid %d)\n" % (
            datetime.datetime.now().isoformat(timespec="seconds"), a.dir, a.bind, a.port, a.minutes, os.getpid()))
    with open(os.path.join(a.dir, "serve.pid"), "w") as fh:
        fh.write(str(os.getpid()))
    srv.serve_forever()


if __name__ == "__main__":
    main()
