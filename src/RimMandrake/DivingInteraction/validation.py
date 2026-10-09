"""validation.py -- modcheck suite for DivingInteraction (mandrake.rm.divinginteraction).

First script for this mod; covers SEABED_PER_SEA_FLOORS_1 only: each terminal sea's surface
biome must carry RM_SeabedAccessExtension.floorBiome naming its own RM_SeabedFloor_<Sea>
biome (Patches/RM_SeabedFloorBiomeWiring.xml). Pure def-state check; no live run recorded yet.
"""
# DIVINGINTERACTION_COVERAGE_GAPS_1: the `toggle_gates` chain below asserts that each of the eleven
# Mod Settings toggles gates its behaviour in source and flips live. UNCOVERED on purpose:
# RM_SeaDiveHatch enter/descent (retired, SEA_DIVE_HATCH_RETIRE_1). UNMEASURED: live floor content and
# floor animal count off the Grey: chain grey_floor_is_a_place generates a floor map directly (layer=, 2026-10-06).
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
                          fields="modExtensions", deep=True)     # without deep=True get_defs returns the extensions as bare type names
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


@suite.chain("seabed_floor_generators")
def seabed_floor_generators(t):
    """SEABED_FLOOR_GENERATORS_1: each floor biome names a layer generator carrying its hatch twin's content, with no exit."""
    import os, xml.etree.ElementTree as ET
    here = os.path.dirname(os.path.abspath(__file__))
    t.clear_area(size=8)

    def gens(name):
        root = ET.parse(os.path.join(here, "Defs", "MapGeneration", name)).getroot()
        return {d.findtext("defName"): d for d in root.findall("MapGeneratorDef")}

    with t.component("floor_biomes_name_layer_generators", beyond_toggle=True):
        root = ET.parse(os.path.join(here, "Defs", "PlanetLayerDefs", "RM_SeabedFloorBiomes.xml")).getroot()
        named = {b.findtext("defName"): b.findtext("modExtensions/li/generator") for b in root.findall("BiomeDef")}
        layer = gens("RM_SeabedGenerators.xml")
        bad = [f for f in SEAS.values() if named.get(f) not in layer]
        if bad:
            raise ExpectationFailed("floor biomes without a layer generator: %s" % bad)
        t.screenshot()
    with t.component("layer_generators_match_hatch_content", beyond_toggle=True):
        hatch, layer = gens("RM_SeaDiveGenerators.xml"), gens("RM_SeabedGenerators.xml")
        if len(hatch) != 4:  # sanity probe: the instrument must see the four hatch twins
            raise ExpectationFailed("expected 4 hatch generators, read %d" % len(hatch))
        for name, g in layer.items():
            steps = [li.text for li in g.findall("genSteps/li")]
            twin = [li.text for li in hatch[name.replace("RM_SeabedGenerator_", "RM_SeaDiveGenerator_")].findall("genSteps/li")]
            if g.find("pocketMapProperties") is not None or "RM_PlaceSeaDiveExit" in steps:
                raise ExpectationFailed("%s still carries the pocket map or the exit" % name)
            if g.findtext("isUnderground") != "false":
                raise ExpectationFailed("%s would roof the floor in thick rock" % name)
            if steps != [s for s in twin if s != "RM_PlaceSeaDiveExit"]:
                raise ExpectationFailed("%s content drifted from its hatch twin: %s vs %s" % (name, steps, twin))
        t.screenshot()
    with t.component("live_floor_generates_sea_content", beyond_toggle=True):
        # UNMEASURED offline: land a ship on the layer under each sea (needs SEABED_DESCENT_ASCENT_1 or a
        # debug map on a floor tile) and read the generator, vents/gallery/scatters and the sea's cast.
        r = t.bridge_call("jawa/get_defs", defs=";".join(
            "MapGeneratorDef/RM_SeabedGenerator_%s" % s for s in ("TheScald", "GreySea", "TwilightSea", "TheChill")))
        if _live(t) and ((r or {}).get("success") is False or (r or {}).get("notFound")):
            raise ExpectationFailed("layer generators missing live: %r" % r)
        t.screenshot()


