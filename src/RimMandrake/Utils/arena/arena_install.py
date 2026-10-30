#!/usr/bin/env python3
"""arena_install.py - install the arm targets, member drop-ins and pre-push hooks. DRY-RUN BY DEFAULT.

    arena_install.py units  [--unit-dir D] [--arm-toml P]            print the plan
    arena_install.py hooks  [--arm-toml P]                           print the plan
    ... --apply                                                      write (refused without it)

It renders the templates in infrastructure/arena/ and writes files ONLY. It never runs systemctl (not even
daemon-reload: do that yourself, once, after reading the plan), never starts anything, and `--apply` against the real
unit dir is a human/owner decision (the real seats and units are not touched by the selftest or by this build).
"""
from __future__ import annotations

import argparse
import os
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import arena as AR  # noqa: E402

DEFAULT_UNIT_DIR = Path.home() / ".config" / "systemd" / "user"


def plan_units(cfg: dict, unit_dir: Path) -> list[tuple[Path, str]]:
    out = []
    for arm in AR.ARMS:
        out.append((unit_dir / AR.target_name(arm), AR.render_target(arm, cfg)))
        for u in cfg["units"].get(arm, []):
            out.append((unit_dir / (u + ".d") / "10-arm.conf", AR.render_dropin(arm)))
    # a unit may belong to exactly one arm: refuse a plan that lists it twice
    seen = {}
    for p, _ in out:
        if p.name == "10-arm.conf":
            if p in seen:
                raise AR.SwitchError("unit %s is listed in two arms" % p.parent.name[:-2])
            seen[p] = 1
    return out


def plan_hooks(cfg: dict, arm_toml: str) -> list[tuple[Path, str]]:
    out = []
    for arm in AR.ARMS:
        if arm in AR.PRODUCTION_ARMS:
            continue
        out.append((AR.clone_path(cfg, arm) / ".git" / "hooks" / "pre-push", AR.render_hook(arm, arm_toml)))
    for c in AR.PROD_CLONES:
        out.append((AR.clone_path(cfg, c) / ".git" / "hooks" / "pre-push", AR.render_hook("production", arm_toml)))
    return out


def apply_plan(plan, apply: bool, out=print) -> int:
    for p, text in plan:
        out("%s %s (%d bytes)" % ("WRITE" if apply else "would write", p, len(text)))
        if apply:
            p.parent.mkdir(parents=True, exist_ok=True)
            p.write_text(text, encoding="utf-8")
            if p.name == "pre-push":
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
    plan = plan_units(cfg, a.unit_dir) if a.what == "units" else plan_hooks(cfg, str(toml))
    apply_plan(plan, a.apply)
    return 0


if __name__ == "__main__":
    sys.exit(main())
