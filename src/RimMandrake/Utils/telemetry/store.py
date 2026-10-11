"""The two stores: SQLite events DB (rows) and VictoriaMetrics (numeric series).

telemetryd is the ONLY writer of both (design §5 reason 5). Both are caches over the raw JSONL:
`telemetry rebuild` re-ingests, and every insert is idempotent on `src_ref`.

VictoriaMetrics is written through /api/v1/import (JSON lines). When VM is unreachable the
batch is spooled to <state>/vm_spool/*.jsonl and replayed later, so a VM restart loses nothing.
"""
from __future__ import annotations

import json
import os
import sqlite3
import time
import urllib.request

from tcommon import cfg

SCHEMA = """
PRAGMA journal_mode=WAL;
CREATE TABLE IF NOT EXISTS events(
  id INTEGER PRIMARY KEY, ts REAL NOT NULL, ts_end REAL, kind TEXT NOT NULL, subject TEXT,
  seat TEXT, sha TEXT, detail TEXT, src TEXT, src_ref TEXT UNIQUE);
CREATE INDEX IF NOT EXISTS ev_ts ON events(ts);
CREATE INDEX IF NOT EXISTS ev_kind_ts ON events(kind, ts);
CREATE TABLE IF NOT EXISTS bridge_calls(
  cid TEXT PRIMARY KEY, ts REAL, ts_end REAL, tool TEXT, ms REAL, status TEXT, success INTEGER,
  mutating INTEGER, script TEXT, seat TEXT, run TEXT, client TEXT);
CREATE INDEX IF NOT EXISTS bc_ts ON bridge_calls(ts);
CREATE TABLE IF NOT EXISTS proof_runs(
  id TEXT PRIMARY KEY, ts REAL, path TEXT, mod TEXT, script TEXT, wall_s REAL, mod_hash TEXT,
  n_pass INTEGER, n_fail INTEGER, n_other INTEGER, n_total INTEGER, all_green INTEGER, detail TEXT);
CREATE TABLE IF NOT EXISTS proof_rows(
  run_id TEXT, row_id TEXT, status TEXT, class TEXT, detail TEXT, PRIMARY KEY(run_id, row_id));
CREATE TABLE IF NOT EXISTS flight(
  id TEXT PRIMARY KEY, ts REAL, session TEXT, file TEXT, trigger TEXT, tick_from INTEGER,
  tick_to INTEGER, worst_us INTEGER, detail TEXT);
CREATE TABLE IF NOT EXISTS exc_sigs(
  session TEXT, sig TEXT, first_ts REAL, last_ts REAL, n INTEGER, sup INTEGER, sample TEXT,
  PRIMARY KEY(session, sig));
CREATE TABLE IF NOT EXISTS mapcomp(
  ts REAL, session TEXT, type TEXT, mod TEXT, ms_per_tick REAL, calls INTEGER, max_ms REAL,
  ticks INTEGER, src_ref TEXT UNIQUE);
CREATE TABLE IF NOT EXISTS cursors(
  src TEXT, key TEXT, ino TEXT, offset INTEGER, size INTEGER, mtime REAL, done INTEGER DEFAULT 0,
  PRIMARY KEY(src, key));
CREATE TABLE IF NOT EXISTS kv(k TEXT PRIMARY KEY, v TEXT);
"""


def connect(path: str | None = None, readonly: bool = False) -> sqlite3.Connection:
    path = path or cfg()["db"]
    if readonly:
        con = sqlite3.connect(f"file:{path}?mode=ro", uri=True, timeout=10)
    else:
        os.makedirs(os.path.dirname(path), exist_ok=True)
        con = sqlite3.connect(path, timeout=30)
        con.executescript(SCHEMA)
        con.execute("PRAGMA synchronous=NORMAL")
    con.row_factory = sqlite3.Row
    return con


def add_event(con, ts, kind, subject=None, detail=None, src=None, src_ref=None, ts_end=None,
              seat=None, sha=None) -> bool:
    cur = con.execute(
        "INSERT OR IGNORE INTO events(ts,ts_end,kind,subject,seat,sha,detail,src,src_ref) VALUES(?,?,?,?,?,?,?,?,?)",
        (ts, ts_end, kind, subject, seat, sha,
         json.dumps(detail, separators=(",", ":"), default=str) if detail is not None else None, src, src_ref))
    return cur.rowcount > 0


