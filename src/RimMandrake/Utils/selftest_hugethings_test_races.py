"""selftest_hugethings_test_races.py -- offline proof of the harness-only Huge Things test races (TITANIC_BODYSIZE_TEST_RACE_1).

    python3 src/RimMandrake/Utils/selftest_hugethings_test_races.py      -> "N/N PASS", exit 0

No vanilla race reaches body size 8, so Huge Things' T2/T3 rows could not run on a minimal list. The harness-only mod
src/RimMandrake/HugeThingsTestRaces carries RM_TestTitanT2 (8), RM_TestTitanT3 (20) and RM_TestTitanT2Control (8, forced
out). This pins, from the XML alone:
  * each race's effective baseBodySize (inheritance resolved) and the tier the kernel gives it against the live
    RM_TitanicTierDef thresholds (RM_TitanicKernel.TierFor mirrored, `>=` boundaries);
  * the control carries RM_TitanicExtension forceEnabled=false, so it is the untiered same-mass control;
  * every race is harnessOnly (TitanPassageUtility.Eligible refuses it) and every kind has canArriveManhunter=false, so
    loading the test mod never puts a test titan into a session uninvited;
  * the live runner's judges (northstar/titan_test_races_live.py) pass a good reading and fail a bad one;
  * every race has a PawnKindDef of the same defName (TitanValidationHooks.KillTitanAt takes a kind name);
  * the mod depends on and loads after mandrake.rm.hugethings (the extension class lives there);
  * no file outside the test mod names a test race: no biome, no trade tag, nothing that could ship one to a player;
  * the races are documented in the rimbridge-companion skill's tool list.
A sanity probe proves the parser can see: the real T2 race RM_Hwelgrue reads 8 from its own def.
"""
import os
import re
import sys
import xml.etree.ElementTree as ET

ROOT = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", ".."))
MOD = os.path.join(ROOT, "src", "RimMandrake", "HugeThingsTestRaces")
TIERS = os.path.join(ROOT, "src", "RimMandrake", "HugeThings", "Defs", "TitanicTierDefs", "RM_TitanicTierDef.xml")
DOC = os.path.join(ROOT, "skills", "rimbridge-companion", "references", "extending-detail.md")
PROBE = os.path.join(ROOT, "src", "RimMandrake", "TheRot", "Defs", "Fauna", "RM_Hwelgrue.xml")
EXT = "RimMandrake.TitanicCreatures.RM_TitanicExtension"
EXPECT = {"RM_TestTitanT2": (8.0, "T2", None), "RM_TestTitanT3": (20.0, "T3", None),
          "RM_TestTitanT2Control": (8.0, "None", False)}

results = []


def check(name, ok, detail=""):
    results.append(ok)
    print("%s %s%s" % ("PASS" if ok else "FAIL", name, (" -- " + detail) if detail and not ok else ""))


def defs_in(folder):
    out = []
    for dp, _, fs in os.walk(folder):
        for f in sorted(fs):
            if f.endswith(".xml"):
                out.extend(ET.parse(os.path.join(dp, f)).getroot())
    return out


def resolve(nodes, tag):
    """defName -> (effective baseBodySize, forceEnabled or None, harnessOnly); ParentName chains inside `nodes` only."""
    by_name = {n.get("Name"): n for n in nodes if n.tag == tag and n.get("Name")}

    def field(n, path):
        while n is not None:
            v = n.findtext(path)
            if v is not None:
                return v.strip()
            n = by_name.get(n.get("ParentName"))
        return None

    out = {}
    for n in nodes:
        if n.tag != tag or not n.findtext("defName"):
            continue
        bs = field(n, "race/baseBodySize")
        fe, ho = None, False
        for li in n.findall("modExtensions/li"):
            if li.get("Class") == EXT and li.findtext("forceEnabled") is not None:
                fe = li.findtext("forceEnabled").strip().lower() == "true"
            if li.get("Class") == EXT and (li.findtext("harnessOnly") or "").strip().lower() == "true":
                ho = True
        out[n.findtext("defName").strip()] = (float(bs) if bs else None, fe, ho)
    return out


