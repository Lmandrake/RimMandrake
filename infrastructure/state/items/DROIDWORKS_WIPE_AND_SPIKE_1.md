# DROIDWORKS_WIPE_AND_SPIKE_1 — memory wipe + faction-keyed data spike

Built both halves of the item scope. No deploy, no `ModsConfig.xml` change.

## Memory wipe — `Recipe_DWMemoryWipe`

Backs `DW_MemoryWipe` (`RecipeDefs/RecipeDefs_Droidworks.xml`). Whole-pawn
(`targetsBodyPart false`), no race restriction — same v0 precedent
`DW_RebootDroid`/`DW_InstallRestrainingBolt` already set.

- **Trait randomization reuses vanilla's own mechanism**, not a hand-rolled
  one: same COUNT of existing traits is removed via `TraitSet.RemoveTrait`,
  then re-rolled via `Verse.PawnGenerator.GenerateTraitsFor(pawn, count)` —
  the exact public static method `PawnGenerator.GenerateTraits` itself calls
  at growth moments. It already respects `TraitDef.ConflictsWith`
  (exclusivity), `disabledWorkTags`/`disabledWorkTypes`, `forcedPassions`,
  gender-specific commonality, and `RandomTraitDegree` for degree ranges —
  read via RimSage (`Source/Verse/PawnGenerator.cs:1564`) rather than
  guessed. Traits go back on through `TraitSet.GainTrait` so every
  downstream side effect (disabled-work recalculation, ability grants,
  graphics-dirty, mood recalculation) fires exactly as it would for a
  freshly generated pawn.
- **Relations**: `Pawn_RelationsTracker.ClearAllRelations()` directly —
  droids carry no blood relations, so the non-blood-only variant buys
  nothing here.
- **Social memories**: copies the exact idiom Anomaly's own memory-wipe
  mechanism uses. Read `Verse.AI.Group.PsychicRitualToil_Brainwipe
  .ApplyOutcome` via RimSage as the "real mechanism" per the item brief —
  it filters the pawn's `Thought_Memory` list by `is ISocialThought`, then
  calls `MemoryThoughtHandler.RemoveMemory` on each. That is the
  vanilla-recognized definition of "a social memory"
  (`Thought_MemorySocial` and its siblings implement `ISocialThought`).
  `Recipe_DWMemoryWipe` reuses the identical filter/remove idiom.
- **Idiosyncrasy hediffs: NONE EXIST YET.** `design/Jawa/
  droid_system_spec.md` sections 4 and 11 (the behavior triad; the
  "EXPERIENCED" idiosyncrasy tier) are explicitly "deliberately
  unengineered until played." Confirmed by a full-source RimSage search for
  "idiosyncrasy" across this codebase: **zero hits.** There is no
  idiosyncrasy `HediffDef` or system anywhere to zero. `ApplyOnPawn` has a
  comment marking this a documented no-op, not an invented placeholder.
- **Faction → player**: `pawn.SetFaction(Faction.OfPlayer, billDoer)`.
- **Skills untouched** — v0 scope, per BENCH's own words ("embodied
  software — skills live in the body"). `pawn.skills` is never referenced.
- `isViolation true` — `RecipeWorker.IsViolationOnPawn`'s own default logic
  already means "violation unless performed on your own faction's pawn,"
  which is exactly right: wiping your own droid isn't a violation, wiping a
  captured hostile is.

## Faction-keyed data spike — `DW_DataSpike`

**Reauthored the mechanism, not the donor mod's class.** Read the real
OuterRim Droid Depot source directly (workshop `3096501398`,
`1.6/Source/OuterRimDroids/`) to understand the actual wiring rather than
trusting `droid_ruling.md`'s prose summary alone:
`Comp_TargetableOnDownedDroid` (targeting gate), `Comp_TargetEffect_Reprogram`
(builds a *second* job), `JobDriver_ReprogramDroid` (the 600-tick job) — a
two-stage `CompUsable` → `CompTargetEffect` → second-job chain, and its
`JobDriver_ReprogramDroid.Reprogram()` never destroys the spent item (a gap,
not a feature).

**Our version is one stage, not two, and fixes that gap:**

- `Droidworks.CompDWDataSpike` / `CompProperties_DWDataSpike` — the faction
  key. **v0 keys ONE generic `DW_DataSpike` def to a single faction**
  (`spikeFaction` is a static XML value on that one `ThingDef`'s comp, not a
  per-instance runtime field) — matching the brief's "ONE generic def"
  framing. Picked `guy762_KotORFaction_RogueDroids` (the KotOR rogue droid
  collective) because `droid_ruling.md`'s own ruling names KotOR as "THE
  capture target" family. Adding another keyed faction later is another
  `ThingDef` of this same shape with a different `spikeFaction` value, not a
  C# change.
- `Droidworks.CompTargetable_DWDataSpike` — the reauthored targeting gate:
  `pawn.Downed || pawn.IsPrisoner` **and** the faction match, via
  `GetTargetingParameters().validator`. Deliberately **excludes corpses** —
  the donor's own documented bug (`droid_ruling.md` §8: "Do not use a data
  spike on a corpse... `InvalidCastException`") cannot happen here because
  corpses were never a legal target.
- `Droidworks.JobDriver_DWDataSpike` — the 600-tick job, shaped after
  `JobDriver_DWClampBolt.cs`'s own goto → delay-toil-with-progress-bar →
  `AddFinishAction` pattern. `DW_DataSpike`'s `CompProperties_Usable.useJob`
  points straight at this JobDef instead of vanilla's generic
  `JobDriver_UseItem`, so `CompUsable.TryStartUseJob` builds the job as
  `TargetA = the spike item, TargetB = the picked target` — which is exactly
  the index order this driver expects, with no second job needed. Effect:
  `target.SetFaction(Faction.OfPlayer, pawn)`, gated a second time
  (defense in depth) on `Downed||IsPrisoner` and the faction match at
  finish-time in case the situation changed mid-job. **The spike is
  destroyed at the end of the job regardless of outcome** — spent trying,
  closing the gap in the donor's own driver.

