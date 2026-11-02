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

OURS = """<Defs>
  <ThingDef ParentName="PlantBase" Name="T_OkBerry"><defName>T_OkBerry</defName>
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
  <ThingDef ParentName="TreeBase"><defName>T_PatchedTall</defName><plant><growDays>30</growDays></plant></ThingDef>
  <ThingDef ParentName="PlantBase"><defName>T_Unknown</defName>
    <plant><growDays>5</growDays><harvestYield>3</harvestYield><harvestedThingDef>T_NoSuchThing</harvestedThingDef></plant></ThingDef>
  <ThingDef ParentName="T_OkBerry"><defName>T_Child</defName><plant><growDays>2</growDays></plant></ThingDef>
  <ThingDef ParentName="PlantBase"><defName>T_PlantAdd</defName>
    <plant><growDays>3</growDays><harvestYield>1</harvestYield><harvestedThingDef>RawBerries</harvestedThingDef></plant></ThingDef>
  <ThingDef ParentName="T_OkBerry"><defName>T_Dup</defName></ThingDef>
</Defs>"""

# a second copy of T_Dup in another file, off the bar: a duplicate must not hide behind the good copy
OURS2 = """<Defs>
  <ThingDef ParentName="PlantBase"><defName>T_Dup</defName>
    <plant><growDays>1</growDays><harvestYield>10</harvestYield><harvestedThingDef>RawBerries</harvestedThingDef></plant></ThingDef>
</Defs>"""

PATCH = """<Patch>
  <Operation Class="PatchOperationSequence"><operations>
    <li Class="PatchOperationReplace"><xpath>/Defs/ThingDef[defName="T_PatchedTall"]/plant/visualSizeRange</xpath>
      <value><visualSizeRange>3~4</visualSizeRange></value></li>
    <li Class="PatchOperationAdd"><xpath>/Defs/ThingDef[defName="T_PlantAdd"]/plant</xpath>
      <value><harvestYield>30</harvestYield><minGrowthTemperature>1</minGrowthTemperature></value></li>
  </operations></Operation>
</Patch>"""


def part1():
    with tempfile.TemporaryDirectory() as td:
        data = os.path.join(td, "Data", "Core", "Defs")
        src = os.path.join(td, "src")
        os.makedirs(data)
        for t in pec.OUR_TIERS:
            os.makedirs(os.path.join(src, t, "M", "Defs"), exist_ok=True)
        os.makedirs(os.path.join(src, "RimMandrake", "M", "Patches"))
        open(os.path.join(data, "base.xml"), "w").write(LUDEON)
        open(os.path.join(src, "RimMandrake", "M", "Defs", "ours.xml"), "w").write(OURS)
        open(os.path.join(src, "RimMandrake", "M", "Patches", "p.xml"), "w").write(PATCH)
        open(os.path.join(src, "RimStarWars", "M", "Defs", "ours2.xml"), "w").write(OURS2)
        old_root, old_roster = pec.ROOT, pec.ROSTER
        pec.ROOT, pec.ROSTER = src, os.path.join(td, "none.xml")
        try:
            rows, meta = pec.census(game_data=os.path.join(td, "Data"), dump_path=os.path.join(td, "nodump.sqlite"))
        finally:
            pec.ROOT, pec.ROSTER = old_root, old_roster
    dups = [r for r in rows if r["defName"] == "T_Dup"]
    by = {r["defName"]: r for r in rows if r["defName"] != "T_Dup"}
    check(len(rows) == 12, "fixture: 12 plant rows (T_Dup twice), got %d" % len(rows))
    check(meta["plant_patches"] == 2, "fixture: 2 plant-field patches (minGrowthTemperature is not read), got %s"
          % meta["plant_patches"])
    check(len(dups) == 2 and sum(1 for r in dups if r["flags"]) == 1,
          "both copies of a duplicated defName are measured, the bad one flagged: %s" % dups)
    check(by.get("T_PlantAdd", {}).get("harvestYield") == 30 and "E2" in " ".join(by.get("T_PlantAdd", {}).get("flags", [])),
          "an Add on /plant setting harvestYield must apply: %s" % by.get("T_PlantAdd"))

    def flags(dn):
        return " ".join(by[dn]["flags"]) if dn in by else "MISSING"
    check(flags("T_OkBerry") == "", "T_OkBerry should be on the bar: " + flags("T_OkBerry"))
    check("E1" in flags("T_E1Gold") and "E2" not in flags("T_E1Gold"), "T_E1Gold must trip E1 only: " + flags("T_E1Gold"))
    check("E2" in flags("T_E2Berry") and "E1" not in flags("T_E2Berry"), "T_E2Berry must trip E2 only: " + flags("T_E2Berry"))
    check("E3" in flags("T_E3SmallTree"), "T_E3SmallTree (inherited WoodLog, drawn 2.0) must trip E3: " + flags("T_E3SmallTree"))
    check(by.get("T_E3SmallTree", {}).get("harvestYield") == 20, "T_E3SmallTree must inherit TreeBase's 20 logs")
    check("E4" in flags("T_E4FastTree") and "E3" not in flags("T_E4FastTree"),
          "T_E4FastTree (20 logs in 4 days, drawn 3.5) must trip E4 not E3: " + flags("T_E4FastTree"))
    check(flags("T_ClearedWood") == "" and by.get("T_ClearedWood", {}).get("product") is None,
          "an empty <harvestedThingDef></harvestedThingDef> must clear the inherited WoodLog: %s" % by.get("T_ClearedWood"))
    check(flags("T_PatchedTall") == "" and by.get("T_PatchedTall", {}).get("visualMax") == 4.0,
          "the Replace patch must raise T_PatchedTall to 4.0: %s" % by.get("T_PatchedTall"))
    check(by.get("T_Unknown", {}).get("unmeasured"), "an unknown product must read UNMEASURED: %s" % by.get("T_Unknown"))
    check(by.get("T_Child", {}).get("harvestYield") == 10 and "E2" in flags("T_Child"),
          "T_Child inherits 10 berries from an OUR parent, in 2 days, so E2: %s" % by.get("T_Child"))


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
