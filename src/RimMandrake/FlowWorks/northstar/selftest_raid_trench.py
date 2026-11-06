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
chk(R.tree_verdict(6, 6, True, 3)[0] == "FAIL", "trees: chop jobs seen but 6 of 6 standing is not FELLS (r55)")
chk(R.tree_verdict(6, 5, True, 3)[0] == "PASS", "trees: chopped and one felled PASS")
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
# RAID_TRENCH_FIX_OWN_JUMP_PACKS_FAIL (live 2026-10-29, raid_trench_20261029.json + gear_probe.txt): a storyteller raid,
# no --jump-packs, Human46558 (PirateWaster Scavenger) on the island in its own Apparel_PackJump, no raider ways
_g29 = {"success": True, "pawns": [{"thingId": "Human46558", "apparel": [
    {"def": "Apparel_Jacket", "defName": "Apparel_Jacket", "stuff": "Cloth", "hp": 114},
    {"def": "Apparel_PackJump", "defName": "Apparel_PackJump", "hp": 100}]}]}
_bare = {"success": True, "pawns": [{"thingId": "Human46566", "apparel": [{"def": "Apparel_Jacket", "defName": "Apparel_Jacket"}]}]}
chk(R.worn_jump_pack(_g29) is True, "jump pack: the 2026-10-29 pawn_get reply reads a worn Apparel_PackJump")
chk(R.worn_jump_pack(_bare) is False, "jump pack: apparel read, no pack -> False")
chk(R.worn_jump_pack({"success": False}) is None and R.worn_jump_pack(None) is None, "jump pack: unread -> None")
_p29 = {"Human46558": R.worn_jump_pack(_g29), "Human46566": R.worn_jump_pack(_bare)}
chk(R.maskswap_verdict(5, "PASS", ["Human46558"], [], False, _p29) == "UNMEASURED",
    "maskswap: the raid's own jump-pack raider on the island is masked, not FAIL (2026-10-29)")
chk(R.maskswap_verdict(5, "PASS", ["Human46566"], [], False, _p29) == "FAIL",
    "maskswap: can-fail, a crossed raider whose gear reads no jump pack")
chk(R.maskswap_verdict(5, "PASS", ["Human46558", "Human46566"], [], False, _p29) == "FAIL",
    "maskswap: one jumper does not excuse a packless crosser")
chk(R.maskswap_verdict(5, "PASS", ["HumanX"], [], False, _p29) == "UNMEASURED", "maskswap: an unread crosser is masked")
chk(R.ladder_breach_verdict(5, "PASS", False, ["Human46558"], False, _p29) == "UNMEASURED",
    "ladder breach: the raid's own jump-pack crossing is not a ladder FAIL (2026-10-29)")
chk(R.ladder_breach_verdict(5, "PASS", False, ["Human46566"], False, _p29) == "FAIL",
    "ladder breach: can-fail, a packless crosser with no ladders")
chk(R.ladder_breach_verdict(5, "PASS", False, [], False, _p29) == "FAIL", "ladder breach: came near, never crossed: stall FAIL")
chk(R.ladder_breach_verdict(5, "PASS", True, ["Human46566"], False, _p29) == "PASS", "ladder breach: both walls laddered and used")
chk(R.ladder_breach_verdict(1, "PASS", True, ["Human46566"], False, _p29) == "UNMEASURED", "ladder breach: under 2 near")
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
_S5 = "ORDERED taken=True from=(127, 0, 125) landing=(129, 0, 125) byLadder=True"   # bridge_run_1f ladder_wall_s5.json
chk(LW.one_way_verdict(_S5, 128)[0] == "PASS", "one way: the s5 walk-round (foot on the ladder side) is PASS")
chk(LW.one_way_verdict("NO_CROSSING roofed=False mightClimb=True", 128)[0] == "PASS", "one way: NO_CROSSING PASS")
chk(LW.one_way_verdict("ORDERED taken=True from=(129, 0, 125) landing=(127, 0, 125) byLadder=False", 128)[0] == "FAIL",
    "one way: can-fail, a crossing that starts east of the wall")
chk(LW.one_way_verdict("ERROR X: y", 128)[0] == "UNMEASURED", "one way: an error reply UNMEASURED")
chk(LW.one_way_verdict("ORDERED taken=True", 128)[0] == "UNMEASURED", "one way: ORDERED with no from UNMEASURED")


