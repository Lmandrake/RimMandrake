"""northstar/extensions_rivers.py -- FlowWorks RIVERS extension suite (River Works, SURFACE_RIVER_WEIRS_1).

River Works was its own mod (mandrake.rm.riverworks) until 2026-10-05, when the owner ruled "I think river works
needs to be part of flow works." and it merged into FlowWorks as Source/Rivers, Defs/Rivers, Patches/Rivers. This
was that mod's first script; it is now a FlowWorks extension suite beside northstar/extensions.py.

Run on request, bridge held, site map WITH a river (design §9: a quicktest river map):
    python.exe src/RimMandrake/FlowWorks/northstar/extension_proof.py --live
FlowWorks/validation.py registers this suite (imported as RIV: its toggles join the floor, its chains run with the
extensions').

Covered live here: slice 1's surface current, fords and washed-off-map return; slice 2's works: weir (bank-edge
PlaceWorker, ~8-cell slack pool, fish from the river stock, breach wash), stake-line levee, silt swap table, rope
ferry. Floods-as-surge, crossing hazards and biome drift are offline C# flips only (validation.rivers_switch_flips),
not components here. Added 2026-10-05 with the merge: the levee flood check (a vanilla
SeasonalFlood asked directly whether it may spread into a stake cell and a gap), the breach cascade order, and
undrafted colonists using a ferry rope. UNCOVERED still: sea.unchanged (TerminalBiomes' own suite). Every probe is
a C# proof (RM_RiverWorksProof / RM_RiverWorksProofWorks) reached through jawa/static_call; a result starting
"UNMEASURED" (e.g. the site has no river) records UNMEASURED, never PASS.
"""
import re
from contextlib import contextmanager

from modcheck import Suite, ExpectationFailed

suite = Suite("FlowWorksRivers")
SETTINGS = "RimMandrake.FlowWorks.Rivers.RM_RiversSettings"
suite.toggles = [
    "riverWorksEnabled", "surfaceCurrentEnabled", "scaleWithRiverSize", "floodSurgeEnabled",
    "countSeasonalFloods", "countTorrentialRainFloods", "carryAnimals", "carryStrangers", "carryItems",
    "washOffMapEdge", "takenByLandTraceEnabled", "pathfinderAvoidsCurrents", "crossingHazardsEnabled", "fordsEnabled",
    "bankWorksEnabled", "breachEnabled", "stakeLineLevee", "weirCatchesFish", "weirCatchesDrift",
    "breachWashesCatch", "siltRichening", "ferryEnabled", "ferryRopeGuidesColonists",
    # FLOWWORKS_QUARRY_DIGGING_1 river half (settings class RimMandrake.FlowWorks.Quarry.RM_QuarrySettings)
    "sluiceBoxEnabled", "panningEnabled", "placerFloodRefill",
]
WORKS = "RimMandrake.FlowWorks.Rivers.RM_RiverWorksProofWorks"
PROOF = "RimMandrake.FlowWorks.Rivers.RM_RiverWorksProof"


def _proof(t, method, args=""):
    r = t.bridge_call("jawa/static_call", type=PROOF, method=method, args=args or "-")
    if not isinstance(r, dict) or r.get("success") is False:
        raise ExpectationFailed("UNMEASURED: static_call %s did not answer: %r" % (method, r))
    res = str(r.get("result", ""))
    if res.startswith("UNMEASURED"):
        raise ExpectationFailed(res)
    return res


def _note(t, label, value):
    """Informational evidence on the current component (no verdict): what a probe reported beside its checks."""
    if t._current is not None:
        # the evidence contract is {"call", "result"} (modcheck/suite.py Component.evidence; report._row reads both)
        t._current.evidence.append({"call": "note: %s" % label, "result": value})


