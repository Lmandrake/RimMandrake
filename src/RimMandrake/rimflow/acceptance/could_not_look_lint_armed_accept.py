#!/usr/bin/env python3
"""Acceptance for RIMMANDRAKE_ARM_COULD_NOT_LOOK_LINT_299_PLACES_ALLOWED.

./publish runs src/RimMandrake/Utils/could_not_look_lint.py as a refusing check (not shadow), the lint is green on
the repo as it stands, and its selftest passes. Exit 0 = every check passes (expected: 3)."""
import json
import os
import subprocess
import sys

REPO = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "..", ".."))
FAILS = []


def check(name, ok, got=""):
    print("%s %s %s" % ("ok  " if ok else "FAIL", name, "" if ok else got))
    FAILS.append(name) if not ok else None


cfg = json.load(open(os.path.join(REPO, "src/RimMandrake/Utils/publish_tree_checks.json"), encoding="utf-8"))
rows = [c for c in cfg["checks"] if c["test"].endswith("could_not_look_lint.py")]
check("./publish runs the lint as a refusing check", len(rows) == 1 and not rows[0].get("shadow")
      and "--shadow" not in rows[0].get("args", []), rows)
for name, argv in (("the lint is green on the repo", ["src/RimMandrake/Utils/could_not_look_lint.py"]),
                   ("selftest_probe_result passes", ["src/RimMandrake/rimflow/selftest_probe_result.py"])):
    r = subprocess.run([sys.executable] + argv, cwd=REPO, capture_output=True, text=True, timeout=120)
    check(name, r.returncode == 0, (r.stdout + r.stderr).strip()[-300:])
print("FAILED %d" % len(FAILS) if FAILS else "PASS could_not_look_lint_armed (3 checks)")
sys.exit(1 if FAILS else 0)
