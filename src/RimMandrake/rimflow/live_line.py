#!/usr/bin/env python3
"""The `live` line: what makes "done" mean "running" (parallel_review_2026-10-31/folded_into_operations.md section 5).

    unit=rm-foo.timer reading=<path> max_age=6h
    unit=rm-foo.timer max_age=6h          the reading is the timer's own last firing
    hook=block_foo.py
    role=Operations max_age=2d            a Dispatcher role's last launch
    once: one-off data repair

parse() and needs_line() are pure. check() asks systemd and the disk; a reading must be younger than max_age AND newer
than the commit it proves (`not_before`), or an old reading would prove a new commit. Shared by relentless.py and by
LIVE_PROOF_ENFORCE_DONE_MEANS_RUNNING's `close --live`.
"""
import json
import os
import re
import subprocess
import time
from datetime import datetime

AGE_RX = re.compile(r"^(\d+)([smhd])$")
AGE_S = {"s": 1, "m": 60, "h": 3600, "d": 86400}
# a change to one of these does nothing until something runs it, so its close must say what runs it
NEEDS_LIVE_RX = re.compile(r"(^|/)(\.claude/hooks/|.*systemd/.*\.(service|timer)$|dispatcher_schedule\.json$|"
                           r"ops_watch_rules\.json$)")


def parse(line):
    """-> {"kind": "unit", "unit", "reading", "max_age_s"} | {"kind": "hook", "hook"} | {"kind": "once", "why"}.
    Raises ValueError on anything else."""
    s = (line or "").strip()
    if s.startswith("once:"):
        why = s[5:].strip()
        if not why:
            raise ValueError("once: needs a reason")
        return {"kind": "once", "why": why}
    fields = dict(p.split("=", 1) for p in s.split() if "=" in p)
    if len(fields) != len(s.split()) or not fields:
        raise ValueError("not a live line: %r" % line)
    if not all(fields.values()):
        raise ValueError("empty value: %r" % line)
    if set(fields) == {"hook"}:
        return {"kind": "hook", "hook": fields["hook"]}
    if set(fields) in ({"unit", "reading", "max_age"}, {"unit", "max_age"}, {"role", "max_age"}):
        m = AGE_RX.match(fields["max_age"])
        if not m:
            raise ValueError("max_age must look like 6h, got %r" % fields["max_age"])
        age = int(m.group(1)) * AGE_S[m.group(2)]
        if "role" in fields:
            return {"kind": "role", "role": fields["role"], "max_age_s": age}
        if "reading" not in fields and not fields["unit"].endswith(".timer"):
            raise ValueError("only a .timer is its own reading; %s needs reading=<path>" % fields["unit"])
        return {"kind": "unit", "unit": fields["unit"], "reading": fields.get("reading"), "max_age_s": age}
    raise ValueError("not a live line: %r" % line)


def needs_line(paths):
    """-> the changed paths that oblige a live line. Pure."""
    return [p for p in paths if NEEDS_LIVE_RX.search(p)]


def _systemctl(verb, unit, runner):
    try:
        r = runner(["systemctl", "--user", verb, unit], capture_output=True, text=True, timeout=30,
                   stdin=subprocess.DEVNULL)
        return (r.stdout or "").strip()
    except Exception as e:  # noqa: BLE001
        return "error %s" % type(e).__name__


def settings_paths():
    """Hooks are wired in the user's settings or in the settings of the clone this runs from."""
    here = os.path.dirname(os.path.abspath(__file__))
    return [os.path.expanduser("~/.claude/settings.json"),
            os.path.normpath(os.path.join(here, "..", "..", "..", ".claude", "settings.json"))]


