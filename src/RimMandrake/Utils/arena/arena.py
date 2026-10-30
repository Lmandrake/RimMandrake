#!/usr/bin/env python3
"""arena.py - the switch: ONE architecture live at a time (ARENA_SWITCH_BUILD_ONE_ARM_LIVE_ONLY).

design/RimMandrake/architecture_switch_harness_2026-10-29.md section 2, testpilot_merged_2026-10-29.md 6.3 (step 7).

    arena.py mode                 print the mode in arm.toml
    arena.py switch <mode>        STOP file, wait idle (<= 90 min), unpushed-work check, stop the old target, release
                                  both bridges, restore the owner's mod list, `switch` event, start the new target, who
    arena.py who                  the four checks (a)-(d) of 2.3; exit code is a bitmask: a=1 b=2 c=4 d=8
    arena.py prepush --arm A      the pre-push hook body (refs on stdin): refuse AND alarm anything not allowed
    arena.py ops-watch            one number for ops_watch's ARENA_TWO_LIVE rule (0 = fine)

arm.toml lives OUTSIDE git (`$ARENA_ARM_TOML`, default `<arena root>/arm.toml`); the committed template is
infrastructure/arena/arm.toml.template. MODES: the arms v3 v3c ralph_a ralph_c trio, `production` (the real seats; its
`[production] scope` names the production clones bench/foundry that are live) and `trial` (v3 stays live as the
control, the replay runner and the lanes carry the other arms).

Every side effect goes through an injectable object (Deps, Systemctl, the signer, the alarm sink) so the selftest
rehearses a switch with a fake systemctl and never touches the real user manager, the real units or the real seats.
Nothing in this file starts systemd, dbus or a private manager; the only systemctl is the one it is handed.

THE SIGNER. A `switch` event must be signed by arena_eventlog. Its ENTRYPOINTS list does not yet name arena.py, so in
production `harness_signer()` is refused until the event-log owner adds "arena.py" there (owed). A switch whose event
cannot be signed STOPS before starting the new target: nothing is live rather than an unrecorded switch.
"""
from __future__ import annotations

import argparse
import datetime as dt
import json
import os
import re
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
MODES = ARMS + ("trial",)
PRODUCTION_ARMS = ("v3", "production")          # these two run in the production clones
PRODUCTION_MODES = ("v3", "production", "trial")  # modes in which the production clones are live
PROD_CLONES = ("bench", "foundry")
LANES = {"steve": "stevedesktop", "archmagi": "archmagi"}
IDLE_WAIT_S = 90 * 60
UNIT_PREFIX = "rm-arm-"
TEMPLATES = REPO / "infrastructure" / "arena"


class SwitchError(Exception):
    pass


class Refused(SwitchError):
    """A refusal that leaves the system safe (nothing newly started)."""


def target_name(arm: str) -> str:
    return "%s%s.target" % (UNIT_PREFIX, arm)


# ------------------------------------------------------------------ config (arm.toml, outside git)

def arm_toml_path(root: Path | None = None) -> Path:
    env = os.environ.get("ARENA_ARM_TOML", "").strip()
    if env:
        return Path(env)
    return (Path(root) if root else A.arena_root()) / "arm.toml"


def clone_root() -> Path:
    return Path(os.environ.get("ARENA_CLONES", "/home/mandrake/rm/arena"))


def load_config(path: Path | None = None) -> dict:
    """Parse arm.toml (tomllib, validated). Raises SwitchError on anything unreadable: callers fail CLOSED."""
    p = Path(path) if path else arm_toml_path()
    try:
        raw = tomllib.loads(p.read_text(encoding="utf-8"))
    except (OSError, tomllib.TOMLDecodeError) as e:
        raise SwitchError("arm.toml %s unreadable: %s" % (p, e))
    mode = raw.get("mode")
    if mode not in MODES:
        raise SwitchError("arm.toml mode %r is not one of %s" % (mode, MODES))
    prod = raw.get("production") or {}
    scope = prod.get("scope", list(PROD_CLONES))
    if (not isinstance(scope, list) or not scope or any(s not in PROD_CLONES for s in scope)
            or len(set(scope)) != len(scope)):
        raise SwitchError("[production] scope must be a non-empty list of %s (got %r)" % (PROD_CLONES, scope))
    clones = raw.get("clones") or {}
    cfg = {"mode": mode, "scope": list(scope), "path": str(p), "trial": raw.get("trial") or {},
           "clones": {k: str(v) for k, v in clones.items()},
           "units": {a: list((raw.get("arms") or {}).get(a, {}).get("units", [])) for a in ARMS}}
    bad = [a for a in (raw.get("arms") or {}) if a not in ARMS]
    if bad:
        raise SwitchError("[arms.%s] is not a known arm %s" % (bad[0], ARMS))
    return cfg


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


