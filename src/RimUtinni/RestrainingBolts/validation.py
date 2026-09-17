"""validation.py -- modcheck suite for RimUtinni: Jawa Restraining Bolts
(mandrake.rut.restrainingbolts).

Never deployed (deploy_custom_mods.py excludes `.py` wholesale). Run with:

    python.exe src/RimMandrake/Utils/modcheck/cli.py run RestrainingBolts

Grounded in the mod's actual source, read whole before writing this:
`RestrainingBoltsMod.cs` for the THREE Mod Settings fields (`enabled`,
`penaltyPerBoltedDroid`, `goodwillFloor` -- all `public static`, per its own
comment citing `GelatinousSlime/Source/SlimeMod.cs`'s house style);
`GoodwillSituationWorker_RestrainingBolts.cs` for the mechanism itself
(`GetMaxGoodwill`: early-out to 100 for any faction whose `.def` is not
`RUT_Jawa_FreeDroidEnclaves`, early-out to 100 if `enabled` is false, early-out
to 100 if Droid Depot's `OuterRim_RestraintBolt` HediffDef cannot be resolved,
otherwise `max(goodwillFloor, 100 - penaltyPerBoltedDroid * N)` where N is a
LIVE count of owned pawns carrying that hediff -- "no stored state ... read
live off currently-owned pawns each recache", per its own doc comment);
`DefOfs.cs` for the plain (non-silent-fail) `[DefOf]` field
`FactionDefOf_RestrainingBolts.RUT_Jawa_FreeDroidEnclaves`; and
`Defs/GoodwillSituationDefs/Jawa_RestrainingBolts.xml` (one def, no
`baseMaxGoodwill` -- the XML's own comment: that field "is read by NOTHING",
omitted on purpose).

A REAL, MOD-SPECIFIC FLOOR GAP, confirmed by reading rather than assumed --
this mod's ENTIRE reason for existing (the N-dependent goodwill cap, walk
steps 4-5) is structurally UNREACHABLE on the runner's own "minimal mechanism
list + the mod under test" environment (mod_validation_runner_spec.md
"Environment"), not merely untested:

  - `RUT_Jawa_FreeDroidEnclaves` is a FactionDef shipped by
    `RimUtinni/UtinniPatches` (confirmed: `grep -rl RUT_Jawa_FreeDroidEnclaves`
    across the repo finds it only in `UtinniPatches/Defs/FactionDefs/
    JawaFreeDroidEnclaves.xml`, `PawnFlavor`, and other RimUtinni-tier mods --
    never in this mod's own `Defs/`), and this mod's own About.xml lists
    UtinniPatches only as a soft dependency (lazy `GetNamedSilentFail`
    resolution paths elsewhere in the doc set), not a hard one. On a minimal
    run with ONLY RestrainingBolts loaded, that FactionDef does not exist at
    all -- so this mod's plain `[DefOf]` field
    (`FactionDefOf_RestrainingBolts.RUT_Jawa_FreeDroidEnclaves`, no
    `[MayRequire]`, no silent-fail resolution) never binds to anything, and
    `GetMaxGoodwill`'s very first line (`other?.def !=
    FactionDefOf_RestrainingBolts.RUT_Jawa_FreeDroidEnclaves`) is comparing
    against `null` for EVERY faction that does exist -- which is trivially
    true for all of them, so the worker returns 100 unconditionally on this
    environment, never mind whether Droid Depot or any bolted pawn exists.
  - Droid Depot (`neronix17.outerrim.droiddepot`, owner of the
    `OuterRim_RestraintBolt` HediffDef) is likewise not part of the minimal
    list, so even if the FactionDef existed, `BoltHediff` would resolve to
    null and hit its own separate early-out.
  - Net effect: walk steps 4 and 5 (the N-dependent formula, and
    `CanChangeGoodwillFor` reflecting a lowered ceiling) need a LIVE run with
    UtinniPatches + Droid Depot both active -- genuinely a playtest-scope
    check per the runner spec ("cross-mod conflicts are playtest's
    problem"), not something this offline-authored suite can fake into a
    real pass. Recorded here rather than invented.

WHAT THIS SUITE CAN HONESTLY PROVE INSTEAD, on the minimal environment:
  - The worker is inert and does not error for a faction it was never meant
    to touch -- proven dynamically (via `jawa/list_factions`'s own hidden/
    permanentEnemy flags, not a guessed defName) rather than assuming any one
    vanilla FactionDef's goodwill-tracking shape.
  - The FDE FactionDef's absence on this environment is asserted EXPLICITLY
    (`jawa/faction_goodwill_situations` on `RUT_Jawa_FreeDroidEnclaves` is
    expected to FAIL with "No FactionDef") rather than silently skipped --
    turning the floor gap above into a checked, self-documenting assertion:
    if UtinniPatches is ever folded into the minimal list, this call starts
    succeeding and this suite will need rewriting to actually exercise N>0,
    which is the correct trigger to notice that.
  - All three Mod Settings fields are live, flippable, static fields
    (`jawa/mod_settings_field`, BRIDGE_STATIC_SETTINGS_FIELDS_1) -- write +
    independent read-back, no behavioral proof beyond that per the floor gap
    above.

Still not proven / likely first-live-run corrections:
  1. Whether `jawa/list_factions` on this minimal environment's generated
     world actually contains a non-hidden, non-permanentEnemy faction other
     than the player -- if the world generates with none, `goodwill_worker_
     inert_for_unrelated_faction` below raises explicitly rather than
     silently reporting nothing, but which factions a minimal-list world
     generates was not measured live before writing this.
  2. The `[DefOf]` resolution failure for `RUT_Jawa_FreeDroidEnclaves` itself
     (distinct from the bridge tool's own "No FactionDef" message) may log
     its own Player.log error at load -- RimWorld's `DefOfHelper` error text
     for a missing `[DefOf]` field was not measured live and is NOT the
     literal "Config error in mandrake.rut.restrainingbolts" string the
     walk's step 1 names, so this suite does not assert on it either way.
"""
from modcheck import Suite, ExpectationFailed

