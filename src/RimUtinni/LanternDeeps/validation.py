"""validation.py -- modcheck suite for RimUtinni Lantern Deeps
(mandrake.rut.lanterndeeps).

Run with:

    python.exe src/RimMandrake/Utils/modcheck/cli.py run LanternDeeps

GROUNDING, read whole before writing this: `Source/LanternDeepsMod.cs`
(MOD_OPTIONS_RETROFIT_1 -- 3 boolean toggles + 3 float multipliers, all
`public static`, per its own comment); `Source/GenStep_ScatterCavePortal.cs`
and `Source/GenStep_ScatterMineshaftPortal.cs` (both extend vanilla
`GenStep_ScatterGroup`; both self-gate through
`LanternDeepsSettings.IsEntranceBiome`, a Mod Setting list
(DEEP_ENTRANCE_BIOMES_SETTING_1) whose DEFAULT is `BiomeGRimond`,
`RUT_NightsideIce`, `RUT_PropaneLake` -- `QUALIFYING_BIOMES` below is that
default, read from `UtinniDefaultEntranceBiomes` in `LanternDeepsMod.cs`, and
holds only while the runner's settings file carries no other list);
`Source/MapComponent_LanternDeepDarkness.cs` (the darkness
mechanic, scoped to Lantern Deep pocket maps only via
`customMapComponents`); and all 4 `Defs/**/*.xml` + both patch files.

TOGGLE-ORDER FACT THAT MAKES ONE CHAIN POSSIBLE WITHOUT A SPECIAL BIOME:
`GenStep_ScatterCavePortal.Generate()`'s own code checks
`LanternDeepsSettings.emergenceEnabled` FIRST, before the biome check, before
the chance roll. So `emergenceEnabled=false` guarantees zero scatter on ANY
map, qualifying biome or not -- a genuine behavioral proof of the toggle that
needs no biome control at all. Same order in
`GenStep_ScatterMineshaftPortal.Generate()` for `mineshaftEnabled`.
`darknessMechanicEnabled` has no such escape: `CheckAmbientLight` only ever
runs inside an already-generated Lantern Deep pocket map, and per the walk
doc's own step 9, "no bridge tool opens a MapPortal or generates a pocket
map directly" -- so that toggle gets a set+readback only, same register
StructureInjections' `enabled_toggle_flips` uses for its own unreachable
toggle.

BIOME-GATE COVERAGE IS DYNAMIC, NOT ASSUMED: the walk doc's own `list: full`
line says proving the POSITIVE scatter (walk step 6) needs a quicktest map
already on `RUT_NightsideIce`/`RUT_PropaneLake`/`BiomeGRimond`, which this
suite has no tool to force (no bridge verb sets a map's biome after the fact
-- confirmed absent from `skills/rimbridge/SKILL.md`'s own tool inventory).
`biome_gate_on_current_map` therefore reads `jawa/map_info`'s own `biome`
field FIRST and branches: on the (overwhelmingly likely) non-qualifying
default quicktest biome it proves the walk's step 7 (negative gate); on the
rare chance the runner's quicktest map lands on a qualifying biome, it
proves step 6 instead (positive scatter). Either branch is a real assertion,
never a skip -- but only one of the two claims gets proven on any given run,
which this suite records in its own detail string.

Still not proven / structurally offline-only:
  1. `jawa/run_genstep` (JawaBenchGenTools2.cs, marked "high risk" in its own
     tool roster comment) has never been called by ANY validation.py suite
     in this repo before this one -- first live use, exact response shape
     unconfirmed.
  2. `jawa/get_defs(..., deep=True)` on nested paths (`portal.
     pocketMapGenerator`, `pocketMapProperties.biome`, `genStep`'s own Class
     type name) carries the same unconfirmed-reflection-path gap already
     flagged in JawaVoice/Droidworks/KotORBandolierNorthFix's own suites --
     not new here, but real.
  3. `darknessMechanicEnabled`/`darknessThresholdMultiplier` get set+readback
     only -- `CheckAmbientLight`'s actual light-draws-predator mechanism
     needs a live Lantern Deep pocket map (walk step 9's own human pass),
     which nothing in this suite can generate.
  4. `GenStep_ScatterMineshaftPortal`'s corpse+rubble dressing
     (`DressRuinedMineshaft`) is checked only for the mineshaft PORTAL
     itself scattering; the AncientSoldier corpse and Filth_RubbleRock
     dressing are read back as a bonus count, not independently gated --
     if the portal scatters but `CellFinder.TryFindRandomCellNear` fails
     every dressing attempt (crowded quicktest map), that failure mode is
     invisible to this suite (the .cs itself treats it as a silent
     non-fatal continue, per its own comments).
  5. Walk step 9 (human pass: enter a scattered geode, confirm the pocket
     map generates as a crystal cavern, test the seal command) is
     explicitly out of scope for a scripted suite.
"""
from modcheck import Suite, ExpectationFailed

