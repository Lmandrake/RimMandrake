#!/usr/bin/env python3
"""ClockGate -- the single owner of "how much game time has been spent".

Design: design/RimMandrake/northstar_helpers_plan.md section 5, as revised by
section 10 items 2 (one clock gate, overhead ledger, epochs), 3 (dedup only,
not built here) and 8 (watchdog is a separate supervisor).

Pure and bridge-agnostic. A "session" is any object with
`call(tool, **params) -> dict`. Stdlib only; no signal.alarm, no fcntl, so it
runs under Windows python.exe as well as WSL python3.

Rules this module enforces
- ONE `last_seen_tick` and an `epoch` counter. `observe(tick)` re-bases and
  charges the delta since the last seen tick, so ticks that passed BETWEEN
  calls are charged. The first observation only sets the base.
- A negative delta, or an observation flagged `epoch_change=True`, starts a
  NEW epoch: new base, nothing charged, epoch + 1, recorded in the ledger.
  Time is never freed silently and never charged negative.
- Two ledgers under ONE hard `session_cap`: `component` (frames stacked as
  suite/chain/component, each with its own cap, every open frame is charged)
  and `overhead` (helper / evidence-refresh ticks, via `with gate.overhead()`).
  Overhead is charged to the session total but to no frame.
- `step()` charges the MEASURED ticksGame delta, never the requested n, and
  refuses (BudgetExceeded) BEFORE moving the clock when the request exceeds
  `remaining()`.
- Tick-moving verbs run inside `gate.lease(reason)`; `assert_leased()` lets the
  suite refuse a raw step/unpause that bypassed the gate.

Supervisor honesty: it is a sibling thread. It CANNOT interrupt a blocked
bridge call in the worker; it can only act beside it (open its own connection
and request pause, optionally kill the worker process). A worker stuck inside
a call stays stuck until the supervisor's action unblocks it.
"""
import contextlib
import json
import threading
import time


# --------------------------------------------------------------- exceptions
class BudgetExceeded(Exception):
    def __init__(self, scope, spent, cap, detail=""):
        self.scope, self.spent, self.cap = scope, spent, cap
        msg = "tick budget exceeded in scope %r: spent %s of cap %s" % (
            scope, spent, cap)
        super().__init__(msg + (" (%s)" % detail if detail else ""))


class ClockLost(Exception):
    """No authoritative clock reading is available."""


class ClockStall(Exception):
    """step_game_ticks reported success K times in a row but moved nothing."""


class UnleasedTickMove(Exception):
    """A tick-moving verb ran outside gate.lease()."""


class PauseUnverified(Exception):
    """The game could not be proven paused."""


class GovernorStop(Exception):
    """jawa/safe_advance did not finish the chunk: the vitals latch STOPPED it (a death, a downed actor, a new hostile,
    a stuck modal, an undeclared clock jump...), it was refused (over budget on a populated map) or aborted.
    Duck-types as a watch.SurpriseAbort (`is_surprise_abort`, `kind`, `summary()`), so a suite component records
    UNMEASURED -- a disturbance, never a verdict about the mod (owner, 2026-10-13: damage restarts the row)."""
    is_surprise_abort = True
    kind = "surprise"

    def __init__(self, result):
        self.result = result if isinstance(result, dict) else {"raw": result}
        r = self.result
        sb = r.get("stopBy") or {}
        why = sb.get("detail") or r.get("refused") or r.get("abortWhy") or r.get("message") or r.get("error") or ""
        Exception.__init__(self, "safe_advance %s after %s of %s tick(s): %s%s" % (
            r.get("state"), r.get("executed"), r.get("requested"),
            ("%s: " % sb.get("kind")) if sb.get("kind") else "", why))
        self.hits, self.captures = [], []
        _record_stop(self)

    def summary(self):
        return {"kind": self.kind, "message": str(self), "hits": [], "evidence": [], "screenshots": [],
                "stopBy": self.result.get("stopBy"), "triggers": (self.result.get("triggers") or [])[:10]}


def _stop_log_path():
    """governor_stops.jsonl beside the bridge evidence log (RIMBRIDGE_EVIDENCE_LOG / the Windows default); override with
    RIMBRIDGE_GOVERNOR_LOG. Empty = no file (stderr only)."""
    import os
    p = os.environ.get("RIMBRIDGE_GOVERNOR_LOG")
    if p is not None:
        return p
    ev = os.environ.get("RIMBRIDGE_EVIDENCE_LOG", r"D:\Luke\dev\_rmscratch\bridge_calls.jsonl" if os.name == "nt" else "")
    return os.path.join(os.path.dirname(ev), "governor_stops.jsonl") if ev else ""


