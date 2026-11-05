#!/usr/bin/env python3
"""facing_art_census.py -- which creature graphics are stuck on one facing.

VERSION 1.0 (2026-11-05). Item: FACING_ART_CENSUS_FIND_UNWIRED_SIDES.
Owner, 2026-11-03: "Please file a ticket to scan for other creatures with facing art that simply
isn't wired up." Trigger: RM_Tellurox walked without turning.

WHAT IT READS (offline, repo only, deterministic)
================================================
Every PawnKindDef under src/RimMandrake, src/RimStarWars and src/RimUtinni (all three tiers),
ParentName resolved across the three tiers. lifeStages is a list, so it follows the engine's
XML inheritance: a child's <li>s are appended to its parent's unless Inherit="False". Every
lifeStage's bodyGraphicData, femaleGraphicData, swimmingGraphicData and femaleSwimmingGraphicData
(and stationaryGraphicData) is a row, and so is each alternateGraphics entry (texPath and
swimmingTexPath, drawn in the class of the adult graphic they replace unless they carry their own
graphicData). dessicatedBodyGraphicData is a corpse and is
not a facing graphic. A graphic with no graphicClass is Graphic_Multi (PawnKindLifeStage sets it).

THE CLASSES (Graphic_Single rows, plus the Graphic_Multi gaps; any other class is counted, not judged)
UNWIRED  Graphic_Single, and <texPath>_south.png plus _east.png or _west.png exist in a Textures
         folder of ours: the art is drawn, the def never turns it on. Fix: -> Graphic_Multi.
         (Graphic_Multi fills a missing _north from _south, and mirrors _east and _west into
         each other.)
PARTIAL  Graphic_Single, some facing PNG exists beside texPath but not a front and a side:
         wiring it would show a wrong side. Art owed, like OWED.
OWED     Graphic_Single, <texPath>.png is ours, and no facing PNG beside it: one picture only.
         (A Single on a vanilla/DLC texture is not ours to draw and is not classed; nor is a
         stationaryGraphicData on one picture -- a still pose -- unless its facings are drawn.)
MULTI_GAP Graphic_Multi whose texPath has facing art in our tree but no _south or no side: the
         engine fills the hole from another facing (a missing east shows the north view sideways).
         A Multi texPath with no facing of ours at all is vanilla/DLC art and is not judged.

--check exits 1 if any UNWIRED row exists, or an OWED/PARTIAL/MULTI_GAP texPath is missing from
facing_art_owed.json (the list the art pipeline item carries), so neither can recur unseen; a
listed texPath no longer owed is STALE and fails too, so the list cannot outlive its art.
Blind spots: a Patches/ operation that rewrites a graphicClass is not applied; an alternate graphic
is judged in the ADULT stage's class only (a kind whose stages mix Single and Multi would be misread;
none does today).

USAGE
    python3 src/RimMandrake/Utils/facing_art_census.py                 # table to stdout
    python3 src/RimMandrake/Utils/facing_art_census.py --md out.md --json rows.json
    python3 src/RimMandrake/Utils/facing_art_census.py --check         # the lint gate
"""
from __future__ import annotations

import argparse
import glob
import json
import os
import sys
import xml.etree.ElementTree as ET

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
TIERS = ("RimMandrake", "RimStarWars", "RimUtinni")
OWED_FILE = os.path.join(HERE, "facing_art_owed.json")
GRAPHIC_FIELDS = ("bodyGraphicData", "femaleGraphicData", "swimmingGraphicData",
                  "femaleSwimmingGraphicData", "stationaryGraphicData")
FACINGS = ("south", "east", "north", "west")
OWED_CLASSES = ("OWED", "PARTIAL", "MULTI_GAP")


def _txt(e, tag):
    c = e.find(tag) if e is not None else None
    return c.text.strip() if c is not None and c.text and c.text.strip() else None


