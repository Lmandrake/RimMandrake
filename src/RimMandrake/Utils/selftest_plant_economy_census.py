#!/usr/bin/env python3
"""selftest_plant_economy_census.py — the census can SEE each rule, then the live tree is on the bar.

Part 1 (offline, synthetic): a fixture tree of tiny defs where each of E1-E4 must fire exactly where planted, an
inherited value must be resolved, an explicitly empty <harvestedThingDef></harvestedThingDef> must clear an
inherited WoodLog, a Replace patch on plant/visualSizeRange must be applied, and an unknown product must read
UNMEASURED, never ok. A census that cannot fail is not evidence (instrument_traps.md).
Part 2 (repo): the real census --check is 0 off-rule, 0 unmeasured. Skipped (exit 0, says so) only when the base
game's Data folder is absent, because the Ludeon parents (PlantBase, TreeBase) live there.
"""
import os
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import plant_economy_census as pec  # noqa: E402

FAIL = []


def check(cond, msg):
    if not cond:
        FAIL.append(msg)


LUDEON = """<Defs>
  <ThingDef Name="PlantBase" Abstract="True"><category>Plant</category>
    <plant><growDays>2</growDays><harvestYield>0</harvestYield></plant></ThingDef>
  <ThingDef Name="TreeBase" ParentName="PlantBase" Abstract="True">
    <plant><harvestedThingDef>WoodLog</harvestedThingDef><harvestTag>Wood</harvestTag><harvestYield>20</harvestYield>
      <visualSizeRange>1.3~2.0</visualSizeRange></plant></ThingDef>
  <ThingDef><defName>WoodLog</defName><statBases><MarketValue>1.2</MarketValue></statBases>
    <stuffProps><categories><li>Woody</li></categories></stuffProps></ThingDef>
  <ThingDef><defName>RawBerries</defName><statBases><MarketValue>1.2</MarketValue><Nutrition>0.05</Nutrition></statBases></ThingDef>
  <ThingDef><defName>Gold</defName><statBases><MarketValue>10</MarketValue></statBases></ThingDef>
</Defs>"""

# Every plant here is (name, expected flags prefix or "" for on the bar, or "UNMEASURED").
EXPECT = {
    "T_OkBerry": "", "T_E1Gold": "E1", "T_E2Berry": "E2", "T_E3SmallTree": "E3", "T_E4FastTree": "E4",
    "T_ClearedWood": "", "T_PatchedTall": "", "T_PatchMiss": "E3", "T_Unknown": "UNMEASURED", "T_Child": "E2",
    "T_PlantAdd": "E2", "T_NotTree": "E3", "T_Malformed": "UNMEASURED", "T_PParent": "E2", "T_PChild": "E2",
    "T_CondYes": "E2", "T_CondSkip": "", "T_Guarded": "UNMEASURED", "T_AddText": "E2", "T_LiWood": "E3",
    "T_InhFalse": "", "T_CycA": "UNMEASURED", "T_CycB": "UNMEASURED", "T_Orphan": "UNMEASURED",
    # second review pass (gpt_review2): whole-plant Replace, Remove of a block, a patch on a parent by @Name, Prepend,
    # and a nested Conditional whose untaken branch must stay untaken
    "T_WholeReplace": "UNMEASURED", "T_Removed": "UNMEASURED", "T_NameKid": "UNMEASURED", "T_Prepend": "",
    "T_Nested": "E2",
}

