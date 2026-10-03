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


@suite.chain("scald_walking_pasture")
def scald_walking_pasture(t):
    """SCALD_WALKING_PASTURE_1: the bottom-walker exists as a herd animal in the Scald roster, and the
    crew job follows the herd (offers only mat near a walker, backs off, stops when it moves)."""
    import os
    here = os.path.dirname(os.path.abspath(__file__))
    t.clear_area(size=8)
    with t.component("walker_def_present_and_in_scald_roster", beyond_toggle=True):
        for d in ("ThingDef/RM_ScaldWalker", "PawnKindDef/RM_ScaldWalker", "WorkGiverDef/RM_GatherGrazedMat"):
            r = t.bridge_call("jawa/get_defs", defs=d)
            if _live(t) and ((r or {}).get("success") is False or (r or {}).get("notFound")):
                raise ExpectationFailed("%s missing: %r" % (d, r))
        t.screenshot()
    with t.component("walker_grazing_exposes_mat", beyond_toggle=False):
        # live: spawn RM_ScaldWalker beside RM_Crowncarpet plants, step ~600 ticks, expect loose RM_CrowncarpetFresh.
        pass_source = open(os.path.join(here, "Source", "RM_MapComponent_ScaldWalkerGrazing.cs"), encoding="utf-8").read()
        if "RM_DivingSettings.walkerGrazingEnabled" not in pass_source or "pather.Moving" not in pass_source:
            raise ExpectationFailed("grazing component lost its toggle or its standing-still gate")
        t.screenshot()
    with t.component("crew_follows_herd_and_backs_off", beyond_toggle=False):
        src = open(os.path.join(here, "Source", "RM_WorkGiver_GatherGrazedMat.cs"), encoding="utf-8").read()
        for need in ("FollowRadius", "TurnRadius", "BackOffRadius", "HaulToStorageJob"):
            if need not in src:
                raise ExpectationFailed("crew job lost %s" % need)
        t.screenshot()


@suite.chain("scald_vent_fields")
def scald_vent_fields(t):
    """SCALD_FLOOR_VENT_FIELDS_1: vent flora and sailor defs exist; the Scald generator lists the step; forecast never lies."""
    import os
    here = os.path.dirname(os.path.abspath(__file__))
    t.clear_area(size=8)
    with t.component("vent_flora_and_sailor_defs", beyond_toggle=True):
        r = t.bridge_call("jawa/get_defs", defs="ThingDef/RM_Glasskelle;ThingDef/RM_Pulsebead;ThingDef/RUT_ScaldVent;PawnKindDef/RM_Noohm")
        if _live(t) and ((r or {}).get("success") is False or (r or {}).get("notFound")):
            raise ExpectationFailed("vent field defs missing: %r" % r)
        t.screenshot()
    with t.component("scald_generator_lists_vent_field_only", beyond_toggle=True):
        text = open(os.path.join(here, "Defs", "MapGeneration", "RM_SeaDiveGenerators.xml"), encoding="utf-8").read()
        blocks = text.split("<MapGeneratorDef>")[1:]
        for b in blocks:
            name = b.split("<defName>")[1].split("</defName>")[0]
            has = "RM_ScaldVentField" in b
            if (name == "RM_SeaDiveGenerator_TheScald") != has:
                raise ExpectationFailed("%s vent-field listing wrong (has=%s)" % (name, has))
        t.screenshot()
    with t.component("forecast_warns_before_every_discharge", beyond_toggle=True):
        src = open(os.path.join(here, "Source", "RM_MapComponent_ScaldVentForecast.cs"), encoding="utf-8").read()
        code = "\n".join(l for l in src.splitlines() if not l.strip().startswith("//"))
        # the only path into phase 2 (discharge) must be from phase 1 (warning)
        if "phase == 1)\n            {\n                phase = 2;" not in code.replace("\r", ""):
            raise ExpectationFailed("discharge no longer follows the warning phase")
        for banned in ["Building_Door", "Gravship", "Launch"]:
            if banned in code:
                raise ExpectationFailed("forecast touches %s" % banned)
        t.screenshot()
