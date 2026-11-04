#!/usr/bin/env python3
"""The `live` line: what makes "done" mean "running" (parallel_review_2026-10-31/folded_into_operations.md section 5).

    unit=rm-foo.timer reading=<path> max_age=6h
    unit=rm-foo.timer max_age=6h          the reading is the timer's own last firing
    unit=rm-foo.path                      a .path unit enabled and armed (it fires only on demand, so no age)
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
# a reading may be written the owner's way (D:\\ClaudeWork\\...); from WSL that string names no file, so check() reads it
# under the drive's mount. OPS_MEMORY_VET_THEN_WIRE_AFTER_WATCH: a live memory.json read "absent" for three gens.
DRIVE_RX = re.compile(r"^([A-Za-z]):[\\/](.*)$")
MOUNT_ROOT = "/mnt"


def local_path(path):
    """-> `path` as this machine can open it: X:\\a\\b becomes <MOUNT_ROOT>/x/a/b; anything else is returned as is."""
    m = DRIVE_RX.match(path or "")
    if not m:
        return path
    return "%s/%s/%s" % (MOUNT_ROOT, m.group(1).lower(), m.group(2).replace("\\", "/"))
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
    if set(fields) == {"unit"}:
        if not fields["unit"].endswith(".path"):
            raise ValueError("only a .path unit is proved by being armed alone; %s needs max_age=" % fields["unit"])
        return {"kind": "unit", "unit": fields["unit"], "reading": None, "max_age_s": None}
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
                got = json.load(f)
            if got.get("disableAllHooks"):
                return "%s disables all hooks" % path
            text = json.dumps(got.get("hooks") or {})
        except (OSError, ValueError):
            continue
        readable += 1
        if rx.search(text):
            home = os.path.dirname(os.path.dirname(path))     # the commands name it relative to the project
            tokens = re.findall(r"[^\s\"']*/" + re.escape(name), text) or [os.path.join(".claude", "hooks", name)]
            found = [os.path.join(home, os.path.expandvars(os.path.expanduser(re.sub(r"^\$\{?CLAUDE_PROJECT_DIR(:-[^}]*)?\}?/", "", t)))) for t in tokens]
            if not any(os.path.exists(t) for t in found):
                return "hook %s is wired in %s but %s is absent" % (name, path, found[0])
            return None
    if not readable:
        return "settings unreadable: %s" % ", ".join(paths)
    return "hook %s is not wired in %s" % (name, ", ".join(paths))


METRONOME_TIMER = "rm-metronome.timer"
PHASES = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "Utils", "systemd",
                                       "metronome_phases.json"))


def metronome_owner(unit, phases=None):
    """-> the metronome phase that owns this old timer (metronome_phases.json `owns`), or None. At cutover the old
    timer is disabled on purpose (OPS_RESTART_UNSTICK_FOUNDRY_HDDT), so a promise on it is judged as the metronome.
    An unreadable table owns nothing: the old timer is judged as written."""
    if not unit.endswith(".timer"):
        return None
    try:
        with open(phases or PHASES, encoding="utf-8") as f:
            table = json.load(f)
        for name, ph in (table.get("phases") or {}).items():
            if unit in (ph.get("owns") or []):
                return name
    except (OSError, ValueError, AttributeError, TypeError):
        pass
    return None


def _timer_last(unit, runner):
    """-> epoch of the timer's last firing | None."""
    got = _systemctl_show(unit, "LastTriggerUSec", runner)
    return int(got) if got.isdigit() and int(got) else None    # --timestamp=unix: whole seconds


def _systemctl_show(unit, prop, runner):
    try:
        r = runner(["systemctl", "--user", "show", "--timestamp=unix", "-P", prop, unit], capture_output=True,
                   text=True, timeout=30, stdin=subprocess.DEVNULL)
        return (r.stdout or "").strip().lstrip("@")
    except Exception as e:  # noqa: BLE001
        return "error %s" % type(e).__name__


def _role_last(role, state_path=None):
    """-> the end of the day of a role's newest launch | None. Slot keys begin YYYY-MM-DD; what follows varies."""
    path = state_path or os.path.join(os.environ.get("RM_DISPATCHER_STATE", "/mnt/d/ClaudeWork/rimmandrake/dispatcher"),
                                      "state.json")
    try:
        with open(path, encoding="utf-8") as f:
            done = json.load(f)["roles"][role]["done"]
        days = [k[:10] for k, v in done.items() if v == "launch"]
        return max(datetime.strptime(k, "%Y-%m-%d").timestamp() + 86400 for k in days) if days else None
    except (OSError, ValueError, KeyError, TypeError, AttributeError):
        return None


def check(line, settings=None, now=None, not_before=0, runner=subprocess.run, state_path=None, phases=None):
    """-> None when the line holds, else why not. `settings` is one settings.json to look in, instead of the two
    defaults. A timer a metronome phase owns (`phases`, default the real table) is judged as rm-metronome.timer."""
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
        if now - t > p["max_age_s"]:
            return "role %s last launched %d s ago (max %d)" % (p["role"], now - t, p["max_age_s"])
        return "role %s's last launch predates the commit it should prove" % p["role"] if t < not_before else None
    unit, owner = p["unit"], metronome_owner(p["unit"], phases)
    if owner:          # disabled on purpose at cutover; the metronome runs its work now
        unit = METRONOME_TIMER
    for verb, want in (("is-enabled", "enabled"), ("is-active", "active")):
        got = _systemctl(verb, unit, runner)
        if got != want:
            via = " (its phase %s owns %s)" % (owner, p["unit"]) if owner else ""
            return "%s: %s says %r, wanted %r%s" % (unit, verb, got, want, via)
    if p["max_age_s"] is None:   # a .path unit: enabled and armed is the promise; it fires only when asked
        return None
    if p["reading"]:
        try:
            mt = os.path.getmtime(local_path(p["reading"]))
        except OSError:
            return "reading %s is absent" % p["reading"]
        name = "reading %s" % p["reading"]
    else:
        mt = _timer_last(unit, runner)
        if mt is None:
            return "%s has no last firing" % unit
        name = "last firing of %s" % unit
    if mt - now > 300:
        return "%s is dated %d s in the future" % (name, mt - now)
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