suite = Suite("LanternDeeps")
suite.toggles = ["emergenceEnabled", "mineshaftEnabled", "darknessMechanicEnabled",
                 "emergenceChanceMultiplier", "mineshaftChanceMultiplier",
                 "darknessThresholdMultiplier"]

SETTINGS_TYPE = "RimMandrake.Utinni.LanternDeeps.LanternDeepsSettings"
QUALIFYING_BIOMES = {"BiomeGRimond", "RUT_NightsideIce", "RUT_PropaneLake"}
EMERGENCE_SCATTER = "RUT_LanternDeepEmergence_Scatter"
MINESHAFT_SCATTER = "RUT_LanternDeepMineshaft_Scatter"
EMERGENCE_THING = "RUT_LanternDeepEmergence"
MINESHAFT_THING = "RUT_LanternDeepMineshaft"

BOOT_ERROR_NEEDLES = [
    "Config error in mandrake.rut.lanterndeeps",
    "RUT_LanternDeepEmergence.xml", "RUT_LanternDeepGenerator.xml",
    "RUT_LanternDeepEmergence_Scatter.xml",
    "RUT_LanternDeepEmergence_MapGenPatch.xml",
]
EXCEPTION_NEEDLES = ["GenStep_ScatterCavePortal", "RimMandrake.Utinni.LanternDeeps"]


def _get_field(t, def_type, def_name, field):
    return t.bridge_call("jawa/get_defs", defs="%s/%s" % (def_type, def_name),
                         fields=field, deep=True)


def _count(t, defName):
    r = t.bridge_call("jawa/list_things", defName=defName)
    return len((r or {}).get("things") or [])


@suite.chain("load_clean")
def load_clean(t):
    """Walk step 1: no config/XML error naming this mod or any of its 4
    def/patch files."""
    with t.component("no_config_or_xml_errors", beyond_toggle=True):
        r = t.bridge_call("jawa/drain_log", limit=400, errorsOnly=True)
        msgs = [m.get("text", "") for m in ((r or {}).get("messages") or [])]
        joined = "\n".join(msgs)
        hits = [n for n in BOOT_ERROR_NEEDLES if n in joined]
        if hits:
            raise ExpectationFailed(
                "error log contains LanternDeeps-related needle(s) %r: %r"
                % (hits, msgs))


