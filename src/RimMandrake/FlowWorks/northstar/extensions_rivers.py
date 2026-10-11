"""northstar/extensions_rivers.py -- FlowWorks RIVERS extension suite (River Works, SURFACE_RIVER_WEIRS_1).

River Works was its own mod (mandrake.rm.riverworks) until 2026-10-05, when the owner ruled "I think river works
needs to be part of flow works." and it merged into FlowWorks as Source/Rivers, Defs/Rivers, Patches/Rivers. This
was that mod's first script; it is now a FlowWorks extension suite beside northstar/extensions.py.

Run on request, bridge held, site map WITH a river (design §9: a quicktest river map):
    python.exe src/RimMandrake/FlowWorks/northstar/extension_proof.py --live   (once validation.py registers it)
NOT YET REGISTERED in FlowWorks/validation.py (another agent owns it). The append-only hook, after the
`for _name, _fn in EXT.suite.chains` loop:
    import extensions_rivers as RIV
    suite.toggles += [t for t in RIV.suite.toggles if t not in suite.toggles]
    suite.chains += RIV.suite.chains
Until then `modcheck floor FlowWorks` reports the 22 Rivers toggles as uncovered -- correct, not a regression.

Covered: slice 1's surface current, fords, floods-as-surge, washed-off-map and crossing hazards; slice 2's
works: weir (bank-edge PlaceWorker, ~8-cell slack pool, fish from the river stock + biome drift, breach wash),
stake-line levee, silt swap table, rope ferry. Added 2026-10-05 with the merge: the levee flood check (a vanilla
SeasonalFlood asked directly whether it may spread into a stake cell and a gap), the breach cascade order, and
undrafted colonists using a ferry rope. UNCOVERED still: sea.unchanged (TerminalBiomes' own suite). Every probe is
a C# proof (RM_RiverWorksProof / RM_RiverWorksProofWorks) reached through jawa/static_call; a result starting
"UNMEASURED" (e.g. the site has no river) records UNMEASURED, never PASS.
"""
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


@suite.chain("swept")
def swept(t):
    """Owner card 1: swept to the edge -> washed away, walks home, with a letter."""
    with t.component("returns_home", toggle="washOffMapEdge"):
        if t._guard():
            res = _proof(t, "ProofSwept", "return")
            if not res.startswith("SWEPT pending=0"):
                raise ExpectationFailed("washed-away pawns could not walk home: %s" % res)


@suite.chain("taken_by_land")
def taken_by_land(t):
    """TAKEN_BY_LAND_SERVICE_1: the river is a taker of the shared service, the trace setting is readable, and the book answers.
    The gale (Stillsand) registers its own policy under 'gale'; with Stillsand not loaded that arm is reported, not failed."""
    with t.component("service_has_river_policy_and_trace_setting", toggle="takenByLandTraceEnabled"):
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


@suite.chain("placer")
def placer(t):
    """FLOWWORKS_QUARRY_DIGGING_1 river half (design 2b-2c): a sluice box on the site's own shallow river washes only
    pool minerals out of the shared stock, does nothing with its setting off, and a panning session draws the same
    stock; a forced flood refill restores it. One probe (RM_PlacerProof 'selfcheck') builds and removes its own box."""
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
            kv = _kv(_placer("selfcheck"))
            if not kv.get("pan", "").startswith("pan=") or kv.get("pan") in ("pan=off", "pan=nocolonist", "pan=rivercarriesnothing"):
                raise ExpectationFailed("a panning session could not run against the stock: %r" % kv)
    with t.component("flood_refill", toggle="placerFloodRefill"):
        if t._guard():
            _placer("drain")
            res = _placer("refill")
            kv = _kv(res.split("PLACER", 1)[-1])
            if float(kv.get("stock", -1)) != float(kv.get("cap", -2)):
                raise ExpectationFailed("a refill did not restore the stock to its cap: %s" % res)
