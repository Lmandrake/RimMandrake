#!/usr/bin/env python3
"""Refuse a destructive bridge call (go_to_main_menu) while ANOTHER client process is mid-run.

MAP_DROP_DIAGNOSE_MENU_MIDRUN_GHOST: a site build's go_to_main_menu dropped the game under a proof run whose
step_game_ticks was in flight (two clients, one game). The evidence is the bridge call log written by
rimbridge_client (`start`/`end` rows with pid, cid, t). Refuse when a row from a foreign pid started within
WINDOW_S, or a foreign start has no end row yet (young enough to be plausible). Override: env
RM_ALLOW_CONCURRENT_BRIDGE=1. Log missing/unreadable => allow (WSL has no log; never block on blindness)."""
import calendar
import json
import os
import time

WINDOW_S = 60
UNENDED_S = 900          # an unended start older than this is a dead client, not a live call
TAIL_BYTES = 400000


class ConcurrentBridgeClient(RuntimeError):
    pass


def default_log():
    p = os.environ.get("RIMBRIDGE_EVIDENCE_LOG")
    if p is not None:
        return p
    return r"D:\Luke\dev\_rmscratch\bridge_calls.jsonl" if os.name == "nt" else ""


def _ts(s):
    return calendar.timegm(time.strptime(s, "%Y-%m-%dT%H:%M:%SZ"))


def foreign_activity(log=None, now=None, own_pid=None, window_s=WINDOW_S):
    """Return a description of recent foreign-pid activity, or None."""
    log = default_log() if log is None else log
    if not log or not os.path.exists(log):
        return None
    now = time.time() if now is None else now
    own_pid = os.getpid() if own_pid is None else own_pid
    try:
        with open(log, "rb") as fh:
            fh.seek(0, 2)
            n = fh.tell()
            fh.seek(max(0, n - TAIL_BYTES))
            lines = fh.read().decode("utf-8", "replace").splitlines()
    except OSError:
        return None
    starts, ended = {}, set()
    for ln in lines:
        try:
            r = json.loads(ln)
        except ValueError:
            continue
        if r.get("ev") == "start":
            starts[r.get("cid")] = r
        elif r.get("ev") == "end":
            ended.add(r.get("cid"))
    for cid, r in starts.items():
        if r.get("pid") in (None, own_pid):
            continue
        try:
            age = now - _ts(r["t"])
        except (KeyError, ValueError):
            continue
        if age <= window_s or (cid not in ended and age <= UNENDED_S):
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
