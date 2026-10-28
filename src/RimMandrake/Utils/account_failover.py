#!/usr/bin/env python3
"""account_failover.py - switch this machine's Claude login once, when the burn account's week runs low.

Owner, 2026-10-27, on incorporating the lukas account: "Yes schedule when they reach 2%."
So: when `system` (the account Archmagi burns) reads MEASURED with at most THRESHOLD % of its week left, arm the
switch, `claude-account use lukas` (closes every Claude window on this machine and relaunches the Fleet), disarm.
Once only (a marker file), and never after DEADLINE (the system week resets then and refills it).

  account_failover.py check [--dry-run]     one pass (a systemd user timer runs it every 5 min)

Log: /mnt/d/ClaudeWork/rimmandrake/account_failover/log.jsonl. No AI; reads account_usage.py's poller output.
"""
import json
import os
import subprocess
import sys
import time
from datetime import datetime

HERE = os.path.dirname(os.path.abspath(__file__))
FROM, TO, MACHINE = "system", "lukas", "archmagi"
THRESHOLD = 2.0
DEADLINE = "2026-10-28T12:45:00-07:00"      # just before the system week resets (~19.2 h after 17:50 PDT 10-27)
OUT = "/mnt/d/ClaudeWork/rimmandrake/account_failover"
MARKER = os.path.join(OUT, "switched.json")
CA = os.path.expanduser("~/.local/bin/claude-account")


def log(rec):
    os.makedirs(OUT, exist_ok=True)
    rec["at"] = datetime.now().astimezone().isoformat(timespec="seconds")
    with open(os.path.join(OUT, "log.jsonl"), "a", encoding="utf-8") as f:
        f.write(json.dumps(rec, sort_keys=True) + "\n")
    print(json.dumps(rec, sort_keys=True))


def run(argv):
    r = subprocess.run(argv, capture_output=True, text=True, timeout=600)
    return r.returncode, (r.stdout + r.stderr)[-2000:]


def decide(acc, now, marker_exists):
    """-> (do_switch, why). Pure: acc is account_usage's {name: record}."""
    if marker_exists:
        return False, "already switched once (marker present)"
    if now >= datetime.fromisoformat(DEADLINE).timestamp():
        return False, "past the deadline: the %s week resets and refills" % FROM
    a, b = acc.get(FROM) or {}, acc.get(TO) or {}
    if a.get("source") != "MEASURED" or a.get("stale"):
        return False, "%s reading is %s%s: never switch on a guess" % (FROM, a.get("source"),
                                                                     " (stale)" if a.get("stale") else "")
    left = a.get("week_pct_left")
    if not isinstance(left, (int, float)):
        return False, "%s week_pct_left unreadable: %r" % (FROM, left)
    if left > THRESHOLD:
        return False, "%s at %.1f%% left > %.1f%%" % (FROM, left, THRESHOLD)
    bl = b.get("week_pct_left")
    # only a live reading of the target can say it is as low: a stale one may predate its own reset (review night)
    if (isinstance(bl, (int, float)) and bl <= THRESHOLD and not b.get("stale")
            and b.get("source") in ("MEASURED", "ESTIMATE")):
        return False, "%s also at %.1f%% left: switching gains nothing" % (TO, bl)
    return True, "%s at %.1f%% left <= %.1f%%; %s reads %r" % (FROM, left, THRESHOLD, TO, bl)


def check(dry):
    r = subprocess.run([sys.executable, os.path.join(HERE, "account_usage.py"), "now", "--json"],
                       capture_output=True, text=True, timeout=120)
    try:
        acc = json.loads(r.stdout).get("accounts") or {}
    except Exception as e:  # noqa: BLE001 - an unreadable meter is a no-switch, logged
        log({"do": "skip", "why": "account_usage unreadable: %s" % e})
        return 1
    go, why = decide(acc, time.time(), os.path.exists(MARKER))
    if not go:
        log({"do": "skip", "why": why})
        return 0
    if dry:
        log({"do": "would_switch", "why": why})
        return 0
    os.makedirs(OUT, exist_ok=True)
    with open(MARKER, "w") as f:      # before the switch: the switch closes this machine's agents, never twice
        json.dump({"why": why, "at": time.time()}, f)
    rc1, o1 = run([CA, "arm", "--confirm", MACHINE])
    if rc1 != 0:
        rc2, o2 = None, "not armed"
    elif time.time() >= datetime.fromisoformat(DEADLINE).timestamp():
        rc2, o2 = None, "the deadline passed while arming: no switch"  # review night: re-read before `use`
    else:
        rc2, o2 = run([CA, "use", TO, "--confirm", MACHINE])
    rc3, o3 = run([CA, "disarm"])
    if rc2 is None:
        os.remove(MARKER)  # `use` never ran, nothing switched: the next pass may retry (review night)
    log({"do": "switch", "why": why, "arm": [rc1, o1], "use": [rc2, o2], "disarm": [rc3, o3]})
    return 0 if rc2 == 0 else 2


if __name__ == "__main__":
    if len(sys.argv) < 2 or sys.argv[1] != "check":
        print(__doc__)
        sys.exit(2)
    sys.exit(check("--dry-run" in sys.argv))
