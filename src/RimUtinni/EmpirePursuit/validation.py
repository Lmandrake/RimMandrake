"""validation.py -- modcheck suite for RimUtinni Empire Pursuit -- Survey
Shadow (mandrake.rut.empirepursuit).

Grounded in the mod's actual Source, read whole before writing this:
`RuthlessPursuingMechanoids.cs` (the ScenPart -- timers, endless waves,
`UpdateDisabled`'s relations gate, and `ShadowMultiplier`, the ONE piece of
this fork's own logic laid over an otherwise-unchanged upstream port),
`ScenPartDef_RuthlessPursuit.cs` (the `surveyShadowBiomes`/
`surveyShadowMultiplier` fields this def carries, per owner-rules-must-be-
data), `HarmonyPatches.cs` (the single postfix on
`IncidentWorker_RaidEnemy.FactionCanBeGroupSource`), `Utilities.cs`
(`DebugUtility.DebugLog`, gated on `RFPSettings.printDebug`), and
`Settings.cs` (the ONE real Mod Settings field, `printDebug`) -- plus the
mod's own `Defs/Scenarios/ScenParts_EmpirePursuit.xml` (the shipped
`RUT_RuthlessPursuingMechanoids` def: `surveyShadowMultiplier=4`,
`surveyShadowBiomes=[AB_RockyCrags]`) and `About.xml` (Odyssey +
brrainz.harmony deps, `incompatibleWith matathias.ruthlessmechanoids` --
the upstream mod this REPLACES via an identical namespace/defName/
scenPartClass, per that file's own header comment).

THIS MOD IS A FORK, and the docstring register reflects that: every method
whose body has a `/* Ported unchanged ... */` or `/* Ported from ... */`
header comment (`RFPSettings`/`RFPMod`, `HarmonyPatcher`+its one postfix,
`DebugUtility`/`CommonUtil`) is upstream's own code, untouched; the ONE
piece that is genuinely this fork's own design is `ShadowMultiplier(Map)`
and the two call sites in `StartTimers` that multiply the raid/warning
delay by it when `def is ScenPartDef_RuthlessPursuit` and the map's biome
is on the owner-editable list (EMPIRE_PURSUIT_SURVEY_SHADOW_1). This suite
weights its coverage accordingly: the survey-shadow mechanism gets the
closest reading, upstream's ported behavior gets proven at the level the
walk doc already scoped it to.

Only ONE real ModSettings field exists (`RFPSettings.printDebug`, `public
static`) and it gates nothing but `DebugUtility.DebugLog`'s own verbosity
-- `suite.toggles = ["printDebug"]`, covered by a bare flip+read-back
(`toggle_flips` below), not a behavioral chain, because it has no behavior
of its own to prove.

WHY `jawa/scenario_part_add`/`jawa/scenario_parts_get`/`jawa/alerts_list`
ARE USED DESPITE NOT BEING INDEPENDENTLY CONFIRMED HERE: unlike
`jawa/raid_preview` (confirmed live in `skills/rimbridge/SKILL.md`'s own
tool table) and `jawa/letter_list` (confirmed live in
`ShipMemory/validation.py`), no other suite in this family and no
`skills/rimbridge/references/*.md` page names these three tools by exact
name. They come from `design/validation_walks/RimUtinni/EmpirePursuit.md`
itself, written with the exact call shape (`className=`, `defName=`,
`fields="k=v;k=v"`, `initCalls="PostWorldGenerate;PostMapGenerate"`,
`allowDuplicate=true`) needed to add a scenario part and force its two
init hooks post-hoc -- a documented, non-trivial requirement this mod's
OWN code states plainly (a part added mid-game never gets
`PostWorldGenerate`/`PostMapGenerate` from the engine, so its timer dicts
stay empty and it never fires). This suite follows the walk doc's exact
shape rather than guessing a different one, but flags the tool names
themselves as UNCONFIRMED against any other grounded source in this repo
-- a first live run may need to correct the parameter names.

WHAT THIS SUITE CANNOT COVER, per the walk doc's own step 11, and why:
the `AB_RockyCrags` (Alpha Biomes "Forsaken Crags") survey-shadow multiplier
itself needs a live map generated on that specific biome, which needs
Alpha Biomes active -- outside `minimal+harmony`, the walk doc's own
declared environment for this mod (Odyssey is an owned DLC, Harmony is the
one genuine third-party dependency; Alpha Biomes is neither). `ShadowMultiplier`
returning `1f` for every OTHER biome is implicitly exercised by every other
chain below (none of them touch `AB_RockyCrags`), but the x4 branch itself
is UNCOVERED here -- a genuine gap, not an oversight. `DebugUtility.DebugLog`
is also gated behind `RFPSettings.printDebug` (default off, no known bridge
control to flip a log VERBOSITY setting mid-run distinct from the settings
flip this suite already does structurally), so this suite reads outcomes
(letters, alerts, def fields) rather than debug-log lines, per the walk's
own note.

Still not proven / likely first-live-run corrections:
  1. Step 3's `fields="pursuitFactionDef=Mechanoid;firstRaidDelayHours=1;..."`
     assumes `jawa/scenario_part_add` can set a `FactionDef`-typed field
     (`pursuitFactionDef`) by its defName string the same way it sets an
     int/bool field -- not independently confirmed.
  2. `raid_timers_fire`'s `wait_ticks(5000)` is sized off the walk doc's own
     reasoning (past `TickInterval`=2500 and past the 1-hour
     `firstRaidDelayHours` set at scenario-part-add time) -- untested at
     this specific scale in this suite family.
  3. `jawa/alerts_list`'s exact return shape (a list of active alert class
     names? labels?) is assumed to include `Alert_PursuitFactionThreat`'s
     class or label verbatim; not independently confirmed.
"""
from modcheck import Suite, ExpectationFailed

