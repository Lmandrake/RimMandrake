#!/usr/bin/env python3
"""account_failover.py - switch this machine's Claude login once, when the burn account's week runs low.

Owner, 2026-10-27, on incorporating the lukas account: "Yes schedule when they reach 2%."
So: when `system` (the account Archmagi burns) reads MEASURED with at most THRESHOLD % of its week left, arm the
switch, `claude-account use lukas` (closes every Claude window on this machine and relaunches the Fleet), disarm.
Once only (a marker file), and never after RESET (the system week refills then); from DEADLINE on the switch is
unconditional while the target reads MEASURED above THRESHOLD. Stage 3: at/after RESET with FROM MEASURED and refilled AND TO MEASURED <= FLOOR (or TO_RESET passed), back to FROM once (own marker), then `slot_allocator clear`; retired.
Stage 2 (marker present, `claude-account --json status`
says TO is live): slot_allocator `set --mode BURN --n 16` until TO's reset; before RESET, `--mode DARK` (every seat 0)
at TO MEASURED <= SOFT and a hard stop (fleet-stop, retried until it succeeds) at <= FLOOR. After RESET with FROM
refilled there is no soft line (stage 3's switch is the stop): a pre-RESET DARK is lifted so TO burns to FLOOR.
Stage 1 switches only from a live FROM (never a hand-switched third account); an unknown status keeps a pending marker.
Owner 11:2x: stage 1 and the post-13:00 stage 3 switch at 0% (THRESHOLD, S3_FLOOR); the pre-13:00 hard stop stays at FLOOR.
Blind-meter guard: a last good FROM or TO reading <= BLIND (1%) then ESTIMATE, stale or unreadable counts as 0%.

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
# Owner 2026-10-28 10:20 PDT card: the floor is ours ("1% if we leave it, 2% if we wait on it"). We leave system (stage 1
# at <=1.0%) and WAIT on lukas until 13:00 (floor 2.0%, soft line 4.0%: "Soft line, then hard stop").
THRESHOLD = 0.0   # stage 1: system -> lukas at or under this much of system's week left (owner 11:2x: let it hit 0%)
BLIND = 1.0       # a last good FROM/TO reading at or under this, then a blind or stale meter or a limit error = 0% (owner 11:2x)
S3_FLOOR = 0.0    # stage 3: lukas at or under this -> back to system (the pre-13:00 hard stop stays at FLOOR)
FLOOR = 2.0       # stage 2: lukas at or under this -> hard stop (fleet-stop); also "lukas is spent" for stage 1
SOFT = FLOOR + 2  # stage 2: lukas at or under this -> allocator DARK (no new helpers)
DEADLINE = "2026-10-28T12:45:00-07:00"      # from here the switch is unconditional (target live): system's unused week expires
RESET = "2026-10-28T13:00:00-07:00"         # the system week resets and refills: no switch after this
# lukas's week resets and refills (meter, 2026-10-28 09:41: week_resets_at 2026-10-28T16:00-07:00). Stage 2 acts only
# before it, and every --hours window ends at it: after it the meter names NEXT week's reset (a 168 h BURN) and a
# reading polled before it is pre-refill (a wrong DARK) (review r3 2026-10-28)
# (Owner 10:07 had ended stage 2 at system's 13:00; superseded by the use-it-or-lose-it ruling below.)
# Owner 10:15 intent ("Use up both lukas and system down to ~2%"), delegated ruling use-it-or-lose-it: burn the account whose
# reset comes soonest among those above their floor. So lukas's own 16:00 reset bounds stage 2 again (BURN to 15:59), and
# stage 3 (back to system) fires at 13:00 or later only when lukas MEASURED <= FLOOR or its 16:00 has passed. Before
# 13:00 there is nowhere to go, so the soft line / hard stop apply; after it lukas at the floor goes to system instead.
TO_RESET = "2026-10-28T16:00:00-07:00"
OWNER_ORDER = ("Ok, wake up! We have tokens to burn! Use up this account, then switch to the other account and use it "
               "up to 2% to, then wait for the reset to hit.")
SLOT = os.path.join(HERE, "slot_allocator.py")
STAGE2 = os.path.join(OUT_DIR := "/mnt/d/ClaudeWork/rimmandrake/account_failover", "stage2.json")
OUT = OUT_DIR
MARKER = os.path.join(OUT, "switched.json")
BACK = os.path.join(OUT, "switched_back.json")   # stage 3's own marker: once only
REFILLED = 50.0   # FROM reads at least this much week left: its reset has landed
CA = os.path.expanduser("~/.local/bin/claude-account")
# a pending marker older than any one pass (arm + use + disarm at 600 s each, plus the reads) is a pass that died
# between writing it and finishing `use` (review r4 2026-10-28)
STALE_PENDING_S = 2400
DRY = False  # set by check(): dry-run records say so in the shared log


def write_atomic(path, obj):
    """json to path via a temp file and os.replace: a pass that dies mid-write leaves the previous state."""
    os.makedirs(os.path.dirname(path), exist_ok=True)
    tmp = path + ".tmp"
    with open(tmp, "w") as f:
        json.dump(obj, f)
    os.replace(tmp, path)


def log(rec):
    os.makedirs(OUT, exist_ok=True)
    rec["at"] = datetime.now().astimezone().isoformat(timespec="seconds")
    if DRY:
        rec["dry"] = True  # a hand dry-run must not read as a timer pass (review r4)
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


def blind_zero(a, last=None):
    """True when FROM's meter cannot be read now but its last good figure was <= BLIND: usage only rises inside a
    window, so a blind meter or a limit error there is 0% (owner 11:2x). a = account_usage record; last = the
    failover's own memory {\"left\": x} of the last fresh MEASURED reading."""
    left = a.get("week_pct_left")
    if isinstance(left, (int, float)) and a.get("source") in ("MEASURED", "ESTIMATE"):
        return left <= BLIND and (a.get("source") == "ESTIMATE" or bool(a.get("stale")))
    return isinstance(last, dict) and isinstance(last.get("left"), (int, float)) and last["left"] <= BLIND