### The `DW_DroidHead` placeholder

`droid_verbs`/spec's crafting requirement ("a `RecipeDef` crafting a keyed
spike that CONSUMES a droid-head item of that faction") needs an ingredient
that **does not exist yet** — the shop/salvage pipeline that would drop a
real, faction-specific head off a damaged/destroyed droid is unbuilt. Ships
`DW_DroidHead`: a generic (not faction-differentiated) `ResourceBase` item,
`ResourcesRaw` category (it's salvage, not a crafted product), no
`recipeMaker` of its own — nothing produces it yet except spawning it. Its
own header comment states plainly: "the shop pipeline fills in the real
drop/salvage logic later; this placeholder exists so the recipe has
something real to consume today." `DW_DataSpike`'s `recipeMaker` consumes 1
of it (`costList`), craftable at `FabricationBench`, Crafting 6 — that
`recipeMaker` block *is* "the RecipeDef crafting a keyed spike" the brief
asks for (vanilla auto-generates a real `RecipeDef` from it, the same
convention `DW_RestrainingBoltItem` already used rather than a hand-written
standalone `RecipeDef`).

Art reused verbatim by texPath: `DW_DataSpike` uses OuterRim's own
`OuterRim/Items/DataSpike`; `DW_DroidHead` uses the KotOR HK-series head
texture already active in this mod's own generated race defs
(`Races_KotOR.xml`) — same "reuse an active mod's art" convention this
session already established twice.

## Files (new)

- `src/Jawa/Droidworks/Source/Droidworks/Recipe_DWMemoryWipe.cs`
- `src/Jawa/Droidworks/Source/Droidworks/CompDWDataSpike.cs`
- `src/Jawa/Droidworks/Source/Droidworks/CompTargetable_DWDataSpike.cs`
- `src/Jawa/Droidworks/Source/Droidworks/JobDriver_DWDataSpike.cs`

## Files (modified)

- `src/Jawa/Droidworks/Source/Droidworks/Droidworks.csproj` — 4 new
  `<Compile>` entries only, re-read fresh immediately before editing (per
  the multi-agent race note — the file's md5 matched what I'd read earlier
  in the session, so no concurrent edit landed between read and write).
- `src/Jawa/Droidworks/Defs/JobDefs/JobDefs_Droidworks.xml` — added
  `DW_DataSpike`.
- `src/Jawa/Droidworks/Defs/RecipeDefs/RecipeDefs_Droidworks.xml` — added
  `DW_MemoryWipe`.
- `src/Jawa/Droidworks/Defs/ThingDefs/Items_Droidworks.xml` — added
  `DW_DroidHead`, `DW_DataSpike`.

## Explicitly not built (per scope)

No deploy, no `ModsConfig.xml` activation, no skill-clearing (deliberate,
not deferred). Charging and restraining-bolt systems untouched. Additional
faction-keyed spikes (Separatists, Outer Rim automatons, etc.) are follow-up
— same shape, different `spikeFaction`/ingredient, not filed as a new item
since v0 explicitly scoped to one working key. Float-menu/WorkGiver wiring
for `DW_MemoryWipe`'s recipe onto race defs (`<recipes>` lists) is the same
"defined, not wired" precedent `DW_RebootDroid`/`DW_InstallRestrainingBolt`
already set.

## Validation

**`dotnet build` (Release):**
```
"/mnt/c/Users/Mandrake/.dotnet/dotnet.exe" build Droidworks.csproj -c Release
  Droidworks -> D:\Luke\dev\Rimworld\src\Jawa\Droidworks\Assemblies\Droidworks.dll
  Build succeeded. 0 Warning(s) 0 Error(s)
```

**`validate_patch.py` on the whole `Defs/` directory** (585 mods, capture
`2026-08-30T01-41-15Z` — confirmed newest on disk, same one the two prior
items in this session used):
`FAIL TOTAL - 14 file(s), 7 error(s), 0 warning(s)`.

Every file this item touched or added is individually clean:
`JobDefs_Droidworks.xml` — 0 errors, 0 warnings. `RecipeDefs_Droidworks.xml`
— 0 errors, 0 warnings. `Items_Droidworks.xml` — **3** errors, all
`ParentName="ResourceBase" resolves to no def carrying Name="ResourceBase"`
— the identical pre-existing false positive `DROIDWORKS_BOLT_CORE_1`
already confirmed and documented (vanilla Core's `ResourceBase` lives under
the game install's `Data/` tree, never under the `--defs Mods` path passed).
One of those three is `DW_RestrainingBoltItem`, present before this item
touched the file; the other two are my own `DW_DroidHead`/`DW_DataSpike`
hitting the identical class of false positive, not a new defect. The
remaining 4 errors (`Races_Base.xml` ×1 `ParentName="Human"`,
`Buildings_Charging.xml` ×3 `ParentName="BuildingBase"`) are pre-existing
and untouched by this item — same known-and-documented condition. The
`info`-level "Class not found" lines for every custom comp/extension across
the mod (mine included: `Droidworks.CompProperties_DWDataSpike`) are
expected — the offline scanner cannot load compiled assemblies, only XML
shape.

## Deployment status

**Not deployed.** No `ModsConfig.xml` change, per scope.
