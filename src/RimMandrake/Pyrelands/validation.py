"""validation.py -- modcheck suite for RimMandrake Pyrelands (mandrake.rm.pyrelands).

Assigned as the resolution for the maturity dashboard's "FireEcology" system
(`Transient/project_maturity_dashboard.json`: functionRung "validated",
evidenceRef "FIRE_ECOLOGY_LOOP_1", tier ""). No folder named `FireEcology`
exists. Traced, not guessed: `infrastructure/state/items/FIRE_ECOLOGY_LOOP_1.md`
records that its RimStarWars-tier engine mod (`src/RimStarWars/FireEcology`,
packageId `mandrake.rsw.fireecology`) and its RimUtinni-tier wiring mod
(`src/RimUtinni/FireEcology`, renamed `PyrelandsFireEcology` the same day
for a folder-collision bug) were the original two halves. On disk today
there is no `src/RimStarWars/FireEcology` at all, and
`src/RimUtinni/PyrelandsFireEcology/About.xml`'s own description names its
dependency as `mandrake.rm.pyrelands`, "generic desert fire-ecology
engine" -- confirmed by grep: only `src/RimMandrake/Pyrelands/About/About.xml`
carries that packageId, and its `Source/FireEcologyHook.cs` is a byte-for-
byte continuation of the engine described in the item file (same class
names `FireEcologyHookMod`/`Patch_LightningStrike_Fulgurite`/
`Patch_FireTick_AshAndScorchFruit`, same defNames `RM_FE_*`). The engine
tier was evidently migrated RimStarWars -> RimMandrake at some point after
2026-09-01 (its C# namespace, `RimMandrake.StarWars.FireEcology`, was not
updated in that move -- a naming drift, not this task's to fix). **This
file is written for `src/RimMandrake/Pyrelands`, which is the "FireEcology"
system.**

The dashboard also lists a SEPARATE system, "Pyrelands" (functionRung
"implemented", evidenceRef "PYRELANDS_SELF_CONTAINED_BIOME_1"), pointing at
this SAME folder but grading the self-contained-biome placement work
specifically. It is not "validated" rung and is not part of this modcheck
wave (only "validated"-rung systems are being scripted), so there is no
double-write here: exactly one validation.py belongs in this folder and
this is it.

Grounded in `Source/FireEcologyHook.cs` (the two Harmony postfixes, the
biome worker, the ashfall MapComponent), `Source/RM_PyrelandsMod.cs` (the
five real Mod Settings toggles), and `Defs/BiomeDefs/Pyrelands.xml` (the
engine's own self-contained `RM_FE_Pyrelands` BiomeDef -- this validator
targets THIS biome directly, not the RimUtinni wiring mod's separate
`ZBiome_Grasslands` patch, which is `PyrelandsFireEcology`'s own concern).

GAP CARRIED FORWARD FROM THE PITS PILOT, confirmed by reading (not
assumed): `RM_PyrelandsSettings`' five fields are all `public static`,
exactly the shape that made `rimworld/update_mod_settings` refuse Pits'
`trapTriggerEnabled` live ("reflection walks INSTANCE fields ... this
mod's actual values live on the class, not the instance" -- Pits
`validation.py`). `t.set_setting` is therefore not attempted anywhere
below -- every component exercises its toggle at the SHIPPED DEFAULT
(all five enabled) only. This is now a second data point for a mod-wide
bridge/pattern fix (`SlimeMod.cs`/`RM_GreentideMod.cs` are cited in this
mod's own source as using the same static-field pattern), not a
one-off.

Still not proven / likely first-live-run corrections:
  1. `fulgurite_armed_only` (toggle `fulguriteEnabled`) cannot exercise the
     actual strike -> fulgurite path: no bridge tool forces a
     `WeatherEvent_LightningStrike` (checked -- `--list-tools` for
     "lightning"/"strike" turns up nothing, same absence
     FIRE_ECOLOGY_LOOP_1.md's own live pass recorded). The component below
     proves only that the Harmony patch is installed and armed (a real,
     deterministic check -- a rename or API break would log "TARGET METHOD
     NOT FOUND" instead). Whether a strike on sand-family ground actually
     leaves `RM_FE_Fulgurite` is UNVERIFIED by this suite.
  2. `biome_def_wiring` (toggle `biomeGenerationEnabled`) cannot exercise
     `BiomeWorker_Pyrelands.GetScore` at all -- it only ever runs during
     world generation, which this project does not automate or test
     (CLAUDE.md: "no worldgen feature, in any version"). The component
     below proves only that `RM_FE_Pyrelands` resolves with its expected
     `terrainPatchMakers` shape -- the toggle's actual gate (whether the
     biome can win a tile) is unverified by construction, not by omission.
  3. Black Rain (`RM_FE_BlackRain`) and the firefoam sprayer/firebreak are
     not covered at all -- neither is gated by a Mod Settings toggle
     (floor is toggles only) and both ride 100% vanilla mechanisms already
     proven by FIRE_ECOLOGY_LOOP_1.md's own live passes (WeatherDecider's
     rain-on-fire multiplier; Fire.TickInterval's rain-extinguish). Adding
     them would be a `beyond_toggle` component for a future revision, not
     required by the floor.
  4. `ash_ladder_escalation` only asserts the FIRST rung (`RM_FE_Ash_Trace`)
     is reached -- FIRE_ECOLOGY_LOOP_1.md's own live run needed a long,
     repeated-reburn session to reach `RM_FE_Ash_Deep`; asserting that here
     would make a smoke-test run for minutes. Reaching Trace is sufficient
     to prove `TerrainDef.burnedDef` resolves at all for this mod's ground
     clones.
"""
from modcheck import Suite, ExpectationFailed

