#!/usr/bin/env python3
"""selftest_facing_art_census.py -- the facing census on a fixture tree, then the lint on the repo.

Item: FACING_ART_CENSUS_FIND_UNWIRED_SIDES. Offline, a few seconds. The repo half fails when a
creature graphic sits on Graphic_Single while its facings are drawn (UNWIRED), or when a creature
owes facing art that facing_art_owed.json does not list (or lists after it landed)."""
import json
import os
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import facing_art_census as F  # noqa: E402

FAILS = []


def check(name, cond, detail=""):
    print(("PASS " if cond else "FAIL ") + name + ("" if cond else "  " + str(detail)))
    if not cond:
        FAILS.append(name)


def png(root, rel):
    p = os.path.join(root, rel + ".png")
    os.makedirs(os.path.dirname(p), exist_ok=True)
    open(p, "wb").close()


def stage(gclass, tex):
    g = "<graphicClass>%s</graphicClass>" % gclass if gclass else ""
    return "<li><bodyGraphicData><texPath>%s</texPath>%s</bodyGraphicData></li>" % (tex, g)


DEFS = """<?xml version="1.0" encoding="utf-8"?>
<Defs>
  <PawnKindDef Name="FxBase" Abstract="True"><lifeStages>%(base)s</lifeStages></PawnKindDef>
  <PawnKindDef><defName>Fx_Wired</defName><race>Fx_Wired</race>
    <lifeStages>%(wired)s</lifeStages></PawnKindDef>
  <PawnKindDef><defName>Fx_Unwired</defName><race>Fx_Unwired</race>
    <lifeStages>%(unwired)s<li><femaleGraphicData><texPath>A/Fem</texPath>
      <graphicClass>Graphic_Single</graphicClass></femaleGraphicData></li></lifeStages></PawnKindDef>
  <PawnKindDef><defName>Fx_Owed</defName><race>Fx_Owed</race>
    <lifeStages>%(owed)s</lifeStages></PawnKindDef>
  <PawnKindDef><defName>Fx_Partial</defName><race>Fx_Partial</race>
    <lifeStages>%(partial)s</lifeStages></PawnKindDef>
  <PawnKindDef><defName>Fx_Gap</defName><race>Fx_Gap</race>
    <lifeStages>%(gap)s</lifeStages></PawnKindDef>
  <PawnKindDef><defName>Fx_Vanilla</defName><race>Fx_Vanilla</race>
    <lifeStages>%(vanilla)s</lifeStages></PawnKindDef>
  <PawnKindDef ParentName="FxBase"><defName>Fx_Child</defName><race>Fx_Child</race>
    <lifeStages>%(child)s</lifeStages></PawnKindDef>
  <PawnKindDef ParentName="FxBase"><defName>Fx_NoInherit</defName><race>Fx_NoInherit</race>
    <lifeStages Inherit="False">%(child)s</lifeStages></PawnKindDef>
  <PawnKindDef><defName>Fx_West</defName><race>Fx_West</race>
    <lifeStages>%(west)s<li><stationaryGraphicData><texPath>A/Still</texPath>
      <graphicClass>Graphic_Single</graphicClass></stationaryGraphicData></li></lifeStages>
    <alternateGraphics><li><texPath>A/Alt</texPath><swimmingTexPath>A/AltSwim</swimmingTexPath></li>
    </alternateGraphics></PawnKindDef>
</Defs>
""" % {"base": stage("Graphic_Single", "A/Inherited"), "wired": stage(None, "A/Wired"),
       "unwired": stage("Graphic_Single", "A/Unwired"), "owed": stage("Graphic_Single", "A/Owed"),
       "partial": stage("Graphic_Single", "A/Partial"), "gap": stage("Graphic_Multi", "A/Gap"),
       "vanilla": stage("Graphic_Single", "Things/Building/Vanilla"),
       "child": stage("Graphic_Multi", "A/Wired"), "west": stage("Graphic_Single", "A/West")}


