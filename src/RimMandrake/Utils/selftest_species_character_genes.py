#!/usr/bin/env python3
"""Species-character genes (SPECIES_TRAITS_OVER_APTITUDES_1) replace the aptitudes that stood in
for them, are wired to real C# conditions, and their arithmetic does what the text says. Offline.

  RSW_HiveMinded  Geonosian  NearKin (+) / NoKinOnMap (-)   replaces AptitudeTerrible_Social
  RSW_WrenduiFur  Bothan     MoodBand high (+) / low (-)     replaces AptitudeStrong_Social
  RSW_TunnelBorn  Abednedo   UnderThickRoof (+)              replaces AptitudeStrong_Construction

Owner 2026-09-20: the species gene REPLACES its surrogate aptitude, never both; Gungan keeps
AptitudePoor_Intellectual ("half joke and half rebuke"). Checks: each condition Class is a class
in Source/RSW_SpeciesConditions.cs; each `setting` is a case of SpeciesMechanicOn, a saved field
and a control on the settings screen; customEffectDescriptions state the XML numbers; the stats
resolve in the game's Core defs (when the install is reachable); a Python port of each condition,
swept over its whole input space, never applies both halves of a gene at once; the shipped
xenotypes and the generator tables agree; the committed DLL's .srchash covers the current source."""
import copy, hashlib, os, re, sys
import xml.etree.ElementTree as ET

HERE = os.path.dirname(os.path.abspath(__file__))
MOD = os.path.join(HERE, "..", "..", "RimStarWars", "StarWarsRaces")
GENES = os.path.join(MOD, "Defs", "GeneDefs", "RSW_SpeciesCharacter.xml")
XENOS = os.path.join(MOD, "Defs", "XenotypeDefs", "RimMandrakeXenotypes.xml")
SRC = os.path.join(MOD, "Source")
COND_CS = os.path.join(SRC, "RSW_SpeciesConditions.cs")
MOD_CS = os.path.join(SRC, "RSW_StarWarsRacesMod.cs")
SRCHASH = os.path.join(MOD, "Assemblies", "RimMandrakeStarWarsRaces.dll.srchash")
CORE_STATS = "/mnt/c/Program Files (x86)/Steam/steamapps/common/RimWorld/Data/Core/Defs/Stats"
NS = "RimMandrake.StarWars.Races."
# xenotype -> (species gene, the surrogate aptitude it replaced, expected metabolism)
SWAP = {"RSW_RimMandrakeGeonosianVariants": ("RSW_HiveMinded", "AptitudeTerrible_Social", 1),
        "RSW_RimMandrakeBothan": ("RSW_WrenduiFur", "AptitudeStrong_Social", -1),
        "RSW_RimMandrakeAbednedo": ("RSW_TunnelBorn", "AptitudeStrong_Construction", -1)}
KEEP = {"RSW_RimMandrakeGungan": "AptitudePoor_Intellectual"}
# the conditions each gene must carry, as (Class, sign of every offset)
SHAPE = {"RSW_HiveMinded": [("ConditionalStatAffecter_NearKin", 1), ("ConditionalStatAffecter_NoKinOnMap", -1)],
         "RSW_WrenduiFur": [("ConditionalStatAffecter_MoodBand", 1), ("ConditionalStatAffecter_MoodBand", -1)],
         "RSW_TunnelBorn": [("ConditionalStatAffecter_UnderThickRoof", 1)]}
sys.path.insert(0, HERE)


def offsets(node):
    return {} if node is None else {c.tag: float(c.text) for c in node}


def fnum(li, tag, default):
    t = li.findtext(tag)
    return float(t) if t is not None else default


# --- Python ports of the C# Applies(), same comparisons ------------------------------------------
def mood_band(m, lo, hi):            # ConditionalStatAffecter_MoodBand: m >= minMood && m < maxMood
    return lo <= m < hi


