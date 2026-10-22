"""Offline checks for reach_map_proof.py (REACH_MAP_BUILD_WALLS_AND_DEPTH_AGREE): its pure verdicts, its scene geometry, and
that every C# proof it calls exists in source and answers the word the script parses. No bridge."""
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import reach_map_proof as R  # noqa: E402

SRC = os.path.abspath(os.path.join(HERE, "..", "Source"))
fails = []


def check(name, cond):
    print("%-4s  %s" % ("ok" if cond else "FAIL", name))
    if not cond:
        fails.append(name)


def pr(can, found, scope="True", cls=2):
    return R.parse("REACHPAIR canReach=%s found=%s veto=x inScope=%s cls=%d band=2 agree=%s" % (can, found, scope, cls, can == found))


check("agree on a cut route, control reachable: PASS", R.pair_verdict(pr(False, False), pr(True, True)) == ("PASS", "MOD"))
check("can-fail: CanReach yes, A* no (the bug) is FAIL", R.pair_verdict(pr(True, False), pr(True, True)) == ("FAIL", "MOD"))
check("can-fail: control refused while A* finds it (a false no) is FAIL", R.pair_verdict(pr(False, False), pr(False, True)) == ("FAIL", "MOD"))
check("can-fail: control both False (everything says no) is FAIL", R.pair_verdict(pr(False, False), pr(False, False))[0] == "FAIL")
check("A* finds the subject's route: the scene did not cut it: UNMEASURED SITE", R.pair_verdict(pr(True, True), pr(True, True)) == ("UNMEASURED", "SITE"))
check("the veto never judged it: UNMEASURED SITE", R.pair_verdict(pr(False, False, scope="False"), pr(True, True)) == ("UNMEASURED", "SITE"))
check("a REFUSED read: UNMEASURED", R.pair_verdict(R.parse("REFUSED: no such pawn"), pr(True, True))[0] == "UNMEASURED")
check("no control (the swim row): agree alone", R.pair_verdict(pr(False, False, cls=16)) == ("PASS", "MOD"))
check("non-swimmer bit read from cls", R.has_bit(pr(False, False, cls=18), 16) and not R.has_bit(pr(False, False, cls=2), 16))

walls = set(R.compound_walls())
check("compound: the gate square and the gap are open", (-1, 0) not in walls and (-1, 4) not in walls and (0, 4) not in walls and (0, 0) not in walls)
check("compound: the inner wall closes x=0 elsewhere", all((0, z) in walls for z in range(-6, 7) if z not in (0, 4)))
check("compound: closed on three sides", all((-7, z) in walls for z in range(-7, 8)) and all((x, 7) in walls and (x, -7) in walls for x in range(-7, 0)))
ww = set(R.winch_walls())
check("winch site: drawbridge_proof scene A's walls", (-2, 1) in ww and (9, -1) in ww and (-3, 0) in ww and (10, 0) in ww and len(ww) == 26)
check("ring: Chebyshev 2..3 round the island", len(R.ring((0, 0), 2, 3)) == 49 - 9 and (0, 0) not in R.ring((0, 0), 2, 3))
check("rows and owed rows named", R.ROW_IDS[0] == "REACH_WINCH_SITE" and "REACH_RESIDUAL_SOAK" in R.OWED)

files = {}
for root, _, names in os.walk(SRC):
    if os.sep + "SelfTest" in root or os.sep + "obj" in root or os.sep + "bin" in root:
        continue
    for n in names:
        if n.endswith(".cs"):
            files[os.path.join(root, n)] = open(os.path.join(root, n), encoding="utf-8").read()
for (ty, method), word in R.PROOFS.items():
    cls = ty.rsplit(".", 1)[1]
    hit = [t for t in files.values() if re.search(r"\bclass %s\b" % cls, t) and re.search(r"public static string %s\(string arg\)" % method, t)]
    check("%s.%s exists (string arg)" % (cls, method), bool(hit))
    check("%s.%s answers %s" % (cls, method, word), bool(hit) and any(('"%s ' % word) in t for t in hit))

print("FAILED: %s" % fails if fails else "all ok")
sys.exit(1 if fails else 0)
