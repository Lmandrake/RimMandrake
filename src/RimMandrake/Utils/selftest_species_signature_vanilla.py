#!/usr/bin/env python3
# selftest-tier: deployed
"""Every vanilla name the species-signature genes lean on resolves against the installed
game's Data (XENOTYPE_CANON_CORRECTION_1, 2026-10-29): the stats and capacity the genes
modify, vanilla VacuumResistance_Partial given to Kel Dor, and no two genes on Kaminoan,
Kel Dor or Defel share an exclusionTag (the game silently drops one of an excluded
pair). A misspelt stat in <statOffsets> fails the def load; a misspelt gene in a
xenotype list is skipped with one red line. Offline counterpart:
selftest_species_signature_genes.py. ConditionalStatAffecter_InSunlight is a class, not
a def; it is checked in the decompiled source when that is present."""
import os, sys
import xml.etree.ElementTree as ET

HERE = os.path.dirname(os.path.abspath(__file__))
MOD = os.path.join(HERE, "..", "..", "RimStarWars", "StarWarsRaces")
UNMEASURED = "UNMEASURED, not a pass or a fail"
DECOMP = "/mnt/d/ClaudeWork/rimmandrake/decomp/rw16/all"
XENOS = ("RSW_RimMandrakeKaminoan", "RSW_RimMandrakeKelDor", "RSW_RimMandrakeDefel")
sys.path.insert(0, HERE)


def walk(root):
    for dp, _, fs in os.walk(root):
        for f in fs:
            if f.endswith(".xml"):
                try:
                    yield ET.parse(os.path.join(dp, f)).getroot()
                except ET.ParseError:
                    pass


def main():
    from game_paths import GAME_DATA
    if not os.path.isdir(os.path.join(GAME_DATA, "Core", "Defs")):
        print("%s: no vanilla Data at %s" % (UNMEASURED, GAME_DATA))
        return 0
    defs = {"StatDef": set(), "PawnCapacityDef": set(), "GeneDef": set()}
    named, genes = {}, {}
    roots = [os.path.join(GAME_DATA, d, "Defs") for d in sorted(os.listdir(GAME_DATA))
             if os.path.isdir(os.path.join(GAME_DATA, d, "Defs"))] + [os.path.join(MOD, "Defs")]
    for r in roots:
        for root in walk(r):
            for d in root:
                if d.tag in defs and d.findtext("defName"):
                    defs[d.tag].add(d.findtext("defName"))
                if d.tag == "GeneDef":
                    if d.get("Name"):
                        named[d.get("Name")] = d
                    if d.findtext("defName"):
                        genes[d.findtext("defName")] = d
    assert len(defs["StatDef"]) > 200 and "Sight" in defs["PawnCapacityDef"] and len(genes) > 150, \
        "sanity probe: %s" % {k: len(v) for k, v in defs.items()}

    def tags(d, seen=0):
        t = {li.text for li in d.findall("exclusionTags/li")}
        p = d.get("ParentName")
        if p in named and seen < 10:
            t |= tags(named[p], seen + 1)
        return t

    bad = []
    sig = ET.parse(os.path.join(MOD, "Defs", "GeneDefs", "RSW_SpeciesSignature.xml")).getroot()
    for g in sig.findall("GeneDef"):
        for so in g.iter("statOffsets"):
            for s in so:
                if s.tag not in defs["StatDef"]:
                    bad.append("%s: stat %s not a StatDef" % (g.findtext("defName"), s.tag))
        for c in g.findall("capMods/li/capacity"):
            if c.text not in defs["PawnCapacityDef"]:
                bad.append("%s: capacity %s not a PawnCapacityDef" % (g.findtext("defName"), c.text))
    xs = {x.findtext("defName"): x for x in
          ET.parse(os.path.join(MOD, "Defs", "XenotypeDefs", "RimMandrakeXenotypes.xml")).getroot().findall("XenotypeDef")}
    # Genes from other mods (Outland_, BS_, VRE aptitudes) are not in Data; their tags come from
    # the newest def dump when one exists. Only clashes that involve a signature gene are ours.
    dumped = {}
    try:
        import json
        from game_paths import DEF_DUMP
        for d in json.load(open(os.path.join(DEF_DUMP, "defs", "GeneDef.json"), encoding="utf-8"))["defs"]:
            dumped[d["defName"]] = set((d.get("fields") or {}).get("exclusionTags") or ())
    except Exception:                                   # noqa: BLE001 - dump optional
        pass
    ours = {g.findtext("defName") for g in sig.findall("GeneDef")} | {"VacuumResistance_Partial"}
    blind = set()
    for dn in XENOS:
        have = [li.text for li in xs[dn].findall("genes/li")]
        tagmap = {}
        for gname in have:
            if gname in genes:
                tagmap[gname] = tags(genes[gname])
            elif gname in dumped:
                tagmap[gname] = dumped[gname]
            elif gname in ours:
                bad.append("%s: signature gene %s resolves nowhere" % (dn, gname))
            else:
                blind.add(gname)
        for a in [x for x in have if x in ours and x in tagmap]:
            for b in have:
                if b != a and b in tagmap and tagmap[a] & tagmap[b]:
                    bad.append("%s: %s and %s share exclusionTag %s" % (dn, a, b, sorted(tagmap[a] & tagmap[b])))
    if blind:
        print("note: tags unseen (not in Data or def dump): %s" % ", ".join(sorted(blind)))
    cls = "unchecked (no decomp)"
    if os.path.isdir(DECOMP):
        hit = any(f.startswith("ConditionalStatAffecter_InSunlight") for _, _, fs in os.walk(DECOMP) for f in fs)
        cls = "found" if hit else "MISSING"
        if not hit:
            bad.append("ConditionalStatAffecter_InSunlight not in decompiled source")
    if bad:
        print("FAIL\n  " + "\n  ".join(bad))
        return 1
    print("PASS signature genes resolve against vanilla Data (%d stats, %d genes); no exclusionTag clash on %d "
          "xenotypes; InSunlight class %s" % (len(defs["StatDef"]), len(genes), len(XENOS), cls))
    return 0


if __name__ == "__main__":
    sys.exit(main())
