#!/usr/bin/env python3
"""Selftest: the saevitha (RM_Cindermare) has only the attacks that its own def declares.

The engine appends a child's <tools> list to the parent's (ThingBaseWolf: claws, a bite, a head butt). The saevitha has no
mouth, so its <tools> carries Inherit="False". Seen live before the fix: 7 tools, the wolf's bite among them
(capture 2026-11-24T11-26-11Z).

    python3 src/RimMandrake/Abyss/selftest_abyss_saevitha_no_bite.py
"""
import os
import sys
import xml.etree.ElementTree as ET

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "Utils"))
import def_inventory  # noqa: E402

WOLF = "<ThingDef><tools><li><capacities><li>Bite</li></capacities></li></tools></ThingDef>"


def main():
    root = ET.parse(os.path.join(HERE, "Defs", "ThingDefs_Races", "RM_Cindermare.xml")).getroot()
    own = [n for n in root if n.tag == "ThingDef" and n.findtext("defName") == "RM_Cindermare"][0]
    got = ET.fromstring(WOLF)
    def_inventory._merge_into(own, got)
    labels = [t.findtext("label") for t in got.find("tools")]
    ok = labels == ["left claw", "right claw", "cold-drain grip"]
    print("%s: resolved tools %r" % ("PASS" if ok else "FAIL", labels))
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