def near_kin(near, min_kin):         # ConditionalStatAffecter_NearKin: near >= minKin
    return near >= min_kin


def no_kin(on_map):                  # ConditionalStatAffecter_NoKinOnMap: onMap == 0
    return on_map == 0


# how customEffectDescriptions name each stat (checked signed, per stat)
STAT_TEXT = {"WorkSpeedGlobal": "global work speed", "ResearchSpeed": "research speed",
             "NegotiationAbility": "negotiation ability", "TradePriceImprovement": "trade price improvement",
             "SocialImpact": "social impact", "MiningSpeed": "mining speed", "ConstructionSpeed": "construction speed"}


def pct(x):
    return "%g%%" % round(x * 100, 6)


def trigger_phrases(cls, li):
    """The words the effect text must contain for the XML's own trigger values."""
    if cls == "ConditionalStatAffecter_NearKin":
        return ["%d or more other" % int(fnum(li, "minKin", 2)), "within %g cells" % fnum(li, "radius", 15)]
    if cls == "ConditionalStatAffecter_NoKinOnMap":
        return ["no other", "on the map"]
    if cls == "ConditionalStatAffecter_MoodBand":
        lo, hi = fnum(li, "minMood", 0.0), fnum(li, "maxMood", 1.01)
        return (["Mood %s or more" % pct(lo)] if lo > 0 else []) + (["below %s" % pct(hi)] if hi <= 1 else [])
    if cls == "ConditionalStatAffecter_UnderThickRoof":
        return ["overhead-mountain roof"]
    return ["<unknown condition class>"]


