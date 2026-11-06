#!/usr/bin/env python3
"""Refuse a destructive bridge call (go_to_main_menu) while ANOTHER client process is mid-run.

MAP_DROP_DIAGNOSE_MENU_MIDRUN_GHOST: a site build's go_to_main_menu dropped the game under a proof run whose
step_game_ticks was in flight (two clients, one game). The evidence is the bridge call log written by
rimbridge_client (`start`/`end` rows with pid, cid, t). Refuse when a foreign pid has a call with no end row yet
(young enough to be plausible) or one that ended within WINDOW_S (10 s). Override: env
RM_ALLOW_CONCURRENT_BRIDGE=1. Log missing/unreadable => allow (WSL has no log; never block on blindness).
BRIDGEGUARD_FIX_DEAD_PID_STILL_BLOCKS: an unended start whose writer process is provably gone (pid dead, or pid
reused: its recorded pid_start differs) is a crashed client, not a live call, and no longer refuses. A writer this
process cannot check (another OS, no pid) stays presumed alive."""
import sys as _rm_sys, pathlib as _rm_pl  # noqa: E401
_rm_sys.path.insert(0, str(_rm_pl.Path(__file__).resolve().parents[3] / "src" / "RimMandrake" / "Utils"))
from rmpaths import rm_path, rm_str, rm_win  # noqa: E402,F401  (data root: rmpaths.py)
import calendar
import json
import os
import time

WINDOW_S = 10           # a foreign call that ENDED within this many seconds still counts as active
UNENDED_S = 900          # an unended start older than this is a dead client, not a live call
TAIL_BYTES = 400000


class ConcurrentBridgeClient(RuntimeError):
    pass


def default_log():
    p = os.environ.get("RIMBRIDGE_EVIDENCE_LOG")
    if p is not None:
        return p
    return rm_win("scratch", "bridge_calls.jsonl") if os.name == "nt" else ""


def _ts(s):
    return calendar.timegm(time.strptime(s, "%Y-%m-%dT%H:%M:%SZ"))


def writer_alive(row):
    """False only when the start row's writer is provably gone; True when alive or not checkable from here."""
    pid = row.get("pid")
    if pid is None or row.get("os", os.name) != os.name:
        return True                                    # a Windows pid means nothing to WSL, and the reverse
    try:
        import rimbridge_client
        return bool(rimbridge_client._pid_alive(int(pid), row.get("pid_start")))
    except Exception:                                  # noqa: BLE001 -- a broken probe must not unblock a live call
        return True


def foreign_activity(log=None, now=None, own_pid=None, window_s=WINDOW_S, alive=None):
    """Return a description of recent foreign-pid activity, or None."""
    log = default_log() if log is None else log
    if not log or not os.path.exists(log):
        return None
    now = time.time() if now is None else now
    own_pid = os.getpid() if own_pid is None else own_pid
    alive = writer_alive if alive is None else alive
    try:
        with open(log, "rb") as fh:
            fh.seek(0, 2)
            n = fh.tell()
            fh.seek(max(0, n - TAIL_BYTES))
            lines = fh.read().decode("utf-8", "replace").splitlines()
    except OSError:
        return None
    starts, ended = {}, {}
    for ln in lines:
        try:
            r = json.loads(ln)
        except ValueError:
            continue
        if r.get("ev") == "start":
            starts[r.get("cid")] = r
        elif r.get("ev") == "end":
            try:
                ended[r.get("cid")] = _ts(r["t"])
            except (KeyError, ValueError):
                ended[r.get("cid")] = now
    for cid, r in starts.items():
        if r.get("pid") in (None, own_pid):
            continue
        try:
            age = now - _ts(r["t"])
        except (KeyError, ValueError):
            continue
        # active = a call with no end row yet, or one that ended within window_s (TESTENV_GUARD_UNSTICK_BLOCKS_ITS_OWN_SEQUEL:
        # a finished client's start time is no evidence it is still driving the game)
        if (cid not in ended and age <= UNENDED_S and alive(r)) or (cid in ended and now - ended[cid] <= window_s):
            return "pid %s (%s) %s %s %ds ago%s" % (r.get("pid"), r.get("script"), r.get("tool"), r.get("t"),
                                                    age, "" if cid in ended else " [no end row: still running]")
    return None


def refuse_if_foreign_activity(what, **kw):
    if os.environ.get("RM_ALLOW_CONCURRENT_BRIDGE") == "1":
        return
    d = foreign_activity(**kw)
    if d:
        raise ConcurrentBridgeClient("refusing %s: another bridge client is active -- %s. Take the bridge "
                                     "(rimflow bridge take) or set RM_ALLOW_CONCURRENT_BRIDGE=1." % (what, d))
