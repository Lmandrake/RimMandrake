"""validation.py -- modcheck suite for RimMandrake: TerminalBiomes (first script, item CHILL_NATIVE_COLD_TOLERANCE_1).

PROVES (def level, offline): every RM_ Chill native ThingDef is comfortable below the -110 C floor
(ComfyTemperatureMin <= -150, ComfyTemperatureMax still set and above the min).
NOT PROVEN: live hypothermia absence on a dive (UNMEASURED; needs a live dive with the owner's walk).
`python3 validation.py` runs static_checks() without a game.
"""
import os
import sys
import xml.etree.ElementTree as ET

HERE = os.path.dirname(os.path.abspath(__file__))
FLOOR_C = -110.0
NATIVE_MIN_C = -150.0
FILES = ["RM_TheChillFauna.xml", "RM_TheChillFloorLife.xml"]
NATIVES = ["RM_Heemin", "RM_Oovanam", "RM_Hoolen", "RM_Vaunoom", "RM_Fessu", "RM_Krellik", "RM_Oddu",
           "RM_Oovu", "RM_Iliss", "RM_Tarnn", "RM_Zhiil"]


def static_checks():
    bad, seen = [], set()
    for f in FILES:
        root = ET.parse(os.path.join(HERE, "Defs", "ThingDefs_Races", f)).getroot()
        for td in root.findall("ThingDef"):
            n = td.findtext("defName")
            if n not in NATIVES:
                continue
            seen.add(n)
            mn = td.findtext("statBases/ComfyTemperatureMin")
            mx = td.findtext("statBases/ComfyTemperatureMax")
            if mn is None or float(mn) > NATIVE_MIN_C:
                bad.append("%s ComfyTemperatureMin=%s, needs <= %g" % (n, mn, NATIVE_MIN_C))
            if mx is None or (mn is not None and float(mx) <= float(mn)):
                bad.append("%s ComfyTemperatureMax %s not above min" % (n, mx))
    for n in NATIVES:
        if n not in seen:
            bad.append("native ThingDef %s not found" % n)
    return bad


OFF_FLOOR = ["RM_Hoolen", "RM_Vaunoom", "AA_AuroraSylph", "AA_Skyeel"]
BIOME = os.path.join(HERE, "Defs", "BiomeDefs", "RM_TheChill.xml")


def roster_checks():
    """wildAnimals parsed as XML (node name = animal, text = commonality; no <li>)."""
    bad = []
    root = ET.parse(BIOME).getroot()
    bd = [b for b in root.findall("BiomeDef") if b.findtext("defName") == "RM_TheChill"]
    if len(bd) != 1:
        return ["RM_TheChill BiomeDef not found exactly once"]
    wa = bd[0].find("wildAnimals")
    rows = {c.tag: c.text for c in wa} if wa is not None else {}
    if len(rows) < 6:
        bad.append("roster sanity probe: only %d rows (expected the 6 floor natives)" % len(rows))
    for n in ("RM_Heemin", "RM_Oovanam", "RM_Fessu", "RM_Krellik", "RM_Oddu", "RM_Oovu", "RM_Iliss", "RM_Tarnn", "RM_Zhiil"):
        if n not in rows:
            bad.append("floor native %s missing from wildAnimals" % n)
    for n in OFF_FLOOR:
        if n in rows:
            bad.append("%s must be off the floor roster (Q1a)" % n)
    if any(c.tag == "li" for c in (wa if wa is not None else [])):
        bad.append("<li> row in wildAnimals (discards the entry)")
    return bad


CATCH_FILE = os.path.join(HERE, "Defs", "ThingDefs_Items", "RM_TheChillCatch.xml")
RARE_FILE = os.path.join(HERE, "Defs", "ThingSetMakerDefs", "RM_ChillRareCatch.xml")


