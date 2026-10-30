#!/usr/bin/env python3
"""arena_install.py - install the arm targets, member drop-ins, the trial replay unit and the pre-push hooks.
DRY-RUN BY DEFAULT.

    arena_install.py units  [--unit-dir D] [--arm-toml P]            print the plan
    arena_install.py hooks  [--arm-toml P]                           print the plan
    ... --apply                                                      write (refused without it)

units: rm-arm-<arm>.target for every arm and `trial`, a 10-arm.conf drop-in (PartOf=) for every member unit, and
rm-arena-replay.service (trial's runner). It never runs systemctl (not even daemon-reload: do that yourself, once,
after reading the plan), never starts or enables anything.

hooks: for every governed clone (each arena arm clone, bench, foundry) the hooks are installed where git REALLY looks.
bench/foundry set core.hooksPath=infrastructure/githooks, so .git/hooks is never run there. The plan writes
<git-common-dir>/arena-hooks/ (pre-push = the arena check, then the clone's own pre-push; a wrapper for every other
hook of the previous hooks dir, recorded in CHAIN_FROM - owner hooks are chained, never overwritten) and sets the
clone's LOCAL core.hooksPath to it. Re-running is idempotent (CHAIN_FROM is kept when the clone already points at
arena-hooks). A missing clone is skipped (and reported). `--apply` against the real clones and unit dir is a
human/owner decision; the selftest applies only inside a temp world.
"""
from __future__ import annotations

import argparse
import os
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import arena as AR  # noqa: E402

INSTANCE_TEMPLATES = ("rm-ralph-loop", "rm-runner")   # base names, each with systemd/<base>@.service.tmpl
DEFAULT_UNIT_DIR = Path.home() / ".config" / "systemd" / "user"


def plan_units(cfg: dict, unit_dir: Path) -> list[tuple[Path, str]]:
    out = []
    for arm in AR.TARGET_ARMS:
        out.append((unit_dir / AR.target_name(arm), AR.render_target(arm, cfg)))
        # the gate (item 2): started by the target, writes the runtime marker every member's drop-in requires
        out.append((unit_dir / AR.gate_name(arm), AR.render_gate(arm)))
        for u in cfg["units"].get(arm, []):
            out.append((unit_dir / (u + ".d") / "10-arm.conf", AR.render_dropin(arm)))
    if AR.REPLAY_UNIT in cfg["units"].get(AR.TRIAL, []):
        out.append((unit_dir / AR.REPLAY_UNIT, AR.render_replay_unit(cfg["path"])))
    # the base units of the template instances the arm sets name (rm-ralph-loop@a1 -> rm-ralph-loop@.service)
    for base in INSTANCE_TEMPLATES:
        if any(u.startswith(base + "@") for us in cfg["units"].values() for u in us):
            t = (AR.TEMPLATES / "systemd" / (base + "@.service.tmpl")).read_text(encoding="utf-8")
            out.append((unit_dir / (base + "@.service"), t.replace("@ARENA_DIR@", AR._unit_safe(str(HERE)))))
    # a unit may belong to exactly one arm: refuse a plan that lists it twice
    seen = {}
    for p, _ in out:
        if p.name == "10-arm.conf":
            if p in seen:
                raise AR.SwitchError("unit %s is listed in two arms" % p.parent.name[:-2])
            seen[p] = 1
    return out


def plan_hooks(cfg: dict, arm_toml: str, alarm_file: str | None = None, arena_py: str | None = None,
               notes=None) -> list[tuple]:
    """[(kind, path, value)]: kind file (write text, chmod +x for hooks), hookspath (git config --local
    core.hooksPath value in clone `path`)."""
    alarm_file = alarm_file or str(AR.alarm_path())
    out = []
    for clone, arm, name in AR.governed_clones(cfg):
        if not AR.is_clone(clone):
            if notes is not None:
                notes.append("skip %s: no git clone at %s" % (name, clone))
            continue
        files, hp, _chain = AR.plan_clone_hooks(clone, arm, name, arm_toml, alarm_file, arena_py)
        out += [("file", p, t) for p, t in files]
        out.append(("hookspath", clone, hp))
    return out


def apply_plan(plan, apply: bool, out=print) -> int:
    for ent in plan:
        kind, p, val = ent if len(ent) == 3 else ("file",) + tuple(ent)
        if kind == "hookspath":
            out("%s git -C %s config --local core.hooksPath %s" % ("RUN" if apply else "would run", p, val))
            if apply:
                subprocess.run(["git", "-C", str(p), "config", "--local", "core.hooksPath", str(val)], check=True,
                               capture_output=True, timeout=60)
            continue
        out("%s %s (%d bytes)" % ("WRITE" if apply else "would write", p, len(val)))
        if apply:
            p.parent.mkdir(parents=True, exist_ok=True)
            p.write_text(val, encoding="utf-8")
            if p.name in AR.GIT_HOOKS:
                os.chmod(p, 0o755)
    if not apply:
        out("dry run: nothing written. Re-run with --apply to write these files.")
    return len(plan)


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("what", choices=("units", "hooks"))
    ap.add_argument("--unit-dir", type=Path, default=DEFAULT_UNIT_DIR)
    ap.add_argument("--arm-toml", type=Path)
    ap.add_argument("--apply", action="store_true", help="write the files (default: print the plan only)")
    a = ap.parse_args(argv)
    toml = a.arm_toml or AR.arm_toml_path()
    cfg = AR.load_config(toml)
    notes = []
    plan = plan_units(cfg, a.unit_dir) if a.what == "units" else plan_hooks(cfg, str(toml), notes=notes)
    for n in notes:
        print(n)
    apply_plan(plan, a.apply)
    return 0


if __name__ == "__main__":
    sys.exit(main())