def load(src_root):
    """(kinds by Name, kinds by defName, Textures dirs, xml files parsed) for every tier."""
    by_name, by_def, tex_dirs, nfiles = {}, {}, [], 0
    for tier in TIERS:
        base = os.path.join(src_root, tier)
        for p in sorted(glob.glob(os.path.join(base, "**", "*.xml"), recursive=True)):
            if os.sep + "Defs" + os.sep not in p:
                continue
            try:
                root = ET.parse(p).getroot()
            except ET.ParseError:
                continue
            nfiles += 1
            if root.tag != "Defs":
                continue
            for e in root:
                if not isinstance(e.tag, str) or e.tag.split(".")[-1] != "PawnKindDef":
                    continue
                e.set("_file", os.path.relpath(p, REPO))
                if e.get("Name"):
                    by_name[e.get("Name")] = e
                dn = _txt(e, "defName")
                if dn and (e.get("Abstract") or "").lower() != "true":
                    by_def[dn] = e
        tex_dirs += sorted(d for d in glob.glob(os.path.join(base, "**", "Textures"), recursive=True)
                           if os.path.isdir(d))
    return by_name, by_def, tex_dirs, nfiles


def _chain(e, by_name):
    """[self, parent, grandparent, ...] by ParentName, stopping at an unknown (vanilla) parent."""
    out, seen = [e], set()
    while e is not None and e.get("ParentName") and e.get("ParentName") not in seen:
        seen.add(e.get("ParentName"))
        e = by_name.get(e.get("ParentName"))
        if e is not None:
            out.append(e)
    return out


def _list(e, by_name, tag):
    """A list field as the engine inherits it: parent's <li>s first, child's appended."""
    lis = []
    for node in _chain(e, by_name):
        f = node.find(tag)
        if f is None:
            continue
        lis = [li for li in f if li.tag == "li"] + lis
        if (f.get("Inherit") or "").lower() == "false":
            break
    return lis


def _owner_file(e, by_name, tag):
    for node in _chain(e, by_name):
        if node.find(tag) is not None:
            return node.get("_file")
    return e.get("_file")


def facings(tex, tex_dirs):
    found = set()
    for d in tex_dirs:
        for f in FACINGS:
            if os.path.isfile(os.path.join(d, tex + "_" + f + ".png")):
                found.add(f)
    return found


def census(src_root=None):
    src_root = src_root or os.path.join(REPO, "src")
    by_name, by_def, tex_dirs, nfiles = load(src_root)
    rows = []
    for dn in sorted(by_def):
        k = by_def[dn]
        race = _txt(k, "race") or next((_txt(n, "race") for n in _chain(k, by_name)
                                        if _txt(n, "race")), None)
        where = _owner_file(k, by_name, "lifeStages")
        stages = _list(k, by_name, "lifeStages")
        for i, li in enumerate(stages):
            for fld in GRAPHIC_FIELDS:
                g = li.find(fld)
                if g is not None:
                    rows.append(_row(dn, race, "lifeStage[%d]/%s" % (i, fld), g, where, tex_dirs))
        # An alternate graphic is drawn with the class of the lifeStage graphic it replaces
        # (the adult's, here) unless it carries its own graphicData.
        adult = {fld: _cls(next((li.find(fld) for li in reversed(stages)
                                 if li.find(fld) is not None), None))
                 for fld in ("bodyGraphicData", "swimmingGraphicData")}
        alt_file = _owner_file(k, by_name, "alternateGraphics")
        for i, li in enumerate(_list(k, by_name, "alternateGraphics")):
            g = li.find("graphicData")
            src = g if g is not None else li
            if _txt(src, "texPath"):
                rows.append(_row(dn, race, "alternateGraphics[%d]" % i, src, alt_file, tex_dirs,
                                 gclass=_txt(src, "graphicClass") or adult["bodyGraphicData"]))
            if _txt(li, "swimmingTexPath"):
                rows.append(_row(dn, race, "alternateGraphics[%d]/swimming" % i, li, alt_file,
                                 tex_dirs, tex=_txt(li, "swimmingTexPath"),
                                 gclass=adult["swimmingGraphicData"]))
    return rows, {"files": nfiles, "kinds": len(by_def), "textureDirs": len(tex_dirs)}


def _cls(g):
    return (_txt(g, "graphicClass") or "Graphic_Multi").split(".")[-1]


def _sides(f):
    """Both a front and a side: _south, and _east or _west (each mirrors the other)."""
    return "south" in f and bool({"east", "west"} & f)


