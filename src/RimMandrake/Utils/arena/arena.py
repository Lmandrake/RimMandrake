#!/usr/bin/env python3
"""arena.py - the switch: ONE architecture live at a time (ARENA_SWITCH_BUILD_ONE_ARM_LIVE_ONLY).

design/RimMandrake/architecture_switch_harness_2026-10-29.md section 2, testpilot_merged_2026-10-29.md 6.3 (step 7).

    arena.py mode                 print the mode in arm.toml (exit 16 if arm.toml is unreadable)
    arena.py switch <mode>        lock, STOP file, wait idle (<= 90 min), clone-state check, stop the old targets, disable
                                  every other arm's member units, release both bridges, restore the owner's mod list,
                                  `switch` event, start the new targets, who.  --force restarts an already-live mode;
                                  --allow-dirty-untracked accepts uncommitted/untracked files (recorded in the event)
    arena.py who                  the checks; exit code is a bitmask: a=1 b=2 c=4 d=8 e=32 f=64 (16 = arm.toml unreadable)
    arena.py prepush --arm A      the pre-push hook body (refs on stdin): refuse (exit 10) AND alarm anything not allowed
    arena.py ops-watch            one number for ops_watch's ARENA_TWO_LIVE rule (0 = fine)
    arena.py trial-runner         ExecStart of rm-arena-replay.service (the replay driving loop is OWED; it exits 3)

arm.toml lives OUTSIDE git (`$ARENA_ARM_TOML`, default `<arena root>/arm.toml`); the committed template is
infrastructure/arena/arm.toml.template. MODES: the arms v3 v3c ralph_a ralph_c trio, `production` (the real seats; its
`[production] scope` names the production clones bench/foundry that are live) and `trial` (design 2.1: v3 stays live
as the control - rm-arm-v3.target - and rm-arm-trial.target runs the replay runner rm-arena-replay.service; the
[trial] lanes carry steve_lane / archmagi_lane, and replay_arms are replayed. v3 and trial are the ONE pair of targets
that do not conflict: every other pair Conflicts= both ways).

THE CHECKS (`who`). a: the active rm-arm targets are exactly the mode's, and no member unit of another arm's target is
active or enabled (an enabled member timer would start at boot beside the live target). b: no process cwd inside a
stopped arm's clone. c: every bridge lock (per lane, from the ledger, plus the shared cross-clone file) is tagged
`arena <arm>` with a live arm (in trial: the lane's own arm); an untagged lock is UNKNOWN and fails in an arena or trial
mode. d: no stopped arm wrote an event or pushed since the switch. e: every governed clone's EFFECTIVE hooks dir
(`git rev-parse --git-path hooks`, i.e. core.hooksPath when set) is the arena hooks dir, its pre-push is the rendered
arena hook, and every hook of the dir it chains has its wrapper. f: no STOP file sits on a live arm while no switch
holds the lock, and no live arm reports `idle` from a status older than 6 h.

HOOKS. bench and foundry set core.hooksPath=infrastructure/githooks, so .git/hooks is never run there. The installer
therefore writes <git-common-dir>/arena-hooks/, records the previous effective hooks dir in arena-hooks/CHAIN_FROM,
writes a wrapper for every hook found there (owner hooks are CHAINED, never overwritten) and points the clone's local
core.hooksPath at arena-hooks. The pre-push runs the arena check FIRST and only then the chained pre-push.

SERVER_SIDE_REQUIREMENTS (what this file can NOT do; an owner decision). A client hook is advisory: `git push
--no-verify` skips it, so does any client that ignores hooks, and a same-user process can repoint core.hooksPath or edit
arm.toml (and a stopped arm could re-enable itself that way - a same-user residual that `who` (e) reports but cannot
prevent). github.com runs no pre-receive hooks; the only unbypassable form is server side: per-arm credentials (one
deploy key / fine-grained token per arm clone) plus GitHub rulesets restricting refs/heads/arena/<arm>/* to that actor
and the production branches to the production credentials. Nothing here claims to be unbypassable.

Every side effect goes through an injectable object (Deps, Systemctl, the signer, the alarm sink) so the selftest
rehearses a switch with a fake systemctl and never touches the real user manager, the real units or the real seats.
Nothing in this file starts systemd, dbus or a private manager; the only systemctl is the one it is handed. A
production rehearsal in a throwaway user session is possible only with the fake systemctl (a real manager is out of
bounds for agents).

THE SIGNER. A `switch` event is signed by arena_eventlog (arena.py is in its ENTRYPOINTS). A switch whose event
cannot be signed STOPS before starting the new target: nothing is live rather than an unrecorded switch.
"""
from __future__ import annotations

import argparse
import contextlib
import datetime as dt
import fcntl
import json
import os
import re
import signal
import subprocess
import sys
import tempfile
import time
import tomllib
from pathlib import Path

HERE = Path(__file__).resolve().parent
UTILS = HERE.parent
REPO = UTILS.parent.parent.parent
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(UTILS))
import arena_tasks as A  # noqa: E402

ARMS = ("v3", "v3c", "ralph_a", "ralph_c", "trio", "production")
TRIAL = "trial"
MODES = ARMS + (TRIAL,)
TARGET_ARMS = ARMS + (TRIAL,)                    # every rm-arm-<x>.target (trial's target runs the replay runner)
COMPAT = (frozenset(("v3", TRIAL)),)             # the only pair of targets that may be live together
PRODUCTION_ARMS = ("v3", "production")          # these two run in the production clones
PRODUCTION_MODES = ("v3", "production", "trial")  # modes in which the production clones are live
PROD_CLONES = ("bench", "foundry")
LANES = {"steve": "stevedesktop", "archmagi": "archmagi"}
HOST_LANE = {h: lane for lane, h in LANES.items()}
LANE_KEYS = {"steve": "steve_lane", "archmagi": "archmagi_lane"}
REPLAY_UNIT = "rm-arena-replay.service"
DEFAULT_UNITS = {TRIAL: [REPLAY_UNIT]}
TRIAL_DEFAULTS = {"steve_lane": "trio", "archmagi_lane": "ralph_c", "replay_arms": ["ralph_a", "trio", "v3", "v3c"]}
IDLE_WAIT_S = 90 * 60
IDLE_FRESH_S = 15 * 60                           # an `idle` status older than this does not count as idle now
STALE_IDLE_S = 6 * 3600                          # who (f): a live arm idle for longer is silently paused
UNIT_PREFIX = "rm-arm-"
TEMPLATES = REPO / "infrastructure" / "arena"
BITS = (("a", 1), ("b", 2), ("c", 4), ("d", 8), ("e", 32), ("f", 64))
EXIT_CONFIG = 16                                 # arm.toml unreadable (who/mode/ops-watch)
PREPUSH_REFUSED = 10                             # prepush's refusal code; anything else nonzero = the hook crashed
HOOKS_DIRNAME = "arena-hooks"
ALLOWABLE_DIRT = ("dirty", "untracked")          # what --allow-dirty-untracked may override
GIT_HOOKS = ("applypatch-msg", "pre-applypatch", "post-applypatch", "pre-commit", "pre-merge-commit",
             "prepare-commit-msg", "commit-msg", "post-commit", "pre-rebase", "post-checkout", "post-merge",
             "pre-push", "pre-receive", "update", "proc-receive", "post-receive", "post-update",
             "reference-transaction", "push-to-checkout", "pre-auto-gc", "post-rewrite", "sendemail-validate",
             "fsmonitor-watchman", "p4-changelist", "p4-prepare-changelist", "p4-post-changelist", "p4-pre-submit",
             "post-index-change")


class SwitchError(Exception):
    pass


class Refused(SwitchError):
    """A refusal that leaves the system safe (nothing newly started, STOP files we wrote removed)."""


class Interrupted(SwitchError):
    """SIGTERM during a switch (raised by the handler main() installs)."""


class UnitStateUnknown(SwitchError):
    """systemctl answered is-active/is-enabled with something that is neither on nor off (error, bus down)."""


class RemoteUnreachable(SwitchError):
    """The authoritative remote could not be read: an unpushed verdict would rest on a stale cache."""


ON_WORDS = ("active", "reloading", "activating", "deactivating", "refreshing")
OFF_WORDS = ("inactive", "failed", "dead", "maintenance")
NOT_ENABLED_WORDS = ("disabled", "static", "indirect", "generated", "transient", "masked", "masked-runtime", "linked",
                     "linked-runtime", "alias", "not-found", "bad")


def target_name(arm: str) -> str:
    return "%s%s.target" % (UNIT_PREFIX, arm)


def sh_quote(s: str) -> str:
    """POSIX single-quote: nothing inside is expanded ($(...), backticks, $VAR, quotes are all literal)."""
    return "'" + str(s).replace("'", "'\\''") + "'"


# ------------------------------------------------------------------ config (arm.toml, outside git)

def arm_toml_path(root: Path | None = None) -> Path:
    env = os.environ.get("ARENA_ARM_TOML", "").strip()
    if env:
        return Path(env)
    return (Path(root) if root else A.arena_root()) / "arm.toml"


def alarm_path(root: Path | None = None) -> Path:
    env = os.environ.get("ARENA_ALARM_FILE", "").strip()
    if env:
        return Path(env)
    return (Path(root) if root else A.arena_root()) / "alarms" / "arena.jsonl"


def clone_root() -> Path:
    return Path(os.environ.get("ARENA_CLONES", "/home/mandrake/rm/arena"))


