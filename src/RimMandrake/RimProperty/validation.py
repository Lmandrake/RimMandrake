"""validation.py -- modcheck suite for RimMandrake RimProperty (mandrake.rm.property).

Never deployed (deploy_custom_mods.py excludes `.py` wholesale -- same
regression guard the Pits pilot's own docstring cites). Run with:

    python.exe src/RimMandrake/Utils/modcheck/cli.py run RimProperty

Grounded in the mod's actual source, read whole before writing this:
`PropertySettings.cs` for the FIVE Mod Settings toggles (its own comment
block enumerates them: perception/propagation, animal theft, theft hauler,
salvage claim fee, walkable commerce -- the claim engine itself is
deliberately left ungated, PropertySettings.cs's own comment explaining
RaidRedesigner's Patch_CaravanRobbed postfixes PropertyEngine.Fire);
`PropertyEngine.cs`/`ClaimEngine.cs`/`GameComponent_PropertyLedger.cs` for
the event-spine mechanism (TakingEvent -> ClaimEngine.ResolveClaim ->
IsAuthorized -> RecordTransfer/RollPerceptionAndPropagate); and the three
feature folders (AnimalTheft/, TheftHauler/, SalvageClaim/ +
WalkableCommerce/) for what each of the mod's four player/AI-facing verbs
actually does mechanically.

WHAT THIS MOD HAS NO BRIDGE ROUTE FOR AT ALL, offline (grep of the whole
Source/ tree for `DebugAction`/`Log.Message`/`Log.Warning` found exactly
ONE debug action in the entire mod -- `DebugActions_TheftHauler.cs`'s own
test harness -- versus Pits' purpose-built `[RMPitsDebug]` log-tag family):

  - SalvageClaim (`FloatMenuOptionProvider_PaySalvageClaim`) and
    WalkableCommerce (`FloatMenuOptionProvider_BuyMerchandise`) BOTH run
    their entire transaction (silver deduction + `PropertyEngine.Fire`)
    directly inside the float-menu option's own delegate -- there is no
    JobDef/JobDriver backing either verb (their own doc comments say so
    explicitly: "no JobDriver/JobDef at all"). `jawa/ordered_job` (the
    escape valve used below for the other two verbs) can only dispatch a
    JobDef; there is nothing to give it here, and no bridge tool exists to
    click a float-menu option directly. **Both toggles
    (`salvageClaimFeeEnabled`, `walkableCommerceEnabled`) are therefore
    UNCOVERED by any component in this suite -- a genuine floor gap, not an
    oversight** (matches the exact shape of Pits' own two uncovered
    toggles, `fallDamageEnabled`/`pitCellExposureEnabled`, and
    `modcheck.floor.uncovered()`'s own docstring: "callers ... decide
    whether an uncovered toggle is fatal to a run", never enforced by
    `load_validation` itself).
  - `perceptionEnabled` gates `PropertyEngine.RollPerceptionAndPropagate`
    (witness roll + `FactionRecord.RegisterWitness`), which has no getter,
    no debug action, and no log line anywhere in this mod -- its only
    observable trace is inside `GameComponent_PropertyLedger`'s private
    `factionRecords` dict, which nothing exposes to the bridge. The
    `theft_hauler_uninstall` chain below DOES exercise the code path that
    calls it (an unauthorized Strip), but has no way to tell whether the
    roll actually ran or was gated off -- so `perceptionEnabled` is ALSO
    left uncovered rather than faked with a component that can't actually
    distinguish on/off.

That leaves two of the five toggles covered: `animalTheftEnabled` and
`theftHaulerEnabled` (the latter honestly caveated below -- see
`theft_hauler_uninstall`'s own comment on what it does NOT prove).

WHY NEITHER CHAIN USES `t.set_setting`: `PropertySettings`'s fields are
ALL `public static` (same declaration shape Pits' `PitsSettings` used,
which the Pits pilot's FIRST LIVE RUN already proved breaks
`rimworld/update_mod_settings` -- "the bridge's reflection walks INSTANCE
fields on the ModSettings object" -- with the exact same "Could not resolve
field" refusal). Applying that already-learned lesson here rather than
re-discovering it live: neither chain calls `t.set_setting`, and both
toggles are exercised only in their DEFAULT (enabled) state, same as every
`toggle=`-tagged component in the Pits exemplar.

WHY `jawa/ordered_job` (not a debug action) IS THE VERB HERE: it dispatches
`RM_TheftHaulUninstall`/`RM_AnimalSteal` directly by JobDef, which bypasses
BOTH mods' own eligibility gates -- `FloatMenuOptionProvider_
TheftHaulUninstall.AppliesInt`'s `TheftHaulerExtension` marker check (no
pawn kind on the minimal mod list carries it: the only patch that grants it,
`Patches/TheftHauler/MuckrakerChassis_TheftHauler.xml`, is
MayRequire-gated on `mandrake.rsw.droidworks`, not on this list) and
`JobGiver_RM_{Trained,Wild}Steal`'s own `WildTheftExtension`/`RM_Steal`
trainable checks. This is deliberate, not an oversight: `DebugActions_
TheftHauler.cs`'s own doc comment says exactly this -- its harness "skips
the eligibility gate ... to prove the thing that IS uncertain:
JobDriver_TheftHaulUninstall.FinishedRemoving actually fires
PropertyEngine.Fire" -- and `jawa/ordered_job` reaches the same JobDriver
the same way, without needing Droidworks live. **Neither chain below proves
the eligibility gates themselves work** (that both toggles' float-menu
GATING is correct is therefore also unproven, on top of not being what
`toggle=` on these components claims to cover -- see each chain's own note).

Real defNames used, none guessed (checked via RimSage against the live
def index, not assumed from a name): `Turret_MiniTurret` (category
Building, `minifiedDef=MinifiedThing` => `Minifiable=true`, matching
`FloatMenuOptionProvider_TheftHaulUninstall`'s own gate); `MealSimple`
(category Item, Mass 0.44kg -- irrelevant here since bypassing
`AnimalTheftUtility.FindStealTarget`'s mass gate is exactly what ordering
the JobDef directly does); `Muffalo` (a real PawnKindDef); `Pirate`
(FactionDef, `requiredCountAtGameStart=1` -- a Pirate Faction instance is
guaranteed to exist in every generated world, so `faction="Pirate"` on
`jawa/set_thing_props` always resolves to a real Faction).

Still not proven / likely first-live-run corrections (per this suite's
own register, same practice as Pits):
  1. `jawa/set_thing_props(faction="Pirate")` on a freshly `jawa/spawn_batch`'d
     Building -- never exercised live. If a spawned Building already carries
     a Faction (e.g. player) by default, the pre-check below will surface
     that immediately as an ExpectationFailed rather than silently drift.
  2. Exact `wait_ticks` budgets (2400 for the uninstall+haul round trip,
     900 for the animal steal's goto+take+wander+drop) are estimates from
     reading `uninstallWork`/toil shapes, not measured against real tick
     rates -- same category of correction Pits' first live run made to its
     own `wait_ticks` values.
  3. Whether `HaulAIUtility.HaulToStorageJob` finds a valid destination on
     the minimal-mod quicktest map (no player stockpile zone) is unknown;
     `uninstall_fires_taking_event`'s expectation is written to hold either
     way (see its own comment) but that reasoning is untested.
  4. The core claim-fabric OUTCOME of both proven components (a Stolen
     ClaimRecord actually landing in `GameComponent_PropertyLedger`, with
     the right `ClaimBasis`) has no independent read-back channel and is
     NOT asserted -- only the physical/job-completion side effect is. Same
     limitation as item 1 in the "no bridge route at all" section above,
     scoped down to the two components that DO run.
"""
from modcheck import Suite, ExpectationFailed

