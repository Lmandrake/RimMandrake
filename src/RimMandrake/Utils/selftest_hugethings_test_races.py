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
    floor = "RM_TestTitanT2 tier=T2 n=6 meat=6720 leather=1920 factor=1.0000"     # live 2026-11-03: the T2 race ON the T2 floor
    check("judge_yield: a factor-1 subject (on its tier floor) has no verdict, never MOD FAIL or PASS",
          L.judge_yield(floor, c.replace("meat=600", "meat=6720"))[0] is None)
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


LIVE_PROOFS = os.path.join(ROOT, "infrastructure", "state", "live_proofs", "TITANIC_BODYSIZE_TEST_RACE_1.txt")
KERNEL = os.path.join(ROOT, "src", "RimMandrake", "HugeThings", "Source", "Kernel", "RM_TitanicKernel.cs")



def live_mods_row():
    """Gen 5 (A2 game_fail 2026-11-02T20:21Z): the built sha changed no mod folder, so the live round gated A2 on no mod and ran
    it on a load without the test races. Pins: the proofs file's `live-mods:` line, read by the round's own parser, names
    HugeThings and HugeThingsTestRaces (each a real mod folder with a packageId, the gate's input), and the file tells the
    stager about neku.largepawns, which that line cannot name."""
    sys.path.insert(0, os.path.join(ROOT, "src", "RimMandrake", "rimflow"))
    import relentless_live_round as R
    with open(LIVE_PROOFS, encoding="utf-8") as fh:
        text = fh.read()
    mods = R.live_mods(text)
    check("live-mods names HugeThings and HugeThingsTestRaces", set(mods) >= {"HugeThings", "HugeThingsTestRaces"}, "%r" % mods)
    for m in mods:                                   # every folder the gate will demand must exist, or A2 is UNMEASURED forever
        about = os.path.join(ROOT, "src", "RimMandrake", m, "About", "About.xml")
        pid = ET.parse(about).getroot().findtext("packageId") if os.path.isfile(about) else None
        check("live-mods folder %s has a packageId" % m, bool(pid and pid.strip()), "read %r" % pid)
    check("proofs file names neku.largepawns for the stager", "neku.largepawns" in text.lower())
    check("A2 proof line still parses with the live-mods header", R.proof_lines(text).get("A2", "") == "python.exe src/RimMandrake/HugeThings/northstar/test_titan_footprint_live.py < /dev/null",
          "%r" % R.proof_lines(text))


