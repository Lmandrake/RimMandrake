# FORGE_MECHANICS_1 — Forge C# mechanics kit

## spec

Map the FROZEN `design/Jawa/worldbuilding/biomes/the_forge.md` sheet's
mechanics onto the engine as a build-ready kit spec, then (build phase) ship
it: F1 boiling-rain weather pulse (scald bursts, flash cycle, flash-interval
growth), F2 beldon tibanna harvest (`RM_CompGatherableGas`), F3 vapor-column
flight layer for the sky fauna, F4 foundry tower dungeon shell (pocket-map
portal), F5 Contagion die-off ring, F6 geothermal vent industry (XML only).
Spec drafted 2026-09-11:
`design/Jawa/worldbuilding/biomes/kits/forge_kit_spec.md` — INVENTED values,
❓ engine unknowns, hard-ban table, build order, 3 owner cards, all there.

## verify

- Spec: every engine anchor either *(verified)* against the RimSage index /
  roster JSON or marked ❓; no lore invented beyond tuning values marked
  INVENTED; the sheet's §6 bans each bind a named linter check.
- Build (later): ❓ list resolved against live 1.6 source before C# is spent;
  portal-chaining quicktest run before any multi-floor tower work; scald
  gear-gate proven on a quicktest map (unroofed unarmored pawn takes scald
  during burst, geared pawn survivable, roofed pawn untouched).

## criteria

- `forge_kit_spec.md` exists in the kits register, follows the
  greentide/miasma pattern, and is registered in `design/INDEX.md`.
- `the_forge.md` Owed entry carries a DRAFTED pointer; no ruling changed.
- Owner cards (tower depth, rain lethality, penned beldons vs the embargo)
  reach a card sitting before the F1/F4 builds start.
  **DONE — 2026-09-13 (FOUNDRY):** all three RULED 2026-09-12, at the same
  sitting as Miasma/Fever Wood/Sump's cards (`MECHANICS_CARDS_SITTING_1`,
  closed). `forge_kit_spec.md`'s own header was stale ("unruled — next card
  sitting") despite every entry already reading "RULED 2026-09-12" —
  fixed to match. Build phase (spike pass, then full wiring) is now
  unblocked and owed.
- Build phase closes only when the six mechanics ship per the spec's v1
  lines and the hard-ban linter checks pass.

## spike pass — 2026-09-13, run per SCALD_MECHANICS_1's/MIASMA_MECHANICS_1's
own methodology