def decide(acc, now, marker_exists, last=None):
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
        if bl <= FLOOR:
            return False, "deadline, but %s is at %.1f%% left: nothing to gain" % (TO, bl)
        return True, "deadline %s reached (%s reads %r); %s reads %r > %.1f%%" % (
            DEADLINE, FROM, a.get("week_pct_left"), TO, bl, FLOOR)
    blind = a.get("source") != "MEASURED" or a.get("stale")
    if blind and blind_zero(a, last):
        bl0 = b.get("week_pct_left")
        if (isinstance(bl0, (int, float)) and bl0 <= FLOOR and not b.get("stale")
                and b.get("source") in ("MEASURED", "ESTIMATE")):
            return False, "%s also at %.1f%% left: switching gains nothing" % (TO, bl0)
        return True, "%s meter blind (%s%s) after a last good reading <= %.1f%%: treated as 0%%" % (
            FROM, a.get("source"), ", stale" if a.get("stale") else "", BLIND)
    if blind:
        return False, "%s reading is %s%s: never switch on a guess" % (FROM, a.get("source"),
                                                                     " (stale)" if a.get("stale") else "")
    left = a.get("week_pct_left")
    if not isinstance(left, (int, float)):
        return False, "%s week_pct_left unreadable: %r" % (FROM, left)
    if left > THRESHOLD:
        return False, "%s at %.1f%% left > %.1f%%" % (FROM, left, THRESHOLD)
    bl = b.get("week_pct_left")
    # only a live reading of the target can say it is as low: a stale one may predate its own reset (review night)
    if (isinstance(bl, (int, float)) and bl <= FLOOR and not b.get("stale")
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


def decide2(acc, now, live, st, allow_stop=True, ready3=False):
    """Stage 2 (live account is TO). -> (action, why); action in None | "burn" | "reburn" | "off" | "stop". Pure.
    ready3: past RESET with FROM refilled - the stage-3 switch is the stop, so no soft line: burn TO to its floor
    (review r5: a DARK fleet barely moves TO, it never reaches the floor and FROM's fresh week idles until TO_RESET)."""
    if live != TO:
        return None, "live account is %r, not %s: stage 2 idle" % (live, TO)
    b = acc.get(TO) or {}
    if now >= datetime.fromisoformat(TO_RESET).timestamp() - 60:
        return None, "%s week reset %s passed: stage 2 finished (retire the timer)" % (TO, TO_RESET)
    left = b.get("week_pct_left")
    fresh = b.get("source") == "MEASURED" and not b.get("stale") and isinstance(left, (int, float))
    # stop_failed: arm or fleet-stop failed - workers still burn under the floor, so retry (review r5 GPT)
    if allow_stop and fresh and left <= FLOOR and (not st.get("stop") or st.get("stop_failed")):
        return "stop", "%s MEASURED at %.1f%% left <= %.1f%% floor: hard stop, wait for the reset" % (TO, left, FLOOR)
    # off needs no prior burn: a TO already spent at the first pass goes straight to DARK, never a burn first
    if ready3:
        if st.get("off") and not st.get("stop") and fresh and left > S3_FLOOR:
            return "reburn", "%s refilled: lift the soft-line DARK, burn %s (%.1f%%) to its %.1f%% floor" % (
                FROM, TO, left, S3_FLOOR)
    elif fresh and left <= SOFT and not st.get("off"):
        return "off", "%s MEASURED at %.1f%% left <= %.1f%% soft line: DARK, wait for the reset" % (TO, left, SOFT)
    if not st.get("burn") and not st.get("off"):
        return "burn", "switched to %s: burn it" % TO
    if st.get("off"):
        return None, "DARK; waiting for the %s reset; %s reads %r%%" % (TO_RESET, TO, left)
    return None, "burning; %s reads %r%%" % (TO, left)


def decide3(acc, now, live, done, stopped=False):
    """Stage 3 (owner 10:07): back to FROM once its week has reset. -> (do_switch, why). Pure; never names another account."""
    if done:
        return False, "stage 3 done: retired"
    if now < datetime.fromisoformat(RESET).timestamp():
        return False, "before the %s reset %s" % (FROM, RESET)
    if live != TO:
        return False, "live account is %r, not %s: not switching" % (live, TO)
    a = acc.get(FROM) or {}
    left = a.get("week_pct_left")
    if a.get("source") != "MEASURED" or a.get("stale") or not isinstance(left, (int, float)):
        return False, "%s reading is %s%s: waiting for a fresh one" % (FROM, a.get("source"), " (stale)" if a.get("stale") else "")
    if left < REFILLED:
        return False, "%s reads %.1f%% left < %.0f%%: its reset has not shown yet" % (FROM, left, REFILLED)
    b = acc.get(TO) or {}
    bl = b.get("week_pct_left")
    # stopped: the hard stop already fleet-stopped TO at its floor; a later noisy reading above it must not strand the
    # stopped fleet until TO_RESET (review r5)
    spent = stopped or (b.get("source") == "MEASURED" and not b.get("stale") and isinstance(bl, (int, float))
                        and bl <= S3_FLOOR) or blind_zero(b)
    if not spent and now < datetime.fromisoformat(TO_RESET).timestamp():
        return False, "%s still above its %.1f%% floor (reads %r) and its reset %s is ahead: keep burning it" % (TO, FLOOR, bl, TO_RESET)
    return True, "%s week reset: reads %.1f%% left; %s is live and %s" % (
        FROM, left, TO, "hard-stopped at its floor" if stopped else
        "MEASURED at %.1f%% <= floor" % bl if spent else "its reset passed")


NOGO = "nogo"   # stage3 verdict: not switching now, nothing pending - stage 2 carries on with lukas


def stage3(acc, live, now, dry, st=None):
    try:
        bk = json.load(open(BACK))
    except Exception:  # noqa: BLE001
        bk = None
    if isinstance(bk, dict) and bk.get("phase") == "done" and bk.get("clear_rc", 0) != 0:
        # review r5: a failed clear left stage 2's override (DARK until TO_RESET) on FROM's fresh week: retry each pass
        if dry:
            log({"do": "stage3_would_retry_clear", "why": "clear_rc %r" % bk.get("clear_rc")})
            return 0
        rc4, o4 = run([sys.executable, SLOT, "clear"])
        write_atomic(BACK, dict(bk, clear_rc=rc4))
        log({"do": "stage3_retry_clear", "clear": [rc4, o4[-200:]]})
        return 0 if rc4 == 0 else 2
    if isinstance(bk, dict) and bk.get("phase") == "pending":
        # abandon only when TO is confirmed live: an unknown status may hide a `use` that switched (review r5 GPT r2)
        if live != TO or now - float(bk.get("at") or now) <= STALE_PENDING_S:
            if live == FROM:  # `use` finished although the pass died before its marker: done
                if not dry:
                    write_atomic(BACK, dict(bk, phase="done", clear_rc=None))  # clear still owed (review r5 GPT)
            log({"do": "stage3_skip", "why": "pending marker; live is %r" % live})
            return 0
        if not dry:
            os.remove(BACK)
        log({"do": "stage3_abandoned_dropped", "why": "pending marker from %s, live is %r" % (bk.get("at"), live)})
        return 0
    go, why = decide3(acc, now, live, bk is not None, stopped=bool((st or {}).get("stop")))
    if not go:
        log({"do": "stage3_skip", "why": why})
        return NOGO
    if dry:
        log({"do": "stage3_would_switch_back", "why": why})
        return 0
    write_atomic(BACK, {"why": why, "at": now, "phase": "pending"})
    rc1, o1 = run([CA, "arm", "--confirm", MACHINE])
    rc2, o2 = (run([CA, "use", FROM, "--confirm", MACHINE]) if rc1 == 0 else (None, "not armed"))
    rc3, o3 = run([CA, "disarm"])
    live_after = FROM if rc2 == 0 else (live_account() if rc2 is not None else TO)
    if live_after is None:  # `use` ran and failed, status unreadable: it may have switched - keep pending (review r5 GPT)
        log({"do": "stage3_switch_back", "why": why, "arm": [rc1, o1], "use": [rc2, o2], "disarm": [rc3, o3],
             "live_after": None, "marker": "kept pending: live account unknown"})
        return 2
    if live_after != FROM:
        os.remove(BACK)  # nothing switched: the next pass may retry
        log({"do": "stage3_switch_back", "why": why, "arm": [rc1, o1], "use": [rc2, o2], "disarm": [rc3, o3],
             "live_after": live_after, "marker": "dropped: the next pass decides again"})
        return 2
    write_atomic(BACK, {"why": why, "at": time.time(), "phase": "done", "use_rc": rc2, "clear_rc": None})
    # the allocator paces the fresh week on its own: drop stage 2's override
    rc4, o4 = run([sys.executable, SLOT, "clear"])
    write_atomic(BACK, {"why": why, "at": time.time(), "phase": "done", "use_rc": rc2, "clear_rc": rc4})
    log({"do": "stage3_switch_back", "why": why, "arm": [rc1, o1], "use": [rc2, o2], "disarm": [rc3, o3],
         "live_after": live_after, "marker": "kept: stage 3 retired", "clear": [rc4, o4[-200:]]})
    return 0 if rc3 == 0 and rc4 == 0 else 2


def hours_to(reset, now):
    """-> hours from now to reset, rounded so the window never ends after it."""
    return max(0.001, int((datetime.fromisoformat(reset).timestamp() - now) / 3.6) / 1000)


def hard_stop(st, why, now, dry):
    """Floor reached on the account we wait on: DARK if not yet, then arm, fleet-stop, disarm, once (marker first)."""
    if dry:
        log({"do": "stage2_would_stop", "why": why})
        return 0
    # before the commands, and owing a retry until arm + fleet-stop succeed: a pass that dies mid-stop is retried
    # (fleet-stop on a stopped fleet finds no pids; review r5 GPT round 2)
    st["stop"] = st["stop_failed"] = now
    write_atomic(STAGE2, st)
    rcs = {}
    if not st.get("off"):
        argv = [sys.executable, SLOT, "set", "--owner-said", OWNER_ORDER, "--mode", "DARK",
                "--hours", str(hours_to(TO_RESET, now))]
        rcs["dark"] = run(argv)
        if rcs["dark"][0] == 0:
            st["off"] = now
            write_atomic(STAGE2, st)
    # fleet-stop needs the machine armed and refuses under Claude (this runs under systemd); it needs no --confirm.
    # Stage 3's `use` relaunches the Fleet whether or not any window is running (fleet_stop() just returns no pids).
    rcs["arm"] = run([CA, "arm", "--confirm", MACHINE])
    rcs["stop"] = run([CA, "fleet-stop"]) if rcs["arm"][0] == 0 else (None, "not armed")
    rcs["disarm"] = run([CA, "disarm"])
    if rcs["arm"][0] == 0 and rcs["stop"][0] == 0:
        st.pop("stop_failed", None)
    else:
        st["stop_failed"] = now
    write_atomic(STAGE2, st)
    log({"do": "stage2_stop", "why": why, "rcs": rcs})
    return 0 if all(v[0] == 0 for v in rcs.values()) else 2


def stage2(acc, dry):
    try:
        st = json.load(open(STAGE2))
    except Exception:  # noqa: BLE001
        st = {}
    live = live_account()
    now = time.time()  # after the status call: a slow one must not push the window past TO_RESET (review r3)
    try:
        mk = json.load(open(MARKER))
    except Exception:  # noqa: BLE001
        mk = {}
    if (isinstance(mk, dict) and mk.get("phase") == "pending" and live not in (None, TO)
            and now - float(mk.get("at") or now) > STALE_PENDING_S):
        # the pass that wrote it died before `use` finished and TO is not live: an attempt, not a switch; drop it so the
        # next pass decides again (review r4: otherwise stage 2 idles on the wrong account for good)
        if not dry:
            os.remove(MARKER)
        log({"do": "abandoned_switch_dropped", "why": "pending marker from %s, live is %r" % (mk.get("at"), live)})
        return 0
    if isinstance(mk, dict) and mk.get("phase") == "pending" and live == TO and not dry:
        # TO seen live: the stage-1 switch happened. Promote it, so a later stage-3 pass (live FROM, clear owed) is never
        # mistaken for an abandoned attempt and its marker deleted (review r5 GPT round 3)
        write_atomic(MARKER, dict(mk, phase="done"))
    after = now >= datetime.fromisoformat(RESET).timestamp()
    if after:
        r3 = stage3(acc, live, now, dry, st)
        if r3 != NOGO:
            return r3
    a = acc.get(FROM) or {}
    ready3 = (after and a.get("source") == "MEASURED" and not a.get("stale")
              and isinstance(a.get("week_pct_left"), (int, float)) and a["week_pct_left"] >= REFILLED)
    act, why = decide2(acc, now, live, st, allow_stop=not after, ready3=ready3)
    if act is None:
        log({"do": "stage2_skip", "why": why})
        return 0
    if act == "stop":
        return hard_stop(st, why, now, dry)
    argv = [sys.executable, SLOT, "set", "--owner-said", OWNER_ORDER]
    # off is DARK (total 0, every seat): `--n 0` zeroed BENCH only and left FOUNDRY's slot burning lukas (review 2026-10-28)
    argv += ["--n", "16", "--mode", "BURN"] if act in ("burn", "reburn") else ["--mode", "DARK"]
    argv += ["--hours", str(hours_to(TO_RESET, now))]  # always: no --hours lets the allocator pick its own reset
    if dry:
        log({"do": "stage2_would_" + act, "why": why, "argv": argv[2:]})
        return 0
    rc, out = run(argv)
    if rc == 0:
        st["burn" if act == "reburn" else act] = now
        if act == "reburn":
            st.pop("off", None)
        os.makedirs(OUT, exist_ok=True)
        write_atomic(STAGE2, st)
    log({"do": "stage2_" + act, "why": why, "rc": rc, "out": out[-300:]})
    return 0 if rc == 0 else 2


def check(dry):
    global DRY
    DRY = dry
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
    lastp, a0 = os.path.join(OUT, "from_last.json"), acc.get(FROM) or {}
    if a0.get("source") == "MEASURED" and not a0.get("stale") and isinstance(a0.get("week_pct_left"), (int, float)):
        if not dry:
            write_atomic(lastp, {"left": a0["week_pct_left"], "at": time.time()})
        last = None
    else:
        try:
            last = json.load(open(lastp))
        except Exception:  # noqa: BLE001
            last = None
    go, why = decide(acc, time.time(), False, last)
    if not go:
        log({"do": "skip", "why": why})
        return 0
    if dry:
        log({"do": "would_switch", "why": why})
        return 0
    os.makedirs(OUT, exist_ok=True)
    live0 = live_account()
    if live0 not in (FROM, TO):  # steven by hand, or unreadable: never close someone else's windows (review r5 GPT)
        log({"do": "skip_switch", "why": "live account is %r, not %s: not switching" % (live0, FROM)})
        return 0
    if live0 == TO:  # already switched (by hand): `use` would close every window for nothing (review 2026-10-28)
        with open(MARKER, "w") as f:
            json.dump({"why": "already live on %s" % TO, "at": time.time()}, f)
        log({"do": "skip_switch", "why": "%s is already live: marked, stage 2 takes over" % TO})
        return 0
    # before the switch, phase pending: if this pass dies before `use` finishes, stage 2 can tell an attempt from a switch
    write_atomic(MARKER, {"why": why, "at": time.time(), "phase": "pending"})
    rc1, o1 = run([CA, "arm", "--confirm", MACHINE])
    if rc1 != 0:
        rc2, o2 = None, "not armed"
    elif time.time() >= datetime.fromisoformat(RESET).timestamp():
        rc2, o2 = None, "the %s reset passed while arming: no switch" % FROM  # review night: re-read before `use`
    else:
        rc2, o2 = run([CA, "use", TO, "--confirm", MACHINE])
    rc3, o3 = run([CA, "disarm"])
    live_after = TO if rc2 == 0 else (live_account() if rc2 is not None else FROM)
    if live_after is None:
        # `use` ran and failed, status unreadable: it may have switched. Keep pending: stage 2 drops it once a live FROM
        # is seen past STALE_PENDING_S, and a lost marker after RESET would bypass stages 2 and 3 for good (review r5 GPT)
        marker = "kept pending: live account unknown"
    elif live_after != TO:
        # `use` never ran, or failed/timed out and TO is not live: nothing switched, the next pass may retry
        # (a kept marker would leave stage 2 idle on the wrong account for good; review night, r2 2026-10-28)
        os.remove(MARKER)
        marker = "dropped: the next pass decides again"
    else:
        write_atomic(MARKER, {"why": why, "at": time.time(), "phase": "done", "use_rc": rc2})
        marker = "kept: stage 2 takes over"
    log({"do": "switch", "why": why, "arm": [rc1, o1], "use": [rc2, o2], "disarm": [rc3, o3],
         "live_after": live_after, "marker": marker})
    # a failed disarm leaves the machine armed: nonzero so the journal shows it (review r4)
    return 0 if rc2 == 0 and rc3 == 0 else 2


if __name__ == "__main__":
    if len(sys.argv) < 2 or sys.argv[1] != "check":
        print(__doc__)
        sys.exit(2)
    sys.exit(check("--dry-run" in sys.argv))
