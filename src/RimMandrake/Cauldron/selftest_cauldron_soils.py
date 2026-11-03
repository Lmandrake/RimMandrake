#!/usr/bin/env python3
"""Offline proof of CAULDRON_SOILS_BUILD_DIRT_THAT_BREATHES: the Cauldron's two soils wear the
dark, gassy art the owner picked, and the rich soil reads visibly different from the plain one.

Chain checked, each link read from its own record (nothing hard-coded but the def names):
  TerrainDef texturePath -> PNG in this mod's Textures/
  owner's pick on the sheet (decisions.json) -> label -> render job (sheet snapshot)
  render job -> sha256 in the art ledger -> must equal the installed PNG's sha256
Then the pixels: both soils dark (mean luma under DARK_MAX), and plain vs rich apart by at least
MIN_RGB_DISTANCE in mean colour. The walk bar `cauldron_soils_read_dark` stays a human look; this
only proves the shipped files are the picked art and are measurably dark and distinct.

    python3 src/RimMandrake/Cauldron/selftest_cauldron_soils.py
"""
import glob
import hashlib
import json
import math
import os
import sys
import xml.etree.ElementTree as ET

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
DEFS = os.path.join(HERE, "Defs", "TerrainDefs", "RM_Cauldron_Terrains.xml")
SHEET = "cauldron_soils_sheet_2026-10-20"
DECISIONS = os.path.join(ROOT, "Transient", "biome_ffar", SHEET + ".decisions.json")
SNAPSHOT = os.path.join(ROOT, "infrastructure", "state", "art", "sheets", SHEET + ".snapshot.json")
ART_EVENTS = os.path.join(ROOT, "infrastructure", "state", "art", "events", "*.jsonl")
SOILS = ("RM_CauldronSoil", "RM_CauldronSoilRich")
DARK_MAX = 70.0          # mean luma, 0-255; vanilla-bright dirt sits well above this
MIN_RGB_DISTANCE = 12.0  # mean-colour distance plain vs rich


def sha256(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def job_shas():
    out = {}
    for p in glob.glob(ART_EVENTS):
        with open(p, encoding="utf-8") as f:
            for line in f:
                if "cauldronsoil" not in line:
                    continue
                e = json.loads(line)
                if e.get("job") and e.get("sha"):
                    out.setdefault(e["job"], set()).add(e["sha"])
    return out


def main():
    fails = []
    texpaths = {}
    for td in ET.parse(DEFS).getroot().iter("TerrainDef"):
        name = td.findtext("defName")
        if name in SOILS:
            texpaths[name] = td.findtext("texturePath")
    decisions = json.load(open(DECISIONS, encoding="utf-8"))["decisions"]
    rows = json.load(open(SNAPSHOT, encoding="utf-8"))["rows"]
    shas = job_shas()
    means = {}
    try:
        from PIL import Image, ImageStat
    except ImportError:
        print("FAIL: Pillow missing; pixel checks cannot run")
        return 1
    for soil in SOILS:
        tp = texpaths.get(soil)
        if not tp:
            fails.append(f"{soil}: no texturePath in {DEFS}")
            continue
        png = os.path.join(HERE, "Textures", tp + ".png")
        if not os.path.isfile(png):
            fails.append(f"{soil}: texturePath {tp} has no PNG in this mod")
            continue
        pick = decisions.get(soil, {}).get("decision")
        label = rows.get(soil, {}).get("labels", {}).get(pick, "")
        job = label.split()[-1] if label.startswith("render ") else None
        if not job:
            fails.append(f"{soil}: owner pick {pick!r} is not a render on the sheet ({label!r})")
            continue
        got = sha256(png)
        if got not in shas.get(job, set()):
            fails.append(f"{soil}: installed sha {got[:12]} is not job {job} ({sorted(shas.get(job, []))})")
        rgba = Image.open(png).convert("RGBA")
        alpha_min = rgba.getchannel("A").getextrema()[0]
        if alpha_min < 250:  # terrain tiles are opaque; hidden RGB under alpha would fake a pass
            fails.append(f"{soil}: not opaque (min alpha {alpha_min})")
        im = rgba.convert("RGB")
        means[soil] = ImageStat.Stat(im).mean
        luma = ImageStat.Stat(im.convert("L")).mean[0]
        if luma >= DARK_MAX:
            fails.append(f"{soil}: mean luma {luma:.1f} >= {DARK_MAX} (not dark)")
        print(f"{soil}: pick {pick} = {job}, sha ok={got in shas.get(job, set())}, luma {luma:.1f}")
    if len(means) == 2:
        d = math.dist(means[SOILS[0]], means[SOILS[1]])
        print(f"plain vs rich mean-colour distance {d:.1f}")
        if d < MIN_RGB_DISTANCE:
            fails.append(f"rich soil not distinct: distance {d:.1f} < {MIN_RGB_DISTANCE}")
    for f in fails:
        print("FAIL:", f)
    print("PASS" if not fails else f"{len(fails)} failure(s)")
    return 1 if fails else 0


if __name__ == "__main__":
    sys.exit(main())