def _record_stop(g):
    """TESTENV_GOVERNOR_STOP_DIAGNOSE_NO_NOTE_LEFT (2026-10-13): a GovernorStop that a probe did not catch left no
    trace of its trigger (bridge_calls.jsonl keeps only start rows). Every stop now names its trigger on stderr AND
    in governor_stops.jsonl at construction, so an uncaught one still leaves a note. Never raises."""
    import json
    import sys
    r = g.result
    row = {"utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()), "message": str(g), "state": r.get("state"),
           "executed": r.get("executed"), "requested": r.get("requested"), "stopBy": r.get("stopBy"),
           "refused": r.get("refused"), "abortWhy": r.get("abortWhy"),
           "triggers": (r.get("triggers") or [])[:10], "argv": list(sys.argv)}
    try:
        sys.stderr.write("GOVERNOR_STOP %s\n" % json.dumps(row, default=str)[:2000])
    except Exception:                                        # noqa: BLE001
        pass
    path = _stop_log_path()
    if path:
        try:
            with open(path, "a", encoding="utf-8") as fh:
                fh.write(json.dumps(row, default=str) + "\n")
        except Exception:                                    # noqa: BLE001 - a note that cannot be written is not a crash
            pass


SAFE_ADVANCE = "jawa/safe_advance"
SAFE_CHUNK_MAX = 2500      # one safe_advance call per chunk: short enough that a refusal/latch is local


def _unwrap(r):
    if isinstance(r, dict) and r.get("content"):
        try:
            import json
            r = json.loads(r["content"][0]["text"])
        except Exception:                                    # noqa: BLE001
            pass
    if isinstance(r, dict) and isinstance(r.get("result"), dict) and "state" not in r:
        r = r["result"]
    return r if isinstance(r, dict) else {"raw": r}


def has_safe_advance(session):
    """True when the live companion has jawa/safe_advance. A session that lists its tools (rimdrive.Session.tools) is
    read; otherwise one status call is made and cached on the session."""
    tools = getattr(session, "tools", None)
    if isinstance(tools, (set, frozenset, list, tuple, dict)) and tools:
        return SAFE_ADVANCE in tools
    cached = getattr(session, "_safe_advance_ok", None)
    if cached is not None:
        return cached
    try:
        r = _unwrap(session.call(SAFE_ADVANCE, action="status"))
        # the real tool's status reply carries `advance` and `ticksGame`; a bare {"success": true} (a generic fake or a
        # proxy that answers anything) is NOT proof the tool exists
        ok = bool(r.get("success")) and "advance" in r and "ticksGame" in r
    except Exception:                                        # noqa: BLE001 - no tool = old companion: fall back
        ok = False
    try:
        session._safe_advance_ok = ok
    except Exception:                                        # noqa: BLE001
        pass
    return ok


def advance_chunk(session, ticks, pause_first=True, stop_on="default", time_exception=False):
    """Move the clock by ONE chunk of `ticks` (WATCH_WAIT_WIRE_SMALL_STEPS): through jawa/safe_advance (paused,
    <=60-tick sub-steps inside a frame budget, stopped by the vitals latch) when the companion has it, else the
    legacy rimworld/step_game_ticks. Returns the ticks the tool says it executed (None on the legacy path: callers
    measure ticksGame themselves). Raises GovernorStop when safe_advance did not finish."""
    ticks = int(ticks)
    if ticks <= 0:
        return 0
    if not has_safe_advance(session):
        session.call("rimworld/step_game_ticks", ticks=ticks, pauseFirst=bool(pause_first))
        return None
    r = _unwrap(session.call(SAFE_ADVANCE, ticks=ticks, stopOn=stop_on, timeException=bool(time_exception),
                             timeoutMs=max(60000, ticks * 100)))
    if r.get("state") == "running":
        try:
            session.call(SAFE_ADVANCE, action="cancel")
        except Exception:                                    # noqa: BLE001
            pass
        r = dict(r, state="cancelled", abortWhy="still running after timeoutMs; cancelled by the harness")
    if r.get("state") != "done":
        raise GovernorStop(r)
    return r.get("executed")


