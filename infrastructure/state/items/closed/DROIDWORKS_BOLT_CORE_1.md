# DROIDWORKS_BOLT_CORE_1 — restraining bolt core

Built the restraining-bolt CORE only (goodwill/faction layer is a later item,
per BENCH's own scope note). No deploy, no `ModsConfig.xml` change.

## What exists now

**HediffDefs** (`src/Jawa/Droidworks/Defs/HediffDefs/HediffDefs_Droidworks.xml`):
- `DW_RestrainingBolt` — pure vanilla `HediffStage` fields, **zero custom
  comp**. Verified against the live Droid Depot mod XML
  (`…/3096501398/1.6/Defs/HediffDefs/Droid_General.xml`) that
  `OuterRim_RestraintBolt` itself ships with no comps either — the whole
  mechanism is stage fields. Copied verbatim:
  - `capMods`: `Talking` `setMax 0` (mute), `Manipulation` `setMax 0.75`
    (25% clumsier).
  - `opinionOfOthersFactor` `0` — a `HediffStage` field, not a capMod; zeroes
    how much this pawn's opinion of others counts.
  - `statFactors`/`SlaveSuppressionFallRate` `0` (`MayRequire`
    `Ludeon.RimWorld.Ideology`), same fidelity to the source.
  - **The Manipulation XML shape**: `setMax` is a capMod field, not an
    offset or multiplier — offset is additive and vanilla capMods have no
    multiplicative field at all. `setMax 0.75` *caps the capacity's ceiling*
    at 75%, which **is** the 25%-clumsier expression, using the identical
    mechanism the mute cap uses at 0%.
- `DW_BoltResentment` — hidden (`everVisible false`) accumulator, backs the
  one new `HediffComp` this item needed
  (`HediffComp_DWBoltResentment.cs`). Rises only while `DW_RestrainingBolt`
  is present on a `Humanlike` (sapient) pawn; **pinned, never decays**, once
  the bolt is removed — mirrors `HediffComp_PoweredDown.CompPostTick`'s own
  "pin, never decay" trick (`severityAdjustment` forced to 0 every tick; the
  method's own conditional bump is the only thing that ever moves severity).
  Seeded onto a pawn by both application routes via the shared helper
  `DroidworksBoltUtility.EnsureBoltResentment`. **Stub accumulator only** —
  nothing reads the severity yet; `// TODO` comments on the def and the comp
  mark mood aura, idiosyncrasy-disable, and instant-rebellion-on-removal as
  unbuilt phase-3 work, per item scope.

**Harmony** (new sub-project, see below): a **prefix on
`Verse.AI.MentalBreakWorker.BreakCanOccur(Pawn)`** returning `false` (via
`__result = false; return false;`) whenever the pawn carries
`DW_RestrainingBolt` — copies exactly the mechanism `design/Jawa/
droid_ruling.md` section 3 documents for OuterRim's own bolt. Looked up by
defName (`DefDatabase<HediffDef>.GetNamedSilentFail("DW_RestrainingBolt")`,
cached after first resolve) rather than a hard reference to `Droidworks.dll`,
so it degrades quietly if Droidworks is absent/renamed and stays fully
independent of the main assembly's build order.

**Items + recipes**:
- `DW_RestrainingBoltItem` ThingDef (`ThingDefs/Items_Droidworks.xml`) — the
  physical bolt, craftable at `FabricationBench`. **Named `…Item`, not the
  bare `DW_RestrainingBolt`**, to avoid a C# `[DefOf]` field-name collision
  with the `HediffDef` of that name (RimWorld itself allows two Def *types*
  to share one defName — Droid Depot's own `OuterRim_RestraintBolt` does
  exactly that across HediffDef/ThingDef/RecipeDef — but `DroidworksDefOf`'s
  static fields can't share a name across two different Def types in one C#
  class). Texture path reused verbatim from Droid Depot
  (`OuterRim/Items/RestraintBolt`) — same "reuse an active mod's art by
  texPath" convention `Buildings_Charging.xml` already established for this
  mod; RimWorld resolves texPaths across all active mods' content packs, not
  just the owning mod's own folder.
- `DW_InstallRestrainingBolt` — the surgery route. `workerClass
  Droidworks.Recipe_InstallRestrainingBolt` (**one line** over vanilla
  `Recipe_InstallImplant`: calls `base.ApplyOnPawn` then
  `DroidworksBoltUtility.EnsureBoltResentment`). `targetsBodyPart false`
  needs zero override from vanilla to resolve as whole-pawn — confirmed
  against the live OuterRim recipe. `surgerySuccessChanceFactor 99999`,
  `isViolation true`, `anesthetize false` — copied from
  `OuterRim_AttachRestraintBolt` per the ruling doc. Consumes 1
  `DW_RestrainingBoltItem`.
- `DW_RemoveRestrainingBolt` — `workerClass
  Droidworks.Recipe_RemoveRestrainingBolt`, a **custom worker** (mirrors
  `Recipe_RebootDroid.cs`'s own whole-pawn `GetPartsToApplyOn`/`ApplyOnPawn`
  shape) because the bolt is whole-pawn — the same reason OuterRimDroids
  ships its own `Recipe_RemoveBolt` instead of vanilla
  `Recipe_RemoveImplant`. Reads `recipe.removesHediff` data-driven rather
  than a hardcoded DefOf. Deliberately does **not** touch
  `DW_BoltResentment`.
- `DW_ClampBolt` JobDef, backed by `JobDriver_DWClampBolt.cs` — the field
  route: 600 ticks on a **Downed** target (`FailOn(() => !Target.Downed)`),
  no bill, no ingredient, mirrors `OuterRim_RestrainDroid`'s own
  `JobDriver_RestrainDroid.Restrain()` (droid_ruling.md §3: "no droid check,
  no violation, no goodwill"). v0 simplification — same precedent
  `Recipe_RebootDroid.cs` already set (no ingredient consumed): the item
  still exists as the surgery route's crafted ingredient. **Wiring a
  float-menu option / WorkGiver to actually issue this job is left as
  follow-up** — same precedent `DW_RebootDroid`'s own header already
  accepted (recipe/job defined, invocation wiring deferred).

## Why "the two Hediff/HediffComp classes" became one

The brief anticipated two custom comp classes. Investigation
(`restraining_bolt_technical.md` §2, confirmed against the live Droid Depot
XML) showed `OuterRim_RestraintBolt` itself needs **zero** custom C# — pure
`HediffStage` fields. So `DW_RestrainingBolt` ships with no comp at all, and
the only comp built is `HediffComp_DWBoltResentment`. The "surgery recipe
workers" ask instead resolved to **two** custom `RecipeWorker` subclasses
(`Recipe_InstallRestrainingBolt`, `Recipe_RemoveRestrainingBolt`) — install
needed only a one-line override, removal needed the full whole-pawn pattern.

## Files (new)

- `src/Jawa/Droidworks/Source/Droidworks/DroidworksBoltUtility.cs`
- `src/Jawa/Droidworks/Source/Droidworks/HediffComp_DWBoltResentment.cs`
- `src/Jawa/Droidworks/Source/Droidworks/Recipe_InstallRestrainingBolt.cs`
- `src/Jawa/Droidworks/Source/Droidworks/Recipe_RemoveRestrainingBolt.cs`
- `src/Jawa/Droidworks/Source/Droidworks/JobDriver_DWClampBolt.cs`
- `src/Jawa/Droidworks/Defs/ThingDefs/Items_Droidworks.xml`
- `src/Jawa/Droidworks/Source/BoltCore/DroidworksBoltCore.csproj` (net48,
  new sub-project — see its own header comment for the full split rationale,
  copied from `JawaIonVehicleTier.csproj`'s known-good pattern)
- `src/Jawa/Droidworks/Source/BoltCore/BoltCorePatches.cs`

## Files (modified)

- `src/Jawa/Droidworks/Source/Droidworks/Droidworks.csproj` — 5 new
  `<Compile>` entries only, added after a fresh re-read immediately before
  editing; diffed afterward to confirm exactly 5 insertions, 0 deletions —
  no collision with `DROIDWORKS_WIPE_AND_SPIKE_1`'s concurrent edits.
- `src/Jawa/Droidworks/Source/Droidworks/DroidworksDefOf.cs` — added
  `DW_RestrainingBolt`, `DW_BoltResentment`, `DW_ClampBolt`,
  `DW_RestrainingBoltItem`.
- `src/Jawa/Droidworks/Defs/HediffDefs/HediffDefs_Droidworks.xml`
- `src/Jawa/Droidworks/Defs/JobDefs/JobDefs_Droidworks.xml`
- `src/Jawa/Droidworks/Defs/RecipeDefs/RecipeDefs_Droidworks.xml`

## Explicitly not built (per scope)

Goodwill/faction consequence layer, mood aura, idiosyncrasy-disable (stubbed
with `// TODO` only), float-menu/WorkGiver wiring for `DW_ClampBolt`, wiring
either recipe onto the race defs' own `<recipes>` list (same "defined, not
wired" precedent `DW_RebootDroid` already set). Charging and memory-wipe/data-
spike systems untouched.

## Validation

**Build — both 0 warnings / 0 errors:**
```
"/mnt/c/Users/Mandrake/.dotnet/dotnet.exe" build Droidworks.csproj -c Release
  Droidworks -> …/Droidworks/Assemblies/Droidworks.dll
  Build succeeded. 0 Warning(s) 0 Error(s)

"/mnt/c/Users/Mandrake/.dotnet/dotnet.exe" build DroidworksBoltCore.csproj -c Release
  DroidworksBoltCore -> …/Droidworks/Assemblies/DroidworksBoltCore.dll
  Build succeeded. 0 Warning(s) 0 Error(s)
```
(First BoltCore attempt failed — `MentalBreakWorker` lives in `Verse.AI`, not
`RimWorld`; fixed the `using`.)

**`validate_patch.py` on the whole `Defs/` directory** (585 mods, 68,787
live defNames from capture `2026-08-30T01-41-15Z`):
`14 files, 5 errors, 0 warnings` total. Every file this item touched or added
(`HediffDefs_Droidworks.xml`, `JobDefs_Droidworks.xml`,
`RecipeDefs_Droidworks.xml`) validates **0 errors, 0 warnings**.

The 5 errors are all `ParentName="X" resolves to no def carrying Name="X"`
against **vanilla Core base defs** (`BuildingBase`, `ResourceBase`, `Human`)
— a pre-existing environment limitation, not a regression: the tool's own
WARN line confirms 6 `ludeon.rimworld.*` packageIds (Core + every DLC) have
no folder under the `--defs Mods` path passed, because Core/DLC content
lives in the game install's `Data/` tree, never under `Mods/`. This exact
false-positive class already existed on `Races_Base.xml`
(`ParentName="Human"`, 1 error) and `Buildings_Charging.xml`
(`ParentName="BuildingBase"`, 3 errors) before this item touched them. My one
new `ParentName="ResourceBase"` on `DW_RestrainingBoltItem`
(`Items_Droidworks.xml`) hits the identical false positive — not a new class
of defect. The many `info`-level "Class not found" lines for every custom
comp/extension across the mod (mine included) are expected: the offline
scanner cannot load compiled assemblies, only XML shape.

## Deployment status

**Not deployed.** No `ModsConfig.xml` change, per scope.
