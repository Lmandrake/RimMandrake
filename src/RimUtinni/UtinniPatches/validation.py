"""validation.py -- modcheck suite for RimUtinni UtinniPatches
(mandrake.rut.patches). list: full (walk doc's own line -- "this mod's
whole purpose is patching third-party defs across ~20 loadAfter mods; the
minimal list cannot exercise it").

THIS MOD IS ENORMOUS (300+ files under Defs/Patches/Textures) and the walk
doc (`design/validation_walks/RimUtinni/UtinniPatches.md`) already itemizes
its own flagship def read-backs in full (## must be true / the walk, steps
1-13) -- this suite does NOT re-walk all ~150 defs as chains, matching
every other suite in this backfill's convention (StructureInjections/
RustChrome/Antiquities/AshkarrWeatherSuite): validation.py chains prove
BEHAVIOR a bridge session can exercise; raw def-existence/log-cleanliness
is that separate walk-doc checklist's own job. What this suite DOES cover
is the mod's actual C# surface -- `Source/AmbientShrineGuardians.cs`,
`Source/GeothermalDensityField.cs`, `Source/PatchOperationSettingGate.cs`,
`Source/TwinkleFloraSpike.cs`, `Source/UtinniPatchesSettings.cs` -- every
one read whole before writing this, plus a small, representative sample of
the walk doc's own flagship defs (not all ~150).

WHAT THE C# ACTUALLY DOES, and why two of its four mechanisms are
UNCOVERED here rather than faked:

  * `SymbolResolver_Interior_AncientTemple_AmbientDoctrine` (Ambient Shrine
    Guardians) swaps an ancient-temple's mechanoid/fleshbeast/hive guardian
    for a sealed cryptosleep watch, ONLY on 8 named biomes, ONLY during
    real BaseGen map generation of a NEW ancient-temple map. The file's OWN
    header says it outright: "⛔ NOT PROVEN YET. A 0W/0E build proves the
    subclass compiles... it proves NOTHING about this resolver actually
    being picked at map generation... owes a quicktest map on one
    candidate biome... before this may be called done." This suite agrees
    and does not fake that proof: `modcheck.suite.TestContext` has no verb
    that generates a NEW map with a chosen biome (every verb here acts on
    `Find.CurrentMap`, already generated before the chain runs) -- the
    tooling this needs does not exist yet on this bridge.
  * `GenStep_ScatterGeysersDensityField` (Geothermal Density Field) scales
    steam-geyser count by `GeothermalDensityUtility.ComputeDensity`, a pure
    static function of world position -- but `ComputeDensity`/
    `CalculateFinalCount` are ONLY ever called from inside real map
    generation too, and neither is exposed by any bridge tool for a direct
    call. Same gap, same reason -- UNCOVERED here, not faked.
  * `PatchOperationSettingGate` (the `utinniWorldIconEnabled` gate on
    `Patches/UtinniWorldIcon.xml`) only ever runs at PATCH-APPLY time,
    which is over long before any bridge session starts (the class's own
    header: "LoadedModManager.LoadAllActiveMods... CreateModClasses()...
    BEFORE LoadModXML()/ApplyPatches()... A settings change therefore
    takes effect on the NEXT game start, not immediately"). Flipping
    `utinniWorldIconEnabled` mid-session via `t.set_setting` changes the
    static field but the def is already built either way -- so this is the
    same "worldgen/boot-time-only toggle" shape StructureInjections'
    `enabled` and RustChrome's `themeEnabled`(false-path) already document,
    and gets the same repo-level (not live) proof: `repo_checks` below
    confirms the XML actually wires `PatchOperationSettingGate` with
    `setting=utinniWorldIconEnabled` and a real `<match>` branch, which is
    everything a live session COULD prove about wiring that already ran.
  * `CompGlowPulse`/`RUT_PlantTwinkle` (Twinkle Flora Spike) is the one
    mechanism that IS live-drivable -- it is a timeboxed feasibility spike
    "not wired into any live biome or shipped plant" (its own header) but
    spawnable by hand, exactly as that header invites. No bridge tool
    reads a Thing's live rendered colour back, so this suite proves only
    that the comp survives real ticking across multiple `CompTickRare`
    (every 250 ticks) cycles without throwing or despawning the plant --
    not the actual colour-pulse math, which needs either a colour-read
    tool or the timeboxed item's own console measurement, neither of which
    exists here.

Still not proven / real gaps:
  1. Ambient Shrine Guardians and Geothermal Density Field: see above --
     both need a "generate a new map with a chosen biome" bridge tool that
     does not exist. Not a smoke-suite gap to paper over; it is this test
     harness's own missing capability.
  2. Walk doc step 6 ("jawa/world_info_get on the frozen Ash'karr worldfile
     ... never a freshly generated world") is NOT what
     `planet_name_patch_on_quicktest_world` below does -- a modcheck
     session's quicktest map necessarily sits on ITS OWN throwaway dev
     world (every suite in this backfill relies on that structurally), not
     the frozen campaign save. This chain proves the `NamerWorld`
     `rulesStrings` patch (walk step 5's def content) actually renames
     WHATEVER world gets generated, which is a stronger live claim than a
     def read-back but still not step 6's specific ask. Confirming the
     FROZEN save's own world.name is a full-campaign-load check, out of
     this suite's quicktest shape (see `rimworld-debug-testing` skill: a
     quicktest is not evidence about the real campaign).
  3. The Conditional-guarded third-party reflavors (`GalacticEmpire.xml`,
     `ForgottenArsenal.xml`, and every other `MayRequire`-guarded patch
     among the ~150 in `Patches/`) are NOT swept here -- whether
     `Neronix17.OuterRim.GalacticEmpire` etc. are actually active on
     whatever "full" list a given run uses is itself runtime-variable, and
     auditing every soft-dependent patch's both branches is the walk doc's
     own job (steps 8-9), not duplicated as ~20 more chains here.
"""
import os
import re

