#!/usr/bin/env python3
r"""pager_triggers.py — the section 8 triggers of the pager: which readings ring the owner's phone, and which are on.

Design: design/specs/2026-11-19-pushover-critical-alerts/design.md section 8. Page: triggers_boundary.md beside it.
Item RIMMANDRAKE_SEND_FIRST_TEST_PAGE_KEYS_VALID_SINCE_NOV_TWENTY. Selftest: selftest_pager_triggers.py.

    pager_triggers.py status                  each trigger: ON or OFF, and what its reading says now; rings nothing
    pager_triggers.py run [--dry-run]         page for each trigger that is ON and fires (through pager.py's one door)
    pager_triggers.py on|off <name> --why W   switch one trigger; the Conductor window only

Every trigger is OFF until the Conductor switches it on. `run` reads only the triggers that are ON. pager.send decides
who may send (the Conductor window or an Operations run) and rings one fault once per window.
A reading is CLEAR, FIRES or COULD_NOT_LOOK. COULD_NOT_LOOK never pages and is never CLEAR.
Exit of run: 0 every ON trigger was read, and each page needed was SENT or a REPEAT (DRY_RUN with --dry-run)
             1 a page that was needed did not leave (REFUSED or COULD_NOT_SEND)
             3 an ON trigger could not be read, or the switch file could not
             4 no trigger is on: nothing was read
             5 the tool itself broke
"""
import argparse
import datetime as _dt
import glob
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
if HERE not in sys.path:
    sys.path.insert(0, HERE)
import pager as P  # noqa: E402

CLEAR, FIRES, COULD_NOT_LOOK = "CLEAR", "FIRES", "COULD_NOT_LOOK"
# MAX_AGE_MIN: a reading older than this says nothing about now. Danger: a frozen ops_watch reads CLEAR for hours, or
# pages for a fault that ended. The same line as alarm_routes.json policy.status_max_age_min.
MAX_AGE_MIN = 45
# FAILED_FRESH_H: the switching plan retries a failed switch each pass and writes the marker's time again, so a failure
# that lasts keeps a fresh time. Danger: a one-time failure that a reset made moot pages him for days.
FAILED_FRESH_H = 6
DISK_FLOOR_GB = 50      # design section 8: about 6 h of writes at the worst measured day


class CannotLook(Exception):
    pass


def _load(path):
    try:
        with open(path, encoding="utf-8") as f:
            return json.load(f)
    except (OSError, ValueError) as e:
        raise CannotLook("%s: %s" % (os.path.basename(path), type(e).__name__))


def _when(s):
    try:
        t = _dt.datetime.fromisoformat(str(s).replace("Z", "+00:00"))
    except ValueError:
        raise CannotLook("time %r is not a time" % (s,))
    if t.tzinfo is None:
        raise CannotLook("time %r has no zone" % (s,))
    return t


def _fresh(at, now, what):
    age = (now - _when(at)).total_seconds() / 60.0
    if age > MAX_AGE_MIN:
        raise CannotLook("%s is %d min old (limit %d)" % (what, age, MAX_AGE_MIN))


def _point(root, now, key):
    d = _load(os.path.join(root, "ops_watch", "status.json"))
    p = (d.get("points") or {}).get(key) if isinstance(d, dict) else None
    if not isinstance(p, dict):
        raise CannotLook("status.json has no %s" % key)
    v = p.get("v")
    if p.get("m") != "MEASURED" or isinstance(v, bool) or not isinstance(v, (int, float)):
        raise CannotLook("%s is %s" % (key, p.get("m")))
    _fresh((p.get("x") or {}).get("observed_at") or d.get("at"), now, key)
    return v


def r_whea(root, now):
    v = _point(root, now, "disk.whea_severe_24h")
    return (FIRES if v > 0 else CLEAR), "disk.whea_severe_24h", "fatal disk or CPU errors in 24 h = %g (line 0)" % v


def r_disk(name):
    def read(root, now):
        v = _point(root, now, "disk.%s_free_gb" % name)
        return (FIRES if v < DISK_FLOOR_GB else CLEAR), "disk.%s_free_gb" % name, "disk %s free = %g GB (line %d)" % (
            name, v, DISK_FLOOR_GB)
    return read