@contextmanager
def _owed(t, name, why):
    """A component with no predicate yet: UNMEASURED, never PASS, no `toggle=` (extensions._owed's contract)."""
    was, reason = t.upstream_failed, t.upstream_reason
    with t.component(name):
        if t._guard():
            t.upstream_failed = True
            t.upstream_reason = "UNMEASURED: owed, no predicate yet: %s" % why
        yield
    t.upstream_failed, t.upstream_reason = was, reason


def _kv(line):
    return dict(p.split("=", 1) for p in line.split() if "=" in p)


@suite.chain("current")
def current(t):
    """Design §3.1 / §3.7 on the site's own river."""
    with t.component("defs_core", beyond_toggle=True):
        r = t.bridge_call("jawa/get_defs", defs="TerrainDef/RM_FordStones")
        if t._guard() and (not isinstance(r, dict) or not r.get("foundCount")):
            raise ExpectationFailed("RM_FordStones not loaded: %r" % (r,))
    with t.component("grid_from_river", toggle="surfaceCurrentEnabled"):
        if t._guard():
            kv = _kv(_proof(t, "ProofGrid"))
            if int(kv.get("current", 0)) <= 0:
                raise ExpectationFailed("UNMEASURED: the site map has no river current (%r)" % kv)
            if int(kv.get("fast", 0)) + int(kv.get("edge", 0)) <= 0:
                raise ExpectationFailed("current grid has cells but no lanes: %r" % kv)
    with t.component("shoves", toggle="surfaceCurrentEnabled"):
        if t._guard():
            res = _proof(t, "ProofShove", "fast;3")
            if not res.startswith("MOVED") or int(res.split()[1]) < 3:
                raise ExpectationFailed("fast lane did not carry a colonist 3 cells: %s" % res)
    with t.component("ford_exempt", toggle="fordsEnabled"):
        if t._guard():
            res = _proof(t, "ProofShove", "ford;3")
            if not res.startswith("MOVED 0"):
                raise ExpectationFailed("a colonist on ford stones was carried: %s" % res)
    with t.component("exemptions", beyond_toggle=True):
        if t._guard():
            res = _proof(t, "ProofExemptions")
            if "building=True" not in res.split():
                raise ExpectationFailed("a building reads as carried: %s" % res)


