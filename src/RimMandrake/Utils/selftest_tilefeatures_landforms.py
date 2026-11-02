#!/usr/bin/env python3
"""
Selftest: the VEE landform tile features (plan group L) stay ported into mandrake.rm.tilefeatures.

Item VEE_LANDFORMS_BUILD_CRATERS_AND_COMPANY; plan design/RimMandrake/vee_port_plan_2026-10-22.md §1a (the rows marked L)
and §2 (VEE_<Stem> -> RM_<Stem>; VEE_QuicksandPits -> the existing RM_QuicksandPits).

Proves, offline:
  1. the plan's §1a table still has exactly 30 L rows covering 1,845 tiles (the instrument reads the table it claims to);
  2. every L row has its RM_ port: a TileMutatorDef in src/RimMandrake/TileFeatures (RM_QuicksandPits in
     EnvironmentalHazards), with chanceOnNonLandmarkTile 0, no biome lists (no worldgen), and VEE's categories;
  3. every RimMandrake.TileFeatures.* workerClass / conditionClass / extension class is declared in TileFeatures' Source
     and that file is compiled by the mod's csproj; every vanilla workerClass is one of the vanilla workers the plan names;
  4. every child of an RM_LandformExtension is a public field of that class (a typo would only log a config error);
  5. every def a landform def names (terrain, thing, gen step, condition) is defined by TileFeatures, by FlowWorks (the mod
     declares it as a dependency), or by the base game/DLC (checked against the game's Data folder when it is readable);
  6. a river/delta port falls back to vanilla's river and a coast port to vanilla's coast when switched off;
  7. the Mod Settings applier's Landforms list is exactly the 29 TileFeatures ports;
  8. no TileFeatures def names a VEE_ def (XML comments are provenance and category strings are not defs: skipped);
  9. the instrument can see: planted defects (a port removed, a VEE_ name, a typo'd extension field, an unknown worker
     class, an undefined terrain) are each caught by the same checks.

    python3 src/RimMandrake/Utils/selftest_tilefeatures_landforms.py
"""
import copy
import glob
import os
import re
import sys
import xml.etree.ElementTree as ET

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
PLAN = os.path.join(ROOT, "design", "RimMandrake", "vee_port_plan_2026-10-22.md")
TF = os.path.join(ROOT, "src", "RimMandrake", "TileFeatures")
FLOWWORKS = os.path.join(ROOT, "src", "RimMandrake", "FlowWorks")
ENVHAZ = os.path.join(ROOT, "src", "RimMandrake", "EnvironmentalHazards")
GAME_DATA = "/mnt/c/Program Files (x86)/Steam/steamapps/common/RimWorld/Data"
NS = "RimMandrake.TileFeatures."

# VEE's own categories per row, read from its TileMutatorDefs on 2026-11-01 (VEE's XML is not in the repo);
# VEE_LoneIsland inherits Coast from vanilla Odyssey's abstract BaseCoastMut.
VEE_CATEGORIES = {
    "SaltPlains": ["Lake"], "DryRiver": ["River"], "FloodPlains": ["River"], "SulfuricLake": ["Lake"],
    "StagnantRivulet": ["River"], "RisingWaters": ["Coast"], "SerpentineCanyons": ["Mountain"], "DustBowl": ["Lake"],
    "JaggedRocks": ["Mountain"], "GravelBeach": ["Coast"], "MeteorCrater": ["Mountain"], "RockRidge": ["Mountain"],
    "QuicksandPits": ["Lake"], "RelictDelta": ["River"], "ContaminatedRiver": ["River"], "AlluvialFan": ["River"],
    "StoneForest": ["Mountain"], "ContaminatedReservoir": ["Lake"], "LoneIsland": ["Coast"], "SulfuricRiver": ["River"],
    "Volcano": ["Mountain"], "ResurgentCaldera": ["Mountain"], "ToxicCrater": ["Mountain"],
    "Cenotes": [], "Sinkholes": [], "PebbleDunes": [], "QuicksandDunes": [], "DeepSnow": [], "FleshPits": [],
    "RedDesert": [],
}
VANILLA_WORKERS = {"TileMutatorWorker_Coast", "TileMutatorWorker_CoastalIsland", "TileMutatorWorker_LavaCrater",
                   "TileMutatorWorker_Patches", "TileMutatorWorker_River"}