@suite.chain("defs_resolve_as_documented")
def defs_resolve_as_documented(t):
    """Walk steps 2-5: every field the module docstring/walk doc claims,
    read back live rather than assumed from the XML on disk."""
    with t.component("emergence_thingdef_fields", beyond_toggle=True):
        r = t.bridge_call("jawa/get_defs", defs="ThingDef/%s" % EMERGENCE_THING,
                          fields="thingClass")
        if not r or "MapPortal" not in str(r):
            raise ExpectationFailed(
                "ThingDef/%s thingClass did not read back as MapPortal: %r"
                % (EMERGENCE_THING, r))
        portal = _get_field(t, "ThingDef", EMERGENCE_THING, "portal")
        for needle in ("RUT_LanternDeepGenerator", "CaveExit", "66"):
            if needle not in str(portal):
                raise ExpectationFailed(
                    "ThingDef/%s portal block missing expected %r: %r"
                    % (EMERGENCE_THING, needle, portal))

    with t.component("generator_mapgen_fields", beyond_toggle=True):
        r = t.bridge_call("jawa/get_defs",
                          defs="MapGeneratorDef/RUT_LanternDeepGenerator",
                          fields="isUnderground,forceCaves")
        if not r or "True" not in str(r).replace("true", "True"):
            raise ExpectationFailed(
                "RUT_LanternDeepGenerator isUnderground/forceCaves did not "
                "both read back true: %r" % r)
        pmp = _get_field(t, "MapGeneratorDef", "RUT_LanternDeepGenerator",
                         "pocketMapProperties")
        # CAVERNS_PARITY_BUILD_1: the pocket map is donor-free. These two needles
        # were BMT_CrystalCaverns and BMT_CrystalsGenerator; asserting the RUT
        # names is what proves the retirement actually took, so this check is the
        # regression guard against a revert to the donor defs.
        for needle in ("RUT_LanternDeeps", "17"):
            if needle not in str(pmp):
                raise ExpectationFailed(
                    "pocketMapProperties missing expected %r: %r" % (needle, pmp))
        if "BMT_" in str(pmp):
            raise ExpectationFailed(
                "pocketMapProperties still names a Biomes! Caverns def: %r" % pmp)
        gs = _get_field(t, "MapGeneratorDef", "RUT_LanternDeepGenerator", "genSteps")
        if "RUT_LanternstoneFormations" not in str(gs):
            raise ExpectationFailed(
                "RUT_LanternDeepGenerator.genSteps missing "
                "RUT_LanternstoneFormations: %r" % gs)
        if "BMT_" in str(gs):
            raise ExpectationFailed(
                "RUT_LanternDeepGenerator.genSteps still names a Biomes! "
                "Caverns GenStepDef: %r" % gs)

    with t.component("scatter_genstepdef_and_global_patch", beyond_toggle=True):
        r = t.bridge_call("jawa/get_defs",
                          defs="GenStepDef/%s" % EMERGENCE_SCATTER,
                          fields="order,genStep", deep=True)
        blob = str(r)
        if "320" not in blob or "GenStep_ScatterCavePortal" not in blob:
            raise ExpectationFailed(
                "%s order/genStep class did not read back as expected "
                "(order=320, class GenStep_ScatterCavePortal): %r"
                % (EMERGENCE_SCATTER, r))
        base = t.bridge_call("jawa/get_defs",
                             defs="MapGeneratorDef/MapCommonBase",
                             fields="genSteps", deep=True)
        if EMERGENCE_SCATTER not in str(base):
            raise ExpectationFailed(
                "MapCommonBase.genSteps does not contain %s -- the global "
                "PatchOperationAdd may not have landed: %r"
                % (EMERGENCE_SCATTER, base))
        if MINESHAFT_SCATTER not in str(base):
            raise ExpectationFailed(
                "MapCommonBase.genSteps does not contain %s -- the mineshaft "
                "entrance's own global PatchOperationAdd may not have "
                "landed: %r" % (MINESHAFT_SCATTER, base))
        t.screenshot()

    with t.component("mineshaft_genstepdef_fields", beyond_toggle=True):
        r = t.bridge_call("jawa/get_defs",
                          defs="GenStepDef/%s" % MINESHAFT_SCATTER,
                          fields="order,genStep", deep=True)
        blob = str(r)
        if "321" not in blob or "GenStep_ScatterMineshaftPortal" not in blob:
            raise ExpectationFailed(
                "%s order/genStep class did not read back as expected "
                "(order=321, class GenStep_ScatterMineshaftPortal): %r"
                % (MINESHAFT_SCATTER, r))


@suite.chain("emergence_toggle_gates_before_biome")
def emergence_toggle_gates_before_biome(t):
    """Behavioral proof, needs no qualifying biome: `emergenceEnabled=false`
    is checked BEFORE the biome allowlist in `GenStep_ScatterCavePortal.
    Generate()`'s own source, so disabling it must zero out the scatter on
    THIS map regardless of what biome it is. `jawa/run_genstep` is called
    repeatedly (first live use of this bridge verb by any suite -- see
    module docstring gap #1) rather than once, because a single call
    proves nothing if the step's own internal chance roll (independent of
    the toggle) would have failed anyway."""
    with t.component("emergence_disabled_never_scatters", toggle="emergenceEnabled"):
        t.set_setting(SETTINGS_TYPE, {"emergenceEnabled": False})
        before = _count(t, EMERGENCE_THING)
        for _ in range(25):
            t.bridge_call("jawa/run_genstep", genStepDef=EMERGENCE_SCATTER)
        after = _count(t, EMERGENCE_THING)
        t.set_setting(SETTINGS_TYPE, {"emergenceEnabled": True})
        if after != before:
            raise ExpectationFailed(
                "emergenceEnabled=false but %s count went %d -> %d after 25 "
                "run_genstep calls -- the toggle is not gating the scatter"
                % (EMERGENCE_THING, before, after))
        r = t.bridge_call("jawa/drain_log", limit=100, errorsOnly=True)
        msgs = [m.get("text", "") for m in ((r or {}).get("messages") or [])]
        hits = [n for n in EXCEPTION_NEEDLES if any(n in m for m in msgs)]
        if hits:
            raise ExpectationFailed(
                "run_genstep(%s) logged an exception naming %r: %r"
                % (EMERGENCE_SCATTER, hits, msgs))