def catch_checks():
    """CHILL_FREE_TIER_CATCH_1: fishTypes parsed as XML; every row a free-tier item, every catch alive on the floor."""
    bad = []
    bd = [b for b in ET.parse(BIOME).getroot().findall("BiomeDef") if b.findtext("defName") == "RM_TheChill"]
    if len(bd) != 1:
        return ["RM_TheChill BiomeDef not found exactly once"]
    ft = bd[0].find("fishTypes")
    rows = []
    for grp in (ft if ft is not None else []):
        if grp.tag == "rareCatchesSetMaker":
            if (grp.text or "").strip() != "RM_RareChillCatches":
                bad.append("rareCatchesSetMaker is %r, want RM_RareChillCatches" % grp.text)
            continue
        for c in grp:
            rows.append(c.tag)
            if c.get("MayRequire"):
                bad.append("%s row carries MayRequire %s" % (c.tag, c.get("MayRequire")))
    if len(rows) != 9:
        bad.append("sanity probe: %d fishTypes rows, expected 9" % len(rows))
    items = set()
    for f in (CATCH_FILE,):
        for td in ET.parse(f).getroot().findall("ThingDef"):
            items.add(td.findtext("defName"))
    wa = {c.tag for c in bd[0].find("wildAnimals")}
    for r in rows:
        if r.startswith("RUT_"):
            bad.append("%s is campaign-tier in the free fishTypes" % r)
        if r not in items:
            bad.append("%s not defined in RM_TheChillCatch.xml" % r)
        name = r[3:-5] if r.startswith("RM_") and r.endswith("Catch") else r
        if ("RM_" + name) not in wa:
            bad.append("catch %s has no floor resident RM_%s in wildAnimals" % (r, name))
    rare = ET.parse(RARE_FILE).getroot().findall("ThingSetMakerDef")
    if [r.findtext("defName") for r in rare] != ["RM_RareChillCatches"]:
        bad.append("free-tier rare table defName wrong")
    for li in rare[0].iter("li"):
        if (li.text or "").strip().startswith("RUT_") or li.get("MayRequire"):
            bad.append("rare table option %r is campaign-tier/guarded" % li.text)
    for fn in os.listdir(os.path.join(HERE, "Defs", "ThingSetMakerDefs")):
        if "RUT_RarePropaneCatches</defName>" in open(os.path.join(HERE, "Defs", "ThingSetMakerDefs", fn), encoding="utf-8").read():
            bad.append("%s still defines RUT_RarePropaneCatches (collides with campaign twin)" % fn)
    return bad


def ekkel_lore_checks():
    """SCALD_SIMMERLACE_EKKEL_LORE_1: creature and catch descriptions carry the simmerlace origin lore."""
    bad = []
    seen = set()
    for dp, _, fns in os.walk(os.path.join(HERE, "Defs")):
        for fn in fns:
            if not fn.endswith(".xml"):
                continue
            for d in ET.parse(os.path.join(dp, fn)).getroot():
                n = d.findtext("defName")
                if n in ("RM_Ekkel", "RM_EkkelCatch") and d.tag == "ThingDef":
                    seen.add(n)
                    if "simmerlace" not in (d.findtext("description") or "").lower():
                        bad.append("ThingDef %s description lacks the simmerlace lore" % n)
    for n in ("RM_Ekkel", "RM_EkkelCatch"):
        if n not in seen:
            bad.append("ThingDef %s not found" % n)
    return bad


def saal_name_checks():
    """SCALD_SAAL_ONE_NAME_1: creature and catch are both labelled saal; no label says noohm."""
    bad = []
    for dp, _, fns in os.walk(os.path.join(HERE, "Defs")):
        for fn in fns:
            if not fn.endswith(".xml"):
                continue
            root = ET.parse(os.path.join(dp, fn)).getroot()
            for d in root:
                if d.findtext("defName") in ("RM_Noohm", "RM_Saal") and d.tag in ("ThingDef", "PawnKindDef"):
                    if (d.findtext("label") or "").strip() != "saal":
                        bad.append("%s %s label is %r, want 'saal'" % (d.tag, d.findtext("defName"), d.findtext("label")))
                if "noohm" in (d.findtext("label") or "").lower():
                    bad.append("%s label says noohm" % fn)
    return bad


