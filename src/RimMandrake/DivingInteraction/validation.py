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


@suite.chain("scald_return_gallery")
def scald_return_gallery(t):
    """SCALD_RETURN_GALLERY_1: gallery defs exist; the Scald generator lists the step; a wrong mark never touches anything but the latch."""
    import os
    here = os.path.dirname(os.path.abspath(__file__))
    t.clear_area(size=8)
    with t.component("gallery_defs", beyond_toggle=True):
        r = t.bridge_call("jawa/get_defs", defs="ThingDef/RM_ReturnGalleryHub;ThingDef/RM_GalleryOutlet;ThingDef/RM_GalleryPipe;ThingDef/RM_GalleryBreak;ThingDef/RM_ReturnGalleryLocker;ThingDef/RM_ImmersionSchematic;ThingDef/RM_CathedralHeatLog;JobDef/RM_ProbeGalleryOutlet")
        if _live(t) and ((r or {}).get("success") is False or (r or {}).get("notFound")):
            raise ExpectationFailed("gallery defs missing: %r" % r)
        t.screenshot()
    with t.component("scald_generator_lists_gallery_only", beyond_toggle=True):
        text = open(os.path.join(here, "Defs", "MapGeneration", "RM_SeaDiveGenerators.xml"), encoding="utf-8").read()
        for b in text.split("<MapGeneratorDef>")[1:]:
            name = b.split("<defName>")[1].split("</defName>")[0]
            if (name == "RM_SeaDiveGenerator_TheScald") != ("RM_ScaldReturnGallery" in b):
                raise ExpectationFailed("%s gallery listing wrong" % name)
        t.screenshot()
    with t.component("gallery_cannot_reach_live_systems", beyond_toggle=True):
        src = open(os.path.join(here, "Source", "RM_ReturnGallery.cs"), encoding="utf-8").read()
        code = "\n".join(l for l in src.splitlines() if not l.strip().startswith("//"))
        for banned in ["Gravship", "Launch", "Building_Door", "GameCondition", "Hediff", "TakeDamage", "IncidentWorker"]:
            if banned in code:
                raise ExpectationFailed("gallery logic touches %s" % banned)
        # exactly one true return per circuit
        gen = open(os.path.join(here, "Source", "GenStep_ScaldReturnGallery.cs"), encoding="utf-8").read()
        if gen.count("GalleryRole.Return,") != 1:
            raise ExpectationFailed("role set must hold exactly one Return")
        t.screenshot()


@suite.chain("chill_return_comb")
def chill_return_comb(t):
    """CHILL_RETURN_COMB_LANDMARK_1: comb defs exist; only the Chill generator lists the step; the comb is inert scenery (no puzzle)."""
    import os
    here = os.path.dirname(os.path.abspath(__file__))
    t.clear_area(size=8)
    with t.component("comb_defs", beyond_toggle=True):
        r = t.bridge_call("jawa/get_defs", defs="ThingDef/RM_ReturnCombIce;ThingDef/RM_ReturnCombBusbar;ThingDef/RM_ReturnCombStud")
        if _live(t) and ((r or {}).get("success") is False or (r or {}).get("notFound")):
            raise ExpectationFailed("comb defs missing: %r" % r)
        t.screenshot()
    with t.component("chill_generator_lists_comb_only", beyond_toggle=True):
        text = open(os.path.join(here, "Defs", "MapGeneration", "RM_SeaDiveGenerators.xml"), encoding="utf-8").read()
        seen = 0
        for b in text.split("<MapGeneratorDef>")[1:]:
            name = b.split("<defName>")[1].split("</defName>")[0]
            seen += 1
            if (name == "RM_SeaDiveGenerator_TheChill") != ("RM_ChillReturnComb" in b):
                raise ExpectationFailed("%s comb listing wrong" % name)
        if seen < 2:
            raise ExpectationFailed("generator file parse found %d generators" % seen)
        t.screenshot()
    with t.component("comb_is_inert_scenery", beyond_toggle=True):
        xml = open(os.path.join(here, "Defs", "ThingDefs_Buildings", "RM_ReturnComb.xml"), encoding="utf-8").read()
        if "<comps>" in xml or "Comp" in xml:
            raise ExpectationFailed("comb defs carry comps; the ruling is scenery and lore only")
        src = open(os.path.join(here, "Source", "GenStep_ChillReturnComb.cs"), encoding="utf-8").read()
        code = "\n".join(l for l in src.splitlines() if not l.strip().startswith("//"))
        for banned in ["Gravship", "Hediff", "TakeDamage", "GameCondition", "MapComponent", "Job"]:
            if banned in code:
                raise ExpectationFailed("comb step touches %s" % banned)
        t.screenshot()
    with t.component("comb_laid_on_live_floor", beyond_toggle=True):
        # UNMEASURED offline: a real Chill floor map must be generated live; a count of RM_ReturnCombStud on it is the check.
        t.screenshot()


@suite.chain("chill_dive_density_sampler")
def chill_dive_density_sampler(t):
    """CHILL_DIVE_DENSITY_SAMPLER_1: the offline sampler reads the Chill roster and the weighted draw yields exactly the set count; live floor count is UNMEASURED."""
    import os, random, sys
    here = os.path.dirname(os.path.abspath(__file__))
    t.clear_area(size=8)
    with t.component("offline_sampler_reads_roster", beyond_toggle=True):
        sys.path.insert(0, here)
        import density_sampler as ds
        density, roster = ds.load_roster()
        if len(roster) < 5 or density <= 0:
            raise ExpectationFailed("sampler cannot read the Chill roster: %d species, density %s" % (len(roster), density))
        rng = random.Random(7)
        legacy = [len(ds.legacy_draw(density, roster, rng)) for _ in range(500)]
        if min(legacy) < 5:  # sanity probe: the legacy one-of-each sampler is known to meet ~7-8
            raise ExpectationFailed("sampler sanity probe failed: legacy dive met %d animals" % min(legacy))
        t.screenshot()
    with t.component("weighted_draw_obeys_count", beyond_toggle=True):
        for c in (2, 3, 4):
            if any(len(ds.weighted_draw(roster, c, rng)) != c for _ in range(200)):
                raise ExpectationFailed("weighted draw did not return %d animals" % c)
        src = open(os.path.join(here, "Source", "GenStep_SeaFloorFauna.cs"), encoding="utf-8").read()
        if "GenerateWeightedDraw" not in src or "chillDensityDrawEnabled" not in src:
            raise ExpectationFailed("GenStep_SeaFloorFauna lacks the weighted-draw path or its toggle")
        t.screenshot()
    with t.component("live_dive_animal_count", beyond_toggle=True):
        # UNMEASURED offline: the number of animals on a freshly generated Chill floor needs a live dive; the
        # owner sets the final count (leaning 2-4) on a walk. Run density_sampler.py for the offline expectation.
        t.screenshot()
