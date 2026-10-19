#!/usr/bin/env python3
"""Offline: no sea-floor biome lists a precipitation weather (TWILIGHT_SEA_FIX_IT_RAINS_UNDERWATER).

Owner 2026-10-16: "Twilight Sea is a sea floor... no rain." Every seabed biome (RM_ and its RUT_ twin, plus the
seabed-layer floors) is parsed as XML; its baseWeatherCommonalities children must hold no rain/snow/storm weather.
RM_GreySaltSnow is the Grey's designed salt fall, not precipitation, and is allowed.

    python3 src/RimMandrake/TerminalBiomes/selftest_sea_floor_no_rain.py
"""
import os
import re
import sys
import xml.etree.ElementTree as ET

ROOT = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", ".."))
FILES = [
    "src/RimMandrake/TerminalBiomes/Defs/BiomeDefs/RM_TwilightSea.xml",
    "src/RimMandrake/TerminalBiomes/Defs/BiomeDefs/RM_GreySea.xml",
    "src/RimMandrake/TerminalBiomes/Defs/BiomeDefs/RM_TheScald.xml",
    "src/RimMandrake/TerminalBiomes/Defs/BiomeDefs/RM_TheChill.xml",
    "src/RimMandrake/LanternDeeps/Defs/Biomes/RM_LanternDeeps.xml",
    "src/RimUtinni/UtinniPatches/Defs/BiomeDefs/RUT_TwilightSea.xml",
    "src/RimUtinni/UtinniPatches/Defs/BiomeDefs/RUT_GreySea.xml",
    "src/RimUtinni/UtinniPatches/Defs/BiomeDefs/RUT_TheScald.xml",
    "src/RimUtinni/UtinniPatches/Defs/BiomeDefs/RUT_PropaneLake.xml",
    "src/RimMandrake/DivingInteraction/Defs/PlanetLayerDefs/RM_SeabedFloorBiomes.xml",
    "src/RimMandrake/DivingInteraction/Patches/RM_SeabedFloor_GreyWeather.xml",
]
PRECIP = re.compile(r"rain|snow|storm|drizzle|hail|sleet|monsoon", re.I)
ALLOWED = {"RM_GreySaltSnow"}


def precip_in(root):
    bad = []
    for wc in root.iter("baseWeatherCommonalities"):
        for el in wc:
            if PRECIP.search(el.tag) and el.tag not in ALLOWED:
                bad.append(el.tag)
    return bad


def main():
    fails = 0
    # sanity probe: the instrument must see a Rain row when one is there
    probe = ET.fromstring("<Defs><BiomeDef><baseWeatherCommonalities><Clear>1</Clear><Rain>4</Rain>"
                          "<RM_GreySaltSnow>2</RM_GreySaltSnow></baseWeatherCommonalities></BiomeDef></Defs>")
    if precip_in(probe) != ["Rain"]:
        print("FAIL  probe: instrument cannot see a Rain row"); return 1
    print("ok    probe sees Rain, allows RM_GreySaltSnow")
    seen = 0
    for rel in FILES:
        p = os.path.join(ROOT, rel)
        if not os.path.exists(p):
            print("FAIL  missing %s" % rel); fails += 1; continue
        root = ET.parse(p).getroot()
        seen += sum(1 for _ in root.iter("baseWeatherCommonalities"))
        bad = precip_in(root)
        print("%s  %s %s" % ("FAIL" if bad else "ok  ", rel, bad or ""))
        fails += bool(bad)
    if seen < 9:
        print("FAIL  only %d weather lists seen; instrument is blind" % seen); fails += 1
    print("%s: %d file(s), %d weather list(s)" % ("FAIL" if fails else "PASS", len(FILES), seen))
    return 1 if fails else 0


if __name__ == "__main__":
    sys.exit(main())
