#!/usr/bin/env python3
"""selftest_gravship_rotation_audit.py -- the gravship rotation classifier on fixtures, then the lint.

Item: GRAVSHIP_ROTATION_AUDIT_EVERY_BUILDING_TURNS. Offline, a few seconds. The fixture half proves
each class (FORCED_TURN, FIXED_FACING, FIXED_BUT_FACED, MULTI_NO_SIDE, MULTI_NO_FRONT, PICTURE_SPIN,
OK for doors / square pictures / vanilla art, UNRESOLVED, not-installable skips, DIRECTION_CODE) and
every --check failure (UNLISTED, UNFILED, STALE, UNREVIEWED). The repo half runs --check on the
real tree: it fails when a building of ours cannot turn with a gravship and no filed item owns it."""
import json
import os
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import gravship_rotation_audit as G  # noqa: E402

FAILS = []


def check(name, cond, detail=""):
    print(("PASS " if cond else "FAIL ") + name + ("" if cond else "  " + str(detail)))
    if not cond:
        FAILS.append(name)


def write(root, rel, text=""):
    p = os.path.join(root, rel)
    os.makedirs(os.path.dirname(p), exist_ok=True)
    with open(p, "w") as fh:
        fh.write(text)


def thing(dn, parent="BuildingBase", rot=None, size=None, gclass=None, tex=None, extra="", gextra=""):
    parts = ['<ThingDef ParentName="%s"><defName>%s</defName>' % (parent, dn),
             "<designationCategory>Misc</designationCategory>"]
    if rot is not None:
        parts.append("<rotatable>%s</rotatable>" % rot)
    if size:
        parts.append("<size>%s</size>" % size)
    if gclass or tex:
        parts.append("<graphicData>%s%s%s</graphicData>" % (
            "<graphicClass>%s</graphicClass>" % gclass if gclass else "",
            "<texPath>%s</texPath>" % tex if tex else "", gextra))
    parts.append(extra + "</ThingDef>")
    return "".join(parts)


def fixture(root):
    src = os.path.join(root, "src")
    m = "RimMandrake/ModA/"
    tx = m + "Textures/T/"
    for n in ("Forced", "Spin", "Sq", "Vanilla"):
        write(src, tx + n + ".png")
    for f in ("south", "east", "north"):
        write(src, tx + "Good_" + f + ".png")
        write(src, tx + "Faced_" + f + ".png")
    write(src, tx + "NoSide_south.png")
    write(src, tx + "NoFront_east.png")
    write(src, tx + "NoFront_north.png")
    defs = "".join([
        thing("F_Forced", rot="false", size="(3,2)", tex="T/Forced"),
        thing("F_Fixed", rot="false", size="(2,2)", tex="T/Sq"),
        thing("F_Faced", rot="false", size="(2,2)", gclass="Graphic_Multi", tex="T/Faced"),
        thing("F_Good", size="(3,2)", gclass="Graphic_Multi", tex="T/Good"),
        thing("F_NoSide", size="(3,1)", gclass="Graphic_Multi", tex="T/NoSide"),
        thing("F_NoFront", size="(1,4)", gclass="Graphic_Multi", tex="T/NoFront"),
        thing("F_Spin", size="(2,1)", tex="T/Spin"),
        thing("F_SquarePic", size="(2,2)", tex="T/Sq"),
        thing("F_VanillaArt", size="(3,2)", tex="Things/Building/Vanilla"),
        thing("F_Door", parent="DoorBase", size="(2,1)", tex="T/Spin"),
        thing("F_Orphan", parent="NoSuchParent"),
        thing("F_Coded", rot="false", extra="<thingClass>ModA.Building_Coded</thingClass>"),
        thing("F_Turned", rot="false", extra="<thingClass>ModA.Building_Turned</thingClass>"),
        thing("F_NoNudge", rot="false", extra="<thingClass>ModA.Building_Turned</thingClass>"
                                               "<comps><li Class=\"ModA.CompProperties_Nudge\" /></comps>"),
        thing("F_FlatSpin", size="(3,1)", tex="T/Spin", gextra="<drawRotated>false</drawRotated>"),
        thing("F_Custom", size="(3,2)", gclass="Graphic_Fancy", tex="T/Spin"),
        '<ThingDef Name="F_SpoutParent" ParentName="BuildingBase" Abstract="True"><comps>'
        '<li Class="ModA.CompProperties_Spout"><spoutOffset>(1,0,0)</spoutOffset></li></comps></ThingDef>',
        thing("F_SpoutDropped", parent="F_SpoutParent", rot="false",
              extra='<comps Inherit="False"><li Class="ModA.CompProperties_Plain" /></comps>'),
        thing("F_SpoutKept", parent="F_SpoutParent", rot="false"),
        thing("F_Offset", rot="false", extra="<comps><li Class=\"ModA.CompProperties_Spout\">"
                                              "<spoutOffset>(1,0,0)</spoutOffset></li></comps>"),
        '<ThingDef ParentName="BuildingBase"><defName>F_NotPlaceable</defName><rotatable>false</rotatable>'
        '<size>(3,2)</size></ThingDef>',
        '<ThingDef ParentName="ItemBase"><defName>F_Item</defName><designationCategory>Misc'
        '</designationCategory></ThingDef>',
    ])
    write(src, m + "Defs/Things.xml", "<Defs>%s</Defs>" % defs)
    write(src, m + "Source/Coded.cs",
          "namespace ModA {\n public class Building_Coded : Building {\n"
          "  void F() { var c = Position + IntVec3.West; }\n }\n}\n")
    write(src, m + "Source/Spout.cs",
          "namespace ModA {\n public class CompProperties_Spout : CompProperties { public IntVec3 spoutOffset; }\n}\n")
    write(src, m + "Source/Nudge.cs",
          "namespace ModA {\n public class CompProperties_Nudge : CompProperties {\n"
          "  public CompProperties_Nudge() { compClass = typeof(CompNudge); } }\n}\n")
    write(src, m + "Source/CompNudge.cs",
          "namespace ModA {\n public class CompNudge : ThingComp {\n"
          "  void F() { var c = parent.Position + IntVec3.East; }\n }\n}\n")
    write(src, m + "Defs/Broken.xml", "<Defs><ThingDef>")
    write(src, m + "Source/Turned.cs",
          "namespace ModA {\n public class Building_Turned : Building {\n"
          "  void F() { var c = Position + IntVec3.West.RotatedBy(Rotation); }\n }\n}\n")
    vanilla = {"nodes": {
        "BuildingBase": {"parent": None, "f": {"category": "Building", "thingClass": "Building"}, "l": {}},
        "DoorBase": {"parent": "BuildingBase", "f": {"thingClass": "Building_Door", "rotatable": "false"}, "l": {}},
        "ItemBase": {"parent": None, "f": {"category": "Item"}, "l": {}}}}
    vp = os.path.join(root, "vanilla.json")
    with open(vp, "w") as fh:
        json.dump(vanilla, fh)
    return src, vp


