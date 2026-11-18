#!/usr/bin/env python3
"""selftest_plant_faults_discovery.py - the blind-challenge mutation harness consults every suite on disk, not the ones
its hand list remembers (RIMMANDRAKE_LIST_WALK_SUITE_IN_HARNESS_MUTANTS_SURVIVED).

  - discover_suites names a selftest_explosiveknockback*.py that exists but is absent from SUITES, and none that is listed;
  - the real tree: the walk_raid suite (which catches PF_V_FRAME_OVER_LOOSE and PF_V_FRAME_ROW_ALWAYS_PASS standalone) is
    now consulted;
  - rc 2 reads UNMEASURED (could not run here), never FAIL ("ran and missed") or PASS.
Fixtures live in a temp dir."""
import importlib.util
import os
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
PF = os.path.join(REPO, "design", "concepts", "ExplosiveKnockback", "version", "blind_challenge", "cycle_5", "lane2",
                  "plant_faults.py")
FAILS = []


def check(name, ok, got=""):
    print("%s %s%s" % ("ok  " if ok else "FAIL", name, "" if ok else "  got: %r" % (got,)))
    if not ok:
        FAILS.append(name)


spec = importlib.util.spec_from_file_location("plant_faults_under_test", PF)
pf = importlib.util.module_from_spec(spec)
spec.loader.exec_module(pf)          # importing runs nothing: main() is guarded

with tempfile.TemporaryDirectory() as repo:
    d = os.path.join(repo, "src", "RimMandrake", "ExplosiveKnockback")
    os.makedirs(d)
    for n in ("selftest_explosiveknockback_listed.py", "selftest_explosiveknockback_forgotten.py", "selftest_other.py"):
        open(os.path.join(d, n), "w").close()
    listed = {"T_LISTED": "python3 src/RimMandrake/ExplosiveKnockback/selftest_explosiveknockback_listed.py"}
    got = pf.discover_suites(repo, listed)
    check("an on-disk suite absent from the list is named, a listed one and an unrelated one are not",
          list(got) == ["T_AUTO_EXPLOSIVEKNOCKBACK_FORGOTTEN"]
          and got["T_AUTO_EXPLOSIVEKNOCKBACK_FORGOTTEN"].endswith("selftest_explosiveknockback_forgotten.py"), got)
    check("nothing unlisted: nothing to add", pf.discover_suites(repo, dict(listed, X="python3 src/RimMandrake/"
          "ExplosiveKnockback/selftest_explosiveknockback_forgotten.py")) == {})
real = pf.discover_suites(pf.REPO, pf.SUITES)
check("the real tree: the walk_raid suite is consulted", "T_AUTO_EXPLOSIVEKNOCKBACK_WALK_RAID" in real, sorted(real))
check("rc 0 PASS, rc 2 UNMEASURED, other FAIL",
      (pf.verdict_of(0), pf.verdict_of(2), pf.verdict_of(1)) == ("PASS", "UNMEASURED", "FAIL"))
print("selftest_plant_faults_discovery: %s" % ("FAIL (%d)" % len(FAILS) if FAILS else "PASS"))
sys.exit(1 if FAILS else 0)