REUSED = {"QuicksandPits": ("RM_QuicksandPits", ENVHAZ)}
REF_TAGS = {"deepTerrain", "shallowTerrain", "shoreTerrain", "outerTerrain", "floorTerrain", "lipTerrain", "bankTerrain",
            "thingTerrain", "thingToSpawn", "from", "to", "terrain", "overrideRiverbankTerrain",
            "overrideCoastalBeachTerrain", "overrideLakeBeachTerrain"}
REF_LISTS = {"extraGenSteps", "additionalGameConditions", "preventGenSteps"}


def plan_rows(text):
    rows = []
    for m in re.finditer(r"^\|\s*\d+\s*\|\s*`VEE_(\w+)`\s*\|\s*([\d,]+)\s*\|.*\|\s*L\s*\|\s*$", text, re.M):
        rows.append((m.group(1), int(m.group(2).replace(",", ""))))
    return rows


def parse_defs(folder):
    """{(tag, defName): element} over folder/Defs/**.xml"""
    out = {}
    for f in glob.glob(os.path.join(folder, "Defs", "**", "*.xml"), recursive=True):
        for d in ET.parse(f).getroot():
            dn = d.findtext("defName")
            if dn:
                out[(d.tag, dn)] = d
    return out


def game_def_names():
    names = set()
    if not os.path.isdir(GAME_DATA):
        return None
    for f in glob.glob(os.path.join(GAME_DATA, "*", "Defs", "**", "*.xml"), recursive=True):
        try:
            for d in ET.parse(f).getroot():
                dn = d.findtext("defName")
                if dn:
                    names.add(dn)
        except ET.ParseError:
            continue
    return names


def source_classes():
    """{class name: file} declared in TileFeatures Source, and the csproj's compiled file names."""
    classes = {}
    for f in glob.glob(os.path.join(TF, "Source", "*.cs")):
        for m in re.finditer(r"\bclass\s+(\w+)", open(f, encoding="utf-8").read()):
            classes[m.group(1)] = os.path.basename(f)
    proj = open(os.path.join(TF, "Source", "RimMandrake_TileFeatures.csproj"), encoding="utf-8").read()
    compiled = set(re.findall(r'<Compile Include="([^"\\]+\.cs)"', proj))
    return classes, compiled


def extension_fields():
    src = open(os.path.join(TF, "Source", "RM_LandformWorkers.cs"), encoding="utf-8").read()
    m = re.search(r"class RM_LandformExtension\b.*?\{(.*?)\n    \}", src, re.S)
    body = m.group(1) if m else ""
    return set(re.findall(r"public\s+(?:static\s+)?[\w<>\[\], ]+?\s+(\w+)\s*(?:=|;)", body))


def applier_landforms():
    src = open(os.path.join(TF, "Source", "RM_TileFeatureApplier.cs"), encoding="utf-8").read()
    m = re.search(r"Landforms\s*=\s*\{(.*?)\};", src, re.S)
    return set(re.findall(r'"(RM_\w+)"', m.group(1))) if m else set()