def r_steve(root, now):
    d = _load(os.path.join(root, "testq", "fault_state.json"))
    ph = d.get("phase") if isinstance(d, dict) else None
    if not isinstance(ph, str):
        raise CannotLook("fault_state.json has no phase")
    _fresh(d.get("at"), now, "fault_state.json")
    if ph == "PASSIVE":     # fault_monitor.step returns at once while it is passive: STUCK cannot be reached
        raise CannotLook("the fault monitor is PASSIVE (advisory), so it never sets STUCK")
    return (FIRES if ph == "STUCK" else CLEAR), "steve.fault_stuck", "SteveDesktop fault phase = %s" % ph


def r_switch_failed(root, now):
    md = os.path.join(root, "switching_plan", "markers")
    if not os.path.isdir(md):
        raise CannotLook("no markers folder")
    done, failed = None, None
    for p in sorted(glob.glob(os.path.join(md, "*.json"))):
        m = _load(p)
        if not isinstance(m, dict) or "phase" not in m:
            raise CannotLook("%s is not a marker" % os.path.basename(p))
        if m["phase"] not in ("done", "failed"):
            continue
        t = _when(m.get("at"))
        if m["phase"] == "done":
            done = t if done is None else max(done, t)
        elif failed is None or t > failed[0]:
            failed = (t, os.path.splitext(os.path.basename(p))[0].lower())
    if failed is None or (done is not None and done > failed[0]):
        return CLEAR, "switching_plan:markers", "no failed switch is newer than the last good one"
    if (now - failed[0]).total_seconds() > FAILED_FRESH_H * 3600:
        return CLEAR, "switching_plan:markers", "the last failed switch is over %d h old" % FAILED_FRESH_H
    return FIRES, "switching_plan:" + failed[1], "a planned switch failed at %s" % P.iso(
        failed[0].astimezone(_dt.timezone.utc))


def r_fleet_stop(root, now):
    # `stopped` is written only after the fleet is stopped, and removed at the restart or the next switch; the log's
    # `do: stop` lines stay there after the stop ends.
    d = _load(os.path.join(root, "switching_plan", "state.json"))
    if not isinstance(d, dict):
        raise CannotLook("state.json is not an object")
    s = d.get("stopped")
    if not s:
        return CLEAR, "switching_plan:fleet_stop", "the fleet is not stopped"
    if not isinstance(s, dict):
        raise CannotLook("state.json stopped is not an object")
    return FIRES, "switching_plan:fleet_stop", "the fleet is stopped since %s: no account to run on" % P.iso(
        _when(s.get("at")).astimezone(_dt.timezone.utc))


# name -> (class, reader, why)
TRIGGERS = {
    "whea_severe": ("HARDWARE_FAILURE", r_whea, "a fatal hardware error is data at risk now"),
    "steve_stuck": ("HARDWARE_FAILURE", r_steve, "a reboot no longer clears the SteveDesktop fault"),
    "disk_root": ("HARDWARE_FAILURE", r_disk("root"), "a write fails soon on a disk this full"),
    "disk_c": ("HARDWARE_FAILURE", r_disk("c"), "a write fails soon on a disk this full"),
    "disk_d": ("HARDWARE_FAILURE", r_disk("d"), "a write fails soon on a disk this full"),
    "switch_failed": ("ACCOUNT_SWITCH_FAILURE", r_switch_failed, "the plan tried to switch accounts and could not"),
    "fleet_stop": ("ACCOUNT_SWITCH_FAILURE", r_fleet_stop, "no account is left to run on"),
}


def read(name, root, now):
    """-> (verdict, cause or None, text). Never raises: a reader that breaks could not look."""
    try:
        return TRIGGERS[name][1](root, now)
    except CannotLook as e:
        return COULD_NOT_LOOK, None, str(e)
    except Exception as e:  # noqa: BLE001  a file of another shape than promised
        return COULD_NOT_LOOK, None, "%s: %s" % (type(e).__name__, e)


def switch_path():
    return os.path.join(P.pager_dir(), "triggers_on.json")