suite = Suite("RimProperty")
suite.toggles = [
    "perceptionEnabled", "animalTheftEnabled", "theftHaulerEnabled",
    "salvageClaimFeeEnabled", "walkableCommerceEnabled",
]

THEFT_BUILDING_DEF = "Turret_MiniTurret"   # category Building, Minifiable (minifiedDef set)
STEAL_ITEM_DEF = "MealSimple"              # category Item, portable
THIEF_KIND = "Muffalo"                      # a real animal PawnKindDef


def _first_id(result, defName):
    rows = (result or {}).get("things") or []
    for row in rows:
        if row.get("def") == defName:
            return row.get("id")
    return None


def _first_faction(result, defName):
    rows = (result or {}).get("things") or []
    for row in rows:
        if row.get("def") == defName:
            return row.get("faction")
    return None


@suite.chain("theft_hauler_uninstall")
def theft_hauler_uninstall(t):
    """Spawn a Minifiable building, give it a Pirate claim (a Faction other
    than the acting colonist's own), and order the acting colonist to run
    `RM_TheftHaulUninstall` on it directly via `jawa/ordered_job` --
    bypassing `FloatMenuOptionProvider_TheftHaulUninstall`'s own
    `TheftHaulerExtension` gate entirely (see module docstring: no pawn
    kind on the minimal list carries that marker). This proves
    `JobDriver_TheftHaulUninstall.FinishedRemoving` actually fires
    `PropertyEngine.Fire(TakingAct.Strip)` and completes the real
    `MinifyUtility.Uninstall()` -- it does NOT prove the eligibility gate
    itself (that a plain colonist would never see this order in the real
    float menu) is correct; that is a live-Droidworks question this suite
    cannot answer offline.

    `toggle="theftHaulerEnabled"` is tagged for floor coverage on the
    mechanism this toggle's tooltip describes ("A pawn with the
    theft-hauler marker can ... uninstall and carry it off"), but note the
    toggle itself only gates the FLOAT MENU option
    (`AppliesInt` checks `PropertySettings.theftHaulerEnabled`) -- since
    this chain bypasses the float menu, it does not prove the toggle's own
    on/off effect, only the default-enabled mechanism underneath it.
    """
    t.clear_area(size=24)
    x, z = t.anchor
    rect = "%d,%d,20,20" % (x - 10, z - 10)

    t.spawn(THEFT_BUILDING_DEF, count=1, at="line")
    building_id = _first_id(
        t.bridge_call("jawa/list_things", defName=THEFT_BUILDING_DEF, rect=rect),
        THEFT_BUILDING_DEF)
    # `t._guard()` is False under the offline declaration-probe (no Session,
    # every verb a no-op returning None) -- these two setup checks must not
    # raise there, only on a real run, or `components_declared()` (the
    # lint/floor walk) breaks for every mod that verifies its own setup
    # this way. `t.expect_*` verbs get this for free via their own internal
    # `_guard()` check; a plain `raise` here needs it spelled out.
    if t._guard() and building_id is None:
        raise ExpectationFailed(
            "no %s found in the test area right after spawn_batch" % THEFT_BUILDING_DEF)

    # Give it a claim the acting colonist does NOT hold -- IsAuthorized
    # returns false only when the resolved claimant's Faction differs from
    # the actor's (PropertyEngine.IsAuthorized's Commons-same-faction
    # carve-out). Pirate always exists (FactionDef requiredCountAtGameStart=1).
    t.bridge_call("jawa/set_thing_props", thing=building_id, faction="Pirate")
    got_faction = _first_faction(
        t.bridge_call("jawa/list_things", defName=THEFT_BUILDING_DEF, rect=rect),
        THEFT_BUILDING_DEF)
    if t._guard() and got_faction != "Pirate":
        raise ExpectationFailed(
            "set_thing_props(faction=Pirate) did not take -- read back faction=%r"
            % got_faction)

    actor = t.spawn_pawn("Colonist", hostile=False, beyond=[(x, z)])

    with t.component("uninstall_fires_taking_event", toggle="theftHaulerEnabled"):
        t.bridge_call("jawa/ordered_job", pawnId=actor, jobDef="RM_TheftHaulUninstall",
                      targetAId=building_id)
        # Generous: uninstallWork (default 200) + FinishedRemoving's queued
        # haul job, whether or not a storage destination exists (see module
        # docstring item 3) -- either way the actor ends up co-located with
        # the resulting MinifiedThing once both jobs finish.
        t.wait_ticks(2400)
        t.expect_not_in_cell_of(actor, THEFT_BUILDING_DEF)
        t.expect_in_cell_of(actor, "MinifiedThing")
        t.screenshot()