def load_config(path: Path | None = None) -> dict:
    """Parse arm.toml (tomllib, validated). Raises SwitchError on anything unreadable: callers fail CLOSED."""
    p = Path(path) if path else arm_toml_path()
    try:
        raw = tomllib.loads(p.read_text(encoding="utf-8"))
    except (OSError, UnicodeDecodeError, tomllib.TOMLDecodeError) as e:
        raise SwitchError("arm.toml %s unreadable: %s" % (p, e))
    mode = raw.get("mode")
    if mode not in MODES:
        raise SwitchError("arm.toml mode %r is not one of %s" % (mode, MODES))
    prod = raw.get("production") or {}
    scope = prod.get("scope", list(PROD_CLONES))
    if (not isinstance(scope, list) or not scope or any(s not in PROD_CLONES for s in scope)
            or len(set(scope)) != len(scope)):
        raise SwitchError("[production] scope must be a non-empty list of %s (got %r)" % (PROD_CLONES, scope))
    arms_raw = raw.get("arms") or {}
    if not isinstance(arms_raw, dict):
        raise SwitchError("[arms] must be a table")
    bad = [a for a in arms_raw if a not in TARGET_ARMS]
    if bad:
        raise SwitchError("[arms.%s] is not a known arm %s" % (bad[0], TARGET_ARMS))
    units = {}
    for a in TARGET_ARMS:
        u = (arms_raw.get(a) or {}).get("units", DEFAULT_UNITS.get(a, []))
        if not isinstance(u, list) or any(not isinstance(x, str) or not re.fullmatch(r"[\w@.:\-\\]+", x) for x in u):
            raise SwitchError("[arms.%s] units must be a list of unit names (got %r)" % (a, u))
        units[a] = list(u)
    trial = dict(TRIAL_DEFAULTS, **(raw.get("trial") or {}))
    lane_ok = tuple(a for a in ARMS if a not in PRODUCTION_ARMS)
    for k in LANE_KEYS.values():
        if trial.get(k) not in lane_ok:
            raise SwitchError("[trial] %s must be one of %s (got %r)" % (k, lane_ok, trial.get(k)))
    ra = trial.get("replay_arms")
    if not isinstance(ra, list) or any(a not in ARMS for a in ra):
        raise SwitchError("[trial] replay_arms must be a list of %s (got %r)" % (ARMS, ra))
    live = {}
    for a in TARGET_ARMS:
        lv = (arms_raw.get(a) or {}).get("live", {})
        if not isinstance(lv, dict) or any(not isinstance(v, list) or any(
                not isinstance(x, str) or not re.fullmatch(r"[\w@.:\-\\*?\[\]]+", x) for x in v) for v in lv.values()):
            raise SwitchError("[arms.%s] live must be a table clone -> list of unit names/globs (got %r)" % (a, lv))
        live[a] = {k: list(v) for k, v in lv.items()}
    plive = live.get("production") or {}
    if any(c not in PROD_CLONES for c in plive):
        raise SwitchError("[arms.production] live keys must be production clones %s (got %s)" % (PROD_CLONES, sorted(plive)))
    if any(not plive.get(c) for c in scope):
        raise SwitchError("[arms.production] live is empty for in-scope clone(s) %s: 'production live' would check "
                          "nothing (item 3; see infrastructure/arena/arm.toml.template)"
                          % [c for c in scope if not plive.get(c)])
    clones = raw.get("clones") or {}
    return {"mode": mode, "scope": list(scope), "path": str(p), "trial": trial,
            "clones": {k: str(v) for k, v in clones.items()}, "units": units, "live": live}


def set_mode(path: Path, mode: str):
    """Rewrite only the top-level `mode = ...` line, atomically; re-parse the result before keeping it."""
    if mode not in MODES:
        raise SwitchError("unknown mode %r" % mode)
    p = Path(path)
    txt = p.read_text(encoding="utf-8")
    lines = txt.split("\n")
    for i, ln in enumerate(lines):
        if ln.startswith("["):
            break
        if re.match(r"^mode\s*=", ln):
            lines[i] = 'mode = "%s"' % mode
            break
    else:
        lines.insert(0, 'mode = "%s"' % mode)
    fd, tmp = tempfile.mkstemp(dir=str(p.parent), prefix=".arm.toml.")
    with os.fdopen(fd, "w", encoding="utf-8") as fh:
        fh.write("\n".join(lines))
    os.replace(tmp, p)
    if load_config(p)["mode"] != mode:
        raise SwitchError("arm.toml did not take mode %s" % mode)


def mode_targets(cfg: dict) -> list[str]:
    """The arms whose rm-arm target is live in this mode (trial: v3 + trial)."""
    return ["v3", TRIAL] if cfg["mode"] == TRIAL else [cfg["mode"]]


def lane_arms(cfg: dict) -> dict[str, str]:
    """trial only: lane -> the arm that lane carries."""
    if cfg["mode"] != TRIAL:
        return {}
    return {lane: cfg["trial"][k] for lane, k in LANE_KEYS.items()}


def live_arms(cfg: dict) -> set[str]:
    """Arms allowed to run, push and write events: the mode's arm; in trial v3 + the lane arms + the replay arms."""
    if cfg["mode"] != TRIAL:
        return {cfg["mode"]}
    return {"v3"} | set(lane_arms(cfg).values()) | set(cfg["trial"].get("replay_arms") or [])


active_arms = live_arms        # the old name


def expected_targets(cfg: dict) -> list[str]:
    return sorted(target_name(a) for a in mode_targets(cfg))


def clone_path(cfg: dict, name: str) -> Path:
    if name in cfg["clones"]:
        return Path(cfg["clones"][name])
    if name in PROD_CLONES:
        return Path("/home/mandrake/rm") / name
    return clone_root() / name


def arm_clones(cfg: dict, arm: str) -> list[Path]:
    if arm == TRIAL:
        return []
    if arm in PRODUCTION_ARMS:
        return [clone_path(cfg, c) for c in PROD_CLONES]
    return [clone_path(cfg, arm)]


def live_clones(cfg: dict) -> set[Path]:
    out = set()
    for a in live_arms(cfg):
        if a in PRODUCTION_ARMS:
            out |= {clone_path(cfg, c) for c in cfg["scope"]}
        else:
            out.add(clone_path(cfg, a))
    return out


def stopped_clones(cfg: dict) -> dict[Path, str]:
    """clone path -> the (stopped) arm that owns it. A clone that a live arm uses is never listed."""
    live = live_clones(cfg)
    out = {}
    for a in ARMS:
        for c in arm_clones(cfg, a):
            if c not in live:
                out.setdefault(c, a)
    return out


def governed_clones(cfg: dict) -> list[tuple[Path, str, str]]:
    """(clone path, hook arm, clone name) for every clone the arena hook guards."""
    out = [(clone_path(cfg, a), a, a) for a in ARMS if a not in PRODUCTION_ARMS]
    out += [(clone_path(cfg, c), "production", c) for c in PROD_CLONES]
    return out


def _inside(child, parent) -> bool:
    c, q = os.path.realpath(child), os.path.realpath(parent)
    return c == q or c.startswith(q.rstrip("/") + "/")


# ------------------------------------------------------------------ systemctl (injected; never the real one in tests)

class Systemctl:
    """A thin runner over `systemctl --user`. `cmd` is the argv prefix; the selftest passes the fake shim. This class
    only ever starts ONE unit per call (a transaction of two conflicting targets is what systemd refuses)."""

    def __init__(self, cmd=None):
        if not cmd and os.environ.get("ARENA_SYSTEMCTL_JSON"):     # selftests / rehearsal: a fake, never the real one
            cmd = json.loads(os.environ["ARENA_SYSTEMCTL_JSON"])
        self.cmd = list(cmd) if cmd else ["systemctl", "--user"]

    def run(self, *args, timeout=120):
        r = subprocess.run(self.cmd + list(args), capture_output=True, text=True, timeout=timeout)
        return r.returncode, (r.stdout + r.stderr)

    def active_targets(self) -> list[str]:
        rc, out = self.run("list-units", "--plain", "--no-legend", "--all", "%s*.target" % UNIT_PREFIX)
        if rc != 0:
            raise SwitchError("systemctl list-units failed (rc %d): %s" % (rc, out.strip()[:200]))
        act = []
        for ln in out.splitlines():
            f = ln.split()
            if len(f) >= 3 and f[0].startswith(UNIT_PREFIX) and f[2] == "active":
                act.append(f[0])
        return sorted(act)

    def is_active(self, unit) -> bool:
        """True for active (and the transitional on-states), False for inactive/failed. Anything else - a bus error,
        an empty answer, a word systemd does not use - is NOT 'inactive': it raises UnitStateUnknown."""
        rc, out = self.run("is-active", unit)
        w = (out.split() or [""])[0]
        if w in ON_WORDS:
            return True
        if w in OFF_WORDS:
            return False
        raise UnitStateUnknown("is-active %s: rc %d, %r" % (unit, rc, out.strip()[:120]))

    def is_enabled(self, unit) -> bool:
        """enabled / enabled-runtime: the unit starts at boot by itself (static/disabled/not-found do not). An answer
        that is none of systemd's words (bus error, empty) raises UnitStateUnknown instead of reading as 'disabled'."""
        rc, out = self.run("is-enabled", unit)
        w = (out.split() or [""])[0]
        if w in ("enabled", "enabled-runtime"):
            return True
        if w in NOT_ENABLED_WORDS:
            return False
        raise UnitStateUnknown("is-enabled %s: rc %d, %r" % (unit, rc, out.strip()[:120]))

    def active_matching(self, pattern: str) -> list[str]:
        """Active units matching a glob (transient seat scopes included). A reader failure raises."""
        rc, out = self.run("list-units", "--plain", "--no-legend", "--all", pattern)
        if rc != 0:
            raise SwitchError("systemctl list-units %s failed (rc %d): %s" % (pattern, rc, out.strip()[:200]))
        return sorted(f[0] for f in (ln.split() for ln in out.splitlines()) if len(f) >= 3 and f[2] == "active")

    def stop(self, unit):
        rc, out = self.run("stop", unit, timeout=300)
        if rc != 0:
            raise SwitchError("systemctl stop %s failed (rc %d): %s" % (unit, rc, out.strip()[:200]))

    def disable(self, unit):
        rc, out = self.run("disable", unit, timeout=120)
        if rc != 0:
            raise SwitchError("systemctl disable %s failed (rc %d): %s" % (unit, rc, out.strip()[:200]))

    def start(self, unit):
        rc, out = self.run("start", unit, timeout=300)
        if rc != 0:
            raise SwitchError("systemctl start %s failed (rc %d): %s" % (unit, rc, out.strip()[:200]))


