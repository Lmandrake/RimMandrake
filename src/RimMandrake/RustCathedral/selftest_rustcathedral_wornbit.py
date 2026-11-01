"""selftest_rustcathedral_wornbit.py -- RUSTCATHEDRAL_WORN_BIT_ARC_1, offline: validation.wornbit_problems is clean on the
shipped mod and reddens on each break it exists to catch (planted in a temp copy), and the arc kernel passes its criteria
under dotnet through the Attitude selftest project (--fuzz-only wornbit)."""
import importlib.util
import os
import shutil
import subprocess
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(os.path.dirname(os.path.dirname(HERE)))
FAILS = []


def check(name, cond, detail=""):
    print("%s  %s %s" % ("ok  " if cond else "FAIL", name, "" if cond else detail))
    if not cond:
        FAILS.append(name)


def _sub(path, old, new):
    with open(path, encoding="utf-8") as fh:
        text = fh.read()
    assert old in text, (path, old)
    with open(path, "w", encoding="utf-8") as fh:
        fh.write(text.replace(old, new, 1))


GOOD = {
    ("ProofDefs", ""): "DEFS restorationDefs 1 wornMass 250 refurbishedMass 250",
    ("ProofStage1", ""): "STAGE1 lone 0 two 100 band 2 stopped 100 calm 0 state Unbitted heads 1 quests 1 yards 1 yardfaction Pirate "
                         "yardCarries True pirateCarries True campaign False stage AwaitingHead",
    ("ProofYard", ""): "YARD fee 1500 timer 600000 days 10 staged Refurbishing after Failed quest EndedFailed yard gone",
    ("ProofRestoreGate", ""): "GATE all:null order:offered | " + " | ".join("%s:missing x (0/1) order:refused named:True" % p for p in (
        "RM_RefurbishedDrillHead", "RM_DeadSmartsteel", "ComponentSpacer", "RM_BoltShedCuriosity", "RM_CoolantEelCatch", "PowerfocusChip")),
    ("ProofBranch", "true"): "BRANCH goodwillDelta 0 droids none faction PlayerColony state Restored colonyMech True controllable False "
                             "gizmos 3 floats 1 draftable True irritationDelta 30 mayDigAfter5d False hostile False",
    ("ProofBranch", "false"): "BRANCH goodwillDelta 0 droids none faction null state Restored colonyMech False controllable False "
                              "gizmos 0 floats 0 draftable False irritationDelta -30 mayDigAfter5d False hostile False",
    ("ProofDig", ""): "DIG mined 2 left 0 sacred 1 warned 1 plateOnly True standingDelta -15",
    ("ProofTimedBegin", "true"): "TIMED begun cells 3",
    ("ProofTimedBegin", "false"): "TIMED begun cells 4",
    ("ProofNoBuff", ""): "NOBUFF colonists 3 stages 6 changed 0",
    ("ProofToggle", "none"): "TOGGLE unbit 1 dig 1 stops 1 service 1 politics 1 landing 1 freeBore 1 favour 1",
}
TIMED = {"true": "TIMED keep True mined 3 sacredMined 0 plateLeft 0 sacredLeft 0 job none",
         "false": "TIMED keep False mined 2 sacredMined 0 plateLeft 1 sacredLeft 1 job none"}
SETTINGS = {"wornBitKeepIrritation": 10, "wornBitFreeIrritation": -10, "wornBitPoliticalMultiplier": 3, "wornBitSacrilegeStanding": 15,
            "wornBitKeepGoodwill": -15, "wornBitFreeGoodwill": 15}


class FakeGame(object):
    """Answers the chain as a live bridge would, from canned proof lines, so every row's judging runs with no game."""

    def __init__(self, v, **lines):
        self.v, self.lines, self.tick, self.timed = v, lines, 1000, "true"

    def _ticks(self):
        return self.tick

    def __getattr__(self, name):
        raise AttributeError(name)

    def call(self, tool, **kw):
        if tool == "jawa/get_defs":
            return {"success": True, "foundCount": 9, "notFound": []}
        if tool == "jawa/mod_settings_field":
            return {"success": True, "value": str(SETTINGS[kw["field"]])}
        if tool == "jawa/static_call":
            method, args = kw["method"], kw.get("args", "")
            for over, line in self.lines.items():
                if over == method + args:
                    return {"result": line}
            if method == "ProofTimedBegin":
                self.timed = args
            if method == "ProofTimedEnd":
                return {"result": TIMED[self.timed]}
            if method == "ProofToggle" and args != "none":
                off = dict.fromkeys(self.v.WORNBIT_TOGGLE_EFFECTS[args], "0")
                base = self.v.wb_kv(GOOD[("ProofToggle", "none")])
                base.update(off)
                return {"result": "TOGGLE " + " ".join("%s %s" % kv for kv in base.items())}
            return {"result": GOOD[(method, args)]}
        self.tick += 2000
        return {"success": True}