def switches():
    """-> {name: {"at", "why"}} of the ON triggers; {} when the file was never written. Raises CannotLook on a torn
    file (never read as all off)."""
    if not os.path.exists(switch_path()):
        return {}
    d = _load(switch_path())
    if not isinstance(d, dict) or not all(isinstance(v, dict) for v in d.values()) or set(d) - set(TRIGGERS):
        raise CannotLook("triggers_on.json is not a switch file of the known triggers")
    return d


def set_switch(name, on, why, now, env=None, cgroup=None):
    """-> (ok, line). Only the Conductor window may switch a trigger (design section 8)."""
    who, who_why = P.caller(env, cgroup)
    if who != "conductor":
        return False, "TRIGGER REFUSED %s: only the Conductor window switches a trigger (%s)" % (name, who_why)
    if name not in TRIGGERS:
        return False, "TRIGGER REFUSED %r: the triggers are %s" % (name, ", ".join(TRIGGERS))
    if len(P._words(why)) < P.WHY_MIN_WORDS:
        return False, "TRIGGER REFUSED %s: --why needs at least %d words" % (name, P.WHY_MIN_WORDS)
    s = switches()
    if on:
        s[name] = {"at": P.iso(now), "why": why}
    else:
        s.pop(name, None)
    os.makedirs(P.pager_dir(), exist_ok=True)
    tmp = switch_path() + ".tmp.%d" % os.getpid()
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(s, f, indent=1, sort_keys=True)
    os.replace(tmp, switch_path())
    P.conductor_line("trigger %s switched %s: %s" % (name, "ON" if on else "OFF", why), now)
    return True, "TRIGGER %s %s" % ("ON" if on else "OFF", name)


def run(root, now, send=None, dry_run=False):
    """-> (exit, lines)."""
    send = send or P.send
    try:
        on = switches()
    except CannotLook as e:
        return 3, ["TRIGGERS COULD NOT LOOK: %s; nothing was read" % e]
    if not on:
        return 4, ["TRIGGERS NONE ON: nothing was read"]
    out, blind, unsent = [], 0, 0
    for name in TRIGGERS:
        if name not in on:
            continue
        verdict, cause, text = read(name, root, now)
        if verdict == FIRES:
            outcome, rec = send(TRIGGERS[name][0], cause, text[:200], "trigger %s: %s" % (name, TRIGGERS[name][2]),  # cut-ok: the pager requires a reading of at most 200 characters
                                dry_run=dry_run)
            if outcome not in (P.SENT, P.REPEAT, P.DRY_RUN):
                unsent += 1
            out.append("%s FIRES %s -> %s" % (name, text, P.verdict_line(outcome, rec)))
        else:
            blind += verdict == COULD_NOT_LOOK
            out.append("%s %s %s" % (name, verdict, text))
    out.append("TRIGGERS read %d of %d ON, could not look at %d, pages that did not leave %d" % (
        len(on) - blind, len(on), blind, unsent))
    return (1 if unsent else 3 if blind else 0), out


def status(root, now):
    try:
        on = switches()
    except CannotLook as e:
        return 3, ["TRIGGERS COULD NOT LOOK: %s" % e]
    return 0, ["%-14s %-3s %-14s %s" % (n, "ON" if n in on else "OFF", v, t)
               for n in TRIGGERS for v, _c, t in [read(n, root, now)]]


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    sub = ap.add_subparsers(dest="cmd", required=True)
    sub.add_parser("status")
    r = sub.add_parser("run")
    r.add_argument("--dry-run", action="store_true")
    for v in ("on", "off"):
        s = sub.add_parser(v)
        s.add_argument("name")
        s.add_argument("--why", required=True)
    a = ap.parse_args(argv)
    try:
        now = P.now_utc()
        if a.cmd in ("on", "off"):
            ok, line = set_switch(a.name, a.cmd == "on", a.why, now)
            print(line)
            return 0 if ok else 1
        rc, lines = run(P.data_root(), now, dry_run=a.dry_run) if a.cmd == "run" else status(P.data_root(), now)
        print("\n".join(lines))
        return rc
    except Exception as e:  # noqa: BLE001
        print("TRIGGERS ERROR %s: %s (no outcome is claimed)" % (type(e).__name__, e))
        return 5


if __name__ == "__main__":
    sys.exit(main())
