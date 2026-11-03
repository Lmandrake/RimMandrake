#!/usr/bin/env python3
"""LANDFORMS_PROBE_REPLACE_OR_KEEP_EXPERIMENT: measure what Geological Landforms (m00nl1ght.geologicallandforms) does for
us, and write design/RimMandrake/geological_landforms_judgment_2026-11-02.evidence.json.

Offline only. Reads:
  - GL's install (workshop 2773943594): its TileMutatorDefs and Landforms-v1 files;
  - GL's settings file in the game's Config folder: the landforms it switches off under Odyssey;
  - every About.xml and every DLL of the mods on ModsConfig.FULL.LATEST.xml (as of --list-as-of, the list that still
    carried GL): who depends on GL, hard or soft;
  - the world save's SurfaceLayer mutator arrays, decoded against the def dump's TileMutatorDef shortHashes (a hash
    resolved against a different mod set gives a plausible lie, so `unresolved` must be empty);
  - COVERAGE below: for each GL landform still enabled, the existing def(s) that make the same shape, verified to exist
    in the dump or in src/.

    python3 src/RimMandrake/Utils/gl_landforms_evidence.py --dump <TileMutatorDef.json> [--save <rws>] [--out <json>]
"""
import argparse
import base64
import collections
import glob
import json
import os
import re
import struct
import sys
import xml.etree.ElementTree as ET
import zlib

ROOT = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", ".."))
GL = "m00nl1ght.geologicallandforms"
WORKSHOP = "/mnt/c/Program Files (x86)/Steam/steamapps/workshop/content/294100"
GAME_MODS = "/mnt/c/Program Files (x86)/Steam/steamapps/common/RimWorld/Mods"
GL_DIR = os.path.join(WORKSHOP, "2773943594")
import sys as _sys; _sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from game_paths import LOCALLOW  # noqa: E402
CONFIG = (LOCALLOW + "/Config/Mod_2773943594_GeologicalLandformsMod.xml")
SAVE = os.path.join(ROOT, "world", "ASHKARR_DEV_START_2026-10-20_PARITY_QUIET_R3.rws")
OUT = os.path.join(ROOT, "design", "RimMandrake", "geological_landforms_judgment_2026-11-02.evidence.json")
LIST = os.path.join(ROOT, "infrastructure", "state", "modlists", "ModsConfig.FULL.LATEST.xml")

# GL landform -> (verdict, [existing defs that make the same shape]). full = same shape; partial = the family exists, a
# detail does not (an island in the cove, ice); gap = nothing of ours or vanilla's makes it. Judged from each def's
# worker and description (Odyssey, Core) or its geometry (ours, src/RimMandrake/TileFeatures).
COVERAGE = {
    "Atoll": ("full", ["CoastalAtoll"]),
    "Caldera": ("full", ["RM_ResurgentCaldera", "RM_Volcano"]),
    "Canyon": ("full", ["RM_SerpentineCanyons", "Chasm"]),
    "CaveEntrance": ("full", ["Cavern", "Caves"]),
    "SurfaceCave": ("full", ["Cavern", "UndergroundCave"]),
    "CoastCorner": ("full", ["Coast"]),
    "Crater": ("full", ["RM_MeteorCrater", "RM_ToxicCrater", "LavaCrater"]),
    "DesertPlateau": ("full", ["Plateau"]),
    "Gorge": ("full", ["Chasm", "RM_SerpentineCanyons"]),
    "Rift": ("full", ["Crevasse", "Chasm"]),
    "Island": ("full", ["RM_LoneIsland", "CoastalIsland"]),
    "LoneMountain": ("full", ["RM_LoneMountain"]),
    "River": ("full", ["River"]),
    "RiverConfluence": ("full", ["RiverConfluence"]),
    "RiverDelta": ("full", ["RiverDelta", "RM_RelictDelta"]),
    "RiverIsland": ("full", ["RiverIsland"]),
    "RiverSource": ("full", ["Headwater"]),
    "RiverTerrain": ("full", ["River"]),
    "SecludedValley": ("full", ["Hollow", "Valley"]),
    "Sinkhole": ("full", ["RM_Sinkholes", "RM_Cenotes"]),
    "CoveWithIsland": ("partial", ["Cove", "Bay"]),
    "SecludedCove": ("partial", ["Cove", "Bay"]),
    "Badlands": ("partial", ["RM_JaggedRocks", "RM_StoneForest"]),
    "Cirque": ("partial", ["Basin"]),
    "IceOasis": ("partial", ["Oasis"]),
    "Glacier": ("gap", []),
    "Landbridge": ("gap", []),
    "Tombolo": ("gap", []),
    "Skerry": ("gap", []),
    "SwampHill": ("gap", []),
}


def about_rows(active):
    rows = []
    for root in (WORKSHOP, GAME_MODS):
        for ab in glob.glob(root + "/*/About/About.xml"):
            try:
                t = ET.parse(ab).getroot()
            except ET.ParseError:
                continue
            pid = (t.findtext("packageId") or "").lower()
            if pid == GL:
                continue
            text = open(ab, encoding="utf-8", errors="ignore").read().lower()
            if GL not in text:
                continue
            hard = any((d.findtext("packageId") or "").lower() == GL for d in t.iter("li") if d.find("packageId") is not None)
            rows.append({"packageId": pid, "active": pid in active, "hard": hard})
    return sorted(rows, key=lambda r: r["packageId"])


