"""validation.py -- modcheck suite for RimMandrake: Sacred Marks
(mandrake.rm.sacredgraffiti).

Never deployed (deploy_custom_mods.py excludes `.py` wholesale). Run with:

    python.exe src/RimMandrake/Utils/modcheck/cli.py run SacredGraffiti

(environment: minimal + mandrake.rm.graffiti, per this mod's own hard
`<modDependencies>` -- `RM_SacredMark_Ishko`'s `ParentName="RM_BaseGraffiti"`
resolves from that mod alone, so it cannot load without it.)

Grounded in the mod's actual source, read whole before writing this:
`RM_SacredGraffitiMod.cs` for the TWO Mod Settings fields
(`sacredMarkEnabled`, `markCountMultiplier` -- both `public static`, same
house style as `GelatinousSlime`/`Greentide`); `SacredGraffiti.cs` for the
ONE runtime mechanism (`RitualOutcomeEffectWorker_PlaceSacredMark.
ApplyExtraOutcome`: returns early unless `sacredMarkEnabled` AND
`outcome.Positive`, then spawns `def.filthDefToSpawn` at the ritual's
target cell -- or a present participant's own position if the target
carried no cell -- via `FilthMaker.TryMakeFilth`, counted by
`filthCountToSpawn.RandomInRange * markCountMultiplier`); `SacredMarks.xml`
(`RM_SacredMark_Ishko`, `ParentName="RM_BaseGraffiti"`, `Beauty 6` --
positive, devotional, unlike `GraffitiMod`'s uniformly-ugly vandal filth);
`RitualOutcomeEffects.xml` (`RM_Ishko_RitualOutcome_PlaceSacredMark`,
`workerClass` pointed at the C# above, `filthDefToSpawn=RM_SacredMark_
Ishko`); and `About.xml`, whose own description says outright: "nothing yet
spawns them automatically outside a ritual outcome" and names the mechanism
"ready ... the moment a real Matrix ritual exists to reference it" -- none
does yet.

CONFIRMED (not inherited from the walk doc unchecked): this mod's ONE
outcome-effect def is genuinely UNREACHABLE from anything this suite can
drive. Read `JawaBenchEventTools.cs`'s `jawa/ritual_start` -- the only
bridge tool that fires a real ritual -- and its own mechanism is "start an
existing ideo PRECEPT by defName" (`Precept_Ritual`, via
`RitualBehaviorWorker.TryExecuteOn`); the fired ritual's outcome effect is
whatever THAT precept's own `RitualBehaviorDef` already carries, never an
arbitrary `RitualOutcomeEffectDef` picked by name. Since
`RM_Ishko_RitualOutcome_PlaceSacredMark` is referenced by no `RitualDef`/
`PreceptDef` at all (per this mod's own About.xml and both Defs files'
header comments -- the Salvation Matrix is design prose only), there is no
sequence of bridge calls that reaches `ApplyExtraOutcome` end-to-end. This
matches the walk doc's own step 4 framing exactly (a def-sanity spawn check,
"not an end-to-end ritual test") -- confirmed independently here rather than
taken on faith.

WHAT THIS SUITE CANNOT PROVE, and why:
  - `ApplyExtraOutcome` itself (the positive-outcome gate, the fallback-to-
    participant-position branch, the `markCountMultiplier` arithmetic) has
    NO live path to exercise per the paragraph above. Both settings below
    get write + independent read-back only (`t.set_setting`, static fields
    via `jawa/mod_settings_field` -- `BRIDGE_STATIC_SETTINGS_FIELDS_1`), no
    behavioral proof.
  - `[D]` def read-back items (walk steps 2-3: exact `Beauty`/`Cleanliness`/
    `godSatiationHook`/`workerClass`/`filthDefToSpawn` values) are covered
    by the offline def dump / RimSage, not this bridge-driven runtime suite
    -- matching every other suite in this family.
  - Walk step X (human pass: does the "pair of glowing orange eyes" art
    actually render, positive Beauty in the inspect pane, rather than a
    placeholder/magenta texture) is explicitly deferred to
    `MOD_HUMAN_EXPLORATION_PASS_1` in the walk doc itself -- no component
    below screenshots for content-correctness beyond confirming the spawn
    succeeded; one screenshot is taken so a human reviewing the run's sheet
    can eyeball the art anyway.
"""
from modcheck import Suite, ExpectationFailed

suite = Suite("SacredGraffiti")
suite.toggles = ["sacredMarkEnabled", "markCountMultiplier"]

SETTINGS_TYPE = "RimMandrake.SacredGraffiti.RM_SacredGraffitiSettings"
MARK_DEF = "RM_SacredMark_Ishko"


@suite.chain("sacred_mark_ishko_is_game_ready")
def sacred_mark_ishko_is_game_ready(t):
    """Walk step 4: spawn the filth def directly -- bypassing the (currently
    unreachable, see module docstring) ritual-outcome worker entirely. This
    proves the def itself resolves and places cleanly, which is the only
    thing about this mark this suite can independently prove offline."""
    t.clear_area(size=20)
    x, z = t.anchor
    with t.component("ishko_mark_spawns", beyond_toggle=True):
        t.spawn(MARK_DEF, count=1, at="line")
        r = t.bridge_call("jawa/list_things", defName=MARK_DEF,
                          rect="%d,%d,5,5" % (x - 2, z - 2))
        if t._guard():
            rows = (r or {}).get("things") or []
            if not any(row.get("def") == MARK_DEF for row in rows):
                raise ExpectationFailed(
                    "no %s found near the anchor after spawning it: %r" % (MARK_DEF, rows))
        t.screenshot()


@suite.chain("settings_are_live_flippable")
def settings_are_live_flippable(t):
    """No behavioral proof beyond write + independent read-back -- see
    module docstring: `ApplyExtraOutcome` has no bridge path to reach it at
    all, since no real RitualDef/PreceptDef references this mod's
    outcome-effect def yet."""

    with t.component("sacred_mark_enabled_flips", toggle="sacredMarkEnabled"):
        t.set_setting(SETTINGS_TYPE, {"sacredMarkEnabled": False})
        t.set_setting(SETTINGS_TYPE, {"sacredMarkEnabled": True})

    with t.component("mark_count_multiplier_flips", toggle="markCountMultiplier"):
        t.set_setting(SETTINGS_TYPE, {"markCountMultiplier": 2.0})
        t.set_setting(SETTINGS_TYPE, {"markCountMultiplier": 1.0})