@suite.chain("animal_theft_take")
def animal_theft_take(t):
    """Spawn a stealable item, a stationary colonist co-located with it (a
    sentinel proving where the item started), and a Muffalo past it; order
    the Muffalo to run `RM_AnimalSteal` directly via `jawa/ordered_job` --
    bypassing `JobGiver_RM_{Trained,Wild}Steal`'s own gates (RM_Steal
    trainable / WildTheftExtension) and `AnimalTheftUtility.FindStealTarget`'s
    mass/reach filtering entirely, same reasoning as the theft-hauler
    chain above. Proves `JobDriver_RM_AnimalSteal`'s three toils
    (goto -> take-and-fire-TakingEvent -> wander-and-drop) actually move
    the item off its start cell and land it wherever the Muffalo ends up --
    it does NOT prove the AI ever chooses to start this job on its own
    (that lives in the `ThinkTreeDefs_AnimalSteal.xml` `mtbHours` chance
    nodes, which are XML-only data with nothing to unit-test here) nor
    that the species/training gates correctly exclude an ungated animal.
    """
    t.clear_area(size=20)
    x, z = t.anchor
    rect = "%d,%d,16,16" % (x - 8, z - 8)

    item_cells = t.spawn(STEAL_ITEM_DEF, count=1, at="line")   # lands at anchor
    item_id = _first_id(
        t.bridge_call("jawa/list_things", defName=STEAL_ITEM_DEF, rect=rect),
        STEAL_ITEM_DEF)
    if t._guard() and item_id is None:   # see theft_hauler_uninstall's comment on this guard
        raise ExpectationFailed(
            "no %s found in the test area right after spawn_batch" % STEAL_ITEM_DEF)

    # Co-located with the item at spawn (spawn_pawn defaults to t.anchor
    # with no `beyond`) -- items don't block pawn movement, so this is a
    # legal placement, and it never moves: its cell is the item's ORIGIN,
    # checked again after the steal.
    sentinel = t.spawn_pawn("Colonist", hostile=False)
    thief = t.spawn_pawn(THIEF_KIND, hostile=False, beyond=item_cells)

    with t.component("take_and_relocate", toggle="animalTheftEnabled"):
        t.bridge_call("jawa/ordered_job", pawnId=thief, jobDef="RM_AnimalSteal",
                      targetAId=item_id)
        t.wait_ticks(900)
        t.expect_not_in_cell_of(sentinel, STEAL_ITEM_DEF)   # left its origin
        t.expect_in_cell_of(thief, STEAL_ITEM_DEF)          # dropped where the thief ended up
        t.screenshot()
