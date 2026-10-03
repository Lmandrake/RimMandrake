"""validation.py -- modcheck suite for DivingInteraction (mandrake.rm.divinginteraction).

First script for this mod; covers SEABED_PER_SEA_FLOORS_1 only: each terminal sea's surface
biome must carry RM_SeabedAccessExtension.floorBiome naming its own RM_SeabedFloor_<Sea>
biome (Patches/RM_SeabedFloorBiomeWiring.xml). Pure def-state check; no live run recorded yet.
"""
from modcheck import Suite, ExpectationFailed

suite = Suite("DivingInteraction")

SEAS = {"RM_TheScald": "RM_SeabedFloor_TheScald",
        "RM_GreySea": "RM_SeabedFloor_GreySea",
        "RM_TwilightSea": "RM_SeabedFloor_TwilightSea",
        "RM_TheChill": "RM_SeabedFloor_TheChill"}


def _live(t):
    return t.session is not None and not t.upstream_failed


@suite.chain("per_sea_floor_biomes")
def per_sea_floor_biomes(t):
    """Floor biomes exist and each sea's surface biome names its own floor."""
    t.clear_area(size=8)
    with t.component("floor_biomes_defined", beyond_toggle=True):
        r = t.bridge_call("jawa/get_defs",
                          defs=";".join("BiomeDef/%s" % f for f in SEAS.values()))
        if _live(t):
            missing = (r or {}).get("notFound") or []
            if (r or {}).get("success") is False or missing:
                raise ExpectationFailed("floor biomes missing or query failed: %r" % (missing or r))
        t.screenshot()
    with t.component("sea_biomes_name_their_floor", beyond_toggle=True):
        r = t.bridge_call("jawa/get_defs",
                          defs=";".join("BiomeDef/%s" % s for s in SEAS),
                          fields="modExtensions")
        if _live(t):
            text = str(r)
            bad = [s for s, f in SEAS.items() if f not in text]
            if bad:
                raise ExpectationFailed("surface biomes not wired to a floor biome: %s" % bad)
        t.screenshot()
