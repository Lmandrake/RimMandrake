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
cells away) -> hot -> Can(few) -> Add 3 -> FRESH cool -> FRESH hot -> Roof off -> Can(noroof) -> Roof on ->
stampedeEnabled=false Can(off) -> true Can(on) -> Fire -> Interrupt -> run 130 -> Runners(reissue) -> cool, run 600 ->
Runners(cooled) -> FRESH hot2 -> Fire(fire2) -> run 5500 -> Runners(cap1) -> run 800 -> Runners(cap2) -> Cleanup.
FRESH <read> = Stage 8 of the same kind as ONE batch -> heat -> run 320 -> jawa/list_pawns (HERD line: n, wild, max pairwise
distance, factions) -> Can(<read>), both at the same paused tick; re-staged up to 3 times while the batch is not together.
The herd precondition is READ, never assumed: wild animals wander, and a gate that says false over a scattered herd says
nothing about the mechanism (LIVE 2026-11-06: best=0 with herd=8 hot=8, 1081 ticks after a two-batch spawn, and no reading
of where the 8 were). A clause whose control or stimulus needs the herd is UNMEASURED unless the HERD line shows >= 8
same-kind, faction-less pawns all within 25 cells; with that shown, a false gate is a FAIL of the mechanism.
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
HEAT_RUN, FRESH_TRIES = 320, 3     # the outdoor cache refreshes every 300 ticks; how many batches may scatter before UNMEASURED
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


def herd_line(rows, kind, tick=None, truncated=0):
    """jawa/list_pawns rows -> 'HERD kind=X n=N wild=N maxd=F factions=a,b|none tick=N truncated=N': the living, spawned,
    not-downed pawns of the kind as FindHerd would weigh them, with the farthest pair (distance as InHorDistOf measures it)."""
    mine = [r for r in rows if r.get("kindDef") == kind and r.get("spawned") and not r.get("dead") and not r.get("downed")]
    pts = [(r.get("x", -1), r.get("z", -1)) for r in mine]
    far = max([((a[0] - b[0]) ** 2 + (a[1] - b[1]) ** 2) ** 0.5 for a in pts for b in pts] or [0.0])
    wild = sum(1 for r in mine if r.get("faction") is None)
    facs = sorted(set(str(r.get("faction")) for r in mine if r.get("faction") is not None))
    return "HERD kind=%s n=%d wild=%d maxd=%.1f factions=%s tick=%s truncated=%s" % (
        kind, len(mine), wild, far, ",".join(facs) or "none", tick, truncated or 0)