class FakeLadderBridge:
    """A FAKE, not the game: just enough of the bridge for ladder_wall_proof.main() to run its rows end to end. The
    first "climb:" crosses the colonist to the far side; the second (the ONE_WAY ask) answers `back`; later NO_CROSSING."""
    def __init__(self, back):
        self.back, self.climbs, self.xz, self.stops = back, 0, (0, 0), 0

    def call(self, tool, **kw):
        if tool == "jawa/map_info":
            return {"sizeX": 250, "sizeZ": 250}
        if tool == "jawa/list_pawns":
            return {"pawns": [{"id": "Thing_Human7", "x": self.xz[0], "z": self.xz[1]}]}
        if tool == "jawa/attack_target_probe":
            return {"curJob": "Wait_Combat"}
        if tool == "jawa/spawn_pawn":
            return {"pawns": [{"id": "Thing_%s9" % kw.get("kindDef")}]}
        if tool == "jawa/static_call" and kw.get("method") == "ProofLadderParity":
            arg = kw.get("args", "")
            if arg.startswith("may:"):
                return {"result": "ladder=RM_LadderPortable mayClimb=True"}
            self.climbs += 1
            if self.climbs == 1:
                self.xz = (129, 125)
                return {"result": "ORDERED taken=True from=(127, 0, 125) landing=(129, 0, 125) byLadder=True"}
            return {"result": self.back if self.climbs == 2 else "NO_CROSSING roofed=False"}
        return {}

    def probe_of(self, _typ, arg):
        if arg == "colonists":
            return {"pawns": [{"id": 7}]}
        if "=tp:" in arg:
            x, z = arg.split("=tp:")[1].split(",")
            self.xz = (int(x), int(z))
        if arg.endswith("=stop"):
            self.stops += 1
        return {}


def one_way_row(back):
    """Run ladder_wall_proof.main() on a FakeLadderBridge; -> (the emitted LADDER_PARITY_ONE_WAY status, the fake)."""
    import contextlib
    import io
    import json
    import tempfile
    import types
    fb = FakeLadderBridge(back)
    fake_v = types.ModuleType("validation_core")
    fake_v.Bridge = lambda: fb
    fake_v.clear_threat_structures = lambda B: "fake"
    fake_v.sweep_at_start = lambda B, made_map=False: {}
    fake_v.prepare_site = lambda *a_, **k_: None
    real = sys.modules.get("validation_core")
    sys.modules["validation_core"] = fake_v
    out = os.path.join(tempfile.mkdtemp(prefix="ladder_wall_selftest_"), "lw.json")
    try:
        with contextlib.redirect_stdout(io.StringIO()):
            LW.main([out])
    finally:
        if real is None:
            sys.modules.pop("validation_core", None)
        else:
            sys.modules["validation_core"] = real
    rows = {r_["id"]: r_["status"] for r_ in json.load(open(out, encoding="utf-8"))["rows"]}
    return rows.get("LADDER_PARITY_ONE_WAY"), fb


_ow, _fb = one_way_row(_S5)
chk(_ow == "PASS", "one way ROW: main() on the s5 walk-round reply (from=127, wallX=128) emits PASS, got %s" % _ow)
chk(_fb.stops == 1, "one way ROW: the walk-round job is stopped after an ORDERED reply")
_ow, _fb = one_way_row("ORDERED taken=True from=(129, 0, 125) landing=(127, 0, 125) byLadder=False")
chk(_ow == "FAIL", "one way ROW: can-fail, main() on a crossing from the far side (from=129) emits FAIL, got %s" % _ow)
_ow, _fb = one_way_row("NO_CROSSING roofed=False mightClimb=True")
chk(_ow == "PASS" and _fb.stops == 0, "one way ROW: main() on NO_CROSSING emits PASS and stops nothing, got %s" % _ow)
_ow, _fb = one_way_row("ERROR X: y")
chk(_ow == "UNMEASURED", "one way ROW: main() on an unreadable reply emits UNMEASURED, got %s" % _ow)
class FakeRaidBridge:
    """A FAKE, not the game: just enough of the bridge for raid_trench_proof.main() to run a STORYTELLER raid (no --direct,
    no --jump-packs) end to end, in the 2026-10-29 live shape: two hostiles come near, then Human46558 stands on the
    island; no raider way anywhere; the ring reads back at its dug depth (nothing filled). pawn_get answers `gear`."""
    def __init__(self, gear):
        self.gear, self.lists, self.pawn_gets = gear, 0, []

    def call(self, tool, **kw):
        if tool == "jawa/debug_settings":
            if kw.get("action") == "list":
                return {"fields": [{"name": "enableStoryteller", "value": True}]}
            return {"success": True, "valueAfter": kw.get("value")}
        if tool == "jawa/map_info":
            return {"sizeX": 250, "sizeZ": 250}
        if tool == "jawa/static_call" and kw.get("method") == "ProofClimb":
            return {"result": "mask derived=True bits=0x00"}
        if tool == "jawa/flowworks_excavation_drive":
            return {"depth": 4}
        if tool == "jawa/fire_raid":
            return {"success": True}
        if tool == "jawa/safe_advance":
            return {"executed": 250}
        if tool == "jawa/list_pawns":
            self.lists += 1
            far = (135, 125)
            isl = (125, 125) if self.lists >= 2 else (136, 126)
            return {"pawns": [
                {"id": "Human46558", "x": isl[0], "z": isl[1], "hostile": True, "spawned": True, "kindDef": "PirateWaster"},
                {"id": "Human46566", "x": far[0], "z": far[1], "hostile": True, "spawned": True, "kindDef": "PirateWaster"}]}
        if tool == "jawa/pawn_get":
            self.pawn_gets.append(kw.get("pawn"))
            return self.gear.get(kw.get("pawn"))
        return {}

    def probe_of(self, _typ, arg):
        return {"pawns": [{"id": 7}]} if arg == "colonists" else {}


