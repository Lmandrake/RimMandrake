#!/usr/bin/env python3
"""Every StarWarsRaces xenotype names its pawns with a namer that exists and whose word
lists exist and are non-empty (XENOTYPE_CANON_CORRECTION_1, 2026-10-26). A nameMaker
pointing at a missing RulePackDef, or a Rule_File path with no .txt, resolves silently
to a blank or default name in game. No xenotype is exempt: Taung, whose Wookieepedia
category holds epithets, not names, takes an INVENTED namer
(TAUNG_NAMES_DESIGN_WITHOUT_CANON_POOL). Invented word lists live under Invented/, never
Canon/, and share no word with any canon pool, so an invented name is never passed off as
canon."""
import os, sys
import xml.etree.ElementTree as ET

HERE = os.path.dirname(os.path.abspath(__file__))
MOD = os.path.join(HERE, "..", "..", "RimStarWars", "StarWarsRaces")
INVENTED = {"RSW_RimMandrakeTaung": "RSW_NamerTaungInvented"}
STRINGS = os.path.join(MOD, "Languages", "English", "Strings")


def words(path):
    t = os.path.join(STRINGS, path + ".txt")
    return {l.strip() for l in open(t, encoding="utf-8-sig") if l.strip()} if os.path.exists(t) else set()


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
        if not nm:
            bad.append("%s: no nameMaker" % dn)
        elif nm and nm not in packs:
            bad.append("%s: nameMaker %s does not resolve" % (dn, nm))
    canon = set()
    for dp, _, fs in os.walk(os.path.join(STRINGS, "RimMandrakeSWNames", "Canon")):
        for f in fs:
            canon |= words(os.path.relpath(os.path.join(dp, f), STRINGS)[:-4])
    for x in xs.findall("XenotypeDef"):
        dn = x.findtext("defName")
        if dn in INVENTED:
            if x.findtext("nameMaker") != INVENTED[dn]:
                bad.append("%s: nameMaker is not %s" % (dn, INVENTED[dn]))
            d = packs.get(INVENTED[dn])
            for p in (d.iter("path") if d is not None else ()):
                if not p.text.startswith("RimMandrakeSWNames/Invented/"):
                    bad.append("%s: invented list outside Invented/: %s" % (INVENTED[dn], p.text))
                w = words(p.text)
                if len(w) < 30:
                    bad.append("%s: %s holds %d words, want >= 30" % (INVENTED[dn], p.text, len(w)))
                if w & canon:
                    bad.append("%s: %s shares canon words %s" % (INVENTED[dn], p.text, sorted(w & canon)))
    assert len(canon) >= 200, "sanity probe: only %d canon words seen" % len(canon)
    assert n >= 60 and len(packs) >= 60, "sanity probe: %d xenotypes, %d packs" % (n, len(packs))
    if bad:
        print("FAIL\n  " + "\n  ".join(bad))
        return 1
    print("PASS %d xenotypes named by %d resolvable namers" % (n, len(packs)))
    return 0


if __name__ == "__main__":
    sys.exit(main())
