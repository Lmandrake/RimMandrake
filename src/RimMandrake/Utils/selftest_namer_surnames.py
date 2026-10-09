#!/usr/bin/env python3
"""Every species namer in SW_NameMakers.xml that ships a surname list (keyword
LastName<X>) must draw its surname from it. A namer whose lastGenerated/lastName rules
reference only [Name<X>] gives pawns two given names (XENOTYPE_CANON_CORRECTION_1)."""
import os, re, sys
import xml.etree.ElementTree as ET

HERE = os.path.dirname(os.path.abspath(__file__))
P = os.path.join(HERE, "..", "..", "RimStarWars", "StarWarsRaces", "Defs",
                 "RulePackDefs", "SW_NameMakers.xml")


def main():
    root = ET.parse(P).getroot()           # also proves the file parses
    bad, wired, nolast = [], 0, []
    for d in root.findall("RulePackDef"):
        name = d.findtext("defName")
        kws = {l.findtext("keyword"): l.findtext("path")
               for l in d.findall("rulePack/rulesRaw/li")}
        lasts = [k for k in kws if k.startswith("LastName")]
        if not lasts:
            nolast.append(name)
            continue
        text = "\n".join(l.text or "" for l in d.findall("rulePack/rulesStrings/li"))
        if any("[" + k + "]" in text for k in lasts) and "[lastName" in text:
            wired += 1
        else:
            bad.append(name)
    if bad:
        print("FAIL surname list unused: %s" % ", ".join(bad))
        return 1
    assert wired >= 40, "sanity probe: expected >=40 wired namers, saw %d" % wired
    print("PASS %d namers wire their surname list; %d have none (%s)"
          % (wired, len(nolast), ", ".join(nolast)))
    return 0


if __name__ == "__main__":
    sys.exit(main())