suite = Suite("EmpirePursuit")
suite.toggles = ["printDebug"]

SCEN_CLASS = "RuthlessPursuingMechanoids.ScenPart_RuthlessPursuingMechanoids"
SCEN_DEF = "RUT_RuthlessPursuingMechanoids"
SETTINGS_TYPE = "RuthlessPursuingMechanoids.RFPSettings"


def _add_part(t, fields, allow_duplicate=False):
    return t.bridge_call(
        "jawa/scenario_part_add", className=SCEN_CLASS, defName=SCEN_DEF,
        fields=fields, initCalls="PostWorldGenerate;PostMapGenerate",
        allowDuplicate=allow_duplicate, dryRun=False)


@suite.chain("scen_part_def_readback")
def scen_part_def_readback(t):
    """The def-level side of the fork's own mechanism (survey shadow) --
    the ONLY genuinely new content this mod ships, per module docstring."""
    t.clear_area(size=10)
    with t.component("ruthless_pursuit_def_resolves", beyond_toggle=True):
        r = t.bridge_call(
            "jawa/get_defs", defs="ScenPartDef/%s" % SCEN_DEF,
            fields="scenPartClass,surveyShadowMultiplier,surveyShadowBiomes")
        rows = (r or {}).get("defs", (r or {}).get("results", [])) or []
        row = next((d for d in rows if d.get("defName") == SCEN_DEF), None)
        fields = (row or {}).get("fields") or {}

        got_class = fields.get("scenPartClass", "")
        ok_class = got_class == SCEN_CLASS
        t._record("scenPartClass -> %r" % got_class, ok_class)
        if not ok_class:
            raise ExpectationFailed(
                "%s.scenPartClass = %r, expected %r" % (SCEN_DEF, got_class, SCEN_CLASS))

        got_mult = fields.get("surveyShadowMultiplier", "(no such field)")
        ok_mult = str(got_mult) == "4"
        t._record("surveyShadowMultiplier -> %r" % got_mult, ok_mult)
        if not ok_mult:
            raise ExpectationFailed(
                "%s.surveyShadowMultiplier = %r, expected 4" % (SCEN_DEF, got_mult))

        got_biomes = fields.get("surveyShadowBiomes", "")
        ok_biomes = "AB_RockyCrags" in str(got_biomes)
        t._record("surveyShadowBiomes -> %r" % got_biomes, ok_biomes)
        if not ok_biomes:
            raise ExpectationFailed(
                "%s.surveyShadowBiomes = %r, expected to contain AB_RockyCrags"
                % (SCEN_DEF, got_biomes))


@suite.chain("scenario_part_lifecycle")
def scenario_part_lifecycle(t):
    """Adds the part with fast timers (1h raid delay, 1h warning delay, no
    variance) and BOTH init calls the mod's own code says are mandatory for
    a part added outside scenario creation (`PostWorldGenerate` seeds
    `PursuitFaction`/clears the timer dicts; `PostMapGenerate` calls
    `StartTimers` for the current map) -- then reads the part straight back."""
    with t.component("part_added_with_fast_timers", beyond_toggle=True):
        r = _add_part(t, "pursuitFactionDef=Mechanoid;firstRaidDelayHours=1;"
                         "firstRaidDelayVarianceHours=0;warningDelayHours=1;"
                         "warningDelayVarianceHours=0;canDoNormalRaid=false")
        ok = bool((r or {}).get("success"))
        t._record("scenario_part_add(%s) -> success=%s" % (SCEN_DEF, ok), ok)
        if not ok:
            raise ExpectationFailed(
                "jawa/scenario_part_add(%s) did not report success: %r" % (SCEN_DEF, r))

    with t.component("part_readback_matches", beyond_toggle=True):
        r = t.bridge_call("jawa/scenario_parts_get")
        parts = (r or {}).get("parts") or []
        part = next((p for p in parts if p.get("defName") == SCEN_DEF), None)
        ok = part is not None and str(part.get("firstRaidDelayHours")) == "1" \
             and str(part.get("canDoNormalRaid")).lower() == "false"
        t._record("scenario_parts_get -> %r" % part, ok)
        if not ok:
            raise ExpectationFailed(
                "the added %s part did not read back with "
                "firstRaidDelayHours=1, canDoNormalRaid=false: %r" % (SCEN_DEF, part))