@suite.chain("biome_gate_on_current_map")
def biome_gate_on_current_map(t):
    """Walk steps 6/7, made dynamic (see module docstring): reads the
    CURRENT quicktest map's own biome and asserts whichever half of the
    biome gate that biome actually exercises. `emergenceEnabled` is
    restored true by the previous chain before this one runs."""
    with t.component("biome_gate_matches_current_map", beyond_toggle=True):
        info = t.bridge_call("jawa/map_info")
        biome = (info or {}).get("biome")
        before = _count(t, EMERGENCE_THING)
        for _ in range(40):
            t.bridge_call("jawa/run_genstep", genStepDef=EMERGENCE_SCATTER)
        after = _count(t, EMERGENCE_THING)
        if biome in QUALIFYING_BIOMES:
            if after <= before:
                raise ExpectationFailed(
                    "current map biome %r IS in the qualifying set but 40 "
                    "run_genstep calls placed nothing (%d -> %d) -- either "
                    "the 8%% roll got unlucky 40 times running, or the "
                    "scatter itself is broken" % (biome, before, after))
            t.screenshot()
        else:
            if after != before:
                raise ExpectationFailed(
                    "current map biome %r is NOT in the qualifying set "
                    "{BiomeGRimond, RUT_NightsideIce, RUT_PropaneLake} but "
                    "%s count went %d -> %d anyway -- the biome gate is not "
                    "excluding this biome" % (biome, EMERGENCE_THING, before, after))
        t._record("biome_gate branch: biome=%r qualifying=%s"
                  % (biome, biome in QUALIFYING_BIOMES), True)


@suite.chain("mineshaft_toggle_gates_before_biome")
def mineshaft_toggle_gates_before_biome(t):
    """Same behavioral escape as `emergence_toggle_gates_before_biome`, for
    the mineshaft entrance (`GenStep_ScatterMineshaftPortal.Generate()`'s
    own code checks `mineshaftEnabled` first, same order as the emergence
    step). Also checks the dressing side-effect count as a bonus, non-
    gating signal (see module docstring gap #4 on why it is not
    independently asserted)."""
    with t.component("mineshaft_disabled_never_scatters", toggle="mineshaftEnabled"):
        t.set_setting(SETTINGS_TYPE, {"mineshaftEnabled": False})
        before = _count(t, MINESHAFT_THING)
        for _ in range(25):
            t.bridge_call("jawa/run_genstep", genStepDef=MINESHAFT_SCATTER)
        after = _count(t, MINESHAFT_THING)
        t.set_setting(SETTINGS_TYPE, {"mineshaftEnabled": True})
        if after != before:
            raise ExpectationFailed(
                "mineshaftEnabled=false but %s count went %d -> %d after 25 "
                "run_genstep calls -- the toggle is not gating the scatter"
                % (MINESHAFT_THING, before, after))
        r = t.bridge_call("jawa/drain_log", limit=100, errorsOnly=True)
        msgs = [m.get("text", "") for m in ((r or {}).get("messages") or [])]
        hits = [n for n in EXCEPTION_NEEDLES if any(n in m for m in msgs)]
        if hits:
            raise ExpectationFailed(
                "run_genstep(%s) logged an exception naming %r: %r"
                % (MINESHAFT_SCATTER, hits, msgs))


@suite.chain("darkness_toggle_flips")
def darkness_toggle_flips(t):
    """Set+readback only, same register StructureInjections' own
    `enabled_toggle_flips` uses -- see module docstring on why
    `CheckAmbientLight` cannot be exercised at all without a live Lantern
    Deep pocket map."""
    with t.component("darkness_setting_flips", toggle="darknessMechanicEnabled"):
        t.set_setting(SETTINGS_TYPE, {"darknessMechanicEnabled": False})
        t.set_setting(SETTINGS_TYPE, {"darknessMechanicEnabled": True})


@suite.chain("chance_multiplier_sliders_flip")
def chance_multiplier_sliders_flip(t):
    """The three float sliders: set+readback only (Droidworks' own
    register -- "sliders are tuning, not independently toggle-tested
    here"). Proving a RATE change would need many sampled map generations,
    out of scope for a smoke suite."""
    with t.component("chance_multiplier_settings_flip", beyond_toggle=True):
        t.set_setting(SETTINGS_TYPE, {"emergenceChanceMultiplier": 2.0})
        t.set_setting(SETTINGS_TYPE, {"emergenceChanceMultiplier": 1.0})
        t.set_setting(SETTINGS_TYPE, {"mineshaftChanceMultiplier": 2.0})
        t.set_setting(SETTINGS_TYPE, {"mineshaftChanceMultiplier": 1.0})
        t.set_setting(SETTINGS_TYPE, {"darknessThresholdMultiplier": 2.0})
        t.set_setting(SETTINGS_TYPE, {"darknessThresholdMultiplier": 1.0})
