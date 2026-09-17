"""validation.py -- modcheck suite for RimUtinni The Long Hunger
(mandrake.rut.longhunger).

Run with:

    python.exe src/RimMandrake/Utils/modcheck/cli.py run LongHunger

Grounded in all 3 Source/*.cs files (read whole -- ~100, ~150 and ~65
lines respectively) and all 4 Defs/**/*.xml files, plus the relevant slice
of `Defs/QuestScriptDefs/Quest_LongHunger.xml`. `Source/LongHungerMod.cs`'s
own header names its house style precedent (`GelatinousSlime/Source/
SlimeMod.cs`) and documents WHY disabling the encounter is a safe no-op:
the quest's `QuestNode_CreateIncidents` and `QuestNode_Delay` are parallel
nodes, not sequenced, so the salvage contract fee pays out on its own timer
regardless of whether `RUT_LongHungerSurfaces` ever fires.

THE WALK DOC NAMES A TOOL THAT DOES NOT EXIST -- checked, not assumed:
step 7 says `rimworld/spawn_thing {defName, x, z}`. `grep -rn
"rimworld/spawn_thing"` across every file in `src/RimMandrake/bridgetools/
JawaBench.BridgeTools/` returns nothing -- no tool by that name is
registered anywhere. The real primitive for this is `jawa/spawn_batch`
(the same tool the TestContext's own `t.spawn()` verb calls), used below
directly so an exact offset from the anchor can be given -- a plain
vanilla `Wall`, 2 cells from `RUT_LongHunger`'s own cell, both inside
`EruptionRadius`/`PulseRadius` -- rather than the anchor-only cell math
`t.spawn()` itself does.

A REAL BUG FOUND WHILE GROUNDING THIS SUITE, recorded per this mod's own
comment rather than guessed: `LongHungerThing.SpawnSetup`'s comment
documents that `nextPulseAt`'s field initializer used the raw
`PulseIntervalTicks` constant (600), NOT the `durationMultiplier`-scaled
value `Tick()` computes for every later pulse -- so the FIRST tremor always
fired at the unscaled 600 ticks regardless of the settings slider. The
`.cs` says this was FIXED (recomputed in `SpawnSetup` before the first
tick), which this suite's `first_pulse_respects_duration_multiplier`
component below is the first thing to actually exercise live.

Still not proven / structurally offline-only:
  1. `eruption_tremor_submerge_lifecycle`'s wait of ~2600 ticks (enough to
     cross `SurfacedDurationTicks`=2500 at the default `durationMultiplier`
     =1) has never been run live -- the real wall-clock cost of that many
     `step_game_ticks` on a quicktest map is unmeasured (Ninefold's own
     validation.py flags the same category of gap for its own long wait).
  2. The eruption/tremor explosions are proven via a nearby Wall's
     hitpoints dropping or the wall being destroyed outright (chosen over
     a pawn, unlike Armoury's own ion-damage pattern, specifically to
     avoid a pawn's death/despawn state machine confounding the read) --
     this proves damage happened, not that the exact radius/damage/
     DamageDefOf.Bomb values match (90/45, radii 4.5/3). No bridge tool
     reads `GenExplosion`'s own applied radius or damage type back, so
     those exact numbers are read from the .cs and asserted nowhere live.
  3. `RUT_DuneHaze` is confirmed atmosphere-only and NOT wired to the
     incident this pass, per `WeatherDefs_LongHunger.xml`'s own header
     comment -- this suite checks the WeatherDef resolves with the
     documented fields, never that it fires alongside the encounter
     (there is no such link to test yet).
  4. Walk step 9 (human pass: the borrowed PitGate VFX/art reads as
     intentional) is out of scope for a scripted suite.
"""
from modcheck import Suite, ExpectationFailed

suite = Suite("LongHunger")
suite.toggles = ["encounterEnabled", "damageMultiplier", "durationMultiplier",
                 "lootValueMultiplier"]

SETTINGS_TYPE = "LongHunger.LongHungerSettings"
LONG_HUNGER_THING = "RUT_LongHunger"
GROUNDCALLER = "RUT_Groundcaller"
INCIDENT = "RUT_LongHungerSurfaces"

