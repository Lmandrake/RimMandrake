# DROID_SIBLING_RELATION_GEN_CRASH_1 — droid pawn generation crashes intermittently

## What was observed (live, quicktest, minimal 25-mod list, 2026-09-10)

While spawning 3 pawns each of 8 Droidworks families for
`DROIDWORKS_PERSONALITY_VERIFY_1`, 2 of 24 spawn attempts (one
`RSW_DW_OuterRim_ProtocolDroid`, one `RSW_DW_KotORDroidColonist_KX12UPD`)
failed with `success: false` and this log:

```
Error while generating pawn. Rethrowing. Exception: System.NullReferenceException:
Object reference not set to an instance of an object
  at RimWorld.PawnRelationWorker_Sibling.CreateRelation (...)
  at Verse.PawnGenerator.GeneratePawnRelations (...)
    - PREFIX OskarPotocki.VEF: ...DisableRelations(Pawn pawn)
    - PREFIX rimworld.erdelf.alien_race.main: ...GeneratePawnRelationsPrefix(...)
  at Verse.PawnGenerator.TryGenerateNewPawnInternal (...)
    - TRANSPILER/PREFIX rimworld.erdelf.alien_race.main: ...
  at Verse.PawnGenerator.GenerateNewPawnInternal (...)
    - POSTFIX OskarPotocki.VEF: ...
  at Verse.PawnGenerator.GenerateOrRedressPawnInternal (...)
  at Verse.PawnGenerator.GeneratePawn (...)
    - PREFIX/POSTFIX rimworld.erdelf.alien_race.main + Neronix17.TabulaRasa: ...
```

Both other spawns of the SAME kindDef in the same batch succeeded — this is
intermittent, not a hard failure on those kinds (consistent with sibling
relation generation only sometimes finding/attempting to create a candidate
sibling). Not a "spawn tool substitutes kinds silently" case: `jawa/list_pawns`
confirmed the kindDef counts matched exactly what spawned (2/3 and 2/3, not
3/3-with-a-swap).

## Not yet determined

- Whether this reproduces without HumanoidAlienRaces/VanillaExpandedFramework
  in the mix (both patch into this exact call stack) — i.e. whether the bug
  is in Droidworks' own race setup (something `PawnRelationWorker_Sibling`
  needs that a droid `RaceProperties`/lifeStage lacks) or a framework
  interaction independent of Droidworks.
- Whether it reproduces on the full 581-mod campaign list, or only surfaces
  under this specific minimal 25-mod combination.
- Whether it happens on OTHER Droidworks families too (only 24 spawns
  sampled, 3 per family — a bigger batch would tell whether this is
  Protocol/Probe-specific or can hit any family).

## spec

1. Reproduce on a clean quicktest: spawn ~10 of `RSW_DW_OuterRim_ProtocolDroid`
   and ~10 of `RSW_DW_KotORDroidColonist_KX12UPD` alone (isolate from the
   other 6 families) to get a real failure rate per kind.
2. Read `PawnRelationWorker_Sibling.CreateRelation` (rimsage
   `read_csharp_symbol`) to see what it dereferences, and check whether
   Droidworks' race defs set whatever that field needs (likely something in
   `childRelationChance`/`generation`-adjacent race config, or an assumption
   about `Pawn.gender`/`ageTracker` that a droid's `RaceProperties` doesn't
   satisfy the same way a human's does).
3. If it is a Droidworks-side gap: fix it there (e.g. `<generateAsPackAnimal>`-
   style suppression, or a childRelationChance override to skip sibling
   generation for constructs entirely — the item file for
   `DROIDWORKS_CHASSIS_PERSONALITY_1` already treats a construct as not
   needing biological-relation trappings).

## verify

The 20-ish-spawn reproduction from step 1: zero NREs on either kind =
closed. Record the actual failure rate observed, not just "fixed" or "not
fixed".

## Fix implemented (not yet live-tested), 2026-09-10

Root cause confirmed by two research passes (see prompt/commit history):
vanilla `PawnRelationWorker_Sibling.CreateRelation` never null-checks what
its `GenerateParent` helper returns; `GeneratePawnRelations`
(`Verse/PawnGenerator.cs:2049`) gates the whole relations pass on
`RaceProps.Humanlike` alone; every Droidworks race is `Humanlike=true` but
restricts `<bodyTypes Inherit="False">`/`<headTypes Inherit="False">` to a
single gender, so `GenerateParent`'s nested opposite-gender pawn generation
fails and returns null, which `CreateRelation` then dereferences.
`hasGenders=false` was tried as a fix candidate first and PROVEN NOT to
help: `GenerateParent` always sets `FixedGender` explicitly on its nested
`PawnGenerationRequest`, so `hasGenders` is never consulted on this path.

Implemented instead: a Harmony prefix on `PawnGenerator.GeneratePawnRelations`
(private, static) that returns `false` (skips the whole relations pass, no
NRE possible) for any pawn whose `RaceProps.FleshType ==
DroidworksDefOf.RSW_DW_FleshType_Droid`. This suppresses the root cause
once for every `PawnRelationWorker_*` subtype reachable from that method,
rather than patching `PawnRelationWorker_Sibling` alone and leaving the same
null-deref shape open in parent/child, spouse, etc.

- New class `Patch_SkipRelationGenerationForDroids` in
  `src/RimStarWars/Droidworks/Source/Droidworks/Patch_ShouldHaveNeed_Power.cs`
  (appended to the existing `DroidworksNeedGateMod` bootstrap alongside the
  need-gate, non-flesh-relations, and apparel patches - same house style:
  `AccessTools.Method` lookup with a null-check `Log.Error`, applied inside
  its own try/catch in the static constructor).
- Built clean against `Droidworks.csproj` (Release): 0 warnings, 0 errors.
- **Not yet live-tested.** A live retest should rerun the spec's ~20-spawn
  reproduction (10x `RSW_DW_OuterRim_ProtocolDroid`, 10x
  `RSW_DW_KotORDroidColonist_KX12UPD`) and confirm zero NREs, per the
  `## verify` section above. This item stays open until that retest runs.