def active_arms(cfg: dict) -> set[str]:
    return {"v3"} if cfg["mode"] == "trial" else {cfg["mode"]}


def expected_targets(cfg: dict) -> list[str]:
    return sorted(target_name(a) for a in active_arms(cfg))


def clone_path(cfg: dict, name: str) -> Path:
    if name in cfg["clones"]:
        return Path(cfg["clones"][name])
    if name in PROD_CLONES:
        return Path("/home/mandrake/rm") / name
    return clone_root() / name


def arm_clones(cfg: dict, arm: str) -> list[Path]:
    if arm in PRODUCTION_ARMS:
        return [clone_path(cfg, c) for c in PROD_CLONES]
    return [clone_path(cfg, arm)]


def live_clones(cfg: dict) -> set[Path]:
    out = set()
    for a in active_arms(cfg):
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


def _inside(child, parent) -> bool:
    c, q = os.path.realpath(child), os.path.realpath(parent)
    return c == q or c.startswith(q.rstrip("/") + "/")


# ------------------------------------------------------------------ systemctl (injected; never the real one in tests)

class Systemctl:
    """A thin runner over `systemctl --user`. `cmd` is the argv prefix; the selftest passes the fake shim. This class
    only ever starts ONE target per call (a transaction of two conflicting targets is what systemd refuses)."""

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
        rc, out = self.run("is-active", unit)
        return rc == 0 and out.strip().startswith("active")

    def stop(self, unit):
        rc, out = self.run("stop", unit, timeout=300)
        if rc != 0:
            raise SwitchError("systemctl stop %s failed (rc %d): %s" % (unit, rc, out.strip()[:200]))

    def start(self, unit):
        rc, out = self.run("start", unit, timeout=300)
        if rc != 0:
            raise SwitchError("systemctl start %s failed (rc %d): %s" % (unit, rc, out.strip()[:200]))


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
            d[sec].setdefault(k.strip(), []).extend(v.split())
    return d


def unit_values(u: dict, key: str, sec="Unit") -> set[str]:
    return set((u.get(sec) or {}).get(key, []))


def check_graph(units: dict[str, str], arms=ARMS) -> list[str]:
    """units: unit name -> file text (targets and member drop-ins by their unit name). Returns problems; [] = sound.
    Checks: every rm-arm target exists; Conflicts= is mutual between every pair of targets and lists every other
    target; every non-target unit carries PartOf= exactly one existing target; no target lists itself."""
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
            if b != a and u not in c:
                probs.append("%s lacks Conflicts=%s" % (t, u))
            if b != a and u in parsed and t not in unit_values(parsed[u], "Conflicts"):
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
    """Read targets (`rm-arm-*.target`) and drop-in files (`<unit>.d/*.conf`, keyed by the unit name) from a dir."""
    out = {}
    for f in sorted(Path(d).glob("%s*.target" % UNIT_PREFIX)):
        out[f.name] = f.read_text(encoding="utf-8")
    for dd in sorted(Path(d).glob("*.d")):
        unit = dd.name[:-2]
        if unit.startswith(UNIT_PREFIX):
            continue
        txt = "".join(c.read_text(encoding="utf-8") + "\n" for c in sorted(dd.glob("*.conf")))
        if "PartOf" in txt or txt.strip():
            out[unit] = txt
    return out


# ------------------------------------------------------------------ templates (rendering only; installer writes)

def render_target(arm: str, cfg: dict, arms=ARMS) -> str:
    name = "rm-arm-production.target.tmpl" if arm == "production" else "rm-arm.target.tmpl"
    t = (TEMPLATES / "systemd" / name).read_text(encoding="utf-8")
    others = " ".join(target_name(b) for b in arms if b != arm)
    wants = " ".join(cfg["units"].get(arm, []))
    return (t.replace("@ARM@", arm).replace("@CONFLICTS@", others).replace("@WANTS@", wants)
            .replace("@SCOPE@", ",".join(cfg["scope"])))


