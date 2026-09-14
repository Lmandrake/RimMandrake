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

## F1 build pass — 2026-09-13

Build order step 2 (forge_kit_spec.md's own "Build order": step 1
`ALPHA_MECHANICS_KIT_1` already shipped). Wires F1 "The closed boiling
rain" — weather pulse, scald damage, flash-interval growth — into real,
shippable classes and XML content, per the spike pass's own resolutions
above. Followed the write-up style of `FEVER_WOOD_MECHANICS_1.md`'s own
"continuation pass" section (own real defs, no invented roster/creature
content).

**C# — 4 new classes, `src/RimMandrake/EnvironmentalHazards/Source/`:**

- **`WeatherPulseExtension : DefModExtension`** — the data side of the new
  condition (GameConditionDef has no props object, same reason
  `EnvironmentalWeatherExtension` exists). Generic: `baseWeather`,
  `burstWeather`, `burstMtbHours`, `burstDurationMinutesRange`,
  `flashWindowHoursAfterBurstStart`, plus a scald-damage field set that
  mirrors `EnvironmentalWeatherExtension`'s own shape
  (`scaldDamageDef`/`scaldDamageAmount`/`armorPenetration`/
  `scaldDamageIntervalTicks`/`onlyUnroofed`/`affects`/`immuneThingDefs`/
  `immunePawnKinds`). `ConfigErrors()` guards every INVENTED range.
- **`RM_GameCondition_WeatherPulse : GameCondition`** — forces
  `ext.baseWeather` via the vanilla `GameCondition.ForcedWeather()`
  override point (verified `Source/RimWorld/GameCondition.cs:345`, same
  hook `GameCondition_EnvironmentalWeather` already uses); rolls
  `Rand.MTBEventOccurs(burstMtbHours, 2500f /*ticks/hour*/, 1f)` once per
  `GameConditionTick` while not already in a burst; on a hit, switches
  `ForcedWeather()` to `ext.burstWeather` for a randomized
  `burstDurationMinutesRange` window and starts the flash window (below)
  on every affected map. While a burst runs, deals scald damage on
  `scaldDamageIntervalTicks` — a **reparameterized copy of
  `GameCondition_EnvironmentalWeather.DoPawnEffects`'s own damage shape**
  (same `HazardTargeting.Affects` gate, same `onlyUnroofed` check, same
  `RM_EnvironmentalHazardsSettings.hazardDamageMultiplier`/
  `environmentalDamageEnabled` gates), not a call into that class — it
  forces one weather and damages continuously, this condition must gate
  the identical shape to "currently in a burst" only, so the donor class
  itself is left untouched (it is shared by every other kit referencing
  `EnvironmentalWeatherExtension`: miasma, scald, sump, fever wood).
  `ExposeData` Scribes `inBurst`/`burstWeatherEndTick`/
  `ticksUntilScaldDamage`.
- **`RM_MapComponent_FlashCycle : MapComponent`** — generic
  `StartWindow(startTick, durationTicks)` / `InFlashWindow()` pair (same
  posture as `RM_MapComponent_GradientAxis`). Auto-instantiates on every
  map via `Map.FillComponents()`'s reflection scan (verified decompile,
  no XML wiring needed for the component itself). The window is set to
  `flashWindowHoursAfterBurstStart` from burst **start**, deliberately
  independent of the burst weather's own shorter duration — it is meant
  to outlast the rain itself, per the spec's own "until 2 in-game hours
  after" line.
- **`RUT_Plant_FlashFlora : Plant`** — overrides `Plant.GrowthRate`
  (`public virtual`, verified `Source/RimWorld/Plant.cs:289`),
  multiplying `base.GrowthRate` (so blight/season/fertility/temperature/
  light/drought all still apply — only the result is scaled) by ×8.0
  inside the flash window, ×0.05 outside it (both INVENTED, F1 spec,
  overridable via `protected virtual` properties for a future biome).
  Named `RUT_` (not `RM_`) per this task's own instruction even though it
  carries no Forge-specific data — reusable base class, no concrete Plant
  ThingDef needed to compile, matching `RM_CompScriptedDieOff`'s own
  posture from the spike.
- **Mod option** (`RM_EnvironmentalHazardsMod.cs`): new
  `weatherPulseEnabled` toggle (default on). Off: the condition never
  starts a new burst (a burst already running finishes rather than
  snapping off) and stays on its base weather permanently; the plant
  class returns `base.GrowthRate` unmultiplied instead of being stuck at
  the "outside window" ×0.05 forever with no burst ever able to lift it —
  required for MOD_OPTIONS_RETROFIT_1's all-off-degrades-gracefully rule,
  not merely nice-to-have (without this special case, turning the toggle
  off would silently cripple every flash-flora plant on the map).