@suite.chain("seabed_floor_ambient_carryover")
def seabed_floor_ambient_carryover(t):
    """SEABED_FLOOR_AMBIENT_CARRYOVER_1: layer floors carry the hatch's temperature, flora and refilling cast.

    Learned offline 2026-10-03 (decompile): MapTemperature.OutdoorTemp/SeasonalTemp return
    BiomeDef.constantOutdoorTemperature for any map on that biome, so the floor biome carries the
    temperature. Flora and cast are copied at startup by RM_SeabedFloorLife (the floor XML says 0;
    only a live read of the floor biome shows the copy)."""
    import os, xml.etree.ElementTree as ET
    here = os.path.dirname(os.path.abspath(__file__))
    t.clear_area(size=8)
    with t.component("floor_temperature_matches_hatch", beyond_toggle=True):
        hatch = ET.parse(os.path.join(here, "Defs", "MapGeneration", "RM_SeaDiveGenerators.xml")).getroot()
        pocket = {g.findtext("pocketMapProperties/biome"): g.findtext("pocketMapProperties/temperature")
                  for g in hatch.findall("MapGeneratorDef")}
        floors = ET.parse(os.path.join(here, "Defs", "PlanetLayerDefs", "RM_SeabedFloorBiomes.xml")).getroot()
        const = {b.findtext("defName"): b.findtext("constantOutdoorTemperature") for b in floors.findall("BiomeDef")}
        if len(pocket) != 4 or None in pocket.values():  # sanity probe: the instrument sees four hatch temperatures
            raise ExpectationFailed("expected 4 hatch temperatures, read %r" % pocket)
        bad = {s: (pocket.get(s), const.get(f)) for s, f in SEAS.items()
               if const.get(f) is None or float(const[f]) != float(pocket.get(s))}
        if bad:
            raise ExpectationFailed("floor temperature differs from the hatch's: %r" % bad)
        t.screenshot()
    with t.component("floor_biomes_carry_sea_life", beyond_toggle=False):
        r = t.bridge_call("jawa/get_defs", defs=";".join("BiomeDef/%s" % f for f in SEAS.values()),
                          fields="plantDensity,animalDensity")   # comma: ';' reads as ONE unknown field (MEASURED 2026-10-06)
        if _live(t):
            if (r or {}).get("success") is False or (r or {}).get("notFound"):
                raise ExpectationFailed("floor biome query failed: %r" % r)
            rows = {row.get("defName"): (row.get("fields") or {}) for row in (r or {}).get("defs") or []}
            if len(rows) != len(SEAS):
                raise ExpectationFailed("expected %d floor biome rows, read %d" % (len(SEAS), len(rows)))
            flat = {d: f for d, f in rows.items()
                    if float(f.get("plantDensity") or 0) <= 0 or float(f.get("animalDensity") or 0) <= 0}
            if flat:
                raise ExpectationFailed("floor biome(s) still at zero density live (startup copy off or failed): %r" % flat)
        t.screenshot()
    # Not a component (it would record PASS with nothing asked): UNMEASURED until a Chill layer floor can be made
    # live (SEABED_DESCENT_ASCENT_1 or a debug map on a floor tile): OutdoorTemp ~ -110, Twilight floor plants > 0,
    # a cleared floor's animal count rising over ticks.

SETTINGS_TYPE = "RimMandrake.DivingInteraction.RM_DivingSettings"

