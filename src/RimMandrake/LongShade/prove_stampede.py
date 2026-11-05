"""Proof of LONGSHADE_STAMPEDE_LIVECHECK_1: the "stampede for your roof" incident (RM_ShadeStampede) on one RM_LongShade map.

    python3 src/RimMandrake/LongShade/prove_stampede.py --offline
    python.exe src/RimMandrake/LongShade/prove_stampede.py --clause A1 < /dev/null    (A1..A7)

Exit 0 = the clause holds, 1 = it does not, 2 = UNMEASURED (no game or bridge, probe not in the loaded DLL, no herd kind in
the biome roster, fewer than 8 spawned, or the heat lever did not make the herd hot / cool when the clause needs it).

The live clauses share ONE scene (~8000 game ticks): the first clause asked generates an RM_LongShade map (tile 114480,
size 150), runs every stage, stores each reading in <tempdir>/rm_stampede_scene.json; a later clause within 45 minutes
reads that record. modEnabled and stampedeEnabled are set true for the run and put back as found.
Heat: Royalty's ClimateAdjustment condition (GameCondition_TemperatureOffset) with its tempOffset set so the outdoor
temperature is the kind's safe max + 8 C (hot) or the middle of its safe range (cool); the outdoor cache refreshes every
300 ticks, so every heat change is followed by a 320-tick run. The gate is read as the worker's own CanFireNowSub (by
reflection): IncidentWorker.CanFireNow caches one answer per tick and its storyteller gates (Map_PlayerHome, earliestDay,
the world tile's biome) say nothing about this mechanism on a generated test map.
Scene: Def -> map -> Stage 5 (wild animals cleared, home + built roof on an open 5x5, 5 of one roster herd kind 30-40
cells away) -> hot -> Can(few) -> Add 3 -> cool -> Can(cool) -> hot -> Can(hot) -> Roof off -> Can(noroof) -> Roof on ->
stampedeEnabled=false Can(off) -> true Can(on) -> Fire -> Interrupt -> run 130 -> Runners(reissue) -> cool, run 600 ->
Runners(cooled) -> hot, run 320 -> Can(hot2) -> Fire(fire2) -> run 5500 -> Runners(cap1) -> run 800 -> Runners(cap2) -> Cleanup.
  A1  IncidentDef RM_ShadeStampede is loaded, worker IncidentWorker_RM_ShadeStampede, allowedBiomes holds RM_LongShade
  A2  a herd of 8 same-def wild herd animals (>= 50 % overheated) and a roofed home cell: canFireNow (CanFireNowSub) true
  A3  no herd: 5 overheated animals (< 6) -> false; 8 cooled animals (< 50 % overheated) -> false
  A4  no roofed home cell (the roof rect taken out of home) with the hot herd -> false
  A5  stampedeEnabled=false with the hot herd and roof -> false; set back true -> true again
  A6  firing returns true, sends the letter "An overheated herd is bolting for your roof", and every runner (the whole
      herd) is on a Goto at Sprint to the target, a roofed home-area cell
  A7  re-issued every 120 ticks until each has cooled or 6000 ticks pass, three readings, all must hold:
      reissue  runners put on Wait are back on the Sprint Goto (or already at the target) within one 120-tick window
      cooled   after the heat drops below their safe max the stampede has no runners, well before 6000 ticks
      cap      a herd that stays overheated keeps running before 6000 ticks and is released after it
--offline  the wiring and the verdict logic (no game): the probe is compiled, every method the driver calls exists, the
           letter title / tuning numbers / toggle the item names still match the mechanism, and judge() passes a good
           record and fails (or calls UNMEASURED) each clause on a record broken for that clause.
"""
import json
import os
import re
import sys
import tempfile
import time

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
PROBE = "RimMandrake.LongShade.RM_StampedeProof"
TILE, SIZE = 114480, 150
RECORD = os.path.join(tempfile.gettempdir(), "rm_stampede_scene.json")
FRESH_S = 45 * 60
CLAUSES = tuple("A%d" % i for i in range(1, 8))
TOGGLES = ("modEnabled", "stampedeEnabled")
METHODS = ("Def", "Toggle", "Stage", "Add", "Heat", "Roof", "Can", "Runners", "Fire", "Interrupt", "Cleanup")
# The item's own numbers and words, pinned here, never read back from the mechanism under test.
TITLE = "An overheated herd is bolting for your roof"
MIN_HERD, HOT_FRACTION, HERD_RADIUS, CAP, REISSUE = 6, 0.5, 25, 6000, 120
FIRST, ADDED = 5, 3
WORKER = "RimMandrake.LongShade.IncidentWorker_RM_ShadeStampede"