def fixture():
    with tempfile.TemporaryDirectory() as src:
        mod = os.path.join(src, "RimMandrake", "Fx")
        os.makedirs(os.path.join(mod, "Defs"))
        with open(os.path.join(mod, "Defs", "fx.xml"), "w") as fh:
            fh.write(DEFS)
        tex = os.path.join(src, "RimStarWars", "Other", "Textures")   # art in another tier
        for f in ("south", "east", "north"):
            png(tex, "A/Wired_" + f)
            png(tex, "A/Unwired_" + f)
            png(tex, "A/Fem_" + f)
        png(tex, "A/Unwired")
        png(tex, "A/Owed")
        png(tex, "A/Inherited")
        png(tex, "A/Partial_north")
        png(tex, "A/Gap_south")
        png(tex, "A/Gap_north")
        png(tex, "A/West_south")
        png(tex, "A/West_west")
        png(tex, "A/Still")
        for f in ("south", "east"):
            png(tex, "A/Alt_" + f)
        rows, stats = F.census(src)
        cls = {(r["kindDef"], r["slot"]): r["class"] for r in rows}
        check("reads every non-abstract kind", stats["kinds"] == 9, stats)
        check("Multi with full facings is clean", cls.get(("Fx_Wired", "lifeStage[0]/bodyGraphicData")) is None, cls)
        check("Single + drawn facings is UNWIRED",
              cls.get(("Fx_Unwired", "lifeStage[0]/bodyGraphicData")) == "UNWIRED", cls)
        check("female variant is censused too",
              cls.get(("Fx_Unwired", "lifeStage[1]/femaleGraphicData")) == "UNWIRED", cls)
        check("Single with no facings is OWED", cls.get(("Fx_Owed", "lifeStage[0]/bodyGraphicData")) == "OWED", cls)
        check("Single with one facing is PARTIAL",
              cls.get(("Fx_Partial", "lifeStage[0]/bodyGraphicData")) == "PARTIAL", cls)
        check("Multi missing _east is MULTI_GAP", cls.get(("Fx_Gap", "lifeStage[0]/bodyGraphicData")) == "MULTI_GAP", cls)
        check("Single on a vanilla texture is not classed",
              ("Fx_Vanilla", "lifeStage[0]/bodyGraphicData") in cls
              and cls[("Fx_Vanilla", "lifeStage[0]/bodyGraphicData")] is None, cls)
        check("lifeStages inherit parent-first (engine list append)",
              cls.get(("Fx_Child", "lifeStage[0]/bodyGraphicData")) == "OWED"
              and ("Fx_Child", "lifeStage[1]/bodyGraphicData") in cls, cls)
        check("Inherit=False drops the parent's stages",
              cls.get(("Fx_NoInherit", "lifeStage[0]/bodyGraphicData")) is None
              and ("Fx_NoInherit", "lifeStage[1]/bodyGraphicData") not in cls, cls)
        check("_west counts as the side (mirrored into east)",
              cls.get(("Fx_West", "lifeStage[0]/bodyGraphicData")) == "UNWIRED", cls)
        check("a still pose on one picture is not owed",
              ("Fx_West", "lifeStage[1]/stationaryGraphicData") in cls
              and cls[("Fx_West", "lifeStage[1]/stationaryGraphicData")] is None, cls)
        check("an alternate graphic takes the adult body's class",
              cls.get(("Fx_West", "alternateGraphics[0]")) == "UNWIRED", cls)
        check("an alternate's swimmingTexPath is censused",
              ("Fx_West", "alternateGraphics[0]/swimming") in cls, cls)
        owed = {"texPaths": ["A/Owed", "A/Partial", "A/Gap", "A/Inherited", "A/Gone"]}
        bad = F.problems(rows, owed)
        check("lint flags each UNWIRED row", sum(b.startswith("UNWIRED") for b in bad) == 4, bad)
        check("lint flags a stale owed entry", any(b.startswith("STALE A/Gone") for b in bad), bad)
        bad2 = F.problems(rows, {"texPaths": ["A/Owed"]})
        check("lint flags owed art nobody listed",
              any(b.startswith("UNLISTED PARTIAL") for b in bad2)
              and any(b.startswith("UNLISTED MULTI_GAP") for b in bad2), bad2)


def repo():
    rows, stats = F.census()
    check("sanity: the repo loader sees the bestiary", stats["kinds"] >= 200, stats)
    multi = [r for r in rows if r["graphicClass"] == "Graphic_Multi" and r["facings"]]
    check("sanity: the texture finder sees facing art", len(multi) >= 500, len(multi))
    owed = F.load_owed()
    check("owed list names its art item", bool(owed.get("item")), owed.get("item"))
    bad = F.problems(rows, owed)
    check("repo: no drawn-but-unwired facings, owed list exact", not bad, bad[:10])


if __name__ == "__main__":
    fixture()
    repo()
    print("%d FAIL" % len(FAILS) if FAILS else "ALL PASS")
    sys.exit(1 if FAILS else 0)
