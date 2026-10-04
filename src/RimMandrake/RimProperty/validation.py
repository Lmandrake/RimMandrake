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
(FactionDef -- see "Still not proven" item 1 below: `requiredCountAtGameStart
=1` does NOT guarantee a live instance the way this paragraph originally
claimed).

Still not proven / likely first-live-run corrections (per this suite's
own register, same practice as Pits):
  1. MODCHECK_SUITE_CORRECTIONS_1 (2026-09-13): the first live wave DID
     abort here, exactly the risk this item flagged -- `set_thing_props`
     itself was never checked for its own `success`, only the independent
     `list_things` read-back. FIXED 2026-09-26: the abort's real cause is
     now KNOWN, not merely distinguished. `jawa/faction_create`'s own C#
     docstring names it -- Biotech's `PirateWaster` declares
     `replacesFaction` at vanilla `Pirate` with `requiredCountAtGameStart`
     above zero, so `FactionGenerator.InitializeFactions` skips generating
     `Pirate` outright on any world generated with Biotech active, and
     CLAUDE.md's own standing rule mandates all five expansions (Biotech
     included) on every test list, no ablation. So `requiredCountAtGameStart
     =1` never actually guarantees a live instance HERE -- it fails
     identically every run, not intermittently. `t.ensure_faction("Pirate")`
     (modcheck.suite, shared with Aftermath's identical fix) now creates it
     via `jawa/faction_create` before the claim is set, so the two
     `set_thing_props`/read-back checks below are exercised for real
     instead of aborting on missing setup.
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
    "pickpocketEnabled", "hirePlacelessEnabled", "bribeEnabled",
    "claimLifetimeMultiplier",
]

SETTINGS_TYPE = "RimMandrake.Property.PropertySettings"
TICKS_PER_DAY = 60000.0
# PropertyTuning.cs consts, read from the C# (Min/MaxClaimLifetimeDays).
MIN_LIFETIME_DAYS = 3.0
MAX_LIFETIME_DAYS = 3650.0


def _py_lifetime_ticks(recog, mult=1.0):
    """Pure-python copy of ClaimDecay.LifetimeTicks (ClaimDecay.cs, read whole):
    Lerp(Min, Max, Clamp01(recog)) days * claimLifetimeMultiplier * TicksPerDay."""
    r = min(1.0, max(0.0, recog))
    return (MIN_LIFETIME_DAYS + (MAX_LIFETIME_DAYS - MIN_LIFETIME_DAYS) * r) * mult * TICKS_PER_DAY


def _py_effective_strength(initial, age, recog, mult=1.0):
    """Pure-python copy of ClaimDecay.EffectiveStrength: linear to zero."""
    if age <= 0:
        return initial
    life = _py_lifetime_ticks(recog, mult)
    if age >= life:
        return 0.0
    return initial * (1.0 - age / life)


def _static_float(t, method, args):
    """jawa/static_call on a public static ClaimDecay/Utility method; reads the tool's own
    `success`, never a payload substring. None under the offline declaration probe."""
    if not t._guard():
        return None
    r = t.bridge_call("jawa/static_call", type=method[0], method=method[1], args=args)
    if not (r or {}).get("success", True) or (r or {}).get("result") in (None, ""):
        raise ExpectationFailed("static_call %s.%s(%s) failed: %r" % (method[0], method[1], args, r))
    try:
        return float(str((r or {}).get("result")).strip())
    except ValueError:
        raise ExpectationFailed("static_call %s.%s(%s) returned non-numeric %r" % (method[0], method[1], args, r))


def _close(a, b, rel=1e-3):
    return abs(a - b) <= rel * max(1.0, abs(a), abs(b))


def _set_field(t, field, value):
    r = t.bridge_call("jawa/mod_settings_field", typeName=SETTINGS_TYPE, action="set",
                      field=field, value=str(value))
    if t._guard() and not (r or {}).get("success"):
        raise ExpectationFailed("mod_settings_field(set %s=%s) failed: %r" % (field, value, r))