def kv_get(con, k, default=None):
    r = con.execute("SELECT v FROM kv WHERE k=?", (k,)).fetchone()
    return json.loads(r[0]) if r else default


def kv_set(con, k, v):
    con.execute("INSERT OR REPLACE INTO kv(k,v) VALUES(?,?)", (k, json.dumps(v, default=str)))


# ------------------------------------------------------------------ VictoriaMetrics

class VMSink:
    """Collects points; flush() POSTs them as /api/v1/import JSON lines, spooling on failure."""

    def __init__(self, url: str | None = None, spool_dir: str | None = None, post=None):
        self.url = (url or cfg()["vm_url"]).rstrip("/")
        self.spool_dir = spool_dir or os.path.join(cfg()["state"], "vm_spool")
        self.points: list[tuple[str, dict, float, float]] = []
        self._post = post or self._http_post
        self.sent = 0
        self.spooled = 0
        self.last_error: str | None = None

    def add(self, name: str, labels: dict | None, value, ts: float) -> None:
        if value is None:
            return
        try:
            v = float(value)
        except (TypeError, ValueError):
            return
        if v != v:  # NaN: absent, never a point
            return
        self.points.append((name, labels or {}, v, ts))

    def _lines(self, pts) -> bytes:
        out = []
        for name, labels, v, ts in pts:
            m = {"__name__": name}
            m.update({k: str(x) for k, x in labels.items() if x is not None and x != ""})
            out.append(json.dumps({"metric": m, "values": [v], "timestamps": [int(ts * 1000)]},
                                  separators=(",", ":")))
        return ("\n".join(out) + "\n").encode()

    def _http_post(self, body: bytes) -> None:
        req = urllib.request.Request(self.url + "/api/v1/import", data=body, method="POST",
                                     headers={"Content-Type": "application/json"})
        with urllib.request.urlopen(req, timeout=10) as r:
            r.read()

    def flush(self) -> int:
        pts, self.points = self.points, []
        if not pts:
            self._replay_spool()
            return 0
        body = self._lines(pts)
        try:
            self._post(body)
            self.sent += len(pts)
            self.last_error = None
            self._replay_spool()
        except Exception as e:  # noqa: BLE001 — any transport failure spools
            self.last_error = f"{type(e).__name__}: {e}"
            self._spool(body)
            self.spooled += len(pts)
        return len(pts)

    def _spool(self, body: bytes) -> None:
        os.makedirs(self.spool_dir, exist_ok=True)
        # cap the spool at 2 GB: a VM down for weeks must not fill E:; raw JSONL can rebuild it
        total = sum(os.path.getsize(os.path.join(self.spool_dir, f)) for f in os.listdir(self.spool_dir))
        if total > 2 << 30:
            return
        p = os.path.join(self.spool_dir, f"spool_{time.time():.3f}_{os.getpid()}.jsonl")
        with open(p, "wb") as f:
            f.write(body)

    def _replay_spool(self) -> None:
        if not os.path.isdir(self.spool_dir):
            return
        for fn in sorted(os.listdir(self.spool_dir))[:20]:
            p = os.path.join(self.spool_dir, fn)
            try:
                with open(p, "rb") as f:
                    self._post(f.read())
                os.remove(p)
            except Exception:  # noqa: BLE001 — still down; try next cycle
                return


def vm_query(expr: str, start: float | None = None, end: float | None = None, step: str | None = None,
             url: str | None = None) -> dict:
    import urllib.parse
    base = (url or cfg()["vm_url"]).rstrip("/")
    q = {"query": expr}
    if start is not None:
        q.update({"start": f"{start:.3f}", "end": f"{(end or time.time()):.3f}", "step": step or "15s"})
        path = "/api/v1/query_range"
    else:
        path = "/api/v1/query"
    with urllib.request.urlopen(base + path + "?" + urllib.parse.urlencode(q), timeout=15) as r:
        return json.loads(r.read())


def vm_get(path: str, url: str | None = None, timeout: float = 5) -> bytes:
    base = (url or cfg()["vm_url"]).rstrip("/")
    with urllib.request.urlopen(base + path, timeout=timeout) as r:
        return r.read()
