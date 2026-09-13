"""validation.py -- modcheck suite for RimMandrake: Structure Injections
(mandrake.rm.injections).

Never deployed (deploy_custom_mods.py excludes `.py` wholesale). Run with:

    python.exe src/RimMandrake/Utils/modcheck/cli.py run StructureInjections

Grounded in the mod's actual source, read whole before writing this:
`RM_StructureInjectionsMod.cs` for the ONE real settings toggle
(`enabled`); `GenStep_RimplacePlan.cs`/`RimplacePlan.cs` for the replay
engine actually under test (CLEAR -> foundation -> terrain -> things
(transmitters before connectors) -> RUN -> roof -> PAWN, an ordering the
class's own comments say is "not a style choice -- it is what the live
path proved necessary"); `StructureInjectionsDebugActions.cs` for the two
ToolMap debug actions this suite drives (`Run plan: dwelling_test.txt`,
`Run plan: moisture_farm_test.txt`) and the `[RMInjectDebug] RAN ...`
summary log line they emit; and both `Templates/*.txt` plan files
themselves, read whole and counted by directive
(`grep -c '^THING\\t' ...`, not guessed) to ground every exact-count
expectation below in the actual file content, not an assumption about it.

A REAL, MOD-SPECIFIC FLOOR GAP -- `enabled` is UNREACHABLE by anything
this mod ships, not merely untested: `RM_StructureInjectionsSettings.
enabled` is checked ONLY inside `GenStep_RimplacePlan.Generate()` (the
real mapgen entry point) -- the debug action this suite otherwise relies
on calls `GenStep_RimplacePlan.ApplyPlan()` directly (the shared "replay
the plan" method Generate() itself calls into AFTER the enabled check),
bypassing that check entirely, by the debug action's own design (its
comment: "so both exercise the identical ordering logic"). And per this
mod's own About.xml, "This mod ships no content of its own" -- there is
no `Defs/` folder at all here (checked: `find Defs` on this mod's tree
returns nothing) and therefore no `TileMutatorDef`/`LandmarkDef` anywhere
in THIS mod that would ever put a `GenStepDef` carrying `GenStep_
RimplacePlan` in front of a real map generation to hit `Generate()` at
all. `enabled` is a real, wired ModSettings field with genuinely nothing
in this mod's own shipped content that would ever reach it. The toggle is
therefore UNCOVERED -- see the "NOT a chain" register at the end of this
file (BENCH edit 2026-09-13; the draft's set_setting write+read-back was
shelved on the known static-field bridge limitation,
BRIDGE_STATIC_SETTINGS_FIELDS_1).

WHY BOTH `replay_*` CHAINS USE THE DEBUG ACTION'S OWN SUMMARY LOG
(`[RMInjectDebug] RAN ...`) FOR THE BULK OF THE PROOF, PLUS ONE
`jawa/list_things` SPOT CHECK EACH: the summary line reports
`plan.Foundation/Terrain/Things/Roof.Count` -- exact, since it comes from
parsing the plan file, regardless of whether any individual directive
actually resolved and placed something (a def that fails to resolve is
logged as its own `Log.Error` and skipped, per `RunItem`'s catch, but
still counted going in). `thingsSpawned` (`after - before` on
`map.listerThings.AllThings.Count`) is the one field in that line that
DOES reflect real placement, so it is the exact-count assertion that
actually proves something happened, not just that the file parsed --
backed up by one `jawa/list_things` spot check per plan for a real
placed Thing, because "the counts matched" and "specifically the RIGHT
things landed in the RIGHT cells" are different claims. No independent
terrain/roof read-back tool was found grounded for this repo (unlike
FluidCanals' own bespoke `Report cell (RAW)` action) -- see "Still not
proven" item 1.

A GENUINE, CONFIRMED CROSS-MOD DEPENDENCY RISK in `moisture_farm_test.txt`
(not a guess -- grepped): its six `KotOR_MoistureVaporator_big` THING
lines resolve to a ThingDef defined in `src/RimStarWars/Armoury/Defs/
Absorbed_KotorCore/ThingDefs_Buildings/Absorbed_KotorCore_Building_
MoistureVaporators.xml` -- the RimStarWars-tier Armoury mod, not this one,
and not part of "minimal mechanism list + the mod under test" (spec
Sec"Environment"). On a minimal modcheck run without Armoury loaded, those
six lines will resolve to `DefDatabase<ThingDef>.GetNamedSilentFail() ==
null`, each logging its own `Log.Error` and contributing 0 to
`thingsSpawned` (`SpawnThing`'s own null-def guard, called from
`ApplyPlan`'s `byPriority` filter). `replay_moisture_farm_plan` below
asserts `thingsSpawned` with that shortfall built in, not an exact match.

Still not proven / likely first-live-run corrections:
  1. Neither template plan actually contains a bound
     transmitter+connector pair (the ordering guarantee `ApplyPlan`'s own
     comments are proudest of, "a connector ... binds to the nearest
     transmitter within ConnectMaxDist AT SPAWN") -- `dwelling_test.txt`'s
     things are all non-power-transmitting furniture, and
     `moisture_farm_test.txt`'s vaporators are the ones most likely to
     need this and are also the ones most likely to be ABSENT on a
     minimal run (see the dependency risk above). This suite therefore
     proves the replay COMPLETES in the documented order and places real
     things/terrain/roof, but does NOT independently prove the
     transmitters-before-connectors claim itself.
  2. No terrain or roof read-back exists in this suite (see the note
     above) -- `terrainCells`/`roofCells` matching the plan's own parsed
     count is not proof any specific cell's terrain/roof actually
     changed, only that the file parsed with that many lines and no
     exception aborted the replay before reaching them.
  3. (BENCH addition, 2026-09-13) `thingsSpawned` is a NET
     map.listerThings delta and DROPS when the plan's own CLEAR phase
     destroys plants or debris still standing in the footprint (project
     memory: a placement log's thingsSpawned "goes negative when a build
     clears plants"). `clear_area(size=50)` sweeps the anchor rect first,
     which should leave nothing to clear -- but if the dwelling chain's
     exact-match assertion fails LOW on first live run, suspect surviving
     plants in the footprint before suspecting the replay engine.
  4. `dx`/`dz` in `StructureInjectionsDebugActions.RunAt` is `clickedCell
     - FootprintX/Z` (not `GenStep_RimplacePlan.Generate()`'s own
     center-on-map math) -- confirmed by reading the debug action's own
     2026-09-02 fix comment, not assumed; both templates declare
     `FOOTPRINT 100 100 ...`, so clicking `t.anchor` (500, 500) is
     expected to land the plan's own (100,100) origin at (500,500) and
     everything else at a `+400,+400` offset from its authored
     coordinates -- arithmetic, not independently measured live.
"""
import re