def kv(line):
    """'HEAD a=1 b=x,y' -> {'a': '1', 'b': 'x,y', '_head': 'HEAD'}"""
    out = {"_head": (line or "").split(" ", 1)[0]}
    for m in re.finditer(r"(\w+)=(\S*)", line or ""):
        out[m.group(1)] = m.group(2)
    return out


def _i(d, k, default=None):
    try:
        return int(d.get(k))
    except (TypeError, ValueError):
        return default


def _b(d, k):
    return d.get(k) == "True"


def _hot_enough(c):
    alive, hot = _i(c, "alive", 0), _i(c, "hot", 0)
    return alive > 0 and hot >= HOT_FRACTION * alive


def _herd_ok(c):
    return _i(c, "alive", 0) >= MIN_HERD


def judge(rec):
    """-> {clause: (code, why)}; code 0 holds, 1 fails, 2 unmeasured. Pure: reads only the record."""
    out = {}
    d = kv(rec.get("def"))
    out["A1"] = ((0 if _b(d, "found") and d.get("worker") == WORKER and "RM_LongShade" in d.get("biomes", "").split(",") else 1),
                 "def: %s" % rec.get("def"))
    st, ad = kv(rec.get("stage")), kv(rec.get("add"))
    spawned = (_i(st, "spawned", 0) or 0) + (_i(ad, "spawned", 0) or 0)
    scene = None
    if st.get("_head") != "STAGED" or st.get("kind") in (None, "none"):
        scene = "staging gave no herd kind: %s" % rec.get("stage")
    elif st.get("biome") != "RM_LongShade":
        scene = "map biome is %s, not RM_LongShade" % st.get("biome")
    elif spawned < FIRST + ADDED:
        scene = "spawned %d of %d" % (spawned, FIRST + ADDED)
    kind = st.get("kind")

    def gate(name):
        return kv(rec.get(name))

    def clause(c, fn):
        if scene:
            out[c] = (2, "UNMEASURED: " + scene)
            return
        try:
            out[c] = fn()
        except Exception as ex:   # a missing reading is unmeasured, never a pass
            out[c] = (2, "UNMEASURED: reading missing (%r)" % (ex,))

    def need(name, head):
        r = gate(name)
        if r.get("_head") != head:
            raise KeyError("%s: %s" % (name, rec.get(name)))
        return r

    def a2():
        h = need("hot", "CAN")
        if not (_herd_ok(h) and _hot_enough(h)):
            return 2, "UNMEASURED: herd not hot enough to test (%s)" % rec["hot"]
        ok = _b(h, "sub") and _i(h, "homeRoofed", 0) >= 1 and h.get("bestDef") == kind and _i(h, "best", 0) >= MIN_HERD
        return (0 if ok else 1), "hot herd + roof: %s" % rec["hot"]

    def a3():
        f, c = need("few", "CAN"), need("cool", "CAN")
        if _i(f, "alive", 0) != FIRST or not _hot_enough(f) or _i(f, "homeRoofed", 0) < 1:
            return 2, "UNMEASURED: the 5-animal control is not 5 hot animals with a roof (%s)" % rec["few"]
        if not _herd_ok(c) or _hot_enough(c) or _i(c, "homeRoofed", 0) < 1:
            return 2, "UNMEASURED: the cooled control is not a cool herd of >= 6 with a roof (%s)" % rec["cool"]
        ok = not _b(f, "sub") and not _b(c, "sub")
        return (0 if ok else 1), "few: sub=%s; cool: sub=%s" % (f.get("sub"), c.get("sub"))

    def a4():
        n = need("noroof", "CAN")
        if not (_herd_ok(n) and _hot_enough(n)):
            return 2, "UNMEASURED: herd not hot for the no-roof control (%s)" % rec["noroof"]
        ok = _i(n, "homeRoofed", -1) == 0 and not _b(n, "sub")
        return (0 if ok else 1), "no roof: %s" % rec["noroof"]

    def a5():
        o, back = need("off", "CAN"), need("on", "CAN")
        if not (_herd_ok(o) and _hot_enough(o)) or _i(o, "homeRoofed", 0) < 1:
            return 2, "UNMEASURED: no hot herd + roof for the toggle control (%s)" % rec["off"]
        ok = o.get("stampedeEnabled") == "False" and not _b(o, "sub") and back.get("stampedeEnabled") == "True" and _b(back, "sub")
        return (0 if ok else 1), "off: sub=%s; back on: sub=%s" % (o.get("sub"), back.get("sub"))

    def a6():
        fr, h = need("fire", "FIRED"), need("hot", "CAN")
        n = _i(fr, "n", 0)
        ok = (_b(fr, "ok") and _b(fr, "letter") and n >= MIN_HERD and n == _i(h, "alive", -1)
              and _i(fr, "goto", -1) == n and _i(fr, "sprint", -1) == n and _i(fr, "toTarget", -1) == n
              and _b(fr, "targetRoofed") and _b(fr, "targetHome"))
        return (0 if ok else 1), "fire: %s" % rec["fire"]

    def a7():
        it, re_ = need("interrupt", "INTERRUPTED"), need("reissue", "RUNNERS")
        n = _i(it, "n", 0)
        if n < 1 or _i(it, "wait", -1) != n or _i(it, "goto", -1) != 0:
            return 1, "the interrupt did not leave every runner on Wait: %s" % rec["interrupt"]
        gap = _i(re_, "tick", 0) - _i(it, "tick", 0)
        if gap > 2 * REISSUE + 100:
            return 2, "UNMEASURED: %d ticks passed, more than one window plus the run's overshoot" % gap
        if _i(re_, "hot", 0) < _i(re_, "alive", 0):
            return 2, "UNMEASURED: some runners cooled during the window: %s" % rec["reissue"]
        g, at = _i(re_, "goto", -1), _i(re_, "atTarget", 0)
        ok = (_i(re_, "n", 0) == n and _i(re_, "wait", -1) == 0 and g == _i(re_, "sprint", -2) == _i(re_, "toTarget", -3)
              and g + at >= _i(re_, "alive", 99) and g >= 1)
        return (0 if ok else 1), "after %d ticks: %s" % (gap, rec["reissue"])

    def a8():
        c = need("cooled", "RUNNERS")
        if _i(c, "herdHot", 1) != 0:
            return 2, "UNMEASURED: the herd did not cool (%s)" % rec["cooled"]
        since = _i(c, "since", CAP)
        ok = _i(c, "n", -1) == 0 and not _b(c, "running") and 0 <= since < CAP
        return (0 if ok else 1), "cooled: %s" % rec["cooled"]

    def a9():
        h2, f2 = need("hot2", "CAN"), need("fire2", "FIRED")
        c1, c2 = need("cap1", "RUNNERS"), need("cap2", "RUNNERS")
        if not _b(h2, "sub") or not _b(f2, "ok") or _i(f2, "n", 0) < MIN_HERD:
            return 2, "UNMEASURED: the second stampede did not start (%s | %s)" % (rec["hot2"], rec["fire2"])
        s1, s2 = _i(c1, "since", -1), _i(c2, "since", -1)
        if not (0 <= s1 < CAP - REISSUE):
            return 2, "UNMEASURED: first read at since=%s is not before the cap" % s1
        if _i(c1, "hot", 0) < 1:
            return 2, "UNMEASURED: no runner still hot before the cap (%s)" % rec["cap1"]
        if _i(c2, "herdHot", 0) < 1:
            return 2, "UNMEASURED: nothing still hot after the cap, so cooling cannot be told from the cap (%s)" % rec["cap2"]
        ok = _i(c1, "n", 0) >= 1 and _b(c1, "running") and s2 >= CAP + REISSUE and _i(c2, "n", -1) == 0 and not _b(c2, "running")
        return (0 if ok else 1), "before: %s | after: %s" % (rec["cap1"], rec["cap2"])

    def a7_all():
        """the item's one re-issue clause: re-issued every 120 ticks until each has cooled or 6000 ticks pass"""
        parts = []
        for name, fn in (("reissue", a7), ("cooled", a8), ("cap", a9)):
            try:
                parts.append((name,) + tuple(fn()))
            except Exception as ex:
                parts.append((name, 2, "UNMEASURED: reading missing (%r)" % (ex,)))
        code = 1 if any(p[1] == 1 for p in parts) else (2 if any(p[1] == 2 for p in parts) else 0)
        return code, " || ".join("%s %s: %s" % (n, {0: "ok", 1: "FAIL", 2: "UNMEASURED"}[c], w) for n, c, w in parts)

    for c, fn in (("A2", a2), ("A3", a3), ("A4", a4), ("A5", a5), ("A6", a6), ("A7", a7_all)):
        clause(c, fn)
    return out