def _unmeasured(t, what):
    """Honest floor-gap component body: raised only on a real run so the offline
    declaration probe still enumerates the component's toggle tag."""
    if t._guard():
        raise ExpectationFailed("UNMEASURED: " + what)

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
    # carve-out). "Pirate" is a real vanilla FactionDef (confirmed:
    # Data/Core/Defs/FactionDefs/Factions_Misc.xml), but MODCHECK_SUITE_
    # CORRECTIONS_1's first live run aborted here with read-back
    # faction=None and no further detail -- `set_thing_props`'s own
    # response (`success`, or its Fail message) was never inspected, only
    # the independent `list_things` read-back, so the first run couldn't
    # tell "the SET call itself failed" (JawaBenchStorytellerTools2.cs's
    # `SetThingProps` returns `success: false` with a specific message if
    # `Find.FactionManager.FirstFactionOfDef` finds no Pirate FACTION
    # INSTANCE in this particular world -- GUARANTEED absent here, see
    # module docstring item 1: Biotech's PirateWaster always pre-empts it)
    # apart from "SET succeeded but the read-back disagrees". `t.ensure_
    # faction` closes the real gap; both remaining checks are now surfaced
    # explicitly so a genuine read-back desync is still self-diagnosing.
    t.ensure_faction("Pirate")
    set_result = t.bridge_call("jawa/set_thing_props", thing=building_id, faction="Pirate")
    if t._guard() and not (set_result or {}).get("success"):
        raise ExpectationFailed(
            "set_thing_props(faction=Pirate) itself failed: %r" % set_result)
    got_faction = _first_faction(
        t.bridge_call("jawa/list_things", defName=THEFT_BUILDING_DEF, rect=rect),
        THEFT_BUILDING_DEF)
    if t._guard() and got_faction != "Pirate":
        raise ExpectationFailed(
            "set_thing_props(faction=Pirate) reported success and "
            "changed=['faction'] (factionAfter=%r) but the independent "
            "jawa/list_things read-back still shows faction=%r -- a real "
            "read-back mismatch, not a setter failure"
            % ((set_result or {}).get("factionAfter"), got_faction))

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


@suite.chain("claim_erase_api")
def claim_erase_api(t):
    """PROPERTY_CLAIM_ERASE_API_1. No site needed: the proof builds its own unspawned items.

    `RM_ClaimEraseProof.Run` records Stolen(X) + BattleLootOrigin(Y) + Purchased(colony) on one item, calls
    ClearForeignClaims (must return 2 and leave exactly the colony's record), then runs ClearForeignClaimsWhere over a
    mixed pair (must wipe 2, keep the colony's Inherited) and checks a FactionRecord suspicion entry reads unchanged.
    Needs the GM-gated `jawa/static_call` tool (JawaBench companion built 52c7de5ba; deploys at the next game DOWN).
    NOT proven here: save then reload keeping the wipe (UNMEASURED, needs a save round trip).
    """
    with t.component("erase_foreign_claims", beyond_toggle=True):
        r = t.bridge_call("jawa/static_call", type="RimMandrake.Property.RM_ClaimEraseProof", method="Run", args="")
        text = str((r or {}).get("result", ""))
        if not text.startswith("PASS"):
            raise ExpectationFailed("claim erase proof: %s (raw: %s)" % (text or "no result", r))

@suite.chain("claim_decay_curve")
def claim_decay_curve(t):
    """Lazy claim decay (ClaimDecay.cs: pure functions of strength/age/recognizability, no tick).
    The live C# is asked via jawa/static_call and compared with a pure-python copy of the formula
    read from ClaimDecay.cs; then claimLifetimeMultiplier is doubled and the lifetime must double."""
    CD = "RimMandrake.Property.ClaimDecay"
    with t.component("decay_curve_matches_formula", beyond_toggle=True):
        for recog in (0.0, 0.5, 1.0):
            got = _static_float(t, (CD, "LifetimeTicks"), "%s" % recog)
            want = _py_lifetime_ticks(recog)
            if got is not None and not _close(got, want):
                raise ExpectationFailed("LifetimeTicks(%s)=%s, formula says %s" % (recog, got, want))
        life0 = _py_lifetime_ticks(0.0)
        for age, recog in ((life0 / 2, 0.0), (life0, 0.0), (life0 * 2, 0.0), (0, 0.0), (1000000, 0.5)):
            got = _static_float(t, (CD, "EffectiveStrength"), "0.9|%d|%s" % (age, recog))
            want = _py_effective_strength(0.9, int(age), recog)
            if got is not None and not _close(got, want):
                raise ExpectationFailed("EffectiveStrength(0.9,%d,%s)=%s, formula says %s" % (age, recog, got, want))

    with t.component("claim_lifetime_multiplier_scales", toggle="claimLifetimeMultiplier"):
        base = _static_float(t, (CD, "LifetimeTicks"), "0.5")
        try:
            _set_field(t, "claimLifetimeMultiplier", 2.0)
            doubled = _static_float(t, (CD, "LifetimeTicks"), "0.5")
            half_age = _static_float(t, (CD, "EffectiveStrength"), "1.0|%d|0.0" % int(_py_lifetime_ticks(0.0)))
        finally:
            _set_field(t, "claimLifetimeMultiplier", 1.0)
        if base is not None and not _close(doubled, 2.0 * base):
            raise ExpectationFailed("multiplier 2 gave lifetime %s, expected 2 x %s" % (doubled, base))
        # at x2 a recog-0 claim of age == old lifetime is exactly half strength, not expired
        if half_age is not None and not _close(half_age, 0.5):
            raise ExpectationFailed("at multiplier 2, age==1x lifetime gave strength %s, expected 0.5" % half_age)


