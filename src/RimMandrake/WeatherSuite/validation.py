"""validation.py -- modcheck suite for RimMandrake WeatherSuite
(mandrake.rm.weathersuite).

Grounded in the mod's actual, entire source read whole -- `Source/
WeatherSuiteHook.cs` (PlanetGeometryDef, WeatherGeometryUtility,
MapComponent_TerminatorBand, GameCondition_DarkAuroraMax,
IncidentWorker_NightsideAurora, CompForecaster) and `Source/
WeatherSuiteSettings.cs` (the three Mod Settings toggles, all `public
static` -- same reflectable shape as StructureInjections/RustChrome) -- and
every one of its five Defs XML files, read whole rather than trusted from
the walk doc's own quotes.

THE WALK DOC ITSELF IS WRONG, same family as CLAUDE.md's RustChrome note
("a doc can describe defects fixed before the doc was written") except this
one was never right in the first place, not merely stale:
`design/validation_walks/RimStarWars/WeatherSuite.md` -- itself filed under
the WRONG TIER directory (RimStarWars, when `subject:` on its own line 2
correctly names `src/RimMandrake/WeatherSuite` and About.xml's packageId is
`mandrake.rm.weathersuite`, a RimMandrake-tier engine mechanism per the
mod's own description: "Campaign-specific wiring... lives in RimUtinni...
This mod carries no Ash'karr/clan/story references") -- quotes EVERY
defName in this mod as `RSW_WS_*` (steps 4-9, 11). Reading the actual XML
(`GameConditionDefs_TerminatorFront.xml`, `GameConditionDefs_DarkAurora.xml`,
`IncidentDefs_DarkAurora.xml`, `ThoughtDefs_DarkAurora.xml`,
`ThingDefs_WeatherInstrument.xml`) shows every one of them is `RM_WS_*` --
`RM_WS_TerminatorFront`, `RM_WS_DarkAurora` (three defs, same name, three
def TYPES), `RM_WS_WeatherInstrument` -- matching `WeatherSuiteHook.cs`'s
own `GetNamedSilentFail("RM_WS_TerminatorFront")` call. The walk doc's step
1 config-error string ("mandrake.rsw.weathersuite") is wrong for the same
reason -- the real packageId is `mandrake.rm.weathersuite`. The ONE thing
the walk doc gets right about naming is the C# namespace
(`RimMandrake.StarWars.WeatherSuite`, confirmed in the source's own
`namespace` line and the static-ctor log string it quotes verbatim at step
2) -- so someone plainly reasoned from the intended RimStarWars-tier
C#-namespace convention and never actually opened the Defs. This suite uses
the REAL `RM_WS_*` names throughout; fixing the walk doc itself is a
separate, out-of-scope pass.

WHAT THIS MOD ACTUALLY DOES: a fixed great-circle-arc geometry test
(`WeatherGeometryUtility`) reads a SINGLE `PlanetGeometryDef` instance (none
ships with this mod -- only the Def TYPE and mechanism; the RimUtinni wiring
mod supplies Ash'karr's real numbers) to decide, once per map at
`FinalizeInit()`, whether to start a PERMANENT `RM_WS_TerminatorFront`
(vanilla `GameCondition_Flashstorm`, unmodified) and, per nightside-band
player-home map, whether `IncidentWorker_NightsideAurora` (a `CanFireNowSub`
override on vanilla `IncidentWorker_Aurora`) can ever fire
`RM_WS_DarkAurora` (`GameCondition_DarkAuroraMax`, a `SkyTarget()` override
of vanilla `GameCondition_Aurora`, +14 mood via `ThoughtWorker_Aurora`
reused unchanged). `CompForecaster` is a passive, `Rand`-free
`CompInspectStringExtra()` reader.

THE STRUCTURAL, ENVIRONMENT-GATED GAP THE WALK DOC ITSELF ALREADY NAMES
(status-hint, step 3): on the minimal modcheck list there is NO
`PlanetGeometryDef` instance loaded anywhere (it ships only with the
RimUtinni wiring mod), so `WeatherGeometryUtility.ActiveGeometry` is
permanently null and `MapInTerminatorBand`/`MapInNightsideBand` are
permanently false. This makes `terminatorFrontEnabled` and
`nightsideAuroraEnabled` STRUCTURALLY UNTESTABLE for their real effect on
this list -- both toggles are checked ONLY after the geometry gate already
forces false, so flipping either one changes nothing observable regardless
of its own value. This is not a setter problem (both are ordinary
reflectable `public static bool` fields `t.set_setting` can reach fine) --
it is that the mechanism they gate never gets a chance to fire at all
without a second mod's def loaded. `auroraMaxBrightnessEnabled` gates pure
render output (`SkyTarget()`'s returned colours) with no bridge tool found
that reads a live `GameCondition`'s rendered sky colour back -- the walk
doc's own step 12 already calls this a human-eyes-only judgment.

Still not proven / likely first-live-run corrections:
  1. `terminatorFrontEnabled` and `nightsideAuroraEnabled`'s actual gating
     effect are UNCOVERED for the structural reason above -- both chains
     below bypass BOTH the settings AND the geometry gate entirely via
     `jawa/game_condition`/dry-run `CanFireNow`, proving the CONDITIONS and
     the INCIDENT WORKER resolve and behave correctly, not that the two
     settings actually suppress them (they cannot be observed to, on this
     list). A future pass needs the RimUtinni wiring mod's `PlanetGeometryDef`
     instance loaded to test the toggles for real.
  2. `RM_WS_TerminatorFront`'s `preventRain=true` payload is NOT
     independently verified live -- proving "no rain ever rolls here" needs
     either a long tick-window statistical absence check or a direct
     `WeatherDecider` read-back tool, neither attempted here; registration
     and permanence are asserted, the weather-suppression EFFECT is not.
  3. `auroraMaxBrightnessEnabled`'s visual effect (`SkyTarget()`'s
     saturation/brightness math) is UNCOVERED -- no bridge tool reads a
     live GameCondition's rendered sky colours back; this is the walk doc's
     own named human-eyes gap (step 12), not a new one.
  4. `WeatherGeometryUtility`'s one-time "no PlanetGeometryDef loaded"
     warning (the `warnedMissing` static flag) is NOT asserted via log
     presence -- it fires at most ONCE per game process and `jawa/drain_log`
     CONSUMES what it reads, so whether this suite's own drain call would
     still see it depends entirely on what ran earlier in the same session.
     `dark_aurora_incident_is_correctly_gated_by_geometry` below proves the
     same underlying fact (`CanFireNow` is false) without that ordering
     fragility.
"""
from modcheck import Suite, ExpectationFailed