BOOT_ERROR_NEEDLES = [
    "Config error in mandrake.rut.longhunger",
    "ThingDefs_LongHunger.xml", "IncidentDefs_LongHunger.xml",
    "Quest_LongHunger.xml", "WeatherDefs_LongHunger.xml",
]


@suite.chain("load_clean")
def load_clean(t):
    """Walk step 1."""
    with t.component("no_config_or_xml_errors", beyond_toggle=True):
        r = t.bridge_call("jawa/drain_log", limit=400, errorsOnly=True)
        msgs = [m.get("text", "") for m in ((r or {}).get("messages") or [])]
        joined = "\n".join(msgs)
        hits = [n for n in BOOT_ERROR_NEEDLES if n in joined]
        if hits:
            raise ExpectationFailed(
                "error log contains LongHunger-related needle(s) %r: %r"
                % (hits, msgs))


@suite.chain("defs_resolve_as_documented")
def defs_resolve_as_documented(t):
    """Walk steps 2-6: every def field the walk doc's own 'must be true'
    section claims, read back live."""
    with t.component("longhunger_thingdef_fields", beyond_toggle=True):
        r = t.bridge_call("jawa/get_defs", defs="ThingDef/%s" % LONG_HUNGER_THING,
                          fields="thingClass,statBases")
        blob = str(r)
        if "LongHungerThing" not in blob or "2000" not in blob:
            raise ExpectationFailed(
                "RUT_LongHunger thingClass/statBases.MaxHitPoints did not "
                "read back as expected (LongHunger.LongHungerThing, 2000): %r" % r)

    with t.component("groundcaller_thingdef_fields", beyond_toggle=True):
        r = t.bridge_call("jawa/get_defs", defs="ThingDef/%s" % GROUNDCALLER,
                          fields="costList,minifiedDef", deep=True)
        blob = str(r)
        for needle in ("Steel", "60", "ComponentIndustrial", "2", "MinifiedThing"):
            if needle not in blob:
                raise ExpectationFailed(
                    "RUT_Groundcaller costList/minifiedDef missing expected "
                    "%r: %r" % (needle, r))

    with t.component("incident_def_fields", beyond_toggle=True):
        r = t.bridge_call("jawa/get_defs", defs="IncidentDef/%s" % INCIDENT,
                          fields="baseChance,workerClass,minThreatPoints,maxThreatPoints")
        blob = str(r)
        for needle in ("0", "IncidentWorker_LongHungerSurfaces", "99999"):
            if needle not in blob:
                raise ExpectationFailed(
                    "RUT_LongHungerSurfaces fields missing expected %r: %r"
                    % (needle, r))

    with t.component("quest_and_weather_def_fields", beyond_toggle=True):
        r = t.bridge_call("jawa/get_defs", defs="QuestScriptDef/RUT_LongHungerContract",
                          fields="rootSelectionWeight,expireDaysRange", deep=True)
        blob = str(r)
        if "0.4" not in blob:
            raise ExpectationFailed(
                "RUT_LongHungerContract.rootSelectionWeight did not read back "
                "as 0.4: %r" % r)
        w = t.bridge_call("jawa/get_defs", defs="WeatherDef/RUT_DuneHaze",
                          fields="isBad,favorability")
        wblob = str(w)
        if "Bad" not in wblob:
            raise ExpectationFailed(
                "RUT_DuneHaze isBad/favorability did not read back as "
                "true/Bad: %r" % w)
        t.screenshot()


