#!/usr/bin/env python3
"""Write a ModsConfig.xml for a sweep batch: base + listed packageIds."""
import sys, xml.etree.ElementTree as ET

LIVE = "/mnt/c/Users/Mandrake/AppData/LocalLow/Ludeon Studios/RimWorld by Ludeon Studios/Config/ModsConfig.xml"
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
