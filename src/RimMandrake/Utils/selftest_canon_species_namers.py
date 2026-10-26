#!/usr/bin/env python3
"""Every StarWarsRaces xenotype names its pawns with a namer that exists and whose word
lists exist and are non-empty (XENOTYPE_CANON_CORRECTION_1, 2026-10-26). A nameMaker
pointing at a missing RulePackDef, or a Rule_File path with no .txt, resolves silently
to a blank or default name in game. The only xenotype allowed no namer is Taung, whose
Wookieepedia category holds epithets, not names."""
import os, sys
import xml.etree.ElementTree as ET

HERE = os.path.dirname(os.path.abspath(__file__))
MOD = os.path.join(HERE, "..", "..", "RimStarWars", "StarWarsRaces")
UNNAMED_OK = {"RSW_RimMandrakeTaung"}


def main():
    packs, bad = {}, []
    rp = os.path.join(MOD, "Defs", "RulePackDefs")
    for f in sorted(os.listdir(rp)):
        if f.endswith(".xml"):
            for d in ET.parse(os.path.join(rp, f)).getroot().findall("RulePackDef"):
                packs[d.findtext("defName")] = d
    for name, d in packs.items():
        for p in d.iter("path"):
            t = os.path.join(MOD, "Languages", "English", "Strings", p.text + ".txt")
            if not os.path.exists(t):
                bad.append("%s: word list missing %s" % (name, p.text))
            elif not [l for l in open(t, encoding="utf-8-sig") if l.strip()]:
                bad.append("%s: word list empty %s" % (name, p.text))
        for i in d.findall("include/li"):
            if i.text not in packs:
                bad.append("%s: include %s does not resolve" % (name, i.text))
    xs = ET.parse(os.path.join(MOD, "Defs", "XenotypeDefs", "RimMandrakeXenotypes.xml")).getroot()
    n = 0
    for x in xs.findall("XenotypeDef"):
        dn, nm = x.findtext("defName"), x.findtext("nameMaker")
        n += 1
        if not nm and dn not in UNNAMED_OK:
            bad.append("%s: no nameMaker" % dn)
        elif nm and nm not in packs:
            bad.append("%s: nameMaker %s does not resolve" % (dn, nm))
    assert n >= 60 and len(packs) >= 60, "sanity probe: %d xenotypes, %d packs" % (n, len(packs))
    if bad:
        print("FAIL\n  " + "\n  ".join(bad))
        return 1
    print("PASS %d xenotypes named by %d resolvable namers" % (n - len(UNNAMED_OK), len(packs)))
    return 0


if __name__ == "__main__":
    sys.exit(main())