# -------------------------------------------------------------------- gate
class ClockGate:
    def __init__(self, session_cap):
        self.session_cap = int(session_cap)
        self.last_seen_tick = None
        self.epoch = 0
        self.frames = []          # open frames, outermost first
        self.component_spent = 0  # all component-ledger ticks this session
        self.overhead_spent = 0
        self._overhead_depth = 0
        self._lease_depth = 0
        self.entries = []         # every charge / epoch event, in order

    # -- frames
    def open_frame(self, scope, cap):
        f = {"scope": scope, "cap": int(cap), "spent": 0}
        self.frames.append(f)
        return f

    def close_frame(self, frame=None):
        if not self.frames:
            raise RuntimeError("no open frame")
        if frame is not None and self.frames[-1] is not frame:
            raise RuntimeError("frames must close innermost-first")
        return self.frames.pop()

    @contextlib.contextmanager
    def frame(self, scope, cap):
        f = self.open_frame(scope, cap)
        try:
            yield f
        finally:
            if self.frames and self.frames[-1] is f:
                self.frames.pop()

    # -- overhead / lease contexts
    @contextlib.contextmanager
    def overhead(self):
        self._overhead_depth += 1
        try:
            yield
        finally:
            self._overhead_depth -= 1

    @contextlib.contextmanager
    def lease(self, reason="tick-move"):
        self._lease_depth += 1
        try:
            yield
        finally:
            self._lease_depth -= 1

    def assert_leased(self):
        if self._lease_depth <= 0:
            raise UnleasedTickMove(
                "tick-moving verb called outside ClockGate.lease()")

    # -- accounting
    @property
    def total_spent(self):
        return self.component_spent + self.overhead_spent

    def observe(self, tick, epoch_change=False, reason="observe", **extra):
        """Re-base on `tick`; return the ticks charged (0 for first/epoch)."""
        if tick is None:
            raise ClockLost("observe() called with no clock reading")
        tick = int(tick)
        prev = self.last_seen_tick
        if prev is None:
            self.last_seen_tick = tick
            return 0
        delta = tick - prev
        if epoch_change or delta < 0:
            self.epoch += 1
            self.last_seen_tick = tick
            self.entries.append({
                "kind": "epoch", "reason": reason, "epoch": self.epoch,
                "tick_from": prev, "tick_to": tick, "ticks": 0,
                "cause": "flagged" if epoch_change else "negative_delta"})
            return 0
        self.last_seen_tick = tick
        if delta == 0:
            return 0
        in_overhead = self._overhead_depth > 0
        entry = {
            "kind": "charge",
            "ledger": "overhead" if in_overhead else "component",
            "reason": reason,
            "scope": "overhead" if in_overhead else
                     [f["scope"] for f in self.frames],
            "epoch": self.epoch, "tick_from": prev, "tick_to": tick,
            "ticks": delta}
        entry.update(extra)
        self.entries.append(entry)
        if in_overhead:
            self.overhead_spent += delta
        else:
            self.component_spent += delta
            for f in self.frames:
                f["spent"] += delta
        return delta

    def check(self):
        for f in self.frames:
            if f["spent"] > f["cap"]:
                raise BudgetExceeded(f["scope"], f["spent"], f["cap"])
        if self.total_spent > self.session_cap:
            raise BudgetExceeded("session", self.total_spent, self.session_cap)

    def remaining(self):
        r = self.session_cap - self.total_spent
        for f in self.frames:
            r = min(r, f["cap"] - f["spent"])
        return max(0, r)

    def as_dict(self):
        return {
            "session_cap": self.session_cap,
            "component_spent": self.component_spent,
            "overhead_spent": self.overhead_spent,
            "total_spent": self.total_spent,
            "epoch": self.epoch,
            "last_seen_tick": self.last_seen_tick,
            "open_frames": [dict(f) for f in self.frames],
            "entries": [dict(e) for e in self.entries],
        }

    def to_json(self):
        return json.dumps(self.as_dict())


# ------------------------------------------------------------ clock reading
def _field(resp, key):
    """Find `key` at top level or one level down (bridge payload nesting)."""
    if not isinstance(resp, dict):
        return None
    if key in resp:
        return resp[key]
    for k in ("result", "data", "state"):
        sub = resp.get(k)
        if isinstance(sub, dict) and key in sub:
            return sub[key]
    return None


def read_clock(session):
    """Return the full time_clock dict; ClockLost if unreadable."""
    try:
        r = session.call("jawa/time_clock")
    except Exception as e:  # transport failure is "no clock", not a crash
        raise ClockLost("time_clock call failed: %r" % (e,))
    if _field(r, "ticksGame") is None:
        raise ClockLost("time_clock returned no ticksGame: %r" % (r,))
    return r


def read_ticks(session):
    return int(_field(read_clock(session), "ticksGame"))