def together(line, kind):
    """-> None when the HERD line shows the clause's herd (>= 8 of the staged kind, all wild, all within 25 cells), else why not."""
    h = kv(line)
    if h.get("_head") != "HERD":
        return "no herd reading (%s)" % line
    n, wild = _i(h, "n", 0), _i(h, "wild", 0)
    try:
        far = float(h.get("maxd"))
    except (TypeError, ValueError):
        return "no distance in the herd reading (%s)" % line
    if h.get("kind") != kind or n < FIRST + ADDED or _i(h, "truncated", 1) != 0:
        return "not the staged 8 (%s)" % line
    if wild != n or h.get("factions") != "none":
        return "not all wild (%s)" % line
    if far > HERD_RADIUS:
        return "scattered past %d cells (%s)" % (HERD_RADIUS, line)
    return None


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

    def apart(name):
        """why the herd the read named was not the clause's herd, or None; a missing reading raises, so UNMEASURED"""
        need(name, "HERD")
        return together(rec[name], kind)

    def a2():
        h = need("hot", "CAN")
        if not (_herd_ok(h) and _hot_enough(h)):
            return 2, "UNMEASURED: herd not hot enough to test (%s)" % rec["hot"]
        why = apart("herd_hot")
        if why:
            return 2, "UNMEASURED: the herd precondition does not hold: %s; %s" % (why, rec["hot"])
        ok = _b(h, "sub") and _i(h, "homeRoofed", 0) >= 1 and h.get("bestDef") == kind and _i(h, "best", 0) >= MIN_HERD
        return (0 if ok else 1), "hot herd + roof: %s | %s" % (rec["hot"], rec["herd_hot"])

    def a3():
        f, c = need("few", "CAN"), need("cool", "CAN")
        if _i(f, "alive", 0) != FIRST or not _hot_enough(f) or _i(f, "homeRoofed", 0) < 1:
            return 2, "UNMEASURED: the 5-animal control is not 5 hot animals with a roof (%s)" % rec["few"]
        if not _herd_ok(c) or _hot_enough(c) or _i(c, "homeRoofed", 0) < 1:
            return 2, "UNMEASURED: the cooled control is not a cool herd of >= 6 with a roof (%s)" % rec["cool"]
        why = apart("herd_cool")
        if why:   # false over a scattered herd is false for the wrong reason
            return 2, "UNMEASURED: the cooled control's herd precondition does not hold: %s" % why
        ok = not _b(f, "sub") and not _b(c, "sub")
        return (0 if ok else 1), "few: sub=%s; cool: sub=%s" % (f.get("sub"), c.get("sub"))

    def a4():
        n = need("noroof", "CAN")
        if not (_herd_ok(n) and _hot_enough(n)):
            return 2, "UNMEASURED: herd not hot for the no-roof control (%s)" % rec["noroof"]
        if _i(n, "best", 0) < MIN_HERD:   # the worker sees no herd, so its false says nothing about the roof
            return 2, "UNMEASURED: the worker sees no herd in the no-roof control (%s)" % rec["noroof"]
        ok = _i(n, "homeRoofed", -1) == 0 and not _b(n, "sub")
        return (0 if ok else 1), "no roof: %s" % rec["noroof"]

    def a5():
        o, back = need("off", "CAN"), need("on", "CAN")
        if not (_herd_ok(o) and _hot_enough(o)) or _i(o, "homeRoofed", 0) < 1:
            return 2, "UNMEASURED: no hot herd + roof for the toggle control (%s)" % rec["off"]
        if _i(o, "best", 0) < MIN_HERD:   # the worker sees no herd, so its false says nothing about the toggle
            return 2, "UNMEASURED: the worker sees no herd in the toggle control (%s)" % rec["off"]
        ok = o.get("stampedeEnabled") == "False" and not _b(o, "sub") and back.get("stampedeEnabled") == "True" and _b(back, "sub")
        return (0 if ok else 1), "off: sub=%s; back on: sub=%s" % (o.get("sub"), back.get("sub"))

    def a6():
        fr, h = need("fire", "FIRED"), need("hot", "CAN")
        why = apart("herd_hot")
        if why:
            return 2, "UNMEASURED: the herd precondition does not hold: %s; %s" % (why, rec["fire"])
        n = _i(fr, "n", 0)
        ok = (_b(fr, "ok") and _b(fr, "letter") and n >= MIN_HERD and n == _i(h, "alive", -1)
              and _i(fr, "goto", -1) == n and _i(fr, "sprint", -1) == n and _i(fr, "toTarget", -1) == n
              and _b(fr, "targetRoofed") and _b(fr, "targetHome"))
        return (0 if ok else 1), "fire: %s" % rec["fire"]

    def a7():
        it, re_ = need("interrupt", "INTERRUPTED"), need("reissue", "RUNNERS")
        why = apart("herd_hot")
        if why:
            return 2, "UNMEASURED: the herd precondition does not hold: %s; %s" % (why, rec["interrupt"])
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
        why = apart("herd_hot")
        if why:
            return 2, "UNMEASURED: no stampede was owed, the herd precondition does not hold: %s" % why
        if _i(c, "herdHot", 1) != 0:
            return 2, "UNMEASURED: the herd did not cool (%s)" % rec["cooled"]
        since = _i(c, "since", CAP)
        ok = _i(c, "n", -1) == 0 and not _b(c, "running") and 0 <= since < CAP
        return (0 if ok else 1), "cooled: %s" % rec["cooled"]

    def a9():
        h2, f2 = need("hot2", "CAN"), need("fire2", "FIRED")
        c1, c2 = need("cap1", "RUNNERS"), need("cap2", "RUNNERS")
        why = apart("herd_hot2")
        if why:
            return 2, "UNMEASURED: the second herd's precondition does not hold: %s" % why
        if not _hot_enough(h2):
            return 2, "UNMEASURED: the second herd is not hot (%s)" % rec["hot2"]
        if not _b(h2, "sub") or not _b(f2, "ok") or _i(f2, "n", 0) < MIN_HERD:
            return 1, "a hot herd held together and the second stampede did not start (%s | %s | %s)" % (rec["herd_hot2"], rec["hot2"], rec["fire2"])
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
    herd = "HERD kind=RM_Bokka n=8 wild=8 maxd=6.0 factions=none tick=%d truncated=0"
    return {
        "def": "DEF found=True worker=%s biomes=RM_LongShade category=Misc" % WORKER,
        "stage": "STAGED kind=RM_Bokka spawned=5 failed=0 herd=5 wildCleared=9 roof=75,75 roofCells=25 herdAt=40,75 biome=RM_LongShade roster=RM_Bokka",
        "add": "ADDED spawned=3 failed=0 herd=8",
        "herd_cool": herd % 320,
        "herd_hot": herd % 640,
        "herd_hot2": herd % 1400,
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
        "A2": [("hot", "sub=True", "sub=False"), ("hot", "best=8", "best=0")],
        "A3": [("few", "sub=False", "sub=True"), ("cool", "sub=False", "sub=True")],
        "A4": [("noroof", "sub=False", "sub=True")],
        "A5": [("off", "sub=False", "sub=True"), ("on", "sub=True", "sub=False")],
        "A6": [("fire", "letter=True", "letter=False"), ("fire", "sprint=8", "sprint=7"), ("fire", "targetRoofed=True", "targetRoofed=False"),
               ("fire", "n=8", "n=7"), ("fire", "ok=True", "ok=False"), ("fire", "targetHome=True", "targetHome=False")],
        "A7": [("reissue", "wait=0", "wait=8"), ("reissue", "goto=6", "goto=0"), ("interrupt", "wait=8", "wait=0"),
               ("cooled", "n=0", "n=8"), ("cooled", "running=False", "running=True"),
               ("cap1", "n=8", "n=0"), ("cap2", "n=0", "n=8"), ("cap2", "since=6400", "since=6050"),
               ("hot2", "sub=True", "sub=False"), ("fire2", "ok=True", "ok=False")],
    }


