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
           "RM_Oovu", "RM_Iliss", "RM_Tarnn"]


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
    for n in ("RM_Heemin", "RM_Oovanam", "RM_Fessu", "RM_Krellik", "RM_Oddu", "RM_Oovu", "RM_Iliss", "RM_Tarnn"):
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
NO_FLOOR_BODY = {"Zhiil"}  # CHILL_ZHIIL_FLOOR_BODY_1 (sitting Q3) - caught, not yet alive on the floor


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
        if name not in NO_FLOOR_BODY and ("RM_" + name) not in wa:
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
except ImportError:
    suite = None

if __name__ == "__main__":
    problems = static_checks() + roster_checks() + catch_checks() + saal_name_checks()
    print("STATIC: %s" % ("PASS (0 findings)" if not problems else "FAIL"))
    for p in problems:
        print("  - " + p)
    sys.exit(1 if problems else 0)