def tier_for(size, t1, t2, t3, force):
    # RM_TitanicKernel.TierFor: ForceOut -> None; >= boundaries; ForceIn floors at T1.
    if force is False:
        return "None"
    tier = "T3" if size >= t3 else "T2" if size >= t2 else "T1" if size >= t1 else "None"
    return "T1" if tier == "None" and force is True else tier


def judges():
    """The live runner's verdict functions (northstar/titan_test_races_live.py) on the hook text the C# formats: a good and a
    bad reading each, so a judge that passes everything or nothing fails here, offline."""
    sys.path.insert(0, os.path.join(ROOT, "src", "RimMandrake", "HugeThings", "northstar"))
    import titan_test_races_live as L
    good = ("RM_TestTitanT2 tier=T2 adultTier=T2 bodySize=8.0 wakeComp=True | RM_TestTitanT3 tier=T3 adultTier=T3 bodySize=20.0 "
            "wakeComp=True | RM_TestTitanT2Control tier=None adultTier=None bodySize=8.0 wakeComp=False | Elephant tier=T1 "
            "adultTier=T1 bodySize=4.0 wakeComp=True")
    check("judge_tiers: a right ladder passes", L.judge_tiers(L.parse_tiers(good)) == [])
    check("judge_tiers: a control read as T2 fails",
          L.judge_tiers(L.parse_tiers(good.replace("Control tier=None", "Control tier=T2"))) != [])
    y = "RM_TestTitanT2 tier=T2 n=6 meat=%d leather=40 factor=0.5000"
    c = "RM_TestTitanT2Control tier=None n=6 meat=600 leather=80 factor=1.0000"
    check("judge_yield: 300 of 600 at factor 0.5 passes", L.judge_yield(y % 300, c)[0] == "PASS")
    check("judge_yield: an unreduced T2 fails", L.judge_yield(y % 600, c)[0] == "FAIL")
    check("judge_yield: off by more than n fails", L.judge_yield(y % 310, c)[0] == "FAIL")
    r2 = "RM_TestTitanT2 tier=T2 roofAfter=none wallHpBefore=%d wallHpAfter=%d wallDestroyed=%s"
    rc = "RM_TestTitanT2Control tier=None roofAfter=RoofConstructed wallHpBefore=195 wallHpAfter=195 wallDestroyed=False"
    check("judge_roof: holed roof + broken wall passes", L.judge_roof(r2 % (195, 0, "True"), rc)[0] == "PASS")
    check("judge_roof: untouched wall fails", L.judge_roof(r2 % (195, 195, "False"), rc)[0] == "FAIL")
    check("judge_roof: a control that holes fails", L.judge_roof(r2 % (195, 0, "True"), rc.replace("RoofConstructed", "none"))[0] == "FAIL")
    t2 = "RM_TestTitanT2 tier=T2 costOpen=%s costThick=%s"
    tc = "RM_TestTitanT2Control tier=None costOpen=13.0 costThick=13.0"
    check("judge_thick: penalty on T2 only passes", L.judge_thick(t2 % ("13.0", "2000.0"), tc)[0] == "PASS")
    check("judge_thick: no penalty fails", L.judge_thick(t2 % ("13.0", "13.0"), tc)[0] == "FAIL")
    rows = [dict(id=i, status="PASS", cls="MOD") for i in L.ROWS]
    check("verdict: five PASS rows -> 0", L.verdict(rows) == 0)
    check("verdict: a MOD FAIL still has a verdict -> 0", L.verdict(rows[:-1] + [dict(id=L.ROWS[-1], status="FAIL", cls="MOD")]) == 0)
    check("verdict: an UNMEASURED row -> 1", L.verdict(rows[:-1] + [dict(id=L.ROWS[-1], status="UNMEASURED", cls="SITE")]) == 1)
    check("verdict: a missing row -> 1", L.verdict(rows[:-1]) == 1)