def foreign_members(cfg: dict, sc: Systemctl) -> list[dict]:
    """Member units of targets that are NOT live in this mode which are active or enabled. A unit whose state cannot
    be read (UnitStateUnknown) is listed with unknown=True and counted as BOTH active and enabled (fail closed: who
    flags it, switch disables and stops it). Any other reader error raises."""
    live = set(mode_targets(cfg))
    out = []
    for a in TARGET_ARMS:
        if a in live:
            continue
        for u in cfg["units"].get(a, []):
            unknown = []
            try:
                on = sc.is_active(u)
            except UnitStateUnknown as e:
                on, unknown = True, unknown + [str(e)]
            try:
                en = sc.is_enabled(u)
            except UnitStateUnknown as e:
                en, unknown = True, unknown + [str(e)]
            if on or en:
                rec = {"unit": u, "arm": a, "active": on, "enabled": en}
                if unknown:
                    rec.update(unknown=True, why=unknown)
                out.append(rec)
    return out


def missing_live(cfg: dict, sc: Systemctl) -> list[str]:
    """Item 3: what the mode's `live` set says must be running and is not. Each entry of [arms.<arm>] live (per clone,
    only the clones in [production] scope for production) is a unit name (must be active) or a glob (at least one
    active unit must match: the seat scopes). A reader failure raises (check a fails)."""
    out = []
    for a in mode_targets(cfg):
        for clone, names in sorted((cfg.get("live") or {}).get(a, {}).items()):
            if a == "production" and clone not in cfg["scope"]:
                continue
            for n in names:
                if any(ch in n for ch in "*?["):
                    if not sc.active_matching(n):
                        out.append("%s (%s): no active unit matches %s" % (a, clone, n))
                else:
                    try:
                        on = sc.is_active(n)
                    except UnitStateUnknown as e:
                        out.append("%s (%s): %s state unknown: %s" % (a, clone, n, e))
                        continue
                    if not on:
                        out.append("%s (%s): %s is not active" % (a, clone, n))
    return out


# ------------------------------------------------------------------ pure graph check of the unit templates

def parse_unit(text: str) -> dict:
    d, sec = {}, None
    for raw in text.splitlines():
        ln = raw.strip()
        if not ln or ln[0] in "#;":
            continue
        m = re.match(r"^\[(\w+)\]$", ln)
        if m:
            sec = m.group(1)
            d.setdefault(sec, {})
            continue
        if "=" in ln and sec:
            k, v = ln.split("=", 1)
            if not v.strip():
                d[sec][k.strip()] = []               # systemd: an empty assignment resets the list
            else:
                d[sec].setdefault(k.strip(), []).extend(v.split())
    return d


def unit_values(u: dict, key: str, sec="Unit") -> set[str]:
    return set((u.get(sec) or {}).get(key, []))


def compatible(a: str, b: str) -> bool:
    return frozenset((a, b)) in COMPAT


def check_graph(units: dict[str, str], arms=TARGET_ARMS) -> list[str]:
    """units: unit name -> file text (targets and member drop-ins by their unit name). Returns problems; [] = sound.
    Checks: every rm-arm target exists; Conflicts= is mutual between every pair of targets except the COMPAT pair
    (v3 + trial), which must NOT conflict; every non-target unit carries PartOf= exactly one existing target."""
    parsed = {n: parse_unit(t) for n, t in units.items()}
    targets = {a: target_name(a) for a in arms}
    probs = []
    for a, t in targets.items():
        if t not in parsed:
            probs.append("missing target unit %s" % t)
    for a, t in targets.items():
        if t not in parsed:
            continue
        c = unit_values(parsed[t], "Conflicts")
        if t in c:
            probs.append("%s conflicts with itself" % t)
        for b, u in targets.items():
            if b == a:
                continue
            if compatible(a, b):
                if u in c:
                    probs.append("%s must NOT conflict with %s (they run together in trial)" % (t, u))
                continue
            if u not in c:
                probs.append("%s lacks Conflicts=%s" % (t, u))
            if u in parsed and t not in unit_values(parsed[u], "Conflicts"):
                probs.append("Conflicts= not mutual: %s -> %s but not back" % (t, u))
    for n, u in parsed.items():
        if n in targets.values():
            continue
        parts = unit_values(u, "PartOf")
        tg = [p for p in parts if p.startswith(UNIT_PREFIX)]
        if len(tg) != 1:
            probs.append("%s must be PartOf= exactly one rm-arm target (has %s)" % (n, sorted(tg)))
        elif tg[0] not in targets.values():
            probs.append("%s is PartOf= unknown target %s" % (n, tg[0]))
    return sorted(set(probs))


def read_unit_dir(d: Path) -> dict[str, str]:
    """Read targets (`rm-arm-*.target`), the arena's own unit files (`rm-arena-*`) and drop-in files
    (`<unit>.d/*.conf`, merged onto the unit by name) from a dir."""
    out = {}
    for f in sorted(Path(d).glob("%s*.target" % UNIT_PREFIX)):
        out[f.name] = f.read_text(encoding="utf-8")
    for f in sorted(Path(d).glob("rm-arena-*.service")):
        out[f.name] = f.read_text(encoding="utf-8") + "\n"
    for dd in sorted(Path(d).glob("*.d")):
        unit = dd.name[:-2]
        if unit.startswith(UNIT_PREFIX):
            continue
        txt = "".join(c.read_text(encoding="utf-8") + "\n" for c in sorted(dd.glob("*.conf")))
        if txt.strip():
            out[unit] = out.get(unit, "") + txt
    return out


# ------------------------------------------------------------------ templates (rendering only; installer writes)

def gate_name(arm: str) -> str:
    """Item 2: the arm's gate unit. Started by the target (Wants=), it writes the runtime marker; every member's
    drop-in has ConditionPathExists= on that marker, so a member started DIRECTLY while its target is stopped is
    skipped by systemd itself (PartOf= alone only propagates stop/restart, never refuses a start)."""
    return "rm-arena-gate-%s.service" % arm


def marker_rel(arm: str) -> str:
    """The marker path under the user runtime dir (%t in a user unit = $XDG_RUNTIME_DIR)."""
    return "rm-arena/live.%s" % arm


def runtime_dir() -> Path:
    return Path(os.environ.get("XDG_RUNTIME_DIR") or "/run/user/%d" % os.getuid())


def target_wants(units: list[str]) -> list[str]:
    """A target Wants= its members, except a .service whose .timer is also a member (the timer starts it)."""
    s = set(units)
    return [u for u in units if not (u.endswith(".service") and u[:-len(".service")] + ".timer" in s)]


def render_target(arm: str, cfg: dict, arms=TARGET_ARMS) -> str:
    name = "rm-arm-production.target.tmpl" if arm == "production" else "rm-arm.target.tmpl"
    t = (TEMPLATES / "systemd" / name).read_text(encoding="utf-8")
    others = " ".join(target_name(b) for b in arms if b != arm and not compatible(arm, b))
    wants = " ".join([gate_name(arm)] + target_wants(cfg["units"].get(arm, [])))
    return (t.replace("@ARM@", arm).replace("@CONFLICTS@", others).replace("@WANTS@", wants)
            .replace("@SCOPE@", ",".join(cfg["scope"])))


def render_dropin(arm: str) -> str:
    t = (TEMPLATES / "systemd" / "rm-arm-member.conf.tmpl").read_text(encoding="utf-8")
    return t.replace("@ARM@", arm).replace("@GATE@", gate_name(arm)).replace("@MARKER@", marker_rel(arm))


def render_gate(arm: str) -> str:
    t = (TEMPLATES / "systemd" / "rm-arena-gate.service.tmpl").read_text(encoding="utf-8")
    return t.replace("@ARM@", arm).replace("@MARKER@", marker_rel(arm))


def _unit_safe(s: str) -> str:
    if not re.fullmatch(r"[\w./@:+\-]+", s):
        raise SwitchError("path %r cannot go into a unit file unquoted (whitespace, quotes, $ or %% in it)" % s)
    return s


def render_replay_unit(arm_toml: str, arena_py: str | None = None) -> str:
    t = (TEMPLATES / "systemd" / "rm-arena-replay.service.tmpl").read_text(encoding="utf-8")
    return (t.replace("@ARM_TOML@", _unit_safe(str(arm_toml)))
            .replace("@ARENA_PY@", _unit_safe(arena_py or str(HERE / "arena.py"))))


def render_hook(arm: str, arm_toml: str, arena_py: str | None = None, *, clone: str | None = None,
                alarm_file: str | None = None, chain: str = "") -> str:
    """The arena pre-push. Every interpolated value is single-quoted (sh_quote): a path holding $(...), backticks,
    quotes or spaces stays a literal string."""
    t = (TEMPLATES / "hooks" / "pre-push.tmpl").read_text(encoding="utf-8")
    if arm not in ARMS or not re.fullmatch(r"\w+", clone or arm):
        raise SwitchError("bad hook arm/clone %r/%r" % (arm, clone))
    return (t.replace("@ARM_Q@", sh_quote(arm)).replace("@CLONE_Q@", sh_quote(clone or arm))
            .replace("@ARM@", arm).replace("@CLONE@", clone or arm)
            .replace("@ARM_TOML_Q@", sh_quote(arm_toml))
            .replace("@ALARM_Q@", sh_quote(alarm_file or str(alarm_path())))
            .replace("@ARENA_PY_Q@", sh_quote(arena_py or str(HERE / "arena.py")))
            .replace("@CHAIN_Q@", sh_quote(chain)))


def render_wrapper(name: str, chain_dir: str) -> str:
    return ("#!/bin/sh\n# arena-hooks wrapper (ARENA_SWITCH_BUILD_ONE_ARM_LIVE_ONLY): runs the clone's own %s hook,\n"
            "# chained from %s. Installed by arena_install.py; core.hooksPath points here.\nexec %s \"$@\"\n"
            % (name, chain_dir.replace("\n", " "), sh_quote(os.path.join(chain_dir, name))))


# ------------------------------------------------------------------ git hooks: where git really looks

