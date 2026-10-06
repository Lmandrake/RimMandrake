"""validation.py -- modcheck suite for RimMandrake: River Works (mandrake.rm.riverworks). First script.

Never deployed (deploy_custom_mods.py excludes `.py`). Run with:

    python.exe src/RimMandrake/Utils/modcheck/cli.py run RiverWorks

State: SLICE 2 (SURFACE_RIVER_WEIRS_1) -- slice 1's surface current, fords, floods-as-surge, washed-off-map
and crossing hazards, plus the works moved out of TerminalBiomes: weir (bank-edge PlaceWorker, ~8-cell slack
pool, fish from the river stock + biome drift, breach wash), stake-line levee, silt swap table, rope ferry.
UNCOVERED still: levee.holds/gap_leaks as a live flood walk (only the engine fact is read), breach.cascade_order
timing, sea.unchanged (TerminalBiomes' own suite). Every probe is a C# proof (RM_RiverWorksProof) reached through
jawa/static_call; a result starting "UNMEASURED" (e.g. the site has no river) records UNMEASURED, never PASS.
Needs a site map WITH a river (design §9: a quicktest river map).
"""
from modcheck import Suite, ExpectationFailed

suite = Suite("RiverWorks")
SETTINGS = "RimMandrake.RiverWorks.RM_RiverWorksSettings"
suite.toggles = [
    "riverWorksEnabled", "surfaceCurrentEnabled", "scaleWithRiverSize", "floodSurgeEnabled",
    "countSeasonalFloods", "countTorrentialRainFloods", "carryAnimals", "carryStrangers", "carryItems",
    "washOffMapEdge", "pathfinderAvoidsCurrents", "crossingHazardsEnabled", "fordsEnabled",
    "bankWorksEnabled", "breachEnabled", "stakeLineLevee", "weirCatchesFish", "weirCatchesDrift",
    "breachWashesCatch", "siltRichening", "ferryEnabled",
]
WORKS = "RimMandrake.RiverWorks.RM_RiverWorksProofWorks"
PROOF = "RimMandrake.RiverWorks.RM_RiverWorksProof"


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
            res = _proof(t, "ProofShove", "fast|3")
            if not res.startswith("MOVED") or int(res.split()[1]) < 3:
                raise ExpectationFailed("fast lane did not carry a colonist 3 cells: %s" % res)
    with t.component("ford_exempt", toggle="fordsEnabled"):
        if t._guard():
            res = _proof(t, "ProofShove", "ford|3")
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
