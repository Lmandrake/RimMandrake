#!/usr/bin/env python3
"""nightly_catchup: a nightly selftest sweep that did not finish runs again on its own
(NIGHTLY_SWEEP_HARDEN_DIED_AT_SIXTY).

Why Persistent= is not enough: rm-selftests-nightly.timer has had Persistent=true, and on 2026-11-02 it did fire late, at
03:21 after a restart. The next restart SIGTERMed the sweep at 03:22, test 60 of 925. The timer's stamp said it had fired,
so nothing ran until a hand restart at 09:07, and everything that reads the nightly read the night before. Persistent= sees
a fire that never happened; it cannot see a run that never finished.

So this reads the outcome, not the schedule. A night is DONE when Transient/selftests_nightly.log (known_reds.log_path, the
file every consumer reads) holds a section with a RESULT line that began at or after that night's start hour. Each pass
(rm-selftests-nightly-catchup.timer, after boot and hourly) starts the sweep's own unit when the night is not done, unless:
  disabled  the nightly timer is off: whoever turned it off meant it, so this does not bring it back
  running   the sweep is up (`systemctl start` on a running oneshot would only wait on it)
  quiet     the next scheduled fire is close, and it will do the same job
  gave_up   selftest.nightly_catchup_attempts tries for this night have gone. A sweep that keeps dying must not be
            restarted for ever; ops_watch's testing.nightly_gave_up raises one alarm instead, and the next night starts over
A section with no RESULT is a killed sweep, and a start that left no section at all still counts, through the `started`
number kept in the reading. Every pass writes ops_watch/nightly_catchup.json whatever it finds; deadman_check holds its age.
What it cannot read (systemd, the log) it does not act on: that is state `blind`, exit 1.

    python3 src/RimMandrake/Utils/nightly_catchup.py run       one pass
    python3 src/RimMandrake/Utils/nightly_catchup.py status    what a pass would decide; changes nothing
"""
import argparse
import datetime as dt
import json
import os
import subprocess
import sys
import time
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(HERE.parent / "rimflow"))
import known_reds as KR  # noqa: E402

SERVICE = "rm-selftests-nightly.service"
TIMER = "rm-selftests-nightly.timer"
QUIET_S = 3600    # one catch-up period: closer than this to the next fire, the fire does the work
UP = {"active", "activating", "reloading", "deactivating"}
DOWN = {"inactive", "failed"}
ON = {"enabled", "enabled-runtime", "static", "linked", "linked-runtime", "alias", "indirect", "generated"}
OFF = {"disabled", "masked", "masked-runtime", "not-found"}


def night_start(now, hour):
    """The latest local start hour at or before `now`, and the one after it. Dates, not now - 86400: a DST night is 23 or
    25 hours long."""
    t = dt.datetime.fromtimestamp(now)
    day = t.date()
    if dt.datetime.combine(day, dt.time(hour)).timestamp() > now:
        day -= dt.timedelta(days=1)
    return (dt.datetime.combine(day, dt.time(hour)).timestamp(),
            dt.datetime.combine(day + dt.timedelta(days=1), dt.time(hour)).timestamp())


def sections(text):
    """The log -> every sweep section, oldest first: {t, finished}. Same section line as known_reds; a killed sweep leaves
    the line and nothing under it."""
    out = []
    for ln in text.splitlines():
        m = KR.SECTION.match(ln)
        if m:
            out.append({"t": KR.epoch(m.group(1)), "finished": False})
        elif out and ln.startswith("RESULT:"):
            out[-1]["finished"] = True
    return out


def decide(now, log_text, state, enabled, started, hour, cap, quiet_s=QUIET_S):
    """(start?, state, why). Pure: `state` is the service's ActiveState, `enabled` whether the nightly timer is on, `started`
    how many starts this tool has made for this night."""
    since, nxt = night_start(now, hour)
    tonight = [s for s in sections(log_text) if s["t"] >= since]
    if not enabled:
        return False, "disabled", TIMER + " is not enabled"
    if state in UP:
        return False, "running", SERVICE + " is " + state
    if any(s["finished"] for s in tonight):
        return False, "done", "a sweep finished since " + KR.stamp(since)
    tries = max(len(tonight), started)
    if tries >= cap:
        return False, "gave_up", "no sweep finished since %s after %d tries of %d" % (KR.stamp(since), tries, cap)
    if nxt - now <= quiet_s:
        return False, "quiet", "the next fire, %s, is close" % KR.stamp(nxt)
    return True, "start", "no sweep finished since %s; try %d of %d" % (KR.stamp(since), tries + 1, cap)


def systemctl(*args):
    """stdout's first word, or None when systemd did not answer. Exit codes say nothing here: is-active exits 3 on the
    healthy answer `inactive`."""
    try:
        r = subprocess.run(["systemctl", "--user", *args], capture_output=True, text=True, timeout=60)
    except (OSError, subprocess.TimeoutExpired):
        return None
    words = r.stdout.split()
    return words[0] if words else None


def reading_path():
    return Path(os.environ.get("RM_OPS_WATCH_DIR", "/mnt/d/ClaudeWork/rimmandrake/ops_watch")) / "nightly_catchup.json"


def read_started(path, night):
    """Starts made for this night. A reading that cannot be read costs the count, and the log's sections still bound it."""
    try:
        r = json.loads(path.read_text(encoding="utf-8"))
        return int(r.get("started", 0)) if r.get("night") == night else 0
    except (OSError, ValueError, AttributeError, TypeError):
        return 0


def read_log(path):
    """The log's text; "" when the file is absent but its folder is there (no sweep has ever written it). None when the
    clone itself is missing or the file cannot be read: that is blindness, not a night with no sweep."""
    try:
        return path.read_text(encoding="utf-8", errors="replace")
    except FileNotFoundError:
        return "" if path.parent.parent.is_dir() else None
    except OSError:
        return None


def write_reading(path, obj):
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix(".tmp")
    tmp.write_text(json.dumps(obj, indent=1, sort_keys=True), encoding="utf-8")
    os.replace(tmp, path)


def one_pass(now, act, ctl=systemctl, log=None, out=None):
    """One decision; acts and writes the reading only when `act`. Returns the reading."""
    import testing_policy as TP
    hour, cap = int(TP.param("selftest.nightly_full_hour_local")), int(TP.param("selftest.nightly_catchup_attempts"))
    log, out = log or KR.log_path(), out or reading_path()
    night = KR.stamp(night_start(now, hour)[0])
    started = read_started(out, night)
    text, state, on = read_log(log), ctl("is-active", SERVICE), ctl("is-enabled", TIMER)
    r = {"at": KR.stamp(now), "night": night, "started": started, "log": str(log)}
    if text is None or state not in UP | DOWN or on not in ON | OFF:
        r.update(state="blind", why="log readable=%s, is-active=%s, is-enabled=%s" % (text is not None, state, on))
    else:
        go, st, why = decide(now, text, state, on in ON, started, hour, cap)
        r.update(state=st, why=why)
        if go and act:
            r["started"] = started + 1     # counted even if the start fails: a start that cannot work stops at the cap
            ctl("start", "--no-block", SERVICE)
            after = ctl("is-active", SERVICE)
            if after not in UP:
                r.update(state="start_failed", why="%s reads %s after the start" % (SERVICE, after))
    if act:
        write_reading(out, r)
    return r


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("verb", choices=("run", "status"))
    a = ap.parse_args(argv)
    r = one_pass(time.time(), a.verb == "run")
    print("%s: %s" % (r["state"], r["why"]))
    return 1 if r["state"] in ("blind", "start_failed") else 0


if __name__ == "__main__":
    sys.exit(main())
