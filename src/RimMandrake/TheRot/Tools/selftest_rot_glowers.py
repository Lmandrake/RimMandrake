#!/usr/bin/env python3
"""selftest_rot_glowers.py -- every CompProperties_Glower in TheRot's defs states its own radius and colour.

An empty <li Class="CompProperties_Glower"/> loads silently with the engine defaults: glowRadius 14 and colour
(369,369,369,0), 1.45x white, brighter than a standing lamp (live def dump 2026-10-25T23-14-27Z). RM_Illoth's
"faint amber" fungal lantern shipped exactly that way. This scans every Defs/**/*.xml under TheRot, demands both
<glowRadius> and <glowColor> on each glower, and proves on planted text that the scan can see an empty one.
    python3 src/RimMandrake/TheRot/Tools/selftest_rot_glowers.py
"""
import glob
import os
import sys
import xml.etree.ElementTree as ET

ROT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
REQUIRED = ("glowRadius", "glowColor")


def glower_findings(text, where):
    """(findings, glower count) for one XML document's text."""
    root = ET.fromstring(text)
    out, n = [], 0
    for parent in root.iter():
        for li in parent.findall("li"):
            if li.get("Class") != "CompProperties_Glower":
                continue
            n += 1
            missing = [f for f in REQUIRED if li.find(f) is None or not (li.find(f).text or "").strip()]
            if missing:
                owner = next((d.findtext("defName") for d in root if d.find(".//li") is not None
                              and any(x is li for x in d.iter())), None)
                out.append("%s: %s glower lacks %s (engine default: radius 14, 1.45x white)"
                           % (where, owner or "?", "/".join(missing)))
    return out, n


def scan():
    findings, total, files = [], 0, 0
    for path in sorted(glob.glob(os.path.join(ROT, "Defs", "**", "*.xml"), recursive=True)):
        files += 1
        f, n = glower_findings(open(path, encoding="utf-8").read(), os.path.relpath(path, ROT))
        findings += f
        total += n
    return findings, total, files


def main():
    findings, total, files = scan()
    cases = [("shipped defs clean", not findings)]
    good = ('<Defs><ThingDef><defName>X</defName><comps><li Class="CompProperties_Glower">'
            '<glowRadius>2</glowRadius><glowColor>(1,2,3,0)</glowColor></li></comps></ThingDef></Defs>')
    cases.append(("full glower green", glower_findings(good, "planted")[0] == []))
    for name, old, new in (("empty glower red", "<glowRadius>2</glowRadius><glowColor>(1,2,3,0)</glowColor>", "\n\t\t\t"),
                           ("no colour red", "<glowColor>(1,2,3,0)</glowColor>", ""),
                           ("blank radius red", "<glowRadius>2</glowRadius>", "<glowRadius> </glowRadius>")):
        mutated = good.replace(old, new, 1)
        if mutated == good:      # an anchor that matches nothing would read as caught
            cases.append((name + " (anchor missing)", False))
            continue
        f, n = glower_findings(mutated, "planted")
        cases.append((name, n == 1 and len(f) == 1 and "X glower" in f[0]))
    # Sanity: the scan must see the glowers we know ship (lantern, pale tree, spore kit); a blind glob reads 0.
    cases.append(("sanity: >=9 glowers in >=20 files (%d in %d)" % (total, files), total >= 9 and files >= 20))
    for n, ok in cases:
        print("%s  %s" % ("ok  " if ok else "FAIL", n))
    for f in findings:
        print("  - " + f)
    bad = [n for n, ok in cases if not ok]
    print("selftest_rot_glowers: %s (%d/%d)" % ("FAIL" if bad else "PASS", len(cases) - len(bad), len(cases)))
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main())