# ---------------------------------------------------------------- offline
def _read(rel):
    with open(os.path.join(REPO, rel), encoding="utf-8") as fh:
        return fh.read()


def _good():
    can = ("CAN sub=%s herd=8 alive=%d hot=%d homeRoofed=%d running=False best=%d bestDef=RM_Bokka outdoor=48 amb=48 "
           "safeMax=40 stampedeEnabled=%s modEnabled=True")
    run = ("RUNNERS n=%d goto=%d sprint=%d toTarget=%d wait=%d atTarget=%d hot=%d alive=%d herdHot=%d since=%d running=%s "
           "tick=%d target=75,75 targetRoofed=True targetHome=True")
    return {
        "def": "DEF found=True worker=%s biomes=RM_LongShade category=Misc" % WORKER,
        "stage": "STAGED kind=RM_Bokka spawned=5 failed=0 herd=5 wildCleared=9 roof=75,75 roofCells=25 herdAt=40,75 biome=RM_LongShade roster=RM_Bokka",
        "add": "ADDED spawned=3 failed=0 herd=8",
        "few": can % ("False", 5, 5, 25, 0, "True"),
        "cool": can % ("False", 8, 0, 25, 0, "True"),
        "hot": can % ("True", 8, 8, 25, 8, "True"),
        "noroof": can % ("False", 8, 8, 0, 8, "True"),
        "off": can % ("False", 8, 8, 25, 8, "False"),
        "on": can % ("True", 8, 8, 25, 8, "True"),
        "fire": "FIRED ok=True letters=1 letter=True " + (run % (8, 8, 8, 8, 0, 0, 8, 8, 8, 0, "True", 1000))[8:],
        "interrupt": "INTERRUPTED n=8 goto=0 wait=8 tick=1000",
        "reissue": run % (8, 6, 6, 6, 0, 2, 8, 8, 8, 160, "True", 1160),
        "cooled": run % (0, 0, 0, 0, 0, 0, 0, 0, 0, 760, "False", 1760),
        "hot2": can % ("True", 8, 8, 25, 8, "True"),
        "fire2": "FIRED ok=True letters=1 letter=True " + (run % (8, 8, 8, 8, 0, 0, 8, 8, 8, 0, "True", 2100))[8:],
        "cap1": run % (8, 3, 3, 3, 0, 5, 8, 8, 8, 5560, "True", 7660),
        "cap2": run % (0, 0, 0, 0, 0, 0, 0, 0, 8, 6400, "False", 8500),
    }