@suite.chain("settlement_fee_tuning")
def settlement_fee_tuning(t):
    """Hire/bribe advance prices follow their Mod Settings fields (HirePlacelessUtility.
    ComputeHireFeeSilver / BribeUtility.ComputeBribeFeeSilver: Max(1, Round(field))). This is the
    PRICE only -- the enabled toggles gate the float menu, see the *_unmeasured chains."""
    HU = "RimMandrake.Property.HirePlacelessUtility"
    BU = "RimMandrake.Property.BribeUtility"
    with t.component("hire_and_bribe_fee_follow_settings", beyond_toggle=True):
        try:
            _set_field(t, "hirePlacelessFeeSilver", 37)
            _set_field(t, "bribeFeeSilver", 41)
            hire = _static_float(t, (HU, "ComputeHireFeeSilver"), "")
            bribe = _static_float(t, (BU, "ComputeBribeFeeSilver"), "")
        finally:
            _set_field(t, "hirePlacelessFeeSilver", 20)
            _set_field(t, "bribeFeeSilver", 15)
        if hire is not None and hire != 37:
            raise ExpectationFailed("ComputeHireFeeSilver with field=37 returned %s" % hire)
        if bribe is not None and bribe != 41:
            raise ExpectationFailed("ComputeBribeFeeSilver with field=41 returned %s" % bribe)


# Each UNMEASURED component sits alone in its chain: a raised component marks every later one in
# the same chain UNMEASURED too (upstream_failed), which would smear one gap across unrelated ones.
@suite.chain("perception_unmeasured")
def perception_unmeasured(t):
    with t.component("witness_roll_and_faction_record_propagation", toggle="perceptionEnabled"):
        _unmeasured(t, "no bridge tool reads GameComponent_PropertyLedger's private factionRecords or "
                       "PerceptionUtility.RollWitnesses; needs a static RM_ proof (like RM_ClaimEraseProof) "
                       "that fires a TakingEvent with perceptionEnabled on/off and reports witnesses/suspicion")


@suite.chain("salvage_fee_unmeasured")
def salvage_fee_unmeasured(t):
    with t.component("salvage_claim_fee_float_menu", toggle="salvageClaimFeeEnabled"):
        _unmeasured(t, "FloatMenuOptionProvider_PaySalvageClaim runs inside the float-menu delegate (no JobDef); "
                       "no bridge tool lists or clicks float-menu options")


@suite.chain("walkable_commerce_unmeasured")
def walkable_commerce_unmeasured(t):
    with t.component("walkable_commerce_float_menu", toggle="walkableCommerceEnabled"):
        _unmeasured(t, "FloatMenuOptionProvider_BuyMerchandise runs inside the float-menu delegate (no JobDef); "
                       "no bridge tool lists or clicks float-menu options")


@suite.chain("pickpocket_unmeasured")
def pickpocket_unmeasured(t):
    with t.component("pickpocket_float_menu", toggle="pickpocketEnabled"):
        _unmeasured(t, "FloatMenuOptionProvider_Pickpocket is float-menu only; no tool lists/clicks float-menu options "
                       "(PickpocketUtility.TransferToActor takes Thing/Pawn objects static_call cannot pass)")


@suite.chain("hire_placeless_unmeasured")
def hire_placeless_unmeasured(t):
    with t.component("hire_placeless_float_menu", toggle="hirePlacelessEnabled"):
        _unmeasured(t, "FloatMenuOptionProvider_HirePlaceless is float-menu only; no tool lists/clicks float-menu options")


@suite.chain("bribe_unmeasured")
def bribe_unmeasured(t):
    with t.component("bribe_float_menu_and_dampen", toggle="bribeEnabled"):
        _unmeasured(t, "FloatMenuOptionProvider_Bribe is float-menu only and FactionRecord suspicion has no getter; "
                       "no tool lists/clicks float-menu options or reads FactionRecord")


@suite.chain("claim_recording_unmeasured")
def claim_recording_unmeasured(t):
    with t.component("stolen_purchased_gifted_inherited_basis_recorded", beyond_toggle=True):
        _unmeasured(t, "PropertyEngine.RecordTransfer/RecordGift/RecordInheritance take Thing/ClaimantRef objects "
                       "(jawa/static_call passes only primitives/IntVec3/Map) and the ledger has no read tool; "
                       "needs an RM_ proof static returning the recorded ClaimBasis per exception")


# Every def this mod ships is loaded and its label is what its XML says (NORTHSTAR_PARTIAL_GAPS_FILL_1;
# theft jobs, think trees, trainable). The Defs/ parse is the list, so a def added later is covered with no edit here.
from modcheck import shipped_defs  # noqa: E402
shipped_defs.add_chain(suite, __file__, sanity=('RM_AnimalSteal',), min_count=5)
