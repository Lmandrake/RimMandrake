#!/usr/bin/env python3
"""OQ-2 / OQ-4 (owner, by card, 2026-10-16): biome density classes. Five classes in ONE table
(src/RimMandrake/Utils/biome_density_classes.json); a biome declares its class in its own file with
`<!-- RM_DENSITY_CLASS: <name> -->` inside the BiomeDef, and its plantDensity / wildPlantRegrowDays must equal the
class's pair. "New biomes first": existing biomes are not moved by this test (moving one is a review row).

    python3 src/RimMandrake/Utils/selftest_biome_density_classes.py

Sanity probes first (instrument_traps: zero declaring biomes is the expected state today, so the parser must prove on
fixtures that it SEES a declaration, a drift and an unknown class before its silence over src/ means anything).
"""
import glob
import json
import os
import re
import sys
import xml.etree.ElementTree as ET

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(os.path.dirname(os.path.dirname(HERE)))
TABLE = os.path.join(HERE, "biome_density_classes.json")
FIX = os.path.join(HERE, "selftest_fixtures", "density_classes")
MARK = re.compile(r"<!--\s*RM_DENSITY_CLASS:\s*([A-Za-z_]+)\s*-->")


def check_file(path, classes):
    """-> (declared, problems) for every BiomeDef in one XML file."""
    text = open(path, encoding="utf-8", errors="replace").read()
    if "RM_DENSITY_CLASS" not in text:
        return 0, []
    declared, bad = 0, []
    for m in re.finditer(r"<BiomeDef\b[^>]*>(.*?)</BiomeDef>", text, re.S):
        body = m.group(1)
        k = MARK.search(body)
        if not k:
            continue
        declared += 1
        name = (re.search(r"<defName>([^<]+)</defName>", body) or [None, "?"])[1]
        cls = k.group(1)
        if cls not in classes:
            bad.append("%s %s: density class %r is not in the table (%s)" % (os.path.relpath(path, REPO), name, cls, ", ".join(classes)))
            continue
        for field in ("plantDensity", "wildPlantRegrowDays"):
            v = re.search(r"<%s>([^<]+)</%s>" % (field, field), body)
            want = classes[cls][field]
            if not v:
                bad.append("%s %s: class %s but no <%s> (want %s)" % (os.path.relpath(path, REPO), name, cls, field, want))
            elif abs(float(v.group(1)) - float(want)) > 1e-9:
                bad.append("%s %s: class %s %s is %s, the table says %s" % (os.path.relpath(path, REPO), name, cls, field, v.group(1), want))
    return declared, bad


def main():
    fails = []
    table = json.load(open(TABLE, encoding="utf-8"))["classes"]
    if len(table) != 5:
        fails.append("the table has %d classes; OQ-4 ruled five" % len(table))
    for c, v in table.items():
        if set(v) != {"plantDensity", "wildPlantRegrowDays"}:
            fails.append("class %s carries %s" % (c, sorted(v)))
    # sanity probes on fixtures
    n, bad = check_file(os.path.join(FIX, "good.xml"), table)
    if n != 1 or bad:
        fails.append("probe: good fixture read %d declarations, %r (want 1, none)" % (n, bad))
    n, bad = check_file(os.path.join(FIX, "bad.xml"), table)
    if n != 2 or len(bad) != 3:
        fails.append("probe: bad fixture read %d declarations and %d problems (want 2 and 3: two drifted numbers, one unknown class): %r" % (n, len(bad), bad))
    # the repo
    files = glob.glob(os.path.join(REPO, "src", "**", "*.xml"), recursive=True)
    biome_files = [p for p in files if "selftest_fixtures" not in p and "<BiomeDef" in open(p, encoding="utf-8", errors="replace").read()]
    if len(biome_files) < 10:
        fails.append("probe: only %d BiomeDef files found under src/ (the glob went blind)" % len(biome_files))
    declared = 0
    for p in biome_files:
        d, bad = check_file(p, table)
        declared += d
        fails.extend(bad)
    print("biome density classes: %d classes, %d BiomeDef files, %d biome(s) declare a class" % (len(table), len(biome_files), declared))
    for f in fails:
        print("FAIL " + f)
    print("selftest_biome_density_classes: %s" % ("OK" if not fails else "FAILED"))
    return 1 if fails else 0


if __name__ == "__main__":
    sys.exit(main())