def raid_rows(gear):
    """Run raid_trench_proof.main() on a FakeRaidBridge; -> ({row id: row}, the fake)."""
    import contextlib
    import io
    import json
    import tempfile
    import types
    fb = FakeRaidBridge(gear)
    fake_v = types.ModuleType("validation_core")
    fake_v.Bridge = lambda: fb
    fake_v.clear_threat_structures = lambda B: "fake"
    fake_v.sweep_at_start = lambda B, made_map=False: {}
    fake_v.prepare_site = lambda *a_, **k_: True
    real = sys.modules.get("validation_core")
    sys.modules["validation_core"] = fake_v
    out = os.path.join(tempfile.mkdtemp(prefix="raid_trench_selftest_"), "rt.json")
    try:
        with contextlib.redirect_stdout(io.StringIO()):
            R.main([out])
    finally:
        if real is None:
            sys.modules.pop("validation_core", None)
        else:
            sys.modules["validation_core"] = real
    return {r_["id"]: r_ for r_ in json.load(open(out, encoding="utf-8"))["rows"]}, fb


# RAID_TRENCH_FIX_OWN_JUMP_PACKS_FAIL, through _run (blind check 2026-11-06: the pure verdicts alone stayed green with the
# packs never read, or never passed): the live run must read each raider's pack and feed it to BOTH rows
_rr, _fr = raid_rows({"Human46558": _g29, "Human46566": _bare})
_ms, _lb = _rr.get("MASKSWAP_no_wall_crossing") or {}, _rr.get("RAID_LADDER_BREACH") or {}
chk("Human46558" in _fr.pawn_gets, "_run: reads Human46558's gear through jawa/pawn_get, got %s" % _fr.pawn_gets)
chk(_ms.get("status") == "UNMEASURED", "_run 2026-10-29 shape: MASKSWAP reads UNMEASURED, got %s" % _ms.get("status"))
chk(_lb.get("status") == "UNMEASURED", "_run 2026-10-29 shape: RAID_LADDER_BREACH reads UNMEASURED, got %s" % _lb.get("status"))
chk((_ms.get("detail") or {}).get("crossedJumpPacks") == {"Human46558": True},
    "_run: MASKSWAP detail crossedJumpPacks {Human46558: true}, got %s" % (_ms.get("detail") or {}).get("crossedJumpPacks"))
chk((_lb.get("detail") or {}).get("crossedJumpPacks") == {"Human46558": True},
    "_run: LADDER_BREACH detail crossedJumpPacks {Human46558: true}, got %s" % (_lb.get("detail") or {}).get("crossedJumpPacks"))
_nopack = {"success": True, "pawns": [{"thingId": "Human46558", "apparel": [{"def": "Apparel_Jacket", "defName": "Apparel_Jacket"}]}]}
_rr, _fr = raid_rows({"Human46558": _nopack, "Human46566": _bare})
chk((_rr.get("MASKSWAP_no_wall_crossing") or {}).get("status") == "FAIL",
    "_run can-fail: a packless crosser, no ways, MASKSWAP FAILs, got %s" % (_rr.get("MASKSWAP_no_wall_crossing") or {}).get("status"))
chk((_rr.get("RAID_LADDER_BREACH") or {}).get("status") == "FAIL",
    "_run can-fail: a packless crosser, no ladders, RAID_LADDER_BREACH FAILs, got %s" % (_rr.get("RAID_LADDER_BREACH") or {}).get("status"))
print("selftest_raid_trench: %s" % ("FAIL" if bad else "ok"))
sys.exit(1 if bad else 0)