# settings field -> the Source files whose behaviour it must gate (each must read masterEnabled beside it)
TOGGLE_GATES = [
    ("greyPoolDefenceEnabled", ["MapComponent_BrineCrystallisation.cs"], "grey_pool_defence_gates_encasement"),
    ("greyPoolSentinelEnabled", ["RM_CompPoolSentinelSquirt.cs"], "grey_pool_sentinel_gates_squirt"),
    ("greyElderDischargeEnabled", ["RM_Building_BrineElder.cs"], "grey_elder_discharge_gates_emp"),
    ("greyElderTradeEnabled", ["RM_Building_BrineElder.cs"], "grey_elder_trade_gates_offer"),
    ("specimenCabinetEnabled", ["RM_SpecimenCabinet.cs"], "specimen_cabinet_gates_display"),
    ("chillFireBanEnabled", ["RM_ChillFireGate.cs"], "chill_fire_ban_gates_flame"),
    ("chillBoilShroudEnabled", ["RM_MapComponent_ChillBoilShroud.cs"], "chill_boil_shroud_gates_flecks"),
    ("chillHeatedSuitEnabled", ["RM_CompHeatedSuitBattery.cs"], "chill_heated_suit_gates_battery"),
    ("chillGardenDefenseEnabled", ["RM_CompTarnnRoused.cs", "RM_MapComponent_ChillGardenDefense.cs"], "chill_garden_defense_gates_fightback"),
    ("chillThermalFootprintsEnabled", ["RM_MapComponent_ChillFootprints.cs"], "chill_footprints_gate_deposits"),
    ("chillDrownedAuroraEnabled", ["Patch_ChillDrownedAurora.cs", "RM_MapComponent_ChillDrownedAurora.cs"], "chill_drowned_aurora_gates_glow"),
    ("chillAuroraSurgeEnabled", ["RM_MapComponent_ChillAuroraSurge.cs", "RM_CompPowerPlantAuroraSurge.cs"], "chill_aurora_surge_gates_storm"),
]
suite.toggles = [f for f, _, _ in TOGGLE_GATES]


def _gated_source(here, fname, field):
    """Every read of `field` in the file (comments stripped) must sit beside masterEnabled and either
    early-return when off or be part of an && enable expression. Returns the number of gate sites."""
    import os
    text = open(os.path.join(here, "Source", fname), encoding="utf-8").read()
    lines = [l for l in text.splitlines() if not l.strip().startswith("//")]
    sites = 0
    for i, l in enumerate(lines):
        if "DivingSettings." + field not in l:
            continue
        sites += 1
        near = "\n".join(lines[max(0, i - 1):i + 1])
        if "masterEnabled" not in near:
            raise ExpectationFailed("%s: %s read without masterEnabled beside it (line %d)" % (fname, field, i))
        if "!RM_DivingSettings." + field in l:
            win = "\n".join(lines[i:i + 4])
            # an exit guard, or an expression the off arm short-circuits (IsCharged: off reads "always full")
            if "return" not in win and "yield break" not in win and "||" not in l.split("!RM_DivingSettings." + field, 1)[1]:
                raise ExpectationFailed("%s: !%s is not followed by an early exit" % (fname, field))
        elif "&&" not in near:
            raise ExpectationFailed("%s: %s read is neither an exit guard nor an && enable" % (fname, field))
    return sites


