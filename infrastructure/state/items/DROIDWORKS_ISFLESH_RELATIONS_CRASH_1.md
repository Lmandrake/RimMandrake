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

---

## 2026-08-30 (FOUNDRY) — fix verified as far as SOURCE can take it; the live 10/10 is still owed

### Droidworks is NOT in this mod list — the shipped case is the whole case
Read from the live `ModsConfig.xml` (590 entries), not from a doc: there is no Droidworks
packageId in it. `DW_OuterRim_GNKDroid` cannot be spawned in this game at all, so the
verify step reduces to `OuterRim_BattleDroid` — which is the **already-shipped, already-
crashing** case and the only one that matters for the campaign. `neronix17.outerrim.core`,
`neronix17.outerrim.droiddepot`, `guy762.kotordroids` and `guy762.mm.kotorcore` are all
active, so the affected roster is live. ⇒ `DROIDWORKS_POWEREDDOWN_NOT_WIRED_1` left
untouched, as that item's own Status note predicted.

### The fix is loaded in the running game
`mandrake.jawa.doctrine` is active in `ModsConfig.xml`;
`…/RimWorld/Mods/Jawa_Doctrine/Assemblies/JawaDoctrineCore.dll` was written **10:33** and
the running RimWorld process started **11:23:36** — deployed before load, not after.

### The patch targets the right method, at the right point, and nothing undoes it
Three checks against 1.6 source (RimSage), each of which could have invalidated the fix:

1. **The `IsFlesh` gate is in `CreateInitialComponents`, not `AddAndRemoveDynamicComponents`.**
   ⚠️ This item's own Spec section above named the wrong method — the quoted code is real,
   but it lives at `RimWorld/PawnComponentsUtility.cs:8-151`, at the very END of
   `CreateInitialComponents`, immediately before that method calls
   `AddAndRemoveDynamicComponents` itself. `DoctrinePatches.Apply` postfixes
   **`CreateInitialComponents`**, which is the correct target. The spec's method name is a
   drafting error, not a defect in the shipped fix.
2. **Ordering is right.** `TryGenerateNewPawnInternal` (`Verse/PawnGenerator.cs:727-740`)
   calls `CreateInitialComponents(pawn)` as its third statement — before `GenerateTraits`,
   before `GeneratePawnRelations`, before every frame in the reported crash stack. A postfix
   there allocates `pawn.relations` before anything can dereference it.
3. **Nothing nulls it afterwards.** `AddAndRemoveDynamicComponents` (`:237-377`) touches
   `pawn.relations` exactly once, and only to **allocate** it (the Biotech mechanitor-subject
   branch). There is no assignment of `null` to `relations` anywhere in that method, so the
   postfix cannot be silently reverted later in generation.

The postfix's own guard set is the complement of vanilla's branch and nothing more —
`Humanlike && !IsFlesh && relations == null` — so no flesh pawn and no true mechanoid
changes behaviour.

### ⚠️ Latent, same gate, NOT fixed and deliberately not chased
The identical `if (pawn.RaceProps.IsFlesh)` block also guards **`pawn.psychicEntropy`**, and
the fix does not allocate that. Checked how bad that is rather than assuming: the per-tick
call is guarded (`Verse/Pawn.cs:2940`, `ModsConfig.RoyaltyActive && psychicEntropy != null`),
so there is **no per-tick NRE**. The unguarded dereferences are all psycast / meditation /
anima-linking paths (`Psycast.cs`, `Verb_CastPsycast.cs`, `RitualRoleAnimaLinker.cs`), which
a droid reaches only if it somehow acquires a psylink or is offered as an anima-linking ritual
role. Far narrower than the relations crash and not on the pawn-generation path. Recorded
here so the next reader knows it was a decision.

### 🔴 What is NOT proven, and why this item stays open
**Everything above is source and deployment evidence. None of it is the live 10/10.** The
quicktest could not be created this session — see the blocker below — so the batch spawn of
10× `OuterRim_BattleDroid` at `faction: null` has still never been run against the fixed
build. Per this project's own rule, a Harmony patch that reports nothing is exactly the class
of thing that must be SEEN working. Item stays `doing`.

### Blocker: the game is wedged and needs a restart (owner's action)
RimWorld (pid 33580, started 11:23:36) is stuck on a **"Loading world." long event that will
never complete**. Three `start_debug_game_ready` calls and one `load_game` all failed:
`get_game_info` has read `game_loaded / mapCount 0 / ticksGame 9252` unchanged for ~35
minutes, `go_to_main_menu` answers with its own NRE, `wait_for_long_event_idle` times out
with `"Last probe error: Object reference not set"`, and `Root_Play.UIRootUpdate` /
`UIRootOnGUI` throw every frame (`Find.WorldGrid` and `Find.WorldSelector` are null under a
live `Root_Play`). RimWorld's own logging has hit `"Reached max messages limit"`, so
`Player.log` has stopped growing. The bridge itself is healthy and answers in ~15 ms
throughout — this is a dead game, not a dead bridge, so the "wait, don't restart" rule does
not apply.
Screenshot: `C:\Users\Mandrake\AppData\LocalLow\Ludeon Studios\RimWorld by Ludeon Studios\Screenshots\zombie_probe_1.png`

**First cause, for the record:** the first two quicktests aborted inside
`BetterRomance.SettingsUtilities.ChildAge(Pawn)` — an NRE reached from
`PawnGenerator.GenerateTraits` via Better Romance's own transpiler, while generating the
quicktest scenario's **starting colonists**, before this session had spawned anything at all.
Third-party, unrelated to any Jawa/RimMandrake code, and unrelated to this item's bug.