def _row(dn, race, slot, g, where, tex_dirs, tex=None, gclass=None):
    tex = tex or _txt(g, "texPath")
    gclass = (gclass or _cls(g)).split(".")[-1]
    r = {"kindDef": dn, "race": race, "slot": slot, "texPath": tex, "graphicClass": gclass,
         "file": where, "facings": [], "class": None}
    if not tex:
        return r
    f = facings(tex, tex_dirs)
    r["facings"] = [x for x in FACINGS if x in f]
    if gclass != "Graphic_Single":
        if gclass == "Graphic_Multi" and f and not _sides(f):
            r["class"] = "MULTI_GAP"
        return r
    if not f and not any(os.path.isfile(os.path.join(d, tex + ".png")) for d in tex_dirs):
        return r   # a vanilla/DLC texture drawn on purpose (e.g. a turret base): not our art
    r["class"] = "UNWIRED" if _sides(f) else ("PARTIAL" if f else "OWED")
    if r["class"] != "UNWIRED" and slot.endswith("stationaryGraphicData"):
        r["class"] = None   # a still pose (dormant, nodule) on one picture is a choice, not a debt
    return r


def load_owed(path=OWED_FILE):
    if not os.path.isfile(path):
        return {"item": None, "texPaths": []}
    with open(path) as fh:
        return json.load(fh)


def problems(rows, owed):
    listed = set(owed.get("texPaths", []))
    bad = ["UNWIRED %s %s %s (%s)" % (r["kindDef"], r["slot"], r["texPath"], r["file"])
           for r in rows if r["class"] == "UNWIRED"]
    bad += ["UNLISTED %s %s %s %s: add to facing_art_owed.json" %
            (r["class"], r["kindDef"], r["slot"], r["texPath"])
            for r in rows if r["class"] in OWED_CLASSES and r["texPath"] not in listed]
    owed_now = {r["texPath"] for r in rows if r["class"] in OWED_CLASSES}
    bad += ["STALE %s is listed in facing_art_owed.json but no longer owed: remove it" % t
            for t in sorted(listed - owed_now)]
    return bad


def table(rows, stats):
    single = [r for r in rows if r["graphicClass"] == "Graphic_Single"]
    classed = [r for r in rows if r["class"]]
    out = ["# Facing art census (%s)" % "FACING_ART_CENSUS_FIND_UNWIRED_SIDES", "",
           "%d PawnKindDefs, %d graphic slots, %d on Graphic_Single; %d Defs files read, %d "
           "Textures dirs." % (stats["kinds"], len(rows), len(single), stats["files"],
                               stats["textureDirs"]), ""]
    for cls in ("UNWIRED",) + OWED_CLASSES:
        rs = [r for r in classed if r["class"] == cls]
        out += ["## %s (%d)" % (cls, len(rs)), ""]
        if rs:
            out += ["| kindDef | race | slot | texPath | facings on disk | file |",
                    "|---|---|---|---|---|---|"]
            out += ["| %s | %s | %s | `%s` | %s | `%s` |" % (
                r["kindDef"], r["race"], r["slot"], r["texPath"], ",".join(r["facings"]) or "-",
                r["file"]) for r in rs]
        out.append("")
    return "\n".join(out)


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--src", default=None, help="src root (default: this repo's src/)")
    ap.add_argument("--owed", default=OWED_FILE)
    ap.add_argument("--md")
    ap.add_argument("--json")
    ap.add_argument("--check", action="store_true")
    a = ap.parse_args(argv)
    rows, stats = census(a.src)
    if stats["kinds"] < (50 if a.src is None else 1):
        print("SANITY FAIL: only %d PawnKindDefs read -- the loader is blind" % stats["kinds"])
        return 2
    md = table(rows, stats)
    if a.md:
        with open(a.md, "w") as fh:
            fh.write(md + "\n")
    if a.json:
        with open(a.json, "w") as fh:
            json.dump(rows, fh, indent=1)
    print(md if not a.md else md.split("\n## ")[0].strip())
    if a.check:
        bad = problems(rows, load_owed(a.owed))
        for b in bad:
            print("FAIL " + b)
        print("CHECK %s: %d problem(s)" % ("FAIL" if bad else "OK", len(bad)))
        return 1 if bad else 0
    return 0


if __name__ == "__main__":
    sys.exit(main())