suite = Suite("Pyrelands")
suite.toggles = ["fulguriteEnabled", "ashDustingEnabled", "scorchFruitEnabled",
                  "ashfallAccumulationEnabled", "biomeGenerationEnabled"]

SAND = "RM_FE_Ground_Sand"
TEST_SIZE = 24


def _rect(t, size=TEST_SIZE):
    x, z = t.anchor
    half = size // 2
    return x - half, z - half, size, size


def _rect_str(t, size=TEST_SIZE):
    x0, z0, w, h = _rect(t, size)
    return "%d,%d,%d,%d" % (x0, z0, w, h)


def _live(t):
    """True only for a real chain run against a real Session and an
    unfailed chain -- False for `Suite.components_declared()`'s offline
    probe walk (`t.session is None`) AND for a chain past a failed
    component (`t.upstream_failed`), matching `TestContext._guard()`'s own
    two conditions without reaching into that private method. Every manual
    assertion below (anything not already one of the guarded `expect_*`
    verbs) checks this first -- otherwise the lint/floor probe's no-op
    bridge_call responses (always None) would trip a false
    ExpectationFailed on every offline load of this file."""
    return t.session is not None and not t.upstream_failed


def _count(t, defName, rect):
    """jawa/list_things is a pure read with no expect_* of its own in the
    verb vocabulary (spec's fixed list has no count/list assertion) --
    `bridge_call` is the escape valve, and this wraps its own reasoned
    assertion exactly as `_report`/`_debug` do in the Pits exemplar."""
    r = t.bridge_call("jawa/list_things", defName=defName, rect=rect)
    return (r or {}).get("countMatched", 0)


@suite.chain("fire_tick_effects")
def fire_tick_effects(t):
    """One fire, watched long enough for both fire-tick postfixes
    (`Patch_FireTick_AshAndScorchFruit`) to roll true at least once, plus
    the pure-vanilla ash-ladder escalation the same burn drives. Tick
    counts are the item file's own live-observed timing
    (FIRE_ECOLOGY_LOOP_1.md: ash filth and scorch-fruit both appeared
    within ~2,200 ticks on a similarly-sized burn; this leaves headroom to
    ~2,600 then a further ~9,000 for the much rarer scorch-fruit roll,
    0.0025 vs ash's 0.02 chance-per-tick-batch)."""
    t.clear_area(size=TEST_SIZE)
    x0, z0, w, h = _rect(t)
    rect = "%d,%d,%d,%d" % (x0, z0, w, h)
    ground = t.bridge_call("jawa/set_terrain", x=x0, z=z0, terrainDef=SAND,
                            width=w, height=h, layer="top")
    if _live(t):
        changed = (ground or {}).get("cellsChanged", 0)
        if not changed or changed < (w * h):
            raise ExpectationFailed(
                "set_terrain(%s) over %s did not paint the whole rect: cellsChanged=%r"
                % (SAND, rect, changed))

    with t.component("ash_dusting", toggle="ashDustingEnabled"):
        t.bridge_call("jawa/map_fire", action="start", rect=rect, fireSize=1.2)
        t.wait_ticks(2600)
        n = _count(t, "RM_FE_Filth_LooseAsh", rect)
        if _live(t) and n < 1:
            raise ExpectationFailed(
                "expected >=1 RM_FE_Filth_LooseAsh in %s after 2600 ticks of fire, got %d"
                % (rect, n))
        t.screenshot()

    with t.component("scorch_fruit_seed", toggle="scorchFruitEnabled"):
        t.wait_ticks(9000)  # same ongoing burn, ~11,600 ticks cumulative
        n = _count(t, "RM_FE_Plant_ScorchFruit", rect)
        if _live(t):
            if n < 1:
                raise ExpectationFailed(
                    "expected >=1 RM_FE_Plant_ScorchFruit in %s after ~11,600 ticks of "
                    "fire, got %d" % (rect, n))
            cap = 40  # RM_PyrelandsSettings.scorchFruitMapCap shipped default
            if n > cap:
                raise ExpectationFailed(
                    "RM_FE_Plant_ScorchFruit count %d exceeds the per-map cap %d -- "
                    "Patch_FireTick_AshAndScorchFruit's cap check is not holding"
                    % (n, cap))
        t.screenshot()

    with t.component("ash_ladder_escalation", beyond_toggle=True):
        # Pure vanilla: TerrainDef.burnedDef, consumed by
        # TerrainGrid.Notify_TerrainBurned off Fire.TryBurnFloor -- no
        # RM_PyrelandsSettings toggle gates this at all.
        got = t.bridge_call("jawa/get_terrain_batch", rects=rect)
        if _live(t):
            distinct = (got or {}).get("distinctTerrains") or []
            if not any(d in distinct for d in
                       ("RM_FE_Ash_Trace", "RM_FE_Ash_Light", "RM_FE_Ash_Heavy", "RM_FE_Ash_Deep")):
                raise ExpectationFailed(
                    "expected the burnedDef chain to have advanced %s past %s at least "
                    "to RM_FE_Ash_Trace; distinctTerrains=%r" % (rect, SAND, distinct))
        t.screenshot()


