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


@suite.chain("scald_immersion_berth")
def scald_immersion_berth(t):
    """SCALD_IMMERSION_BERTH_1: Scald floor exists to host the berth; the component never touches doors or launch."""
    import os
    t.clear_area(size=8)
    with t.component("scald_floor_biome_present", beyond_toggle=True):
        r = t.bridge_call("jawa/get_defs", defs="BiomeDef/RM_SeabedFloor_TheScald")
        if _live(t) and ((r or {}).get("success") is False or (r or {}).get("notFound")):
            raise ExpectationFailed("Scald floor biome missing: %r" % r)
        t.screenshot()
    with t.component("berth_never_seals_or_blocks_launch", beyond_toggle=True):
        src = os.path.join(os.path.dirname(os.path.abspath(__file__)), "Source",
                           "RM_MapComponent_ScaldImmersionBerth.cs")
        text = open(src, encoding="utf-8").read()
        code = "\n".join(l for l in text.splitlines() if not l.strip().startswith("//"))
        banned = ["Building_Door", "HarmonyPatch", "Gravship", "SetForbidden", "Launch", "holdOpen", "Lock"]
        hit = [b for b in banned if b in code]
        if hit:
            raise ExpectationFailed("berth source touches doors/launch: %s" % hit)
        if "GenTemperature.PushHeat" not in code:
            raise ExpectationFailed("berth no longer works through vanilla room heat")
        t.screenshot()
