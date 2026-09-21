# SHADEWHALE_EXTENSIONS_UNBUILT_1 — three C# types are missing from the deployed CreatureBehaviors DLL, and each one kills a def

## what is wrong

`Config error in RSW_ShadeWhale: no race` on every load. That message comes from the
**PawnKindDef**, and it means the **ThingDef** of the same name is not in the database at
all — its `<race>RSW_ShadeWhale</race>` has nothing to resolve to.

The ThingDef is discarded because three of its `Class=` attributes name C# types, and two
of them do not exist in the assembly the game loads:

`src/RimStarWars/SWBestiary/Defs/ThingDefs_Races/RSW_ShadeWhale.xml`

```
line  98  <modExtensions>
line 103    <li Class="RimMandrake.CreatureBehaviors.RM_ShadeSeekingWanderExtension">
line 131    <li Class="RimMandrake.CreatureBehaviors.RM_FilterFeedExtension">
line 144  <comps>
line 175    <li Class="RimMandrake.CreatureBehaviors.RM_CompProperties_DungSeeder">
```

**MEASURED 2026-09-21** against the deployed assembly
`C:\Program Files (x86)\Steam\steamapps\common\RimWorld\Mods\CreatureBehaviors\Assemblies\RimMandrake.CreatureBehaviors.dll`
(79,360 bytes, built 2026-09-20 12:45) — searched for each type name as both ASCII and
UTF-16LE:

| type | in the DLL | source on disk |
|---|---|---|
| `RM_ShadeSeekingWanderExtension` | **yes** | `src/RimMandrake/CreatureBehaviors/Source/RM_ShadeSeekingWanderExtension.cs` |
| `RM_FilterFeedExtension` | **no** | `src/RimMandrake/CreatureBehaviors/Source/RM_FilterFeedExtension.cs` |
| `RM_CompProperties_DungSeeder` | **no** | `src/RimMandrake/CreatureBehaviors/Source/RM_CompProperties_DungSeeder.cs` |

Both missing types are `DESERT_SHADE_WHALE_FILTERFEED_1`'s work. **The C# was written and
the assembly was never rebuilt**, so the def that consumes it has been dead since the day
it landed. An unresolvable `Class=` discards the whole def silently — the same failure
mode `SWBestiary/About/About.xml`'s own comment already documents (it promoted
`mandrake.rm.creaturebehaviors` from `loadAfter` to a hard `modDependency` on 2026-09-20
for exactly this, which is correct and is **not** the cause here: the dependency is
declared, the types simply are not compiled).

⛔ This is **not** a mod-list or dependency-declaration problem, and re-checking the
About.xml will not find anything. It is a build-and-deploy problem.

## CONFIRMED live, and it is not only the whale

A load on the `desertplants` tier (19 mods, all five DLC, `mandrake.rm.creaturebehaviors`
active) on 2026-09-21 printed the diagnosis verbatim:

```
Exception loading def from file RSW_ShadeWhale.xml: System.ArgumentException:
  Could not find type named RimMandrake.CreatureBehaviors.RM_CompProperties_DungSeeder
Could not resolve cross-reference: No Verse.ThingDef named RSW_ShadeWhale found to give
  to Verse.PawnKindDef RSW_ShadeWhale
Config error in RSW_ShadeWhale: no race
```

🔴 **And a third missing type takes a second def**, found in the same log:

```
Exception loading def from file RUT_Staggerseed_Hediffs.xml: System.ArgumentException:
  Could not find type named RimMandrake.CreatureBehaviors.RM_HediffCompProperties_ShadeStagger
Could not resolve cross-reference: No Verse.HediffDef named RUT_StaggerseedBrood found
  to give to RimWorld.IngestionOutcomeDoer_GiveHediff
```

⚠️ That `<li>` **is** `MayRequire="mandrake.rm.creaturebehaviors"` guarded, and the guard
passed — the mod was active. `MayRequire` checks the MOD, never the TYPE, so it is no
protection at all against an assembly that is present but stale. `RUT_StaggerseedBrood`
is the hediff `DESERT_STAGGERSEED_BUILD_1`'s whole cycle mechanism hangs off, so the
staggerseed currently spawns (VERIFIED, 2 on a live desert map) and does nothing.

⇒ **One rebuild fixes both defs.** Add
`RM_HediffCompProperties_ShadeStagger` to the table above when checking the output.

## also seen on that load, NOT this item's work

Three texture paths resolve to nothing — `Things/Plant/RM_Venomvine`,
`Things/Item/Plant/RUT_StaggerseedFruit`, `Things/Item/Meal/RUT_StaggerseedSeedDish`.
Art, not code; recorded here only so the next reader of that log does not re-diagnose it
as part of this defect.

## the work

1. Build `src/RimMandrake/CreatureBehaviors` (user-local .NET SDK, no Visual Studio — see
   the C# toolchain notes) and confirm the two types land in the output assembly with the
   same byte-level check used above, not by trusting the build log.
2. Deploy it. 🔴 **An assembly cannot be written while RimWorld is running** — this needs
   the game down, which is why this item is `needs: deploy` rather than offline.
3. Then re-check `RSW_ShadeWhale` resolves as a ThingDef and the config error is gone.

## criteria

`RimMandrake.CreatureBehaviors.dll` contains `RM_FilterFeedExtension` and
`RM_CompProperties_DungSeeder`, and a load produces **no** `Config error in
RSW_ShadeWhale` line while `jawa/get_defs ThingDef/RSW_ShadeWhale` resolves.

## provenance

Found by `BIOMEFLORA_PATCH_WIPES_WILDPLANTS_1` while clearing the config errors that the
same live load reported. Diagnosed to the assembly rather than fixed, because a C# build
plus a game-down deploy window is its own unit of work.