OURS = """<Defs>
  <ThingDef ParentName="PlantBase" Name="T_BerryParent"><defName>T_OkBerry</defName>
    <plant><growDays>6</growDays><harvestYield>10</harvestYield><harvestedThingDef>RawBerries</harvestedThingDef></plant></ThingDef>
  <ThingDef ParentName="PlantBase"><defName>T_E1Gold</defName>
    <plant><growDays>5</growDays><harvestYield>3</harvestYield><harvestedThingDef>Gold</harvestedThingDef></plant></ThingDef>
  <ThingDef ParentName="PlantBase"><defName>T_E2Berry</defName>
    <plant><growDays>3</growDays><harvestYield>10</harvestYield><harvestedThingDef>RawBerries</harvestedThingDef></plant></ThingDef>
  <ThingDef ParentName="TreeBase"><defName>T_E3SmallTree</defName><plant><growDays>30</growDays></plant></ThingDef>
  <ThingDef ParentName="TreeBase"><defName>T_E4FastTree</defName>
    <plant><growDays>4</growDays><visualSizeRange>2~3.5</visualSizeRange></plant></ThingDef>
  <ThingDef ParentName="TreeBase"><defName>T_ClearedWood</defName>
    <plant><growDays>30</growDays><harvestedThingDef></harvestedThingDef><harvestYield>0</harvestYield></plant></ThingDef>
  <ThingDef ParentName="TreeBase"><defName>T_PatchedTall</defName>
    <plant><growDays>30</growDays><visualSizeRange>1~2</visualSizeRange></plant></ThingDef>
  <ThingDef ParentName="TreeBase"><defName>T_PatchMiss</defName><plant><growDays>30</growDays></plant></ThingDef>
  <ThingDef ParentName="PlantBase"><defName>T_Unknown</defName>
    <plant><growDays>5</growDays><harvestYield>3</harvestYield><harvestedThingDef>T_NoSuchThing</harvestedThingDef></plant></ThingDef>
  <ThingDef ParentName="T_BerryParent"><defName>T_Child</defName><plant><growDays>2</growDays></plant></ThingDef>
  <ThingDef ParentName="PlantBase"><defName>T_PlantAdd</defName>
    <plant><growDays>3</growDays><harvestYield>1</harvestYield><harvestedThingDef>RawBerries</harvestedThingDef></plant></ThingDef>
  <ThingDef ParentName="T_BerryParent"><defName>T_Dup</defName></ThingDef>
  <ThingDef ParentName="TreeBase"><defName>T_NotTree</defName>
    <plant><growDays>30</growDays><visualSizeRange>3~4</visualSizeRange></plant></ThingDef>
  <ThingDef ParentName="PlantBase"><defName>T_Malformed</defName>
    <plant><growDays>soon</growDays><harvestYield>3</harvestYield><harvestedThingDef>RawBerries</harvestedThingDef></plant></ThingDef>
  <ThingDef ParentName="PlantBase" Name="T_PParentN"><defName>T_PParent</defName>
    <plant><growDays>30</growDays><harvestYield>1</harvestYield><harvestedThingDef>RawBerries</harvestedThingDef></plant></ThingDef>
  <ThingDef ParentName="T_PParentN"><defName>T_PChild</defName></ThingDef>
  <ThingDef ParentName="PlantBase"><defName>T_CondYes</defName>
    <plant><growDays>3</growDays><harvestYield>1</harvestYield><harvestedThingDef>RawBerries</harvestedThingDef></plant></ThingDef>
  <ThingDef ParentName="PlantBase"><defName>T_CondSkip</defName>
    <plant><growDays>3</growDays><harvestYield>1</harvestYield><harvestedThingDef>RawBerries</harvestedThingDef></plant></ThingDef>
  <ThingDef ParentName="PlantBase"><defName>T_Guarded</defName>
    <plant><growDays>3</growDays><harvestYield>1</harvestYield><harvestedThingDef>RawBerries</harvestedThingDef></plant></ThingDef>
  <ThingDef ParentName="PlantBase"><defName>T_AddText</defName>
    <plant><growDays>3</growDays><harvestYield>1</harvestYield><harvestedThingDef>RawBerries</harvestedThingDef></plant></ThingDef>
  <ThingDef Name="T_WoodyParentN" Abstract="True"><statBases><MarketValue>1</MarketValue></statBases>
    <stuffProps><categories><li>Woody</li></categories></stuffProps></ThingDef>
  <ThingDef ParentName="T_WoodyParentN"><defName>T_WoodyChild</defName>
    <stuffProps><categories><li>Metallic</li></categories></stuffProps></ThingDef>
  <ThingDef ParentName="T_WoodyParentN"><defName>T_NotWoody</defName>
    <stuffProps><categories Inherit="False"><li>Metallic</li></categories></stuffProps></ThingDef>
  <ThingDef ParentName="PlantBase"><defName>T_LiWood</defName>
    <plant><growDays>30</growDays><harvestYield>5</harvestYield><harvestedThingDef>T_WoodyChild</harvestedThingDef>
      <visualSizeRange>1~2</visualSizeRange></plant></ThingDef>
  <ThingDef ParentName="PlantBase"><defName>T_InhFalse</defName>
    <plant><growDays>30</growDays><harvestYield>5</harvestYield><harvestedThingDef>T_NotWoody</harvestedThingDef>
      <visualSizeRange>1~2</visualSizeRange></plant></ThingDef>
  <ThingDef ParentName="T_CycBN" Name="T_CycAN"><defName>T_CycA</defName><plant><growDays>3</growDays></plant></ThingDef>
  <ThingDef ParentName="T_CycAN" Name="T_CycBN"><defName>T_CycB</defName><plant><growDays>3</growDays></plant></ThingDef>
  <ThingDef ParentName="SomeDonorPlantBase"><defName>T_Orphan</defName></ThingDef>
  <ThingDef ParentName="PlantBase"><defName>T_WholeReplace</defName>
    <plant><growDays>30</growDays><harvestYield>1</harvestYield><harvestedThingDef>RawBerries</harvestedThingDef></plant></ThingDef>
  <ThingDef ParentName="PlantBase"><defName>T_Removed</defName>
    <plant><growDays>30</growDays><harvestYield>1</harvestYield><harvestedThingDef>RawBerries</harvestedThingDef></plant></ThingDef>
  <ThingDef ParentName="PlantBase" Name="T_NameBase" Abstract="True">
    <plant><growDays>30</growDays><harvestYield>1</harvestYield><harvestedThingDef>RawBerries</harvestedThingDef></plant></ThingDef>
  <ThingDef ParentName="T_NameBase"><defName>T_NameKid</defName></ThingDef>
  <ThingDef ParentName="PlantBase"><defName>T_Prepend</defName>
    <plant><growDays>1</growDays><harvestYield>1</harvestYield><harvestedThingDef>RawBerries</harvestedThingDef></plant></ThingDef>
  <ThingDef ParentName="PlantBase"><defName>T_Nested</defName>
    <plant><growDays>3</growDays><harvestYield>1</harvestYield><harvestedThingDef>RawBerries</harvestedThingDef></plant></ThingDef>
</Defs>"""

