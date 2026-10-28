#!/usr/bin/env python3
"""timers_guard: alarm when enabled rm-*/testq-* user timers are INACTIVE (stopped, not failed), plus the pause helper
(TIMERS_DIAGNOSE_SILENT_MASS_STOP).

2026-10-28 05:04 a remote `systemctl --user stop $(... rm-*/testq-*.timer)` stopped every timer, deadman and ops_watch
included, for 4.6 h with no alarm: ops_watch only counts failed/overdue timers and a stopped timer has no next elapse.
So this guard (a) runs from a unit named OUTSIDE the rm-*/testq-* glob (timer-guard.timer; a glob stop cannot take it),
(b) judges by ActiveState of every ENABLED watched timer, (c) files ONE ledger alarm the way deadman does
(ops_watch.real_filer), edge-triggered. A pause that armed its own restart (pause below, unit timer-resume-*) is
tolerated while that restart is pending; if the restart is gone and timers are still inactive, that is the alarm.

    timers_guard.py run [--file-alarms]
    timers_guard.py install [--apply]
    timers_guard.py pause --hours H TIMER [TIMER...]     arm restart (systemd-run --on-active) THEN stop, one step
    timers_guard.py pause --hours H --all                every enabled watched timer
"""
import argparse
import json
import os
import re
import subprocess
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(HERE.parent / "rimflow"))

WATCH_RE = re.compile(r"^(rm|testq)-[A-Za-z0-9_.@-]+\.timer$")
GUARD_NAME = "timer-guard"
RESUME_PREFIX = "timer-resume-"


def ops_dir():
    return Path(os.environ.get("RM_OPS_WATCH_DIR", "/mnt/d/ClaudeWork/rimmandrake/ops_watch"))


def state_file():
    return ops_dir() / "timers_guard.json"


def pauses_file():
    return ops_dir() / "timers_pauses.json"


def load_pauses():
    """{resume_unit.timer: [covered timers]} as recorded by pause(); {} when absent or unreadable (=> nothing tolerated)."""
    try:
        d = json.loads(pauses_file().read_text(encoding="utf-8"))
        return d if isinstance(d, dict) else {}
    except (OSError, ValueError):
        return {}


def _sc(args, runner=subprocess.run):
    return runner(["systemctl", "--user"] + args, capture_output=True, text=True, timeout=60, stdin=subprocess.DEVNULL)


def enabled_from_listing(text):
    """Pure. `list-unit-files --no-legend` text -> enabled watched timers."""
    out = []
    for ln in text.splitlines():
        p = ln.split()
        if len(p) >= 2 and WATCH_RE.match(p[0]) and p[1] in ("enabled", "enabled-runtime"):
            out.append(p[0])
    return sorted(out)


def read_states(runner=subprocess.run):
    """-> ({timer: ActiveState}, covered). covered = timers whose pause still has a PENDING restart (pause() recorded it).
    Raises RuntimeError when systemctl cannot be read (never 'all fine')."""
    r = _sc(["list-unit-files", "--type=timer", "--no-legend", "--no-pager"], runner)
    if r.returncode:
        raise RuntimeError("list-unit-files failed: %s" % (r.stderr or "")[:200])
    names = enabled_from_listing(r.stdout)
    states = {}
    for n in names:
        s = _sc(["is-active", n], runner)
        states[n] = (s.stdout or "").strip()
        if not states[n]:
            raise RuntimeError("is-active %s gave no answer (exit %s): %s" % (n, s.returncode, (s.stderr or "")[:120]))
    t = _sc(["list-timers", "--no-legend", "--no-pager", RESUME_PREFIX + "*"], runner)  # no --all: only timers that still elapse
    if t.returncode:
        raise RuntimeError("list-timers failed: %s" % (t.stderr or "")[:200])
    pending = {w for ln in (t.stdout or "").splitlines() for w in ln.split() if w.startswith(RESUME_PREFIX) and w.endswith(".timer")}
    rec = load_pauses()
    covered = {n for u in pending for n in rec.get(u, [])}
    return states, covered


def judge(states, covered=()):
    """Pure. -> {timer: reason} for enabled timers that are inactive and NOT covered by a pending restart.
    failed belongs to ops_watch. (A bool is accepted for old callers: True covers everything.)"""
    if covered is True:
        covered = set(states)
    elif not covered:
        covered = ()
    return {n: "inactive (stopped, not failed)" for n, s in states.items() if s == "inactive" and n not in covered}