from modcheck import Suite, ExpectationFailed

suite = Suite("StructureInjections")
suite.toggles = ["enabled"]

# Counted directly from the shipped template files (grep -c '^KEY\t' <file>,
# 2026-09-13), not guessed:
DWELLING_TERRAIN = 130
DWELLING_THINGS = 73
DWELLING_ROOF = 192
MOISTURE_TERRAIN = 9
MOISTURE_THINGS = 99
MOISTURE_ROOF = 25
MOISTURE_KOTOR_ITEMS = 6   # KotOR_MoistureVaporator_big lines -- Armoury-only def,
                           # not on a minimal modcheck run (see module docstring)


def _run_plan(t, label, x, z):
    return t.bridge_call("rimworld/execute_debug_action",
                         path="Actions\\T: Run plan: " + label, x=x, z=z)


def _thing_count(t, defName, rect):
    r = t.bridge_call("jawa/list_things", defName=defName, rect=rect)
    return len((r or {}).get("things") or [])


@suite.chain("replay_dwelling_plan")
def replay_dwelling_plan(t):
    """Run `dwelling_test.txt` (footprint 16x12, no foreign defs -- every
    ThingDef/TerrainDef/RoofDef it names is plain vanilla) at the anchor
    and prove the full replay actually placed things, not merely parsed
    the file."""
    t.clear_area(size=50)
    x, z = t.anchor
    _run_plan(t, "dwelling_test.txt", x, z)

    with t.component("dwelling_plan_replays_fully", beyond_toggle=True):
        t.expect_log_contains("dwelling_test.txt", field="foundationCells", value="0")
        t.expect_log_contains("dwelling_test.txt", field="terrainCells",
                              value=str(DWELLING_TERRAIN))
        t.expect_log_contains("dwelling_test.txt", field="things",
                              value=str(DWELLING_THINGS))
        t.expect_log_contains("dwelling_test.txt", field="roofCells",
                              value=str(DWELLING_ROOF))
        # thingsSpawned is the one field that reflects REAL placement
        # (map.listerThings delta), not just the parsed line count -- every
        # def dwelling_test.txt names is plain vanilla, so this should
        # match DWELLING_THINGS exactly with nothing dropped.
        t.expect_log_contains("dwelling_test.txt", field="thingsSpawned",
                              value=str(DWELLING_THINGS))
        # Spot check: plan THING Wall 100 100 -> anchor + (100-100, 100-100)
        # = the anchor cell itself (FOOTPRINT 100 100 ...).
        if t._guard():   # no-op under the offline declaration probe --
                         # see FluidCanals/validation.py's own note on why.
            if _thing_count(t, "Wall", "%d,%d,3,3" % (x - 1, z - 1)) < 1:
                raise ExpectationFailed(
                    "no Wall found near the anchor (%d,%d) after replaying "
                    "dwelling_test.txt (plan THING Wall 100 100 maps there)"
                    % (x, z))
            # Plan THING ElectricStove 113 110 -> (x+13, z+10).
            ex, ez = x + 13, z + 10
            if _thing_count(t, "ElectricStove", "%d,%d,3,3" % (ex - 1, ez - 1)) < 1:
                raise ExpectationFailed(
                    "no ElectricStove found near (%d,%d) after replaying "
                    "dwelling_test.txt (plan THING ElectricStove 113 110)"
                    % (ex, ez))
        t.screenshot()


