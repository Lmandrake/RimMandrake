#!/usr/bin/env python3
"""selftest_taozin_split.py -- offline proof of the taozin split (TAOZIN_SPLIT_BUILD_ONE_WORM_BECOMES_TWO).

Owner 2026-10-17: one worm becomes two -- a huge wild-only adult RSW_Taozin on the Crags (RM_Abyss), and a small
RSW_TaozinGrub found only in a guarded nest, whose brine (Cuisine) gives mood and break resistance.

Run bare: python3 src/RimStarWars/SWBestiary/selftest_taozin_split.py   (exit 0 = clean)

Reads the shipped XML as elements (never by counting <li>). A self-check at the end feeds a broken adult (tameable,
egg-laying) through the same predicates and requires them to go red, so a predicate that can never fail is caught.
"""
import glob
import os
import sys
import xml.etree.ElementTree as ET

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
SWB = HERE
CUISINE = os.path.join(ROOT, "src", "RimStarWars", "Cuisine")
ABYSS = os.path.join(ROOT, "src", "RimMandrake", "Abyss")
WILD_ABYSS = os.path.join(ROOT, "src", "RimUtinni", "UtinniPatches", "Patches", "WildAnimals_Abyss.xml")

FAILS = []


def check(name, cond, detail=""):
    print("%s  %s %s" % ("ok  " if cond else "FAIL", name, "" if cond else detail))
    if not cond:
        FAILS.append(name)


def defs_in(folder):
    """{(tag, defName): element} over every Defs/**/*.xml under folder."""
    out = {}
    for p in glob.glob(os.path.join(folder, "Defs", "**", "*.xml"), recursive=True):
        for el in ET.parse(p).getroot():
            dn = el.findtext("defName")
            if dn:
                out[(el.tag, dn)] = el
    return out


def stat(el, name):
    v = el.findtext("statBases/" + name)
    return float(v) if v is not None else None


def adult_problems(race, kind, all_defs):
    """Everything that makes RSW_Taozin NOT the wild-only adult the owner asked for."""
    bad = []
    w = stat(race, "Wildness")
    if w is None or w < 1.0:
        bad.append("Wildness %r < 1 (vanilla TameUtility refuses only Wildness >= 1)" % w)
    ages = race.find("race/lifeStageAges")
    if ages is not None and len(list(ages)) != 1:
        bad.append("%d life stages, want adult only" % len(list(ages)))
    if kind.find("lifeStages") is None or len(list(kind.find("lifeStages"))) != 1:
        bad.append("PawnKind lifeStages is not exactly one (adult)")
    for c in race.findall("comps/li"):
        if "EggLayer" in (c.get("Class") or ""):
            bad.append("has an egg layer comp")
    for (tag, dn), el in all_defs.items():
        for h in el.iter("hatcherPawn"):
            if (h.text or "").strip() == "RSW_Taozin":
                bad.append("%s %s hatches RSW_Taozin" % (tag, dn))
    if race.find("race/wildBiomes") is not None:
        bad.append("own wildBiomes (its only home is the RM_Abyss patch row)")
    return bad


def texpaths(kind):
    return [t.text.strip() for t in kind.iter("texPath") if t.text]


def tex_ok(tp):
    base = os.path.join(SWB, "Textures", *tp.split("/"))
    return all(os.path.isfile(base + "_" + f + ".png") for f in ("north", "east", "south"))


