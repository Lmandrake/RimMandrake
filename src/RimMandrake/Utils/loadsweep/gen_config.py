#!/usr/bin/env python3
"""Write a ModsConfig.xml for a sweep batch: base + listed packageIds."""
import os, sys, xml.etree.ElementTree as ET

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from game_paths import MODS_CONFIG  # noqa: E402

LIVE = MODS_CONFIG
BASE = [
    "brrainz.harmony",
    "ludeon.rimworld",
    "ludeon.rimworld.royalty",
    "ludeon.rimworld.ideology",
    "ludeon.rimworld.biotech",
    "ludeon.rimworld.anomaly",
    "ludeon.rimworld.odyssey",
    "imranfish.xmlextensions",
    "brrainz.rimbridgeserver",
]

def main(listfile):
    extra = [l.strip() for l in open(listfile) if l.strip() and not l.startswith("#")]
    mods = BASE + extra
    tree = ET.parse(LIVE)  # keep version + knownExpansions from the live file
    root = tree.getroot()
    am = root.find("activeMods")
    for li in list(am):
        am.remove(li)
    for m in mods:
        e = ET.SubElement(am, "li")
        e.text = m
    tree.write(LIVE, encoding="utf-8", xml_declaration=True)
    print(f"wrote {len(mods)} active mods to live ModsConfig.xml")

if __name__ == "__main__":
    main(sys.argv[1])