suite = Suite("RestrainingBolts")
suite.toggles = ["enabled", "penaltyPerBoltedDroid", "goodwillFloor"]

FDE_FACTION_DEF = "RUT_Jawa_FreeDroidEnclaves"
SETTINGS_TYPE = "RimMandrake.Utinni.RestrainingBolts.RestrainingBoltsSettings"


@suite.chain("goodwill_worker_on_minimal_environment")
def goodwill_worker_on_minimal_environment(t):
    """No test area needed -- this chain is entirely world/faction state, no
    map things. Two components: prove the FDE faction genuinely does not
    exist here (the documented floor gap, checked rather than assumed), and
    prove the worker is inert for whatever faction actually IS present."""

    with t.component("fde_faction_absent_on_minimal_list", beyond_toggle=True):
        r = t.bridge_call("jawa/faction_goodwill_situations", faction=FDE_FACTION_DEF)
        if t._guard():
            if (r or {}).get("success"):
                raise ExpectationFailed(
                    "jawa/faction_goodwill_situations(%s) SUCCEEDED on the minimal "
                    "environment -- the module docstring's floor gap assumed "
                    "UtinniPatches is NOT loaded here; if it now is, this suite "
                    "needs rewriting to actually exercise the N-dependent cap "
                    "(walk steps 4-5), not just this absence check. Result: %r"
                    % (FDE_FACTION_DEF, r))
            err = (r or {}).get("error") or ""
            if "No FactionDef" not in err:
                raise ExpectationFailed(
                    "jawa/faction_goodwill_situations(%s) failed for a reason "
                    "other than the expected missing FactionDef: %r"
                    % (FDE_FACTION_DEF, r))

    with t.component("goodwill_worker_inert_for_unrelated_faction", beyond_toggle=True):
        factions = t.bridge_call("jawa/list_factions")
        rows = (factions or {}).get("factions") or []
        other = None
        for row in rows:
            if (not row.get("isPlayer") and not row.get("hidden")
                    and not row.get("permanentEnemy")):
                other = row.get("defName")
                break
        if t._guard() and other is None:
            raise ExpectationFailed(
                "jawa/list_factions returned no non-player, non-hidden, "
                "non-permanentEnemy faction to test the worker's early-out "
                "against on this world: %r" % rows)
        r = t.bridge_call("jawa/faction_goodwill_situations", faction=other)
        if t._guard():
            if not (r or {}).get("success"):
                raise ExpectationFailed(
                    "jawa/faction_goodwill_situations(%s) failed: %r" % (other, r))
            situations = r.get("situations") or []
            mine = next((s for s in situations if s.get("defName") == "Jawa_RestrainingBolts"), None)
            # GetMaxGoodwill's very first check is `other.def != FDE`, true for
            # every faction here -- either the situation never enters the list
            # at all, or it enters reporting the vanilla 100 ceiling. Both are
            # "inert"; only a LOWERED ceiling here would be the bug.
            if mine is not None and mine.get("maxGoodwill") != 100:
                raise ExpectationFailed(
                    "Jawa_RestrainingBolts situation capped %s's goodwill to "
                    "%r -- the worker should be a no-op for any faction other "
                    "than %s" % (other, mine.get("maxGoodwill"), FDE_FACTION_DEF))
            t.screenshot()


@suite.chain("settings_are_live_flippable")
def settings_are_live_flippable(t):
    """All three fields are `public static` on `RestrainingBoltsSettings` --
    `jawa/mod_settings_field` resolves static fields directly
    (BRIDGE_STATIC_SETTINGS_FIELDS_1), so each gets a real write + independent
    read-back component. No behavioral proof beyond that: per the module
    docstring, the mechanism these gate is unreachable on this environment
    regardless of their value."""

    with t.component("enabled_flips", toggle="enabled"):
        t.set_setting(SETTINGS_TYPE, {"enabled": False})
        t.set_setting(SETTINGS_TYPE, {"enabled": True})

    with t.component("penalty_per_bolted_droid_flips", toggle="penaltyPerBoltedDroid"):
        t.set_setting(SETTINGS_TYPE, {"penaltyPerBoltedDroid": 5.0})
        t.set_setting(SETTINGS_TYPE, {"penaltyPerBoltedDroid": 2.5})

    with t.component("goodwill_floor_flips", toggle="goodwillFloor"):
        t.set_setting(SETTINGS_TYPE, {"goodwillFloor": -50.0})
        t.set_setting(SETTINGS_TYPE, {"goodwillFloor": -70.0})
