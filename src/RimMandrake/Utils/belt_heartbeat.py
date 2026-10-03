"""belt_heartbeat.py - a long live run says "I am alive, on step X" every <=30 s, and dies LOUDLY at its budget.

WHY (2026-10-03, five hang classes in one belt night; design/RimMandrake/live_test_hang_runbook.md)
    A watcher polling "is the process alive" cannot tell SLOW from DEAD from ALREADY-FINISHED. rerun13 died in
    under a second on a focus refusal while the bridge agent polled it for 5+ minutes believing it ran. So every
    long runner writes one small JSON file, rewritten atomically by a daemon thread that does not depend on the
    main thread or the bridge:

        .belt_state/heartbeat_<job>.json   {"job","pid","host","ts","iso","step","step_started","step_budget_s",
                                            "job_started","job_budget_s","finished","status","cause"}

    `belt_watchdog.py` reads it: ts older than STALE_S means the runner process is gone or frozen; a step older
    than its budget means the main thread is stuck; finished=true with status UNMEASURED means the run is OVER
    and nobody should be polling it.

HARD BUDGETS
    A step (one suite) and the whole job each carry a wall-clock budget. When one is exceeded the thread records
    UNMEASURED(BUDGET: ...) through the job's own finish() - same results file, same shape - marks the heartbeat
    finished, prints a loud line, and hard-exits the process with EXIT_BUDGET (os._exit: a main thread blocked in
    a socket read on Windows cannot be interrupted any other way). A hang therefore costs at most one budget,
    never an evening.

USE (common.main does this for every live_queue job)
    hb = belt_heartbeat.start(job_id, on_budget=lambda cause: ..., job_budget_s=...)
    belt_heartbeat.step("suite Cauldron", budget_s=1500)
    belt_heartbeat.stop(status="MEASURED", cause=None)
"""
import json
import os
import socket
import sys
import threading
import time

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(HERE)))
STATE_DIR = os.environ.get("BELT_STATE_DIR") or os.path.join(ROOT, ".belt_state")
BEAT_S = 30            # rewrite interval; the watchdog calls a beat older than STALE_S stale
STALE_S = 150
EXIT_BUDGET = 4        # distinct from live_queue's 0 PASS / 1 FAIL / 2 UNMEASURED / 3 FOCUS_LOST
DEFAULT_STEP_BUDGET_S = int(os.environ.get("BELT_SUITE_BUDGET_S", "1500"))
DEFAULT_JOB_BUDGET_S = int(os.environ.get("BELT_JOB_BUDGET_S", str(4 * 3600)))

_lock = threading.Lock()
_state = None          # dict, the current heartbeat record
_thread = None
_stop = threading.Event()
_on_budget = None
_exit = os._exit       # injectable for the selftest


def path_for(job):
    return os.path.join(STATE_DIR, "heartbeat_%s.json" % job)


def _write(rec):
    os.makedirs(STATE_DIR, exist_ok=True)
    p = path_for(rec["job"])
    tmp = "%s.%d.tmp" % (p, os.getpid())
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(rec, f, default=str)
    os.replace(tmp, p)


def _beat(now=None):
    now = time.time() if now is None else now
    with _lock:
        if _state is None:
            return
        _state["ts"] = now
        _state["iso"] = time.strftime("%Y-%m-%dT%H:%M:%S", time.localtime(now))
        rec = dict(_state)
    try:
        _write(rec)
    except OSError:
        pass          # a heartbeat must never take the run down


def over_budget(rec, now=None):
    """The budget cause string if rec is over a step or job budget, else None. Pure."""
    now = time.time() if now is None else now
    if rec.get("finished"):
        return None
    sb, ss = rec.get("step_budget_s"), rec.get("step_started")
    if sb and ss and now - ss > sb:
        return "BUDGET: step %r ran %.0f s > %d s budget" % (rec.get("step"), now - ss, sb)
    jb, js = rec.get("job_budget_s"), rec.get("job_started")
    if jb and js and now - js > jb:
        return "BUDGET: job %r ran %.0f s > %d s budget (step %r)" % (rec.get("job"), now - js, jb, rec.get("step"))
    return None


def _check_budget(now=None):
    with _lock:
        rec = dict(_state) if _state else None
    if not rec:
        return None
    cause = over_budget(rec, now)
    if not cause:
        return None
    print("\n!! %s -- killing the run, recording UNMEASURED" % cause, file=sys.stderr, flush=True)
    try:
        if _on_budget:
            _on_budget(cause)
    finally:
        stop(status="UNMEASURED", cause=cause)
        sys.stdout.flush()
        _exit(EXIT_BUDGET)
    return cause


def _loop():
    while not _stop.wait(BEAT_S):
        _beat()
        _check_budget()


def start(job, on_budget=None, job_budget_s=None, thread=True):
    """Begin beating for `job`. on_budget(cause) is called once, from the beat thread, before the hard exit."""
    global _state, _thread, _on_budget
    now = time.time()
    with _lock:
        _state = {"job": job, "pid": os.getpid(), "host": socket.gethostname(), "argv": sys.argv[1:],
                  "job_started": now, "job_budget_s": job_budget_s or DEFAULT_JOB_BUDGET_S,
                  "step": "start", "step_started": now, "step_budget_s": None,
                  "finished": False, "status": None, "cause": None}
    _on_budget = on_budget
    _stop.clear()
    _beat(now)
    if thread:
        _thread = threading.Thread(target=_loop, name="belt-heartbeat", daemon=True)
        _thread.start()
    return path_for(job)


def step(name, budget_s=None):
    """Mark the start of a step. budget_s=None keeps no step budget (the job budget still applies)."""
    with _lock:
        if _state is None:
            return
        _state["step"] = str(name)
        _state["step_started"] = time.time()
        _state["step_budget_s"] = budget_s
    _beat()


def stop(status=None, cause=None):
    """Final beat: finished=true, so a watcher knows the run is OVER rather than silent."""
    global _state
    _stop.set()
    with _lock:
        if _state is None:
            return
        _state["finished"] = True
        _state["status"] = status
        _state["cause"] = cause
    _beat()
    with _lock:
        _state = None


def read(job=None, state_dir=None):
    """Every heartbeat record (or one job's), each with age_s added. Never raises."""
    d = state_dir or STATE_DIR
    out = []
    try:
        names = sorted(os.listdir(d))
    except OSError:
        return out
    now = time.time()
    for n in names:
        if not (n.startswith("heartbeat_") and n.endswith(".json")):
            continue
        if job and n != "heartbeat_%s.json" % job:
            continue
        try:
            with open(os.path.join(d, n), encoding="utf-8") as f:
                rec = json.load(f)
        except (OSError, ValueError):
            continue
        rec["age_s"] = now - float(rec.get("ts") or 0)
        out.append(rec)
    return out