@suite.chain("encounter_toggle_gates_canfire")
def encounter_toggle_gates_canfire(t):
    """Behavioral proof via `jawa/fire_incident(dryRun=True)`, which reads
    `IncidentWorker_LongHungerSurfaces.CanFireNowSub`'s real return value
    (`canFireNow` in the tool's own result) WITHOUT actually spawning
    anything -- `encounterEnabled=false` must make `canFireNow` false
    regardless of whether a valid cell exists; restoring it should make
    `canFireNow` true (assuming this quicktest map has a standable,
    unfogged cell near its center, which every quicktest map should)."""
    with t.component("encounter_disabled_blocks_canfirenow", toggle="encounterEnabled"):
        t.set_setting(SETTINGS_TYPE, {"encounterEnabled": False})
        r_off = t.bridge_call("jawa/fire_incident", incidentDef=INCIDENT, dryRun=True)
        can_off = (r_off or {}).get("canFireNow")
        if can_off is not False:
            raise ExpectationFailed(
                "encounterEnabled=false but fire_incident(dryRun=True) "
                "reports canFireNow=%r, expected False: %r" % (can_off, r_off))

        t.set_setting(SETTINGS_TYPE, {"encounterEnabled": True})
        r_on = t.bridge_call("jawa/fire_incident", incidentDef=INCIDENT, dryRun=True)
        can_on = (r_on or {}).get("canFireNow")
        if can_on is not True:
            raise ExpectationFailed(
                "encounterEnabled=true but fire_incident(dryRun=True) "
                "reports canFireNow=%r, expected True (map may lack a "
                "standable/unfogged cell near its center): %r" % (can_on, r_on))


def _wall_hp(t, x, z):
    """The wall's own (present, hitPoints) at a small rect around (x, z),
    or (False, None) if it is gone (destroyed outright -- also valid
    evidence of damage, handled by the caller)."""
    r = t.bridge_call("jawa/list_things", defName="Wall",
                      rect="%d,%d,3,3" % (x - 1, z - 1))
    rows = (r or {}).get("things") or []
    if not rows:
        return False, None
    return True, rows[0].get("hitPoints")


@suite.chain("eruption_tremor_submerge_lifecycle")
def eruption_tremor_submerge_lifecycle(t):
    """Walk steps 7-8, using `t.bridge_call("jawa/spawn_batch", ...)` (see
    module docstring on why not the walk's own named, nonexistent
    `rimworld/spawn_thing`) to place `RUT_LongHunger` at the anchor and a
    plain vanilla `Wall` 2 cells away -- inside both `EruptionRadius` (4.5)
    and `PulseRadius` (3), but not on the same cell, so the wall survives
    to be read rather than risking a pawn's death/despawn state machine
    (Armoury's own ion-damage chain uses a pawn; a stationary Thing's
    hitpoints are a strictly simpler signal here). Submerge is proven via
    the thing's disappearance AND at least one new item appearing near its
    former cell."""
    t.clear_area(size=30)
    x, z = t.anchor
    wall_x, wall_z = x + 2, z

    with t.component("eruption_damages_nearby_wall", beyond_toggle=True):
        t.bridge_call("jawa/spawn_batch", ops="Wall:%d,%d" % (wall_x, wall_z))
        present0, hp_before = _wall_hp(t, wall_x, wall_z)
        if not present0 or hp_before is None:
            raise ExpectationFailed(
                "test Wall not found/no hitPoints at (%d,%d) right after "
                "spawning it" % (wall_x, wall_z))

        t.bridge_call("jawa/spawn_batch", ops="%s:%d,%d" % (LONG_HUNGER_THING, x, z))
        present = t.bridge_call("jawa/list_things", defName=LONG_HUNGER_THING)
        if not (present or {}).get("things"):
            raise ExpectationFailed(
                "RUT_LongHunger not found on the map immediately after spawn: %r"
                % present)

        present1, hp_after = _wall_hp(t, wall_x, wall_z)
        if present1 and hp_after is not None and hp_after >= hp_before:
            raise ExpectationFailed(
                "nearby Wall's hitPoints did not drop after RUT_LongHunger "
                "spawned (%r -> %r, still present=%s) -- SpawnSetup's "
                "eruption GenExplosion may not have fired"
                % (hp_before, hp_after, present1))
        # present1=False (wall destroyed outright by the eruption) is ALSO
        # valid evidence of damage -- not a failure.
        t.screenshot()

    with t.component("submerges_and_drops_loot", beyond_toggle=True):
        # ~2600 ticks: SurfacedDurationTicks=2500 at the default
        # durationMultiplier=1, plus margin. See module docstring gap #1 --
        # this wall-clock cost has never been measured live.
        t.wait_ticks(2600)
        remaining = t.bridge_call("jawa/list_things", defName=LONG_HUNGER_THING)
        if (remaining or {}).get("things"):
            raise ExpectationFailed(
                "RUT_LongHunger still present after 2600 ticks -- Submerge() "
                "either did not run or ran later than SurfacedDurationTicks "
                "documents: %r" % remaining)
        nearby_items = t.bridge_call("jawa/list_things",
                                     rect="%d,%d,10,10" % (x - 5, z - 5))
        count = len((nearby_items or {}).get("things") or [])
        if count < 1:
            raise ExpectationFailed(
                "no items found near (%d,%d) after submerge -- Reward_"
                "ItemsStandard loot generation may not have run: %r"
                % (x, z, nearby_items))
        r = t.bridge_call("jawa/drain_log", limit=100, errorsOnly=True)
        msgs = [m.get("text", "") for m in ((r or {}).get("messages") or [])]
        hits = [m for m in msgs if "LongHungerThing" in m]
        if hits:
            raise ExpectationFailed(
                "error log mentions LongHungerThing after the lifecycle "
                "ran: %r" % hits)
        t.screenshot()


