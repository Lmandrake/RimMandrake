# DROIDWORKS_PHASE0_XML_1 — the phase-0 Droidworks Defs

Filed by BENCH 2026-08-30, caused by `DROID_SYSTEM_BUILD_1`. Spec (ledger `file`
event): NeedDef `DW_Power`, HediffDef `DW_PoweredDown`, HediffDef `DW_IonOverload`
placeholder, RecipeDef `DW_RebootDroid`, skip research gating in v0 — all matching
the C# in `src/Jawa/Droidworks/Source/Droidworks/*.cs` exactly by defName/class.

## Done

- `src/Jawa/Droidworks/Defs/NeedDefs/NeedDefs_Droidworks.xml` — `DW_Power`,
  `needClass Droidworks.Need_Power`, `showOnNeedList true`, `major false`.
- `src/Jawa/Droidworks/Defs/HediffDefs/HediffDefs_Droidworks.xml` —
  `DW_PoweredDown` (`HediffWithComps`, one comp
  `Droidworks.HediffCompProperties_PoweredDown`, single stage `Consciousness
  setMax 0.10`, `everVisible true`, `isBad true`, `scenarioCanAdd false`) and
  `DW_IonOverload` (placeholder, mirrors `JawaIon_Stun`'s own "overloaded" stage
  shape read from `JawaIonWeapons/Defs/HediffDefs_JawaIonStun.xml` — not yet
  wired to any DamageWorker; that's `DROIDWORKS_ION_GUARD_1`'s job).
- `src/Jawa/Droidworks/Defs/RecipeDefs/RecipeDefs_Droidworks.xml` —
  `DW_RebootDroid`, `workerClass Droidworks.Recipe_RebootDroid`,
  `targetsBodyPart false`, no ingredients, `recipeUsers` left unset (no
  Droidworks race ThingDef exists yet — `DROIDWORKS_DEF_GENERATOR_1` hasn't run
  — so there is nothing real to name; the C#'s own `GetPartsToApplyOn` already
  gates correctly on `HasHediff(DW_PoweredDown)` regardless of race, so this is
  not a functional gap, just an unwired convenience later work should close by
  adding `<recipes><li>DW_RebootDroid</li></recipes>` to the generated defs).
- Research gating: skipped by omission, as asked — no `researchPrerequisite`
  anywhere in these three files.

## Judgment call, flagged for the owner

Spec asked for **"skill Crafting 4 or Medicine 4 (either-or)"**. Vanilla
`RecipeDef.skillRequirements` is an AND list — there is no XML-only way to
express OR without a custom `RecipeWorker`, which would be a design change
outside this item's stated scope (XML only). **v0 simplification: Crafting 4
alone** (the more droid-appropriate of the two). Revisit if the either-or is
load-bearing to the design.

## Validate

`validate_patch.py` over `src/Jawa/Droidworks/Defs` against the live def dump
(2026-08-29T20-07-29Z, 585 mods, 68,772 defNames) — **0 errors, 0 warnings**,
one informational note confirming `HediffCompProperties_PoweredDown`'s `Class`
attribute resolves to this mod's own (unrecognized-by-the-scan, correctly so)
assembly — checked by hand against the C# source: public class, matching
namespace. defName uniqueness confirmed by hand (4 defNames, 4 distinct).

## criteria

- [x] NeedDef `DW_Power` authored, matches C#.
- [x] HediffDef `DW_PoweredDown` authored, matches C# comp class and the
      spec's stage shape.
- [x] HediffDef `DW_IonOverload` placeholder authored.
- [x] RecipeDef `DW_RebootDroid` authored, matches C# worker class.
- [x] Research gating skipped (v0).
- [x] `validate_patch.py` clean.
- [x] defName uniqueness confirmed.

--- history ---
