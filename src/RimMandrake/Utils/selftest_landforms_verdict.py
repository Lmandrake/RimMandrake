#!/usr/bin/env python3
"""LANDFORMS_PROBE_REPLACE_OR_KEEP_EXPERIMENT: the Geological Landforms verdict stands on its evidence.

Checks the committed census (design/RimMandrake/geological_landforms_judgment_2026-11-02.evidence.json, written by
gl_landforms_evidence.py): it was measured on a list that carried GL; no active mod hard-depends on GL; the world save's
mutators all resolved and none is GL's; every enabled GL landform is mapped, and every def it is mapped to exists (ours
in src/, vanilla in the dump). Then checks the repo: GL is off ModsConfig.FULL.LATEST.xml, RM_LoneMountain is a painted-only
TileFeatures landform under the Landforms switch, its worker is in the compiled source, and the map-makers design no
longer offers the impossible "keep GL and strip it per tile" option. Planted negatives show the coverage and dependency
checks can fail.
"""
import copy
import glob
import json
import os
import re
import sys
import xml.etree.ElementTree as ET

ROOT = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", ".."))
GL = "m00nl1ght.geologicallandforms"
DOC = "design/RimMandrake/geological_landforms_judgment_2026-11-02.md"
TF = "src/RimMandrake/TileFeatures"
fails = []


def read(rel):
    with open(os.path.join(ROOT, rel), encoding="utf-8") as f:
        return f.read()


def check(ok, what):
    print(("ok   " if ok else "FAIL ") + what)
    if not ok:
        fails.append(what)


def src_rm_defs():
    names = set()
    for f in glob.glob(os.path.join(ROOT, "src", "**", "*.xml"), recursive=True):
        with open(f, encoding="utf-8", errors="ignore") as fh:
            names.update(re.findall(r"<defName>(RM_\w+)</defName>", fh.read()))
    return names


def evidence_problems(ev, rm_defs):
    """Everything wrong with a census; [] when it supports the verdict."""
    p = []
    if not ev["listAsMeasured"]["carriedGL"] or ev["listAsMeasured"]["active"] < 100:
        p.append("census not measured on a real list carrying GL")
    if len(ev["glTileMutatorDefs"]) < 40 or ev["glLandformFiles"] < 40:
        p.append("GL's defs/landform files not seen (instrument blind)")
    if ev["dllsScanned"] < 100:
        p.append("too few DLLs scanned to trust 'no hard dependent'")
    hard = [d["packageId"] for d in ev["dependents"] if d["active"] and d["hard"]]
    if hard:
        p.append("active hard dependents: %s" % hard)
    sm = ev["saveMutators"]
    if sm["entries"] < 1000 or sm["unresolved"]:
        p.append("save mutators not all resolved (wrong hash table?)")
    if sm["glEntries"] != 0:
        p.append("save carries %d GL mutator entries" % sm["glEntries"])
    enabled = set(ev["glEnabled"])
    expect = {d[3:] for d in ev["glTileMutatorDefs"]} - set(ev["glDisabledUnderOdyssey"])
    if enabled != expect or len(enabled) < 20:
        p.append("enabled set is not GL defs minus the Odyssey-disabled ones")
    if set(ev["coverage"]) != enabled:
        p.append("coverage does not map exactly the enabled landforms")
    for lf, c in ev["coverage"].items():
        if c["verdict"] not in ("full", "partial", "gap"):
            p.append("%s unmapped" % lf)
        if c["verdict"] in ("full", "partial") and not c["defs"]:
            p.append("%s covered by nothing" % lf)
        for d in c["defs"]:
            if d.startswith("RM_"):
                if d not in rm_defs:
                    p.append("%s: %s is not defined in src/" % (lf, d))
            elif c["where"].get(d) in (None, "MISSING", "src"):
                p.append("%s: %s not found in the dump" % (lf, d))
    return p


