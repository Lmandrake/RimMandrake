"""validation.py -- modcheck suite for Lantern Deeps
(mandrake.rm.lanterndeeps).

Run with:

    python.exe src/RimMandrake/Utils/modcheck/cli.py run LanternDeeps

GROUNDING, read whole before writing this: `Source/LanternDeepsMod.cs`
(MOD_OPTIONS_RETROFIT_1, plus LANTERNDEEPS_RM_MOD_BUILD_1's added master
toggle -- 4 boolean toggles + 3 float multipliers, all `public static`, per
its own comment); `Source/GenStep_ScatterCavePortal.cs`
and `Source/GenStep_ScatterMineshaftPortal.cs` (both extend vanilla
`GenStep_ScatterGroup`; both self-gate through
`LanternDeepsSettings.IsEntranceBiome`, a Mod Setting list
(DEEP_ENTRANCE_BIOMES_SETTING_1) whose DEFAULT is `BiomeGRimond`,
`RM_NightsideIce`, `RM_TheChill` -- `QUALIFYING_BIOMES` below is that
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
already on `RM_NightsideIce`/`RM_TheChill`/`BiomeGRimond`, which this
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
import re

from modcheck import Suite, ExpectationFailed

suite = Suite("LanternDeeps")
suite.toggles = ["lanternDeepsEnabled",
                 "emergenceEnabled", "mineshaftEnabled", "darknessMechanicEnabled",
                 "emergenceChanceMultiplier", "mineshaftChanceMultiplier",
                 "darknessThresholdMultiplier", "safeLanternEnabled"]

SETTINGS_TYPE = "RimMandrake.LanternDeeps.LanternDeepsSettings"
# FIX 2026-09-25 (TERMINALBIOMES_RM_MOD_BUILD_1): RUT_NightsideIce/RUT_PropaneLake
# restored alongside their RM_ twins. Those RUT_ defs are FROZEN, not deleted --
# the planet is painted ONCE at the end (BIOME_PAINT_ONCE_AT_THE_END_1) -- and
# still carry every live Ash'karr tile today; the RM_ twins sit at 0 tiles. A
# QUALIFYING_BIOMES set missing the RUT_ names would read every real-world
# entrance as non-qualifying.
QUALIFYING_BIOMES = {"BiomeGRimond", "RUT_NightsideIce", "RM_NightsideIce",
                      "RUT_PropaneLake", "RM_TheChill"}
EMERGENCE_SCATTER = "RM_LanternDeepEmergence_Scatter"
MINESHAFT_SCATTER = "RM_LanternDeepMineshaft_Scatter"
EMERGENCE_THING = "RM_LanternDeepEmergence"
MINESHAFT_THING = "RM_LanternDeepMineshaft"

BOOT_ERROR_NEEDLES = [
    "Config error in mandrake.rm.lanterndeeps",
    "RM_LanternDeepEmergence.xml", "RM_LanternDeepGenerator.xml",
    "RM_LanternDeepEmergence_Scatter.xml",
    "RM_LanternDeepEmergence_MapGenPatch.xml",
]
EXCEPTION_NEEDLES = ["GenStep_ScatterCavePortal", "RimMandrake.LanternDeeps"]


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


def _genstep_read(t, def_name, order, xml_file, cls):
    """GenStepDef order read live; the genStep CLASS asserted from the shipped XML. jawa/get_defs shows a GenStep as
    its FIELDS and never names its class, so 'class name in the reply' FAILED loaded, correct defs (load 13). The live
    half still proves the def resolved with a non-null genStep object -- an unresolvable Class= discards the whole def."""
    import os as _o
    path = _o.path.join(_o.path.dirname(_o.path.abspath(__file__)), "Defs", "MapGeneration", xml_file)
    if 'Class="RimMandrake.LanternDeeps.%s"' % cls not in open(path, encoding="utf-8").read():
        raise ExpectationFailed("%s no longer names RimMandrake.LanternDeeps.%s" % (xml_file, cls))
    r = t.bridge_call("jawa/get_defs", defs="GenStepDef/%s" % def_name, fields="order,genStep", deep=True)
    if t._guard():
        rows = (r or {}).get("defs") or []
        f = (rows[0].get("fields") or {}) if rows else {}
        if (r or {}).get("notFound") or float(f.get("order") or -1) != float(order) or not isinstance(f.get("genStep"), dict):
            raise ExpectationFailed("%s did not read back loaded with order=%s and a genStep object: %r" % (def_name, order, r))
    return r


@suite.chain("defs_resolve_as_documented")
def defs_resolve_as_documented(t):
    """Walk steps 2-5: every field the module docstring/walk doc claims,
    read back live rather than assumed from the XML on disk."""
    with t.component("emergence_thingdef_fields", beyond_toggle=True):
        # jawa/get_defs cannot read System.Type fields ('(no such field)'); jawa/get_def carries thingClass under extra.
        r = t.bridge_call("jawa/get_def", defType="ThingDef", defName=EMERGENCE_THING)
        if not r or "MapPortal" not in str(((r or {}).get("extra") or {}).get("thingClass")):
            raise ExpectationFailed(
                "ThingDef/%s thingClass did not read back as MapPortal: %r"
                % (EMERGENCE_THING, r))
        portal = _get_field(t, "ThingDef", EMERGENCE_THING, "portal")
        for needle in ("RM_LanternDeepGenerator", "CaveExit", "66"):
            if needle not in str(portal):
                raise ExpectationFailed(
                    "ThingDef/%s portal block missing expected %r: %r"
                    % (EMERGENCE_THING, needle, portal))

    with t.component("generator_mapgen_fields", beyond_toggle=True):
        r = t.bridge_call("jawa/get_defs",
                          defs="MapGeneratorDef/RM_LanternDeepGenerator",
                          fields="isUnderground,forceCaves")
        if not r or "True" not in str(r).replace("true", "True"):
            raise ExpectationFailed(
                "RM_LanternDeepGenerator isUnderground/forceCaves did not "
                "both read back true: %r" % r)
        pmp = _get_field(t, "MapGeneratorDef", "RM_LanternDeepGenerator",
                         "pocketMapProperties")
        # CAVERNS_PARITY_BUILD_1: the pocket map is donor-free. These two needles
        # were BMT_CrystalCaverns and BMT_CrystalsGenerator; asserting the RUT
        # names is what proves the retirement actually took, so this check is the
        # regression guard against a revert to the donor defs.
        for needle in ("RM_LanternDeeps", "17"):
            if needle not in str(pmp):
                raise ExpectationFailed(
                    "pocketMapProperties missing expected %r: %r" % (needle, pmp))
        if "BMT_" in str(pmp):
            raise ExpectationFailed(
                "pocketMapProperties still names a Biomes! Caverns def: %r" % pmp)
        gs = _get_field(t, "MapGeneratorDef", "RM_LanternDeepGenerator", "genSteps")
        if "RM_LanternstoneFormations" not in str(gs):
            raise ExpectationFailed(
                "RM_LanternDeepGenerator.genSteps missing "
                "RM_LanternstoneFormations: %r" % gs)
        if "BMT_" in str(gs):
            raise ExpectationFailed(
                "RM_LanternDeepGenerator.genSteps still names a Biomes! "
                "Caverns GenStepDef: %r" % gs)

    with t.component("scatter_genstepdef_and_global_patch", beyond_toggle=True):
        _genstep_read(t, EMERGENCE_SCATTER, 320, "RM_LanternDeepEmergence_Scatter.xml", "GenStep_ScatterCavePortal")
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
        _genstep_read(t, MINESHAFT_SCATTER, 321, "RM_LanternDeepMineshaft_Scatter.xml", "GenStep_ScatterMineshaftPortal")


@suite.chain("master_toggle_gates_before_per_mechanic")
def master_toggle_gates_before_per_mechanic(t):
    """LANTERNDEEPS_RM_MOD_BUILD_1's added master toggle: `lanternDeepsEnabled=false`
    is checked FIRST in both GenStep_ScatterCavePortal.Generate() and
    GenStep_ScatterMineshaftPortal.Generate(), before either's own per-mechanic
    toggle -- same behavioral-proof shape as emergence/mineshaft's own toggles
    below, needs no qualifying biome."""
    with t.component("master_disabled_neither_entrance_scatters", toggle="lanternDeepsEnabled"):
        t.set_setting(SETTINGS_TYPE, {"lanternDeepsEnabled": False})
        before_e = _count(t, EMERGENCE_THING)
        before_m = _count(t, MINESHAFT_THING)
        for _ in range(25):
            t.bridge_call("jawa/run_genstep", genStepDef=EMERGENCE_SCATTER)
            t.bridge_call("jawa/run_genstep", genStepDef=MINESHAFT_SCATTER)
        after_e = _count(t, EMERGENCE_THING)
        after_m = _count(t, MINESHAFT_THING)
        t.set_setting(SETTINGS_TYPE, {"lanternDeepsEnabled": True})
        if after_e != before_e or after_m != before_m:
            raise ExpectationFailed(
                "lanternDeepsEnabled=false but counts moved (emergence %d -> %d, "
                "mineshaft %d -> %d) after 25 run_genstep calls each -- the "
                "master toggle is not gating both entrances"
                % (before_e, after_e, before_m, after_m))


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
        # jawa/map_info has no top-level "biome" key -- JawaBenchMapInfoTools.cs
        # returns tileInfo.biome (the world tile's PrimaryBiome) and the separate
        # top-level mapBiome (what the map actually generated as, which is what
        # this chain needs post-generation). The old key read None on every
        # call, so this branch never once took the qualifying-biome path.
        biome = (info or {}).get("mapBiome")
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
                    "{BiomeGRimond, RM_NightsideIce, RM_TheChill} but "
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


@suite.chain("lantern_defs_and_toggle")
def lantern_defs_and_toggle(t):
    """LANTERNDEEPS_LANTERN_LIGHT_BUILD_1: the Lantern plant loaded (a def with an unresolvable field is silently
    discarded) and its safe-light toggle flips. The exclusion itself needs a live Deep with a colonist standing
    in Lantern-only light (exposure is a private field): joint session, UNMEASURED here."""
    with t.component("lantern_def_loaded", beyond_toggle=True):
        r = t.bridge_call("jawa/get_defs", defs="ThingDef/RM_Lantern")
        if t._guard() and (not r or not r.get("success") or r.get("foundCount") != 1):
            raise ExpectationFailed("RM_Lantern did not load: %r" % (r,))
    with t.component("safe_lantern_setting_flips", toggle="safeLanternEnabled"):
        t.set_setting(SETTINGS_TYPE, {"safeLanternEnabled": False})
        t.set_setting(SETTINGS_TYPE, {"safeLanternEnabled": True})


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


@suite.chain("fauna_residents_loaded")
def fauna_residents_loaded(t):
    """LANTERNDEEPS_FAUNA_TIER_PORT_BUILD_1 (Q12): the eight RM_ residents loaded (a def with an unresolvable
    field is silently discarded) and RM_LanternDeeps names all eight. Whether light draws one is the darkness
    walk, not this chain. A false theory worth keeping: the old RSW_ rows were patch-added, so reading the
    BiomeDef alone showed an EMPTY roster; it is inline now."""
    kinds = ["BloodropMoth", "GlowSlug", "BovineBeetle", "FacetMothLarvae",
             "Gembug", "Megapleura", "MossBeetleLarvae", "ShatterjawBeetle"]
    with t.component("fauna_kinds_loaded", beyond_toggle=True):
        for k in kinds:
            r = t.bridge_call("jawa/get_defs", defs="PawnKindDef/RM_%s" % k)
            if t._guard() and (not r or not r.get("success") or r.get("foundCount") != 1):
                raise ExpectationFailed("PawnKindDef/RM_%s did not load: %r" % (k, r))
    with t.component("biome_roster_inline", beyond_toggle=True):
        # LIVE 2026-10-03: get_defs renders a BiomeAnimalRecord WITHOUT the animal's name, so a name search over it reads every
        # row missing. jawa/biome_probe lists the resolved roster by defName.
        r = t.bridge_call("jawa/biome_probe", biomes="RM_LanternDeeps", animals=True, limit=100)
        brows = (((r or {}).get("biomes") or [{}])[0].get("animals") or []) if isinstance(r, dict) else []
        names = set(a.get("defName") for a in brows)
        miss = [k for k in kinds if "RM_" + k not in names]
        if t._guard() and not names:
            raise ExpectationFailed("biome_probe returned no roster for RM_LanternDeeps: %r" % (r,))
        if t._guard() and miss:
            raise ExpectationFailed("RM_LanternDeeps roster missing %r (live roster: %s)" % (miss, sorted(names)))


@suite.chain("lanternstone_deep_gate_toggle")
def lanternstone_deep_gate_toggle(t):
    """MINERAL_BIOME_LEAKS_1: set+readback only for the gate. Proving the gate needs a deep-scanner pick on a
    non-Deeps map, which is a random weighted draw and not drivable offline (UNMEASURED live)."""
    with t.component("lanternstone_deep_gate_setting_flips", toggle="lanternstoneDeepGateEnabled"):
        t.set_setting(SETTINGS_TYPE, {"lanternstoneDeepGateEnabled": False})
        t.set_setting(SETTINGS_TYPE, {"lanternstoneDeepGateEnabled": True})


@suite.chain("working_dead")
def working_dead(t):
    """LANTERNDEEPS_WORKING_DEAD_BUILD_1: the well-provisioned dead, the Shard-minds and the Working Dead.
    Run on a LANTERN DEEP map (current map). ProofPlace runs the real placement with both halves on; every
    chassis placed around a Shard-mind must then STAND after one ProofAnimate pass. Not proven here: that a
    freshly generated Deep carries them (genSteps wiring) -- enter a new Deep and count RM_ShardMind; and the
    droid stop, which needs a player droid in range (ProofPull, then read the droid's job report)."""
    WD = "RimMandrake.LanternDeeps.RM_WorkingDeadProof"
    with t.component("working_dead_defs_loaded", beyond_toggle=True):
        for d in ("ThingDef/RM_WorkingDead", "ThingDef/RM_ShardMind", "JobDef/RM_ListenToShardMind",
                  "GenStepDef/RM_DeepWellProvisionedDead"):
            r = t.bridge_call("jawa/get_defs", defs=d)
            if t._guard() and (not r or not r.get("success") or r.get("foundCount") != 1):
                raise ExpectationFailed("def did not load: %s -> %r" % (d, r))
    with t.component("well_provisioned_dead_placed", toggle="wellProvisionedDeadEnabled"):
        r = t.bridge_call("jawa/static_call", type=WD, method="ProofPlace", args="current")
        res = str((r or {}).get("result", ""))
        if t._guard() and ("minds=0" in res or "corpses=0" in res or not res.startswith("sites=")):
            raise ExpectationFailed("placement short: %r" % (r,))
    with t.component("chassis_stand_near_shard_mind", toggle="workingDeadAnimateEnabled"):
        r = t.bridge_call("jawa/static_call", type=WD, method="ProofAnimate", args="current")
        res = str((r or {}).get("result", ""))
        if t._guard() and (res.startswith("standing=0 facingLight=0") or not res.startswith("standing=")):
            raise ExpectationFailed("no chassis stood up next to a Shard-mind: %r" % (r,))
    with t.component("working_dead_toggles_flip", beyond_toggle=True):
        for k in ("wellProvisionedDeadEnabled", "shardMindsEnabled", "workingDeadAnimateEnabled",
                  "shardMindDroidPullEnabled"):
            t.set_setting(SETTINGS_TYPE, {k: False})
            t.set_setting(SETTINGS_TYPE, {k: True})


@suite.chain("orun_ghal")
def orun_ghal(t):
    """LANTERNDEEPS_ORUN_GHAL_BUILD_1: Orun-Ghal lives in the Deep, can be studied and befriended, and never digs.
    Run on a LANTERN DEEP map with at least one colonist. ProofPlace spawns one (the genstep's own Place);
    ProofStudy 9 completes nine study sessions on separate days and must reach the friend tier with no mining job.
    Not proven here: the real study job by a colonist (Research work) and its rounds toward the Lantern."""
    OG = "RimMandrake.LanternDeeps.RM_OrunGhalProof"
    with t.component("orun_ghal_defs_loaded", beyond_toggle=True):
        for d in ("ThingDef/RM_OrunGhal", "PawnKindDef/RM_OrunGhal", "JobDef/RM_StudyOrunGhal",
                  "WorkGiverDef/RM_StudyOrunGhal", "GenStepDef/RM_DeepOrunGhal"):
            r = t.bridge_call("jawa/get_defs", defs=d)
            if t._guard() and (not r or not r.get("success") or r.get("foundCount") != 1):
                raise ExpectationFailed("def did not load: %s -> %r" % (d, r))
    with t.component("orun_ghal_placed", toggle="orunGhalEnabled"):
        r = t.bridge_call("jawa/static_call", type=OG, method="ProofPlace", args="current")
        res = str((r or {}).get("result", ""))
        if t._guard() and not res.startswith("placed"):
            raise ExpectationFailed("Orun-Ghal not placed: %r" % (r,))
    with t.component("orun_ghal_befriended_never_digs", toggle="orunGhalStudyEnabled"):
        r = t.bridge_call("jawa/static_call", type=OG, method="ProofStudy", args="9")
        res = str((r or {}).get("result", ""))
        if t._guard() and ("tier=3" not in res or "mining=False" not in res):
            raise ExpectationFailed("nine visits did not befriend it, or it is mining: %r" % (r,))


@suite.chain("hydrocarbon_wave1")
def hydrocarbon_wave1(t):
    """LANTERNDEEPS_HYDROCARBON_WAVE1_BUILD_1: drifter, candler, galuush, chiller, shoal load; a drifter killed with a blade
    is judged a cold kill and one killed by burns a hot kill (the ignition gate); a galuush can be hung in a Deep.
    Not proven here: the explosion itself on screen, the chiller's cooling (vanilla CompHeatPusher on a pawn -- read a
    penned chiller's room temperature over an hour), milking a candler, and the shoal's shared wounds."""
    HP = "RimMandrake.LanternDeeps.RM_HydrocarbonProof"
    with t.component("wave1_defs_loaded", beyond_toggle=True):
        for d in ("ThingDef/RM_Drifter", "ThingDef/RM_Candler", "ThingDef/RM_Galuush", "ThingDef/RM_Chiller",
                  "ThingDef/RM_Shoal", "HediffDef/RM_ShoalSharedCirculation", "GenStepDef/RM_DeepGaluush"):
            r = t.bridge_call("jawa/get_defs", defs=d)
            if t._guard() and (not r or not r.get("success") or r.get("foundCount") != 1):
                raise ExpectationFailed("def did not load: %s -> %r" % (d, r))
    with t.component("drifter_ignites_only_when_killed_hot", toggle="hydrocarbonIgnitionEnabled"):
        cold = str((t.bridge_call("jawa/static_call", type=HP, method="ProofDrifterKill", args="cold") or {}).get("result", ""))
        hot = str((t.bridge_call("jawa/static_call", type=HP, method="ProofDrifterKill", args="hot") or {}).get("result", ""))
        if t._guard() and ("killedHot=False" not in cold or "killedHot=True" not in hot):
            raise ExpectationFailed("ignition gate wrong: cold=%r hot=%r" % (cold, hot))
    with t.component("galuush_hung_in_a_deep", toggle="galuushEnabled"):
        r = t.bridge_call("jawa/static_call", type=HP, method="ProofGaluush", args="current")
        res = str((r or {}).get("result", ""))
        if t._guard() and not res.startswith("placed"):
            raise ExpectationFailed("galuush not placed: %r" % (r,))


@suite.chain("creep_cleavers")
def creep_cleavers(t):
    """LANTERNDEEPS_CREEP_CLEAVERS_BUILD_1: the Creep stalks a downed body and grows over it; a Cleaver struck hard
    splits. Run in a Deep (the Creep's map component lives only there). Not proven here: the crust art on screen,
    mining the crust, the shard trail while a Cleaver runs, and a wild Cleaver pack hunting."""
    CP = "RimMandrake.LanternDeeps.RM_CreepCleaversProof"
    with t.component("crystal_life_defs_loaded", beyond_toggle=True):
        for d in ("ThingDef/RM_CreepCrust", "HediffDef/RM_CreepEngulfed", "GenStepDef/RM_DeepCreep",
                  "ThingDef/RM_Cleaver", "PawnKindDef/RM_Cleaver", "ThingDef/RM_Filth_CleaverShards"):
            r = t.bridge_call("jawa/get_defs", defs=d)
            if t._guard() and (not r or not r.get("success") or r.get("foundCount") != 1):
                raise ExpectationFailed("def did not load: %s -> %r" % (d, r))
    with t.component("creep_stalks_and_engulfs", toggle="creepEnabled"):
        res = str((t.bridge_call("jawa/static_call", type=CP, method="ProofCreep", args="10") or {}).get("result", ""))
        m = re.search(r"before=([\d.]+) after=([\d.]+) engulf=([\d.]+)", res)
        if t._guard() and (not m or float(m.group(2)) >= float(m.group(1)) or float(m.group(3)) <= 0):
            raise ExpectationFailed("the Creep did not close on and engulf the downed body: %r" % res)
    with t.component("cleaver_splits_when_struck", toggle="cleavingEnabled"):
        res = str((t.bridge_call("jawa/static_call", type=CP, method="ProofCleave", args="") or {}).get("result", ""))
        m = re.search(r"before=(\d+) after=(\d+)", res)
        if t._guard() and (not m or int(m.group(2)) <= int(m.group(1))):
            raise ExpectationFailed("no shard walked away: %r" % res)


@suite.chain("aurora_collapse")
def aurora_collapse(t):
    """LANTERNDEEPS_AURORA_COLLAPSE_BUILD_1: the Deep's aurora condition brightens lanternstone; a marked roof cell is
    held for its warning (dust, sand, grumble) instead of falling the same tick. Run in a Deep. Not proven here: the
    Chorus sound, the dust/sand on screen, a propped roof holding, a galuush blast bringing its roof down."""
    AP = "RimMandrake.LanternDeeps.RM_AuroraCollapseProof"
    with t.component("aurora_brightens_lanternstone", toggle="auroraEnabled"):
        res = str((t.bridge_call("jawa/static_call", type=AP, method="ProofAurora", args="") or {}).get("result", ""))
        m = re.search(r"glow=([\d.]+)->([\d.]+)", res)
        if t._guard() and ("active=True" not in res or not m or float(m.group(2)) <= float(m.group(1))):
            raise ExpectationFailed("aurora did not start or did not brighten lanternstone: %r" % res)
    with t.component("roof_warns_before_it_falls", toggle="collapseWarningsEnabled"):
        res = str((t.bridge_call("jawa/static_call", type=AP, method="ProofCollapse", args="") or {}).get("result", ""))
        if t._guard() and "heldForWarning=True" not in res:
            raise ExpectationFailed("the roof was not held for its warning: %r" % res)


@suite.chain("hydrocarbon_wave2")
def hydrocarbon_wave2(t):
    """LANTERNDEEPS_HYDROCARBON_WAVE2_BUILD_1: slick, blinker, knocker load; a slick leaves fuel on the cells it leaves; a
    blinker's flash puts up its flare and dazzles a beast beside it; a knocker hears a roof held for its warning. Run in a
    Deep (the knocker needs the collapse component). Not proven here: a spark running a slick trail, predators drawn to a
    flash, the tame knocker's longer warning window."""
    WP = "RimMandrake.LanternDeeps.RM_HydrocarbonWave2Proof"
    with t.component("wave2_defs_loaded", beyond_toggle=True):
        for d in ("ThingDef/RM_Slick", "ThingDef/RM_Blinker", "ThingDef/RM_Knocker", "ThingDef/RM_BlinkerFlare",
                  "HediffDef/RM_BlinkerDazzled"):
            r = t.bridge_call("jawa/get_defs", defs=d)
            if t._guard() and (not r or not r.get("success") or r.get("foundCount") != 1):
                raise ExpectationFailed("def did not load: %s -> %r" % (d, r))
    with t.component("slick_lays_fuel", toggle="slickTrailEnabled"):
        res = str((t.bridge_call("jawa/static_call", type=WP, method="ProofSlick", args="") or {}).get("result", ""))
        m = re.search(r"moved=(\d+) fuelCells=(\d+)", res)
        if t._guard() and (not m or int(m.group(1)) == 0 or int(m.group(2)) == 0):
            raise ExpectationFailed("no fuel trail: %r" % res)
    with t.component("blinker_flashes", toggle="blinkerFlashEnabled"):
        res = str((t.bridge_call("jawa/static_call", type=WP, method="ProofBlinker", args="") or {}).get("result", ""))
        if t._guard() and "flare=True" not in res:
            raise ExpectationFailed("no flash: %r" % res)
    with t.component("knocker_hears_failing_roof", toggle="knockerAlarmEnabled"):
        res = str((t.bridge_call("jawa/static_call", type=WP, method="ProofKnocker", args="") or {}).get("result", ""))
        m = re.search(r"heard=(\d+)", res)
        if t._guard() and (not m or int(m.group(1)) == 0):
            raise ExpectationFailed("the knocker heard nothing: %r" % res)


@suite.chain("hydrocarbon_wave3")
def hydrocarbon_wave3(t):
    """LANTERNDEEPS_HYDROCARBON_WAVE3_BUILD_1: hush, sipper, tapper, pooler load; a hush on unlit natural ground is
    hidden and lunges at a beast set beside it; ten sippers on the brightest light shrink it; a wild tapper beside a
    colony battery drains it; a pooler beside a fire puts it out and a flame hit does not hurt it. Run in a Deep with a
    lit lamp and a charged colony battery. Not proven here: the hush genstep's placement on a fresh Deep, the tame
    tapper's aurora charge, a pooler holding a powered heater off, the hypothermia on a warm body."""
    WP = "RimMandrake.LanternDeeps.RM_HydrocarbonWave3Proof"
    with t.component("wave3_defs_loaded", beyond_toggle=True):
        for d in ("ThingDef/RM_Hush", "ThingDef/RM_Sipper", "ThingDef/RM_Tapper", "ThingDef/RM_Pooler",
                  "HediffDef/RM_HushUnseen", "GenStepDef/RM_DeepHush"):
            r = t.bridge_call("jawa/get_defs", defs=d)
            if t._guard() and (not r or not r.get("success") or r.get("foundCount") != 1):
                raise ExpectationFailed("def did not load: %s -> %r" % (d, r))
    with t.component("hush_hides_and_lunges", toggle="hushHidingEnabled"):
        res = str((t.bridge_call("jawa/static_call", type=WP, method="ProofHush", args="") or {}).get("result", ""))
        if t._guard() and ("hidden=True" not in res or "second=lunge" not in res):
            raise ExpectationFailed("hush did not hide and lunge: %r" % res)
    with t.component("sippers_drink_light", toggle="sipperDrinkingEnabled"):
        res = str((t.bridge_call("jawa/static_call", type=WP, method="ProofSipper", args="") or {}).get("result", ""))
        m = re.search(r"before=([\d.]+) after=([\d.]+)", res)
        if t._guard() and (not m or float(m.group(2)) >= float(m.group(1))):
            raise ExpectationFailed("the light did not shrink: %r" % res)
    with t.component("tapper_drains_battery", toggle="tapperEnabled"):
        res = str((t.bridge_call("jawa/static_call", type=WP, method="ProofTapper", args="") or {}).get("result", ""))
        m = re.search(r"before=([\d.]+) after=([\d.]+)", res)
        if t._guard() and (not m or float(m.group(2)) >= float(m.group(1))):
            raise ExpectationFailed("the battery did not drain: %r" % res)
    with t.component("pooler_smothers_fire", toggle="poolerSmotherEnabled"):
        res = str((t.bridge_call("jawa/static_call", type=WP, method="ProofPooler", args="") or {}).get("result", ""))
        if t._guard() and ("fireLeft=False" not in res or "flameHurt=False" not in res):
            raise ExpectationFailed("pooler did not put the fire out unhurt: %r" % res)
