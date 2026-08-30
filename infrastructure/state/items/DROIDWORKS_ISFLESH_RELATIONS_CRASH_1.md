## 🔴 Scope correction: this is NOT a Droidworks-only bug

Discovered while testing Droidworks, but it affects the **already-shipped**
droid roster too. Any `PawnKindDef` on a race whose `FleshTypeDef.isOrganic`
is `false` AND whose `intelligence` is `Humanlike` can crash pawn generation
— that's every OuterRim Droid Depot and Star Wars KotOR Droids race, all of
which run on `Asimov_Automaton`/`ABF_FleshType_Synstruct_Base`, both patched
to `isOrganic:false` by `Jawa_Doctrine/Patches/DroidsAreMachines.xml`
(2026-08-11). This is a live crash risk in the current campaign build, not
a Droidworks-in-development problem.

## Spec (the bug, precisely)
`Verse.PawnComponentsUtility.AddAndRemoveDynamicComponents` (decompiled 1.6
source, read via RimSage, not guessed):

```csharp
if (pawn.RaceProps.IsFlesh)
{
    if (pawn.relations == null)
        pawn.relations = new Pawn_RelationsTracker(pawn);
    ...
}
```

`RaceProperties.IsFlesh => FleshType.isOrganic`. Any race with
`isOrganic:false` never gets a `relations` tracker allocated — by vanilla
design, this is fine for true mechanoids because `ToolUser`/`Animal`
intelligence pawns skip full relation generation. But a **Humanlike**
non-organic race (exactly what both the existing droid packs and Droidworks
want, for the traits/backstory/social layer) still goes through
`PawnGenerator.GenerateTraits` → `GeneratePawnRelations`, which
unconditionally touches `pawn.relations` — NRE on the null tracker.

## Live confirmation (quicktest, 2026-08-30)
- `jawa/spawn_pawn {kindDef: DW_OuterRim_GNKDroid, faction: null}` (Droidworks,
  new `DW_FleshType_Droid`, `isOrganic:false`): failed 3-9 times out of 10
  across several batches whenever the resolved random faction carried a real
  ideoligion. `faction: PlayerColony` never failed.
- `jawa/spawn_pawn {kindDef: OuterRim_BattleDroid, faction: null}`
  (**already-shipped**, `Asimov_Automaton` fleshtype): **10/10 failed**,
  identical stack.
- Exact traces (`jawa/drain_log`): `System.NullReferenceException` inside
  `RimWorld.LovePartnerRelationUtility.HasAnyLovePartnerOfTheOppositeGender`
  (`pawn.relations.DirectRelations` on a null `relations`) and
  `AlienRace.HarmonyPatches.GenerationChanceGenderless`
  (`HarmonyPatches.cs:2720`), both reached from
  `Verse.PawnGenerator.TryGenerateNewPawnInternal` → `GenerateTraits` /
  `GeneratePawnRelations` — the CORE pawn-generation pipeline, used by every
  raid, wild encounter, and world-pawn spawn, not just this bridge tool.

## What was ruled out
- Droidworks' `xenotypeSet` addition: reverted (git-stash A/B), crash
  persisted unchanged. Not the cause.
- `hasGenders:false`: tried as a fix, made it WORSE (9/10 fail, routes into a
  *different* broken HAR code path, `GenerationChanceGenderless`, rather than
  fixing anything). Reverted.
- Random chance / bad luck: reproducible at ~50-100% depending on whether the
  resolved faction happens to carry an ideo; the existing `OuterRim_BattleDroid`
  reproduces it at 10/10 with zero code changes of any kind.

## Verify
1. A Harmony postfix on `PawnComponentsUtility.AddAndRemoveDynamicComponents`
   (or the narrower method that gates the `relations` allocation) that also
   allocates `pawn.relations` for any Humanlike-intelligence pawn regardless
   of `IsFlesh` — the safest fix: it doesn't touch vanilla behavior for true
   mechanoids (still `ToolUser`/non-Humanlike, still skips relation
   generation entirely) and doesn't require picking a design stance on
   "should droids have spouses" (a relations tracker existing doesn't mean
   the generator will populate it with anything — spouse/family chances can
   still be tuned to zero later as a separate, non-urgent decision).
2. Quicktest re-check: batch-spawn 10x `OuterRim_BattleDroid` AND
   `DW_OuterRim_GNKDroid` with `faction: null`, expect 10/10 success.
3. Once fixed, `<fleshType>DW_FleshType_Droid</fleshType>` can be wired back
   onto `DW_Race_Base` (currently held out, see that file's own comment) and
   redeployed/re-tested.

## criteria
- [ ] Root cause fix identified above, built, and quicktest-verified 10/10
      on both an existing pack race and a Droidworks race.
- [ ] `DW_FleshType_Droid` wired back onto `DW_Race_Base` afterward.
- [ ] Owner told this affects the LIVE shipped droid roster (a raid or wild
      encounter spawning an existing OuterRim/KotOR droid kind into a
      real-ideo faction can crash pawn generation right now) — flagged in
      this session's summary, not just filed silently.