@suite.chain("ashfall_weather_accumulation")
def ashfall_weather_accumulation(t):
    """`MapComponent_PyrelandsAshfall` floors its attempts-per-batch at 1
    regardless of map/test-area size (`FireEcologyHook.cs`: "if (attempts
    < 1) attempts = 1"), so even this small rect is guaranteed a
    deposit attempt every 250 ticks once the weather matches -- the only
    real uncertainty is the roofed/water-cell skip, which a freshly
    cleared, freshly sanded rect does not hit."""
    t.clear_area(size=TEST_SIZE)
    x0, z0, w, h = _rect(t)
    rect = "%d,%d,%d,%d" % (x0, z0, w, h)
    t.bridge_call("jawa/set_terrain", x=x0, z=z0, terrainDef=SAND,
                  width=w, height=h, layer="top")

    with t.component("ashfall_accumulates", toggle="ashfallAccumulationEnabled"):
        t.bridge_call("jawa/weather_set", weather="RM_FE_Weather_AshFall", lockWeather=True)
        t.wait_ticks(2600)   # >=10 of the component's 250-tick batches
        n = _count(t, "RM_FE_Filth_LooseAsh", rect)
        if _live(t) and n < 1:
            raise ExpectationFailed(
                "expected >=1 RM_FE_Filth_LooseAsh in %s after 2600 ticks under "
                "RM_FE_Weather_AshFall, got %d" % (rect, n))
        t.screenshot()
        t.bridge_call("jawa/weather_set", unlock=True)


@suite.chain("startup_and_def_wiring")
def startup_and_def_wiring(t):
    """No live game state to build or tear down -- both components are
    pure reads of what the current session already has loaded. Still runs
    inside a chain (with a no-op `clear_area`) so the runner's evidence/
    screenshot machinery applies uniformly."""
    t.clear_area(size=8)

    with t.component("fulgurite_armed_only", toggle="fulguriteEnabled"):
        # The only proof available offline-of-a-real-strike: the startup
        # Harmony-apply log line. See module docstring point 1 for what
        # this does NOT prove.
        t.expect_log_contains(
            "[RimMandrake.StarWars.FireEcology] fulgurite-spawn",
            field=None, value=None)
        t.screenshot()

    with t.component("biome_def_wiring", toggle="biomeGenerationEnabled"):
        # See module docstring point 2 for why this cannot exercise the
        # toggle's actual gate (world-generation-only).
        d = t.bridge_call("jawa/get_def", defName="RM_FE_Pyrelands", defType="BiomeDef")
        if _live(t):
            makers = (d or {}).get("terrainPatchMakers") or []
            if len(makers) < 1:
                raise ExpectationFailed(
                    "RM_FE_Pyrelands resolved with no terrainPatchMakers -- expected the "
                    "burn-scar ladder patchmaker (trace/light/heavy thresholds); got %r" % d)
            thresholds = (makers[0] or {}).get("thresholds") or []
            names = [th.get("terrain") for th in thresholds]
            if "RM_FE_Ash_Trace" not in names:
                raise ExpectationFailed(
                    "RM_FE_Pyrelands's first terrainPatchMaker does not list "
                    "RM_FE_Ash_Trace among its thresholds: %r" % names)
        t.screenshot()