def render_dropin(arm: str) -> str:
    t = (TEMPLATES / "systemd" / "rm-arm-member.conf.tmpl").read_text(encoding="utf-8")
    return t.replace("@ARM@", arm)


def render_hook(arm: str, arm_toml: str, arena_py: str | None = None) -> str:
    t = (TEMPLATES / "hooks" / "pre-push.tmpl").read_text(encoding="utf-8")
    return (t.replace("@ARM@", arm).replace("@ARM_TOML@", arm_toml)
            .replace("@ARENA_PY@", arena_py or str(HERE / "arena.py")))


# ------------------------------------------------------------------ bridge locks, idle, events (default readers)

def default_bridge_locks() -> list[dict]:
    """[{lane, holder, purpose}] from rimflow's shared bridge lock. The arena stamps the arm into the purpose
    ('arena <arm> <lane> <run>: ...'), which is how check (c) reads it. No lock -> []."""
    sys.path.insert(0, str(UTILS.parent / "rimflow"))
    try:
        import model
        d = model.read_shared_bridge()
    except Exception as e:  # noqa: BLE001 - an unreadable lock is UNMEASURED, so fail the check
        raise SwitchError("bridge lock unreadable: %s: %s" % (type(e).__name__, e))
    if not d:
        return []
    return [{"lane": d.get("lane") or "?", "holder": d.get("holder"), "purpose": d.get("purpose") or ""}]


def lock_arm(lock: dict) -> str | None:
    m = re.match(r"^arena\s+(\w+)\b", lock.get("purpose") or "")
    return m.group(1) if m else None


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
        lines = f.read_text(encoding="utf-8").splitlines()
    except OSError:
        return 0
    for ln in lines:
        try:
            r = json.loads(ln)
            t = _epoch(r["ts"])
        except (ValueError, KeyError, TypeError):
            n += 1                      # a line we cannot read after the switch is written by SOMEONE: count it
            continue
        if t > ts and r.get("event") not in ("switch", "stop"):
            n += 1
    return n


def _epoch(s) -> float:
    return dt.datetime.fromisoformat(str(s).replace("Z", "+00:00")).timestamp()


def pushed_since(cfg: dict, arm: str, ts: float) -> list[str]:
    """Refs in the arm's namespace whose tip is newer than `ts`, read from the arm clone's remote-tracking refs.
    (A tip's commit date is a proxy for the push time; a stopped arm pushing OLD commits is caught by the hook.)"""
    out = []
    for c in arm_clones(cfg, arm):
        if not (c / ".git").exists():
            continue
        r = subprocess.run(["git", "-C", str(c), "for-each-ref", "--format=%(refname) %(committerdate:unix)",
                            "refs/remotes/origin/arena/%s/" % arm], capture_output=True, text=True, timeout=60)
        for ln in r.stdout.splitlines():
            ref, _, t = ln.rpartition(" ")
            if t.isdigit() and int(t) > ts:
                out.append(ref)
    return out