@suite.chain("toggle_gates")
def toggle_gates(t):
    """One component per Mod Settings toggle: the setting really gates its behaviour (source guard with an
    off arm that exits) and the field can be flipped off and restored live. Behaviour under the off arm on a
    live Chill/Grey floor is UNMEASURED: no bridge tool lands a ship on a seabed layer."""
    import os
    here = os.path.dirname(os.path.abspath(__file__))
    t.clear_area(size=8)
    for field, files, cname in TOGGLE_GATES:
        with t.component(cname, toggle=field):
            sites = sum(_gated_source(here, f, field) for f in files)
            if sites < len(files):
                raise ExpectationFailed("%s: expected a gate in each of %s, found %d site(s)" % (field, files, sites))
            if _live(t):
                t.set_setting(SETTINGS_TYPE, {field: "False"})
                t.set_setting(SETTINGS_TYPE, {field: "True"})
            t.screenshot()
    with t.component("chill_fire_gate_is_wired_into_vanilla_fire", beyond_toggle=True):
        pc = open(os.path.join(here, "Source", "Patch_ChillFireBan.cs"), encoding="utf-8").read()
        if "HarmonyPatch" not in pc or "RM_ChillFireGate" not in pc:
            raise ExpectationFailed("Patch_ChillFireBan no longer routes vanilla fire through RM_ChillFireGate")
        t.screenshot()
    with t.component("sentinel_and_pool_share_one_consequence", beyond_toggle=True):
        sq = open(os.path.join(here, "Source", "RM_CompPoolSentinelSquirt.cs"), encoding="utf-8").read()
        if "BrineEncasementUtility" not in sq:
            raise ExpectationFailed("orruhmu squirt no longer encases through BrineEncasementUtility")
        t.screenshot()
    with t.component("live_floor_content_and_animal_count", beyond_toggle=True):
        raise ExpectationFailed("UNMEASURED: no bridge tool lands a ship on a seabed layer to read live floor content or animal count")


# Every def this mod ships is loaded and its label is what its XML says (NORTHSTAR_PARTIAL_GAPS_FILL_1;
# sea-floor layer, biomes, map generators). The Defs/ parse is the list, so a def added later is covered with no edit here.
from modcheck import shipped_defs  # noqa: E402
shipped_defs.add_chain(suite, __file__, sanity=('RM_SeaFloorTerrain', 'RM_ProbeGalleryOutlet'), min_count=50)


# GREYSEA_FLOOR_PASS_1 / SEABED_PER_SEA_FLOORS_1: the Grey Sea floor is a PLACE. A floor map is generated straight
# on the RM_SeabedLayer (jawa/world_tile_map_generate layer=, 2026-10-06), its tile set to the Grey floor biome
# so an unpainted planet still checks out (planet painting is last, CLAUDE.md), and the map is censused for the
# sea's signature: salt pillars + domes + crystals from its scatter GenSteps, its ruled flora, its cast.
GREY_SCATTER = ("RM_SaltPillar", "RM_SaltDome", "RM_SaltChimney", "RM_GreatSaltCrystal_White",
                "RM_GreatSaltCrystal_Pink", "RM_GreatSaltCrystal_Amber", "RM_GreatSaltCrystal_Violet")


class _ToolTooOld(Exception):
    """The deployed companion DLL predates the layer= parameter: an environment fact, so UNMEASURED."""
    is_surprise_abort = True
    kind = "tool-too-old"

    def summary(self):
        return {"evidence": []}


def _roster(kind):
    import os, re
    here = os.path.dirname(os.path.abspath(__file__))
    b = open(os.path.join(here, "..", "TerminalBiomes", "Defs", "BiomeDefs", "RM_GreySea.xml"), encoding="utf-8").read()
    m = re.search(r"<%s>(.*?)</%s>" % (kind, kind), b, re.S)
    return re.findall(r"<(\w+)[^>]*>[\d.]+</\1>", m.group(1)) if m else []