from modcheck import Suite, ExpectationFailed

suite = Suite("UtinniPatches")
suite.toggles = ["ambientShrineDoctrineEnabled", "geothermalDensityFieldEnabled",
                 "utinniWorldIconEnabled"]

_MOD_DIR = os.path.dirname(os.path.abspath(__file__))
_WORLDICON_PATCH = os.path.join(_MOD_DIR, "Patches", "UtinniWorldIcon.xml")
_TWINKLE_DEF = os.path.join(_MOD_DIR, "Defs", "ThingDefs_Plants",
                            "RUT_TwinkleSpikeTestPlant.xml")

TWINKLE_PLANT = "RUT_TwinkleSpikeTestPlant"


def _live(t):
    """Distinguishes a real chain run from the offline declaration probe --
    same idiom as AshkarrWeatherSuite/validation.py."""
    return t.session is not None and not t.upstream_failed


@suite.chain("repo_checks")
def repo_checks(t):
    """Pure repo checks against the XML/Defs text itself -- no bridge call,
    runs even under the offline declaration probe. Covers the two
    boot/patch-time-only mechanisms (module docstring) that a live session
    cannot re-observe after the fact."""
    t.clear_area(size=8)

    with t.component("world_icon_gate_wired_correctly", beyond_toggle=True):
        with open(_WORLDICON_PATCH, "r", encoding="utf-8") as f:
            xml = f.read()
        if 'Class="RimMandrake.Utinni.UtinniPatches.PatchOperationSettingGate"' not in xml:
            raise ExpectationFailed(
                "UtinniWorldIcon.xml no longer wires PatchOperationSettingGate")
        if "<setting>utinniWorldIconEnabled</setting>" not in xml:
            raise ExpectationFailed(
                "UtinniWorldIcon.xml's PatchOperationSettingGate is missing "
                "<setting>utinniWorldIconEnabled</setting> -- PatchOperationSettingGate.ApplyWorker "
                "only recognises that exact string (named-switch, not reflection, by design)")
        if "<match" not in xml:
            raise ExpectationFailed(
                "UtinniWorldIcon.xml's gate has no <match> branch -- nothing would "
                "apply even with the setting on")

    with t.component("twinkle_flora_spike_only_wired_to_its_own_test_plant",
                      beyond_toggle=True):
        # The comp's own header claims RUT_TwinkleSpikeTestPlant.xml is the
        # ONLY def referencing CompProperties_GlowPulse -- confirmed by
        # grepping every Defs/ThingDefs_Plants file, not trusted from the
        # comment alone.
        plants_dir = os.path.join(_MOD_DIR, "Defs", "ThingDefs_Plants")
        referencing = []
        for name in os.listdir(plants_dir):
            if not name.endswith(".xml"):
                continue
            with open(os.path.join(plants_dir, name), "r", encoding="utf-8") as f:
                if "CompProperties_GlowPulse" in f.read():
                    referencing.append(name)
        if referencing != ["RUT_TwinkleSpikeTestPlant.xml"]:
            raise ExpectationFailed(
                "expected exactly RUT_TwinkleSpikeTestPlant.xml to reference "
                "CompProperties_GlowPulse, found %r -- either the spike got wired "
                "into a real plant (update this suite's live coverage) or the "
                "test def was renamed/removed" % referencing)