def _hook(name, settings):
    """None | why not. A whole-name match: `foo.py` is not wired by `block_foo.py`. The file must exist too."""
    paths = [settings] if settings else settings_paths()
    rx = re.compile(r"(?<![\w.-])%s(?![\w.-])" % re.escape(name))
    readable = 0
    for path in paths:
        try:
            with open(path, encoding="utf-8") as f:
                text = json.dumps(json.load(f).get("hooks") or {})
        except (OSError, ValueError):
            continue
        readable += 1
        if rx.search(text):
            target = os.path.join(os.path.dirname(os.path.dirname(path)), ".claude", "hooks", name)
            if ".claude/hooks/" + name in text and not os.path.exists(target):
                return "hook %s is wired in %s but %s is absent" % (name, path, target)
            return None
    if not readable:
        return "settings unreadable: %s" % ", ".join(paths)
    return "hook %s is not wired in %s" % (name, ", ".join(paths))


def _timer_last(unit, runner):
    """-> epoch of the timer's last firing | None."""
    got = _systemctl_show(unit, "LastTriggerUSec", runner)
    return int(got) / 1e6 if got.isdigit() and int(got) else None


def _systemctl_show(unit, prop, runner):
    try:
        r = runner(["systemctl", "--user", "show", "--timestamp=unix", "-P", prop, unit], capture_output=True,
                   text=True, timeout=30, stdin=subprocess.DEVNULL)
        return (r.stdout or "").strip().lstrip("@")
    except Exception as e:  # noqa: BLE001
        return "error %s" % type(e).__name__


def _role_last(role, state_path=None):
    """-> epoch of a Dispatcher role's newest launch | None. Slot keys are 'YYYY-MM-DD HH:MM'."""
    path = state_path or os.path.join(os.environ.get("RM_DISPATCHER_STATE", "/mnt/d/ClaudeWork/rimmandrake/dispatcher"),
                                      "state.json")
    try:
        with open(path, encoding="utf-8") as f:
            done = json.load(f)["roles"][role]["done"]
        slots = [k for k, v in done.items() if v == "launch"]
        return max(datetime.strptime(k, "%Y-%m-%d %H:%M").timestamp() for k in slots) if slots else None
    except (OSError, ValueError, KeyError, TypeError, AttributeError):
        return None


def check(line, settings=None, now=None, not_before=0, runner=subprocess.run, state_path=None):
    """-> None when the line holds, else why not. `settings` is one settings.json to look in, instead of the two
    defaults."""
    try:
        p = parse(line)
    except ValueError as e:
        return str(e)
    now = time.time() if now is None else now
    if p["kind"] == "once":
        return None
    if p["kind"] == "hook":
        return _hook(p["hook"], settings)
    if p["kind"] == "role":
        t = _role_last(p["role"], state_path)
        if t is None:
            return "role %s has no recorded launch" % p["role"]
        return "role %s last launched %d s ago (max %d)" % (p["role"], now - t, p["max_age_s"]) \
            if now - t > p["max_age_s"] else None
    for verb, want in (("is-enabled", "enabled"), ("is-active", "active")):
        got = _systemctl(verb, p["unit"], runner)
        if got != want:
            return "%s: %s says %r, wanted %r" % (p["unit"], verb, got, want)
    if p["reading"]:
        try:
            mt = os.path.getmtime(p["reading"])
        except OSError:
            return "reading %s is absent" % p["reading"]
        name = "reading %s" % p["reading"]
    else:
        mt = _timer_last(p["unit"], runner)
        if mt is None:
            return "%s has no last firing" % p["unit"]
        name = "last firing of %s" % p["unit"]
    if now - mt > p["max_age_s"]:
        return "%s is %d s old (max %d)" % (name, now - mt, p["max_age_s"])
    if mt < not_before:
        return "%s predates the commit it should prove" % name
    return None


def can_see(runner=subprocess.run):
    """Can this process ask systemd at all? A blind sweep must hold, never read every unit as dead."""
    try:
        r = runner(["systemctl", "--user", "is-system-running"], capture_output=True, text=True, timeout=30,
                   stdin=subprocess.DEVNULL)
    except Exception:  # noqa: BLE001
        return False
    return (r.stdout or "").strip() in ("running", "degraded", "starting", "initializing", "maintenance")