def unpushed(clone: Path) -> list[str]:
    """Local branches with commits no remote-tracking ref has. A clone with no remote: everything is unpushed.
    A git failure raises (UNMEASURED never passes)."""
    clone = Path(clone)
    if not (clone / ".git").exists():
        return []
    r = subprocess.run(["git", "-C", str(clone), "for-each-ref", "--format=%(refname)", "refs/heads/"],
                       capture_output=True, text=True, timeout=60)
    if r.returncode != 0:
        raise SwitchError("git for-each-ref in %s failed: %s" % (clone, r.stderr.strip()[:200]))
    bad = []
    for ref in r.stdout.split():
        c = subprocess.run(["git", "-C", str(clone), "rev-list", "--count", ref, "--not", "--remotes"],
                           capture_output=True, text=True, timeout=60)
        if c.returncode != 0:
            raise SwitchError("git rev-list %s in %s failed: %s" % (ref, clone, c.stderr.strip()[:200]))
        if int(c.stdout.strip() or "0") > 0:
            bad.append("%s (%s commits)" % (ref, c.stdout.strip()))
    return bad


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
    import game_paths
    live = live or game_paths.MODS_CONFIG
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
    """Everything `switch` touches. Defaults are the real thing; tests replace every attribute."""

    def __init__(self, root: Path | None = None, systemctl: Systemctl | None = None, signer=None):
        self.root = Path(root) if root else A.arena_root()
        self.systemctl = systemctl or Systemctl()
        self.signer = signer or harness_signer
        self.clock = time.time
        self.sleep = time.sleep
        self.poll_s = 30.0
        self.bridge_release = self._bridge_release
        self.modlist_restore = real_modlist_restore
        self.unpushed = unpushed
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

    def alarm_file(self) -> Path:
        return self.root / "alarms" / "arena.jsonl"

    def is_idle(self, arm: str) -> bool:
        """Target inactive -> idle. Active -> its status file must read idle; missing/unreadable is NOT idle."""
        if not self.systemctl.is_active(target_name(arm)):
            return True
        try:
            return json.loads(self.status_file(arm).read_text(encoding="utf-8")).get("state") == "idle"
        except (OSError, ValueError, AttributeError):
            return False


def write_json(path: Path, obj):
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, tmp = tempfile.mkstemp(dir=str(path.parent), prefix=".tmp.")
    with os.fdopen(fd, "w", encoding="utf-8") as fh:
        json.dump(obj, fh, sort_keys=True)
    os.replace(tmp, path)