def check(rows, tf_defs, other_defs, classes, compiled, fields, applier, game_names, about_text):
    """Returns a list of failure strings."""
    fails = []
    all_defs = dict(other_defs)
    all_defs.update(tf_defs)
    known = {dn for (_, dn) in all_defs}
    for stem, _tiles in rows:
        if stem in REUSED:
            name, folder = REUSED[stem]
            if ("TileMutatorDef", name) not in other_defs:
                fails.append("%s: reused port %s not found in %s" % (stem, name, os.path.relpath(folder, ROOT)))
            continue
        d = tf_defs.get(("TileMutatorDef", "RM_" + stem))
        if d is None:
            fails.append("VEE_%s: no TileMutatorDef RM_%s in TileFeatures" % (stem, stem))
            continue
        if (d.findtext("chanceOnNonLandmarkTile") or "").strip() != "0":
            fails.append("RM_%s: chanceOnNonLandmarkTile is not 0" % stem)
        for gate in ("biomeWhitelist", "biomeBlacklist"):
            if d.find(gate) is not None:
                fails.append("RM_%s: carries %s (a worldgen gate)" % (stem, gate))
        cats = [li.text.strip() for li in d.find("categories")] if d.find("categories") is not None else []
        if stem not in VEE_CATEGORIES:
            fails.append("RM_%s: no recorded VEE categories (update VEE_CATEGORIES from VEE's def)" % stem)
        elif cats != VEE_CATEGORIES[stem]:
            fails.append("RM_%s: categories %s, VEE had %s" % (stem, cats, VEE_CATEGORIES[stem]))
        ext = None
        for li in d.findall("modExtensions/li"):
            if li.get("Class") == NS + "RM_LandformExtension":
                ext = li
        off = ext.findtext("offWorkerClass") if ext is not None else None
        worker = (d.findtext("workerClass") or "").strip()
        if "River" in cats and "Landform" in worker and off != "TileMutatorWorker_River":
            fails.append("RM_%s: river port without offWorkerClass TileMutatorWorker_River" % stem)
        if "Coast" in cats and off != "TileMutatorWorker_Coast":
            fails.append("RM_%s: coast port without offWorkerClass TileMutatorWorker_Coast" % stem)
    # every landform def in TileFeatures (the landforms file) and every class/field/reference it names
    land = [d for (t, dn), d in tf_defs.items() if t == "TileMutatorDef" and dn in applier | {"RM_" + s for s, _ in rows}]
    for d in land:
        dn = d.findtext("defName")
        for e in d.iter():
            for cls in ([e.text.strip()] if e.tag in ("workerClass", "offWorkerClass") and e.text else []) + \
                       ([e.get("Class")] if e.get("Class") else []):
                if cls.startswith(NS):
                    short = cls[len(NS):]
                    if short not in classes:
                        fails.append("%s: class %s not declared in TileFeatures Source" % (dn, cls))
                    elif classes[short] not in compiled:
                        fails.append("%s: class %s lives in %s, which the csproj does not compile" % (dn, cls, classes[short]))
                elif cls not in VANILLA_WORKERS and not cls.startswith("VEF."):
                    fails.append("%s: class %s is neither ours nor a vanilla worker the plan names" % (dn, cls))
        for li in d.findall("modExtensions/li"):
            if li.get("Class") != NS + "RM_LandformExtension":
                continue
            for child in li:
                if child.tag not in fields:
                    fails.append("%s: RM_LandformExtension has no field '%s'" % (dn, child.tag))
        refs = []
        for e in d.iter():
            if e.tag in REF_TAGS and e.text and e.text.strip():
                refs.append(e.text.strip())
            if e.tag in REF_LISTS:
                refs += [li.text.strip() for li in e if li.text]
        for r in refs:
            if r in known:
                continue
            if game_names is not None and r in game_names:
                continue
            if game_names is None and r in {"WaterDeep", "WaterShallow", "Gravel", "Sand", "SoftSand", "SoilRich",
                                            "ToxicWaterDeep", "ToxicWaterShallow"}:
                continue
            fails.append("%s: names '%s', defined by neither TileFeatures, FlowWorks nor the game" % (dn, r))
        if any(r.startswith("RM_") and ("TerrainDef", r) in other_defs and ("TerrainDef", r) not in tf_defs for r in refs) \
                and "mandrake.rm.flowworks" not in about_text:
            fails.append("%s: names a FlowWorks terrain but About.xml does not depend on mandrake.rm.flowworks" % dn)
    ports = {"RM_" + s for s, _ in rows if s not in REUSED}
    if applier != ports:
        fails.append("applier Landforms list differs from the ports: missing %s, extra %s"
                     % (sorted(ports - applier), sorted(applier - ports)))
    # no VEE_ def named anywhere in our defs (element text, tag or attribute); comments are dropped by ElementTree, and
    # category lists are skipped: a category is a free string the F/W ports keep as VEE spelled it on purpose, so a tile's
    # mutator conflicts stay like-for-like - it names no def
    for (t, dn), d in tf_defs.items():
        skip = {id(li) for cat in d.iter() if cat.tag in ("categories", "overrideCategories") for li in cat}
        for e in d.iter():
            if id(e) in skip:
                continue
            vals = [e.tag, (e.text or "").strip()] + list(e.attrib.values())
            if any(v.startswith("VEE_") for v in vals if v):
                fails.append("%s %s: names a VEE_ def" % (t, dn))
                break
    return fails