@suite.chain("replay_moisture_farm_plan")
def replay_moisture_farm_plan(t):
    """Run `moisture_farm_test.txt` (footprint 20x20, a much larger and
    differently-shaped plan than dwelling_test.txt -- proves the engine is
    genuinely plan-agnostic, not tuned to one shape) at the anchor.
    `thingsSpawned` is asserted with the Armoury-only vaporator shortfall
    built in (module docstring's confirmed dependency risk), not as an
    exact match."""
    t.clear_area(size=50)
    x, z = t.anchor
    _run_plan(t, "moisture_farm_test.txt", x, z)

    with t.component("moisture_farm_plan_replays", beyond_toggle=True):
        t.expect_log_contains("moisture_farm_test.txt", field="foundationCells", value="0")
        t.expect_log_contains("moisture_farm_test.txt", field="terrainCells",
                              value=str(MOISTURE_TERRAIN))
        t.expect_log_contains("moisture_farm_test.txt", field="things",
                              value=str(MOISTURE_THINGS))
        t.expect_log_contains("moisture_farm_test.txt", field="roofCells",
                              value=str(MOISTURE_ROOF))
        if t._guard():   # see replay_dwelling_plan's own note on this guard
            line = None
            r = t.bridge_call("jawa/drain_log", limit=200,
                              contains="moisture_farm_test.txt")
            msgs = [m.get("text", "") for m in ((r or {}).get("messages") or [])]
            line = msgs[-1] if msgs else None
            m = re.search(r"thingsSpawned=(-?\d+)", line or "")
            spawned = int(m.group(1)) if m else None
            floor = MOISTURE_THINGS - MOISTURE_KOTOR_ITEMS
            if spawned is None or spawned < floor:
                raise ExpectationFailed(
                    "thingsSpawned expected >= %d (all %d plan things minus "
                    "the %d Armoury-only KotOR_MoistureVaporator_big lines "
                    "this minimal run cannot resolve), got %r (line=%r)"
                    % (floor, MOISTURE_THINGS, MOISTURE_KOTOR_ITEMS, spawned, line))
            # Spot check a plain-vanilla item the plan places once: plan
            # THING Door 110 108 -> (x+10, z+8).
            dx_, dz_ = x + 10, z + 8
            if _thing_count(t, "Door", "%d,%d,3,3" % (dx_ - 1, dz_ - 1)) < 1:
                raise ExpectationFailed(
                    "no Door found near (%d,%d) after replaying "
                    "moisture_farm_test.txt (plan THING Door 110 108)"
                    % (dx_, dz_))
        t.screenshot()


# NOT a chain: the `enabled` toggle is UNCOVERED, deliberately (edited by
# BENCH before the first live run, 2026-09-13). The draft proved it via a
# `t.set_setting` write+read-back that near-certainly fails on the known
# `public static`-field reflection limitation of `rimworld/update_mod_settings`
# (measured live on Pits, same declaration shape here) -- a component that
# fails every run on a KNOWN bridge gap keeps this mod permanently un-GREEN
# and blocks its playtest gate on the wrong culprit. Recorded on
# BRIDGE_STATIC_SETTINGS_FIELDS_1; restore the write+read-back component when
# the tool learns static fields. Mirrors Pits' own uncovered toggles:
# registered, not faked.