def main():
    swb = defs_in(SWB)
    cui = defs_in(CUISINE)
    alldefs = dict(swb)
    alldefs.update(cui)

    race = swb.get(("ThingDef", "RSW_Taozin"))
    kind = swb.get(("PawnKindDef", "RSW_Taozin"))
    grace = swb.get(("ThingDef", "RSW_TaozinGrub"))
    gkind = swb.get(("PawnKindDef", "RSW_TaozinGrub"))
    for n, v in (("adult race", race), ("adult kind", kind), ("grub race", grace), ("grub kind", gkind)):
        check("def present: " + n, v is not None)
    if FAILS:
        return 1

    # Adult: huge, wild only, adult only, no eggs.
    probs = adult_problems(race, kind, alldefs)
    check("adult is wild-only, adult-only, egg-free", not probs, "; ".join(probs))
    bs = float(race.findtext("race/baseBodySize") or 0)
    check("adult is huge (bodySize >= 6)", bs >= 6, "bodySize %s" % bs)
    ds = [float(d.text) for d in kind.iter("drawSize")]
    check("adult drawn >= 10 cells (ten times a man)", ds and min(ds) >= 10, "drawSize %s" % ds)
    egg_defs = [dn for (tag, dn) in alldefs if tag == "ThingDef" and "EggTaozin" in dn]
    check("no orphan taozin egg defs", not egg_defs, str(egg_defs))

    # Grub: small, tameable, never wild.
    gbs = float(grace.findtext("race/baseBodySize") or 0)
    check("grub is small (bodySize <= 0.2)", 0 < gbs <= 0.2, "bodySize %s" % gbs)
    gw = stat(grace, "Wildness")
    check("grub is tameable (Wildness < 1)", gw is not None and gw < 1, "Wildness %r" % gw)
    check("grub has no wildBiomes", grace.find("race/wildBiomes") is None)
    with open(WILD_ABYSS, encoding="utf-8") as f:
        wild_xml = f.read()
    check("grub is on no wild roster row", "RSW_TaozinGrub" not in wild_xml)

    # Abyss row for the adult (parsed as elements).
    rows = [el for el in ET.parse(WILD_ABYSS).getroot().iter("RSW_Taozin")]
    check("adult on the RM_Abyss wild row", rows and float(rows[0].text) > 0, "rows %d" % len(rows))

    # Nest: adult anchored + grubs + silk, patched onto RM_Abyss.extraGenSteps, biome has that node.
    nest = swb.get(("GenStepDef", "RSW_GenStep_TaozinNest"))
    check("nest GenStepDef present", nest is not None)
    if nest is not None:
        anchored = [e for e in nest.iter("li") if "AnchoredPawn" in (e.get("Class") or "")
                    and e.findtext("pawnKind") == "RSW_Taozin"]
        grubs = [e for e in nest.iter("li") if e.findtext("kind") == "RSW_TaozinGrub"]
        silk = [e for e in nest.iter("li") if e.findtext("thing") == "RSW_WoolTaozin"]
        check("nest anchors a guarding adult", bool(anchored))
        check("nest holds grubs", bool(grubs))
        check("nest holds silk", bool(silk))
    patch = ET.parse(os.path.join(SWB, "Patches", "RSW_TaozinNest_Abyss.xml")).getroot()
    adds = [op for op in patch.iter() if op.get("Class") == "PatchOperationAdd"
            and (op.findtext("xpath") or "").strip() == 'Defs/BiomeDef[defName="RM_Abyss"]/extraGenSteps'
            and any((li.text or "").strip() == "RSW_GenStep_TaozinNest" for li in op.iter("li"))]
    check("nest patched onto RM_Abyss.extraGenSteps", bool(adds))
    ab = defs_in(ABYSS).get(("BiomeDef", "RM_Abyss"))
    check("RM_Abyss has an extraGenSteps node for the patch to match",
          ab is not None and ab.find("extraGenSteps") is not None)

    # Brine: mood thought + break-resistance hediff.
    brine = cui.get(("ThingDef", "RSW_TaozinBrine"))
    check("RSW_TaozinBrine present", brine is not None)
    if brine is not None:
        tt = brine.findtext(".//tasteThought")
        check("brine gives a mood thought", tt in [dn for (t, dn) in cui if t == "ThoughtDef"], str(tt))
        hd = [h.text for h in brine.iter("hediffDef")]
        hed = [cui.get(("HediffDef", h)) for h in hd]
        mb = [h for h in hed if h is not None and h.find(".//MentalBreakThreshold") is not None
              and float(h.findtext(".//MentalBreakThreshold")) < 0]
        check("brine gives a break-resistance hediff", bool(mb), str(hd))

    # Art: every texPath of both creatures resolves to N/E/S PNGs.
    for k in (kind, gkind):
        for tp in texpaths(k):
            check("art present: " + tp, tex_ok(tp))

    # Sanity: the adult predicate must go red on a broken adult.
    broken = ET.fromstring(ET.tostring(race))
    broken.find("statBases/Wildness").text = "0.5"
    comps = broken.find("comps")
    if comps is None:
        comps = ET.SubElement(broken, "comps")
    ET.SubElement(comps, "li", {"Class": "CompProperties_EggLayer"})
    check("self-check: a tameable egg-laying adult is caught", len(adult_problems(broken, kind, alldefs)) >= 2)

    print("FAILS: %d" % len(FAILS))
    return 1 if FAILS else 0


if __name__ == "__main__":
    sys.exit(main())
