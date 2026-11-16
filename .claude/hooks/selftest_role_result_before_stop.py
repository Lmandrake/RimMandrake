#!/usr/bin/env python3
"""Selftest for role_result_before_stop.py (guard RESULT_BEFORE_EXIT) and its wiring: the REAL designer_stage check on a
concept folder with no result.json, the alarm when the real check cannot run, role_launch's argv arming the hook only
for a Claude stage run, and designer_stage.on_origin_main against this repo. The contract itself:
src/RimMandrake/rimflow/acceptance/guard_designer_result_accept.py."""
import glob
import json
import os
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

HOOK = Path(__file__).with_name("role_result_before_stop.py")
REPO = HOOK.parents[2]
RIMFLOW = REPO / "src" / "RimMandrake" / "rimflow"
sys.path.insert(0, str(RIMFLOW))
sys.path.insert(0, str(HOOK.parent))
import role_result_before_stop as H  # noqa: E402

fails = 0


def check(ok, what):
    global fails
    fails += 0 if ok else 1
    print(("ok    " if ok else "FAIL  ") + what)


def hook(env):
    full = {k: v for k, v in os.environ.items() if not k.startswith(("RM_DESIGNER", "RM_ROLE_UNIT", "RM_STOP_BLOCKS"))}
    full.update(env)
    p = subprocess.run([sys.executable, str(HOOK)], input="{}", capture_output=True, text=True, env=full, timeout=120)
    return p.returncode, p.stdout.strip(), p.stderr


with tempfile.TemporaryDirectory() as tmp:
    states = sorted(glob.glob(str(REPO / "design" / "concepts" / "*" / "stage.json")))
    d = os.path.join(tmp, "Concept")
    os.makedirs(d)
    if states:
        shutil.copy(states[0], os.path.join(d, "stage.json"))
    # 1. the real default check: a folder with a state and no result.json is blocked with the stage machine's words
    rc, out, err = hook({"RM_DESIGNER_DIR": d, "RM_ROLE_UNIT": "st-real", "RM_STOP_BLOCKS_DIR": tmp})
    try:
        reason = json.loads(out).get("reason", "")
    except ValueError:
        reason = ""
    check(states and rc == 0 and "no result.json" in reason and "would_pass" in reason and "smallest_fix" in reason,
          "the real check blocks a run with no result.json, with evidence, would_pass and smallest_fix")
    # 2. the real check cannot run -> no block, "did not run", the alarm raised; an overridden check raises none
    said = []
    old = H.DEFAULT_CHECK
    H.DEFAULT_CHECK = os.path.join(tmp, "no_such_python") + " check"
    try:
        rc = H.main("{}", env={"RM_DESIGNER_DIR": d, "RM_ROLE_UNIT": "st-blind", "RM_STOP_BLOCKS_DIR": tmp},
                    raise_alarm=said.append)
    finally:
        H.DEFAULT_CHECK = old
    check(rc == 0 and len(said) == 1 and "did not run" in said[0], "a real check that cannot run raises its alarm once")
    said = []
    H.main("{}", env={"RM_DESIGNER_DIR": d, "RM_ROLE_UNIT": "st-blind2", "RM_STOP_BLOCKS_DIR": tmp,
                      "RM_DESIGNER_CHECK_CMD": os.path.join(tmp, "nope")}, raise_alarm=said.append)
    check(said == [], "an overridden (test) check that cannot run raises no alarm")
    # 3. an unwritable counter never blocks (no unbounded loop)
    bad = os.path.join(tmp, "afile")
    open(bad, "w").close()
    rc, out, err = hook({"RM_DESIGNER_DIR": d, "RM_ROLE_UNIT": "st-ctr", "RM_STOP_BLOCKS_DIR": os.path.join(bad, "x"),
                         "RM_DESIGNER_CHECK_CMD": "false"})
    check(rc == 0 and out == "" and "did not run" in err, "a block counter that cannot be written blocks nothing")

# 4. the launcher arms the hook for a Claude stage run only
import role_launch as RL  # noqa: E402
role = {"name": "designer", "seat": "DESIGNER", "clone": str(REPO), "model": "opus", "stage_machine": "designer_stage"}


def argv_of(a, **extra):
    return RL.launch_argv(RL.launch_role(dict(role, **extra), a), "U", "m", "/o", "/e", "/x/claude")


armed = argv_of({"mode": "run", "run_now": {"by": "B"}, "concept": "/c/Graffiti"})
check("RM_DESIGNER_DIR=/c/Graffiti" in armed and "RM_ROLE_UNIT=U" in armed, "a Claude stage run carries RM_DESIGNER_DIR")
check(not any(str(x).startswith("RM_DESIGNER_DIR=") for x in argv_of({"mode": "run", "run_now": {"by": "B"}})),
      "a run with no concept is not armed")
check(not any(str(x).startswith("RM_DESIGNER_DIR=") for x in argv_of(
    {"mode": "run", "run_now": {"by": "B", "runner": "codex"}, "concept": "/c/G"})), "a Codex stage run is not armed")
reg = json.load(open(REPO / ".claude" / "settings.json"))
check(any("role_result_before_stop.py" in h.get("command", "") and "|| true" not in h.get("command", "")
          for grp in reg["hooks"]["Stop"] for h in grp["hooks"]), "registered as a Stop hook whose stdout is not swallowed")

# 5. the real origin/main lookup
import designer_stage as DS  # noqa: E402
with tempfile.TemporaryDirectory() as notgit:
    check(DS.on_origin_main(str(REPO), "CLAUDE.md") is True, "origin/main holds CLAUDE.md")
    check(DS.on_origin_main(str(REPO), "design/no/such_file_ever.md") is False, "origin/main lacks a made-up path")
    check(DS.on_origin_main(notgit, "CLAUDE.md") is None, "a folder that is no git repo reads None")
    check(DS.source_errors("CLAUDE.md", "w", notgit, None, on_origin=lambda p: DS.on_origin_main(str(REPO), p)) == [],
          "source_errors accepts a path only origin/main holds")

print("FAIL %d" % fails if fails else "PASS")
sys.exit(1 if fails else 0)
