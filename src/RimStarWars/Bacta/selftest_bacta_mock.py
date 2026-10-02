#!/usr/bin/env python3
"""Selftest for Bacta's north-star suite (BACTA_FIRST_SCRIPT_1). Offline; no bridge.

Runs validation.py through the northstar driver on northstar_mock.py. The clean mock must give every component PASS;
each BACTA_MOCK_BREAK mode re-introduces one defect and must turn its named component FAIL (a check never seen red
proves nothing, debug_process.md section 3 rung 3). Dev tooling, never deployed.
"""
import json
import os
import subprocess
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
CLI = os.path.join(ROOT, "src", "RimMandrake", "Utils", "northstar_driver", "cli.py")
PLAN = os.path.join(HERE, "northstar_plan.py")
BREAKS = {
    "no_heal": "heals_fresh_wound_at_tuned_rate", "heal_when_off": "enters_and_reports_off",
    "heals_brain": "never_regrows_never_touches_brain", "regrows_part": "never_regrows_never_touches_brain",
    "ignores_power": "unpowered_tank_does_not_heal", "no_drain": "drains_bacta_while_healing",
    "no_eject": "ejects_when_nothing_left", "no_needs_hold": "needs_held_while_immersed",
    "scar_when_off": "scar_erasure_off_keeps_the_scar", "revival_when_off": "revival_off_by_default_refuses_corpse",
    "ignores_window": "revival_window_refuses_old_corpse", "droid_always": "droid_toggle_off_stops_the_assist",
    "field_ignores_toggle": "patch_unusable_when_field_items_off", "trader_missing": "trader_stock_patch_landed",
    "recipes_missing": "doctor_recipes_patch_landed",
}
FAILS = []


def run(brk):
    out = os.path.join(tempfile.mkdtemp(prefix="bacta_st_"), "r.json")
    env = dict(os.environ, BACTA_MOCK_BREAK=brk)
    subprocess.run([sys.executable, CLI, "run", "--mock", "--mod", "Bacta", "--plan", PLAN, "--mock-skip-site",
                    "--out", out], env=env, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, timeout=300)
    return dict((c["name"], c["verdict"]) for c in json.load(open(out))["components"])


def check(name, cond, detail=""):
    print("%s  %s %s" % ("ok  " if cond else "FAIL", name, detail))
    if not cond:
        FAILS.append(name)


def main():
    clean = run("")
    bad = dict((k, v) for k, v in clean.items() if not v.startswith("PASS"))
    check("clean mock: every component PASS", len(clean) >= 30 and not bad,
          "%d components, non-pass: %s" % (len(clean), bad))
    for mode, comp in sorted(BREAKS.items()):
        got = run(mode)
        check("break %s -> %s FAIL" % (mode, comp), got.get(comp) == "FAIL", "got %s" % got.get(comp))
    print("selftest_bacta_mock: %s" % ("FAIL %s" % FAILS if FAILS else "ok"))
    return 1 if FAILS else 0


if __name__ == "__main__":
    sys.exit(main())