def main():
    with tempfile.TemporaryDirectory() as root:
        src, vp = fixture(root)
        rows, stats = G.audit(src, vp)
        cls = {r["def"]: r["cls"] for r in rows}
        want = {"F_Forced": "FORCED_TURN", "F_Fixed": "FIXED_FACING", "F_Faced": "FIXED_BUT_FACED",
                "F_Good": "OK", "F_NoSide": "MULTI_NO_SIDE", "F_NoFront": "MULTI_NO_FRONT",
                "F_Spin": "PICTURE_SPIN", "F_SquarePic": "OK", "F_VanillaArt": "OK", "F_Door": "OK",
                "F_Orphan": "UNRESOLVED", "F_Coded": "FIXED_FACING", "F_Offset": "FIXED_FACING",
                "F_Custom": "CUSTOM_GRAPHIC", "F_FlatSpin": "PICTURE_SPIN"}
        for d, c in want.items():
            check("class %s = %s" % (d, c), cls.get(d) == c, cls.get(d))
        flat = [r for r in rows if r["def"] == "F_FlatSpin"]
        check("drawRotated=false is named in PICTURE_SPIN's reason", flat and "drawRotated=false" in flat[0]["why"], flat)
        check("a broken Defs XML file is reported, not skipped silently",
              len(stats["parse_errors"]) == 1 and "Broken.xml" in stats["parse_errors"][0], stats["parse_errors"])
        check("PARSE_ERROR fails --check", any(x.startswith("PARSE_ERROR") for x in
                                               G.problems([], {}, set(), stats["parse_errors"])))
        check("not placeable / not a Building are skipped",
              "F_NotPlaceable" not in cls and "F_Item" not in cls and stats["skipped"] == 2, stats)
        dc = {r["def"]: r.get("direction_code", []) for r in rows}
        check("DIRECTION_CODE: fixed IntVec3.West in a file with no Rotation is flagged",
              [h["class"] for h in dc.get("F_Coded", [])] == ["Building_Coded"], dc.get("F_Coded"))
        check("DIRECTION_CODE: a comp with a vector offset and no Rotation in its file is flagged",
              [h["class"] for h in dc.get("F_Offset", [])] == ["CompProperties_Spout"], dc.get("F_Offset"))
        check("a file that turns its direction by Rotation is trusted (no DIRECTION_CODE)",
              dc.get("F_Turned") == [], dc.get("F_Turned"))
        check("compClass = typeof(X) leads from the props class to the comp's own file",
              [h["class"] for h in dc.get("F_NoNudge", [])] == ["CompNudge"], dc.get("F_NoNudge"))
        check('comps Inherit="False" drops the parent comp and its vector flag',
              dc.get("F_SpoutDropped") == [], dc.get("F_SpoutDropped"))
        check("an inherited comp keeps its vector flag",
              [h["class"] for h in dc.get("F_SpoutKept", [])] == ["CompProperties_Spout"], dc.get("F_SpoutKept"))
        defects = ["F_Forced", "F_Faced", "F_NoSide", "F_NoFront", "F_Spin", "F_Orphan", "F_Custom",
                   "F_FlatSpin"]
        coded = {"class": "Building_Coded", "file": "src/RimMandrake/ModA/Source/Coded.cs", "verdict": "ok", "why": "t"}
        spout = {"class": "CompProperties_Spout", "file": "src/RimMandrake/ModA/Source/Spout.cs", "verdict": "ok", "why": "t"}
        nudge = {"class": "CompNudge", "file": "src/RimMandrake/ModA/Source/CompNudge.cs", "verdict": "ok", "why": "t"}
        owed = {"groups": [{"group": "g", "item": "ITEM_A", "defs": defects}], "reviewed": [coded, spout, nudge]}
        check("clean owed list -> no problems", G.problems(rows, owed, {"ITEM_A"}) == [],
              G.problems(rows, owed, {"ITEM_A"}))
        p = G.problems(rows, owed, set())
        check("group item never filed -> UNFILED", any(x.startswith("UNFILED") for x in p), p)
        o2 = {"groups": [{"group": "g", "item": "ITEM_A", "defs": defects[1:] + ["F_Good"]}],
              "reviewed": [coded, spout, nudge]}
        p = G.problems(rows, o2, {"ITEM_A"})
        check("defect missing from groups -> UNLISTED", "UNLISTED F_Forced (FORCED_TURN)" in p, p)
        check("OK def listed -> STALE", any(x.startswith("STALE F_Good") for x in p), p)
        o3 = {"groups": [{"group": "g", "item": "ITEM_A", "defs": defects}], "reviewed": [spout, nudge]}
        p = G.problems(rows, o3, {"ITEM_A"})
        check("unreviewed direction code -> UNREVIEWED", any(x.startswith("UNREVIEWED F_Coded") for x in p), p)
        o4 = {"groups": [{"group": "g", "item": "ITEM_A", "defs": defects}],
              "reviewed": [dict(coded, verdict="defect"), spout, nudge]}
        p = G.problems(rows, o4, {"ITEM_A"})
        check("direction code judged a defect must be listed", "UNLISTED F_Coded (DIRECTION_CODE)" in p, p)
        o5 = {"groups": [{"group": "g", "item": "ITEM_A", "defs": defects[1:]}],
              "row_ok": {"F_Forced": "t", "F_Good": "t"}, "reviewed": [coded, spout, nudge]}
        p = G.problems(rows, o5, {"ITEM_A"})
        check("row_ok clears a defect row, and a row_ok on an OK row is STALE",
              p == ["STALE F_Good judged OK in row_ok but is no longer a defect row"], p)
        p = G.problems(rows, dict(owed, reviewed=[dict(coded, verdict="Defect"), spout, nudge]), {"ITEM_A"})
        check("a verdict outside ok/defect is BAD_REVIEW", any(x.startswith("BAD_REVIEW") for x in p), p)
        p = G.problems(rows, dict(owed, reviewed=owed["reviewed"] + [dict(coded, file="gone.cs")]), {"ITEM_A"})
        check("a review no row flags any more is STALE", any(x.startswith("STALE review") for x in p), p)
        ledger = os.path.join(root, "led.jsonl")
        with open(ledger, "w") as fh:
            fh.write(json.dumps({"seat": "BENCH", "event": "file", "id": "ITEM_A"}) + "\n")
            fh.write(json.dumps({"seat": "BENCH", "event": "note", "id": "ITEM_B"}) + "\n")
        check("filed_ids reads only file events", G.filed_ids(ledger) == {"ITEM_A"}, G.filed_ids(ledger))
    rows, stats = G.audit()
    check("repo sanity: the instrument sees our buildings (>100 installable, RM_HoseReel among them)",
          len(rows) > 100 and any(r["def"] == "RM_HoseReel" for r in rows), len(rows))
    hose = [r for r in rows if r["def"] == "RM_HoseReel"]
    check("repo: RM_HoseReel (the first case, HOSE_REEL_FIX_TURNS_WITH_THE_SHIP) turns", hose and hose[0]["cls"] == "OK",
          hose)
    bad = G.problems(rows, G.load_owed(), parse_errors=stats["parse_errors"])
    check("repo --check: every building that cannot turn is owned by a filed item", not bad, bad[:10])
    print("%d failed" % len(FAILS))
    return 1 if FAILS else 0


if __name__ == "__main__":
    sys.exit(main())
