#!/usr/bin/env python3
"""Offline: no player-facing sea text places life on a sea's surface (SEA_DESCRIPTIONS_CORRECT_NO_SURFACE_PLACE).

Owner 2026-11-01: "You are either on their sea floor, or you are on their beach. There is no 'on their
surface' location." Every def and keyed line of the four seas (RM_ and RUT_ twins) is parsed as XML. A text
naming a surface or top layer fails unless SURFACE_IS_NOT_THE_SEA says why it is another surface (a brine
pool's, a material's, the surface world). Scald comments may not cite the withdrawn "no macro-life" ban 4.

    python3 src/RimMandrake/TerminalBiomes/Tools/selftest_sea_text_no_surface_place.py
"""
import os
import re
import sys
import xml.etree.ElementTree as ET

ROOT = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "..", ".."))
TB = "src/RimMandrake/TerminalBiomes"
RUT = "src/RimUtinni/UtinniPatches"
# Every tree holding sea defs; RUT_ twins and other mods' files only when the file names a sea.
WHOLE_TREES = [TB + "/Defs", TB + "/Patches", TB + "/Languages"]
SEA_NAMED_TREES = [RUT + "/Defs", RUT + "/Patches", RUT + "/Languages",
                   "src/RimMandrake/DivingInteraction/Defs", "src/RimMandrake/DivingInteraction/Languages"]
SEA_NAME = re.compile(r"Scald|Chill|Twilight|GreySea|Propane|Seabed", re.I)

PLACE = re.compile(r"\bsurface\b|\btop layer\b|\btopside\b|dead calm on", re.I)
FACING = ("description", "label", "descriptionShort", "letterText", "letterLabel", "baseDescription")

# defName or keyed tag -> why its "surface" is not the sea's. Anything else naming one fails.
SURFACE_IS_NOT_THE_SEA = {
    "RM_BrineChannel": "the brine's own face, inside the water on the floor",
    "RM_BrinePoolDeep": "the brine pool's face, on the floor",
    "RM_SaltChimneyVine": "the surface of a mineral spiral",
    "RM_Stillbloom": "the brine pool's interface, on the floor",
    "RM_LampBlack": "the surface world: dye-houses",
    "RM_Tithemoss": "the surface world: its people",
}

# The defs the item named or the sweep found, so a rename cannot make this test pass by not looking.
MUST_SEE = {
    "RM_Oovu", "RM_OovuCatch", "RUT_Oovu", "RM_ScaldWaterDeep", "RM_ScaldWaterOceanDeep", "RM_Heemin",
    "RM_Vaunoom", "RUT_VWake", "RM_Hollu", "RM_HolluCatch", "RUT_Hollu", "RM_Bladderboil",
    "RM_BladderboilCatch", "RUT_BladderboilCatch", "RM_TwilightSea", "RM_WalkerSurfacingSighting",
}

# Text of the withdrawn ban. The Chill's and Grey's own "ban 4" are other bans and still stand.
WITHDRAWN_BAN = re.compile(r"no macro-life|roiling surface layer|swims the roiling|Ban 4's own carve-out|§6 ban 4", re.I)
SCALD_COMMENT_FILES = [
    TB + "/Defs/TerrainDefs/RM_ScaldWater.xml",
    TB + "/Defs/TerrainDefs/RM_ScaldMargin.xml",
    TB + "/Defs/ThingDefs_Races/RM_ScaldFloorFauna.xml",
    "src/RimMandrake/EnvironmentalHazards/Source/RM_IncidentWorker_WalkerSurfacing.cs",
]


def sea_files():
    out = []
    for trees, need_name in ((WHOLE_TREES, False), (SEA_NAMED_TREES, True)):
        for tree in trees:
            for dirpath, _dirs, names in os.walk(os.path.join(ROOT, tree)):
                for name in names:
                    if name.endswith(".xml") and (not need_name or SEA_NAME.search(name)):
                        out.append(os.path.join(dirpath, name))
    return sorted(out)


def texts(root):
    """Yield (name, text) for every player-facing text under a parsed XML root."""
    if root.tag == "LanguageData":
        for el in root:
            yield el.tag, el.text or ""
        return
    for parent in root.iter():
        name = parent.findtext("defName")
        if name is None:
            continue
        for tag in FACING:
            text = parent.findtext(tag)
            if text:
                yield name, text


def main():
    failures = []
    # The instrument must catch the sentences this item removed.
    for old in ("A bell of frozen hydrocarbon jelly that rides at the surface of the fuel",
                "It is dead calm on the surface and scalding underneath",
                "A near-transparent sliver swimming the top layer of the Chill",
                "that sheets so much of the topside ocean like stained glass"):
        if not PLACE.search(old):
            failures.append("instrument blind to: " + old)

    files = sea_files()
    seen = set()
    total = 0
    for path in files:
        rel = os.path.relpath(path, ROOT)
        try:
            root = ET.parse(path).getroot()
        except ET.ParseError as exc:
            failures.append("%s: does not parse: %s" % (rel, exc))
            continue
        for name, text in texts(root):
            total += 1
            seen.add(name)
            if PLACE.search(text) and name not in SURFACE_IS_NOT_THE_SEA:
                m = PLACE.search(text)
                failures.append("%s %s: places life on the surface: ...%s..."
                                % (rel, name, text[max(0, m.start() - 50):m.end() + 40].replace("\n", " ")))

    missing = sorted(MUST_SEE - seen)
    if missing:
        failures.append("could not see named defs (renamed or moved?): " + ", ".join(missing))
    if len(files) < 100 or total < 500:
        failures.append("too little parsed to trust a pass: %d files, %d texts" % (len(files), total))

    for rel in SCALD_COMMENT_FILES:
        with open(os.path.join(ROOT, rel), encoding="utf-8") as f:
            for lineno, line in enumerate(f, 1):
                if WITHDRAWN_BAN.search(line):
                    failures.append("%s:%d: cites the withdrawn Scald ban 4: %s" % (rel, lineno, line.strip()))

    for line in failures:
        print("FAIL " + line)
    print("%s: %d sea files, %d player-facing texts, %d failures"
          % ("FAIL" if failures else "PASS", len(files), total, len(failures)))
    return 1 if failures else 0


if __name__ == "__main__":
    sys.exit(main())