def wax_checks():
    """CHILL_WAX_PROCESSION_GIANT_1 (def/source level): race, kind, sheet, roster row, comp class, csproj, toggle."""
    bad = []
    races = os.path.join(HERE, "Defs", "ThingDefs_Races", "RM_ChillWaxProcession.xml")
    root = ET.parse(races).getroot()
    td = {d.findtext("defName"): d for d in root.findall("ThingDef")}
    for n in ("RM_Hesuun", "RM_DeadFilterSheet"):
        if n not in td:
            bad.append("ThingDef %s missing" % n)
    if not [k for k in root.findall("PawnKindDef") if k.findtext("race") == "RM_Hesuun"]:
        bad.append("PawnKindDef for RM_Hesuun missing")
    h = td.get("RM_Hesuun")
    if h is not None:
        mn = h.findtext("statBases/ComfyTemperatureMin")
        if mn is None or float(mn) > NATIVE_MIN_C:
            bad.append("RM_Hesuun ComfyTemperatureMin %s needs <= %g" % (mn, NATIVE_MIN_C))
        if h.findtext("race/trainability") != "None":
            bad.append("RM_Hesuun must be untameable")
        if h.find("comps/li[@Class='RimMandrake.TerminalBiomes.RM_CompProperties_WaxProcession']") is None:
            bad.append("RM_Hesuun lacks the procession comp")
    meat = h.findtext("race/meatDef") if h is not None else None
    items = os.path.join(HERE, "Defs", "ThingDefs_Items", "RM_TheChillFloraProducts.xml")
    if meat and meat not in [d.findtext("defName") for d in ET.parse(items).getroot().findall("ThingDef")]:
        bad.append("meatDef %s not defined" % meat)
    bd = [b for b in ET.parse(BIOME).getroot().findall("BiomeDef") if b.findtext("defName") == "RM_TheChill"][0]
    if "RM_Hesuun" not in {c.tag for c in bd.find("wildAnimals")}:
        bad.append("RM_Hesuun missing from RM_TheChill wildAnimals")
    if "RM_Hesuun" + "Catch" in {c.tag for g in (list(bd.find("fishTypes")) if bd.find("fishTypes") is not None else []) for c in g}:
        bad.append("RM_Hesuun must not be fishable")
    src = os.path.join(HERE, "Source")
    if "RM_Comp_WaxProcession.cs" not in open(os.path.join(src, "RM_TerminalBiomes.csproj"), encoding="utf-8").read():
        bad.append("RM_Comp_WaxProcession.cs missing from csproj Compile list")
    if "ChillWaxProcessionActive" not in open(os.path.join(src, "RM_TerminalBiomesMod.cs"), encoding="utf-8").read():
        bad.append("Mod Settings toggle ChillWaxProcessionActive missing")
    if not os.path.exists(os.path.join(HERE, "Textures", "Things", "Pawn", "Animal", "RM_Hesuun", "RM_Hesuun.png")):
        bad.append("RM_Hesuun texture missing")
    return bad


try:
    from modcheck import Suite
    suite = Suite("TerminalBiomes")

    @suite.chain("natives_tolerate_floor")
    def natives_tolerate_floor(t):
        bad = static_checks()
        if bad:
            from modcheck import ExpectationFailed
            raise ExpectationFailed("; ".join(bad))

    @suite.chain("floor_roster_trimmed")
    def floor_roster_trimmed(t):
        bad = roster_checks()
        if bad:
            from modcheck import ExpectationFailed
            raise ExpectationFailed("; ".join(bad))

    @suite.chain("saal_one_name")
    def saal_one_name(t):
        bad = saal_name_checks()
        if bad:
            from modcheck import ExpectationFailed
            raise ExpectationFailed("; ".join(bad))

    @suite.chain("catch_free_tier")
    def catch_free_tier(t):
        bad = catch_checks()
        if bad:
            from modcheck import ExpectationFailed
            raise ExpectationFailed("; ".join(bad))

    @suite.chain("wax_procession_built")
    def wax_procession_built(t):
        bad = wax_checks()
        if bad:
            from modcheck import ExpectationFailed
            raise ExpectationFailed("; ".join(bad))
        # Live pause/extrude/kill-spoil behaviour needs a floor map and a game: UNMEASURED here.
except ImportError:
    suite = None

if __name__ == "__main__":
    problems = static_checks() + roster_checks() + catch_checks() + saal_name_checks() + ekkel_lore_checks() + wax_checks()
    print("STATIC: %s" % ("PASS (0 findings)" if not problems else "FAIL"))
    for p in problems:
        print("  - " + p)
    sys.exit(1 if problems else 0)