suite = Suite("WeatherSuite")
suite.toggles = ["terminatorFrontEnabled", "nightsideAuroraEnabled",
                 "auroraMaxBrightnessEnabled"]

SETTINGS_TYPE = "RimMandrake.StarWars.WeatherSuite.WeatherSuiteSettings"
TERMINATOR = "RM_WS_TerminatorFront"
DARK_AURORA = "RM_WS_DarkAurora"
INSTRUMENT = "RM_WS_WeatherInstrument"


@suite.chain("terminator_front_registers_permanently_bypassing_geometry")
def terminator_front_registers_permanently_bypassing_geometry(t):
    """`jawa/game_condition(start, RM_WS_TerminatorFront, permanent=True)`
    bypasses `MapComponent_TerminatorBand.FinalizeInit`'s own geometry gate
    entirely -- deliberately, per the walk doc's own step 11 ("bypassing
    the geometry gate, testing the condition itself"), since the minimal
    list can never make that gate pass naturally (module docstring's
    structural gap). Proves `RM_WS_TerminatorFront` resolves as a real,
    permanent-capable GameConditionDef whose conditionClass (vanilla
    `GameCondition_Flashstorm`) registers without error -- not that this
    mod's OWN gating logic ever starts it on this list.

    🔴 FOUND AND FIXED (wave 12): read `r.get("active")`, but
    `JawaBenchEventTools.cs`'s `GameConditionTool` returns the list under
    `activeConditions`, never `active` -- confirmed by reading its return
    statement (`activeConditions = active` is the OUTER key name; `active`
    is only the LOCAL variable it was built from). `.get("active")` was
    therefore always `None` -> `[]`, so `row` was always `None` and this
    component raised `ExpectationFailed` on every live run regardless of
    whether the condition actually registered -- another instance of the
    same guaranteed-false-failure key-mismatch bug class AshkarrFlora's
    wave-11 fix and this wave's RimDefDump/AshkarrLandmarkArt fixes are
    all in. Fixed by reading `activeConditions`."""
    t.clear_area(size=20)
    with t.component("terminator_front_condition_resolves_and_registers",
                      beyond_toggle=True):
        r = t.bridge_call("jawa/game_condition", action="start",
                          condition=TERMINATOR, permanent=True)
        if not (r or {}).get("success"):
            raise ExpectationFailed(
                "jawa/game_condition(start, %s, permanent=True) failed: %r"
                % (TERMINATOR, r))
        active = (r or {}).get("activeConditions") or []
        row = next((c for c in active if c.get("def") == TERMINATOR), None)
        if row is None or not row.get("permanent"):
            raise ExpectationFailed(
                "%s is not active-and-permanent after starting it: %r"
                % (TERMINATOR, active))
        t.bridge_call("jawa/game_condition", action="end", condition=TERMINATOR)
        t.screenshot()