def main():
    tr = ET.parse(TIERS).getroot().find("*")
    t1, t2, t3 = (float(tr.findtext(k)) for k in ("t1MinBodySize", "t2MinBodySize", "t3MinBodySize"))
    check("tier thresholds read 4/8/20", (t1, t2, t3) == (4.0, 8.0, 20.0), "%r" % ((t1, t2, t3),))

    probe = resolve(list(ET.parse(PROBE).getroot()), "ThingDef").get("RM_Hwelgrue", (None, None, False))[0]
    check("sanity probe: parser reads RM_Hwelgrue baseBodySize 8", probe == 8.0, "read %r" % probe)

    nodes = defs_in(os.path.join(MOD, "Defs"))
    races = resolve(nodes, "ThingDef")
    check("exactly the three test races", sorted(races) == sorted(EXPECT), "%r" % sorted(races))
    for d, (size, tier, force) in sorted(EXPECT.items()):
        got = races.get(d, (None, None, False))
        check("%s harnessOnly (never a titan-passage pick)" % d, got[2] is True)
        check("%s baseBodySize %g" % (d, size), got[0] == size, "read %r" % (got[0],))
        check("%s forceEnabled %r" % (d, force), got[1] == force, "read %r" % (got[1],))
        check("%s is tier %s" % (d, tier), got[0] is not None and tier_for(got[0], t1, t2, t3, got[1]) == tier,
              "kernel mirror gives %s" % (tier_for(got[0], t1, t2, t3, got[1]) if got[0] else "n/a"))
    kinds = {n.findtext("defName").strip(): (n.findtext("race") or "").strip() for n in nodes
             if n.tag == "PawnKindDef" and n.findtext("defName")}
    check("one PawnKindDef per race, same defName", kinds == {d: d for d in EXPECT}, "%r" % kinds)
    kind_base = {n.get("Name"): n for n in nodes if n.tag == "PawnKindDef" and n.get("Name")}
    for n in nodes:
        if n.tag == "PawnKindDef" and n.findtext("defName"):
            v, m = None, n
            while m is not None and v is None:
                v = m.findtext("canArriveManhunter")
                m = kind_base.get(m.get("ParentName"))
            check("%s canArriveManhunter false" % n.findtext("defName"), (v or "").strip().lower() == "false", "read %r" % v)
    with open(os.path.join(ROOT, "src", "RimMandrake", "HugeThings", "Source", "Titanic", "Events", "TitanPassage.cs")) as fh:
        check("TitanPassageUtility.Eligible refuses a harnessOnly race (drift guard)",
              "GetModExtension<RM_TitanicExtension>()?.harnessOnly == true) return false;" in fh.read())
    for n in nodes:
        if n.tag == "ThingDef" and n.find("tradeTags") is not None:
            check("no trade tags on %s" % (n.get("Name") or n.findtext("defName")), False)

    about = ET.parse(os.path.join(MOD, "About", "About.xml")).getroot()
    deps = [li.findtext("packageId") for li in about.findall("modDependencies/li")]
    check("About depends on mandrake.rm.hugethings", deps == ["mandrake.rm.hugethings"], "%r" % deps)
    check("About loads after mandrake.rm.hugethings",
          "mandrake.rm.hugethings" in [li.text for li in about.findall("loadAfter/li")])
    check("About packageId", about.findtext("packageId") == "mandrake.rm.hugethingstestraces")

    pat = re.compile(r"RM_TestTitan")
    leaks = []
    for tier_dir in ("RimMandrake", "RimStarWars", "RimUtinni"):
        base = os.path.join(ROOT, "src", tier_dir)
        for dp, dns, fs in os.walk(base):
            if os.path.abspath(dp).startswith(MOD):
                continue
            for f in fs:
                if f.endswith(".xml"):
                    p = os.path.join(dp, f)
                    with open(p, encoding="utf-8", errors="replace") as fh:
                        if pat.search(fh.read()):
                            leaks.append(os.path.relpath(p, ROOT))
    check("no XML outside the test mod names a test race (nothing ships one)", not leaks, "%r" % leaks[:5])

    with open(DOC, encoding="utf-8") as fh:
        doc = fh.read()
    check("rimbridge-companion tool list documents the test races",
          all(d in doc for d in EXPECT) and "mandrake.rm.hugethingstestraces" in doc)

    judges()
    n_ok = sum(1 for r in results if r)
    print("%d/%d PASS" % (n_ok, len(results)))
    return 0 if n_ok == len(results) and results else 1


if __name__ == "__main__":
    sys.exit(main())