def _git(clone, *args, timeout=60) -> str:
    r = subprocess.run(["git", "-C", str(clone)] + list(args), capture_output=True, text=True, timeout=timeout)
    if r.returncode != 0:
        raise SwitchError("git %s in %s failed: %s" % (" ".join(args[:3]), clone, r.stderr.strip()[:200]))
    return r.stdout


def is_clone(p) -> bool:
    return (Path(p) / ".git").exists()


def hook_dirs(clone) -> tuple[Path, Path]:
    """(the hooks dir git really runs - core.hooksPath when set -, the arena hooks dir)."""
    eff = _git(clone, "rev-parse", "--path-format=absolute", "--git-path", "hooks").strip()
    common = _git(clone, "rev-parse", "--path-format=absolute", "--git-common-dir").strip()
    return Path(os.path.normpath(eff)), Path(os.path.normpath(common)) / HOOKS_DIRNAME


def chain_dir(clone) -> str:
    """The hooks dir the arena dir chains to: the previous effective dir, or (re-install) what CHAIN_FROM says."""
    eff, arena = hook_dirs(clone)
    if eff == arena:
        f = arena / "CHAIN_FROM"
        return f.read_text(encoding="utf-8").strip() if f.exists() else ""
    return str(eff)


def chained_hooks(chain: str) -> list[str]:
    if not chain or not os.path.isdir(chain):
        return []
    return [n for n in GIT_HOOKS if os.path.isfile(os.path.join(chain, n)) and os.access(os.path.join(chain, n), os.X_OK)]


def plan_clone_hooks(clone, arm: str, name: str, arm_toml: str, alarm_file: str, arena_py: str | None = None):
    """-> (files [(path, text)], hooksPath value, chain). Reads only."""
    _, arena = hook_dirs(clone)
    chain = chain_dir(clone)
    if chain and os.path.normpath(chain) == str(arena):
        chain = ""
    files = [(arena / "CHAIN_FROM", chain + "\n")]
    for n in chained_hooks(chain):
        if n != "pre-push":
            files.append((arena / n, render_wrapper(n, chain)))
    pp = os.path.join(chain, "pre-push") if "pre-push" in chained_hooks(chain) else ""
    files.append((arena / "pre-push", render_hook(arm, arm_toml, arena_py, clone=name, alarm_file=alarm_file,
                                                  chain=pp)))
    return files, str(arena), chain


def hook_problems(cfg: dict, alarm_file: str, arena_py: str | None = None) -> tuple[list[str], list[str]]:
    """who (e): (problems, notes). A missing clone is a note (nothing there can push)."""
    probs, notes = [], []
    for clone, arm, name in governed_clones(cfg):
        if not is_clone(clone):
            notes.append("%s: no clone at %s" % (name, clone))
            continue
        eff, arena = hook_dirs(clone)
        if eff != arena:
            probs.append("%s: git runs hooks from %s, not %s: the arena pre-push never runs" % (name, eff, arena))
            continue
        cf = arena / "CHAIN_FROM"
        if not cf.exists():
            probs.append("%s: %s missing" % (name, cf))
            continue
        chain = cf.read_text(encoding="utf-8").strip()
        hooks = chained_hooks(chain)
        pp = os.path.join(chain, "pre-push") if "pre-push" in hooks else ""
        want = render_hook(arm, cfg["path"], arena_py, clone=name, alarm_file=alarm_file, chain=pp)
        f = arena / "pre-push"
        if not (f.is_file() and os.access(f, os.X_OK) and f.read_text(encoding="utf-8") == want):
            probs.append("%s: %s is not the rendered arena hook (missing, not executable, or edited/repointed)"
                         % (name, f))
        for n in hooks:
            if n == "pre-push":
                continue
            w = arena / n
            if not (w.is_file() and os.access(w, os.X_OK) and w.read_text(encoding="utf-8") == render_wrapper(n, chain)):
                probs.append("%s: chained hook %s/%s has no wrapper in %s (it would silently stop running)"
                             % (name, chain, n, arena))
    return probs, notes


# ------------------------------------------------------------------ bridge locks, idle, events (default readers)

def default_bridge_locks() -> list[dict]:
    """[{lane, host, holder, purpose, source}]: one per held per-host lock in the ledger (rimflow model.replay ->
    bridge_hosts), plus the shared cross-clone lock file. The arena stamps the arm into the purpose
    ('arena <arm> <lane> <run>: ...'), which is how check (c) reads it. A lock file that exists but cannot be read
    RAISES (rimflow itself reads it as 'no lock'; an unreadable lock is UNMEASURED here)."""
    sys.path.insert(0, str(UTILS.parent / "rimflow"))
    try:
        import model
        world = model.replay()
        out = []
        for host, ent in sorted((world.bridge_hosts or {}).items()):
            if ent and ent.get("holder"):
                out.append({"lane": HOST_LANE.get(host, host), "host": host, "holder": ent.get("holder"),
                            "purpose": ent.get("purpose") or "", "source": "ledger"})
        p = model.shared_bridge_path()
    except Exception as e:  # noqa: BLE001 - an unreadable lock is UNMEASURED, so fail the check
        raise SwitchError("bridge lock unreadable: %s: %s" % (type(e).__name__, e))
    if p and os.path.exists(p):
        try:
            with open(p, encoding="utf-8") as fh:
                d = json.load(fh)
        except (OSError, ValueError) as e:
            raise SwitchError("shared bridge lock %s unreadable: %s" % (p, e))
        if not isinstance(d, dict):
            raise SwitchError("shared bridge lock %s is not an object" % p)
        if d.get("holder"):
            out.append({"lane": "archmagi", "host": model.DEFAULT_BRIDGE_HOST, "holder": d.get("holder"),
                        "purpose": d.get("purpose") or "", "source": "shared"})
    return out


def lock_arm(lock: dict) -> str | None:
    m = re.match(r"^arena\s+(\w+)\b", lock.get("purpose") or "")
    return m.group(1) if m else None


def lock_problems(cfg: dict, locks: list[dict]) -> list[dict]:
    live = live_arms(cfg)
    lanes = lane_arms(cfg)
    arena_mode = cfg["mode"] not in PRODUCTION_ARMS
    wrong = []
    for l in locks:
        arm = lock_arm(l)
        if arm is None:
            if arena_mode:
                wrong.append(dict(l, why="untagged lock: its arm is unknown in mode %s" % cfg["mode"]))
        elif arm not in live:
            wrong.append(dict(l, why="lock names stopped arm %s" % arm))
        elif lanes and l.get("lane") in lanes and arm != lanes[l["lane"]]:
            wrong.append(dict(l, why="lane %s carries %s in this trial, not %s" % (l["lane"], lanes[l["lane"]], arm)))
    return wrong


def proc_cwds(proc="/proc") -> list[tuple[int, str]]:
    out = []
    for d in Path(proc).iterdir():
        if d.name.isdigit():
            try:
                out.append((int(d.name), os.readlink(d / "cwd")))
            except OSError:
                continue
    return out


def events_since(root: Path, arm: str, ts: float) -> int:
    """Events a stopped arm wrote after `ts` (raw JSON lines of events/<arm>.jsonl; a `switch` line is the harness's)."""
    f = Path(root) / "events" / ("%s.jsonl" % arm)
    n = 0
    try:
        lines = f.read_text(encoding="utf-8", errors="replace").splitlines()
    except FileNotFoundError:
        return 0                        # the arm never wrote an event
    except OSError as e:
        raise SwitchError("events/%s.jsonl unreadable: %s" % (arm, e))   # item 8: unreadable is not 'zero events'
    for ln in lines:
        try:
            r = json.loads(ln)
            t = _epoch(r["ts"])
        except (ValueError, KeyError, TypeError):
            n += 1                      # a line we cannot read after the switch is written by SOMEONE: count it
            continue
        if t >= int(ts) and r.get("event") not in ("switch", "stop"):   # event stamps are whole seconds: floor ts
            n += 1
    return n


def _epoch(s) -> float:
    return dt.datetime.fromisoformat(str(s).replace("Z", "+00:00")).timestamp()


def arm_ref_prefix(arm: str) -> str:
    return "refs/remotes/origin/arena/%s/" % arm


def refs_snapshot(cfg: dict, arm: str) -> dict[str, dict[str, str]]:
    """{clone: {tracking ref: sha}} of the arm's namespace in each of its clones (arena arms only: production and v3
    push to main, which is not theirs alone). A clone path that is not a clone is recorded as absent (None); a git
    failure RAISES."""
    out = {}
    if arm in PRODUCTION_ARMS:
        return out
    for c in arm_clones(cfg, arm):
        if not is_clone(c):
            out[str(c)] = None
            continue
        refs = {}
        for ln in _git(c, "for-each-ref", "--format=%(objectname) %(refname)", arm_ref_prefix(arm)).splitlines():
            sha, _, ref = ln.strip().partition(" ")
            if ref:
                refs[ref] = sha
        out[str(c)] = refs
    return out


def pushed_since(cfg: dict, arm: str, ts: float, snapshot: dict | None = None) -> list[str]:
    """Item 8: refs of a stopped arm that MOVED since the switch, by two timestamp-free-of-commits methods:
    (1) compare the arm clone's tracking refs now with the snapshot the switch stored (new / moved / deleted ref);
    (2) the reflog of each tracking ref: an update recorded locally after `ts` (reflog times are when the ref moved
    here, not commit dates, so an old commit pushed late is caught). A git failure RAISES; a clone recorded in the
    snapshot that is no longer readable raises. No snapshot for an arena arm (a pre-round-2 state) is flagged, not
    passed."""
    out = []
    if arm in PRODUCTION_ARMS:
        return out
    now = refs_snapshot(cfg, arm)
    if snapshot is None:
        if any(v for v in now.values()):
            out.append("(no refs snapshot recorded by the switch for %s: cannot prove nothing moved)" % arm)
    else:
        for c, refs in now.items():
            then = snapshot.get(c) or {}
            for ref in sorted(set(then) | set(refs or {})):
                if (refs or {}).get(ref) != then.get(ref):
                    out.append("%s %s" % (ref, "deleted" if ref not in (refs or {}) else
                                          ("new" if ref not in then else "moved")))
    for c, refs in now.items():
        for ref in sorted(refs or {}):
            log = _git(c, "reflog", "show", "--date=unix", "--format=%gd", ref, "--")
            for ln in log.splitlines()[:1]:
                m = re.search(r"@\{(\d+)\}$", ln.strip())
                if m and int(m.group(1)) > ts and not any(o.startswith(ref + " ") for o in out):
                    out.append("%s updated %s (reflog)" % (ref, m.group(1)))
    return out