def _breaks():
    """clause -> list of (key, old, new) edits that must make that clause FAIL (code 1), not pass."""
    return {
        "A1": [("def", "found=True", "found=False"), ("def", "biomes=RM_LongShade", "biomes=Desert")],
        "A2": [("hot", "sub=True", "sub=False")],
        "A3": [("few", "sub=False", "sub=True"), ("cool", "sub=False", "sub=True")],
        "A4": [("noroof", "sub=False", "sub=True")],
        "A5": [("off", "sub=False", "sub=True"), ("on", "sub=True", "sub=False")],
        "A6": [("fire", "letter=True", "letter=False"), ("fire", "sprint=8", "sprint=7"), ("fire", "targetRoofed=True", "targetRoofed=False"),
               ("fire", "n=8", "n=7"), ("fire", "ok=True", "ok=False"), ("fire", "targetHome=True", "targetHome=False")],
        "A7": [("reissue", "wait=0", "wait=8"), ("reissue", "goto=6", "goto=0"), ("interrupt", "wait=8", "wait=0"),
               ("cooled", "n=0", "n=8"), ("cooled", "running=False", "running=True"),
               ("cap1", "n=8", "n=0"), ("cap2", "n=0", "n=8"), ("cap2", "since=6400", "since=6050")],
    }


def _unmeasured():
    """clause -> list of edits that must make that clause UNMEASURED (code 2): a bad scene is never a pass or a fail."""
    return {
        "A2": [("hot", "hot=8 homeRoofed=25 running=False best=8", "hot=2 homeRoofed=25 running=False best=8")],
        "A3": [("cool", "hot=0", "hot=8")],
        "A4": [("noroof", "alive=8 hot=8", "alive=8 hot=1")],
        "A7": [("cooled", "herdHot=0", "herdHot=3"), ("cap2", "herdHot=8", "herdHot=0"), ("cap1", "since=5560", "since=6100")],
    }


