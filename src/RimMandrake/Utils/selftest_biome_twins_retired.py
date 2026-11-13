#!/usr/bin/env python3
"""BIOME_TWINS_RETIRE_TWENTY_FIVE_FROZEN: the 25 frozen RUT_ twin BiomeDefs stay deleted.

Owner card 2026-11-06 (HQ_728B0108CA): delete the 25 twins; CANONICAL_ASHKARR_START_2026-09-12.rws stays on disk as a
record only and is no longer expected to load. Before deleting, measure the live start: if it carries twin tiles, stop.

Checks: no BiomeDef and no def file for a twin; RUT_Umbra and RUT_Jawa_BackgroundWater kept; no twin name in any src/
XML (comments too) or C# code; a tool naming one is on the list below with its reason; the committed pre-delete scan
shows 0 twin tiles on the live start; removing the twins moves no other biome's ShortHash (a moved hash would
re-paint tiles on a save). Probes first: each scanner must see a planted name.
"""
import json
import math
import os
import re
import sys
import xml.etree.ElementTree as ET

REPO = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", ".."))
SRC = os.path.join(REPO, "src")
SCAN = os.path.join(REPO, "design", "Jawa", "worldbuilding", "twin_save_scan_2026-11-06.json")
TWINS = tuple("RUT_" + n for n in (
    "Greentide BlueDesert TheScald TheRot FeverWood Cauldron PropaneLake Scarlands ExtremeDesert GreySea SleepingIce "
    "CrackedLands Miasma Sump TwilightSea WeepingStones Slime Abyss Webwork TheForge Wastes Contagion Desert "
    "RustCathedral AridShrubland").split())
KEPT = ("RUT_Umbra", "RUT_Jawa_BackgroundWater")
NAME = re.compile(r"\b(?:" + "|".join(TWINS) + r")\b")
# path under src/ -> why this tool still spells a twin. Each reads the world RECORD, an old save or a texture file name
# (world/*.csv and the 09-12 save keep these names for good); none resolves one as a live def.
TOOLS = {
    "RimMandrake/Utils/art/biome_worldfaces.py": "twin names as texture file stems and the RECORD map of the world CSV",
    "RimMandrake/Utils/art/loadscreen_candidates.py": "selects tiles from the world CSV record",
    "RimMandrake/Utils/art/selftest_sea_faces_picked.py": "sea table keeps the RUT_ texture stems",
    "RimMandrake/Utils/art/selftest_sea_faces_picked_mutants.py": "mirrors the sea table above",
    "RimMandrake/Utils/art/world_face_variants.py": "a texture file stem",
    "RimMandrake/Utils/ashkarr_horrorwastes_dissolve.py": "one-off paint of the record CSV, kept as lineage",
    "RimMandrake/Utils/ashkarr_shore_and_ice.py": "one-off paint of the record CSV, kept as lineage",
    "RimMandrake/Utils/ashkarr_three_seas.py": "one-off paint of the record CSV, kept as lineage",
    "RimMandrake/Utils/build_landmark_density_sheet.py": "selects tiles from the world CSV record",
    "RimMandrake/Utils/desert_wasteland_enrichment_plan.py": "reads the world CSV record by its names",
    "RimMandrake/Utils/fauna_normalization.py": "reads the world CSV record by its names",
    "RimMandrake/Utils/perf/mappretick_window.py": "pinned to the old BENCH_leaf_scenes save scene",
    "RimMandrake/Utils/perf/selftest_mappretick_window.py": "fixture of that pin",
    "RimMandrake/Utils/planet_portrait.py": "colour for a record CSV name",
    "RimMandrake/Utils/remake/repaint_biomes.py": "proves the R3 hash decode, where RUT_Cauldron shares a base hash",
    "RimMandrake/Utils/selftest_desert_wasteland_enrichment_plan.py": "fixture of the plan above",
    "RimMandrake/Utils/selftest_world_layers_export.py": "fixture of the record export below",
    "RimMandrake/Utils/sim/selftest_csuite_tps.py": "fixture pinned to an old recorded scene",
    "RimMandrake/Utils/world_layers_export.py": "rename map of the record CSV",
    "RimMandrake/bridgetools/repair_lost_biomes_2026-10-18.py": "dated one-off on the 10-18 saves",
    "RimMandrake/Utils/mineral_matrix/gen_matrix.py": "reads round-two rows and drops the three twin rows by name",
    "RimMandrake/Utils/mineral_matrix/prereview_harness.py": "asserts the sheet shows no twin row",
    "RimMandrake/Utils/mineral_matrix/selftest_mineral_matrix.py": "plants a twin row as a mutant that must go red",
}
fails = []


def check(ok, what):
    print(("ok   " if ok else "FAIL ") + what)
    if not ok:
        fails.append(what)


