#!/usr/bin/env python3
"""selftest_warden_mother_art.py — RM_WardenMother draws, and her last season draws aged.

MIASMA_WARDEN_MOTHER_ART_1. Offline half of the item's criteria:
  * every lifeStage texPath of the RM_WardenMother PawnKindDef resolves to a
    Graphic_Multi set (_south, _east, _north PNGs) inside this mod — a missing
    file is the magenta/missing-texture warning in game;
  * the LAST lifeStage (the RM_WardenMotherElder stage, her last season) points
    at a DIFFERENT texture set than the adult stage, and that set really differs
    in pixels (an aged copy that is byte-identical to the adult is no swap);
  * the race's last lifeStageAges entry is RM_WardenMotherElder, so the two lists
    line up (PawnKindDef.lifeStages is indexed by the race's lifeStageAges);
  * each PNG is RGBA with real alpha, and each aged facing keeps the adult
    facing's footprint (bbox within 4%) so the swap does not pop or shift her.

Exit 0 = all hold, 1 = a failure (printed).
"""
import sys
import xml.etree.ElementTree as ET
from pathlib import Path

from PIL import Image

MOD = Path(__file__).resolve().parent
DEF = MOD / "Defs" / "ThingDefs_Races" / "RM_WardenMother.xml"
TEX = MOD / "Textures"
FACINGS = ("south", "east", "north")


def bbox(path):
    return Image.open(path).convert("RGBA").getchannel("A").point(lambda v: 255 if v > 128 else 0).getbbox()


def main():
    fails = []
    root = ET.parse(DEF).getroot()
    race = next(t for t in root.iter("ThingDef") if t.findtext("defName") == "RM_WardenMother")
    ages = [li.findtext("def") for li in race.find("race/lifeStageAges")]
    kind = next(k for k in root.iter("PawnKindDef") if k.findtext("defName") == "RM_WardenMother")
    paths = [li.findtext("bodyGraphicData/texPath") for li in kind.find("lifeStages")]

    if ages[-1] != "RM_WardenMotherElder":
        fails.append(f"last lifeStageAges entry is {ages[-1]!r}, not RM_WardenMotherElder")
    if len(ages) != len(paths):
        fails.append(f"{len(ages)} lifeStageAges but {len(paths)} PawnKindDef lifeStages")

    for tp in sorted(set(paths)):
        for f in FACINGS:
            png = TEX / f"{tp}_{f}.png"
            if not png.is_file():
                fails.append(f"missing {png.relative_to(MOD)}")
                continue
            im = Image.open(png)
            if im.mode != "RGBA" or im.getchannel("A").getextrema()[0] != 0:
                fails.append(f"{png.name}: no real alpha (mode {im.mode})")

    adult, elder = paths[-2], paths[-1]
    if adult == elder:
        fails.append(f"elder stage reuses the adult art ({elder})")
    elif not fails:
        for f in FACINGS:
            a, e = TEX / f"{adult}_{f}.png", TEX / f"{elder}_{f}.png"
            if a.read_bytes() == e.read_bytes():
                fails.append(f"{e.name} is byte-identical to {a.name}")
                continue
            ba, be = bbox(a), bbox(e)
            for i, (x, y) in enumerate(zip(ba, be)):
                if abs(x - y) > 0.04 * 512:
                    fails.append(f"{e.name}: bbox {be} drifts from adult {ba}")
                    break

    for line in fails:
        print("FAIL", line)
    print(f"{'PASS' if not fails else 'FAIL'} warden mother art: stages={paths}")
    return 1 if fails else 0


if __name__ == "__main__":
    sys.exit(main())