Sizing followed those items' own precedent exactly: prove each named ❓
minimally, offline, against real engine source (RimSage's index, the vendored
1.6/Odyssey decompile at `/mnt/d/Luke/dev/reference/rimworld-decompiled`,
and — where source alone couldn't settle it — the actual mod assemblies on
the owner's Steam install) or a real compiling artifact, not the full
6-mechanic build. New files added to the ruled kit home,
`src/RimMandrake/EnvironmentalHazards/` (`mandrake.rm.environmentalhazards`,
already extended repeatedly tonight). Builds clean:

```
"C:\Users\Mandrake\.dotnet\dotnet.exe" build D:\Luke\dev\Rimworld\src\RimMandrake\EnvironmentalHazards\Source\RM_EnvironmentalHazards.csproj -c Release
```
→ `Assemblies/RimMandrake.EnvironmentalHazards.dll`, **0 warnings, 0 errors**,
with the two new files below added.

### Engine ground-truth: all 5 named claims MEASURED against the real
1.6/Odyssey decompile, RimSage's live index, and (for the Aerofleet claim)
the actual Alpha Animals + Vanilla Expanded Framework assemblies on disk.

1. **Donor biomes for lava terrain — CONFIRMED, and the sheet's own donor
   line is half wrong.** `LavaField` is vanilla Odyssey DLC
   (`Defs/Odyssey/BiomeDefs/LavaField.xml`, a `LavaField` `FeatureDef` in
   `Defs/Odyssey/FeatureDefs/Features.xml`, `workerClass
   BiomeWorker_LavaField` in the core `RimWorld` namespace; the BiomeDef
   carries no `MayRequire` at all). `Volcano` is NOT vanilla — CONFIRMED
   absent from vanilla's own `RimWorld/LandmarkDefOf.cs` roster (24
   `[MayRequireOdyssey]` landmarks listed, no `Volcano`; nearest is
   `LavaFlow`) and absent everywhere in the decompile; it is **Advanced
   Biomes** (`emipa606/AdvancedBiomes`, WS 3541022508 —
   `design/Jawa/worldbuilding/biome_terrain_palette.md` §A3 already had this
   right: "Advanced Biomes uses unprefixed defNames... `Volcano`... lava +
   obsidian terrain"). `AB_PyroclasticConflagration` is CONFIRMED Alpha
   Biomes (`rosters/the_forge.json`'s own "Alpha pyroclastic donor family"
   line). Surfaced a naming collision already flagged elsewhere but worth
   restating: Advanced Biomes' OWN terrain
   (`AB_LiquidLava`/`AB_Obsidian`/`AB_VolcanicGravel`) also carries an `AB_`
   prefix — a different mod than Alpha Biomes, same two letters.
   Whether 1.6 lava terrain damages standing pawns natively — CONFIRMED yes,
   same native mechanism the Scald spike found: `TerrainDef.burnDamage`/
   `burnIntervalTicks` (`Verse/TerrainDef.cs:212`) read every tick by
   `Verse/HediffGiver_Terrain.cs:17`. The concrete vanilla terrain matters
   for F4's "open melt" framing: `LavaShallow` (merged def) is walkable
   (`burnDamage 3`, `burnIntervalTicks 120`, `dangerous true`,
   `avoidWander true`) — a real crossable hazard; `LavaDeep` is
   `Impassable` outright, so nothing (native or scripted) can stand on it.
   No C# needed — stock TerrainDef data + the stock HediffGiver.
2. **F3 Aerofleet float mechanism — CONFIRMED, and it is not Alpha
   Animals' own code.** `AA_Aerofleet`'s ThingDef
   (`.../workshop/content/294100/1541721856/1.6/Defs/ThingDefs_Races/Races_Aerofleet.xml`)
   carries `<li Class="VEF.AnimalBehaviours.CompProperties_Floating">` — a
   Vanilla Expanded Framework comp (WS 2023507013, `VEF.dll`). Binary-string
   read of `VEF.dll` (`MEASURE_ALLOW_SCAN=1`, the same technique the Scald
   spike used on `BadHygiene.dll`) found the real seam: a shared static
   roster (`floating_animals`, added/removed on spawn/despawn via
   `AddFloatingAnimalToList`/`RemoveFloatingAnimalFromList`) consumed by
   exactly one Harmony postfix,
   `VanillaExpandedFramework_Pawn_DrawTracker_DrawPos_Patch` — a patch on
   `Verse.Pawn_DrawTracker.DrawPos`'s getter applying a `FloatingOffset`.
   A second string, `DisablePathCostForFloatingCreatures`, confirms
   Aerofleet's "ignores terrain movement costs" flavor text is the same
   comp's doing. **Consequence**: `RM_CompVaporDrifter` should crib this
   exact seam (register into a shared list on spawn, one Harmony postfix on
   `Pawn_DrawTracker.DrawPos`) rather than a PawnRenderer node or def-side
   float property — no new dependency needed, this mod's `.csproj` already
   references `0Harmony.dll`.
3. **F3 wander-root vs ThinkTree seam — CONFIRMED, resolved by the miasma
   kit's own spike, not re-litigated.** `RM_CompTerritorialAnchor`
   (`src/RimMandrake/EnvironmentalHazards/Source/RM_CompTerritorialAnchor.cs`,
   MIASMA_MECHANICS_1's M6 spike) already found the real seam: vanilla's
   hive defenders use `Verse.AI.PawnDuty` read by two `protected virtual`
   JobGiver overrides — `JobGiver_HiveDefense`'s
   `GetFlagPosition`/`GetFlagRadius` and `JobGiver_WanderHive`'s
   `GetWanderRoot` (on `JobGiver_Wander`, a real overridable method). F3's
   pasture-binding needs no new engine proof — a sibling
   `RM_JobGiver_ColumnWander : JobGiver_Wander` overriding `GetWanderRoot`
   to consult `RM_MapComponent_VaporColumns.InColumn` is the same,
   already-compiling pattern; wiring it into a ThinkTreeDef is XML content
   work for the full build, not an open engine question.
4. **F4 portal-in-pocket-map chaining — NARROWED, still ❓, live quicktest
   still owed (none attempted this pass, per this item's own scope).**
   Full-body reads of `RimWorld/MapPortal.cs`, `Verse/PocketMapUtility.cs`,
   `Verse/MapGenerator.cs` and `RimWorld/MapPortalProperties.cs` found no
   guard anywhere checking whether a pocket map's own `sourceMap` is itself
   already a pocket map — `PocketMapParent.sourceMap` is untyped as to
   "must be a real map," `Find.World.pocketMaps` is a flat list with no
   depth field, and several `IsPocketMap` call sites (e.g.
   `RimWorld/GenStep_InsectLairCave.cs:130`) walk exactly one level up,
   which would silently stop short in a chain. So: nothing explicitly
   FORBIDS chaining, but nothing explicitly HANDLES it either — genuinely
   untested territory, which raises rather than lowers the live-test risk.
   The kit spec's own ❓ mark stays in place; PROVE in a quicktest before
   any multi-floor tower work, exactly as before.
5. **F5 exact PlantProperties field name — CONFIRMED, and the guessed name
   does not exist.** Full class read of `RimWorld/PlantProperties.cs`
   against the live decompile: no `reproduces`/`spreads`/`multiplies` field
   anywhere on the class. The real mechanism is
   `RimWorld/WildPlantSpawner.cs`'s `GetCommonalityOfPlant` (reads
   `RimWorld/BiomeDef.cs:419`'s `CommonalityOfPlant`, itself keyed off the
   BiomeDef's own `wildPlants` dict) — a plant absent from every BiomeDef's
   `wildPlants` gets commonality 0 and is never spread by
   `WildPlantSpawner`. **The linter check is therefore "`RUT_DyingCreep`
   appears in no BiomeDef's `wildPlants`," not "no `plant.reproduces`
   field"** (that field was never real). `forge_kit_spec.md` updated in
   place to say so.

### Built this pass (compiling proofs)

- **`RM_CompGatherableGas : CompHasGatherableBodyResource`** (F2) — the
  tibanna-tap generic, cribbing `CompMilkable`/`CompShearable`'s shape
  (both confirmed thin subclasses overriding only the four abstract
  accessors + `Active` + `CompInspectStringExtra`). Sex-independent per the
  spec's own line — no gender/life-stage gate beyond `base.Active` and the
  Anomaly shambler check both vanilla siblings carry. Inspect-line/job-label
  strings are XML-configurable translate keys on `CompProperties_GatherableGas`
  (`fullnessLabelKey`, default `RM_GasPressure`), not hardcoded tibanna text
  — the concrete `RUT_TibannaGas` ThingDef and beldon PawnKindDef wiring
  stay XML, later, per the spec's own scoping.
- **`RM_CompScriptedDieOff : ThingComp`** (F5) — generic spread-then-die:
  each spawned instance gets its own comp (XML `<li Class=...>` on a shared
  ThingDef), so "spread N cells over M hours, dead by hour X" is a
  per-instance countdown (`CompProperties_ScriptedDieOff`:
  `spreadAttemptCountRange`, `spreadRadius`, `spreadDurationHours`,
  `lifetimeHours`, `spreadThingDef`, `deadThingDef`, `deadThingIsFilth`) —
  no MapComponent coordinator needed for an S-effort spike. Cell picking
  uses `GenRadial.RadialCellsAround` + `IEnumerable.TryRandomElement` with a
  walkability/`ThingDef.CanEverPlantAt` predicate (both confirmed real
  signatures, decompile); death spawns `deadThingDef` via
  `FilthMaker.TryMakeFilth` (default) or `GenSpawn.Spawn`. Reusable beyond
  the Forge per the spec's own cross-flow note (`the_contagion.md`'s future
  kit is the named future consumer).
- `forge_kit_spec.md` updated in place at every resolved ❓ (donor biomes +
  lava damage, Aerofleet float mechanism + its stale "class-side vs
  def-side" hedge, the wander-root/ThinkTree seam, the plant-reproduction
  field correction); the F4 portal-chaining ❓ is narrowed but deliberately
  left in place with a live-quicktest requirement restated.

**Owed, not done, explicitly**: F1 (weather pulse/scald), F3's
`RM_MapComponent_VaporColumns`/`RM_CompVaporDrifter`/`RM_JobGiver_ColumnWander`
classes themselves (the seam is proven, the classes are not yet written —
that's full-build work), F4's floor GenSteps/entrance content and the
portal-chaining live quicktest, F6 (XML-only, unblocked, just not done this
pass), all roster/faction/item content, any live/quicktest verification of
anything in this write-up. Full 6-mechanic build stays separate FOUNDRY
work — item stays in `doing`.

## verdict

All 5 named ❓ engine claims resolved with file:line, decompile, or
binary-string citations against the real 1.6/Odyssey decompile and the
actual Alpha Animals + Vanilla Expanded Framework assemblies — none left a
guess standing, and one (F4) is honestly left ❓ because the source genuinely
does not settle it (narrowed, not resolved — a live quicktest is still
required, exactly as the kit spec already said). Two compiling C# proofs
landed (F2, F5), both S-effort exactly as scoped; F1/F3/F4 were explicitly
NOT started, per this item's own instructions. `forge_kit_spec.md` corrected
in five places, including fixing a wrong claim in the sheet's own donor
line (`Volcano` is Advanced Biomes, not vanilla) that this spike's source
read surfaced rather than assumed. Full 6-mechanic build, F1/F3/F4/F6
content authoring, and any live/quicktest pass are explicitly owed to a
later, separate FOUNDRY item.

## files

- `src/RimMandrake/EnvironmentalHazards/Source/RM_CompGatherableGas.cs` (new)
- `src/RimMandrake/EnvironmentalHazards/Source/RM_CompScriptedDieOff.cs` (new)
- `src/RimMandrake/EnvironmentalHazards/Source/RM_EnvironmentalHazards.csproj` (2 new `<Compile>` entries)
- `src/RimMandrake/EnvironmentalHazards/Assemblies/RimMandrake.EnvironmentalHazards.dll` (rebuilt, 0 warnings/errors)
- `design/Jawa/worldbuilding/biomes/kits/forge_kit_spec.md` (5 ❓s resolved/narrowed in place)