ROSTER = """<Defs><RimMandrake.ExplosiveGrowth.RM_ExplosiveGrowthRosterDef><defName>T_Roster</defName>
  <notTrees><li>T_NotTree</li></notTrees><treeRulesExempt /></RimMandrake.ExplosiveGrowth.RM_ExplosiveGrowthRosterDef></Defs>"""

# a second copy of T_Dup in another file, off the bar: a duplicate must not hide behind the good copy
OURS2 = """<Defs>
  <ThingDef ParentName="PlantBase"><defName>T_Dup</defName>
    <plant><growDays>1</growDays><harvestYield>10</harvestYield><harvestedThingDef>RawBerries</harvestedThingDef></plant></ThingDef>
</Defs>"""

PATCH = """<Patch>
  <Operation Class="PatchOperationSequence"><operations>
    <li Class="PatchOperationReplace"><xpath>/Defs/ThingDef[defName="T_PatchedTall"]/plant/visualSizeRange</xpath>
      <value><visualSizeRange>3~4</visualSizeRange></value></li>
    <li Class="PatchOperationReplace"><xpath>/Defs/ThingDef[defName="T_PatchMiss"]/plant/visualSizeRange</xpath>
      <value><visualSizeRange>3~4</visualSizeRange></value></li>
    <li Class="PatchOperationAdd"><xpath>/Defs/ThingDef[defName="T_PlantAdd"]/plant</xpath>
      <value><harvestYield>30</harvestYield><minGrowthTemperature>1</minGrowthTemperature></value></li>
    <li Class="PatchOperationReplace"><xpath>/Defs/ThingDef[defName="T_PParent"]/plant/harvestYield</xpath>
      <value><harvestYield>90</harvestYield></value></li>
    <li Class="PatchOperationAdd"><xpath>/Defs/ThingDef[defName="T_AddText"]/plant/harvestYield</xpath>
      <value>0</value></li>
  </operations></Operation>
  <Operation Class="PatchOperationConditional"><xpath>/Defs/ThingDef[defName="T_CondYes"]</xpath>
    <match Class="PatchOperationReplace"><xpath>/Defs/ThingDef[defName="T_CondYes"]/plant/harvestYield</xpath>
      <value><harvestYield>30</harvestYield></value></match>
    <nomatch Class="PatchOperationReplace"><xpath>/Defs/ThingDef[defName="T_CondSkip"]/plant/harvestYield</xpath>
      <value><harvestYield>100</harvestYield></value></nomatch>
  </Operation>
  <Operation Class="PatchOperationConditional"><xpath>/Defs/ThingDef[defName="T_NoSuchDef"]</xpath>
    <match Class="PatchOperationReplace"><xpath>/Defs/ThingDef[defName="T_CondSkip"]/plant/harvestYield</xpath>
      <value><harvestYield>100</harvestYield></value></match>
  </Operation>
  <Operation Class="PatchOperationReplace"><xpath>/Defs/ThingDef[defName="T_WholeReplace"]/plant</xpath>
    <value><plant><growDays>1</growDays><harvestYield>50</harvestYield></plant></value></Operation>
  <Operation Class="PatchOperationRemove"><xpath>/Defs/ThingDef[defName="T_Removed"]/plant</xpath></Operation>
  <Operation Class="PatchOperationReplace"><xpath>/Defs/ThingDef[@Name="T_NameBase"]/plant/harvestYield</xpath>
    <value><harvestYield>90</harvestYield></value></Operation>
  <Operation Class="PatchOperationAdd"><xpath>/Defs/ThingDef[defName="T_Prepend"]/plant/growDays</xpath>
    <order>Prepend</order><value>0</value></Operation>
  <Operation Class="PatchOperationConditional"><xpath>/Defs/ThingDef[defName="T_Nested"]</xpath>
    <match Class="PatchOperationConditional"><xpath>/Defs/ThingDef[defName="T_Nested"]/plant</xpath>
      <match Class="PatchOperationReplace"><xpath>/Defs/ThingDef[defName="T_Nested"]/plant/harvestYield</xpath>
        <value><harvestYield>30</harvestYield></value></match>
      <nomatch Class="PatchOperationReplace"><xpath>/Defs/ThingDef[defName="T_Nested"]/plant/harvestYield</xpath>
        <value><harvestYield>1</harvestYield></value></nomatch>
    </match>
  </Operation>
  <Operation Class="PatchOperationFindMod"><mods><li>Some Donor</li></mods>
    <match Class="PatchOperationReplace"><xpath>/Defs/ThingDef[defName="T_Guarded"]/plant/harvestYield</xpath>
      <value><harvestYield>100</harvestYield></value></match>
  </Operation>
</Patch>"""