@suite.chain("twinkle_flora_spike_survives_ticking")
def twinkle_flora_spike_survives_ticking(t):
    """The one live-drivable mechanism (module docstring). Spawns the
    timeboxed test plant and steps past several `CompTickRare` cycles
    (every 250 ticks) -- proves the comp does not throw/despawn the plant
    across real ticking, NOT the actual colour-pulse math (no bridge tool
    reads a Thing's rendered colour back). `t.screenshot()` at the end is
    the best available evidence for a human glance at the pulse itself."""
    t.clear_area(size=10)
    t.spawn(TWINKLE_PLANT, count=1, at="point")

    with t.component("plant_survives_multiple_glow_pulse_ticks", beyond_toggle=True):
        r = t.bridge_call("jawa/list_things", defName=TWINKLE_PLANT)
        rows = (r or {}).get("things") or []
        if _live(t) and not rows:
            raise ExpectationFailed(
                "no %s found via jawa/list_things right after spawning it"
                % TWINKLE_PLANT)

        t.wait_ticks(1200)  # ~5 CompTickRare cycles (250 ticks each)

        r2 = t.bridge_call("jawa/list_things", defName=TWINKLE_PLANT)
        rows2 = (r2 or {}).get("things") or []
        if _live(t) and not rows2:
            raise ExpectationFailed(
                "%s is gone after 1200 ticks of CompTickRare pulsing -- "
                "CompGlowPulse or RUT_PlantTwinkle.Graphic may be throwing "
                "and getting the plant destroyed/de-registered" % TWINKLE_PLANT)
        t.screenshot()


@suite.chain("planet_name_patch_on_quicktest_world")
def planet_name_patch_on_quicktest_world(t):
    """`JawaWorld_Name.xml` replaces RulePackDef `NamerWorld`'s
    `rulesStrings` unconditionally (walk doc bullet 2) -- this proves the
    LIVE EFFECT on whatever world this modcheck session's own quicktest map
    sits on, not the frozen campaign save (module docstring gap #2: that is
    a full-campaign-load check, out of a quicktest's scope per the
    `rimworld-debug-testing` skill)."""
    with t.component("namer_world_patch_renames_the_live_world", beyond_toggle=True):
        r = t.bridge_call("jawa/world_info_get")
        if _live(t):
            info = (r or {}).get("info") or {}
            name = info.get("name")
            if name != "Ash'karr":
                raise ExpectationFailed(
                    "jawa/world_info_get's world name is %r, expected exactly "
                    "\"Ash'karr\" (U+0027 apostrophe) from JawaWorld_Name.xml's "
                    "unconditional NamerWorld patch: %r" % (name, r))