def run_chain(v, session):
    from modcheck.suite import TestContext
    name_fn = dict(v.suite.chains)["worn_bit"]
    t = TestContext(session)
    import clockgate
    real = clockgate.advance_chunk

    def advance(sess, ticks, *a, **k):
        sess.tick += ticks
        return ticks
    clockgate.advance_chunk = advance
    try:
        name_fn(t)
    finally:
        clockgate.advance_chunk = real
    return {c.name: (c.verdict, c.detail) for c in t.components}


def live_chain(v):
    """worn_bit itself, every criterion a named row: no game UNMEASURED and naming the need, good lines green, each bad line red in ITS row."""
    if v.suite is None:
        check("modcheck imports", False)
        return
    want = ["live_game_present", "defs_resolve_and_heads_heavy", "stage1_lone_worker_two_workers_band_stop_quest_yard",
            "yard_timer_and_attack_ends_quest", "restoration_offered_and_refuses_naming_the_missing_item", "keep_branch",
            "kept_dig_counts_down_and_sacred_cell_recorded_free_bore_plate_only", "kept_dig_area_empties_over_game_time", "free_branch",
            "free_bores_plate_never_sacred_over_60000_ticks", "no_stage_buffs_a_colonist", "toggles_baseline_shows_every_effect"]
    want += ["toggle_off_removes_exactly_its_effect_" + x for x in v.WORNBIT_TOGGLES] + ["droid_goodwill_moved_by_the_multiple"]
    rows = run_chain(v, None)
    check("no game: every criterion is a row", sorted(rows) == sorted(want), sorted(set(want) ^ set(rows)))
    check("no game: nothing passes silently", all(x[0] == "UNMEASURED" for x in rows.values()), rows)
    check("no game: each row names what it needs", all("needs a live game" in x[1] for x in rows.values()), rows)
    fake = FakeGame(v)
    rows = run_chain(v, fake)
    green = {k: x for k, x in rows.items() if x[0] != "PASS"}
    check("good lines: the free tier stops only at the campaign's goodwill row", list(green) == ["droid_goodwill_moved_by_the_multiple"]
          and "RUT_Jawa_FreeDroidEnclaves" in green.get("droid_goodwill_moved_by_the_multiple", ("", ""))[1], green)
    campaign = dict(ProofBranchtrue=GOOD[("ProofBranch", "true")].replace("goodwillDelta 0 droids none", "goodwillDelta -45 droids RUT_Jawa_FreeDroidEnclaves"),
                    ProofBranchfalse=GOOD[("ProofBranch", "false")].replace("goodwillDelta 0 droids none", "goodwillDelta 45 droids RUT_Jawa_FreeDroidEnclaves"))
    rows = run_chain(v, FakeGame(v, **campaign))
    check("campaign lines: goodwill multiple passes", rows["droid_goodwill_moved_by_the_multiple"][0] == "PASS", rows["droid_goodwill_moved_by_the_multiple"])
    wrong = dict(campaign, ProofBranchtrue=campaign["ProofBranchtrue"].replace("goodwillDelta -45", "goodwillDelta -15"))
    rows = run_chain(v, FakeGame(v, **wrong))
    check("an unmultiplied goodwill reddens", rows["droid_goodwill_moved_by_the_multiple"][0] == "FAIL" or rows["keep_branch"][0] == "FAIL", rows["droid_goodwill_moved_by_the_multiple"])

    def red(label, key, old, new, row):
        args = key[1]
        line = GOOD[key]
        assert old in line, (key, old)
        got = run_chain(v, FakeGame(v, **{key[0] + args: line.replace(old, new)}))
        check("bad line: " + label, got.get(row, ("?",))[0] == "FAIL", got.get(row))

    s1, br, stage = ("ProofStage1", ""), ("ProofBranch", "true"), "stage1_lone_worker_two_workers_band_stop_quest_yard"
    fr = ("ProofBranch", "false")
    red("band IS 2 and the work went on", s1, "band 2 stopped 100", "band 2 stopped 140", stage)
    red("band never reached 2", s1, "band 2 stopped 100", "band 0 stopped 100", stage)
    red("a lone worker progressed", s1, "lone 0", "lone 5", stage)
    red("Pirate kept the extension with the campaign", s1, "yardfaction Pirate yardCarries True pirateCarries True campaign False",
        "yardfaction RUT_Jawa_Junkers yardCarries True pirateCarries True campaign True", stage)
    red("two yards", s1, "yards 1", "yards 2", stage)
    red("timer off the setting", ("ProofYard", ""), "timer 600000", "timer 60000", "yard_timer_and_attack_ends_quest")
    red("quest not failed", ("ProofYard", ""), "EndedFailed", "Ongoing", "yard_timer_and_attack_ends_quest")
    gate = "restoration_offered_and_refuses_naming_the_missing_item"
    red("order not offered", ("ProofRestoreGate", ""), "all:null order:offered", "all:null order:absent", gate)
    red("refusal does not name the item", ("ProofRestoreGate", ""), "RM_DeadSmartsteel:missing x (0/1) order:refused named:True",
        "RM_DeadSmartsteel:missing x (0/1) order:refused named:False", gate)
    red("keep state not Restored", br, "state Restored", "state Unbitted", "keep_branch")
    red("keep irritation unmultiplied", br, "irritationDelta 30", "irritationDelta 10", "keep_branch")
    red("free irritation unmultiplied", fr, "irritationDelta -30", "irritationDelta -10", "free_branch")
    red("free offers a float order", fr, "floats 0", "floats 1", "free_branch")
    red("free offers a gizmo", fr, "gizmos 0", "gizmos 2", "free_branch")
    red("free can be drafted", fr, "draftable False", "draftable True", "free_branch")
    red("a colonist was buffed", ("ProofNoBuff", ""), "changed 0", "changed 1", "no_stage_buffs_a_colonist")
    red("no colonist to watch", ("ProofNoBuff", ""), "colonists 3", "colonists 0", "no_stage_buffs_a_colonist")
    red("sacrilege without the cost", ("ProofDig", ""), "standingDelta -15", "standingDelta 0", "kept_dig_counts_down_and_sacred_cell_recorded_free_bore_plate_only")
    bad_off = "TOGGLE unbit 1 dig 1 stops 1 service 1 politics 1 landing 1 freeBore 1 favour 1"
    got = run_chain(v, FakeGame(v, ProofTogglewornBitPoliticsEnabled=bad_off))
    check("bad line: a toggle that removes nothing", got["toggle_off_removes_exactly_its_effect_wornBitPoliticsEnabled"][0] == "FAIL", got)
    too_far = bad_off.replace("politics 1 landing 1", "politics 0 landing 0")
    got = run_chain(v, FakeGame(v, ProofTogglewornBitPoliticsEnabled=too_far))
    check("bad line: a toggle that removes a neighbour's effect", got["toggle_off_removes_exactly_its_effect_wornBitPoliticsEnabled"][0] == "FAIL", got)
    check("judge: a sacred bore reddens", v.wb_timed_problem(TIMED["false"].replace("sacredMined 0", "sacredMined 1"), False) is not None)
    check("judge: nothing bored in 60000 ticks reddens", v.wb_timed_problem(TIMED["false"].replace("mined 2", "mined 0"), False) is not None)
    check("judge: a dig area left full reddens", v.wb_timed_problem(TIMED["true"].replace("plateLeft 0", "plateLeft 2"), True) is not None)
    got = run_chain(v, FakeGame(v, ProofNoBuff="NOBUFF refused: x"))
    check("a proof that refuses is UNMEASURED, not a pass", got["no_stage_buffs_a_colonist"][0] == "UNMEASURED", got["no_stage_buffs_a_colonist"])


