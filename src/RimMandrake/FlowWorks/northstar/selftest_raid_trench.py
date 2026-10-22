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
print("selftest_raid_trench: %s" % ("FAIL" if bad else "ok"))
sys.exit(1 if bad else 0)