@suite.chain("scaling_settings_flip")
def scaling_settings_flip(t):
    """Set+readback only for the 3 float sliders (Droidworks' own
    register: "sliders are tuning, not independently toggle-tested here").
    `first_pulse_respects_duration_multiplier` below is the one exception
    that DOES behaviorally exercise a slider, because it targets the
    specific bug the .cs's own comment documents fixing."""
    with t.component("scaling_multiplier_settings_flip", beyond_toggle=True):
        t.set_setting(SETTINGS_TYPE, {"damageMultiplier": 2.0})
        t.set_setting(SETTINGS_TYPE, {"damageMultiplier": 1.0})
        t.set_setting(SETTINGS_TYPE, {"lootValueMultiplier": 2.0})
        t.set_setting(SETTINGS_TYPE, {"lootValueMultiplier": 1.0})


@suite.chain("first_pulse_respects_duration_multiplier")
def first_pulse_respects_duration_multiplier(t):
    """Targets the exact bug `LongHungerThing.SpawnSetup`'s own comment
    documents fixing: with `durationMultiplier=3`, the FIRST tremor should
    wait ~1800 ticks (600*3), not the unscaled 600. The eruption itself
    (immediate, unrelated to this bug) is let happen and settle first; a
    FRESH wall is then placed and its hitpoints tracked ONLY across the
    700-tick window that follows -- past the unscaled 600-tick interval,
    well short of the scaled ~1800. If the fix regressed, a pulse landing
    at the unscaled 600 mark would damage or destroy this fresh wall inside
    that window."""
    t.clear_area(size=30)
    x, z = t.anchor
    wall_x, wall_z = x + 2, z

    with t.component("no_early_pulse_with_multiplier_3", toggle="durationMultiplier"):
        t.set_setting(SETTINGS_TYPE, {"durationMultiplier": 3.0})
        t.bridge_call("jawa/spawn_batch", ops="%s:%d,%d" % (LONG_HUNGER_THING, x, z))
        t.wait_ticks(5)   # let the immediate eruption's dust settle
        t.bridge_call("jawa/spawn_batch", ops="Wall:%d,%d" % (wall_x, wall_z))
        present0, hp_before = _wall_hp(t, wall_x, wall_z)
        if not present0 or hp_before is None:
            raise ExpectationFailed(
                "fresh test Wall not found/no hitPoints at (%d,%d) right "
                "after spawning it" % (wall_x, wall_z))

        t.wait_ticks(700)   # total ticksSinceSpawn now ~705 -- past the
                            # UNSCALED 600-tick mark, short of the scaled ~1800
        present1, hp_after = _wall_hp(t, wall_x, wall_z)
        t.set_setting(SETTINGS_TYPE, {"durationMultiplier": 1.0})

        if not present1:
            raise ExpectationFailed(
                "fresh Wall was destroyed within the 700-tick window at "
                "durationMultiplier=3 -- a pulse landed near the UNSCALED "
                "600-tick mark, which is exactly the bug this .cs "
                "documents fixing")
        if hp_after is not None and hp_after < hp_before:
            raise ExpectationFailed(
                "fresh Wall took damage within the 700-tick window at "
                "durationMultiplier=3 (%r -> %r) -- the first-pulse-uses-"
                "raw-constant bug this .cs documents fixing may have "
                "regressed" % (hp_before, hp_after))
