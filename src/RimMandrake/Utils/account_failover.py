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
DEADLINE = "2026-10-28T12:45:00-07:00"      # from here the switch is unconditional (target live): system's unused week expires
RESET = "2026-10-28T13:00:00-07:00"         # the system week resets and refills: no switch after this
OWNER_ORDER = ("Ok, wake up! We have tokens to burn! Use up this account, then switch to the other account and use it "
               "up to 2% to, then wait for the reset to hit.")
SLOT = os.path.join(HERE, "slot_allocator.py")
STAGE2 = os.path.join(OUT_DIR := "/mnt/d/ClaudeWork/rimmandrake/account_failover", "stage2.json")
OUT = OUT_DIR
MARKER = os.path.join(OUT, "switched.json")
CA = os.path.expanduser("~/.local/bin/claude-account")


def log(rec):
    os.makedirs(OUT, exist_ok=True)
    rec["at"] = datetime.now().astimezone().isoformat(timespec="seconds")
    with open(os.path.join(OUT, "log.jsonl"), "a", encoding="utf-8") as f:
        f.write(json.dumps(rec, sort_keys=True) + "\n")
    print(json.dumps(rec, sort_keys=True))


def run(argv):
    # a hang or a missing binary is a failed step, not an exception past check()'s marker cleanup (review night)
    try:
        r = subprocess.run(argv, capture_output=True, text=True, timeout=600)
    except subprocess.TimeoutExpired:
        return 124, "%s timed out after 600 s" % argv[1:2]
    except OSError as e:
        return 127, "%s could not run: %s" % (argv[:1], e)
    return r.returncode, (r.stdout + r.stderr)[-2000:]


def decide(acc, now, marker_exists):
    """-> (do_switch, why). Pure: acc is account_usage's {name: record}."""
    if marker_exists:
        return False, "already switched once (marker present)"
    if now >= datetime.fromisoformat(RESET).timestamp():
        return False, "past the %s reset: its week refilled" % FROM
    a, b = acc.get(FROM) or {}, acc.get(TO) or {}
    if now >= datetime.fromisoformat(DEADLINE).timestamp():
        # unused system week expires at RESET anyway; the target must still be a live reading, and not already spent
        bl = b.get("week_pct_left")
        if b.get("source") != "MEASURED" or b.get("stale") or not isinstance(bl, (int, float)):
            return False, "deadline, but %s reading is %s: never switch on a guess" % (TO, b.get("source"))
        if bl <= THRESHOLD:
            return False, "deadline, but %s is at %.1f%% left: nothing to gain" % (TO, bl)
        return True, "deadline reached with %s above %.1f%%; %s reads %r" % (FROM, THRESHOLD, TO, bl)
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


def live_account():
    """-> the live account name from `claude-account --json status`, or None."""
    rc, out = run([CA, "--json", "status"])
    try:
        return json.loads(out[out.index("{"):]).get("live") if rc == 0 else None
    except Exception:  # noqa: BLE001
        return None


def decide2(acc, now, live, st):
    """Stage 2 (live account is TO). -> (action, why); action in None | "burn" | "off". Pure; never switches."""
    if live != TO:
        return None, "live account is %r, not %s: stage 2 idle" % (live, TO)
    b = acc.get(TO) or {}
    reset = b.get("week_resets_at")
    if reset and now >= datetime.fromisoformat(reset).timestamp() + 600 and st.get("off"):
        return None, "%s week reset passed: stage 2 finished (retire the timer)" % TO
    left = b.get("week_pct_left")
    if (st.get("burn") and not st.get("off") and b.get("source") == "MEASURED" and not b.get("stale")
            and isinstance(left, (int, float)) and left <= THRESHOLD):
        return "off", "%s MEASURED at %.1f%% left <= %.1f%%: wait for the reset" % (TO, left, THRESHOLD)
    if not st.get("burn"):
        return "burn", "switched to %s: burn it" % TO
    return None, "burning; %s reads %r%%" % (TO, left)


def hours_to(reset, now):
    try:
        h = (datetime.fromisoformat(reset).timestamp() - now) / 3600
    except Exception:  # noqa: BLE001
        return None
    return round(h, 2) if h > 0.05 else None


def stage2(acc, dry):
    try:
        st = json.load(open(STAGE2))
    except Exception:  # noqa: BLE001
        st = {}
    now = time.time()
    act, why = decide2(acc, now, live_account(), st)
    if act is None:
        log({"do": "stage2_skip", "why": why})
        return 0
    n, mode = (16, "BURN") if act == "burn" else (0, None)
    hrs = hours_to((acc.get(TO) or {}).get("week_resets_at"), now)
    argv = [sys.executable, SLOT, "set", "--n", str(n), "--owner-said", OWNER_ORDER]
    if mode:
        argv += ["--mode", mode]
    if hrs:
        argv += ["--hours", str(hrs)]
    if dry:
        log({"do": "stage2_would_" + act, "why": why, "argv": argv[2:]})
        return 0
    rc, out = run(argv)
    if rc == 0:
        st[act] = now
        os.makedirs(OUT, exist_ok=True)
        json.dump(st, open(STAGE2, "w"))
    log({"do": "stage2_" + act, "why": why, "rc": rc, "out": out[-300:]})
    return 0 if rc == 0 else 2


def check(dry):
    r = subprocess.run([sys.executable, os.path.join(HERE, "account_usage.py"), "now", "--json"],
                       capture_output=True, text=True, timeout=120)
    try:
        acc = json.loads(r.stdout).get("accounts") or {}
    except Exception as e:  # noqa: BLE001 - an unreadable meter is a no-switch, logged
        log({"do": "skip", "why": "account_usage unreadable: %s" % e})
        return 1
    if os.path.exists(MARKER):
        return stage2(acc, dry)
    go, why = decide(acc, time.time(), False)
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
    elif time.time() >= datetime.fromisoformat(RESET).timestamp():
        rc2, o2 = None, "the %s reset passed while arming: no switch" % FROM  # review night: re-read before `use`
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
