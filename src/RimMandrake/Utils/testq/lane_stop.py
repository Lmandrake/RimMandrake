#!/usr/bin/env python3
"""lane_stop.py - a stop of the SteveDesktop lane names its end: two equal bad endings on one game stop that game, and
every pause ends by itself. Page: design/specs/2026-11-23-lane-stops-name-their-end/boundary.md. No AI, no ssh.

Why: on 2026-11-23 Steve2 gave the same refusal 47 times in 11 h, and the lane once stood 49 h under a pause with no end.
"""
import os
import subprocess
import time

import retest as R
import schema as S

RETRY_S = 30 * 60           # the end of a stop and of an auto pause: one job is tried again (page, LIMITS)
DEFAULT_PAUSE_H = 2         # a hand pause that names no end
ESCALATE_S = 60 * 60        # a game still stopped this long after its first stop is the steward's
NEVER = ("BLOCKED_SELECTION", "SCHEMA", "GUARD_HELD", "CANARY")   # a bad request, a lock, or a cause with its own pause


def stop_path(T, host):
    return T.q("%s_stop.json" % host)


def last_path(T, host):
    return T.q("%s_last_end.json" % host)


def stamp(t):
    return time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime(t))


def signature(res):
    """-> the ending two jobs must share to be equal, or None: DONE, a stop from outside, or a cause that never counts."""
    res = res or {}
    if res.get("outcome") not in ("REFUSED", "INVALID") or res.get("cause") in NEVER:
        return None
    return "%s/%s: %s" % (res["outcome"], res.get("cause"), R.normal(res.get("note"))[:60])


def on_finish(T, host, job, res, cancelled, now=None):
    """Count this ending on HOST -> the stop record when it is the second equal one in a row, else None."""
    now = time.time() if now is None else now
    if cancelled or res.get("outcome") == "INTERRUPTED":
        return None
    sig, last = signature(res), T.read_json(last_path(T, host)) or {}
    if sig is None:
        if os.path.exists(stop_path(T, host)):
            os.remove(stop_path(T, host))
        S.dump({"sig": None, "job": job["id"], "mod": job.get("mod"), "stops": 0}, last_path(T, host))
        return None
    same = last.get("sig") == sig
    one_mod = same and res.get("outcome") == "INVALID" and res.get("cause") == "HARNESS" and last.get("mod") == job.get("mod")
    stops = (last.get("stops") or 0) + 1 if same and not one_mod else 0
    S.dump({"sig": sig, "job": job["id"], "mod": job.get("mod"), "stops": stops,
            "first": last.get("first") if same and last.get("first") else stamp(now)}, last_path(T, host))
    if not stops:
        return None
    rec = {"since": stamp(now), "first": last.get("first") or stamp(now), "until": stamp(now + RETRY_S), "signature": sig,
           "jobs": [last.get("job"), job["id"]], "stops": stops}
    S.dump(rec, stop_path(T, host))
    T.log("GAME %s STOPPED until %s: %s and %s ended the same (%s); one job is tried again then" % (
        T.GAME_NAMES.get(host, host), rec["until"], rec["jobs"][0], job["id"], sig[:100]))
    return rec


def stopped(T, host, now=None):
    """-> HOST's stop record while it stands, else None. Past its end it stands no more; `step` removes the file."""
    rec = T.read_json(stop_path(T, host))
    if not rec:
        return None
    try:
        return rec if S.parse_ts(rec["until"]) > (time.time() if now is None else now) else None
    except (KeyError, TypeError, ValueError):       # a torn record stops nothing
        return None


def unit_active(unit):
    """-> True, False, or None when systemd could not be asked."""
    try:
        r = subprocess.run(["systemctl", "--user", "is-active", unit], capture_output=True, text=True, timeout=20)
    except (OSError, subprocess.SubprocessError):
        return None
    word = r.stdout.strip()
    if word in ("active", "activating", "reloading", "deactivating"):
        return True
    return False if word in ("inactive", "failed", "unknown") else None


def pause_ended(pz, now, active=unit_active):
    """-> (True | False | None, why). None: the end could not be read, so the pause stays."""
    if pz.get("until_unit"):
        a = active(pz["until_unit"])
        if a is None:
            return None, "could not look: systemd did not answer for %s" % pz["until_unit"]
        return (not a), "unit %s is %s" % (pz["until_unit"], "active" if a else "over")
    try:
        until = S.parse_ts(pz["until"]) if pz.get("until") else S.parse_ts(pz["since"]) + DEFAULT_PAUSE_H * 3600
    except (KeyError, TypeError, ValueError):
        return None, "could not look: the pause's times are not readable"
    return now >= until, "its end %s %s" % (stamp(until), "passed" if now >= until else "is ahead")


def step(T, hosts, now=None, active=unit_active):
    """One pass of the tick: lift each pause and drop each stop whose end has come -> [what was lifted]."""
    now = time.time() if now is None else now
    out = []
    for host in hosts:
        pz = T.paused(host)
        if pz:
            over, why = pause_ended(pz, now, active)
            if over:
                T.cmd_resume(T.argparse.Namespace(reason="the pause's own end: " + why, lane=host))
                out.append("pause %s" % host)
            elif over is None:
                T.log("pause of %s stays: %s" % (host, why))
        if os.path.exists(stop_path(T, host)) and not stopped(T, host, now):
            os.remove(stop_path(T, host))
            T.log("GAME %s: its stop ended; one job is tried" % T.GAME_NAMES.get(host, host))
            out.append("stop %s" % host)
    return out