def remote_refresh(clone: Path, timeout=120) -> dict[str, str]:
    """Item 7: make the origin view CURRENT before judging 'unpushed'. `git fetch --prune origin` (a ref the remote
    force-replaced or deleted is updated/removed locally, so a commit that only the stale tracking ref held counts as
    unpushed again), then `git ls-remote --tags --refs origin` -> {refs/tags/x: sha} (tags are not judged by the
    tracking refs at all). Any failure (no origin, unreachable, auth) raises RemoteUnreachable: fail closed."""
    for args in (["fetch", "--quiet", "--prune", "--no-tags", "origin"],
                 ["ls-remote", "--tags", "--refs", "origin"]):
        try:
            r = subprocess.run(["git", "-C", str(clone)] + args, capture_output=True, text=True, timeout=timeout,
                               env=dict(os.environ, GIT_TERMINAL_PROMPT="0"))
        except (OSError, subprocess.TimeoutExpired) as e:
            raise RemoteUnreachable("git %s: %s" % (args[0], e))
        if r.returncode != 0:
            raise RemoteUnreachable("git %s exit %d: %s" % (args[0], r.returncode, (r.stderr or r.stdout).strip()[:200]))
    tags = {}
    for ln in r.stdout.splitlines():
        sha, _, ref = ln.strip().partition("\t")
        if ref.startswith("refs/tags/"):
            tags[ref] = sha
    return tags


def clone_dirt(clone: Path, _prefix: str = "", refresh: bool = True, remote=None) -> list[dict]:
    """Everything a stopped clone would lose or strand: [{kind, what}] with kind one of
    missing (no clone there), unpushed (a local branch with commits origin has not), tag (a local tag origin lacks or
    holds at another object), detached (HEAD off every branch with commits origin has not), stash, dirty (uncommitted
    tracked change), untracked (non-ignored file), submodule dirt (recursive, prefixed with its path). The reference
    is origin AS IT IS NOW: with refresh (the default) `remote(clone)` (remote_refresh: fetch --prune + ls-remote)
    runs first and raises RemoteUnreachable when origin cannot be asked; refresh=False judges from the cached
    tracking refs (the --allow-offline path; tags are then not judged). A git failure RAISES (UNMEASURED never
    passes)."""
    clone = Path(clone)
    tag = _prefix + str(clone)
    if not clone.exists():
        return [{"kind": "missing", "what": "%s: no clone at this path" % tag}]
    if not is_clone(clone):
        return [{"kind": "missing", "what": "%s: not a git clone" % tag}]
    out = []
    if refresh:
        rtags = (remote or remote_refresh)(clone)
        for ln in _git(clone, "for-each-ref", "--format=%(objectname) %(refname)", "refs/tags/").splitlines():
            sha, _, ref = ln.strip().partition(" ")
            if ref and rtags.get(ref) != sha:
                out.append({"kind": "tag", "what": "%s: %s (%s)" % (
                    tag, ref, "not on origin" if ref not in rtags else "origin holds another object")})
    for ref in _git(clone, "for-each-ref", "--format=%(refname)", "refs/heads/").split():
        n = int(_git(clone, "rev-list", "--count", ref, "--not", "--remotes=origin").strip() or "0")
        if n:
            out.append({"kind": "unpushed", "what": "%s: %s (%d commits not on origin)" % (tag, ref, n)})
    sym = subprocess.run(["git", "-C", str(clone), "symbolic-ref", "-q", "HEAD"], capture_output=True, text=True,
                         timeout=60)
    has_head = subprocess.run(["git", "-C", str(clone), "rev-parse", "-q", "--verify", "HEAD"], capture_output=True,
                              text=True, timeout=60).returncode == 0
    if sym.returncode != 0 and has_head:
        n = int(_git(clone, "rev-list", "--count", "HEAD", "--not", "--remotes=origin").strip() or "0")
        if n:
            out.append({"kind": "detached", "what": "%s: detached HEAD with %d commits not on origin" % (tag, n)})
    st = subprocess.run(["git", "-C", str(clone), "rev-parse", "-q", "--verify", "refs/stash"], capture_output=True,
                        text=True, timeout=60)
    if st.returncode == 0:
        n = len(_git(clone, "stash", "list").splitlines())
        out.append({"kind": "stash", "what": "%s: %d stash entries" % (tag, n)})
    for ln in _git(clone, "status", "--porcelain=v1", "--untracked-files=all", "--ignore-submodules=none").splitlines():
        if not ln.strip():
            continue
        kind = "untracked" if ln.startswith("??") else "dirty"
        out.append({"kind": kind, "what": "%s: %s" % (tag, ln.strip())})
    if (clone / ".gitmodules").exists():
        subs = _git(clone, "submodule", "status", "--recursive")
        for ln in subs.splitlines():
            f = ln[1:].split()
            if len(f) >= 2 and (clone / f[1]).exists() and is_clone(clone / f[1]):
                out += clone_dirt(clone / f[1], _prefix=tag + " submodule ", refresh=refresh, remote=remote)
    return out


unpushed = clone_dirt          # the old name; Deps.unpushed


def _norm_dirt(items) -> list[dict]:
    return [i if isinstance(i, dict) else {"kind": "unpushed", "what": str(i)} for i in (items or [])]


# ------------------------------------------------------------------ the injectable dependency bundle

def modsconfig_active(path) -> list[str]:
    """ModsConfig.xml is PARSED (activeMods), never grepped."""
    import xml.etree.ElementTree as ET
    node = ET.parse(str(path)).getroot().find("activeMods")
    if node is None:
        raise SwitchError("%s has no <activeMods>" % path)
    return [li.text.strip().lower() for li in node.findall("li") if li.text and li.text.strip()]


def real_modlist_restore(live=None, full=None, run=None) -> dict:
    """`modlist_swap.py --restore --apply`, then verify by PARSING both files that the live list is the owner's."""
    if live is None:
        import game_paths
        live = game_paths.MODS_CONFIG
    full = full or str(REPO / "infrastructure" / "state" / "modlists" / "ModsConfig.FULL.LATEST.xml")
    rc = (run or subprocess.run)([sys.executable, str(UTILS / "modlist_swap.py"), "--restore", "--apply"],
                                 capture_output=True, text=True, timeout=300)
    if rc.returncode != 0:
        raise SwitchError("modlist_swap restore failed: %s" % (rc.stdout + rc.stderr)[-300:])
    return verify_restored(live, full)


def verify_restored(live, full) -> dict:
    a, b = modsconfig_active(live), modsconfig_active(full)
    if a != b:
        raise SwitchError("after restore the live ModsConfig.xml activeMods (%d) differs from the owner's list (%d)"
                          % (len(a), len(b)))
    return {"active": len(a)}


class Deps:
    """Everything `switch` and `who` touch. Defaults are the real thing; tests replace every attribute."""

    def __init__(self, root: Path | None = None, systemctl: Systemctl | None = None, signer=None):
        self.root = Path(root) if root else A.arena_root()
        self.systemctl = systemctl or Systemctl()
        self.signer = signer or harness_signer
        self.clock = time.time
        self.sleep = time.sleep
        self.poll_s = 30.0
        self.bridge_release = self._bridge_release
        self.bridge_locks = default_bridge_locks
        if os.environ.get("ARENA_BRIDGE_LOCKS_FILE"):     # selftest seam: a JSON list of locks instead of the ledger
            self.bridge_locks = lambda p=os.environ["ARENA_BRIDGE_LOCKS_FILE"]: json.loads(Path(p).read_text())
        self.modlist_restore = real_modlist_restore
        self.unpushed = clone_dirt
        self.refs_snapshot = refs_snapshot
        self.runtime_dir = runtime_dir      # where the gate units write rm-arena/live.<arm> (systemd's %t)
        self.who_fn = None              # set by switch() to who() when None
        self.log = lambda m: print(m, flush=True)

    def _bridge_release(self, host: str):
        r = subprocess.run([sys.executable, str(REPO / "src" / "RimMandrake" / "rimflow" / "cli.py"),
                            "bridge", "release", "--host", host], capture_output=True, text=True, timeout=120)
        return r.returncode == 0, (r.stdout + r.stderr)

    # --- files
    def stop_file(self, arm: str) -> Path:
        return self.root / ("STOP.%s" % arm)

    def status_file(self, arm: str) -> Path:
        return self.root / "status" / ("%s.json" % arm)

    def state_file(self) -> Path:
        return self.root / "switch_state.json"

    def last_file(self) -> Path:
        return self.root / "switch_last.json"

    def lock_file(self) -> Path:
        return self.root / "switch.lock"

    def alarm_file(self) -> Path:
        return alarm_path(self.root)

    def status(self, arm: str) -> dict | None:
        """{state, epoch} or None (missing). Unreadable or without a timestamp raises ValueError."""
        try:
            r = json.loads(self.status_file(arm).read_text(encoding="utf-8"))
        except FileNotFoundError:
            return None
        except (OSError, UnicodeDecodeError) as e:
            raise ValueError("status/%s.json unreadable: %s" % (arm, e))
        if not isinstance(r, dict):
            raise ValueError("status/%s.json is not an object" % arm)
        if isinstance(r.get("epoch"), (int, float)):
            ep = float(r["epoch"])
        else:
            try:
                ep = _epoch(r["ts"])
            except (KeyError, ValueError, TypeError):
                raise ValueError("status/%s.json has no readable ts/epoch" % arm)
        return {"state": r.get("state"), "epoch": ep}

    def is_idle(self, arm: str) -> bool:
        """Target inactive -> idle. Active -> its status must read idle AND be fresh (within IDLE_FRESH_S);
        missing, unreadable, untimed or stale is NOT idle."""
        try:
            if not self.systemctl.is_active(target_name(arm)):
                return True
        except UnitStateUnknown:
            return False                # item 9: an unknown state is not 'inactive'
        try:
            s = self.status(arm)
        except ValueError:
            return False
        return bool(s and s["state"] == "idle" and self.clock() - s["epoch"] <= IDLE_FRESH_S)