@suite.chain("grey_floor_is_a_place")
def grey_floor_is_a_place(t):
    """A map made on the Grey Sea's floor tile runs the Grey generator and shows pillars, flora and cast."""
    plants, cast = _roster("wildPlants"), _roster("wildAnimals")
    with t.component("grey_roster_read_offline", beyond_toggle=True):
        # sanity probe: the instrument sees the ruled roster (16 plants, 17 animals on 2026-10-06)
        if len(plants) < 10 or len(cast) < 10 or "RM_Fessk" not in cast:
            raise ExpectationFailed("RM_GreySea roster misread: %d plants, %d animals" % (len(plants), len(cast)))
    state = {}
    with t.component("grey_floor_map_generates", beyond_toggle=True):
        if _live(t):
            g = None
            for tile in range(1000, 1400, 37):      # first tile on the layer with no map yet
                d = t.bridge_call("jawa/world_tile_map_generate", tile=tile, layer="RM_SeabedLayer",
                                  biome="RM_SeabedFloor_GreySea", sizeX=120, sizeZ=120, dryRun=True) or {}
                if "layer" not in d:
                    raise _ToolTooOld("world_tile_map_generate has no layer= (deployed DLL older than 2026-10-06)")
                if d.get("success") and not d.get("wasAlreadyGenerated"):
                    g = t.bridge_call("jawa/world_tile_map_generate", tile=tile, layer="RM_SeabedLayer",
                                      biome="RM_SeabedFloor_GreySea", sizeX=120, sizeZ=120) or {}
                    break
            if not g or g.get("success") is not True:
                raise ExpectationFailed("no Grey floor map generated: %r" % (g or "no free tile in 1000..1400"))
            if (g.get("biome"), g.get("mapGenerator")) != ("RM_SeabedFloor_GreySea", "RM_SeabedGenerator_GreySea"):
                raise ExpectationFailed("floor map is %s / %s, not the Grey floor" % (g.get("biome"), g.get("mapGenerator")))
            if (g.get("mapFinalize") or {}).get("failedSteps"):
                raise ExpectationFailed("map finalize failed: %r" % g["mapFinalize"]["failedSteps"])
            sc = t.bridge_call("jawa/set_current_map", mapId=g["mapIndex"]) or {}
            if sc.get("success") is not True:
                raise ExpectationFailed("set_current_map refused: %r" % sc)
            state["map"] = g["mapIndex"]
        t.screenshot()

    def census(defs, pawns=False):
        r = t.bridge_call("jawa/list_things", defName=",".join(defs), includePawns=pawns, limit=2000) or {}
        if r.get("success") is False or not r.get("scanned"):
            raise ExpectationFailed("census could not ask (scanned=%r): %r" % (r.get("scanned"), r.get("message")))
        got = {}
        for th in r.get("things") or []:
            got[th.get("def")] = got.get(th.get("def"), 0) + 1
        return got, r
    with t.component("grey_floor_has_pillars_and_crystals", beyond_toggle=True):
        if _live(t) and "map" in state:
            got, r = census(GREY_SCATTER)
            if not got.get("RM_SaltPillar"):
                raise ExpectationFailed("no salt pillars on the Grey floor (the navigation system): %r" % got)
            crystals = [d for d in GREY_SCATTER if "Crystal" in d and got.get(d)]
            if len(crystals) < 2:
                raise ExpectationFailed("fewer than two crystal colours on the floor: %r" % got)
    with t.component("grey_floor_grows_its_flora", beyond_toggle=True):
        if _live(t) and "map" in state:
            got, _ = census(plants)
            if len(got) < 3:
                raise ExpectationFailed("only %d of %d ruled Grey plants on the floor: %r" % (len(got), len(plants), got))
    with t.component("grey_floor_carries_its_cast", beyond_toggle=True):
        if _live(t) and "map" in state:
            got, _ = census(cast, pawns=True)
            if not got:
                raise ExpectationFailed("none of the %d Grey cast spawned on the floor map" % len(cast))
            strays = t.bridge_call("jawa/list_pawns", limit=2000) or {}
            alien = sorted({p.get("def") for p in strays.get("pawns") or []
                            if not p.get("hasGenes") and p.get("def") not in cast})
            if alien:
                raise ExpectationFailed("animals from outside the Grey cast on its floor: %s" % alien[:8])
    with t.component("grey_floor_returns_home", beyond_toggle=True):
        if _live(t) and "map" in state:      # Find.Maps[0] is the home map on every test world
            r = t.bridge_call("jawa/set_current_map", mapId=0) or {}
            if r.get("success") is not True:
                raise ExpectationFailed("could not return to map 0: %r" % r)
