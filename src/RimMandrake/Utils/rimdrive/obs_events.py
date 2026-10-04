"""rimdrive.obs_events -- per-call bridge telemetry (observatory S1/S2).

Design: design/RimMandrake/bridge_validation_observatory.md section 3.2-3.3.

CONTRACT (each clause has a red-able test in selftest_obs_events.py):
  * emit() NEVER blocks and NEVER raises: two clock reads, one non-blocking put into a
    bounded queue. A full queue DROPS the event and counts it.
  * A daemon writer thread owns all file I/O. A slow, locked or failing sink fills the
    queue (drops) -- it cannot stall a bridge call. close() joins it for at most
    `join_s` seconds (default 1).
  * call_start is emitted BEFORE the socket write, so a call that never returns leaves
    a call_start with no call_end (the hang class that used to leave no trace).
  * run_end carries emitted/dropped/written counts; a file without it, or with
    dropped > 0, is telemetry-incomplete (obs_summary says so).
  * Read-only for the game: this module never calls the bridge.

Files: <obs dir>/runs/<run_id>.jsonl, outside git (default D:\\Luke\\dev\\_obs).
"""
import itertools
import json
import os
import queue
import threading
import time

SCHEMA = 1
DEFAULT_CAPACITY = 20000


def default_dir():
    env = os.environ.get("OBS_DIR")
    if env:
        return env
    return r"D:\Luke\dev\_obs" if os.name == "nt" else "/mnt/d/Luke/dev/_obs"


def new_run_id(label="run"):
    return "%s-%s-%d" % (time.strftime("%Y%m%dT%H%M%S"), label, os.getpid())


class Sink(object):
    def __init__(self, run_id, directory=None, capacity=DEFAULT_CAPACITY, producer=None,
                 opener=None, start_thread=True):
        self.run_id = run_id
        self.dir = directory or default_dir()
        self.path = os.path.join(self.dir, "runs", "%s.jsonl" % run_id)
        self.producer = producer or ("client:%d" % os.getpid())
        self._q = queue.Queue(maxsize=capacity)
        self._open = opener or (lambda p: open(p, "a", encoding="utf-8"))
        self._seq = itertools.count(1)
        self._req = itertools.count(1)
        self.emitted = 0
        self.dropped = 0
        self.written = 0
        self.write_errors = 0
        self._stop = threading.Event()
        self._closed = False
        self._thread = None
        self.ctx = {}
        if start_thread:
            self._thread = threading.Thread(target=self._writer, name="obs-writer", daemon=True)
            self._thread.start()

    # ---------------------------------------------------------- hot path
    def emit(self, ev, **fields):
        """Non-blocking; returns True when queued, False when dropped. Never raises."""
        try:
            rec = {"v": SCHEMA, "run_id": self.run_id, "producer": self.producer,
                   "seq": next(self._seq), "t": time.time(), "mono": time.monotonic(), "ev": ev}
            rec.update(fields)
            self.emitted += 1
            self._q.put_nowait(rec)
            return True
        except queue.Full:
            self.dropped += 1
            return False
        except Exception:                                         # noqa: BLE001
            self.dropped += 1
            return False

    def call_start(self, tool):
        """-> token for call_end. Never raises."""
        try:
            req = "r%d" % next(self._req)
            mono = time.monotonic()
            self.emit("call_start", req=req, attempt=1, tool=tool, ctx=dict(self.ctx) or None)
            return (req, tool, time.time(), mono)
        except Exception:                                         # noqa: BLE001
            return None

    def call_end(self, token, outcome, reply_success=None, timeout=False):
        if token is None:
            return
        try:
            req, tool, t_start, mono0 = token
            ms = round((time.monotonic() - mono0) * 1000.0, 2)
            self.emit("call_end", req=req, attempt=1, tool=tool, t_start=t_start, t_end=time.time(),
                      outcome=outcome, latency_ms=ms, timeout=bool(timeout),
                      reply_success=reply_success, transport="ok" if outcome in ("ok", "reply_fail") else outcome)
        except Exception:                                         # noqa: BLE001
            pass

    # ------------------------------------------------------------ writer
    def _writer(self):
        f = None
        try:
            try:
                os.makedirs(os.path.dirname(self.path), exist_ok=True)
                f = self._open(self.path)
            except Exception:                                     # noqa: BLE001
                self.write_errors += 1
            while True:
                try:
                    rec = self._q.get(timeout=0.2)
                except queue.Empty:
                    if self._stop.is_set():
                        break
                    continue
                self._write(f, rec)
                if self._stop.is_set() and self._q.empty():
                    break
            self._write(f, {"v": SCHEMA, "run_id": self.run_id, "producer": self.producer,
                            "seq": next(self._seq), "t": time.time(), "mono": time.monotonic(),
                            "ev": "run_end", "emitted": self.emitted, "dropped": self.dropped,
                            "written": self.written, "write_errors": self.write_errors}, final=True)
        finally:
            try:
                if f:
                    f.close()
            except Exception:                                     # noqa: BLE001
                pass

    def _write(self, f, rec, final=False):
        if f is None:
            self.write_errors += 1
            return
        try:
            f.write(json.dumps(rec, default=str) + "\n")
            f.flush()
            if not final:
                self.written += 1
        except Exception:                                         # noqa: BLE001
            self.write_errors += 1

    def close(self, join_s=1.0):
        """Bounded: returns after at most join_s even when the sink is stalled."""
        if self._closed:
            return
        self._closed = True
        self._stop.set()
        if self._thread is not None:
            self._thread.join(join_s)


_CURRENT = []


def install(run_id, directory=None, **kw):
    uninstall()
    sink = Sink(run_id, directory, **kw)
    _CURRENT.append(sink)
    return sink


def uninstall(join_s=1.0):
    while _CURRENT:
        _CURRENT.pop().close(join_s)


def current():
    return _CURRENT[-1] if _CURRENT else None


def call_start(tool):
    s = current()
    return (s, s.call_start(tool)) if s else None


def call_end(handle, outcome, reply_success=None, timeout=False):
    if handle:
        handle[0].call_end(handle[1], outcome, reply_success, timeout)


def end_exception(handle, e):
    outcome, timeout = classify_exception(e)
    call_end(handle, outcome, False, timeout)


def classify_result(r):
    """-> (outcome, reply_success) for a returned reply."""
    if isinstance(r, dict) and r.get("success") is False:
        return "reply_fail", False
    return "ok", (r.get("success") if isinstance(r, dict) else None)


def classify_exception(e):
    if isinstance(e, TimeoutError) or "timed out" in str(e).lower():
        return "timeout", True
    if isinstance(e, (ConnectionError, OSError)):
        return "reconnected", False
    return "error", False