**Cross-kit reuse landed, not deferred**: `forge_kit_spec.md` F1's own
"the scald" line says `RUT_Scald`/`RM_ScaldArmor` are the greentide kit's
M3 DamageDef/DamageArmorCategoryDef, "cross-kit reuse — if the greentide
build slips, the def is XML and ships here first." Checked this pass: no
`RUT_Scald`/`RM_ScaldArmor` def exists anywhere in the repo (confirmed via
grep across `src/` and `design/` — `GREENTIDE_MECHANICS_1`'s own M3 has
not landed) — so this pass ships them, per the spec's own named
contingency:

- **`RM_ScaldArmor.xml`** (`DamageArmorCategoryDef`,
  `src/RimMandrake/EnvironmentalHazards/Defs/DamageArmorCategoryDefs/`,
  RM_-tier home matching its RM_ prefix) — `armorRatingStat
  RM_ArmorRating_Scald`, no `multStat` (no vendored Stuff in this repo
  grants scald resistance, unlike vanilla's Sharp/Blunt/Heat trio each
  citing a `StuffPower_Armor_*` stat).
- **`RM_ArmorRating_Scald.xml`** (`StatDef ParentName="ArmorRatingBase"`,
  same folder family, `Defs/StatDefs/`) — cribs the vanilla
  `ArmorRating_Sharp`/`Heat` shape (RimSage-verified: category, value
  range, `toStringStyle` all inherited from the abstract base; only the
  quality-scaling `StatPart` repeated, no `StatPart_Stuff`).
- **`RUT_Scald.xml`** (`DamageDef`, `src/RimUtinni/UtinniPatches/Defs/
  DamageDefs/`, RUT-tier — campaign content, not generic) — **not**
  Flame-class (no `ParentName="Flame"`, no `DamageWorker_Flame`) per the
  spec's own "not a Flame-class damage → no ignition" line; cribbed
  vanilla `Frostbite`'s posture instead (RimSage-verified: environmental
  injury, `externalViolence false`, no ignition) with `workerClass
  DamageWorker_AddInjury` and `hediff Burn` (an ordinary burn wound to the
  player/health system; only `armorCategory` makes it scald-typed for
  defense). `armorCategory` cross-references `RM_ScaldArmor` with its own
  `MayRequire="mandrake.rm.environmentalhazards"` so the field degrades to
  unset rather than a dangling cross-reference if that mod is absent.

**Forge-specific content, `src/RimUtinni/UtinniPatches/`:**

- **`Defs/WeatherDefs/RUT_ForgeStill.xml`** — the calm state (`rainRate
  0`), ambient/sky values cribbed from the biome's own already-shipped
  `AB_VolcanicAsh` donor stand-in (warmer/redder tint). Never reachable
  via natural weather-commonality rolls (`RUT_TheForge.xml`'s
  `baseWeatherCommonalities` does not list it) — only
  `ForcedWeather()` ever selects it.
