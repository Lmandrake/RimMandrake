#!/usr/bin/env python3
"""check_kit_art.py - offline proof for GELATINOUSSLIME_KIT_ART_1: the Slime free kit draws its own art.

    python3 src/RimMandrake/GelatinousSlime/check_kit_art.py        exit 0 holds, 1 fails

Holds when, over every Def XML under src/RimMandrake/GelatinousSlime/Defs/:
  1. every texture path (texPath, texturePath, pollutedTexturePath, pollutionOverlayTexturePath, iconPath,
     leaflessGraphicPath, texture, ...) resolves to a PNG of this mod's own Textures/ (bare file, a _south/_east/_north
     facing, or a Graphic_Random folder), or is on ALLOWED below with its reason;
  2. no path names the vanilla tortoise or dandelion (the stand-ins the item was filed to remove), allowlist or not;
  3. every ALLOWED entry is still in use (a stale entry would let the allowlist hide a regression);
  4. each kit row of the art list (rimflow_item_id GELATINOUSSLIME_KIT_ART_1) has a def whose graphic resolves to
     our own art;
  5. sanity: the scan saw at least MIN_PATHS paths, so a broken parse cannot pass by seeing nothing.
"""
import csv
import sys
import xml.etree.ElementTree as ET
from pathlib import Path

MOD = Path(__file__).resolve().parent
REPO = MOD.parents[2]
DEFS = MOD / "Defs"
TEX = MOD / "Textures"
ART_LIST = REPO / "infrastructure/artpipe/art_lists/gelatinousslime_turn1_2026-10-02.csv"
ITEM = "GELATINOUSSLIME_KIT_ART_1"
MIN_PATHS = 40
PATH_TAGS = {"texPath", "texture", "iconPath", "uiIconPath", "texturePath", "pollutedTexturePath",
             "pollutionOverlayTexturePath", "leaflessGraphicPath", "immatureGraphicPath",
             "flyingAnimationFramePathPrefix", "wornGraphicPath", "graphicPath"}
FORBIDDEN = ("tortoise", "dandelion")

# Vanilla paths that remain on purpose, each with why. Anything vanilla not here fails.
ALLOWED = {
    "UI/Icons/Genes/Gene_TotalToxicityResistance":
        "RM_Gene_SlimeResistance gene icon: a UI icon in the gene picker, never drawn on the map; not a kit row",
    "Things/Item/Meal/Lavish":
        "RM_Meal_SlimeAmbrosyx: the pit-solvent dish, art owed by GELATINOUSSLIME_PIT_SOLVENT_1 (not a kit row)",
    "Things/Filth/Spatter":
        "RM_Filth_SlimeSmear: filth draws the vanilla spatter SHAPE tinted slime-green by <color>, as vanilla filths do",
    "Terrain/Surfaces/Soil": "RM_Slime_Hardened terrain: ground, not a kit row (biome terrain art is separate work)",
    "Terrain/Surfaces/Mossy": "RM_Slime_Rich terrain: ground, not a kit row",
    "Terrain/Surfaces/SoilRich": "RM_Slime_Grass terrain: ground, not a kit row",
    "Terrain/Surfaces/Mud": "RM_Slime_Mud terrain: ground, not a kit row",
    "Terrain/Surfaces/MarshyTerrain": "RM_Slime_Liquid terrain: ground, not a kit row",
    "Terrain/Surfaces/PollutionMud": "donor slime terrains' pollution overlay: the vanilla overlay every terrain uses",
}

# art-list id -> the def that draws it (the kit's defNames differ from some list ids)
KIT_DEFS = {"RM_Gelatid": "RM_Gelatid", "RM_SlimeGrass": "RM_Plant_SlimeGrass", "RM_SlimeBellows": "RM_Plant_Bellows",
            "RM_Thumbstalk": "RM_Plant_Thumbstalk", "RM_Readerbloom": "RM_Plant_Readerbloom",
            "RM_SlimeCompressor": "RM_SlimeCompressor", "RM_SlimePit": "RM_SlimePit", "RM_SlimeBlock": "RM_SlimeBlock",
            "RM_RawSlime": "RM_RawSlime", "RM_SlimeAntidote": "RM_SlimeAntidote", "RM_GeneSeeker": "RM_GeneSeeker",
            "RM_GeneSeekerLoaded": "RM_GeneSeeker_Loaded"}


def resolves_own(path):
    base = TEX / path
    if base.with_suffix(".png").is_file() or Path(str(base) + ".png").is_file():
        return True
    if any(Path(f"{base}_{f}.png").is_file() for f in ("south", "east", "north")):
        return True
    return base.is_dir() and any(base.glob("*.png"))


def scan():
    """Yield (file, defName, tag, path) for every texture path in the mod's Defs."""
    for f in sorted(DEFS.rglob("*.xml")):
        root = ET.parse(f).getroot()
        for d in root:
            dn = d.findtext("defName") or d.get("Name") or "?"
            for el in d.iter():
                if el.tag in PATH_TAGS and (el.text or "").strip():
                    yield f.relative_to(MOD), dn, el.tag, el.text.strip()


def main():
    fails, seen_allowed, rows = [], set(), list(scan())
    if len(rows) < MIN_PATHS:
        fails.append(f"sanity: only {len(rows)} texture paths seen (< {MIN_PATHS}); the scan is blind")
    for f, dn, tag, p in rows:
        if any(w in p.lower() for w in FORBIDDEN):
            fails.append(f"stand-in: {f} {dn} <{tag}> {p}")
        elif not resolves_own(p):
            if p in ALLOWED:
                seen_allowed.add(p)
            else:
                fails.append(f"vanilla/unresolved: {f} {dn} <{tag}> {p}")
    for p in sorted(set(ALLOWED) - seen_allowed):
        fails.append(f"stale allowlist entry (no longer used): {p}")
    graphic = {}
    for f, dn, tag, p in rows:
        if tag == "texPath":
            graphic.setdefault(dn, []).append(p)
    with open(ART_LIST, newline="") as fh:
        kit = [r["id"] for r in csv.DictReader(fh) if r["rimflow_item_id"] == ITEM]
    if len(kit) != len(KIT_DEFS):
        fails.append(f"art list has {len(kit)} kit rows, KIT_DEFS maps {len(KIT_DEFS)}")
    for rid in kit:
        dn = KIT_DEFS.get(rid)
        paths = graphic.get(dn, [])
        if not paths:
            fails.append(f"kit row {rid}: def {dn} has no texPath")
        for p in paths:
            if not resolves_own(p):
                fails.append(f"kit row {rid}: {dn} draws {p}, not our art")
    print(f"scanned {len(rows)} texture paths; kit rows {len(kit)}; vanilla on purpose {len(seen_allowed)}:")
    for p in sorted(seen_allowed):
        print(f"  {p} -- {ALLOWED[p]}")
    for x in fails:
        print("FAIL", x)
    print("HOLDS" if not fails else f"FAILS ({len(fails)})")
    return 1 if fails else 0


if __name__ == "__main__":
    sys.exit(main())
