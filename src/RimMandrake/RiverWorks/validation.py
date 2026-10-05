"""validation.py -- modcheck suite for RimMandrake: River Works (mandrake.rm.riverworks). First script.

Never deployed (deploy_custom_mods.py excludes `.py`). Run with:

    python.exe src/RimMandrake/Utils/modcheck/cli.py run RiverWorks

State: SLICE 1 (SURFACE_RIVER_WEIRS_1) -- the surface current, fords, floods-as-surge, washed-off-map
and crossing hazards. The weir / stake-line levee / silt-trap move out of TerminalBiomes in slice 2, so
those walk lines are UNCOVERED here. Every probe is a C# proof (RM_RiverWorksProof) reached through
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
]
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