def main():
    spec = importlib.util.spec_from_file_location("rc_v", os.path.join(HERE, "validation.py"))
    v = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(v)
    bad, unmeasured = v.wornbit_problems()
    check("shipped: arc clean", bad == [], bad)
    check("shipped: campaign files seen", unmeasured == [], unmeasured)

    def planted(label, rel, old, new, expect):
        tmp = tempfile.mkdtemp()
        try:
            for d in ("Defs", "Patches", "Source"):
                shutil.copytree(os.path.join(HERE, d), os.path.join(tmp, d), ignore=shutil.ignore_patterns("obj", "bin", "__pycache__"))
            _sub(os.path.join(tmp, rel), old, new)
            got, _u = v.wornbit_problems(mod_root=tmp)
            check(label, any(expect in g for g in got), got)
        finally:
            shutil.rmtree(tmp)

    heads = os.path.join("Defs", "ThingDefs_Items", "RM_WornBitDrillHeads.xml")
    misc = os.path.join("Defs", "Misc", "RM_WornBit.xml")
    races = os.path.join("Defs", "ThingDefs_Races", "RM_Borehulk.xml")
    planted("light head reddens", heads, "<Mass>250</Mass>", "<Mass>25</Mass>", "mass")
    planted("lost job reddens", os.path.join("Defs", "JobDefs", "RM_WornBitJobs.xml"), "<defName>RM_Job_RestoreBorehulk</defName>",
            "<defName>RM_Job_RestoreBorehulkX</defName>", "RM_Job_RestoreBorehulk")
    planted("a dropped part reddens", misc, "<PowerfocusChip>1</PowerfocusChip>", "", "restoration parts")
    planted("a short count reddens", misc, "<RM_DeadSmartsteel>12<", "<RM_DeadSmartsteel>2<", "RM_DeadSmartsteel")
    planted("inherited overseer reddens", races, '<comps Inherit="False">', "<comps>", "mechanitor")
    planted("no dig job reddens", os.path.join("Defs", "ThinkTreeDefs", "RM_ThinkTree_Borehulk.xml"),
            '<li Class="RimMandrake.RustCathedral.RM_JobGiver_BorehulkWork" />', "", "dig job")
    planted("no refurbisher reddens", os.path.join("Patches", "RM_WornBit.xml"), 'FactionDef[defName="Pirate"]', 'FactionDef[defName="Nobody"]', "Pirate")
    planted("a buff reddens", os.path.join("Source", "RustCathedral", "RM_WornBitDig.cs"), "comp.cellsMined++;",
            "comp.cellsMined++; pawn.health.AddHediff(null);", "buff")
    tmp = tempfile.mkdtemp()
    try:
        bad_patch = os.path.join(tmp, "p.xml")
        with open(bad_patch, "w", encoding="utf-8") as fh:
            fh.write('<Patch><Operation MayRequire="x" Class="PatchOperationAdd" /></Patch>')
        got, _u = v.wornbit_problems(rut_patch=bad_patch)
        check("a thin campaign patch reddens", any("campaign patch lacks" in g for g in got), got)
        check("a guarded top-level MayRequire reddens", any("MayRequire" in g for g in got), got)
    finally:
        shutil.rmtree(tmp)
    check("no campaign patch says UNMEASURED", any("campaign patch" in u for u in v.wornbit_problems(rut_patch="/nonexistent")[1]))

    live_chain(v)

    sys.path.insert(0, os.path.join(REPO, "src", "RimMandrake", "Utils"))
    fuzz = os.path.join(REPO, "src", "RimMandrake", "Utils", "selftest_rustcathedral_attitude_fuzz.py")
    r = subprocess.run([sys.executable, fuzz, "--fuzz-only", "wornbit"], capture_output=True, text=True, timeout=400)
    print("\n".join(x for x in r.stdout.splitlines() if x.startswith(("FAIL", "WORNBIT"))))
    check("arc kernel passes under dotnet", r.returncode == 0 and "WORNBIT PASS" in r.stdout, (r.stdout + r.stderr)[-600:])
    print("%s (%d failures)" % ("PASS" if not FAILS else "FAIL", len(FAILS)))
    return 1 if FAILS else 0


if __name__ == "__main__":
    sys.exit(main())