def offline():
    bad = []
    proj = _read("src/RimMandrake/LongShade/Source/RM_LongShade.csproj")
    if '<Compile Include="RM_StampedeProof.cs" />' not in proj:
        bad.append("RM_StampedeProof.cs is not compiled by RM_LongShade.csproj")
    src = _read("src/RimMandrake/LongShade/Source/RM_StampedeProof.cs")
    for meth in METHODS:
        if not re.search(r"public static string %s\(string \w+\)" % meth, src):
            bad.append("RM_StampedeProof.%s(string) missing" % meth)
    if 'public const string Title = "%s";' % TITLE not in src:
        bad.append("the probe's letter title drifted from the item's")
    mech = _read("src/RimMandrake/LongShade/Source/RM_ShadeExtras.cs")
    if 'SendStandardLetter("%s",' % TITLE not in mech:
        bad.append("the stampede letter title in RM_ShadeExtras.cs is no longer the item's")
    pins = {"MinHerd": str(MIN_HERD), "MinOverheatedFraction": "0.5f", "HerdRadius": "25f", "MaxStampedeTicks": str(CAP),
            "ReissueTicks": str(REISSUE)}
    for field, val in pins.items():
        if not re.search(r"public const \w+ %s = %s;" % (field, re.escape(val)), mech):
            bad.append("RM_ShadeExtrasTuning.%s is not the item's %s" % (field, val))
    for frag in ("locomotionUrgency = LocomotionUrgency.Sprint", "JobMaker.MakeJob(JobDefOf.Goto, target)",
                 "p.AmbientTemperature > p.SafeTemperatureRange().max", "c.Roofed(map) && c.Standable(map)",
                 "private static List<Pawn> FindHerd(Map map)", "private readonly List<Pawn> runners",
                 "private int startTick", "private IntVec3 target"):
        if frag not in mech:
            bad.append("mechanism lost %r (the probe reads or the item names it)" % frag)
    sett = _read("src/RimMandrake/LongShade/Source/RM_LongShadeMod.cs")
    for t in TOGGLES:
        if not re.search(r"public static bool %s\s*=" % t, sett):
            bad.append("RM_LongShadeSettings.%s is not a public static bool" % t)
    inc = _read("src/RimMandrake/LongShade/Defs/IncidentDefs/RM_ShadeStampede.xml")
    if "<defName>RM_ShadeStampede</defName>" not in inc or "<workerClass>%s</workerClass>" % WORKER not in inc:
        bad.append("RM_ShadeStampede.xml no longer names the worker")
    me = _read("src/RimMandrake/LongShade/prove_stampede.py")
    if ("type=PROBE, method=method, " + 'args=arg or "x")') not in me:
        bad.append('the driver can send args="" to jawa/static_call, which reads it as ZERO arguments (every probe method takes one)')
    calls = set(re.findall(r'static\("(\w+)"', me))
    if not calls or not calls <= set(METHODS):
        bad.append("the driver calls probe methods outside METHODS: %s" % sorted(calls - set(METHODS)))
    g = judge(_good())
    bad += ["judge does not pass %s on a good record: %s" % (c, w) for c, (code, w) in g.items() if code != 0]
    if set(g) != set(CLAUSES):
        bad.append("judge covers %s, not %s" % (sorted(g), CLAUSES))
    for want, table in ((1, _breaks()), (2, _unmeasured())):
        for c, edits in table.items():
            for k, old, new in edits:
                rec = _good()
                if old not in rec[k]:
                    bad.append("planted edit for %s does not apply (%s lacks %r)" % (c, k, old))
                    continue
                rec[k] = rec[k].replace(old, new, 1)
                got = judge(rec)[c][0]
                if got != want:
                    bad.append("judge gives %s=%d, not %d, on %s: %r -> %r" % (c, got, want, k, old, new))
    for k in _good():
        rec = _good()
        del rec[k]
        if all(code == 0 for code, _ in judge(rec).values()):
            bad.append("judge passes every clause with %s missing" % k)
    for b in bad:
        print("FAIL " + b)
    print("%s offline: probe compiled, mechanism strings and numbers match the item, judge sees a pass and every clause's fail"
          % ("PASS" if not bad else "FAIL"))
    return 0 if not bad else 1