def _build(td, roster=True):
    data = os.path.join(td, "Data", "Core", "Defs")
    src = os.path.join(td, "src")
    os.makedirs(data, exist_ok=True)
    for t in pec.OUR_TIERS:
        os.makedirs(os.path.join(src, t, "M", "Defs"), exist_ok=True)
    os.makedirs(os.path.join(src, "RimMandrake", "M", "Patches"), exist_ok=True)
    open(os.path.join(data, "base.xml"), "w").write(LUDEON)
    open(os.path.join(src, "RimMandrake", "M", "Defs", "ours.xml"), "w").write(OURS)
    open(os.path.join(src, "RimMandrake", "M", "Patches", "p.xml"), "w").write(PATCH)
    open(os.path.join(src, "RimStarWars", "M", "Defs", "ours2.xml"), "w").write(OURS2)
    open(os.path.join(td, "roster.xml"), "w").write(ROSTER)
    return src


def _run(td, src, roster):
    old_root, old_roster = pec.ROOT, pec.ROSTER
    pec.ROOT, pec.ROSTER = src, roster
    try:
        return pec.census(game_data=os.path.join(td, "Data"), dump_path=os.path.join(td, "nodump.sqlite"))
    finally:
        pec.ROOT, pec.ROSTER = old_root, old_roster