@suite.chain("normal_raid_pool_gate_flips_both_ways")
def normal_raid_pool_gate_flips_both_ways(t):
    """`IncidentWorker_RaidEnemy_FactionCanBeGroupSource`'s postfix
    (HarmonyPatches.cs) excludes the pursuit faction from ordinary raid
    selection unless `canDoNormalRaid` is true -- proven in BOTH
    directions, per the walk doc's own step 9, rather than only the
    default-off case (which a broken postfix that always returns true
    could pass by coincidence)."""
    with t.component("mechanoid_excluded_when_canDoNormalRaid_false", beyond_toggle=True):
        r = t.bridge_call("jawa/raid_preview", points=2000)
        factions = (r or {}).get("factions") or (r or {}).get("hostileFactions") or []
        names = [f.get("defName", f) if isinstance(f, dict) else f for f in factions]
        ok = "Mechanoid" not in names
        t._record("raid_preview(2000) factions -> %r" % names, ok)
        if not ok:
            raise ExpectationFailed(
                "Mechanoid appears in raid_preview's hostile factions with "
                "canDoNormalRaid=false, expected it excluded: %r" % names)

    with t.component("mechanoid_included_when_canDoNormalRaid_true", beyond_toggle=True):
        r = _add_part(t, "canDoNormalRaid=true", allow_duplicate=True)
        if not (r or {}).get("success"):
            raise ExpectationFailed(
                "jawa/scenario_part_add(canDoNormalRaid=true, allowDuplicate=true) "
                "did not report success: %r" % r)
        r2 = t.bridge_call("jawa/raid_preview", points=2000)
        factions = (r2 or {}).get("factions") or (r2 or {}).get("hostileFactions") or []
        names = [f.get("defName", f) if isinstance(f, dict) else f for f in factions]
        ok = "Mechanoid" in names
        t._record("raid_preview(2000) factions after canDoNormalRaid=true -> %r"
                  % names, ok)
        if not ok:
            raise ExpectationFailed(
                "Mechanoid still excluded from raid_preview after adding a "
                "canDoNormalRaid=true part -- the postfix's true-branch is "
                "not confirmed: %r" % names)


@suite.chain("raid_and_warning_timers_fire")
def raid_and_warning_timers_fire(t):
    """Advances the paused game 5000 ticks (past TickInterval=2500 and past
    the 1-hour firstRaidDelayHours set in `scenario_part_lifecycle`) and
    checks BOTH outcomes the walk doc names: a raid-incoming letter on the
    stack (or a raid having already fired) and the pursuit alert active."""
    t.wait_ticks(5000)

    with t.component("raid_timer_tripped", beyond_toggle=True):
        r = t.bridge_call("jawa/letter_list")
        letters = (r or {}).get("letters") or []
        labels = [l.get("label", "") for l in letters]
        ok = any("mechanoid" in (l or "").lower() or "ruthless" in (l or "").lower()
                for l in labels)
        t._record("letter_list labels -> %r" % labels, ok)
        if not ok:
            raise ExpectationFailed(
                "no mechanoid/ruthless-pursuit letter found after 5000 ticks "
                "past a 1-hour raid delay; letter_list had: %r" % labels)

    with t.component("pursuit_alert_active", beyond_toggle=True):
        r = t.bridge_call("jawa/alerts_list")
        alerts = (r or {}).get("alerts") or []
        names = [a.get("defName", a.get("label", a)) if isinstance(a, dict) else a
                for a in alerts]
        ok = any("pursuit" in str(n).lower() for n in names)
        t._record("alerts_list -> %r" % names, ok)
        if not ok:
            raise ExpectationFailed(
                "no pursuit-threat alert active after the warning window "
                "should have passed; alerts_list had: %r" % names)
        t.screenshot()


@suite.chain("toggle_flips")
def toggle_flips(t):
    """`RFPSettings.printDebug` is `public static`
    (BRIDGE_STATIC_SETTINGS_FIELDS_1 shape) and gates nothing but
    `DebugUtility.DebugLog`'s own verbosity -- a bare flip+read-back is
    the entirety of what is worth proving about it."""
    with t.component("printDebug_flips", toggle="printDebug"):
        t.set_setting(SETTINGS_TYPE, {"printDebug": True})
        t.set_setting(SETTINGS_TYPE, {"printDebug": False})
