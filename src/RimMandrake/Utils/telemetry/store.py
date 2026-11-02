"""The two stores: SQLite events DB (rows) and VictoriaMetrics (numeric series).

telemetryd is the ONLY writer of both (design §5 reason 5). Both are caches over the raw JSONL:
`telemetry rebuild` re-ingests, and every insert is idempotent on `src_ref`.

VictoriaMetrics is written through /api/v1/import (JSON lines). When VM is unreachable the
batch is spooled to <state>/vm_spool/*.jsonl and replayed later, so a VM restart loses nothing.
"""
from __future__ import annotations

import json
import math
import os
import shutil
import sqlite3
import subprocess
import itertools
import time
import urllib.error
import urllib.parse
import urllib.request

from tcommon import IS_WIN, cfg

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
CREATE TABLE IF NOT EXISTS exc_seen(src_ref TEXT PRIMARY KEY, ts REAL);
CREATE TABLE IF NOT EXISTS mapcomp(
  ts REAL, session TEXT, type TEXT, mod TEXT, ms_per_tick REAL, calls INTEGER, max_ms REAL,
  ticks INTEGER, src_ref TEXT UNIQUE);
-- cursors.done = bytes of this file already copied to raw/ (a rebuild re-reads from 0, never re-copies)
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
        if os.path.dirname(path):
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
        self.dropped_ts = 0      # points refused for a time that is not a finite epoch
        self.dropped = 0         # points lost because neither VM nor the spool would take them
        self._seq = itertools.count()

    MAX_PENDING = 500_000        # points held in memory while VM and the spool both refuse

    def add(self, name: str, labels: dict | None, value, ts: float) -> None:
        if value is None:
            return
        try:
            v = float(value)
        except (TypeError, ValueError, OverflowError):
            return
        if not math.isfinite(v):  # NaN: absent; +-inf serialises as bare Infinity, which VM drops from the batch
            return
        try:        # a time that is not a finite epoch would raise in _lines and cost the whole queued batch
            ts = float(ts)
        except (TypeError, ValueError, OverflowError):
            self.dropped_ts += 1
            return
        # and a day ahead is past what VM will keep (it refuses the future beyond its limit): never "sent"
        if not (math.isfinite(ts) and 0 < ts < 1e11 and ts <= time.time() + 86400):
            self.dropped_ts += 1
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
        # urllib only: the one writer, telemetryd, runs on Windows beside VM (no WSL NAT on this path)
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
            try:
                spooled = self._spool(body)
            except OSError as e2:   # disk full / unwritable: keep the batch queued for the next flush
                spooled = False
                self.last_error += f"; spool: {type(e2).__name__}: {e2}"
            if spooled:
                self.spooled += len(pts)
            else:
                keep = (pts + self.points)[-self.MAX_PENDING:]
                self.dropped += len(pts) + len(self.points) - len(keep)
                self.points = keep
        return len(pts)

    def _spool(self, body: bytes) -> bool:
        """True when the batch is on disk; False when the 2 GB cap refuses it (raises OSError if it cannot write)."""
        os.makedirs(self.spool_dir, exist_ok=True)
        # cap the spool at 2 GB: a VM down for weeks must not fill E:; raw JSONL can rebuild it
        total = sum(os.path.getsize(os.path.join(self.spool_dir, f)) for f in os.listdir(self.spool_dir))
        if total + len(body) > 2 << 30:
            return False
        # unique per process and call ("x" never overwrites), and sorts oldest first for replay
        p = os.path.join(self.spool_dir, f"spool_{time.time_ns():020d}_{os.getpid()}_{next(self._seq):06d}.jsonl")
        with open(p, "xb") as f:
            f.write(body)
        return True

    def _replay_spool(self) -> None:
        if not os.path.isdir(self.spool_dir):
            return
        replayed = 0
        for fn in sorted(os.listdir(self.spool_dir))[:20]:
            p = os.path.join(self.spool_dir, fn)
            try:
                with open(p, "rb") as f:
                    self._post(f.read())
                os.remove(p)
                replayed += 1
            except Exception as e:  # noqa: BLE001 — still down; try next cycle
                self.last_error = f"spool replay: {type(e).__name__}: {e}"
                return
        if replayed:    # VM took every replayed batch: any earlier transport error is over
            self.last_error = None


def _get(url: str, timeout: float) -> bytes:
    """GET url. WSL cannot reach the Windows-side VM on 127.0.0.1 (NAT), so from WSL a refused or unreachable local
    address is retried once through Windows' own curl.exe, which can; any other failure is raised as is."""
    try:
        with urllib.request.urlopen(url, timeout=timeout) as r:
            return r.read()
    except urllib.error.HTTPError:
        raise
    except (urllib.error.URLError, OSError) as e:
        host = urllib.parse.urlsplit(url).hostname
        if IS_WIN or host not in ("127.0.0.1", "localhost") or not shutil.which("curl.exe"):
            raise
        try:
            r = subprocess.run(["curl.exe", "-sS", "-f", "-m", str(int(timeout) + 1), url],
                               capture_output=True, timeout=timeout + 15)
        except (OSError, subprocess.SubprocessError) as e2:
            raise OSError(f"{e}; via curl.exe: {e2}") from e2
        if r.returncode:
            raise OSError(f"{e}; via curl.exe: exit {r.returncode} {r.stderr.decode(errors='replace')[-300:]}")
        return r.stdout


def vm_query(expr: str, start: float | None = None, end: float | None = None, step: str | None = None,
             url: str | None = None) -> dict:
    base = (url or cfg()["vm_url"]).rstrip("/")
    q = {"query": expr}
    if start is not None:
        q.update({"start": f"{start:.3f}", "end": f"{(end or time.time()):.3f}", "step": step or "15s"})
        path = "/api/v1/query_range"
    else:
        if end is not None:
            q["time"] = f"{end:.3f}"
        path = "/api/v1/query"
    return json.loads(_get(base + path + "?" + urllib.parse.urlencode(q), 15))


def vm_get(path: str, url: str | None = None, timeout: float = 5) -> bytes:
    base = (url or cfg()["vm_url"]).rstrip("/")
    return _get(base + path, timeout)


def vm_export(selectors: list[str], start: float, end: float, url: str | None = None, timeout: float = 60,
              get=None) -> list[tuple[dict, list[float], list[float]]]:
    """Raw samples of every series matching any selector in [start, end]: [(labels, timestamps_s, values)], each
    series oldest first. Raises when VM cannot be asked (an unreachable store is UNMEASURED, never empty)."""
    q = [("match[]", s) for s in selectors] + [("start", f"{start:.3f}"), ("end", f"{end:.3f}")]
    body = (get or vm_get)("/api/v1/export?" + urllib.parse.urlencode(q), url, timeout)
    out = []
    for line in body.splitlines():
        if not line.strip():
            continue
        d = json.loads(line)
        pairs = [(ts / 1000.0, float(v)) for ts, v in zip(d.get("timestamps") or [], d.get("values") or [])
                 if start * 1000 <= ts <= end * 1000 and v is not None]
        pairs = sorted((p for p in pairs if math.isfinite(p[1])), key=lambda p: p[0])   # VM exports +-Inf/NaN
        #   as strings: never a window; sorted on time alone, so a mixed-type value never meets a comparison
        out.append((d.get("metric") or {}, [p[0] for p in pairs], [p[1] for p in pairs]))
    return out