def write_json(path: Path, obj):
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, tmp = tempfile.mkstemp(dir=str(path.parent), prefix=".tmp.")
    with os.fdopen(fd, "w", encoding="utf-8") as fh:
        json.dump(obj, fh, sort_keys=True)
    os.replace(tmp, path)


def read_state(d: Deps) -> dict | None:
    """None only when no switch was ever recorded (file absent). Unreadable/corrupt/untimed RAISES (item 8: who (d)
    fails closed instead of reading 'nothing to compare')."""
    try:
        text = d.state_file().read_text(encoding="utf-8")
    except FileNotFoundError:
        return None
    except (OSError, UnicodeDecodeError) as e:
        raise SwitchError("%s unreadable: %s" % (d.state_file(), e))
    try:
        st = json.loads(text)
        float(st["epoch"])
    except (ValueError, KeyError, TypeError) as e:
        raise SwitchError("%s is corrupt (%s: %s)" % (d.state_file(), type(e).__name__, e))
    if not isinstance(st, dict):
        raise SwitchError("%s is not an object" % d.state_file())
    return st


def harness_signer(arm: str, event: str, *, lane: str, run_id: str, detail: dict, ts: str | None = None) -> dict:
    """The production signer: arena_eventlog.HarnessWriter inside a harness_pass."""
    import arena_eventlog as L
    p = A.paths()
    with L.harness_pass(p) as cap:
        return L.HarnessWriter(p, cap=cap).emit(arm, event, lane=lane, run_id=run_id, ts=ts, detail=detail)