# --------------------------------------------------------------- tick mover
def step(session, gate, n, chunk=600, pause_first=True, on_chunk=None,
         max_stalls=3):
    """Advance the game by about `n` REAL ticks through the gate.

    Charges the measured ticksGame delta of every chunk. Refuses before
    moving anything if n > gate.remaining(). Returns the ticks advanced.
    `on_chunk(now)` runs after each chunk and may raise to abort."""
    n = int(n)
    if n <= 0:
        return 0
    with gate.lease("step"):
        # ticks that passed since the last observation are charged first
        gate.observe(read_ticks(session), reason="pre-step")
        gate.check()
        if n > gate.remaining():
            raise BudgetExceeded(
                "request", n, gate.remaining(),
                "step(%d) exceeds remaining()" % n)
        advanced, stalls = 0, 0
        while advanced < n:
            rem = gate.remaining()
            req = min(int(chunk), n - advanced, rem)
            if req <= 0:
                raise BudgetExceeded("remaining", gate.total_spent,
                                     gate.session_cap, "no budget left")
            epoch0 = gate.epoch
            advance_chunk(session, req, pause_first=pause_first)
            now = read_ticks(session)
            extra = {"requested": req}
            before = gate.last_seen_tick
            if before is not None and now - before > req:
                extra["overshoot"] = now - before - req
            measured = gate.observe(now, reason="step", **extra)
            if gate.epoch != epoch0:
                raise ClockLost("clock epoch changed mid-step (save/load or "
                                "map change); nothing charged")
            gate.check()
            if measured <= 0:
                stalls += 1
                if stalls >= max_stalls:
                    raise ClockStall(
                        "step_game_ticks moved nothing %d times in a row"
                        % stalls)
                continue
            stalls = 0
            advanced += measured
            if on_chunk is not None:
                on_chunk(now)
        return advanced


# -------------------------------------------------------------------- pause
def verify_pause(session, samples=3, gap_s=0.15, sleep=time.sleep):
    """True only if paused flag is true AND ticksGame is identical across
    `samples` reads separated by real wall-clock gaps. Two equal reads
    back-to-back are not proof (plan section 10 / GPT review)."""
    try:
        clock = read_clock(session)
    except ClockLost:
        return False
    if _field(clock, "paused") is not True:
        return False
    # MEASURED 2026-10-01: while paused the bridge still reports curTimeSpeed "Normal";
    # the `paused` flag is the truth, so the speed string is never consulted.
    first = int(_field(clock, "ticksGame"))
    for _ in range(max(1, int(samples) - 1)):
        sleep(gap_s)
        try:
            if read_ticks(session) != first:
                return False
        except ClockLost:
            return False
    return True


def ensure_paused(session, tries=3, samples=3, gap_s=0.15, sleep=time.sleep):
    for _ in range(max(1, tries)):
        if verify_pause(session, samples, gap_s, sleep):
            return True
        try:
            session.call("rimworld/pause_game", pause=True)
        except Exception:
            pass
    if verify_pause(session, samples, gap_s, sleep):
        return True
    raise PauseUnverified("could not verify the game is paused after %d "
                          "attempts" % tries)


# --------------------------------------------------------------- supervisor
class Supervisor:
    """Wall-clock watchdog in a sibling thread.

    On expiry, calls `on_expire()` from its own thread (supply a function
    that opens an INDEPENDENT connection and requests pause), then the
    optional `kill_worker()`. Sets `expired` and records `reason`.
    Cannot interrupt a blocked call in the worker -- only act beside it."""

    def __init__(self, wall_limit_s, on_expire, kill_worker=None):
        self.wall_limit_s = wall_limit_s
        self.on_expire = on_expire
        self.kill_worker = kill_worker
        self.expired = False
        self.reason = None
        self.error = None
        self.fired_in_thread = None
        self.done = threading.Event()   # set once the expiry action finished
        self._stop = threading.Event()
        self._thread = None

    def _run(self):
        if self._stop.wait(self.wall_limit_s):
            return
        self.expired = True
        self.reason = "wall-clock limit %.3fs expired" % self.wall_limit_s
        self.fired_in_thread = threading.current_thread()
        try:
            self.on_expire()
            if self.kill_worker is not None:
                self.kill_worker()
        except Exception as e:
            self.error = e
        finally:
            self.done.set()

    def start(self):
        self._thread = threading.Thread(target=self._run, daemon=True,
                                        name="clockgate-supervisor")
        self._thread.start()
        return self

    def stop(self):
        self._stop.set()
        if self._thread is not None:
            self._thread.join(timeout=5)

    def __enter__(self):
        return self.start()

    def __exit__(self, *exc):
        self.stop()
        return False