def read_state(d: Deps) -> dict | None:
    try:
        return json.loads(d.state_file().read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return None


def harness_signer(arm: str, event: str, *, lane: str, run_id: str, detail: dict, ts: str | None = None) -> dict:
    """The production signer: arena_eventlog.HarnessWriter inside a harness_pass. Refused (Rejected) until
    arena.py is in arena_eventlog.ENTRYPOINTS (owed to that module's owner)."""
    import arena_eventlog as L
    p = A.paths()
    with L.harness_pass(p) as cap:
        return L.HarnessWriter(p, cap=cap).emit(arm, event, lane=lane, run_id=run_id, ts=ts, detail=detail)


def now_iso(clock=time.time) -> str:
    return dt.datetime.fromtimestamp(clock(), dt.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


# ------------------------------------------------------------------ arena switch

def switch(mode: str, cfg_path: Path | None = None, deps: Deps | None = None) -> dict:
    """Switch to `mode`. Raises Refused (safe: the new target was not started) or SwitchError. Returns a summary."""
    d = deps or Deps()
    if mode not in MODES:
        raise Refused("unknown mode %r (modes: %s)" % (mode, ", ".join(MODES)))
    cfg_path = Path(cfg_path) if cfg_path else arm_toml_path(d.root)
    cfg = load_config(cfg_path)
    old_arms = sorted(a for a in set(ARMS) if d.systemctl.is_active(target_name(a)) or a in active_arms(cfg))
    summary = {"from": cfg["mode"], "to": mode, "stopped": [], "waited_s": 0.0, "forced": []}
    t0 = d.clock()

    # 1. STOP for every running arm; its loop honours it at the next pass boundary
    running = [a for a in old_arms if d.systemctl.is_active(target_name(a))]
    for a in running:
        write_json(d.stop_file(a), {"ts": now_iso(d.clock), "reason": "arena switch %s" % mode})
    # 2. wait for idle, at most 90 minutes in total
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
    # 4 (first). unpushed work: BEFORE stopping, because a stopped arm's hook refuses its pushes. The STOP file stays.
    holders = {}
    keep = live_clones(dict(cfg, mode=mode))               # clones the new mode keeps using are not "stopped"
    for a in old_arms:
        for c in arm_clones(cfg, a):
            if c in keep:
                continue
            try:
                bad = d.unpushed(c)
            except Exception as e:  # noqa: BLE001 - unmeasured never passes
                raise Refused("cannot read git state of %s (%s): switch refused" % (c, e))
            if bad:
                holders[str(c)] = bad
    if holders:
        raise Refused("unpushed commits in the stopped arm's clone; push or save them first (the STOP file stays): %s"
                      % json.dumps(holders, sort_keys=True))
    # 3. stop the old targets, release both bridges, restore the owner's list
    for a in running:
        d.systemctl.stop(target_name(a))
        summary["stopped"].append(a)
    rel = {}
    for lane, host in LANES.items():
        ok, out = d.bridge_release(host)
        rel[lane] = bool(ok)
        if not ok:
            raise SwitchError("bridge release failed on %s: %s" % (lane, str(out).strip()[:200]))
    summary["released"] = rel
    summary["restored"] = d.modlist_restore()
    # 5. the switch event (signed), then the new target, then who
    run_id = "switch-%s" % now_iso(d.clock).replace(":", "")
    detail = {"from": cfg["mode"], "to": mode, "stopped": summary["stopped"],
              "waited_s": round(summary["waited_s"], 1), "forced_stop": summary["forced"],
              "scope": cfg["scope"] if mode in PRODUCTION_MODES else None}
    detail = {k: v for k, v in detail.items() if v is not None}
    try:
        summary["event"] = d.signer(mode, "switch", lane="none", run_id=run_id, detail=detail, ts=now_iso(d.clock))
    except Exception as e:  # noqa: BLE001
        raise SwitchError("switch event could not be signed (%s: %s); the old arm is stopped and the new target was "
                          "NOT started" % (type(e).__name__, e))
    write_json(d.state_file(), {"ts": now_iso(d.clock), "epoch": d.clock(), "mode": mode, "from": cfg["mode"],
                                "stopped": sorted(set(ARMS) - active_arms({"mode": mode}))})
    set_mode(cfg_path, mode)
    for a in active_arms({"mode": mode}):
        try:
            d.stop_file(a).unlink()
        except FileNotFoundError:
            pass
        d.systemctl.start(target_name(a))                   # ONE target per call, sequentially
    cfg = load_config(cfg_path)
    res = (d.who_fn or who)(cfg, d)
    summary["who"] = res
    if res["exit"] != 0:
        raise SwitchError("arena who failed after the switch: %s" % json.dumps(res["checks"], sort_keys=True))
    return summary


# ------------------------------------------------------------------ arena who

def who(cfg: dict, d: Deps, bridge_locks=None, cwds=None, events=None, pushed=None) -> dict:
    """The four checks of 2.3. exit = bitmask: a=1 b=2 c=4 d=8. A reader that raises FAILS its check (never passes)."""
    checks = {}
    exp = set(expected_targets(cfg))
    try:
        act = set(d.systemctl.active_targets())
        checks["a"] = {"ok": act == exp, "expected": sorted(exp), "active": sorted(act)}
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
        locks = (bridge_locks or default_bridge_locks)()
        live = active_arms(cfg)
        wrong = [l for l in locks if lock_arm(l) is not None and lock_arm(l) not in live]
        checks["c"] = {"ok": not wrong, "locks": locks, "wrong": wrong}
    except Exception as e:  # noqa: BLE001
        checks["c"] = {"ok": False, "error": "%s: %s" % (type(e).__name__, e)}
    try:
        st = read_state(d)
        if st is None:
            checks["d"] = {"ok": True, "note": "no switch recorded yet; nothing to compare"}
        else:
            ts = float(st["epoch"])
            stopped_arms = [a for a in ARMS if a not in active_arms(cfg)]
            ev = {a: (events or events_since)(d.root, a, ts) for a in stopped_arms}
            ev = {a: n for a, n in ev.items() if n}
            pu = {a: (pushed or pushed_since)(cfg, a, ts) for a in stopped_arms}
            pu = {a: r for a, r in pu.items() if r}
            checks["d"] = {"ok": not ev and not pu, "events_since_switch": ev, "pushed_since_switch": pu}
    except Exception as e:  # noqa: BLE001
        checks["d"] = {"ok": False, "error": "%s: %s" % (type(e).__name__, e)}
    code = sum(bit for k, bit in (("a", 1), ("b", 2), ("c", 4), ("d", 8)) if not checks[k]["ok"])
    return {"exit": code, "checks": checks, "mode": cfg["mode"]}


# ------------------------------------------------------------------ pre-push hook

def refs_from_stdin(text: str) -> list[tuple[str, str, str, str]]:
    out = []
    for ln in text.splitlines():
        f = ln.split()
        if len(f) == 4:
            out.append(tuple(f))
    return out


def prepush_verdict(cfg: dict, arm: str, refs) -> list[str]:
    """Reasons to refuse ([] = allow). `arm` is the clone's arm, or `production` for bench/foundry.
    A stopped arm may push nothing; a live arena arm only refs/heads/arena/<arm>/* (never a delete); the production
    clones may push anything except an arena ref, and only while a production mode is live."""
    why = []
    live = cfg["mode"] in PRODUCTION_MODES if arm == "production" else arm in active_arms(cfg)
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


def alarm(d: Deps, kind: str, **fields):
    rec = dict(ts=now_iso(d.clock), kind=kind, **fields)
    p = d.alarm_file()
    p.parent.mkdir(parents=True, exist_ok=True)
    with open(p, "a", encoding="utf-8") as fh:
        fh.write(json.dumps(rec, sort_keys=True) + "\n")
    return rec


def prepush(arm: str, stdin_text: str, cfg_path: Path | None = None, sink=None, deps: Deps | None = None) -> int:
    """The hook. 0 = allow; 1 = refuse and alarm. Unreadable config REFUSES (fails closed). `sink(kind, **f)` is the
    alarm sink (injectable); the default appends to <arena>/alarms/arena.jsonl, which ops_watch reads."""
    d = deps or Deps()
    sink = sink or (lambda kind, **f: alarm(d, kind, **f))
    refs = refs_from_stdin(stdin_text)
    try:
        cfg = load_config(Path(cfg_path) if cfg_path else arm_toml_path(d.root))
    except SwitchError as e:
        sink("PUSH_REFUSED", arm=arm, reasons=["arm.toml unreadable (fail closed): %s" % e], refs=[r[2] for r in refs])
        sys.stderr.write("arena pre-push: REFUSED: arm.toml unreadable (%s)\n" % e)
        return 1
    why = prepush_verdict(cfg, arm, refs)
    if why:
        sink("PUSH_REFUSED", arm=arm, mode=cfg["mode"], reasons=why, refs=[r[2] for r in refs])
        sys.stderr.write("arena pre-push: REFUSED (%s):\n  %s\n" % (arm, "\n  ".join(why)))
        return 1
    return 0


# ------------------------------------------------------------------ ops_watch bridge

def ops_two_live(cfg_path: Path | None = None, deps: Deps | None = None) -> dict:
    """-> {value, why}: 0 when `who` passes; else the failed-check bitmask (>0). Unreadable config is a nonzero 16."""
    d = deps or Deps()
    try:
        cfg = load_config(cfg_path or arm_toml_path(d.root))
    except SwitchError as e:
        return {"value": 16, "why": str(e)}
    r = who(cfg, d)
    return {"value": r["exit"], "why": json.dumps(r["checks"], sort_keys=True)[:500], "mode": cfg["mode"]}


def main(argv=None):
    ap = argparse.ArgumentParser(prog="arena")
    sub = ap.add_subparsers(dest="cmd", required=True)
    sub.add_parser("mode")
    s = sub.add_parser("switch"); s.add_argument("mode", choices=MODES)
    sub.add_parser("who")
    h = sub.add_parser("prepush"); h.add_argument("--arm", required=True, choices=ARMS)
    h.add_argument("--remote"); h.add_argument("--url")
    sub.add_parser("ops-watch")
    a = ap.parse_args(argv)
    if a.cmd == "mode":
        print(load_config()["mode"]); return 0
    if a.cmd == "prepush":
        return prepush(a.arm, sys.stdin.read())
    if a.cmd == "ops-watch":
        r = ops_two_live(); print(json.dumps(r)); return 0 if r["value"] == 0 else 1
    d = Deps()
    if a.cmd == "who":
        r = who(load_config(arm_toml_path(d.root)), d)
        print(json.dumps(r, indent=1, sort_keys=True)); return r["exit"]
    try:
        r = switch(a.mode, deps=d)
    except Refused as e:
        print("REFUSED: %s" % e, file=sys.stderr); return 3
    except SwitchError as e:
        print("FAILED: %s" % e, file=sys.stderr); return 4
    print(json.dumps(r, indent=1, sort_keys=True, default=str)); return 0


if __name__ == "__main__":
    sys.exit(main())