def footprint_row():
    """Gen 3 (blind check WEAK, GAP footprint): the item's spec names the rows 'T2/T3 tiers, yield curve, roof, footprint', so A2's
    live proof must drive a footprint row. Pins: the A2 line runs the six-row wrapper; the wrapper's rows are the runner's five
    plus large_pawns_footprint_bridge; its judge passes 3/4/1 on the 4/8/20 ladder and fails an untouched Large Pawns; its edges
    are the kernel's FootprintSize; its verdict needs all six."""
    sys.path.insert(0, os.path.join(ROOT, "src", "RimMandrake", "HugeThings", "northstar"))
    import titan_test_races_live as L
    import test_titan_footprint_live as F
    with open(LIVE_PROOFS, encoding="utf-8") as fh:
        a2 = [ln.split(":", 1)[1].strip() for ln in fh if ln.startswith("live-proof A2:")]
    check("live-proof A2 is one line running the six-row wrapper",
          a2 == ["python.exe src/RimMandrake/HugeThings/northstar/test_titan_footprint_live.py < /dev/null"], "%r" % a2)
    check("wrapper rows = runner's five + large_pawns_footprint_bridge",
          tuple(F.ROWS) == tuple(L.ROWS) + ("large_pawns_footprint_bridge",) and len(L.ROWS) == 5, "%r" % (F.ROWS,))
    spec_words = {"tiers": "tier", "corpse site": "corpse", "yield curve": "yield", "roof": "roof", "footprint": "footprint"}
    miss = [w for w, k in spec_words.items() if not any(k in r for r in F.ROWS)]
    check("every row the item spec names is driven by A2", not miss, "undriven: %r" % miss)
    with open(KERNEL, encoding="utf-8") as fh:
        ksrc = fh.read()
    m = re.search(r"FootprintSize\(int tier\)\s*\{.*?case T3: return (\d+);\s*case T2: return (\d+);", ksrc, re.S)
    k = (int(m.group(1)), int(m.group(2))) if m else None
    check("wrapper edges match RM_TitanicKernel.FootprintSize (T3, T2) and force-out 1",
          k is not None and (F.EDGE[L.T3], F.EDGE[L.T2], F.EDGE[L.CTL]) == k + (1,), "kernel %r wrapper %r" % (k, F.EDGE))
    check("wrapper ladder is the tier def's 4/8/20",
          (F.LADDER["size2Min"], F.LADDER["size3Min"], F.LADDER["size4Min"]) == tier_floors(), "%r" % F.LADDER)
    cell = "(%d, 0, %d)"
    sq = lambda e, x0=100, z0=100: [cell % (x0 + i, z0 + j) for i in range(e) for j in range(e)]
    r3 = "[" + ", ".join(sq(3)) + "]"
    r4 = "[" + ", ".join(sq(4)[:12]) + "] (16 total)"
    r1 = "[" + cell % (5, 7) + "]"
    check("rect_edge: 9 listed cells -> 3", F.rect_edge(r3) == 3, "%r" % F.rect_edge(r3))
    check("rect_edge: 12 listed + (16 total) -> 4", F.rect_edge(r4) == 4, "%r" % F.rect_edge(r4))
    check("rect_edge: one cell -> 1", F.rect_edge(r1) == 1)
    check("rect_edge: 6 cells is no square -> None", F.rect_edge("[" + ", ".join(sq(3)[:6]) + "]") is None)
    check("rect_edge: nine cells in a row -> None", F.rect_edge("[" + ", ".join(cell % (100 + i, 100) for i in range(9)) + "]") is None)
    check("rect_edge: a duplicated cell -> None", F.rect_edge("[" + ", ".join(sq(3)[:8] + sq(3)[:1]) + "]") is None)
    check("rect_edge: '(16 total)' with no cells -> None", F.rect_edge("[] (16 total)") is None)
    check("rect_edge: an error text -> None", F.rect_edge("No public static OccupiedRect with 1 params.") is None)
    good_l = {"size2Min": 4.0, "size3Min": 8.0, "size4Min": 20.0}
    good_e = {L.T2: 3, L.T3: 4, L.CTL: 1}
    check("judge_footprint: 3/4/1 on 4/8/20 passes", F.judge_footprint(good_l, good_e)[0] == "PASS")
    check("judge_footprint: control 3 (override row not pushed) fails",
          F.judge_footprint(good_l, dict(good_e, **{L.CTL: 3}))[0] == "FAIL")
    check("judge_footprint: T3 at 3 fails", F.judge_footprint(good_l, dict(good_e, **{L.T3: 3}))[0] == "FAIL")
    check("judge_footprint: all 1x1 (Large Pawns inert) fails", F.judge_footprint(good_l, {L.T2: 1, L.T3: 1, L.CTL: 1})[0] == "FAIL")
    check("judge_footprint: Large Pawns' own 2.5/4.5/10 ladder fails",
          F.judge_footprint({"size2Min": 2.5, "size3Min": 4.5, "size4Min": 10.0}, good_e)[0] == "FAIL")
    check("judge_footprint: a NaN ladder fails",
          F.judge_footprint(dict(good_l, size3Min=float("nan")), good_e)[0] == "FAIL")
    check("judge_footprint: an unread edge fails", F.judge_footprint(good_l, dict(good_e, **{L.T2: None}))[0] == "FAIL")
    rows = [dict(id=r, status="PASS", cls="MOD") for r in F.ROWS]
    check("wrapper verdict: six PASS -> 0", F.verdict(rows) == 0)
    check("wrapper verdict: the runner's five alone -> 1", F.verdict(rows[:-1]) == 1)
    check("wrapper verdict: footprint UNMEASURED SITE (no Large Pawns) -> 1",
          F.verdict(rows[:-1] + [dict(id=F.FOOT, status="UNMEASURED", cls="SITE")]) == 1)
    check("wrapper verdict: a runner row missing -> 1", F.verdict(rows[1:]) == 1)


