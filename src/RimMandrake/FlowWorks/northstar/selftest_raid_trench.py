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
# CAUSEWAY_DIAGNOSE_WAITS_AT_THE_LIP (live 2026-10-31): a --direct raid gets no shovel from PostProcessSpawnedPawns; the
# proof hands them out melee first, because a gunner with a sight line is held by vanilla's AIFightEnemies
chk(R.shovel_order([("g1", "Mercenary_Gunner"), ("s1", "Mercenary_Slasher"), ("g2", "Mercenary_Gunner"),
                    ("s2", "Mercenary_Slasher")]) == ["s1", "s2", "g1", "g2"], "shovels: melee first, then spawn order")
chk(R.shovel_order([("g1", None)]) == ["g1"], "shovels: an unread kind still gets one")
chk(R.give_shovels(None, ["x"], 0, (0, 0)) == [], "shovels: --shovels 0 hands none and calls nothing")
chk('"no shovel in the raid" if not res.get("shovelHolders")' in open(R.__file__).read(),
    "shovels: the shallow fill row with no shovel holder is UNMEASURED, not a mod FAIL")
# --fill-speed compression: a set is confirmed only by a read-back equal to the asked value; the restore is in main's finally


class SetBridge:
    """A MOCK, not the game: mod_settings_field get answers `after` whatever was set."""
    def __init__(self, after):
        self.after = after

    def call(self, tool, **kw):
        assert tool == "jawa/mod_settings_field", tool
        return {"success": True, "value": self.after}


chk(R.set_setting(SetBridge("4"), R.TRENCH_SETTINGS, "raiderFillSpeed", 4.0) == (True, "4"), "fill speed: read-back 4 confirmed")
chk(R.set_setting(SetBridge("0.5"), R.TRENCH_SETTINGS, "raiderFillSpeed", 4.0)[0] is False,
    "fill speed: can-fail, a set that read back unchanged is not confirmed")
chk(R.set_setting(SetBridge(None), R.TRENCH_SETTINGS, "raiderFillSpeed", 4.0)[0] is False, "fill speed: unread is not confirmed")
chk('if hold.get("fillSpeedPrior") is not None' in open(R.__file__).read().split("def _run")[0],
    "fill speed: main's finally restores the shipped value")
# MASKSWAP: a crossing over the PLAYER's ladders (--colony-ladders; filtered out of the raider ways) is legal, never a FAIL
chk(R.maskswap_verdict(3, "PASS", [5], [], staged_way=True) == "UNMEASURED",
    "maskswap: a crossing with colony ladders staged is masked, not a mask FAIL")
chk(R.maskswap_verdict(3, "PASS", [5], [], staged_way=False) == "FAIL", "maskswap: can-fail, a crossing with no way across")
chk(R.maskswap_verdict(3, "PASS", [5], [{"def_": "RM_LadderPortable"}], staged_way=False) == "UNMEASURED",
    "maskswap: a crossing over the raid's own ladder is masked")
chk(R.maskswap_verdict(3, "PASS", [], [], staged_way=False) == "PASS", "maskswap: no crossing PASS")
chk(R.maskswap_verdict(1, "PASS", [], [], staged_way=False) == "UNMEASURED", "maskswap: under 2 raiders near UNMEASURED")
chk(R.maskswap_verdict(3, "FAIL", [], [], staged_way=False) == "UNMEASURED", "maskswap: an unsealed island UNMEASURED")
# OWNER RULING 2026-10-31 (shallow fills only; deep: go around or shoot, never idle at the lip): the lip-idle instrument
# and the three rule rows
chk(R.job_of("duty=AssaultColony toil=X job=Wait_Wander giver=JobGiver_WanderAnywhere") == "Wait_Wander" and
    R.job_of("no pawn") is None, "rule: job token parse")
chk(R.job_read("job=Wait_Combat giver=JobGiver_AIFightEnemies started=1 enemy=Lachi Petrov | x") == "Wait_Combat+enemy"
    and R.job_read("job=Wait_Combat giver=G enemy=none") == "Wait_Combat"
    and R.lip_idlers([(t_, {"a": "Wait_Combat+enemy"}) for t_ in (500, 1000, 1500, 2000)]) == {},
    "rule: Wait_Combat facing an enemy is stand-and-shoot, not a lip idler (deep3_exposed); with no enemy it is idle")
_J = [(t_, {"a": "Wait_Combat", "b": "AttackStatic"}) for t_ in (500, 1000, 1500, 2000)]
chk(R.lip_idlers(_J) == {"a": 500}, "rule: 4 idle reads running is a lip idler; AttackStatic is not")
chk(R.lip_idlers(_J[:3]) == {}, "rule: 3 idle reads is not")
chk(R.lip_idlers(_J[:2] + [(1500, {"a": "Goto"})] + _J[2:]) == {}, "rule: a Goto between idle reads breaks the run")
chk(R.lip_idlers(_J[:2] + [(1500, {})] + _J[2:]) == {}, "rule: a raider gone from a read (left NEAR) breaks the run")
chk(R.rule_verdict("deep", None, [], None, {}, ["x"], []) == "PASS", "rule: deep, nothing filled, raid left PASS")
chk(R.rule_verdict("deep", None, [(1, 2, 6)], None, {}, ["x"], []) == "FAIL", "rule: can-fail, a deep pit filled")
chk(R.rule_verdict("deep", None, [], None, {"a": 500}, ["x"], []) == "FAIL", "rule: can-fail, a raider idled at the lip")
chk(R.rule_verdict("deep", None, [], None, {}, [], []) == "FAIL", "rule: can-fail, neither left nor shot (stall)")
chk(R.rule_verdict("nomelee", None, [], None, {}, [], ["g"]) == "PASS", "rule: no melee, gunners shooting PASS")
chk(R.rule_verdict("shallow", None, [(1, 2, 2)], 9000, {}, [], []) == "PASS", "rule: shallow filled and used in the raid PASS")
chk(R.rule_verdict("shallow", None, [(1, 2, 2)], 30000, {}, [], []) == "FAIL", "rule: can-fail, used after the raid's give-up")
chk(R.rule_verdict("shallow", None, [], None, {}, [], []) == "FAIL", "rule: can-fail, shallow not filled")
chk(R.rule_verdict("shallow", "--fill-speed compression", [(1, 2, 2)], 9000, {}, [], []) == "UNMEASURED",
    "rule: a compressed run is never a pass")
chk(R.rule_verdict("deep", None, None, None, {}, ["x"], []) == "UNMEASURED", "rule: an unread ring UNMEASURED")
chk('hold.get("settingsPrior")' in open(R.__file__).read().split("def _run")[0], "rule: main's finally restores --no-ladders")
chk("RAID_FILL_CAUSEWAY" not in open(R.__file__).read().split('"""', 2)[2].split("OWNER RULING 2026-10-31")[0],
    "rule: the deleted deep-fill row is not emitted")
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