def now_iso(clock=time.time) -> str:
    return dt.datetime.fromtimestamp(clock(), dt.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


# ------------------------------------------------------------------ the switch lock

@contextlib.contextmanager
def switch_lock(d: Deps):
    """flock(LOCK_EX|LOCK_NB) on <arena>/switch.lock for the whole switch; a second concurrent switch is Refused."""
    p = d.lock_file()
    p.parent.mkdir(parents=True, exist_ok=True)
    fh = open(p, "a+")
    try:
        try:
            fcntl.flock(fh.fileno(), fcntl.LOCK_EX | fcntl.LOCK_NB)
        except BlockingIOError:
            raise Refused("another arena switch holds %s; refused (nothing changed)" % p)
        fh.seek(0); fh.truncate(); fh.write("%d %s\n" % (os.getpid(), now_iso(d.clock))); fh.flush()
        yield
    finally:
        fh.close()


def switch_lock_held(d: Deps) -> bool:
    p = d.lock_file()
    if not p.exists():
        return False
    with open(p, "a+") as fh:
        try:
            fcntl.flock(fh.fileno(), fcntl.LOCK_SH | fcntl.LOCK_NB)
        except BlockingIOError:
            return True
        return False


# ------------------------------------------------------------------ arena switch

def _record_last(d: Deps, **rec):
    try:
        write_json(d.last_file(), dict(ts=now_iso(d.clock), **rec))
    except OSError as e:
        d.log("arena: could not write %s: %s" % (d.last_file(), e))


def switch(mode: str, cfg_path: Path | None = None, deps: Deps | None = None, *, force: bool = False,
           allow_dirty_untracked: bool = False, allow_offline: bool = False) -> dict:
    """Switch to `mode`. Raises Refused (safe: nothing new started, our STOP files removed) or SwitchError (recorded
    in switch_last.json with the steps done and how to recover). Returns a summary."""
    d = deps or Deps()
    if mode not in MODES:
        raise Refused("unknown mode %r (modes: %s)" % (mode, ", ".join(MODES)))
    cfg_path = Path(cfg_path) if cfg_path else arm_toml_path(d.root)
    with switch_lock(d):
        return _switch_locked(mode, cfg_path, d, force, allow_dirty_untracked, allow_offline)


def releasable_locks(cfg: dict, new: dict, locks: list[dict]) -> list[dict]:
    """Item 4: the bridge locks this switch may release - only holds of an arm that STOPS in it. A lock tagged with an
    arm that stays live is kept; an untagged lock belongs to the production seats, so it is released only when the
    production clones stop (a production mode -> an arena mode)."""
    stopping = live_arms(cfg) - live_arms(new)
    prod_stops = cfg["mode"] in PRODUCTION_MODES and new["mode"] not in PRODUCTION_MODES
    out = []
    for l in locks:
        arm = lock_arm(l)
        if (arm is not None and arm in stopping) or (arm is None and prod_stops):
            out.append(l)
    return out


def owns_game_list(cfg: dict, new: dict) -> list[str]:
    """Item 4: the stopping arms that may have swapped the game's mod list (the arena arms; modlist_swap's tier swap).
    Only for them is the list restored. v3/production never trigger a restore: the owner's ModsConfig is his (CLAUDE.md:
    never restore the owner's mod list)."""
    return sorted(a for a in live_arms(cfg) - live_arms(new) if a not in PRODUCTION_ARMS)


def _dirt_holders(d, clones, allow_dirty_untracked, allow_offline, offline, overrides):
    """-> {clone: [what]} that block; fills overrides (dirty/untracked accepted) and offline (clones judged from the
    cached refs because the remote was unreachable and --allow-offline was given). Unreadable state raises Refused."""
    holders = {}
    for c in clones:
        try:
            items = _norm_dirt(d.unpushed(c))
        except RemoteUnreachable as e:
            if not allow_offline:
                raise Refused("cannot reach origin of %s (%s): an unpushed verdict from cached refs is refused "
                              "(--allow-offline accepts it and records it in the switch event)" % (c, e))
            try:
                items = _norm_dirt(d.unpushed(c, refresh=False))
            except Exception as e2:  # noqa: BLE001
                raise Refused("cannot read git state of %s (%s): switch refused" % (c, e2))
            offline.append(str(c))
        except Exception as e:  # noqa: BLE001 - unmeasured never passes
            raise Refused("cannot read git state of %s (%s): switch refused" % (c, e))
        if allow_dirty_untracked:
            overrides += [i for i in items if i["kind"] in ALLOWABLE_DIRT]
            items = [i for i in items if i["kind"] not in ALLOWABLE_DIRT]
        if items:
            holders[str(c)] = [i["what"] for i in items]
    return holders


def _switch_locked(mode, cfg_path, d, force, allow_dirty_untracked, allow_offline=False) -> dict:
    cfg = load_config(cfg_path)
    new = dict(cfg, mode=mode)
    act = set(d.systemctl.active_targets())
    resumed_from = None
    if mode == cfg["mode"] and not force:
        # item 6: "already live" only when the FULL `who` is green; after a partial failure (bridge, hook, STOP,
        # status, events) the switch resumes as if forced instead of reporting a false success
        res = (d.who_fn or who)(cfg, d)
        if res["exit"] == 0:
            _record_last(d, result="already_live", mode=mode)
            return {"already_live": True, "from": mode, "to": mode, "active": sorted(act), "who": 0}
        resumed_from = res["exit"]
        d.log("arena: mode %s is recorded but `who` exits %d; resuming the switch" % (mode, res["exit"]))
    old_arms = sorted(a for a in TARGET_ARMS if target_name(a) in act or a in mode_targets(cfg))
    running = [a for a in old_arms if target_name(a) in act]
    summary = {"from": cfg["mode"], "to": mode, "stopped": [], "waited_s": 0.0, "forced": [], "disabled": [],
               "overrides": [], "steps": [], "offline": []}
    if resumed_from is not None:
        summary["resumed_after_who"] = resumed_from
    steps = summary["steps"]
    t0 = d.clock()
    wrote_stop = []
    # ---- phase 1 (reversible): STOP files, idle wait, clone-state check. Any failure or interrupt undoes our STOPs.
    try:
        for a in running:
            if not d.stop_file(a).exists():
                write_json(d.stop_file(a), {"ts": now_iso(d.clock), "reason": "arena switch %s" % mode})
                wrote_stop.append(a)
        steps.append("STOP written for %s" % (",".join(running) or "nothing"))
        deadline = t0 + IDLE_WAIT_S
        pending = list(running)
        while pending:
            pending = [a for a in pending if not d.is_idle(a)]
            if not pending:
                break
            if d.clock() >= deadline:
                summary["forced"] = list(pending)
                d.log("arena: %s not idle after %d min; stopping the target (SIGTERM, EXIT trap)"
                      % (",".join(pending), IDLE_WAIT_S // 60))
                break
            d.sleep(d.poll_s)
        summary["waited_s"] = d.clock() - t0
        steps.append("waited %.0f s (forced: %s)" % (summary["waited_s"], ",".join(summary["forced"]) or "none"))
        # clone state BEFORE stopping (a stopped arm's hook refuses its pushes); checked AGAIN after the writers stop
        overrides = []
        keep = live_clones(new)
        dirt_clones = []
        for a in old_arms:
            for c in arm_clones(cfg, a):
                if c not in keep and c not in dirt_clones:
                    dirt_clones.append(c)
        holders = _dirt_holders(d, dirt_clones, allow_dirty_untracked, allow_offline, summary["offline"], overrides)
        # item 4: which bridge holds this switch may release (read now: an unreadable lock refuses, nothing stopped)
        try:
            to_release = releasable_locks(cfg, new, d.bridge_locks())
        except Exception as e:  # noqa: BLE001
            raise Refused("bridge locks unreadable (%s: %s): switch refused" % (type(e).__name__, e))
        if holders:
            raise Refused("unsaved work in the stopped arm's clone (unpushed commits, detached HEAD, stash, uncommitted "
                          "or untracked files, submodule dirt, or a missing clone); push or save it first "
                          "(--allow-dirty-untracked accepts only uncommitted/untracked files): %s"
                          % json.dumps(holders, sort_keys=True))
        summary["overrides"] = [i["what"] for i in overrides]
        steps.append("clone state clean%s" % (" (overrode %d dirty/untracked)" % len(overrides) if overrides else ""))
    except BaseException as e:
        resumed = []
        for a in wrote_stop:
            try:
                d.stop_file(a).unlink()
                resumed.append(a)
            except FileNotFoundError:
                resumed.append(a)
            except OSError:
                pass
        _record_last(d, result="refused" if isinstance(e, Refused) else "interrupted", mode_from=cfg["mode"],
                     mode_to=mode, reason="%s: %s" % (type(e).__name__, e), resumed=resumed, steps=steps,
                     rollback="nothing was stopped; STOP removed for %s, which resume at their next pass"
                     % (",".join(resumed) or "nobody"))
        raise
    # ---- phase 2 (past the point of no return): every failure is recorded with the steps done and the recovery
    try:
        for a in running:
            d.systemctl.stop(target_name(a))
            summary["stopped"].append(a)
        steps.append("stopped targets %s" % (",".join(summary["stopped"]) or "none"))
        for f in foreign_members(new, d.systemctl):
            if f["enabled"]:
                d.systemctl.disable(f["unit"])
            if f["active"]:
                d.systemctl.stop(f["unit"])
            summary["disabled"].append(f["unit"])
        steps.append("disabled/stopped other arms' members %s" % (",".join(summary["disabled"]) or "none"))
        # item 5: the writers are stopped now; a push or commit that slipped in between the first check and the stop
        # is caught here (under the switch lock). The new target is NOT started on dirt.
        late_offline, late_over = [], []
        try:
            late = _dirt_holders(d, dirt_clones, allow_dirty_untracked, allow_offline, late_offline, late_over)
        except Refused as e:
            raise SwitchError("clone state unreadable after the writers stopped (%s); the new target was NOT started" % e)
        if late:
            raise SwitchError("unsaved work appeared in the stopped clone(s) while the switch ran (after the first "
                              "check, before the writers stopped); the new target was NOT started: %s"
                              % json.dumps(late, sort_keys=True))
        summary["offline"] = sorted(set(summary["offline"]) | set(late_offline))
        steps.append("clone state re-checked clean after the writers stopped")
        rel = {}
        try:
            to_release = releasable_locks(cfg, new, d.bridge_locks())   # re-read: a hold taken after the first read
        except Exception as e:  # noqa: BLE001
            raise SwitchError("bridge locks unreadable after the writers stopped (%s: %s); the new target was NOT "
                              "started" % (type(e).__name__, e))
        for l in to_release:
            host = l.get("host") or LANES.get(l.get("lane"), l.get("lane"))
            ok, out = d.bridge_release(host)
            rel[l.get("lane") or host] = bool(ok)
            if not ok:
                raise SwitchError("bridge release failed on %s: %s" % (host, str(out).strip()[:200]))
        summary["released"] = rel
        steps.append("released bridge holds of the stopped arm(s): %s" % (",".join(sorted(rel)) or "none"))
        owners = owns_game_list(cfg, new)
        if owners:
            summary["restored"] = d.modlist_restore()
            steps.append("restored the mod list after arena arm(s) %s (modlist_swap tier restore, verified by parse)"
                         % ",".join(owners))
        else:
            summary["restored"] = None
            steps.append("mod list untouched (no stopping arm owns the game list)")
        run_id = "switch-%s" % now_iso(d.clock).replace(":", "")
        detail = {"from": cfg["mode"], "to": mode, "stopped": summary["stopped"],
                  "waited_s": round(summary["waited_s"], 1), "forced_stop": summary["forced"],
                  "scope": cfg["scope"] if mode in PRODUCTION_MODES else None,
                  "targets": expected_targets(new), "disabled": summary["disabled"] or None,
                  "overrides": summary["overrides"] or None, "force": True if force else None,
                  "offline": summary["offline"] or None, "resumed_after_who": summary.get("resumed_after_who"),
                  "live_arms": sorted(live_arms(new)) if mode == TRIAL else None, "steps": list(steps)}
        detail = {k: v for k, v in detail.items() if v is not None}
        try:
            summary["event"] = d.signer(mode, "switch", lane="none", run_id=run_id, detail=detail,
                                        ts=now_iso(d.clock))
        except Exception as e:  # noqa: BLE001
            raise SwitchError("switch event could not be signed (%s: %s); the old arm is stopped and the new target "
                              "was NOT started" % (type(e).__name__, e))
        steps.append("signed the switch event")
        stopped_now = sorted(set(ARMS) - live_arms(new))
        try:
            snap = {a: d.refs_snapshot(new, a) for a in stopped_now}
        except Exception as e:  # noqa: BLE001 - who (d) must have a baseline; without one it would fail open
            raise SwitchError("tracking refs of the stopped arms unreadable (%s: %s); the new target was NOT started"
                              % (type(e).__name__, e))
        write_json(d.state_file(), {"ts": now_iso(d.clock), "epoch": d.clock(), "mode": mode, "from": cfg["mode"],
                                    "stopped": stopped_now, "refs": snap})
        set_mode(cfg_path, mode)
        steps.append("arm.toml mode = %s" % mode)
        clear = live_arms(new) | set(mode_targets(new))
        if new["mode"] in PRODUCTION_MODES:
            clear |= set(PRODUCTION_ARMS)       # the production clones run as v3 or production: both aliases clear
        for a in sorted(clear):
            try:
                d.stop_file(a).unlink()
            except FileNotFoundError:
                pass
        for a in mode_targets(new):
            d.systemctl.start(target_name(a))                   # ONE target per call, sequentially
            steps.append("started %s" % target_name(a))
    except BaseException as e:
        cur = None
        with contextlib.suppress(Exception):
            cur = load_config(cfg_path)["mode"]
        _record_last(d, result="failed", mode_from=cfg["mode"], mode_to=mode, reason="%s: %s" % (type(e).__name__, e),
                     steps=steps, arm_toml_mode=cur,
                     rollback="old targets %s are stopped (not restarted); arm.toml mode is %s; `arena who` (a) "
                              "flags what is not live; fix the cause and re-run `arena switch %s`"
                              % (",".join(summary["stopped"]) or "none", cur, mode))
        raise
    cfg = load_config(cfg_path)
    res = (d.who_fn or who)(cfg, d)
    summary["who"] = res
    _record_last(d, result="ok" if res["exit"] == 0 else "who_failed", mode_from=summary["from"], mode_to=mode,
                 steps=steps, who=res["exit"])
    if res["exit"] != 0:
        raise SwitchError("arena who failed after the switch: %s" % json.dumps(res["checks"], sort_keys=True,
                                                                               default=str)[:2000])
    return summary


# ------------------------------------------------------------------ arena who

def stray_markers(cfg: dict, d) -> list[str]:
    """Gate markers (<runtime>/rm-arena/live.<arm>) of arms whose target is not live in this mode: a member could
    start under them. Unreadable runtime dir raises."""
    base = Path(d.runtime_dir()) / "rm-arena"
    if not base.exists():
        return []
    live = set(mode_targets(cfg))
    return sorted(str(p) for p in base.glob("live.*") if p.name[len("live."):] not in live)


def who(cfg: dict, d: Deps, bridge_locks=None, cwds=None, events=None, pushed=None, hooks=None) -> dict:
    """The checks (module docstring). exit = bitmask a=1 b=2 c=4 d=8 e=32 f=64. A reader that raises FAILS its check."""
    checks = {}
    exp = set(expected_targets(cfg))
    try:
        act = set(d.systemctl.active_targets())
        foreign = foreign_members(cfg, d.systemctl)
        missing = missing_live(cfg, d.systemctl)            # item 3: production's live set, read from the config
        stray = stray_markers(cfg, d)                       # item 2: a gate marker of an arm that is not live
        checks["a"] = {"ok": act == exp and not foreign and not missing and not stray, "expected": sorted(exp),
                       "active": sorted(act), "foreign_members": foreign, "missing_live": missing,
                       "stray_markers": stray, "unknown_state": [f["unit"] for f in foreign if f.get("unknown")]}
    except Exception as e:  # noqa: BLE001
        checks["a"] = {"ok": False, "error": "%s: %s" % (type(e).__name__, e)}
    try:
        stopped = stopped_clones(cfg)
        me = os.getpid()
        bad = [(pid, cwd, str(c)) for pid, cwd in (cwds or proc_cwds)() if pid != me
               for c in stopped if _inside(cwd, c)]
        checks["b"] = {"ok": not bad, "inside_stopped_clone": bad[:10]}
    except Exception as e:  # noqa: BLE001
        checks["b"] = {"ok": False, "error": "%s: %s" % (type(e).__name__, e)}
    try:
        locks = (bridge_locks or getattr(d, "bridge_locks", None) or default_bridge_locks)()
        wrong = lock_problems(cfg, locks)
        checks["c"] = {"ok": not wrong, "locks": locks, "wrong": wrong}
    except Exception as e:  # noqa: BLE001
        checks["c"] = {"ok": False, "error": "%s: %s" % (type(e).__name__, e)}
    try:
        st = read_state(d)
        if st is None:
            checks["d"] = {"ok": True, "note": "no switch recorded yet; nothing to compare"}
        else:
            ts = float(st["epoch"])
            stopped_arms = [a for a in ARMS if a not in live_arms(cfg)]
            ev = {a: (events or events_since)(d.root, a, ts) for a in stopped_arms}
            ev = {a: n for a, n in ev.items() if n}
            snaps = st.get("refs") if isinstance(st.get("refs"), dict) else {}
            pushed_fn = pushed or (lambda c, a, t: pushed_since(c, a, t, snapshot=snaps.get(a)))
            pu = {a: pushed_fn(cfg, a, ts) for a in stopped_arms}
            pu = {a: r for a, r in pu.items() if r}
            checks["d"] = {"ok": not ev and not pu, "events_since_switch": ev, "pushed_since_switch": pu}
    except Exception as e:  # noqa: BLE001
        checks["d"] = {"ok": False, "error": "%s: %s" % (type(e).__name__, e)}
    try:
        probs, notes = (hooks or (lambda c: hook_problems(c, str(d.alarm_file()))))(cfg)
        checks["e"] = {"ok": not probs, "problems": probs, "notes": notes}
    except Exception as e:  # noqa: BLE001
        checks["e"] = {"ok": False, "error": "%s: %s" % (type(e).__name__, e)}
    try:
        flags = []
        held = switch_lock_held(d)
        for a in mode_targets(cfg):
            if d.stop_file(a).exists() and not held:
                flags.append("STOP.%s sits on a LIVE arm and no switch is running: the arm is silently paused" % a)
            try:
                s = d.status(a)
            except ValueError as e:
                flags.append(str(e))
                continue
            if s and s["state"] == "idle" and d.clock() - s["epoch"] > STALE_IDLE_S:
                flags.append("%s has reported idle for %.1f h" % (a, (d.clock() - s["epoch"]) / 3600))
        checks["f"] = {"ok": not flags, "flags": flags, "switch_running": held}
    except Exception as e:  # noqa: BLE001
        checks["f"] = {"ok": False, "error": "%s: %s" % (type(e).__name__, e)}
    code = sum(bit for k, bit in BITS if not checks[k]["ok"])
    return {"exit": code, "checks": checks, "mode": cfg["mode"]}


# ------------------------------------------------------------------ pre-push hook

def refs_from_stdin(text: str) -> list[tuple[str, str, str, str]]:
    out = []
    for ln in text.splitlines():
        f = ln.split()
        if len(f) == 4:
            out.append(tuple(f))
    return out


def prepush_verdict(cfg: dict, arm: str, refs, clone: str | None = None) -> list[str]:
    """Reasons to refuse ([] = allow). `arm` is the clone's arm, or `production` for bench/foundry (then `clone`
    names which: it must be in [production] scope). A stopped arm may push nothing; a live arena arm only
    refs/heads/arena/<arm>/* (never a delete); the production clones may push anything except an arena ref, and only
    while a production mode is live and the clone is in scope."""
    why = []
    if arm == "production":
        live = cfg["mode"] in PRODUCTION_MODES
        if live and clone is not None and clone not in cfg["scope"]:
            why.append("clone %s is outside [production] scope %s: it may not push" % (clone, cfg["scope"]))
    else:
        live = arm in live_arms(cfg)
    if not live:
        why.append("arm %s is STOPPED (mode %s): it may not push" % (arm, cfg["mode"]))
    for lref, lsha, rref, rsha in refs:
        if arm == "production":
            if rref.startswith("refs/heads/arena/"):
                why.append("%s is an arena ref; the production clones never push there" % rref)
            continue
        pre = "refs/heads/arena/%s/" % arm
        if not (rref.startswith(pre) and len(rref) > len(pre)):
            why.append("%s is outside %s*" % (rref, pre))
        elif set(lsha) == {"0"}:
            why.append("%s: deleting an arena branch is refused (they are never deleted)" % rref)
    return why


def switch_in_progress(d: Deps, arm: str) -> list[str]:
    """Item 5: a push during a switch is refused - the switch lock is held, or a STOP file names this clone's arm
    (production clones: STOP.production or STOP.v3, the arms that run in them). An unreadable lock refuses."""
    why = []
    try:
        if switch_lock_held(d):
            why.append("an arena switch is running (%s held): pushes wait until it finishes" % d.lock_file())
    except OSError as e:
        why.append("switch lock %s unreadable (%s): fail closed" % (d.lock_file(), e))
    arms = list(PRODUCTION_ARMS) if arm == "production" else [arm]
    for a in arms:
        if d.stop_file(a).exists():
            why.append("%s exists: arm %s is being stopped by a switch" % (d.stop_file(a), a))
    return why


def alarm(d: Deps, kind: str, **fields):
    rec = dict(ts=now_iso(d.clock), kind=kind, **fields)
    p = d.alarm_file()
    p.parent.mkdir(parents=True, exist_ok=True)
    with open(p, "a", encoding="utf-8") as fh:
        fh.write(json.dumps(rec, sort_keys=True) + "\n")
    return rec


def prepush(arm: str, stdin_text: str, cfg_path: Path | None = None, sink=None, deps: Deps | None = None,
            clone: str | None = None) -> int:
    """The hook. 0 = allow; PREPUSH_REFUSED (10) = refuse and alarm. Unreadable config REFUSES (fails closed).
    `sink(kind, **f)` is the alarm sink (injectable); the default appends to the alarm file ($ARENA_ALARM_FILE, set
    by the hook, else <arena>/alarms/arena.jsonl), which ops_watch reads (ARENA_PUSH_REFUSED). Any other nonzero exit
    is a crash: the shell hook alarms PUSH_HOOK_CRASH and refuses."""
    d = deps or Deps()
    sink = sink or (lambda kind, **f: alarm(d, kind, **f))
    refs = refs_from_stdin(stdin_text)
    try:
        cfg = load_config(Path(cfg_path) if cfg_path else arm_toml_path(d.root))
    except SwitchError as e:
        sink("PUSH_REFUSED", arm=arm, clone=clone, reasons=["arm.toml unreadable (fail closed): %s" % e],
             refs=[r[2] for r in refs])
        sys.stderr.write("arena pre-push: REFUSED: arm.toml unreadable (%s)\n" % e)
        return PREPUSH_REFUSED
    why = prepush_verdict(cfg, arm, refs, clone=clone) + switch_in_progress(d, arm)
    if why:
        sink("PUSH_REFUSED", arm=arm, clone=clone, mode=cfg["mode"], reasons=why, refs=[r[2] for r in refs])
        sys.stderr.write("arena pre-push: REFUSED (%s):\n  %s\n" % (arm, "\n  ".join(why)))
        return PREPUSH_REFUSED
    return 0


# ------------------------------------------------------------------ ops_watch bridge

def ops_two_live(cfg_path: Path | None = None, deps: Deps | None = None) -> dict:
    """-> {value, why}: 0 when `who` passes; else the failed-check bitmask (>0). Unreadable config is a nonzero 16."""
    d = deps or Deps()
    try:
        cfg = load_config(cfg_path or arm_toml_path(d.root))
    except SwitchError as e:
        return {"value": EXIT_CONFIG, "why": str(e)}
    r = who(cfg, d)
    return {"value": r["exit"], "why": json.dumps(r["checks"], sort_keys=True, default=str)[:500], "mode": cfg["mode"]}


def alarms_since(path: Path, since_epoch: float) -> int:
    """Alarm lines (any kind) with ts >= since_epoch; a line whose ts cannot be read counts (someone wrote it).
    A missing file is 0 lines; an unreadable one raises."""
    try:
        text = Path(path).read_text(encoding="utf-8", errors="replace")
    except FileNotFoundError:
        return 0
    n = 0
    for ln in text.splitlines():
        if not ln.strip():
            continue
        try:
            if _epoch(json.loads(ln)["ts"]) >= since_epoch:
                n += 1
        except (ValueError, KeyError, TypeError):
            n += 1
    return n


def trial_runner() -> int:
    """ExecStart of rm-arena-replay.service. The replay DRIVING loop (arena_replay.py has schedule/leftovers/sweep but
    no run loop) is OWED to arena_replay's owner; until then the unit fails loudly instead of pretending to run."""
    sys.stderr.write("arena trial-runner: OWED - the replay driving loop is not built yet (arena_replay.py has no run "
                     "loop); rm-arena-replay.service exits 3\n")
    return 3


def main(argv=None):
    ap = argparse.ArgumentParser(prog="arena")
    sub = ap.add_subparsers(dest="cmd", required=True)
    sub.add_parser("mode")
    s = sub.add_parser("switch"); s.add_argument("mode", choices=MODES)
    s.add_argument("--force", action="store_true", help="restart the mode even if it is already live")
    s.add_argument("--allow-dirty-untracked", action="store_true",
                   help="accept uncommitted/untracked files in the stopped clones (recorded in the switch event)")
    s.add_argument("--allow-offline", action="store_true",
                   help="when origin cannot be reached, judge unpushed work from the cached refs (recorded in the "
                        "switch event; without it an unreachable origin refuses the switch)")
    sub.add_parser("who")
    h = sub.add_parser("prepush"); h.add_argument("--arm", required=True, choices=ARMS)
    h.add_argument("--clone"); h.add_argument("--remote"); h.add_argument("--url")
    sub.add_parser("ops-watch")
    sub.add_parser("trial-runner")
    a = ap.parse_args(argv)
    if a.cmd == "prepush":
        return prepush(a.arm, sys.stdin.read(), clone=a.clone)
    if a.cmd == "trial-runner":
        return trial_runner()
    if a.cmd == "ops-watch":
        r = ops_two_live(); print(json.dumps(r)); return 0 if r["value"] == 0 else 1
    if a.cmd == "mode":
        try:
            print(load_config()["mode"]); return 0
        except SwitchError as e:
            print("arm.toml unreadable: %s" % e, file=sys.stderr); return EXIT_CONFIG
    d = Deps()
    if a.cmd == "who":
        try:
            cfg = load_config(arm_toml_path(d.root))
        except SwitchError as e:
            print("arm.toml unreadable: %s" % e, file=sys.stderr); return EXIT_CONFIG
        r = who(cfg, d)
        print(json.dumps(r, indent=1, sort_keys=True, default=str)); return r["exit"]

    def on_term(signum, frame):
        raise Interrupted("SIGTERM during the switch")
    signal.signal(signal.SIGTERM, on_term)
    try:
        r = switch(a.mode, deps=d, force=a.force, allow_dirty_untracked=a.allow_dirty_untracked,
                   allow_offline=a.allow_offline)
    except Refused as e:
        print("REFUSED: %s" % e, file=sys.stderr); return 3
    except SwitchError as e:
        print("FAILED: %s" % e, file=sys.stderr); return 4
    except KeyboardInterrupt:
        print("INTERRUPTED: see %s" % d.last_file(), file=sys.stderr); return 130
    print(json.dumps(r, indent=1, sort_keys=True, default=str)); return 0


if __name__ == "__main__":
    sys.exit(main())
