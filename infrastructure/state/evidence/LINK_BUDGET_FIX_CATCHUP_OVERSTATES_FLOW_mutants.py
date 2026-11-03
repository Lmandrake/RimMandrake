#!/usr/bin/env python3
"""Mutation proof for LINK_BUDGET_FIX_CATCHUP_OVERSTATES_FLOW.

Runs the FlowWorks SelfTest case LEVELLING_link_budget_catch_up_scales_by_visited_fraction on the code as it
stands (must pass), then on each mutant of RM_LevellingMath.Plan's rate line (each must FAIL), restoring the source
byte-identically afterwards. Exit 0 only when the clean run passes AND every mutant is caught.

Mutants (each one a way the item's done-when can break):
  ceil      the original bug: rate = R * min(ceil(n/visit), MaxCatchUp)  -> n=65 moves ~2x
  nocap     the MaxCatchUp cap dropped                                    -> n=1000 moves 15x
  noscale   no catch-up at all (rate = R always)                          -> n=128 moves only 1x
  capoff1   the cap one lower (MaxCatchUp - 1)                         -> n=1000 moves 7x, not 8x
Not a selftest (no `selftest` in the name): it edits a tracked source file, so run_selftests must never run it in
parallel with the FlowWorks suite. Run it alone:
    python3 infrastructure/state/evidence/LINK_BUDGET_FIX_CATCHUP_OVERSTATES_FLOW_mutants.py
"""
import os
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(os.path.dirname(os.path.dirname(HERE)))
SRC = os.path.join(REPO, "src", "RimMandrake", "FlowWorks", "Source", "RM_LevellingMath.cs")
RUNNER = os.path.join(REPO, "src", "RimMandrake", "Utils", "selftest_flowworks_stock.py")
CASE = "LEVELLING_link_budget_catch_up_scales_by_visited_fraction"
LINE = "long rate = n <= visit ? ratePerLink : Math.Min(ratePerLink * n / visit, ratePerLink * MaxCatchUp);"
MUTANTS = {
    "ceil": "long rate = ratePerLink * Math.Min((n + visit - 1) / visit, MaxCatchUp);",
    "nocap": "long rate = n <= visit ? ratePerLink : ratePerLink * n / visit;",
    "noscale": "long rate = ratePerLink;",
    "capoff1": "long rate = n <= visit ? ratePerLink : Math.Min(ratePerLink * n / visit, ratePerLink * (MaxCatchUp - 1));",
}


def run_case():
    p = subprocess.run([sys.executable, RUNNER, "--only", CASE], cwd=REPO, capture_output=True, text=True, timeout=500)
    out = p.stdout + p.stderr
    ok = p.returncode == 0 and ("ok    " + CASE) in out
    tail = [l for l in out.splitlines() if CASE in l or "aggregate per cycle" in l or "FAIL" in l][:4]
    return ok, p.returncode, tail


def main():
    with open(SRC, "rb") as f:
        orig = f.read()
    text = orig.decode("utf-8")
    if text.count(LINE) != 1:
        print("PROBE BROKEN: the rate line is not in RM_LevellingMath.cs exactly once; the mutants would test nothing")
        return 1
    bad = 0
    ok, rc, tail = run_case()
    print("clean    %s rc=%d %s" % ("PASS" if ok else "FAIL", rc, " | ".join(tail)))
    if not ok:
        bad += 1
    try:
        for name, repl in MUTANTS.items():
            with open(SRC, "wb") as f:
                f.write(text.replace(LINE, repl).encode("utf-8"))
            ok, rc, tail = run_case()
            print("%-8s %s rc=%d %s" % (name, "CAUGHT" if not ok else "SURVIVED", rc, " | ".join(tail)))
            if ok:
                bad += 1
    finally:
        with open(SRC, "wb") as f:
            f.write(orig)
    with open(SRC, "rb") as f:
        if f.read() != orig:
            print("RESTORE FAILED: RM_LevellingMath.cs differs from its original")
            return 1
    print("restored RM_LevellingMath.cs byte-identical")
    print("RESULT %s" % ("PASS" if bad == 0 else "FAIL (%d)" % bad))
    return 0 if bad == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
