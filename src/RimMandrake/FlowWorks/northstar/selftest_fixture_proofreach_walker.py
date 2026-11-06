#!/usr/bin/env python3
"""Offline selftest for fixture_proofreach_walker.py (PROOFREACH_FIX_PAWNLESS_READ_HAS_NO_WALKER). Reds on: the bare
pawnless read (the source at 7479374edefa) passing; the wrapped read failing; the working tree failing; a commented-out
wrap passing; a missing method passing."""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import fixture_proofreach_walker as F  # noqa: E402

FAILS = []


def ok(c, m):
    print("%s %s" % ("PASS" if c else "FAIL", m))
    if not c:
        FAILS.append(m)


HEAD = "\t\tpublic static string ProofReach(string arg)\n\t\t{\n\t\t\tbool veto = true;\n%s\n\t\t\treturn \"x\";\n\t\t}\n"
BARE = ("\t\t\tbool reachPawnless = map.reachability.CanReach(p.Position, dest, PathEndMode.OnCell,\n"
        "\t\t\t\tTraverseParms.For(TraverseMode.PassDoors));")
WRAPPED = ("\t\t\tbool reachPawnless = RM_Patch_PathFollower_ReachWalker.As(p, () => map.reachability.CanReach(p.Position, "
           "dest,\n\t\t\t\tPathEndMode.OnCell, TraverseParms.For(TraverseMode.PassDoors)));")
COMMENTED = ("\t\t\tbool reachPawnless = // RM_Patch_PathFollower_ReachWalker.As(p, () =>\n\t\t\t\tmap.reachability.CanReach("
             "p.Position, dest, PathEndMode.OnCell, TraverseParms.For(TraverseMode.PassDoors));")
ok(F.judge(HEAD % BARE)[0] == "FAIL", "the bare pawnless read FAILS")
ok(F.judge(HEAD % WRAPPED)[0] == "PASS", "the read wrapped in ReachWalker.As PASSES")
ok(F.judge(HEAD % COMMENTED)[0] == "FAIL", "a commented-out wrap FAILS")
ok(F.judge("class X {}")[0] == "FAIL", "no ProofReach FAILS")
ok(F.judge(F.source("WORKTREE"))[0] == "PASS", "the source on disk passes")
try:
    old = F.source("7479374edefa")
except OSError:
    old = None
ok(old is None or F.judge(old)[0] == "FAIL", "the source at 7479374edefa (bare read) FAILS where history holds it")
print("FAILED: %d" % len(FAILS) if FAILS else "ALL PASS")
sys.exit(1 if FAILS else 0)