def no_bridge_no_verdict():
    """Gen 7: both live A2 'FAIL's (2026-11-02T20:21Z, 2026-11-03T06:01Z) were the proof itself: run as WSL python3 it cannot
    reach the bridge (Windows loopback), the RimBridgeError went uncaught, exit 1 read as FAIL, and relentless_live reruns under
    python.exe only on a non-PASS/FAIL code. Pins: the A2 line runs under python.exe (asserted in footprint_row); an unreachable
    bridge makes BOTH scripts return NO_VERDICT (2), never 0 or 1, and never touches the result JSON."""
    import tempfile
    sys.path.insert(0, os.path.join(ROOT, "src", "RimMandrake", "HugeThings", "northstar"))
    import rimbridge_client as C
    import titan_test_races_live as L
    import test_titan_footprint_live as F
    check("NO_VERDICT is neither PASS 0 nor FAIL 1", L.NO_VERDICT not in (0, 1), "%r" % L.NO_VERDICT)
    saved = (C.discover_from_log, C.RimBridge.connect, sys.argv, F.subprocess.call)

    def refuse(self):
        raise C.RimBridgeError("cannot reach the bridge from WSL (selftest probe)")
    for label, patch in (("connect refused", lambda: setattr(C.RimBridge, "connect", refuse)),
                         ("no bridge log", lambda: setattr(C, "discover_from_log",
                                                           lambda *a, **k: (_ for _ in ()).throw(OSError("no log"))))):
        C.discover_from_log, C.RimBridge.connect = saved[0], saved[1]
        if label == "connect refused":
            C.discover_from_log = lambda *a, **k: ("127.0.0.1", 1, "t")
        patch()
        with tempfile.TemporaryDirectory() as td:
            out = os.path.join(td, "a2.json")
            def run(main, argv):
                sys.argv = argv
                try:
                    return main()
                except Exception as e:                        # the pre-gen-7 shape: an uncaught traceback (exit 1)
                    return "raised %s" % type(e).__name__
            rc_inner = run(L.main, ["titan_test_races_live.py", "--out", out])
            rc_outer = {}
            for inner in (L.NO_VERDICT, 1):                   # the runner's own no-verdict, and a runner exit the wrapper must
                F.subprocess.call = lambda *a, **k: inner      # follow with its own (refused) connect
                try:
                    rc_outer[inner] = run(F.main, ["test_titan_footprint_live.py", "--out", out])
                finally:
                    F.subprocess.call = saved[3]
            check("%s: runner and wrapper both return NO_VERDICT" % label,
                  rc_inner == L.NO_VERDICT and set(rc_outer.values()) == {L.NO_VERDICT},
                  "inner %r outer %r" % (rc_inner, rc_outer))
            check("%s: no result JSON written" % label, not os.path.exists(out))
    C.discover_from_log, C.RimBridge.connect = saved[0], saved[1]
    # a runner no-verdict must stop the wrapper BEFORE it connects: a live wrapper bridge would judge five absent rows as FAIL
    opened, ob = [], L.open_bridge
    L.open_bridge = lambda: opened.append(1) or (_ for _ in ()).throw(RuntimeError("wrapper connected"))
    F.subprocess.call = lambda *a, **k: L.NO_VERDICT
    try:
        sys.argv = ["test_titan_footprint_live.py", "--out", os.path.join(tempfile.gettempdir(), "titan_nv_probe.json")]
        try:
            rc = F.main()
        except RuntimeError as e:
            rc = "raised %s" % e
    finally:
        L.open_bridge, F.subprocess.call = ob, saved[3]
    with open(F.__file__, encoding="utf-8") as fh:
        wsrc = fh.read()
    # live 2026-11-03: spawned pawns came in at 23-33y (forward-only aging refused), and static_call could not resolve a
    # ThingID whose defName ends in a digit (STATIC_CALL_THINGID_FIX_DIGIT_EATS_ITSELF): both left R6 UNMEASURED
    check("R6 ages with allowBackwards=True", 'biologicalYears=3.0, allowBackwards=True' in wsrc)
    check("R6 calls OccupiedRect by bare thingIDNumber", 'method="OccupiedRect", args=num)' in wsrc and "args=pid)" not in wsrc)
    check("runner no-verdict: wrapper returns NO_VERDICT without connecting", rc == L.NO_VERDICT and not opened,
          "rc %r connected %r" % (rc, bool(opened)))
    sys.argv = saved[2]


def tier_floors():
    n = ET.parse(TIERS).getroot().find("*")
    return tuple(float(n.findtext(k)) for k in ("t1MinBodySize", "t2MinBodySize", "t3MinBodySize"))


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
            if os.path.commonpath([os.path.abspath(dp), MOD]) == MOD:
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
    footprint_row()
    live_mods_row()
    no_bridge_no_verdict()
    n_ok = sum(1 for r in results if r)
    print("%d/%d PASS" % (n_ok, len(results)))
    return 0 if n_ok == len(results) and results else 1


if __name__ == "__main__":
    sys.exit(main())
