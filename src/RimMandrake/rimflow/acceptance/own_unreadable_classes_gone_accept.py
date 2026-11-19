#!/usr/bin/env python3
"""Acceptance for RIMMANDRAKE_MOVE_OWN_UNREADABLE_CLASSES_ONTO_PROBE_TEN_LEFT.

No non-test .py file under src/RimMandrake/rimflow or src/RimMandrake/Utils defines a class of its own named
Unreadable or Unmeasured: its reads answer through probe_result.py (value, empty, could_not_look, failed) instead.
KEPT names the one file that keeps its class, and why. Exit 0 = none left (expected: 1 check); 1 = each file named;
3 = the scan could not see (probe_result.py not found among the files it read)."""
import ast
import os
import sys

REPO = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "..", ".."))
ROOTS = ("src/RimMandrake/rimflow", "src/RimMandrake/Utils")
NAMES = {"Unreadable", "Unmeasured"}
KEPT = {"src/RimMandrake/rimflow/control.py": "the store's own raise inside txn(); its systemd and cgroup reads answer "
                                              "through probe_result since f5b06712b7a8"}

seen, own, blind = [], [], []
for root in ROOTS:
    for dp, dns, fns in os.walk(os.path.join(REPO, root)):
        dns[:] = [d for d in dns if d not in ("__pycache__", "acceptance")]
        for fn in fns:
            if not fn.endswith(".py") or fn.startswith("selftest"):
                continue
            rel = os.path.relpath(os.path.join(dp, fn), REPO).replace(os.sep, "/")
            try:
                tree = ast.parse(open(os.path.join(REPO, rel), encoding="utf-8").read())
            except (OSError, SyntaxError, UnicodeDecodeError, ValueError) as e:
                blind.append("%s: %s" % (rel, e))
                continue
            seen.append(rel)
            if rel not in KEPT and any(isinstance(n, ast.ClassDef) and n.name in NAMES for n in ast.walk(tree)):
                own.append(rel)
if "src/RimMandrake/rimflow/probe_result.py" not in seen:
    print("COULD NOT LOOK: probe_result.py was not among the %d files read" % len(seen))
    sys.exit(3)
for b in blind:
    print("note: did not parse %s" % b)
for f in sorted(own):
    print("FAIL %s defines its own Unreadable/Unmeasured class" % f)
print("FAILED %d of %d files read" % (len(own), len(seen)) if own else
      "PASS own_unreadable_classes_gone (1 check, %d files read)" % len(seen))
sys.exit(1 if own else 0)
