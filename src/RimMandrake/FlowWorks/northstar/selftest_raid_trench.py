"""Offline selftest of raid_trench_proof.py's storyteller restore (WSL python3; no bridge). Each case can go red."""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import raid_trench_proof as R  # noqa: E402


class MockBridge:
    """A MOCK, not the game: holds one bool and answers debug_settings like the tool does."""
    def __init__(self, st=True, refuse=False):
        self.st, self.refuse, self.sets = st, refuse, []

    def call(self, tool, **kw):
        assert tool == "jawa/debug_settings", tool
        if kw.get("action") == "list":
            return {"success": True, "fields": [{"name": "enableStoryteller", "value": self.st}]}
        if self.refuse:
            return {"success": False, "message": "refused"}
        self.sets.append(kw["value"])
        self.st = kw["value"]
        return {"success": True, "valueAfter": self.st}


bad = []


def chk(ok, why):
    if not ok:
        bad.append(why)
        print("FAIL", why)


b = MockBridge(True)
chk(R.storyteller_value(b) is True, "reads prior True")
chk(R.restore_storyteller(MockBridge(False), True) == (True, "enableStoryteller restored to True"), "restore to True confirmed")
chk(R.restore_storyteller(MockBridge(True), False)[0] is True, "restore to False (storyteller was off) honoured")
chk(R.restore_storyteller(MockBridge(False, refuse=True), True)[0] is False, "refused set is NOT a confirmed restore")
chk(R.restore_storyteller(MockBridge(False), None)[0] is False, "unread prior is UNMEASURED, never a guessed True")

# main() restores even when the body raises
b2 = MockBridge(True)


def boom(argv, hold):
    hold["B"], hold["prior"] = b2, True
    b2.st, hold["changed"] = False, True
    raise RuntimeError("body died")


orig = R._run
R._run = boom
try:
    R.main([])
    chk(False, "exception swallowed")
except RuntimeError:
    pass
finally:
    R._run = orig
chk(b2.st is True, "finally restored storyteller after the body raised")

# classify: a positionless sample is skipped (it used to raise on cheb(None)); a raider that died is never LEFT
C = (100, 100)
S = [dict(tick=250, raiders=[dict(id=1, x=103, z=100), dict(id=2, x=130, z=100)]),
     dict(tick=500, raiders=[dict(id=1, x=None, z=None), dict(id=2, x=130, z=100, dead=True)])]
w, d = R.classify(S, C)
chk("BREACH" in w, "classify: a raider sampled on the island is BREACH (%r)" % w)
chk(2 not in d["despawnedAlive"], "classify: a dead raider is not 'despawned alive' (%r)" % d)
chk(1 in d["despawnedAlive"], "classify: can-fail, a raider gone from the last sample alive is LEFT (%r)" % d)
# LADDER_PARITY_RAIDER_FELLS_TREE: oaks 10..15 east of the bank, disjoint from the ring; the verdict can go red
sp = R.tree_spots((125, 125), 6)
chk(len(set(sp)) == 6 and all(10 <= x - 132 <= 15 for x, _z in sp) and all(R.cheb(p_, (125, 125)) > 7 for p_ in sp),
    "trees: six distinct oak squares 10..15 east of the east bank, off the trench (%r)" % sp)
chk(R.tree_verdict(6, 5, False, 3)[0] == "PASS", "trees: a felled oak PASS")
chk(R.tree_verdict(6, 6, True, 3)[0] == "PASS", "trees: a chop job seen PASS")
chk(R.tree_verdict(6, 6, False, 3)[0] == "FAIL", "trees: can-fail, raiders near and every oak standing")
chk(R.tree_verdict(0, 0, False, 3)[0] == "UNMEASURED", "trees: nothing planted UNMEASURED")
chk(R.tree_verdict(6, 6, False, 0)[0] == "UNMEASURED", "trees: no raider near UNMEASURED")
chk(R.tree_verdict(6, None, False, 3)[0] == "UNMEASURED", "trees: uncounted UNMEASURED")
import ladder_wall_proof as LW  # noqa: E402
ok_reads = {k: "ladder=RM_LadderPortable faction=x mayClimb=%s letsOut=True" % w for k, _f, w in LW.CENSUS}
chk(LW.census_verdict(ok_reads)[0] == "PASS", "census: the table read back PASS")
chk(LW.census_verdict(dict(ok_reads, Muffalo=ok_reads["Cobra"]))[0] == "FAIL", "census: can-fail, a muffalo that may climb")
chk(LW.census_verdict(dict(ok_reads, Cobra=None))[0] == "UNMEASURED", "census: an unread pawn UNMEASURED")
chk(LW.pawn_num("Thing_Husky1234") == 1234 and LW.pawn_num(77) == 77 and LW.pawn_num(None) is None, "census: spawn id parse")
_S = [(0, None, None, "Wait"), (30, 127, 125, "RM_ClimbOverWall"), (60, 129, 125, "Wait_Combat"), (90, 117, 110, "Wait_Combat")]
chk(LW.first_crossing(_S, 128, (115, 135)) == ("PASS", _S[2]), "over wall: the FIRST east sample is the verdict, a later walk-off cannot hide it")
chk(LW.first_crossing(_S[:2], 128, (115, 135))[0] == "FAIL", "over wall: can-fail, still on the ladder side")
chk(LW.first_crossing([(30, 140, 140, "Goto")], 128, (115, 135))[0] == "FAIL", "over wall: east but outside the wall's z span (walked round) is not a crossing")
chk(LW.first_crossing(_S[:1], 128, (115, 135))[0] == "UNMEASURED", "over wall: no position read UNMEASURED")
print("selftest_raid_trench: %s" % ("FAIL" if bad else "ok"))
sys.exit(1 if bad else 0)