def part1():
    with tempfile.TemporaryDirectory() as td:
        src = _build(td)
        rows, meta = _run(td, src, os.path.join(td, "roster.xml"))
        rows_nr, _m = _run(td, src, os.path.join(td, "none.xml"))
        # --check on a tree this small must refuse: a census that sees a handful of plants is blind, not clean
        old_root, old_roster = pec.ROOT, pec.ROSTER
        pec.ROOT, pec.ROSTER = src, os.path.join(td, "roster.xml")
        try:
            import contextlib, io
            with contextlib.redirect_stdout(io.StringIO()):
                rc = pec.main(["--check", "--game-data", os.path.join(td, "Data"), "--dump", os.path.join(td, "x.sqlite")])
        finally:
            pec.ROOT, pec.ROSTER = old_root, old_roster
    check(rc == 1, "--check on a 25-plant fixture must exit 1 (blind), got %s" % rc)

    dups = [r for r in rows if r["defName"] == "T_Dup"]
    by = {r["defName"]: r for r in rows if r["defName"] != "T_Dup"}
    check(len(dups) == 2 and sum(1 for r in dups if r["flags"]) == 1,
          "both copies of a duplicated defName are measured, the bad one flagged: %s" % dups)
    for dn, want in EXPECT.items():
        r = by.get(dn)
        if r is None:
            check(False, "%s missing from the census" % dn)
            continue
        fl = " ".join(r["flags"])
        if want == "UNMEASURED":
            check(bool(r["unmeasured"]), "%s must be UNMEASURED: %s" % (dn, r))
        elif want == "":
            check(not r["flags"] and not r["unmeasured"], "%s must be on the bar AND measured: %s" % (dn, r))
        else:
            check(want in fl and not r["unmeasured"], "%s must trip %s (measured): %s" % (dn, want, r))
    check(by["T_E3SmallTree"]["harvestYield"] == 20, "T_E3SmallTree inherits TreeBase's 20 logs")
    check(by["T_PatchedTall"]["visualMax"] == 4.0, "a Replace on an explicit field applies")
    check(by["T_PatchMiss"]["visualMax"] == 2.0, "patches run BEFORE inheritance: a Replace on an inherited field misses")
    check(by["T_PChild"]["harvestYield"] == 90, "a patch on a parent reaches its child")
    check(by["T_AddText"]["harvestYield"] == 10, "Add of text onto 1 reads 10, as in game")
    check(by["T_CondSkip"]["harvestYield"] == 1, "a Conditional's untaken branch is not applied")
    check(by["T_ClearedWood"]["product"] is None, "an empty <harvestedThingDef></harvestedThingDef> clears WoodLog")
    check(by["T_Prepend"]["growDays"] == 1.0, "Prepend of 0 onto growDays 1 reads 01 = 1: %s" % by["T_Prepend"])
    check(by["T_Nested"]["harvestYield"] == 30, "a nested Conditional takes only its matched branch: %s" % by["T_Nested"])
    nr = {r["defName"]: r for r in rows_nr}
    check(nr["T_PatchedTall"]["unmeasured"], "no roster -> a wood row is UNMEASURED: %s" % nr["T_PatchedTall"])
    check(not nr["T_OkBerry"]["unmeasured"], "no roster -> a non-wood row is still measured")


def part2():
    game = next((g for g in pec.GAME_DATA_CANDIDATES if os.path.isdir(g)), None)
    if not game:
        print("part 2 SKIPPED: base game Data folder not found")
        return
    rows, meta = pec.census()
    off = [r["defName"] for r in rows if r["flags"]]
    unm = [r["defName"] for r in rows if r["unmeasured"]]
    check(len(rows) > 300, "live census sees only %d plant defs (instrument blind?)" % len(rows))
    check(not off, "live census off-rule: %s" % off[:10])
    check(not unm, "live census unmeasured: %s" % unm[:10])


if __name__ == "__main__":
    part1()
    part2()
    if FAIL:
        for f in FAIL:
            print("FAIL", f)
        sys.exit(1)
    print("selftest_plant_economy_census: OK")
