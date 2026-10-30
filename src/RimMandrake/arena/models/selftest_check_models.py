#!/usr/bin/env python3
"""Selftest for check_models.py: the TLC-output parser offline, then (if TLC is installed) the cheap
live cases: the unfixed goodbye race and one mutation per safety property.  The two fixed runs take
~2 min and are left to `check_models.py` itself.
"""
# selftest-timeout: 240
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import check_models as CM  # noqa: E402

fails = 0


def check(cond, what):
    global fails
    print(("ok    " if cond else "FAIL  ") + what)
    fails += not cond


# --- offline: the parser ---------------------------------------------------------------------
check(CM.outcome("Error: Invariant S5 is violated.\nError: The behavior up to this point is:\n[check_models] returncode=12\n")
      == "invariant:S5", "an invariant violation is named")
check(CM.outcome("Error: Temporal property L1 was violated.\n[check_models] returncode=13\n") == "temporal:L1",
      "a temporal violation is named")
check(CM.outcome("Model checking completed. No error has been found.\n[check_models] returncode=0\n") == "ok", "a clean run is ok")
check(CM.outcome("Progress(3) ...\n[check_models] returncode=137\n").startswith("broken:"),
      "a killed run (no verdict line) is broken, never ok")
check(CM.outcome("Model checking completed. No error has been found.\n[check_models] TIMEOUT after 5s\n")
      == "broken:timeout", "a timeout is broken even if a stale line looks clean")
check(CM.outcome("Model checking completed. No error has been found.\n[check_models] returncode=137\n").startswith("broken:"),
      "a clean line from a run that then died is broken")
check(CM.outcome("Error: Invariant S5 is violated.\n[check_models] returncode=1\n").startswith("broken:"),
      "a matching violation followed by a TLC crash is broken")
check(CM.outcome("Semantic error in module LiveHandoff\n").startswith("broken:"), "a spec error is broken")
race = ["Initial", "Goodbye", "Send", "CloseOut", "Check", "KillOk", "SwitchRecord", "Relaunch"]
check(CM.has_known_race(race), "the known race shape is recognised")
check(not CM.has_known_race(["Initial", "Send", "Goodbye", "CloseOut", "Check", "KillOk", "Relaunch"]),
      "a Send before the goodbye is not the race")
check(CM.trace_actions("State 1: <Initial predicate>\nState 2: <Send(m1) line 1, col 1>\n")
      == ["Initial", "Send"], "trace action names are read without their arguments")
cs = CM.cases()
check(cs["unfixed"][1] == "invariant:S5" and cs["fixed_safety"][1] == "ok" and cs["fixed_liveness"][1] == "ok",
      "the headline cases expect what the item says")
names = {exp.split(":")[1] for _, exp in cs.values() if ":" in exp}
check({"S1", "S2", "S3", "S4", "S5", "S6", "L1", "L2", "L2Bound"} <= names,
      "every invariant and liveness property has a mutation that must break it")
spec = CM.SPEC.read_text()
bugs = {b for c, _ in cs.values() for grp in re.findall(r"Bugs = \{([^}]*)\}", c) for b in re.findall(r'"(\w+)"', grp)}
check(bugs and all(f'Bug("{b}")' in spec for b in bugs), f"every mutation names a guard the spec has ({len(bugs)})")

# --- live: the cheap cases ---------------------------------------------------------------------
t = CM.tools()
if t is None:
    print(f"TLC/Java not installed: {CM.UNMEASURED} (live cases)")
else:
    import os
    import tempfile
    os.environ["RM_TLA_RUNS"] = tempfile.mkdtemp(prefix="selftest_tlc_runs_")
    quick = ["unfixed", "mut_relaunch_after_survive", "mut_verdict_stale", "mut_deploy_live",
             "mut_silent_reload", "mut_queue_in_memory", "mut_switch_early", "mut_ignore_owner"]
    check(CM.main(["--only", *quick, "--workers", "4", "--timeout", "120"]) == 0,
          "TLC: the unfixed model shows the goodbye race and every safety guard has teeth")
    import shutil
    shutil.rmtree(os.environ["RM_TLA_RUNS"], ignore_errors=True)

print(f"\n{'FAIL' if fails else 'PASS'}: {fails} failure(s)")
sys.exit(1 if fails else 0)
