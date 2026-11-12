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

A reading older than the commit while the commit itself is younger than max_age is NOT YET, not broken: the unit has
not had its cadence to run since (LIVECHECK_FIX_JUMPS_THE_GUN; fourteen fixes ended live_broken minutes after landing).
check() still returns a reason (the close gate refuses), but as a NotYet, which not_yet() tells apart so a caller waits.
Once the commit is older than max_age with no newer reading, the unit missed its cadence: that is broken.
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


DESIGN_ONLY_LINE = "once: design-only change, nothing runs"


def prose_only(paths):
    """True when every changed path is design prose (design/** or *.md outside infrastructure/state) and none needs a
    line: an alarm-prefixed item whose commit only edits prose has nothing to keep running. Pure."""
    if not paths or needs_line(paths):
        return False
    return all((p.startswith("design/") or (p.endswith(".md") and not p.startswith("infrastructure/state/")))
               for p in paths)


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


def _hook(name, settings, root=None):
    """None | why not. A whole-name match: `foo.py` is not wired by `block_foo.py`. The file must exist too, under the
    project the settings file sits in, or under `root` for a settings copy kept elsewhere (selftest_hook_promises_wired)."""
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
            home = root or os.path.dirname(os.path.dirname(path))     # the commands name it relative to the project
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


ISO_Z_RX = re.compile(r"\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}Z")
SLOT_RX = re.compile(r"^(\d{4}-\d{2}-\d{2}) (\d{2}:\d{2})$")


def _key_floor(key):
    """-> an epoch no later than the launch a `done` key records | None. A run-now key carries the request's UTC
    time, a slot key its local HH:MM, both made before the launch; any other key gives only the start of its local
    day. Never the END of the day: that dated a launch hours late (LIVE_ROLE_FIX_END_OF_DAY_ALIBI)."""
    m = ISO_Z_RX.search(key)
    if m:
        return datetime.strptime(m.group(0) + "+0000", "%Y-%m-%dT%H:%M:%SZ%z").timestamp()
    m = SLOT_RX.match(key)
    if m:
        return datetime.strptime("%s %s" % m.groups(), "%Y-%m-%d %H:%M").timestamp()
    return datetime.strptime(key[:10], "%Y-%m-%d").timestamp()


def _role_last(role, state_path=None):
    """-> the epoch of a role's newest launch | None. A run on record (`runs[].at`, written when it starts; kept two
    days) is the exact time; an older launch only in `done` is dated no later than it happened (_key_floor), so an
    early launch never proves a later commit and freshness never runs long."""
    path = state_path or os.path.join(os.environ.get("RM_DISPATCHER_STATE", "/mnt/d/ClaudeWork/rimmandrake/dispatcher"),
                                      "state.json")
    try:
        with open(path, encoding="utf-8") as f:
            rs = json.load(f)["roles"][role]
    except (OSError, ValueError, KeyError, TypeError):
        return None
    got = []
    for r in (rs.get("runs") if isinstance(rs, dict) else None) or []:
        if isinstance(r, dict) and isinstance(r.get("at"), (int, float)) and not isinstance(r.get("at"), bool):
            got.append(float(r["at"]))
    done = rs.get("done") if isinstance(rs, dict) else None
    for k, v in (done.items() if isinstance(done, dict) else ()):
        if v == "launch" and isinstance(k, str):
            try:
                got.append(_key_floor(k))
            except ValueError:
                continue
    return max(got) if got else None


class NotYet(str):
    """A reason that is a wait, not a failure: the reading predates the commit, and the unit's cadence since has not run out."""


def not_yet(why):
    return isinstance(why, NotYet)


def _predates(name, now, not_before, max_age_s):
    """-> the reason a reading older than the commit fails: NotYet while the commit is within one cadence (max_age)."""
    if now - not_before <= max_age_s:
        return NotYet("%s predates the commit it should prove; not yet: its next run is due within %d s of the commit"
                      % (name, max_age_s))
    return "%s predates the commit it should prove, and nothing newer came in the %d s since" % (name, max_age_s)


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
        if t < not_before:
            return _predates("role %s's last launch" % p["role"], now, not_before, p["max_age_s"])
        if now - t > p["max_age_s"]:
            return "role %s last launched %d s ago (max %d)" % (p["role"], now - t, p["max_age_s"])
        return None
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
    if mt < not_before:        # before the age test: a stale reading under a fresh commit is still a wait
        return _predates(name, now, not_before, p["max_age_s"])
    if now - mt > p["max_age_s"]:
        return "%s is %d s old (max %d)" % (name, now - mt, p["max_age_s"])
    return None


def can_see(runner=subprocess.run):
    """Can this process ask systemd at all? A blind sweep must hold, never read every unit as dead."""
    try:
        r = runner(["systemctl", "--user", "is-system-running"], capture_output=True, text=True, timeout=30,
                   stdin=subprocess.DEVNULL)
    except Exception:  # noqa: BLE001
        return False
    return (r.stdout or "").strip() in ("running", "degraded", "starting", "initializing", "maintenance")