def iso(t):
    return datetime.fromtimestamp(t, timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def check(now, filer, ids=None, states=None, resume_armed=None):
    """resume_armed: set of covered timers (or bool, see judge)."""
    """One pass. -> state dict ({} when quiet). filer(todo, conf) -> {name: None|error}; None files nothing."""
    import ops_watch as OW
    if states is None:
        states, resume_armed = read_states()
    bad = judge(states, resume_armed)
    tolerated = any(s == "inactive" for s in states.values())
    p = state_file()
    try:
        st = json.loads(p.read_text(encoding="utf-8")) if p.exists() else {}
    except (OSError, ValueError):
        st = None
    if not isinstance(st, dict):
        return {"_state": "UNREADABLE: %s; filing held" % p}
    conf = OW.alarm_conf(OW.load_rules())
    todo = []
    if not bad:
        if st and tolerated:
            return st      # inactive only under a pending restart: neither recovery nor a new alarm; keep the episode
        if st:
            if st.get("item") and filer:
                filer([{"note_only": True, "item": st["item"], "name": "note:timers",
                        "text": "timers_guard: watched timers are active again (%s)" % iso(now)}], conf)
            OW.atomic_json(p, {})
        return {}
    names = sorted(bad)
    if st.get("state") == "OPEN":
        st["last_seen"] = iso(now)
        st["timers"] = names
        OW.atomic_json(p, st)
        return st
    if not st:
        st = {"state": "PENDING", "since": iso(now), "tries": 0}
    ids_ = ids if ids is not None else __import__("deadman_check").known_ids()
    if st.get("name") in ids_:
        st.update(state="OPEN", item=st["name"])
        OW.atomic_json(p, st)
        return st
    if not st.get("name"):
        st["name"] = OW.mint_name("timers", set(ids_), "OPS_TIMERS_REVIVE")
    st["timers"] = names
    st["title"] = ("Timers stopped: %d enabled rm-/testq- timers inactive (%s)" % (len(names), ", ".join(names[:4])))[:160]
    OW.atomic_json(p, st)
    if filer:
        try:
            err = filer([{"aid": "timers", "name": st["name"], "title": st["title"]}], conf).get(st["name"])
        except Exception as e:  # noqa: BLE001
            err = "filer raised %s: %s" % (type(e).__name__, str(e)[:200])
        st["tries"] = st.get("tries", 0) + 1
        if err is None:
            st.update(state="OPEN", item=st["name"], error=None, filed=iso(now))
        else:
            st["error"] = err
    else:
        st["error"] = "filing off (run without --file-alarms)"
    OW.atomic_json(p, st)
    return st


def pause(names, hours, runner=subprocess.run):
    """Arm the restart FIRST (a transient timer-resume-* unit, outside the watched glob), then stop. -> {"unit","names"}."""
    names = list(names)
    if not names or not all(WATCH_RE.match(n) for n in names):
        raise ValueError("pause takes rm-*/testq-* .timer names, got %r" % names)
    if not (hours > 0 and hours < 24 * 366):
        raise ValueError("pause --hours must be > 0 and finite, got %r" % hours)
    secs = max(1, int(hours * 3600))
    unit = RESUME_PREFIX + time.strftime("%Y%m%d-%H%M%S")
    r = runner(["systemd-run", "--user", "--on-active=%ds" % secs, "--unit=" + unit, "--collect",
                "systemctl", "--user", "start"] + names, capture_output=True, text=True, timeout=60, stdin=subprocess.DEVNULL)
    if r.returncode:
        raise RuntimeError("could not arm the restart, NOTHING stopped: %s" % (r.stderr or "")[:200])
    from ops_watch import atomic_json
    rec = load_pauses()
    rec[unit + ".timer"] = names
    atomic_json(pauses_file(), rec)
    r = runner(["systemctl", "--user", "stop"] + names, capture_output=True, text=True, timeout=120, stdin=subprocess.DEVNULL)
    if r.returncode:
        raise RuntimeError("stop failed (restart %s stays armed): %s" % (unit, (r.stderr or "")[:200]))
    return {"unit": unit + ".timer", "names": names, "resume_in_s": secs}


UNIT = """# timer-guard: alarm on stopped rm-/testq- timers; deliberately NOT named rm-*/testq-* so a glob stop cannot take it. No AI.
[Unit]
Description=Alarm when enabled rm-/testq- timers are inactive

[Service]
Type=oneshot
ExecStart=/usr/bin/python3 {deploy}/src/RimMandrake/Utils/timers_guard.py run --file-alarms
TimeoutStartSec=300s
Nice=10
"""
TIMER = """[Unit]
Description=Timer guard every 10 min

[Timer]
OnCalendar=*:08/10
Persistent=true

[Install]
WantedBy=timers.target
"""


def install(apply, deploy):
    d = Path.home() / ".config/systemd/user"
    files = {d / (GUARD_NAME + ".service"): UNIT.format(deploy=deploy), d / (GUARD_NAME + ".timer"): TIMER}
    for p, body in files.items():
        old = p.read_text() if p.exists() else None
        print(("unchanged " if old == body else "write ") + str(p))
        if apply and old != body:
            p.parent.mkdir(parents=True, exist_ok=True)
            p.write_text(body)
    if not apply:
        print("plan only: pass --apply to write and enable")
        return 0
    for cmd in (["daemon-reload"], ["enable", "--now", GUARD_NAME + ".timer"]):
        r = _sc(cmd)
        print("systemctl --user %s: exit %d %s" % (" ".join(cmd), r.returncode, r.stderr.strip()))
        if r.returncode:
            return 1
    return 0


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    sub = ap.add_subparsers(dest="cmd", required=True)
    r = sub.add_parser("run")
    r.add_argument("--file-alarms", action="store_true")
    i = sub.add_parser("install")
    i.add_argument("--apply", action="store_true")
    i.add_argument("--deploy", default=os.environ.get("RM_PULSE_DEPLOY", "/mnt/d/ClaudeWork/rimmandrake/pulse-deploy"))
    pp = sub.add_parser("pause")
    pp.add_argument("--hours", type=float, required=True)
    pp.add_argument("--all", action="store_true")
    pp.add_argument("timers", nargs="*")
    a = ap.parse_args(argv)
    if a.cmd == "install":
        return install(a.apply, a.deploy)
    if a.cmd == "pause":
        names = a.timers or []
        if a.all:
            names = sorted(read_states()[0])
        res = pause(names, a.hours)
        print("paused %d timers; restart armed as %s in %ds" % (len(res["names"]), res["unit"], res["resume_in_s"]))
        return 0
    import ops_watch as OW
    st = check(time.time(), OW.real_filer if a.file_alarms else None)
    print("timers_guard: %s" % ("all watched timers active" if not st else json.dumps(st, sort_keys=True)[:400]))
    return 1 if "_state" in st else 0     # an unreadable state file must fail the unit, not hide as success


if __name__ == "__main__":
    sys.exit(main())