- **`Defs/WeatherDefs/RUT_BoilingRain.xml`** — the burst state
  (`rainRate 1`, real driving rain per the spec's own "WeatherDef.rainRate
  is a native field" line), `moveSpeedMultiplier`/`accuracyMultiplier`
  mirroring vanilla `RainyThunderstorm`'s own figures (a real storm).
  Carries no damage fields itself — `WeatherDef` has none in the live
  decompile; scald damage is `RUT_ForgePulse`'s own
  `WeatherPulseExtension.scaldDamageDef`, ticking independently of which
  weather is currently drawn.
- **`Defs/GameConditionDefs/RUT_ForgePulse.xml`** — the concrete
  `GameConditionDef` (`canBePermanent true`, matching the donor
  `AB_VolcanicHeatWave`'s own field — required because
  `BiomeDef.biomeMapConditions` entries are always made permanent by the
  engine, verified `RimWorld/BiomeConditionMapComponent.cs`). Tuning: MTB
  mean 10h, burst 20–40min, flash window 2h from burst start, ~4 scald
  dmg/60-tick interval unroofed-only — all INVENTED per the spec's own
  figures, matching owner card 2 ("boiling rain is survivable once...
  never instant death from one burst").
- **`Patches/RUT_ForgePulse_BiomeWiring.xml`** — wires `RUT_ForgePulse`
  onto `RUT_TheForge` via `PatchOperationAdd` (`RUT_TheForge.xml` carries
  no `<biomeMapConditions>` node today), **not** a direct edit to the
  BiomeDef — exactly the caution `SCALD_MECHANICS_1`'s own
  `RUT_ScaldSteamLock_BiomeWiring.xml` already established for this exact
  file family (built the same day, found while surveying precedent for
  this pass): a bare `<li>` baked into the BiomeDef would be a dangling
  cross-reference the moment `mandrake.rm.environmentalhazards` is absent.
  `RUT_TheForge.xml` itself is **not edited** — its own
  `baseWeatherCommonalities` (AB_VolcanicAsh/AB_VolcanicAshRain/
  RSW_SW_RedFog/Clear) is left as-is; once `RUT_ForgePulse` registers,
  `ForcedWeather()` overrides natural selection unconditionally for as
  long as the (permanent) condition runs, so those entries go
  structurally unreachable rather than wrong — re-tuning that table is
  biome-authoring judgment outside this build pass's scope.

**Build**: `RM_EnvironmentalHazards.csproj` rebuilds clean with the 4 new
`<Compile>` entries — **0 warnings, 0 errors**.

**Validate**: `skills/rimworld-modding/scripts/validate_patch.py` on all 7
new/changed files against the live 589-mod installed set (`--defs` Data +
Mods + Workshop root + both source mods) — **0 errors**, 1 advisory
warning (the `PatchOperationAdd` not wrapped in `PatchOperationConditional`
— the same advisory the `RUT_ScaldSteamLock_BiomeWiring.xml` precedent
produces for the identical shape; the Operation's own `MayRequire` is the
real guard). One info-level note on `RUT_ForgePulse.xml` flagging that
`WeatherPulseExtension`'s `Class` isn't yet visible to the validator's
installed-mod scan — expected: the assembly is freshly rebuilt in `src/`,
not yet deployed to the live `Mods/` folder (deployment is explicitly out
of this task's scope).

**Explicitly NOT done, per this task's own scope**: F2 (tibanna tap), F3
(vapor columns), F4 (towers), F5 (die-off ring), F6 (geothermal) —
untouched, separate build-order steps. No PawnKindDef/creature/roster
content authored. `ModsConfig.xml` untouched. No bridge/game/quicktest run
— offline only, as instructed; the scald gear-gate live-fire verification
the spec's own "verify" section calls for (`unroofed unarmored pawn takes
scald, geared pawn survivable, roofed pawn untouched`) is still owed to a
live quicktest pass, not attempted here.

## files

- `src/RimMandrake/EnvironmentalHazards/Source/RM_CompGatherableGas.cs` (new)
- `src/RimMandrake/EnvironmentalHazards/Source/RM_CompScriptedDieOff.cs` (new)
- `src/RimMandrake/EnvironmentalHazards/Source/WeatherPulseExtension.cs` (new, F1)
- `src/RimMandrake/EnvironmentalHazards/Source/RM_GameCondition_WeatherPulse.cs` (new, F1)
- `src/RimMandrake/EnvironmentalHazards/Source/RM_MapComponent_FlashCycle.cs` (new, F1)
- `src/RimMandrake/EnvironmentalHazards/Source/RUT_Plant_FlashFlora.cs` (new, F1)
- `src/RimMandrake/EnvironmentalHazards/Source/RM_EnvironmentalHazardsMod.cs` (edit, F1: `weatherPulseEnabled` toggle)
- `src/RimMandrake/EnvironmentalHazards/Defs/DamageArmorCategoryDefs/RM_ScaldArmor.xml` (new, F1)
- `src/RimMandrake/EnvironmentalHazards/Defs/StatDefs/RM_ArmorRating_Scald.xml` (new, F1)
- `src/RimUtinni/UtinniPatches/Defs/DamageDefs/RUT_Scald.xml` (new, F1)
- `src/RimUtinni/UtinniPatches/Defs/WeatherDefs/RUT_ForgeStill.xml` (new, F1)
- `src/RimUtinni/UtinniPatches/Defs/WeatherDefs/RUT_BoilingRain.xml` (new, F1)
- `src/RimUtinni/UtinniPatches/Defs/GameConditionDefs/RUT_ForgePulse.xml` (new, F1)
- `src/RimUtinni/UtinniPatches/Patches/RUT_ForgePulse_BiomeWiring.xml` (new, F1)
- `src/RimMandrake/EnvironmentalHazards/Source/RM_EnvironmentalHazards.csproj` (2 new `<Compile>` entries from the spike, 4 more from F1)
- `src/RimMandrake/EnvironmentalHazards/Assemblies/RimMandrake.EnvironmentalHazards.dll` (rebuilt, 0 warnings/errors)
- `design/Jawa/worldbuilding/biomes/kits/forge_kit_spec.md` (5 ❓s resolved/narrowed in place)
