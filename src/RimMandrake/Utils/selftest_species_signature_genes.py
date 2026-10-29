#!/usr/bin/env python3
"""Species-signature genes (XENOTYPE_CANON_CORRECTION_1 Pattern 4, 2026-10-29) are real,
wired and do what their description claims - offline, repo only.

  RSW_UltravioletVision  (Kaminoan)  Sight capMod offset > 0, no dark vision
  RSW_AntioxRespiration  (Kel Dor)   tox gas immunity + ToxicEnvironmentResistance > 0
  RSW_LightAbsorbingFur  (Defel)     stealth/dodge offsets that ConditionalStatAffecter_InSunlight
                                     cancels EXACTLY (a typo leaves daylight bonus or penalty)

Wiring: each xenotype carries its genes in the shipped XML AND in the generator's
OWNER_GENE_ADDITIONS (so a regen keeps them), and apply_owner_tables over the shipped
xenotypes changes nothing (table and shipped file agree). That the stat, capacity, class
and vanilla gene names resolve is the deployed-tier selftest_species_signature_vanilla.py."""
import copy, os, sys
import xml.etree.ElementTree as ET

HERE = os.path.dirname(os.path.abspath(__file__))
MOD = os.path.join(HERE, "..", "..", "RimStarWars", "StarWarsRaces")
GENES = os.path.join(MOD, "Defs", "GeneDefs", "RSW_SpeciesSignature.xml")
XENOS = os.path.join(MOD, "Defs", "XenotypeDefs", "RimMandrakeXenotypes.xml")
WANT = {"RSW_RimMandrakeKaminoan": {"RSW_UltravioletVision"},
        "RSW_RimMandrakeKelDor": {"RSW_AntioxRespiration", "VacuumResistance_Partial"},
        "RSW_RimMandrakeDefel": {"RSW_LightAbsorbingFur"}}
sys.path.insert(0, HERE)


def offsets(node):
    return {} if node is None else {c.tag: float(c.text) for c in node}


def main():
    import gen_races_mod as g
    bad = []
    genes = {d.findtext("defName"): d for d in ET.parse(GENES).getroot().findall("GeneDef")}
    allg = {}
    gd = os.path.join(MOD, "Defs", "GeneDefs")
    for f in sorted(os.listdir(gd)):
        if f.endswith(".xml"):
            for d in ET.parse(os.path.join(gd, f)).getroot().iter("GeneDef"):
                n = d.findtext("defName")
                if n:
                    allg.setdefault(n, []).append(f)
    assert len(genes) == 3 and len(allg) >= 10, "sanity probe: %d signature, %d mod genes" % (len(genes), len(allg))
    for n in genes:
        if len(allg.get(n, [])) != 1:
            bad.append("%s defined in %s" % (n, allg.get(n)))
        for f in ("label", "description", "iconPath", "biostatCpx", "biostatMet"):
            if not genes[n].findtext(f):
                bad.append("%s: no %s" % (n, f))

    uv = genes["RSW_UltravioletVision"]
    sight = [float(li.findtext("offset") or 0) for li in uv.findall("capMods/li") if li.findtext("capacity") == "Sight"]
    if not sight or sight[0] <= 0:
        bad.append("UltravioletVision: no positive Sight capMod")
    if uv.findtext("ignoreDarkness") == "true":
        bad.append("UltravioletVision: claims dark vision; description says it is not")

    ax = genes["RSW_AntioxRespiration"]
    if ax.findtext("immuneToToxGasExposure") != "true":
        bad.append("AntioxRespiration: not immune to tox gas")
    if offsets(ax.find("statOffsets")).get("ToxicEnvironmentResistance", 0) <= 0:
        bad.append("AntioxRespiration: no ToxicEnvironmentResistance")
    if "ToxicEnvironmentResistance" not in [li.text for li in ax.findall("exclusionTags/li")]:
        bad.append("AntioxRespiration: missing exclusionTag ToxicEnvironmentResistance (stacks with vanilla tox genes)")

    lf = genes["RSW_LightAbsorbingFur"]
    base = offsets(lf.find("statOffsets"))
    sun = [li for li in lf.findall("conditionalStatAffecters/li") if li.get("Class") == "ConditionalStatAffecter_InSunlight"]
    if not base or any(v <= 0 for v in base.values()):
        bad.append("LightAbsorbingFur: base offsets missing or not bonuses: %s" % base)
    if len(sun) != 1:
        bad.append("LightAbsorbingFur: want exactly one InSunlight affecter, got %d" % len(sun))
    else:
        so = offsets(sun[0].find("statOffsets"))
        if set(so) != set(base) or any(abs(so[k] + base[k]) > 1e-9 for k in base):
            bad.append("LightAbsorbingFur: sunlight %s does not cancel base %s" % (so, base))

    shipped = {x.findtext("defName"): x for x in ET.parse(XENOS).getroot().findall("XenotypeDef")}
    for dn, want in WANT.items():
        x = shipped.get(dn)
        if x is None:
            bad.append("%s: xenotype missing" % dn)
            continue
        have = [li.text for li in x.findall("genes/li")]
        for gname in sorted(want):
            if have.count(gname) != 1:
                bad.append("%s: carries %s x%d in shipped XML" % (dn, gname, have.count(gname)))
            if gname not in g.OWNER_GENE_ADDITIONS.get(dn, ()):
                bad.append("%s: %s not in OWNER_GENE_ADDITIONS (a regen drops it)" % (dn, gname))
        x2 = copy.deepcopy(x)
        g.apply_owner_tables([x2])
        if [li.text for li in x2.findall("genes/li")] != have:
            bad.append("%s: apply_owner_tables changes the shipped gene list" % dn)
    for dn, x in shipped.items():
        if dn not in WANT and set(li.text for li in x.findall("genes/li")) & set(genes):
            bad.append("%s: carries a signature gene it was not assigned" % dn)

    if bad:
        print("FAIL\n  " + "\n  ".join(bad))
        return 1
    print("PASS 3 signature genes well-formed, wired on %d xenotypes (shipped + generator table)" % len(WANT))
    return 0


if __name__ == "__main__":
    sys.exit(main())