def _unmeasured():
    """clause -> list of edits that must make that clause UNMEASURED (code 2): a bad scene is never a pass or a fail."""
    return {
        "A2": [("hot", "hot=8 homeRoofed=25 running=False best=8", "hot=2 homeRoofed=25 running=False best=8"),
               ("herd_hot", "maxd=6.0", "maxd=25.1"), ("herd_hot", "wild=8", "wild=7"), ("herd_hot", "factions=none", "factions=PlayerColony"),
               ("herd_hot", "n=8 wild=8", "n=7 wild=7"), ("herd_hot", "kind=RM_Bokka", "kind=RM_Other"), ("herd_hot", "truncated=0", "truncated=3"),
               ("herd_hot", "HERD", "UNREAD")],
        "A3": [("cool", "hot=0", "hot=8"), ("herd_cool", "maxd=6.0", "maxd=40.0"), ("herd_cool", "wild=8", "wild=0")],
        "A4": [("noroof", "alive=8 hot=8", "alive=8 hot=1"), ("noroof", "best=8", "best=0")],
        "A5": [("off", "best=8", "best=0")],
        "A6": [("herd_hot", "maxd=6.0", "maxd=40.0"), ("herd_hot", "wild=8", "wild=0")],
        "A7": [("cooled", "herdHot=0", "herdHot=3"), ("cap2", "herdHot=8", "herdHot=0"), ("cap1", "since=5560", "since=6100"),
               ("herd_hot", "maxd=6.0", "maxd=40.0"), ("herd_hot2", "maxd=6.0", "maxd=40.0"), ("hot2", "hot=8", "hot=1")],
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
    tool = _read("src/RimMandrake/bridgetools/JawaBench.BridgeTools/JawaBenchTerrainTools.cs")
    for frag in ('"jawa/list_pawns"', "kindDef = pawn.kindDef?.defName", "faction = pawn.Faction?.def?.defName", "x = pos.IsValid ? pos.x : -1",
                 "z = pos.IsValid ? pos.z : -1", "spawned = pawn.Spawned", "dead = pawn.Dead", "downed = pawn.Downed", "ticksGame = TicksGameSafe()", "truncated,"):
        if frag not in tool:
            bad.append("jawa/list_pawns lost %r (the herd reading reads it)" % frag)
    if 'p.Faction == null && p.RaceProps.Animal && p.RaceProps.herdAnimal && !p.Dead && !p.Downed' not in mech or "a.def == animals[i].def" not in mech:
        bad.append("FindHerd no longer weighs what the herd reading weighs (wild, same def, alive, not downed)")
    calls = set(re.findall(r'static\("(\w+)"', me))
    if not calls or not calls <= set(METHODS):
        bad.append("the driver calls probe methods outside METHODS: %s" % sorted(calls - set(METHODS)))
    bad += _logic_checks()
    bad += _mutants(me)
    for b in bad:
        print("FAIL " + b)
    print("%s offline: probe compiled, mechanism strings and numbers match the item, judge sees a pass and every clause's fail, "
          "the herd is read beside each gate, every mutant goes red" % ("PASS" if not bad else "FAIL"))
    return 0 if not bad else 1


def _logic_checks():
    """the verdict logic, the herd reading and the driver's order: pure, so a mutant of this file can run them too"""
    bad = []
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
    for name, clauses in (("herd_hot", ("A2", "A6", "A7")), ("herd_cool", ("A3",)), ("herd_hot2", ("A7",))):
        rec = _good()
        del rec[name]
        for c in clauses:
            if judge(rec)[c][0] != 2:
                bad.append("%s is not UNMEASURED with %s missing" % (c, name))
    bad += _replay_checks() + _herd_line_checks() + _script_checks()
    return bad


def _replay_checks():
    """the LIVE reading of 2026-11-06 (best=0, herd=8 hot=8): the proof must tell a scattered herd from a broken FindHerd"""
    seen = ("CAN sub=False herd=8 alive=8 hot=8 homeRoofed=25 running=False best=0 bestDef=none outdoor=113 amb=128 safeMax=105 "
            "stampedeEnabled=True modEnabled=True")
    bad = []
    for far, wild, want, says in (("6.0", "8", 1, "a broken FindHerd"), ("41.0", "8", 2, "a scattered herd"), ("6.0", "0", 2, "a herd with a faction")):
        rec = _good()
        rec["hot"] = seen
        rec["herd_hot"] = "HERD kind=RM_Bokka n=8 wild=%s maxd=%s factions=%s tick=1 truncated=0" % (wild, far, "none" if wild == "8" else "Ancients")
        code, why = judge(rec)["A2"]
        if code != want:
            bad.append("the 2026-11-06 reading over %s gives A2=%d, not %d: %s" % (says, code, want, why))
        if want == 1 and ("maxd=" not in why or "factions=" not in why or "best=" not in why):
            bad.append("the A2 verdict does not print spread and faction beside best=: %s" % why)
    # its knock-on: nothing fired, so no runners. Over a scattered herd that is unmeasured; over a herd held together, a failure
    run0 = ("RUNNERS n=0 goto=0 sprint=0 toTarget=0 wait=0 atTarget=0 hot=0 alive=0 herdHot=%d downed=0 since=-1 running=False tick=1211 "
            "target=none targetRoofed=False targetHome=False")
    for far, want in (("6.0", 1), ("41.0", 2)):
        rec = _good()
        rec.update(hot=seen, noroof=seen, off=seen, on=seen, fire="FIRED ok=False letters=0 letter=False " + (run0 % 8)[8:],
                   interrupt="INTERRUPTED n=0 goto=0 wait=0 tick=1081", reissue=run0 % 8, cooled=run0 % 0,
                   herd_hot="HERD kind=RM_Bokka n=8 wild=8 maxd=%s factions=none tick=1 truncated=0" % far)
        got = judge(rec)
        for c in ("A6", "A7"):
            if got[c][0] != want:
                bad.append("the 2026-11-06 knock-on with maxd=%s gives %s=%d, not %d: %s" % (far, c, got[c][0], want, got[c][1]))
        for c in ("A4", "A5"):
            if got[c][0] != 2:
                bad.append("the 2026-11-06 reading (the worker sees no herd) gives %s=%d, not UNMEASURED: %s" % (c, got[c][0], got[c][1]))
    return bad


def _herd_line_checks():
    bad = []

    def row(x, z, kind="K", faction=None, **kw):
        out = {"kindDef": kind, "x": x, "z": z, "faction": faction, "spawned": True, "dead": False, "downed": False}
        out.update(kw)
        return out
    pack = [row(0, 0)] * 7
    for rows, field, want in (([row(0, 0), row(15, 20)], "maxd", "25.0"),     # 15,20 is exactly the radius: InHorDistOf holds
                              ([row(0, 0), row(15, 21)], "maxd", "25.8"),
                              ([row(0, 0), row(3, 4), row(9, 0, kind="Other")], "n", "2"),     # another kind is not the herd
                              ([row(0, 0), row(90, 0, dead=True)], "maxd", "0.0"),
                              ([row(0, 0), row(90, 0, downed=True)], "n", "1"),
                              ([row(0, 0), row(90, 0, spawned=False)], "n", "1"),
                              ([row(0, 0), row(1, 0, faction="PlayerColony")], "wild", "1"),
                              ([row(0, 0), row(1, 0, faction="PlayerColony")], "factions", "PlayerColony"),
                              ([row(0, 0)], "factions", "none"), ([], "maxd", "0.0")):
        got = kv(herd_line(rows, "K", 7, 0)).get(field)
        if got != want:
            bad.append("herd_line %s=%s, not %s on %r" % (field, got, want, rows))
    for rows, ok in ((pack + [row(15, 20)], True), (pack + [row(15, 21)], False), (pack, False), (pack[:6] + [row(1, 0, kind="Other")] * 2, False),
                     (pack + [row(1, 0, faction="PlayerColony")], False), ([row(0, 0)] * 8, True)):
        why = together(herd_line(rows, "K", 7, 0), "K")
        if (why is None) != ok:
            bad.append("together says %r on %d rows, want together=%s" % (why, len(rows), ok))
    if together(herd_line([row(0, 0)] * 8, "K", 7, 2), "K") is None:
        bad.append("together accepts a truncated pawn list")
    if together("", "K") is None or together("HERD kind=K n=8 wild=8 factions=none truncated=0", "K") is None:
        bad.append("together accepts a line with no reading")
    return bad


def _fake_scene(scatter=lambda stages: False, lines=None):
    """_script against a stand-in game: a clock, a call log, and scatter(stages) saying whether this batch has spread."""
    st = {"clock": 0, "stages": 0, "log": []}

    def static(method, arg="x"):
        st["log"].append((method, arg, st["clock"]))
        if method == "Stage":
            st["stages"] += 1
            return "STAGED kind=K spawned=%s biome=RM_LongShade" % arg.split(",")[0]
        return (lines or {}).get(method, method.upper())

    def run(n):
        st["log"].append(("run", n, st["clock"]))
        st["clock"] += n

    def herd(kind):
        st["log"].append(("herd", kind, st["clock"]))
        return "HERD kind=%s n=8 wild=8 maxd=%s factions=none tick=%d truncated=0" % (kind, "40.0" if scatter(st["stages"]) else "6.0", st["clock"])
    rec = {}
    _script(rec, static, run, herd)
    return rec, st


def _script_checks():
    bad = []
    rec, st = _fake_scene()
    log = st["log"]
    names = {"herd_cool": 0, "herd_hot": 1, "herd_hot2": 2}
    reads = [i for i, e in enumerate(log) if e[0] == "herd"]
    if len(reads) != len(names) or any(k not in rec for k in names):
        return ["the driver does not read the herd once per fresh read: %s" % [e[0] for e in log]]
    for i in reads:
        nxt, clock = log[i + 1], log[i][2]
        if nxt[0] != "Can" or nxt[2] != clock:
            bad.append("the herd read at tick %d is not followed by Can at that tick: %r" % (clock, nxt))
        stage = [e for e in log[:i] if e[0] == "Stage"][-1]
        if clock - stage[2] > HEAT_RUN:
            bad.append("the herd read at tick %d comes %d ticks after its batch, more than one heat run" % (clock, clock - stage[2]))
        if stage[1] != "%d,kind=K" % (FIRST + ADDED):
            bad.append("the fresh batch is not 8 of the staged kind as one spawn: %r" % (stage,))
    order = [e[0] for e in log]
    hot_at, fire_at = reads[1], order.index("Fire")
    if any(e[0] == "run" for e in log[hot_at:fire_at]):
        bad.append("ticks pass between the hot herd read and the fire, so the read no longer describes what fired")
    fire2_at = len(order) - 1 - order[::-1].index("Fire")
    if any(e[0] == "run" for e in log[reads[2]:fire2_at]):
        bad.append("ticks pass between the second herd read and the second fire")
    if not rec.get("add", "").startswith("ADD") or rec.get("few") != "CAN":
        bad.append("the 5-animal control or the Add step is gone from the driver")
    # a scattered batch is staged again, up to FRESH_TRIES, then stays on the record for the judge to call UNMEASURED
    once = _fake_scene(lambda n: n == 2)[1]["stages"]
    if once != 1 + 2 + 1 + 1:
        bad.append("one scattered batch gave %d stagings, not 5" % once)
    rec2, st2 = _fake_scene(lambda n: True)
    if st2["stages"] != 1 + 3 * FRESH_TRIES:
        bad.append("an always-scattered herd gave %d stagings, not %d" % (st2["stages"], 1 + 3 * FRESH_TRIES))
    good = _good()
    good["herd_hot"] = rec2.get("herd_hot", "").replace("kind=K", "kind=RM_Bokka")
    if judge(good)["A2"][0] != 2:
        bad.append("an always-scattered herd does not leave A2 UNMEASURED")
    # a staging the probe refuses stops the scene; it is never read as a herd
    r3 = {}
    _script(r3, lambda m, a="x": "REFUSED: no" if m == "Stage" else m, lambda n: None, lambda k: "HERD")
    if not r3.get("unmeasured"):
        bad.append("a refused staging does not stop the scene as unmeasured")
    return bad


# (what the mutant does, the text in this file, its replacement): each must turn _logic_checks red, or the check is decoration
MUTANTS = (
    ("the driver stops reading the herd", 'rec["herd_" + name] = herd(kind)', 'rec["herd_" + name] = rec.get("herd_" + name, "HERD kind=K n=8 wild=8 maxd=6.0 factions=none tick=0 truncated=0")'),
    ("the batch ages four heat runs before it is read", 'static("Heat", mode)\n            run(HEAT_RUN)\n            rec["herd_"', 'static("Heat", mode)\n            run(HEAT_RUN * 4)\n            rec["herd_"'),
    ("the fresh batch is not re-staged", 'rec["stage_" + name] = static("Stage", "%d,kind=%s" % (FIRST + ADDED, kind))', 'rec["stage_" + name] = "STAGED"'),
    ("a2 stops asking where the herd is", '        why = apart("herd_hot")\n        if why:\n            return 2, "UNMEASURED: the herd precondition does not hold: %s; %s" % (why, rec["hot"])\n', ''),
    ("a6 stops asking where the herd is", '        why = apart("herd_hot")\n        if why:\n            return 2, "UNMEASURED: the herd precondition does not hold: %s; %s" % (why, rec["fire"])\n', ''),
    ("a7 stops asking where the herd is", '        why = apart("herd_hot")\n        if why:\n            return 2, "UNMEASURED: the herd precondition does not hold: %s; %s" % (why, rec["interrupt"])\n', ''),
    ("the cooled reading stops asking where the herd was", '        why = apart("herd_hot")\n        if why:\n            return 2, "UNMEASURED: no stampede was owed, the herd precondition does not hold: %s" % why\n', ''),
    ("a3 stops asking where the cooled herd is", '        why = apart("herd_cool")\n        if why:   # false over a scattered herd is false for the wrong reason\n            return 2, "UNMEASURED: the cooled control\'s herd precondition does not hold: %s" % why\n', ''),
    ("a4 stops asking if the worker saw the herd", 'if _i(n, "best", 0) < MIN_HERD:', 'if False:'),
    ("a5 stops asking if the worker saw the herd", 'if _i(o, "best", 0) < MIN_HERD:', 'if False:'),
    ("the second herd is not read", '        why = apart("herd_hot2")\n        if why:\n            return 2, "UNMEASURED: the second herd\'s precondition does not hold: %s" % why\n', ''),
    ("the radius is wrong", 'if far > HERD_RADIUS:', 'if far > HERD_RADIUS + 20:'),
    ("faction is ignored", 'if wild != n or h.get("factions") != "none":', 'if False:'),
    ("distance measures only x", '((a[0] - b[0]) ** 2 + (a[1] - b[1]) ** 2) ** 0.5', 'abs(a[0] - b[0]) * 1.0'),
    ("a dead pawn counts as herd", 'and r.get("spawned") and not r.get("dead") and not r.get("downed")]', 'and r.get("spawned") and not r.get("downed")]'),
    ("the verdict hides the spread", '"hot herd + roof: %s | %s" % (rec["hot"], rec["herd_hot"])', '"hot herd + roof: %s" % rec["hot"]'),
)


def _mutants(src):
    bad = []
    src = re.sub(r"(?ms)^MUTANTS = \(.*?^\)\n", "", src)     # the table holds every mutant's text too; a mutant needs only the code
    for what, old, new in MUTANTS:
        if src.count(old) != 1:
            bad.append("mutant %r does not apply: its text occurs %d times" % (what, src.count(old)))
            continue
        ns = {"__name__": "prove_stampede_mutant", "__file__": os.path.abspath(__file__)}
        exec(compile(src.replace(old, new), "<mutant>", "exec"), ns)
        try:
            caught = ns["_logic_checks"]()
        except Exception as ex:     # a crash in the checks is red too
            caught = ["crashed: %r" % (ex,)]
        if not caught:
            bad.append("mutant survived: %s" % what)
    return bad


# ---------------------------------------------------------------- live
def _script(rec, static, run, herd):
    """The scene's stages, in order, into rec. run() advances paused, so no tick passes between two reads with no run between."""
    rec["stage"] = static("Stage", str(FIRST))
    if not rec["stage"].startswith("STAGED") or "kind=none" in rec["stage"]:
        rec["unmeasured"] = "staging refused: " + rec["stage"]
        return
    kind = kv(rec["stage"]).get("kind")
    rec["heat1"] = static("Heat", "hot")
    if not rec["heat1"].startswith("HEAT"):
        rec["unmeasured"] = "heat lever refused: " + rec["heat1"]
        return
    run(HEAT_RUN)
    rec["few"] = static("Can")
    rec["add"] = static("Add", str(ADDED))

    def fresh(name, mode):
        """8 of the kind as ONE batch, the heat, one heat run, then the herd's whereabouts and the gate at one paused tick"""
        for _ in range(FRESH_TRIES):
            rec["stage_" + name] = static("Stage", "%d,kind=%s" % (FIRST + ADDED, kind))
            rec["heat_" + name] = static("Heat", mode)
            run(HEAT_RUN)
            rec["herd_" + name] = herd(kind)
            rec[name] = static("Can")
            if together(rec["herd_" + name], kind) is None:
                return

    fresh("cool", "cool")
    fresh("hot", "hot")
    rec["roof_off"] = static("Roof", "off")
    rec["noroof"] = static("Can")
    rec["roof_on"] = static("Roof", "on")
    static("Toggle", "stampedeEnabled=false")
    rec["off"] = static("Can")
    static("Toggle", "stampedeEnabled=true")
    rec["on"] = static("Can")
    rec["fire"] = static("Fire")
    rec["interrupt"] = static("Interrupt")
    run(130)
    rec["reissue"] = static("Runners")
    rec["heat_cool2"] = static("Heat", "cool")
    run(600)
    rec["cooled"] = static("Runners")
    fresh("hot2", "hot")
    rec["fire2"] = static("Fire")
    run(5500)
    rec["cap1"] = static("Runners")
    run(800)
    rec["cap2"] = static("Runners")
    rec["cleanup"] = static("Cleanup")


def _scene():
    sys.path.insert(0, os.path.join(REPO, "src", "RimMandrake", "Utils"))
    from scenes import scenelib as S  # noqa: E402
    from await_lifecycle import await_lifecycle  # noqa: E402

    def herd(kind):
        r = S.call("jawa/list_pawns", limit=500)
        if not S.ok(r):
            return "UNREAD jawa/list_pawns: %s" % str(r)[:200]
        return herd_line(r.get("pawns") or [], kind, r.get("ticksGame"), r.get("truncated"))

    def static(method, arg="x"):
        # never args="": jawa/static_call reads "" as ZERO arguments, so every one-string probe method (Def, Can, Fire,
        # Runners...) silently returned "" (LIVE 2026-11-04, scene record of gen 3); the probe ignores the "x".
        r = S.call("jawa/static_call", type=PROBE, method=method, args=arg or "x")
        return str((r or {}).get("result", "")) if isinstance(r, dict) else str(r)

    lc = await_lifecycle(S.call, "map_ready", deadline_s=400, start=True)
    if not lc.ok:
        return {"started": time.time(), "unmeasured": "no playing map: " + lc.reason}
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
        _script(rec, static, S.run, herd)
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