@suite.chain("dark_aurora_incident_is_correctly_gated_by_geometry")
def dark_aurora_incident_is_correctly_gated_by_geometry(t):
    """`jawa/storyteller_fire(RM_WS_DarkAurora, dryRun=True)` resolves the
    IncidentDef/workerClass (proving `IncidentWorker_NightsideAurora` and
    the def wiring are intact) and reports `canFireNow` from
    `idef.Worker.CanFireNow(parms)` WITHOUT firing anything. On the minimal
    list this must be false -- not because `nightsideAuroraEnabled` is off
    (it defaults true), but because `WeatherGeometryUtility.
    MapInNightsideBand` is unconditionally false with no `PlanetGeometryDef`
    loaded (module docstring's structural gap). This is the mechanism the
    walk doc's own bullet 4 describes ("on the minimal list that second
    condition is always false, so the incident never fires").

    🔴 FOUND AND FIXED (wave 12): checked `r.get("canFire")`, but
    `JawaBenchIncidentTools.cs`'s `StorytellerFire` names the dry-run field
    `canFireNow` (`success = true, dryRun = true, resolved, canFireNow =
    canFire, ...` -- `canFire` is only the LOCAL variable; the response key
    is `canFireNow`). `.get("canFire")` was therefore always `None`
    (falsy), so this component's whole check was a silent no-op: it would
    never have raised even if the incident genuinely could fire on this
    list. Fixed by reading `canFireNow`."""
    with t.component("nightside_gate_blocks_on_minimal_list", beyond_toggle=True):
        t.set_setting(SETTINGS_TYPE, {"nightsideAuroraEnabled": True})
        r = t.bridge_call("jawa/storyteller_fire", incidentDef=DARK_AURORA,
                          dryRun=True)
        if not (r or {}).get("success"):
            raise ExpectationFailed(
                "jawa/storyteller_fire(%s, dryRun=True) failed to resolve the "
                "def at all: %r" % (DARK_AURORA, r))
        if r.get("canFireNow"):
            raise ExpectationFailed(
                "%s reported canFireNow=True on the minimal list with no "
                "PlanetGeometryDef loaded -- MapInNightsideBand should be "
                "unconditionally false: %r" % (DARK_AURORA, r))