# ---------------------------------------------------------------- live
def _scene():
    sys.path.insert(0, os.path.join(REPO, "src", "RimMandrake", "Utils"))
    from scenes import scenelib as S  # noqa: E402

    def static(method, arg="x"):
        # never args="": jawa/static_call reads "" as ZERO arguments, so every one-string probe method (Def, Can, Fire,
        # Runners...) silently returned "" (LIVE 2026-11-04, scene record of gen 3); the probe ignores the "x".
        r = S.call("jawa/static_call", type=PROBE, method=method, args=arg or "x")
        return str((r or {}).get("result", "")) if isinstance(r, dict) else str(r)

    if S.call("rimworld/get_ui_state").get("programState") != "Playing":
        S.call("rimworld/start_debug_game_ready", timeoutMs=280000, readiness="mapData", pauseIfNeeded=True)
        for _ in range(120):
            if S.call("rimworld/get_ui_state").get("programState") == "Playing":
                break
            time.sleep(1)
    back = (S.call("jawa/map_info") or {}).get("mapIndex", 0)
    rec = {"started": time.time()}
    if not static("Toggle", "probe").startswith("REFUSED: want"):
        rec["unmeasured"] = "probe RM_StampedeProof absent (new LongShade DLL not loaded): " + static("Toggle", "probe")
        return rec
    rec["def"] = static("Def")
    found = {}
    for t in TOGGLES:
        found[t] = kv(static("Toggle", t + "=true")).get("was")
    rec["toggles_found"] = found
    mid = None
    try:
        mid = S.biome_map(TILE, "RM_LongShade", size=SIZE)
        S.run(120)
        rec["stage"] = static("Stage", str(FIRST))
        if not rec["stage"].startswith("STAGED") or "kind=none" in rec["stage"]:
            rec["unmeasured"] = "staging refused: " + rec["stage"]
            return rec
        rec["heat1"] = static("Heat", "hot")
        if not rec["heat1"].startswith("HEAT"):
            rec["unmeasured"] = "heat lever refused: " + rec["heat1"]
            return rec
        S.run(320)
        rec["few"] = static("Can")
        rec["add"] = static("Add", str(ADDED))
        rec["heat_cool"] = static("Heat", "cool")
        S.run(320)
        rec["cool"] = static("Can")
        rec["heat2"] = static("Heat", "hot")
        S.run(320)
        rec["hot"] = static("Can")
        rec["roof_off"] = static("Roof", "off")
        rec["noroof"] = static("Can")
        rec["roof_on"] = static("Roof", "on")
        static("Toggle", "stampedeEnabled=false")
        rec["off"] = static("Can")
        static("Toggle", "stampedeEnabled=true")
        rec["on"] = static("Can")
        rec["fire"] = static("Fire")
        rec["interrupt"] = static("Interrupt")
        S.run(130)
        rec["reissue"] = static("Runners")
        rec["heat_cool2"] = static("Heat", "cool")
        S.run(600)
        rec["cooled"] = static("Runners")
        rec["heat3"] = static("Heat", "hot")
        S.run(320)
        rec["hot2"] = static("Can")
        rec["fire2"] = static("Fire")
        S.run(5500)
        rec["cap1"] = static("Runners")
        S.run(800)
        rec["cap2"] = static("Runners")
        rec["cleanup"] = static("Cleanup")
    finally:
        for t, was in found.items():
            if was in ("True", "False"):
                static("Toggle", "%s=%s" % (t, was.lower()))
        if mid is not None:
            S.drop_map(mid, TILE, back)
    return rec


def live(clause):
    rec = None
    if os.path.isfile(RECORD):
        with open(RECORD, encoding="utf-8") as fh:
            old = json.load(fh)
        if time.time() - old.get("started", 0) < FRESH_S and not old.get("unmeasured"):
            rec = old
            print("scene record reused: %s" % RECORD)
    if rec is None:
        try:
            rec = _scene()
        except Exception as ex:   # no bridge, no game
            print("UNMEASURED: %r" % (ex,))
            return 2
        with open(RECORD, "w", encoding="utf-8") as fh:
            json.dump(rec, fh, indent=1)
    if rec.get("unmeasured"):
        print("UNMEASURED: " + rec["unmeasured"])
        return 2
    code, why = judge(rec)[clause]
    print("%s %s: %s" % ({0: "PASS", 1: "FAIL"}.get(code, "UNMEASURED"), clause, why))
    return code


def main(argv):
    if "--offline" in argv:
        return offline()
    if "--clause" in argv and argv.index("--clause") + 1 < len(argv) and argv[argv.index("--clause") + 1] in CLAUSES:
        return live(argv[argv.index("--clause") + 1])
    print(__doc__)
    return 2


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