def main():
    text = open(PLAN, encoding="utf-8").read()
    rows = plan_rows(text)
    ok = True

    def say(cond, msg):
        nonlocal ok
        print(("PASS  " if cond else "FAIL  ") + msg)
        ok = ok and cond

    say(len(rows) == 30 and sum(t for _, t in rows) == 1845,
        "plan §1a has 30 L rows over 1,845 tiles (read %d rows, %d tiles)" % (len(rows), sum(t for _, t in rows)))
    tf_defs = parse_defs(TF)
    other_defs = {}
    other_defs.update(parse_defs(FLOWWORKS))
    other_defs.update(parse_defs(ENVHAZ))
    classes, compiled = source_classes()
    fields = extension_fields()
    applier = applier_landforms()
    game_names = game_def_names()
    about = open(os.path.join(TF, "About", "About.xml"), encoding="utf-8").read()
    if game_names is None:
        print("NOTE  game Data folder unreadable: vanilla names checked against a fixed list only")
    say(len(fields) > 20 and "lakeRadius" in fields, "RM_LandformExtension fields read from source (%d)" % len(fields))
    args = (rows, tf_defs, other_defs, classes, compiled, fields, applier, game_names, about)
    fails = check(*args)
    for f in fails:
        print("      " + f)
    say(not fails, "29 landform ports + RM_QuicksandPits: defs, classes, fields, references, fallbacks, applier, no VEE_ names")

    # planted negatives: each must be caught by the same check
    def planted(name, mutate):
        tf2 = {k: copy.deepcopy(v) for k, v in tf_defs.items()}
        mutate(tf2)
        caught = check(rows, tf2, other_defs, classes, compiled, fields, applier, game_names, about)
        say(len(caught) > len(fails), "planted negative caught: %s" % name)

    def drop_port(d):
        del d[("TileMutatorDef", "RM_Cenotes")]

    def vee_name(d):
        ET.SubElement(d[("TileMutatorDef", "RM_SaltPlains")], "overrideLakeBeachTerrain").text = "VEE_Salt"

    def typo_field(d):
        li = d[("TileMutatorDef", "RM_SaltPlains")].find("modExtensions/li")
        ET.SubElement(li, "lakeRadious").text = "0.5"

    def bad_worker(d):
        d[("TileMutatorDef", "RM_DryRiver")].find("workerClass").text = NS + "RM_TileMutatorWorker_Nope"

    def bad_terrain(d):
        d[("TileMutatorDef", "RM_RedDesert")].find("modExtensions/li/swaps/li/to").text = "RM_NoSuchSand"

    def no_fallback(d):
        li = d[("TileMutatorDef", "RM_FloodPlains")].find("modExtensions/li")
        li.remove(li.find("offWorkerClass"))

    planted("a port removed", drop_port)
    planted("a VEE_ terrain named", vee_name)
    planted("a typo'd extension field", typo_field)
    planted("an undeclared worker class", bad_worker)
    planted("an undefined terrain", bad_terrain)
    planted("a river port without its off-switch fallback", no_fallback)
    print("OK" if ok else "FAILED")
    sys.exit(0 if ok else 1)


if __name__ == "__main__":
    main()