ev = json.loads(read(DOC.replace(".md", ".evidence.json")))
rm_defs = src_rm_defs()
check(len(rm_defs) > 500, "src/ RM_ defs read (sanity: %d)" % len(rm_defs))
probs = evidence_problems(ev, rm_defs)
check(not probs, "census supports the verdict%s" % ("" if not probs else ": " + "; ".join(probs)))
cc = ev["coverageCounts"]
doc = read(DOC)
check(re.search(r"\*\*Verdict: GO\.\*\*", doc) is not None, "the judgment states a verdict")
check("| full | %d |" % cc.get("full", 0) in doc and "| partial | %d |" % cc.get("partial", 0) in doc
      and "| gap | %d |" % cc.get("gap", 0) in doc, "the doc's coverage table matches the evidence %s" % cc)
check("%s tile-mutator entries" % format(ev["saveMutators"]["entries"], ",") in doc, "the doc's save count matches")

# planted negatives: the same checks must see a broken census
bad = copy.deepcopy(ev)
bad["coverage"]["LoneMountain"]["defs"] = ["RM_LoneMountainNope"]
check(any("RM_LoneMountainNope" in x for x in evidence_problems(bad, rm_defs)), "planted: an undefined RM_ def is caught")
bad = copy.deepcopy(ev)
bad["dependents"].append({"packageId": "x.y", "active": True, "hard": True})
check(any("hard dependents" in x for x in evidence_problems(bad, rm_defs)), "planted: an active hard dependent is caught")
bad = copy.deepcopy(ev)
del bad["coverage"]["Canyon"]
check(any("exactly" in x for x in evidence_problems(bad, rm_defs)), "planted: an unmapped landform is caught")
bad = copy.deepcopy(ev)
bad["saveMutators"]["glEntries"] = 3
check(any("GL mutator" in x for x in evidence_problems(bad, rm_defs)), "planted: GL entries in the save are caught")

active = [e.text.lower() for e in
          ET.parse(os.path.join(ROOT, "infrastructure/state/modlists/ModsConfig.FULL.LATEST.xml")).find("activeMods")]
check(len(active) > 100, "FULL.LATEST parsed (sanity: %d mods)" % len(active))
check(GL not in active, "GL is off ModsConfig.FULL.LATEST.xml")

defs = {}
for f in glob.glob(os.path.join(ROOT, TF, "Defs", "**", "*.xml"), recursive=True):
    for d in ET.parse(f).getroot():
        if d.tag == "TileMutatorDef" and d.findtext("defName"):
            defs[d.findtext("defName")] = d
lm = defs.get("RM_LoneMountain")
check(lm is not None, "RM_LoneMountain is a TileFeatures TileMutatorDef")
if lm is not None:
    check((lm.findtext("chanceOnNonLandmarkTile") or "").strip() == "0", "RM_LoneMountain is painted only (chance 0)")
    check(lm.find("biomes") is None and lm.find("allowedBiomes") is None, "RM_LoneMountain names no biome (no worldgen)")
    check((lm.findtext("workerClass") or "").strip() == "RimMandrake.TileFeatures.RM_TileMutatorWorker_LoneMountain",
          "RM_LoneMountain uses its own worker")
check("class RM_TileMutatorWorker_LoneMountain" in read(TF + "/Source/RM_LandformWorkers.cs"), "the worker is in source")
check('"RM_LoneMountain"' in read(TF + "/Source/RM_TileFeatureApplier.cs"), "RM_LoneMountain sits under the Landforms switch")
check("LoneMountainFit" in read(TF + "/Source/RM_LandformGeometry.cs")
      and "LoneMountain();" in read(TF + "/Source/SelfTest/Program.cs"), "its geometry is in the DLL selftest")
mm = read("design/RimMandrake/biome_map_makers_design_2026-10-10.md")
check("Keep GL, and the paint pass strips GL" not in mm and "GL is active on the full list" not in mm,
      "the map-makers design carries no stale keep-GL claim")

print("%d failure(s)" % len(fails))
sys.exit(1 if fails else 0)
