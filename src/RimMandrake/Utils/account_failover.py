#!/usr/bin/env python3
"""account_failover.py - switch this machine's Claude login once, when the burn account's week runs low.

Owner, 2026-10-27, on incorporating the lukas account: "Yes schedule when they reach 2%."
So: when `system` (the account Archmagi burns) reads MEASURED with at most THRESHOLD % of its week left, arm the
switch, `claude-account use lukas` (closes every Claude window on this machine and relaunches the Fleet), disarm.
Once only (a marker file), and never after RESET (the system week refills then); from DEADLINE on the switch is
unconditional while the target reads MEASURED above THRESHOLD. Stage 2 (marker present, `claude-account --json status`
says TO is live): slot_allocator `set --mode BURN --n 16` until TO's reset, then `--mode DARK` (every seat 0) once TO
reads MEASURED at or under THRESHOLD.

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
# lukas's week resets and refills (meter, 2026-10-28 09:41: week_resets_at 2026-10-28T16:00-07:00). Stage 2 acts only
# before it, and every --hours window ends at it: after it the meter names NEXT week's reset (a 168 h BURN) and a
# reading polled before it is pre-refill (a wrong DARK) (review r3 2026-10-28)
TO_RESET = "2026-10-28T16:00:00-07:00"
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


def run(argv, full=False, timeout=600):
    # a hang or a missing binary is a failed step, not an exception past check()'s marker cleanup (review night).
    # full=True -> (rc, stdout) whole: a parser must never see the 2000-char log tail (review 2026-10-28)
    try:
        r = subprocess.run(argv, capture_output=True, text=True, timeout=timeout)
    except subprocess.TimeoutExpired:
        return 124, "%s timed out after %d s" % (argv[1:2], timeout)
    except OSError as e:
        return 127, "%s could not run: %s" % (argv[:1], e)
    return r.returncode, r.stdout if full else (r.stdout + r.stderr)[-2000:]


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
    # the real status is ~2030 chars: the old 2000-char tail cut its opening brace -> None -> stage 2 never fired
    rc, out = run([CA, "--json", "status"], full=True, timeout=120)
    if rc != 0:
        return None
    dec, i = json.JSONDecoder(), out.find("{")
    while i >= 0:  # text before or after the JSON (a warning, a trailing note) must not hide the status
        try:
            obj, _ = dec.raw_decode(out[i:])
            if isinstance(obj, dict) and "live" in obj:
                return obj["live"]
        except ValueError:
            pass
        i = out.find("{", i + 1)
    return None


def decide2(acc, now, live, st):
    """Stage 2 (live account is TO). -> (action, why); action in None | "burn" | "off". Pure; never switches."""
    if live != TO:
        return None, "live account is %r, not %s: stage 2 idle" % (live, TO)
    b = acc.get(TO) or {}
    if now >= datetime.fromisoformat(TO_RESET).timestamp() - 60:
        return None, "%s week reset %s passed: stage 2 finished (retire the timer)" % (TO, TO_RESET)
    left = b.get("week_pct_left")
    # off needs no prior burn: a TO already spent at the first pass goes straight to DARK, never a burn first
    if (not st.get("off") and b.get("source") == "MEASURED" and not b.get("stale")
            and isinstance(left, (int, float)) and left <= THRESHOLD):
        return "off", "%s MEASURED at %.1f%% left <= %.1f%%: wait for the reset" % (TO, left, THRESHOLD)
    if not st.get("burn") and not st.get("off"):
        return "burn", "switched to %s: burn it" % TO
    return None, "burning; %s reads %r%%" % (TO, left)


def hours_to(reset, now):
    """-> hours from now to reset, rounded so the window never ends after it."""
    return max(0.001, int((datetime.fromisoformat(reset).timestamp() - now) / 3.6) / 1000)


def stage2(acc, dry):
    try:
        st = json.load(open(STAGE2))
    except Exception:  # noqa: BLE001
        st = {}
    live = live_account()
    now = time.time()  # after the status call: a slow one must not push the window past TO_RESET (review r3)
    act, why = decide2(acc, now, live, st)
    if act is None:
        log({"do": "stage2_skip", "why": why})
        return 0
    argv = [sys.executable, SLOT, "set", "--owner-said", OWNER_ORDER]
    # off is DARK (total 0, every seat): `--n 0` zeroed BENCH only and left FOUNDRY's slot burning lukas (review 2026-10-28)
    argv += ["--n", "16", "--mode", "BURN"] if act == "burn" else ["--mode", "DARK"]
    argv += ["--hours", str(hours_to(TO_RESET, now))]  # always: no --hours lets the allocator pick its own reset
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
    try:  # a hung meter is a logged skip, never a traceback that kills the pass (review 2026-10-28)
        r = subprocess.run([sys.executable, os.path.join(HERE, "account_usage.py"), "now", "--json"],
                           capture_output=True, text=True, timeout=120)
        if r.returncode != 0:
            raise RuntimeError("exit %s" % r.returncode)
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
    if live_account() == TO:  # already switched (by hand): `use` would close every window for nothing (review 2026-10-28)
        with open(MARKER, "w") as f:
            json.dump({"why": "already live on %s" % TO, "at": time.time()}, f)
        log({"do": "skip_switch", "why": "%s is already live: marked, stage 2 takes over" % TO})
        return 0
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
    if rc2 is None or (rc2 != 0 and live_account() != TO):
        # `use` never ran, or failed/timed out and TO is not live: nothing switched, the next pass may retry
        # (a kept marker would leave stage 2 idle on the wrong account for good; review night, r2 2026-10-28)
        os.remove(MARKER)
    log({"do": "switch", "why": why, "arm": [rc1, o1], "use": [rc2, o2], "disarm": [rc3, o3]})
    return 0 if rc2 == 0 else 2


if __name__ == "__main__":
    if len(sys.argv) < 2 or sys.argv[1] != "check":
        print(__doc__)
        sys.exit(2)
    sys.exit(check("--dry-run" in sys.argv))