@suite.chain("dark_aurora_condition_grants_the_paired_mood_thought")
def dark_aurora_condition_grants_the_paired_mood_thought(t):
    """Bypasses BOTH the incident gate and the geometry gate (same
    `jawa/game_condition` idiom as the terminator front chain) to register
    `RM_WS_DarkAurora` directly, then proves the mechanical half the walk
    doc's own bullet 12 calls a human-eyes-only judgment is actually NOT
    all cosmetic: the paired `ThoughtDef RM_WS_DarkAurora` (`workerClass
    ThoughtWorker_Aurora`, reused unchanged) is a real, situational,
    +14 mood grant to any pawn outdoors/unroofed/sighted while the
    condition is active -- read back via `jawa/pawn_thoughts`, which calls
    `Notify_SituationalThoughtsDirty()` first so this is not a stale-cache
    false negative."""
    t.clear_area(size=20)
    x, z = t.anchor
    pawn = t.spawn_pawn("Colonist", hostile=False)

    with t.component("dark_aurora_thought_grants_14_mood", beyond_toggle=True):
        r = t.bridge_call("jawa/game_condition", action="start",
                          condition=DARK_AURORA, durationTicks=60000)
        if not (r or {}).get("success"):
            raise ExpectationFailed(
                "jawa/game_condition(start, %s) failed: %r" % (DARK_AURORA, r))

        thoughts = t.bridge_call("jawa/pawn_thoughts", pawn=pawn)
        rows = (thoughts or {}).get("thoughts") or []
        match = next((th for th in rows if th.get("def") == DARK_AURORA), None)
        if match is None:
            raise ExpectationFailed(
                "no %s thought found on the colonist while the condition is "
                "active (pawn may be roofed/blind/indoors, or "
                "ThoughtWorker_Aurora's gating differs from vanilla Aurora's): "
                "%r" % (DARK_AURORA, rows))
        if abs(match.get("moodOffset", 0) - 14) > 0.01:
            raise ExpectationFailed(
                "%s thought's moodOffset is %r, expected 14 (ThoughtDefs_"
                "DarkAurora.xml stages[0].baseMoodEffect): %r"
                % (DARK_AURORA, match.get("moodOffset"), match))

        t.bridge_call("jawa/game_condition", action="end", condition=DARK_AURORA)
        t.screenshot()


@suite.chain("weather_instrument_reports_a_live_forecast_reading")
def weather_instrument_reports_a_live_forecast_reading(t):
    """`RM_WS_WeatherInstrument`'s `CompForecaster.CompInspectStringExtra()`
    always returns one of exactly three shapes (forced-weather line,
    ranked-forecast line, or "no clear signal") -- this chain does not pin
    which branch fires (that depends on the live biome/weather roll this
    suite does not control), only that the instrument produces its own
    "Instrument reading" line at all once spawned and selected."""
    t.clear_area(size=15)
    cells = t.spawn(INSTRUMENT, count=1, at="point")

    with t.component("forecaster_inspect_string_present", beyond_toggle=True):
        things = t.bridge_call("jawa/list_things", defName=INSTRUMENT)
        rows = (things or {}).get("things") or []
        if not rows:
            raise ExpectationFailed(
                "no %s found via jawa/list_things after spawning it" % INSTRUMENT)
        thing_id = rows[0].get("id")
        r = t.bridge_call("jawa/inspect_string", thingIds=thing_id)
        rows2 = (r or {}).get("things") or []
        lines = []
        for row in rows2 if isinstance(rows2, list) else []:
            lines.extend((row or {}).get("inspect") or [])
        text = "\n".join(str(l) for l in lines)
        if "Instrument reading" not in text:
            raise ExpectationFailed(
                "no 'Instrument reading' text in %s's inspect string: %r"
                % (INSTRUMENT, text))
        t.screenshot()