def cs_code(text):
    text = re.sub(r"/\*.*?\*/", "", text, flags=re.S)
    return re.sub(r"//[^\n]*", "", text)


def short_hash(name):
    h = 23
    for ch in name:
        h = (h * 31 + ord(ch)) & 0xFFFFFFFF
    if h >= 0x80000000:
        h -= 0x100000000
    return int(math.fmod(h, 65535)) & 0xFFFF


def give(names):
    """ShortHashGiver over sorted names: a taken hash bumps by one."""
    taken, out = set(), {}
    for n in sorted(names):
        h = short_hash(n)
        while h == 0 or h in taken:
            h = (h + 1) & 0xFFFF
        taken.add(h)
        out[n] = h
    return out


def walk(exts):
    for dp, dns, fns in os.walk(SRC):
        dns[:] = [d for d in dns if d not in ("bin", "obj", "__pycache__", "time_ledger_replay", "fixtures")]
        for fn in fns:
            if fn.endswith(exts):
                yield os.path.join(dp, fn)


def main():
    # probes: the instruments can see
    check(bool(NAME.search("<li>RUT_Sump</li>")), "probe: the name scan sees a planted <li>")
    check(not NAME.search("RUT_SumpDuskLock RUT_Umbra"), "probe: a longer name and a kept biome are not hits")
    check(bool(NAME.search(cs_code('var x = "RUT_Sump"; // note'))), "probe: the C# strip keeps a string")
    check(not NAME.search(cs_code('var x = 1; // RUT_Sump')), "probe: the C# strip drops a comment")
    check(give(["RM_RustCathedral", "RUT_Cauldron"]) == {"RM_RustCathedral": 3765, "RUT_Cauldron": 3766},
          "probe: the hash sim bumps the later name as the game's dump does")

    biomes, xml_hits, xmls = set(), [], 0
    for p in walk((".xml",)):
        xmls += 1
        text = open(p, encoding="utf-8", errors="replace").read()
        if NAME.search(text):
            xml_hits.append(os.path.relpath(p, SRC))
        if "BiomeDef" in text:
            try:
                biomes |= {(b.findtext("defName") or "").strip() for b in ET.fromstring(text.encode("utf-8")).iter("BiomeDef")}
            except ET.ParseError as ex:
                check(False, "%s parses: %s" % (p, ex))
    check(xmls > 1000 and len(biomes) > 30, "instrument sees the tree (%d xml, %d BiomeDefs)" % (xmls, len(biomes)))
    check(not (set(TWINS) & biomes), "no twin BiomeDef in src/: %s" % sorted(set(TWINS) & biomes))
    check(all(k in biomes for k in KEPT), "RUT_Umbra and RUT_Jawa_BackgroundWater stay")
    check(all(not os.path.exists(os.path.join(SRC, "RimUtinni", "UtinniPatches", "Defs", "BiomeDefs", t + ".xml")) for t in TWINS),
          "the 25 def files are gone")
    check(not xml_hits, "no twin name in src/ XML: %s" % xml_hits[:8])
    cs_hits = [os.path.relpath(p, SRC) for p in walk((".cs",)) if NAME.search(cs_code(open(p, encoding="utf-8", errors="replace").read()))]
    check(not cs_hits, "no twin name in C# code: %s" % cs_hits[:8])
    py = {os.path.relpath(p, SRC).replace(os.sep, "/") for p in walk((".py",)) if NAME.search(open(p, encoding="utf-8", errors="replace").read())}
    py.discard("RimMandrake/Utils/selftest_biome_twins_retired.py")
    check(not (py - set(TOOLS)), "a tool naming a twin is listed with its reason: %s" % sorted(py - set(TOOLS)))
    check(not (set(TOOLS) - py), "the list holds no tool that stopped naming one: %s" % sorted(set(TOOLS) - py))

    scan = json.load(open(SCAN, encoding="utf-8"))
    live = scan["live_start"]
    check(scan["saves_scanned"] >= 200 and scan["frozen_record"] > 10000, "the scan saw the saves and the 09-12 record's twins (%d)" % scan["frozen_record"])
    check(live["twin_tiles"] == 0, "the live start %s carries 0 twin tiles" % live["save"])
    check(not any(k.startswith("?") for k in live["other_hashes_by_name"]), "every other hash on the live start has a name: %s" % live["other_hashes_by_name"])
    names = set(scan["biome_names_for_hash_sim"]) | biomes
    check(len(set(TWINS) & names) == 25, "the sim runs over a list that held the twins")
    before, after = give(names), give(names - set(TWINS))
    moved = {n: (before[n], after[n]) for n in after if before[n] != after[n]}
    check(not moved, "removing the twins moves no other biome's ShortHash: %s" % moved)

    print("FAIL %d" % len(fails) if fails else "PASS")
    return 1 if fails else 0


if __name__ == "__main__":
    sys.exit(main())