def main():
    import gen_races_mod as g
    bad = []
    root = ET.parse(GENES).getroot()
    genes = {d.findtext("defName"): d for d in root.findall("GeneDef")}
    cond_src = open(COND_CS, encoding="utf-8").read()
    mod_src = open(MOD_CS, encoding="utf-8").read()
    classes = set(re.findall(r"public class (\w+) : RSW_SpeciesCondition\b", cond_src))
    cases = set(re.findall(r'case "(\w+)": return (\w+);', mod_src))
    assert len(genes) == 3 and len(classes) == 4 and len(cases) == 3, \
        "sanity probe: %d genes, %d condition classes, %d setting cases" % (len(genes), len(classes), len(cases))
    if "RSW_SpeciesConditions.cs" not in open(os.path.join(SRC, "RSW_StarWarsRaces.csproj")).read():
        bad.append("csproj does not compile RSW_SpeciesConditions.cs")

    allg = {}
    gd = os.path.join(MOD, "Defs", "GeneDefs")
    for f in sorted(os.listdir(gd)):
        if f.endswith(".xml"):
            for d in ET.parse(os.path.join(gd, f)).getroot().iter("GeneDef"):
                if d.findtext("defName"):
                    allg.setdefault(d.findtext("defName"), []).append(f)

    core_stats = None
    if os.path.isdir(CORE_STATS):
        core_stats = set()
        for f in os.listdir(CORE_STATS):
            if f.endswith(".xml"):
                core_stats |= {d.findtext("defName") for d in ET.parse(os.path.join(CORE_STATS, f)).getroot().iter("StatDef")}
        assert "WorkSpeedGlobal" in core_stats and len(core_stats) > 100, "sanity probe: Core stats unreadable"

    for gname, shape in SHAPE.items():
        d = genes.get(gname)
        if d is None:
            bad.append("%s: not defined" % gname)
            continue
        if len(allg.get(gname, [])) != 1:
            bad.append("%s defined in %s" % (gname, allg.get(gname)))
        for f in ("label", "description", "iconPath", "biostatCpx", "biostatMet"):
            if not d.findtext(f):
                bad.append("%s: no %s" % (gname, f))
        lis = d.findall("conditionalStatAffecters/li")
        if len(lis) != len(shape):
            bad.append("%s: %d conditions, want %d" % (gname, len(lis), len(shape)))
            continue
        texts = [li.text for li in d.findall("customEffectDescriptions/li")]
        if len(texts) != len(lis):
            bad.append("%s: %d effect descriptions for %d conditions" % (gname, len(texts), len(lis)))
        for i, (li, (want_cls, sign)) in enumerate(zip(lis, shape)):
            cls = li.get("Class", "")
            if cls != NS + want_cls or want_cls not in classes:
                bad.append("%s[%d]: Class %s, want %s%s defined in the C#" % (gname, i, cls, NS, want_cls))
            if not li.findtext("label"):
                bad.append("%s[%d]: no label (the stat explanation would print the class name)" % (gname, i))
            st = li.findtext("setting")
            if st not in {c for c, _ in cases} or ("public static bool %s = true;" % st) not in mod_src \
                    or ('Scribe_Values.Look(ref %s, "%s", true)' % (st, st)) not in mod_src \
                    or ("ref %s," % st) not in mod_src.split("Scribe_Values")[-1]:
                bad.append("%s[%d]: setting %r is not a saved, shown, default-on SpeciesMechanicOn case" % (gname, i, st))
            if want_cls in ("ConditionalStatAffecter_NearKin", "ConditionalStatAffecter_NoKinOnMap") \
                    and li.findtext("kinGene") != gname:
                bad.append("%s[%d]: kinGene %r is not the gene itself (a missing one never applies)"
                           % (gname, i, li.findtext("kinGene")))
            so = offsets(li.find("statOffsets"))
            if not so or any((v > 0) != (sign > 0) for v in so.values()):
                bad.append("%s[%d]: offsets %s are not all %s" % (gname, i, so, "bonuses" if sign > 0 else "penalties"))
            if core_stats is not None:
                for s in so:
                    if s not in core_stats:
                        bad.append("%s[%d]: stat %s is not a Core StatDef" % (gname, i, s))
            if i < len(texts):
                t = texts[i]
                said = {tag: float(v) for tag, phrase in STAT_TEXT.items()
                        for v in re.findall(re.escape(phrase) + r" ([+-]\d+(?:\.\d+)?)%", t)}
                have = {k: v * 100 for k, v in so.items()}
                if set(said) != set(have) or any(abs(said[k] - have[k]) > 1e-6 for k in have):
                    bad.append("%s[%d]: text says %s, XML gives %s" % (gname, i, said, have))
                for need in trigger_phrases(want_cls, li):
                    if need not in t:
                        bad.append("%s[%d]: text %r does not state the trigger %r" % (gname, i, t, need))

    # --- sweep the ports over the whole input space with the XML's own numbers ---------------------
    if "RSW_WrenduiFur" in genes:
        hi_li, lo_li = genes["RSW_WrenduiFur"].findall("conditionalStatAffecters/li")[:2]
        hi = (fnum(hi_li, "minMood", 0.0), fnum(hi_li, "maxMood", 1.01))
        lo = (fnum(lo_li, "minMood", 0.0), fnum(lo_li, "maxMood", 1.01))
        both = [m / 1000 for m in range(1001) if mood_band(m / 1000, *hi) and mood_band(m / 1000, *lo)]
        if both:
            bad.append("WrenduiFur: mood %s is in both bands" % both[:3])
        if not mood_band(1.0, *hi) or not mood_band(0.0, *lo) or mood_band(0.5, *hi) or mood_band(0.5, *lo):
            bad.append("WrenduiFur: bands %s / %s do not cover full mood high, empty mood low, and leave 50%% neutral" % (hi, lo))
        if "m >= minMood && m < maxMood" not in cond_src:
            bad.append("MoodBand C# comparison is not the one this port sweeps")
    if "RSW_HiveMinded" in genes:
        nk = genes["RSW_HiveMinded"].findall("conditionalStatAffecters/li")[0]
        mk = int(fnum(nk, "minKin", 2))
        for on_map in range(0, 8):
            for near in range(0, on_map + 1):
                if near_kin(near, mk) and no_kin(on_map):
                    bad.append("HiveMinded: near=%d onMap=%d gets bonus and penalty" % (near, on_map))
        if mk < 1:
            bad.append("HiveMinded: minKin %d lets a lone pawn count as among the hive" % mk)
        if "return near >= minKin;" not in cond_src or "return onMap == 0;" not in cond_src:
            bad.append("kin C# comparisons are not the ones this port sweeps")
        if "other == pawn" not in cond_src:
            bad.append("kin census counts the pawn itself")

    # --- wiring: shipped XML, generator tables, metabolism ------------------------------------------
    shipped = {x.findtext("defName"): x for x in ET.parse(XENOS).getroot().findall("XenotypeDef")}
    for dn, (gname, surrogate, met) in SWAP.items():
        x = shipped.get(dn)
        if x is None:
            bad.append("%s: xenotype missing" % dn)
            continue
        have = [li.text for li in x.findall("genes/li")]
        if have.count(gname) != 1:
            bad.append("%s: carries %s x%d" % (dn, gname, have.count(gname)))
        if surrogate in have:
            bad.append("%s: still carries the surrogate %s beside %s (double count)" % (dn, surrogate, gname))
        if gname not in g.OWNER_GENE_ADDITIONS.get(dn, ()):
            bad.append("%s: %s not in OWNER_GENE_ADDITIONS (a regen drops it)" % (dn, gname))
        if surrogate not in g.OWNER_GENE_REMOVALS.get(dn, ()):
            bad.append("%s: %s not in OWNER_GENE_REMOVALS (a regen brings it back)" % (dn, surrogate))
        x2 = copy.deepcopy(x)
        g.apply_owner_tables([x2])
        if [li.text for li in x2.findall("genes/li")] != have:
            bad.append("%s: apply_owner_tables changes the shipped gene list" % dn)
        if gname in genes and int(genes[gname].findtext("biostatMet") or 99) != met:
            bad.append("%s: biostatMet %s, priced at %d" % (gname, genes[gname].findtext("biostatMet"), met))
    for dn, gname in KEEP.items():
        x = shipped.get(dn)
        if x is None or gname not in [li.text for li in x.findall("genes/li")]:
            bad.append("%s lost %s (ruled to STAY)" % (dn, gname))
    for dn, x in shipped.items():
        if dn not in SWAP and set(li.text for li in x.findall("genes/li")) & set(genes):
            bad.append("%s: carries a species-character gene it was not assigned" % dn)

    # --- the committed DLL was built from this source ---------------------------------------------
    stamp = {}
    for line in open(SRCHASH, encoding="utf-8"):
        m = re.match(r"([0-9a-f]{64}) (.+)$", line.strip())
        if m:
            stamp[m.group(2)] = m.group(1)
    dll = SRCHASH[:-len(".srchash")]
    want_dll = re.search(r"^# dll: ([0-9a-f]{64})$", open(SRCHASH, encoding="utf-8").read(), re.M)
    if not os.path.isfile(dll) or not want_dll \
            or hashlib.sha256(open(dll, "rb").read()).hexdigest() != want_dll.group(1):
        bad.append("committed DLL missing or not the one its .srchash stamp records")
    for rel in ("RSW_SpeciesConditions.cs", "RSW_StarWarsRacesMod.cs"):
        h = hashlib.sha256(open(os.path.join(SRC, rel), "rb").read()).hexdigest()
        if stamp.get(rel) != h:
            bad.append("DLL .srchash does not match current %s (rebuild with winbuild.py)" % rel)

    if bad:
        print("FAIL\n  " + "\n  ".join(bad))
        return 1
    print("PASS 3 species-character genes replace their surrogate aptitudes on %d xenotypes; conditions swept%s"
          % (len(SWAP), "" if core_stats is not None else " (Core stats UNMEASURED: no game install)"))
    return 0


if __name__ == "__main__":
    sys.exit(main())