def dll_refs(active):
    hits, n = collections.defaultdict(list), 0
    for root in (WORKSHOP, GAME_MODS):
        for ab in glob.glob(root + "/*/About/About.xml"):
            try:
                pid = (ET.parse(ab).getroot().findtext("packageId") or "").lower()
            except ET.ParseError:
                continue
            if pid not in active or pid == GL:
                continue
            d = os.path.dirname(os.path.dirname(ab))
            for f in glob.glob(d + "/1.6/**/*.dll", recursive=True):
                n += 1
                b = open(f, "rb").read()
                if b"GeologicalLandforms" in b or "GeologicalLandforms".encode("utf-16le") in b:
                    hits[pid].append(os.path.relpath(f, d))
    return dict(hits), n


def save_mutators(save, rows):
    byh = {r["shortHash"]: r for r in rows}
    s = open(save, encoding="utf-8", errors="ignore").read()
    surf = s[s.find('<li Class="SurfaceLayer"'):]

    def blob(tag):
        a = surf.find("<%s>" % tag)
        b = surf.find("</%s>" % tag, a)
        return zlib.decompress(base64.b64decode(re.sub(r"\s", "", surf[a + len(tag) + 2:b])), -15)

    mb, tb = blob("tileMutatorDefsDeflate"), blob("tileMutatorTilesDeflate")
    h = struct.unpack("<%dH" % (len(mb) // 2), mb)
    t = struct.unpack("<%dI" % (len(tb) // 4), tb)
    by_mod, unres = collections.Counter(), collections.Counter()
    for x in h:
        r = byh.get(x)
        if r is None:
            unres[str(x)] += 1
        else:
            by_mod[r["packageId"].lower()] += 1
    i = s.find('<li Class="GeologicalLandforms.LandformData">')
    seg = s[i:s.find("</tileData>", i)] if i >= 0 else ""
    keys = seg[:seg.find("</keys>")].count("<li>") if seg else 0
    return {"save": os.path.relpath(save, ROOT), "entries": len(h), "tiles": len(set(t)), "unresolved": dict(unres),
            "byMod": dict(by_mod.most_common()), "glEntries": by_mod.get(GL, 0),
            "landformDataComponent": i >= 0, "landformDataTiles": keys,
            "landformDataNonNullLandforms": seg.count("<landforms>")}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--dump", required=True, help="a def dump's defs/TileMutatorDef.json of the list that carried GL")
    ap.add_argument("--save", default=SAVE)
    ap.add_argument("--list", default=LIST, help="the mod list that still carried GL (its active set is read)")
    ap.add_argument("--out", default=OUT)
    a = ap.parse_args()
    rows = json.load(open(a.dump))["defs"]
    names = {r["defName"]: r["packageId"].lower() for r in rows}
    gl_defs = sorted(r["defName"] for r in rows if r["packageId"].lower() == GL)
    active = {li.text.lower() for li in ET.parse(a.list).getroot().find("activeMods")}
    cfg = ET.parse(CONFIG).getroot()
    off = sorted(li.text for li in cfg.iter("Odyssey_DisabledLandforms") for li in li)
    off_vanilla = sorted(li.text for li in cfg.iter("Odyssey_DisabledTileMutators") for li in li)
    enabled = sorted(d[3:] for d in gl_defs if d[3:] not in off)
    src_defs = set()
    for f in glob.glob(os.path.join(ROOT, "src", "**", "*.xml"), recursive=True):
        src_defs.update(re.findall(r"<defName>(RM_\w+)</defName>", open(f, encoding="utf-8", errors="ignore").read()))
    cov = {}
    for lf in enabled:
        verdict, defs = COVERAGE.get(lf, ("UNMAPPED", []))
        cov[lf] = {"verdict": verdict, "defs": defs,
                   "where": {d: ("src" if d in src_defs else names.get(d, "MISSING")) for d in defs}}
    deps = about_rows(active)
    dlls, ndll = dll_refs(active)
    ev = {
        "item": "LANDFORMS_PROBE_REPLACE_OR_KEEP_EXPERIMENT",
        "dump": a.dump, "dumpTileMutatorDefs": len(rows),
        "glTileMutatorDefs": gl_defs, "glLandformFiles": len(glob.glob(os.path.join(GL_DIR, "1.6", "Landforms-v1", "*.xml"))),
        "glDisabledUnderOdyssey": off, "vanillaMutatorsGlDisables": off_vanilla, "glEnabled": enabled,
        "listAsMeasured": {"path": a.list, "active": len(active), "carriedGL": GL in active},
        "dependents": deps, "dllReferences": dlls, "dllsScanned": ndll,
        "saveMutators": save_mutators(a.save, rows),
        "coverage": cov,
        "coverageCounts": dict(collections.Counter(v["verdict"] for v in cov.values())),
        "vanillaDefsNamed": sorted({d for v in cov.values() for d, w in v["where"].items() if w != "src"}),
    }
    with open(a.out, "w", encoding="utf-8") as f:
        json.dump(ev, f, indent=1, sort_keys=True)
        f.write("\n")
    print("wrote %s: %d GL defs, %d enabled, coverage %s, save GL entries %d (unresolved %d), dependents %d"
          % (os.path.relpath(a.out, ROOT), len(gl_defs), len(enabled), ev["coverageCounts"],
             ev["saveMutators"]["glEntries"], len(ev["saveMutators"]["unresolved"]), len(deps)))


if __name__ == "__main__":
    main()
