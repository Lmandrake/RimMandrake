#!/usr/bin/env python3
"""External live drivers a mod's suite reads (TESTQ_SWEEP_WIRE_FLOWWORKS_DRIVERS).

Some chains do not measure anything themselves: they read a result JSON that a separate northstar/ driver script wrote
at the current mod hash (FlowWorks: thirst_live.py, drawbridge_proof.py, validation_v2.py --live ...). A sweep that only
runs the chains leaves every such row UNMEASURED ("no result at the current mod hash"), which is what the 2026-10-26
SteveDesktop sweep read for ~180 FlowWorks rows. A suite names its drivers in `suite.live_drivers`, a list of dicts:

    {"name": "thirst_live",                      # a label for receipts
     "script": "northstar/thirst_live.py",       # relative to the mod folder
     "args": ["--site", "150,130"],              # extra argv
     "chains": ["thirst"],                       # the chains whose rows this driver's result feeds
     "timeout_s": 2400,                          # killed after this (receipt status TIMEOUT)
     "stage": "pre"}                             # "pre": run before the suite (default); "chain": run on demand by
                                                 #   the chain itself through once() (a site the other chains must not
                                                 #   run on, e.g. FlowWorks' river site, which its chains use last)

`modcheck run --drivers on` (sets MODCHECK_RUN_DRIVERS=1; the SteveDesktop worker passes it) makes runner.run call run()
after the map and test profile are up and before the chains: each "pre" driver whose chains overlap the selected chains
runs once, in table order, under this interpreter, and returns a receipt. A driver that fails or times out is a receipt,
never a crash: its chains then read their honest UNMEASURED. Without the flag nothing runs (a desk run keeps its old
behaviour: the drivers are run by hand). Never runs a driver for a chain that was not selected.
"""
import os
import subprocess
import sys
import time

ENV = "MODCHECK_RUN_DRIVERS"
DEFAULT_TIMEOUT_S = 1200
# All "pre" drivers of one run share this wall budget: a sweep's job timeout (14400 s) must still cover the chains.
DEFAULT_BUDGET_S = int(os.environ.get("MODCHECK_DRIVERS_BUDGET_S") or 7200)

_DONE = {}      # (mod_dir, name) -> receipt: a "chain"-stage driver runs at most once per process


def enabled():
    return os.environ.get(ENV) == "1"


def plan(suite, chain_names, stage="pre"):
    """The drivers of `suite` at `stage` whose chains overlap `chain_names`, in table order."""
    want = set(chain_names)
    return [d for d in (getattr(suite, "live_drivers", None) or [])
            if d.get("stage", "pre") == stage and want.intersection(d.get("chains") or ())]


PLAYER_LOG_TOKEN = "@player_log"


def player_log():
    """This machine's live Player.log (None when it is not a file here)."""
    try:
        import rimbridge_client as rb  # noqa: E402
        p = rb.DEFAULT_PLAYER_LOG
    except Exception:     # noqa: BLE001 - no client here: no log
        return None
    return p if os.path.isfile(p) else None


def _argv(mod_dir, d, python, _log=player_log):
    """argv for driver `d`. An arg PLAYER_LOG_TOKEN becomes this machine's Player.log; with none, that token and the
    flag before it are dropped (the driver then reports its log rows UNMEASURED instead of crashing on a bad path)."""
    args = [str(a) for a in (d.get("args") or [])]
    if PLAYER_LOG_TOKEN in args:
        i = args.index(PLAYER_LOG_TOKEN)
        log = _log()
        args = args[:i] + [log] + args[i + 1:] if log else args[:max(i - 1, 0)] + args[i + 1:]
    return [python, os.path.join(mod_dir, d["script"])] + args


def _call(argv, cwd, timeout_s):
    """(rc or None on timeout, combined output tail)."""
    try:
        r = subprocess.run(argv, cwd=cwd, capture_output=True, text=True, timeout=timeout_s,
                           encoding="utf-8", errors="replace")
        return r.returncode, ((r.stdout or "") + (r.stderr or ""))[-1500:]
    except subprocess.TimeoutExpired as ex:
        out = ex.stdout or ""
        if isinstance(out, bytes):
            out = out.decode("utf-8", "replace")
        return None, out[-1500:]


def run_one(mod_dir, d, cwd=None, _call_fn=None, python=None, log=None):
    """Run one driver; return its receipt {driver, argv, status PASSED_RC0|FAILED|TIMEOUT, rc, wall_s, tail}."""
    log = log or sys.stderr
    argv = _argv(mod_dir, d, python or sys.executable)
    timeout_s = int(d.get("timeout_s") or DEFAULT_TIMEOUT_S)
    print("[modcheck] driver %s START (timeout %d s): %s" % (d["name"], timeout_s, " ".join(argv[1:])),
          file=log, flush=True)
    t0 = time.monotonic()
    rc, tail = (_call_fn or _call)(argv, cwd or mod_dir, timeout_s)
    wall = round(time.monotonic() - t0, 1)
    status = "TIMEOUT" if rc is None else ("RC0" if rc == 0 else "FAILED")
    print("[modcheck] driver %s %s rc=%s in %.0f s" % (d["name"], status, rc, wall), file=log, flush=True)
    return {"driver": d["name"], "argv": argv[1:], "chains": list(d.get("chains") or []), "status": status,
            "rc": rc, "wall_s": wall, "tail": tail}


def run(suite, mod_dir, chain_names, cwd=None, after=None, budget_s=None, _call_fn=None, python=None, log=None):
    """Run the "pre" drivers plan() selects; `after(receipt)` runs after each (runner: ensure_playing_map), and an
    exception it raises is recorded on that receipt. Drivers past the shared budget are SKIPPED_BUDGET receipts.
    Returns [] when the flag is off."""
    if not enabled():
        return []
    budget = DEFAULT_BUDGET_S if budget_s is None else budget_s
    t0 = time.monotonic()
    out = []
    for d in plan(suite, chain_names):
        left = budget - (time.monotonic() - t0)
        if left < 60:
            out.append({"driver": d["name"], "chains": list(d.get("chains") or []), "status": "SKIPPED_BUDGET",
                        "rc": None, "wall_s": 0.0, "tail": "driver budget %d s spent" % budget})
            continue
        d = dict(d, timeout_s=min(int(d.get("timeout_s") or DEFAULT_TIMEOUT_S), int(left)))
        rec = run_one(mod_dir, d, cwd=cwd, _call_fn=_call_fn, python=python, log=log)
        if after is not None:
            try:
                after(rec)
            except Exception as ex:     # noqa: BLE001 - a recovery failure is recorded; the chains then say why
                rec["after_error"] = "%s: %s" % (type(ex).__name__, ex)
        out.append(rec)
    return out


def once(mod_dir, d, cwd=None, _call_fn=None, python=None, log=None):
    """A "chain"-stage driver, run the first time a chain asks in this process (None when the flag is off)."""
    if not enabled():
        return None
    key = (os.path.abspath(mod_dir), d["name"])
    if key not in _DONE:
        _DONE[key] = run_one(mod_dir, d, cwd=cwd, _call_fn=_call_fn, python=python, log=log)
    return _DONE[key]
