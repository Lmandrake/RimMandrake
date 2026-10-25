"""HEAVY_BRIDGE_RENAME_TRUSS_LIKE_THE_PHOTO (owner card 2026-10-25: "Heavy bridge name -> Heavy truss bridge"; the
art is a truss, per his photo). Pins the player-facing names of the heavy deck, its grated variant and its anchor,
and that the defNames (saves, patches, designators) did not move. Offline: reads the def XML and the C# message."""
import os
import sys
import xml.etree.ElementTree as ET

HERE = os.path.dirname(os.path.abspath(__file__))
DEFS = os.path.join(HERE, "Defs", "Pits", "ThingDefs", "RM_SuspensionBridges.xml")
MATH = os.path.join(HERE, "Source", "RM_SuspensionMath.cs")

WANT = {
    "RM_SuspensionDeck_Heavy": "heavy truss bridge",
    "RM_SuspensionDeck_HeavyGrated": "grated heavy truss bridge",
    "RM_SuspensionAnchor_Heavy": "heavy truss bridge anchor",
}


def main():
    fails = []
    root = ET.parse(DEFS).getroot()
    defs = {d.findtext("defName"): d for d in root if d.findtext("defName")}
    for name, label in WANT.items():
        d = defs.get(name)
        if d is None:
            fails.append("can-fail: defName %s gone (a rename must keep defNames)" % name)
            continue
        if d.findtext("label") != label:
            fails.append("%s label %r, want %r" % (name, d.findtext("label"), label))
        if "heavy suspension" in (d.findtext("description") or "").lower():
            fails.append("can-fail: %s description still says heavy suspension bridge" % name)
    if "heavy suspension bridge" in open(MATH, encoding="utf-8").read():
        fails.append("can-fail: RM_SuspensionMath.cs still tells the player 'heavy suspension bridge'")
    if 'return t == SuspensionTier.Heavy ? "heavy truss bridge" : TierLabel(t) + " suspension bridge";' not in open(MATH, encoding="utf-8").read():
        fails.append("can-fail: RM_SuspensionMath.BridgeName does not name the heavy tier a truss (span/width refusals, give-way messages)")
    for f in fails:
        print("FAIL  " + f)
    print("ok    heavy truss labels (%d defs)" % len(WANT) if not fails else "FAIL  %d" % len(fails))
    return 1 if fails else 0


if __name__ == "__main__":
    sys.exit(main())