def edge_river_cells(terrain, size, step=4, cap=12):
    """Staging cells for the swept row: moving river water on the map's outermost ring, grouped into runs per edge,
    the middle of each run plus every `step`-th cell, at most `cap` in all. `terrain` is {(x,z): defName} (top layer,
    site_spec.parse_ops of jawa/get_terrain_batch). 'Moving' in the defName is vanilla's WaterMovingShallow /
    WaterMovingChestDeep; which end is downstream is the mod's flow map, so every run gets cells and the book says who
    went off the edge."""
    w, h = size
    edges = (
        [(x, 0) for x in range(w)], [(x, h - 1) for x in range(w)],
        [(0, z) for z in range(1, h - 1)], [(w - 1, z) for z in range(1, h - 1)],
    )
    runs = []
    for line in edges:
        cur = []
        for c in line:
            if "Moving" in str(terrain.get(c) or ""):
                cur.append(c)
            elif cur:
                runs.append(cur)
                cur = []
        if cur:
            runs.append(cur)
    out = []
    for run in runs:
        pick = [run[len(run) // 2]] + run[::step]
        for c in pick:
            if c not in out:
                out.append(c)
    # interleave so a cap never spends every pawn on one (perhaps upstream) end
    by_run = [[c for c in out if c in set(r)] for r in runs]
    inter = []
    while any(by_run):
        for r in by_run:
            if r:
                inter.append(r.pop(0))
    return inter[:cap]


SWEPT_WAIT_CHUNK = 250          # RM_MapComponent_RiverCurrent.ScanIntervalTicks: a pawn is enrolled within one scan
SWEPT_WAIT_MAX = 1500           # an edge cell is one step from off-map: scan (<=250) + one cadence (<=~100 at size 1)


def _pending(res):
    try:
        return int(_kv(res).get("pending"))
    except (TypeError, ValueError):
        return None


def _map_pawn_ids(t):
    return {p.get("id") for p in ((t.bridge_call("jawa/list_pawns", limit=500) or {}).get("pawns") or []) if p.get("id")}


@suite.chain("swept")
def swept(t):
    """Owner card 1: swept to the edge -> washed away, walks home, with a letter.
    FW_RIVER_SITE_DIAGNOSE_NOBODY_SWEPT_AWAY: this row used only to READ the book, and nothing in river_site.py or any
    chain ever put a pawn in the current near an edge (the site's colonists stand drafted on dry ground), so it read
    'SWEPT pending=0' UNMEASURED on every pass 4-8 by construction. It now stages its own: drafted throwaway colonists on
    moving water at the map edge, waits for the current to carry one off (pending rises), then walks them home."""
    with t.component("returns_home", toggle="washOffMapEdge"):
        if t._guard():
            # ProofSwept with any arg but "return" only reads the book (RM_RiverWorksProof.cs ProofSwept)
            before = _proof(t, "ProofSwept", "read")
            p0 = _pending(before)
            if not before.startswith("SWEPT pending=") or p0 is None:
                raise ExpectationFailed("UNMEASURED: the swept book gave no pending count: %s" % before)
            staged, swept_ids = [], set()
            try:
                if p0 == 0:
                    mi = t.bridge_call("jawa/map_info") or {}
                    w, h = int(mi.get("sizeX") or 0), int(mi.get("sizeZ") or mi.get("sizeY") or 0)
                    if w <= 2 or h <= 2:
                        raise ExpectationFailed("UNMEASURED: map_info gave no map size: %r" % (mi,))
                    import site_spec as S
                    rects = "0,0,%d,1;0,%d,%d,1;0,0,1,%d;%d,0,1,%d" % (w, h - 1, w, h, w - 1, h)
                    tb = t.bridge_call("jawa/get_terrain_batch", rects=rects) or {}
                    if not tb.get("success"):
                        raise ExpectationFailed("UNMEASURED: get_terrain_batch on the map edges refused: %r" % (tb,))
                    cells = edge_river_cells(S.parse_ops(tb.get("ops")), (w, h))
                    if not cells:
                        raise ExpectationFailed("UNMEASURED: no moving river water on any map edge, so no edge to be swept off")
                    t.expect("letter", {"label_contains": "Swept away"})
                    t.expect("letter", {"label_contains": "Back from the river"})
                    for x, z in cells:
                        r = t.bridge_call("jawa/spawn_pawn", kindDef="Colonist", x=x, z=z, faction="player", count=1) or {}
                        pid = ((r.get("pawns") or [{}])[0] or {}).get("id")
                        if pid:
                            staged.append(pid)
                            t.bridge_call("jawa/set_draft", pawnId=pid, drafted=True)   # stays put; the current still carries
                    if not staged:
                        raise ExpectationFailed("UNMEASURED: no throwaway colonist spawned on %d edge river cells" % len(cells))
                    _note(t, "staged colonists on edge river cells", "%d on %s" % (len(staged), cells))
                    waited, now = 0, p0
                    while waited < SWEPT_WAIT_MAX and now <= p0:
                        t.wait_ticks(SWEPT_WAIT_CHUNK)
                        waited += SWEPT_WAIT_CHUNK
                        now = _pending(_proof(t, "ProofSwept", "read")) or 0
                    if now <= p0:
                        raise ExpectationFailed("UNMEASURED: %d colonists stood on moving water at the map edge %s for %d ticks "
                                                "and none was washed away (pending %d)" % (len(staged), cells, waited, now))
                    swept_ids = set(staged) - _map_pawn_ids(t)
                    _note(t, "washed away", "pending %d -> %d after %d ticks; off the map: %s" % (p0, now, waited, sorted(swept_ids)))
                res = _proof(t, "ProofSwept", "return")
                if not res.startswith("SWEPT pending=0"):
                    raise ExpectationFailed("washed-away pawns could not walk home: %s" % res)
                if swept_ids and not (swept_ids & _map_pawn_ids(t)):
                    raise ExpectationFailed("the book emptied but no washed-away colonist %s is back on the map" % sorted(swept_ids))
            finally:
                for pid in staged:
                    t.bridge_call("jawa/pawn_force_incapacitate", pawn=pid, action="vanish")


@suite.chain("taken_by_land")
def taken_by_land(t):
    """TAKEN_BY_LAND_SERVICE_1: the river is a taker of the shared service, the trace setting is readable, and the book answers.
    The gale (Stillsand) registers its own policy under 'gale'; with Stillsand not loaded that arm is reported, not failed."""
    # beyond_toggle: `traceSetting` in (True, False) and `pending >= 0` hold for any bool and any count, so this never
    # measured takenByLandTraceEnabled (named in validation.RIVER_TOGGLES_OWED); `river=True` is the real reading.
    with t.component("service_has_river_policy_and_trace_setting", beyond_toggle=True):
        if t._guard():
            kv = _kv(_proof(t, "ProofTaken"))
            if kv.get("river") != "True" or kv.get("traceSetting") not in ("True", "False"):
                raise ExpectationFailed("the shared service has no river policy or its trace setting is unreadable: %r" % kv)
            if int(kv.get("pending", -1)) < 0:
                raise ExpectationFailed("the book gave no pending count: %r" % kv)
            _note(t, "gale taker registered (Stillsand loaded)", kv.get("gale"))


def _works(t, method, args=""):
    r = t.bridge_call("jawa/static_call", type=WORKS, method=method, args=args or "-")
    if not isinstance(r, dict) or r.get("success") is False:
        raise ExpectationFailed("UNMEASURED: static_call %s did not answer: %r" % (method, r))
    res = str(r.get("result", ""))
    if res.startswith("UNMEASURED"):
        raise ExpectationFailed(res)
    return res


@suite.chain("works")
def works(t):
    """Slice 2: the bank works on the site's own river (each probe builds and removes its own works)."""
    with t.component("place_weir_bank_edge", toggle="bankWorksEnabled"):
        if t._guard():
            kv = _kv(_works(t, "ProofWeirPlace"))
            if kv.get("edge") != "True" or kv.get("dry") != "False" or kv.get("wet") != "False":
                raise ExpectationFailed("weir PlaceWorker wrong: %r" % kv)
    with t.component("weir_arrest_and_pool", toggle="bankWorksEnabled"):
        if t._guard():
            kv = _kv(_works(t, "ProofWeirPool"))
            if kv.get("arrestedWet") != "True" or int(kv.get("dropped", 0)) <= 0:
                raise ExpectationFailed("weir did not arrest or calm upstream: %r" % kv)
    with t.component("weir_fish_draws_stock", toggle="weirCatchesFish"):
        if t._guard():
            kv = _kv(_works(t, "ProofWeirCatch", "20"))
            if int(kv.get("fishRolls", 0)) <= 0 or float(kv.get("after", 0)) >= float(kv.get("before", 0)):
                raise ExpectationFailed("weir caught no fish or the stock did not drop: %r" % kv)
    with t.component("breach_wash", toggle="breachWashesCatch"):
        if t._guard():
            kv = _kv(_works(t, "ProofBreach"))
            if kv.get("breaching") != "True" or int(kv.get("heldAfter", 99)) >= int(kv.get("heldBefore", 0)):
                raise ExpectationFailed("breach did not wash the held catch away: %r" % kv)
    with t.component("silt_richen_and_revert", toggle="siltRichening"):
        if t._guard():
            kv = _kv(_works(t, "ProofSilt"))
            if kv.get("changed") != "True":
                raise ExpectationFailed("silt-trap did not richen and revert: %r" % kv)
    with t.component("ferry_rope", toggle="ferryEnabled"):
        if t._guard():
            kv = _kv(_works(t, "ProofFerry"))
            if kv.get("paired") != "True" or kv.get("ropeExempt") != "True":
                raise ExpectationFailed("ferry posts did not string an exempt rope: %r" % kv)
    with t.component("levee_engine_fact", toggle="stakeLineLevee"):
        if t._guard():
            kv = _kv(_works(t, "ProofLeveeFact"))
            if kv.get("stakeIsEdifice") != "True":
                raise ExpectationFailed("a stake is not an edifice, so it cannot hold a flood: %r" % kv)
    with t.component("levee_holds_and_gap_leaks", toggle="stakeLineLevee"):
        if t._guard():
            kv = _kv(_works(t, "ProofLevee"))
            if kv.get("stakeHolds") != "True" or kv.get("gapLeaks") != "True" or kv.get("offLetsThrough") != "True":
                raise ExpectationFailed("levee wrong (stake must hold, gap must leak, off must let through): %r" % kv)
    with t.component("breach_cascade_order", toggle="breachEnabled"):
        if t._guard():
            kv = _kv(_works(t, "ProofCascadeOrder"))
            if kv.get("anyDown") != "True":
                raise ExpectationFailed("UNMEASURED: no dry ground downstream of the weir for stakes: %r" % kv)
            if kv.get("monotone") != "True" or kv.get("upstreamSpared") != "True" or kv.get("allDownScheduled") != "True":
                raise ExpectationFailed("stake cascade not nearest-downstream-first / upstream not spared: %r" % kv)
    with t.component("ferry_rope_undrafted", toggle="ferryRopeGuidesColonists"):
        if t._guard():
            kv = _kv(_works(t, "ProofFerryPath"))
            if int(kv.get("onRope", -1)) != 0 or int(kv.get("offRope", 0)) <= 0:
                raise ExpectationFailed("rope cell still reads as costly to undrafted colonists: %r" % kv)


PLACER = "RimMandrake.FlowWorks.Quarry.RM_PlacerProof"
QUARRY = "RimMandrake.FlowWorks.Quarry.RM_QuarrySettings"
PAN_FIELDS = ("panningYieldMultiplier", "placerStockPercent")
PAN_MULT = 10            # slider max: hit chance 0.125 x (0.4 + 0.06 x Mining) x 10 >= 0.5
PAN_STOCK_PERCENT = 10   # default 2: a cap five washes cannot drain below one unit
PAN_TRIES = 8            # all-nothing at >= 50% a try is 0.4%: then it is a reading, not bad luck
# RM_PlacerPanning.Session answers that are no reading of the draw (nothing = roll 0; the others the site)
PAN_NO_READING = ("pan=nothing", "pan=stockspent", "pan=noroom", "pan=nocolonist")


def _setting_get(t, type_name, field):
    r = t.bridge_call("jawa/mod_settings_field", typeName=type_name, action="get", field=field) or {}
    return r.get("value") if r.get("success") is not False else None


@suite.chain("placer")
def placer(t):
    """FLOWWORKS_QUARRY_DIGGING_1 river half (design 2b-2c): a sluice box on the site's own shallow river washes only
    pool minerals out of the shared stock, does nothing with its setting off, and a panning session draws the same
    stock; the flood refill is owed (no flood edge staged). One probe (RM_PlacerProof 'selfcheck') builds and removes its own box."""
    def _placer(arg):
        r = t.bridge_call("jawa/static_call", type=PLACER, method="ProofReport", args=arg)
        if not isinstance(r, dict) or r.get("success") is False:
            raise ExpectationFailed("UNMEASURED: static_call RM_PlacerProof did not answer: %r" % (r,))
        res = str(r.get("result", ""))
        if res.startswith("UNMEASURED") or res.startswith("REFUSED"):
            raise ExpectationFailed(res)
        return res
    with t.component("sluice_washes_pool_from_stock", toggle="sluiceBoxEnabled"):
        if t._guard():
            kv = _kv(_placer("selfcheck"))
            if int(kv.get("poolCount", 0)) <= 0:
                raise ExpectationFailed("UNMEASURED: the site's rock holds no placer mineral, so its river carries nothing: %r" % kv)
            if int(kv.get("got", 0)) <= 0 or kv.get("drawMatches") != "True" or kv.get("inPool") != "True":
                raise ExpectationFailed("sluice washed nothing, or off-pool, or the stock did not fall by what came out: %r" % kv)
            if kv.get("off") != "sluice=off":
                raise ExpectationFailed("a sluice washed with sluiceBoxEnabled OFF: %r" % kv)
    with t.component("panning_draws_stock", toggle="panningEnabled"):
        if t._guard():
            # FW_RIVER_SITE_DIAGNOSE_NOBODY_SWEPT_AWAY (MEASURED in the C#): SelfCheck pans ONCE, and a session hits only
            # PanHitChance 0.125 x PanSkillFactor (0.4 + 0.06 x Mining) = 5-11% at Mining 0-10, so 'pan=nothing' was the
            # expected answer; and it pans AFTER five washes have drained the stock (before 11.2 -> after 0.2: a hit would
            # read 'stockspent'). The row raises the yield multiplier (hit chance >= 50%) and the stock percent (cap x5) for
            # its own tries only, restores both, and reads the pan off the stock book: panned += n, stock -= n.
            orig = {f: _setting_get(t, QUARRY, f) for f in PAN_FIELDS}
            if any(v is None for v in orig.values()):
                raise ExpectationFailed("UNMEASURED: could not read %s settings %r" % (QUARRY, orig))
            kv, pans, rep0, rep1 = {}, [], {}, {}
            try:
                t.set_setting(QUARRY, {"panningYieldMultiplier": PAN_MULT,
                                       "placerStockPercent": max(PAN_STOCK_PERCENT, float(orig["placerStockPercent"]))})
                for _ in range(PAN_TRIES):
                    rep0 = _kv(_placer("-"))
                    kv = _kv(_placer("selfcheck"))
                    rep1 = _kv(_placer("-"))
                    pans.append(kv.get("pan", ""))
                    if pans[-1] not in PAN_NO_READING:
                        break
            finally:
                t.set_setting(QUARRY, orig)
            _note(t, "pan tries", pans)
            pan = pans[-1] if pans else ""
            if pans and all(p == "pan=nothing" for p in pans):
                raise ExpectationFailed("%d panning sessions at yield x%s all rolled nothing (each >= 50%% to hit): %r"
                                        % (len(pans), PAN_MULT, pans))
            if pan in PAN_NO_READING:
                raise ExpectationFailed("UNMEASURED: the panning session drew nothing to see (%s): %r" % (pan, kv))
            m = re.match(r"pan=(\w+)x(\d+)$", pan)
            if not m or int(m.group(2)) <= 0:
                raise ExpectationFailed("a panning session could not draw from the stock: %r" % kv)
            n = int(m.group(2))
            try:
                panned = int(rep1["panned"]) - int(rep0["panned"])
                fell = float(kv["after"]) - float(rep1["stock"])
            except (KeyError, TypeError, ValueError):
                raise ExpectationFailed("UNMEASURED: the stock book was unreadable around the pan: %r / %r" % (rep0, rep1))
            if panned != n or abs(fell - n) > 0.05:
                raise ExpectationFailed("pan took %d but the book says panned +%d, stock fell %.2f: %r / %r"
                                        % (n, panned, fell, rep0, rep1))
    # Owed (review 2026-10-11): "refill" calls RM_MapComponent_PlacerStock.Refill(), which sets stock = cap whatever
    # placerFloodRefill says (the setting is read only by the flood-edge detector), so drain + refill could not fail.
    # A real pair raises a flood edge with the setting on and off; placerFloodRefill is in validation.RIVER_TOGGLES_OWED.
    with _owed(t, "flood_refill", "placerFloodRefill: no flood edge staged; the forced refill ignores the setting"):
        pass
