#!/usr/bin/env python3
"""Offline lint of the SacredGraffiti mod (defs/patches vs C#): see lint_mod_defs.py for the checks, plus the sacred-mark data rules a ritual
reward depends on (every mark's category / god / thought / texture resolve, the outcome chances form a distribution with a positive and a
non-positive branch, the worker's filth def is one of this mod's marks). The mod has two C# mechanics (a count multiplier and a master switch)
and no engine-free logic worth a kernel; this lint is its L0 test.

    python3 src/RimMandrake/Utils/lint_sacredgraffiti_defs.py [--mod-dir <dir>] [--quiet]
"""
import glob
import os
import re
import sys
import xml.etree.ElementTree as ET

HERE = os.path.dirname(os.path.abspath(__file__))
SRC = os.path.dirname(HERE)
sys.path.insert(0, HERE)
import lint_mod_defs  # noqa: E402


def _enum(path, name):
    text = open(path, encoding="utf-8-sig").read()
    m = re.search(r"enum\s+%s\s*\{(.*?)\}" % name, text, re.S)
    return set(re.findall(r"^\s*(\w+)\s*[,=}]", re.sub(r"//[^\n]*", "", m.group(1)), re.M)) if m else set()


def mark_findings(mod_dir):
    errs = []
    defs = {}
    for p in glob.glob(os.path.join(mod_dir, "Defs", "*.xml")):
        for d in ET.parse(p).getroot():
            if d.findtext("defName"):
                defs[(d.tag, d.findtext("defName"))] = d
    marks = [d for (t, n), d in defs.items() if t == "ThingDef" and n.startswith("RM_SacredMark_")]
    if not marks:
        return ["ERROR sacredgraffiti-marks: no RM_SacredMark_* ThingDef parsed (sanity probe: Defs moved?)"]
    cats = _enum(os.path.join(SRC, "Graffiti", "Source", "GraffitiCategory.cs"), "GraffitiCategory")
    gods = _enum(os.path.join(SRC, "Ninefold", "Source", "God.cs"), "God")
    if len(cats) < 4 or len(gods) < 9:
        errs.append("ERROR sacredgraffiti-marks: enum probe read %d categories and %d gods (sanity probe failed)" % (len(cats), len(gods)))
    for m in marks:
        n = m.findtext("defName")
        if m.get("ParentName") != "RM_BaseGraffiti":
            errs.append("ERROR sacredgraffiti-marks: %s does not inherit RM_BaseGraffiti" % n)
        ext = m.find("modExtensions/li[@Class='RimMandrake.Graffiti.ModExtension_Graffiti']")
        if ext is None:
            errs.append("ERROR sacredgraffiti-marks: %s has no graffiti extension (the engine never counts it)" % n)
            continue
        cat = ext.findtext("category")
        if cat != "Devotional" or cat not in cats:
            errs.append("ERROR sacredgraffiti-marks: %s category %r (a stale enum name silently parses to None; sacred marks are Devotional)" % (n, cat))
        god = ext.findtext("godSatiationHook")
        if god not in gods:
            errs.append("ERROR sacredgraffiti-marks: %s godSatiationHook %r is no Ninefold God" % (n, god))
        elif not n.endswith("_" + god):
            errs.append("ERROR sacredgraffiti-marks: %s is named for one god but hooks %s" % (n, god))
        th = ext.findtext("viewerReactionThought")
        if th and ("ThoughtDef", th) not in defs:
            errs.append("ERROR sacredgraffiti-marks: %s viewerReactionThought %s is not a ThoughtDef of this mod" % (n, th))
        if ext.findtext("supportsQuality") != "false" or ext.findtext("hasSubject") != "false":
            errs.append("ERROR sacredgraffiti-marks: %s must be fixed-quality with no subject (the marks ARE the livery)" % n)
        if m.findtext("statBases/Flammability") != "0":
            errs.append("ERROR sacredgraffiti-marks: %s is flammable" % n)
        tex = m.findtext("graphicData/texPath")
        if not tex or not (glob.glob(os.path.join(mod_dir, "Textures", *tex.split("/")) + ".png")):
            errs.append("ERROR sacredgraffiti-marks: %s texPath %r has no png" % (n, tex))
        try:
            if float(m.findtext("statBases/Beauty")) <= 0 and cat == "Devotional":
                errs.append("ERROR sacredgraffiti-marks: %s is a devotional mark with non-positive Beauty" % n)
        except (TypeError, ValueError):
            errs.append("ERROR sacredgraffiti-marks: %s has no numeric Beauty" % n)
    if not any(re.search(r'Name="RM_BaseGraffiti"', open(f, encoding="utf-8-sig").read()) for f in glob.glob(os.path.join(SRC, "Graffiti", "Defs", "**", "*.xml"), recursive=True)):
        errs.append("ERROR sacredgraffiti-marks: the parent RM_BaseGraffiti is defined by no Graffiti def (the marks would not load)")
    names = {m.findtext("defName") for m in marks}
    outcomes = [d for (t, n), d in defs.items() if t == "RitualOutcomeEffectDef"]
    if not outcomes:
        errs.append("ERROR sacredgraffiti-marks: no RitualOutcomeEffectDef parsed (sanity probe)")
    for o in outcomes:
        n = o.findtext("defName")
        if o.findtext("filthDefToSpawn") not in names:
            errs.append("ERROR sacredgraffiti-marks: %s spawns %r, which is none of this mod's marks" % (n, o.findtext("filthDefToSpawn")))
        rng = o.findtext("filthCountToSpawn") or ""
        if not re.fullmatch(r"\d+~\d+", rng) or int(rng.split("~")[0]) < 1 or int(rng.split("~")[0]) > int(rng.split("~")[1]):
            errs.append("ERROR sacredgraffiti-marks: %s filthCountToSpawn %r is not a positive ascending range" % (n, rng))
        chances = [(float(li.findtext("chance")), int(li.findtext("positivityIndex"))) for li in o.findall("outcomeChances/li")]
        if abs(sum(c for c, _ in chances) - 1.0) > 1e-6:
            errs.append("ERROR sacredgraffiti-marks: %s outcome chances sum to %.3f, not 1" % (n, sum(c for c, _ in chances)))
        if not any(i > 0 for _, i in chances) or not any(i <= 0 for _, i in chances):
            errs.append("ERROR sacredgraffiti-marks: %s needs both a positive outcome (leaves a mark) and a non-positive one (a curse leaves none)" % n)
        if "RitualOutcomeEffectWorker_PlaceSacredMark" not in (o.findtext("workerClass") or ""):
            errs.append("ERROR sacredgraffiti-marks: %s does not use the PlaceSacredMark worker" % n)
    return errs


if __name__ == "__main__":
    argv = sys.argv[1:]
    mod_dir = argv[argv.index("--mod-dir") + 1] if "--mod-dir" in argv else os.path.join(SRC, "SacredGraffiti")
    rc = lint_mod_defs.run("SacredGraffiti", argv)
    errs = mark_findings(mod_dir)
    for e in errs:
        print(e)
    sys.exit(1 if (rc == 1 or errs) else rc)
