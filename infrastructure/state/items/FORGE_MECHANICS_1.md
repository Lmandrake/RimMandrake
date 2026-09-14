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

## F2/F5/F6 build pass — 2026-09-13

Build order steps 4-5 and 3 (forge_kit_spec.md's own "Build order": F1
already shipped). Wires F2 "the tibanna harvest", F5 "the Contagion die-off
ring" and F6 "geothermal industry" into real, shippable content on top of
the spike pass's two already-compiling comps (`RM_CompGatherableGas`,
`RM_CompScriptedDieOff`). F3 (vapor columns), F4 (towers) untouched, per
this pass's own scope. No bridge/game/quicktest — offline only.

**F2 — tibanna tap.** The shipped Beldon is `RSW_Beldon`
(`src/RimStarWars/SWBestiary/Defs/ThingDefs_Races/RSW_Beldon.xml`,
MLIE_FAUNA_ABSORPTION_1 Wave C — repo-owned, RSW_ tier, not a donor/vendor
folder). Patched rather than hand-edited even though repo-owned: it is
generic RimStarWars-tier content, and the tap is Utinni-tier campaign
mechanics — same discipline F1's own `RUT_ForgePulse_BiomeWiring.xml`
already applied to `RUT_TheForge` itself. `RUT_TibannaTap_BeldonWiring.xml`
(`PatchOperationAdd`, `MayRequire="mandrake.rm.environmentalhazards"`)
appends `RM_CompGatherableGas`'s comp onto `RSW_Beldon`'s existing `<comps>`
node at the spec's own INVENTED values (interval 2 days, amount 12).
`RUT_TibannaGas.xml` ships the resource good (`ParentName="ResourceBase"`,
no comps of its own, MarketValue an explicit placeholder —
`TIBANNA_EMBARGO_PLOT_1` owns real pricing).

**Ban #5 linter check — PASS.** Repo-wide grep for `RUT_TibannaGas` outside
its own def file: the ONLY hit is the single `<gatherDef>RUT_TibannaGas</gatherDef>`
in `RUT_TibannaTap_BeldonWiring.xml`. No RecipeDef product, no
butcherProducts, no trader-stock tag anywhere names it — the monopoly holds
by construction.

**F5 — Contagion die-off ring.** `RUT_DeadCreep` (filth, `ParentName="BaseFilth"`,
`rainWashes false` — ban 6 means ordinary rain never reaches this biome
anyway, so leaving it `true` would document an unreachable mechanism).
`RUT_DyingCreep` (`ParentName="PlantBase"`, carries
`RM_CompScriptedDieOff` at its class defaults — spread 6~10 over 4h, dead
by 8h, matching the spec's own INVENTED figures exactly, only `deadThingDef`
overridden to `RUT_DeadCreep`). Ban-edge check: `RUT_DyingCreep` is listed
in no BiomeDef's `wildPlants` anywhere in this repo (confirmed — this pass
touches no BiomeDef's `wildPlants` at all) and carries no `sowTags`
(unsowable) and `harvestable` unset (defaults false) — the spike's own
resolution ("no `plant.reproduces` field exists; the real gate is
`wildPlants` absence") is satisfied structurally, not by a flag.

Gen-time scatter: `RM_GenStep_EdgeBandFilth` (new C# this pass) — a
bespoke, generic (biome-list + filthDef + band + chance, all XML-settable)
edge-band paint pass, NOT a reuse of `RM_GenStep_PlacedSetPieces` or
vanilla `GenStep_ScatterThings`: both of those pick N discrete sites via
the scatterer framework, built for set-pieces, and a patchy contiguous band
near the map edge is a different shape entirely — judgment call the spec's
own text explicitly invited ("reuse if genuinely a fit... use judgment,
don't force-fit"). `RUT_ContagionRingScatter.xml` configures one instance
(`RUT_DeadCreep`, biomes `[RUT_TheForge]`, band 8~15 cells, 0.35 chance/cell)
and `RUT_ContagionRingScatter_Register.xml` adds it to `Base_Player`'s
`genSteps` globally — safe everywhere per the class's own biome-list no-op,
same registration pattern `RUT_ScaldWreckScatter_Register.xml` already
established.

The probe: `RUT_IncidentWorker_ContagionProbe` (new C#) hardcodes the
`RUT_TheForge` biome check directly (the kit spec's own gate is singular —
one merged BiomeDef, not a list) — finds a standable map edge cell, spawns
a 3-6 count cluster of `RUT_DyingCreep` within radius 4 (INVENTED,
"cluster"), sends a standard letter (`RUT_ContagionProbe.xml`, `baseChance
1.5`, `minRefireDays 8` — the spec's own "~1 per 8 days" read as the
storyteller's idiomatic refire floor, same conversion
`RUT_FeverWood_MirrorBreak.xml` already uses for its own plain-English MTB).
Translate keys in `RUT_Forge_Mechanics.xml`.

**F6 — geothermal industry, pure XML.** `RUT_VentSmelter` /
`RUT_VentForge` / `RUT_VentKiln`, all `ParentName="BenchBase"`,
`thingClass Building_WorkTable` (no fuel/power comp of any kind), gated
onto real vanilla steam geysers via the stock `PlaceWorker_OnSteamGeyser`
(`RimWorld/PlaceWorker_OnSteamGeyser.cs`, decompile-read this pass:
`AllowsPlacing` requires this building's own anchor cell to literally BE
the geyser's anchor cell, `ForceAllowPlaceOver` allows building directly
over it) — size `(2,2)` matching vanilla `SteamGeyser`'s own footprint
exactly (confirmed via RimSage). `WorkTableWorkSpeedFactor 1.2` (+20%,
INVENTED per this task's brief) on all three; `BenchBase`'s own
`CompProperties_ReportWorkSpeed` already surfaces that stat, confirmed
reading `BenchBase`'s raw XML this pass.

Recipe cribs, verified against the live installed set rather than invented:
- `RUT_VentSmelter` copies vanilla `ElectricSmelter`'s own `<recipes>` list
  verbatim (`ExtractMetalFromSlag`/`SmeltOrDestroyThing`/`SmeltWeapon`/
  `SmeltApparel`/`DestroyWeapon`/`DestroyApparel`) — that building lists
  recipes directly on itself, so a direct copy is correct here.
- `RUT_VentForge` mirrors `FueledSmithy` via a PATCH
  (`RUT_VentForge_RecipeWiring.xml`), not a copied list: vanilla smithing
  recipes are each weapon/apparel `ThingDef`'s own
  `<recipeMaker><recipeUsers>` entry (confirmed reading
  `Core/Defs/ThingDefs_Misc/Weapons/BaseWeapons.xml:125-135`, the
  `BaseMeleeWeapon` abstract — NOT a standalone RecipeDef), so the patch's
  xpath (`ThingDef[recipeMaker/recipeUsers/li="FueledSmithy"]/recipeMaker/recipeUsers`)
  matches on content, reaching 11 ThingDefs in the live set (weapons,
  headgear, apparel) and automatically mirroring any future addition using
  the same entry, not a snapshot.
- `RUT_VentKiln` mirrors vanilla `TableStonecutter` — 🔴 **honest
  substitution, not the literal thing this task asked for**: there is NO
  "Kiln" ThingDef anywhere in this repo, the vanilla Core/DLC Data folders,
  or the live ~599-mod installed set (checked three ways: RimSage's own def
  index, a full-text grep of every `Data/*/Defs` tree, and a defName grep
  across the Workshop content root — all zero). `TableStonecutter` was
  picked as the closest fit in the family's absence: the one vanilla
  production bench that already needs no fuel AND no power, so stripping it
  costs nothing, versus forcing a second smithy-shaped def to stand in for
  "kiln." Recipes wired the same content-match-patch way as VentForge
  (`RUT_VentKiln_RecipeWiring.xml`, targeting the one `RecipeDef` node —
  the abstract `MakeStoneBlocksBase` — whose `recipeUsers` names
  `TableStonecutter`; 12 live matches: vanilla stone blocks, Alpha Biomes'
  own stone recipes, Star Wars Animal Collection's ivory recipes).

**Art.** All six new visible ThingDefs (`RUT_TibannaGas`, `RUT_DeadCreep`,
`RUT_DyingCreep`, `RUT_VentSmelter`, `RUT_VentForge`, `RUT_VentKiln`) were
originally drafted to reuse an existing vanilla texPath as a placeholder
(the same practice `RUT_WickStem.xml`/`RM_FE_Filth_LooseAsh.xml` already
established) — `validate_patch.py` refused all six as a hard ERROR: this
mod already ships its own `Things/Building`, `Things/Item`, `Things/Filth`
and `Things/Plant` trees elsewhere, so its own-namespace heuristic cannot
tell a deliberate cross-mod reuse from a typo in this mod's own art (its
own source documents this exact tradeoff at `validate_patch.py:1838-1890`).
Rather than ship six disputed texPath claims with no live game access this
task to settle them, each was repointed to its own new RUT_-named path and
held via `src/DEPLOY_HOLD.txt` — same shape as every other new-art hold in
that file (Scald/Sump precedent). `validate_patch.py` result: 6 expected/held
texPath errors (the ONLY failures — same accepted shape the Scald/Sump
holds document), 0 other errors, 3 warnings (`PatchOperationAdd` not
wrapped in `PatchOperationConditional`/`PatchOperationFindMod` on
`RUT_TibannaTap_BeldonWiring.xml`, `RUT_VentForge_RecipeWiring.xml`,
`RUT_VentKiln_RecipeWiring.xml` — `MayRequire` on each Operation is the
real guard, same accepted posture as every other same-family patch in this
mod, e.g. `RUT_ForgePulse_BiomeWiring.xml`).

**Build**: `RM_EnvironmentalHazards.csproj` rebuilds clean with 2 new
`<Compile>` entries (`RM_GenStep_EdgeBandFilth.cs`,
`RUT_IncidentWorker_ContagionProbe.cs`) — **0 warnings, 0 errors**. (Note:
this shared `.csproj` and the DLL are being built on concurrently by other
FOUNDRY/BENCH agents tonight — this pass's own two `<Compile>` entries were
appended against the live file each time a concurrent edit landed first,
per this repo's own documented "whole staged index" discipline; the two
entries this pass owns are confirmed present.)

**Explicitly NOT done, per this task's own scope**: F3 (vapor columns), F4
(towers) — untouched. `ModsConfig.xml` untouched. No bridge/game/quicktest
run. Art for all six new visible things (held, `src/DEPLOY_HOLD.txt`). Live
verification of the tap cadence, the die-off ring's actual visual density,
the probe's cluster placement, and the three Vent* buildings' in-game
placement onto a real geyser are all owed to a live quicktest pass, not
attempted here.

### files (F2/F5/F6 build pass)

- `src/RimMandrake/EnvironmentalHazards/Source/RM_GenStep_EdgeBandFilth.cs` (new, F5)
- `src/RimMandrake/EnvironmentalHazards/Source/RUT_IncidentWorker_ContagionProbe.cs` (new, F5)
- `src/RimMandrake/EnvironmentalHazards/Source/RM_EnvironmentalHazards.csproj` (2 new `<Compile>` entries)
- `src/RimMandrake/EnvironmentalHazards/Assemblies/RimMandrake.EnvironmentalHazards.dll` (rebuilt, 0 warnings/errors)
- `src/RimUtinni/UtinniPatches/Defs/ThingDefs_Items/RUT_TibannaGas.xml` (new, F2)
- `src/RimUtinni/UtinniPatches/Patches/RUT_TibannaTap_BeldonWiring.xml` (new, F2)
- `src/RimUtinni/UtinniPatches/Defs/ThingDefs_Items/RUT_DeadCreep.xml` (new, F5)
- `src/RimUtinni/UtinniPatches/Defs/ThingDefs_Plants/RUT_DyingCreep.xml` (new, F5)
- `src/RimUtinni/UtinniPatches/Defs/MapGeneration/RUT_ContagionRingScatter.xml` (new, F5)
- `src/RimUtinni/UtinniPatches/Patches/RUT_ContagionRingScatter_Register.xml` (new, F5)
- `src/RimUtinni/UtinniPatches/Defs/IncidentDefs/RUT_ContagionProbe.xml` (new, F5)
- `src/RimUtinni/UtinniPatches/Languages/English/Keyed/RUT_Forge_Mechanics.xml` (new, F2/F5)
- `src/RimUtinni/UtinniPatches/Defs/ThingDefs_Buildings/RUT_VentSmelter.xml` (new, F6)
- `src/RimUtinni/UtinniPatches/Defs/ThingDefs_Buildings/RUT_VentForge.xml` (new, F6)
- `src/RimUtinni/UtinniPatches/Defs/ThingDefs_Buildings/RUT_VentKiln.xml` (new, F6)
- `src/RimUtinni/UtinniPatches/Patches/RUT_VentForge_RecipeWiring.xml` (new, F6)
- `src/RimUtinni/UtinniPatches/Patches/RUT_VentKiln_RecipeWiring.xml` (new, F6)
- `src/DEPLOY_HOLD.txt` (edit — 6 new held entries)

## F3 build pass — 2026-09-14

Build order step 6 (forge_kit_spec.md's own "Build order": F1/F2/F5/F6
already shipped; F4 towers is separate, later work, not this pass). Wires
F3 "the vapor-column flight layer" — the pasture-binding half of the sky
fauna mechanic, since F3's own float mechanism (VEF's `CompFloating` via a
class-side Harmony postfix on `Pawn_DrawTracker.DrawPos`) was already
CONFIRMED class-side and needing no further code by the spike pass. No
bridge/game/quicktest — offline only, per this task's own scope.

**C# — 2 new classes, `src/RimMandrake/EnvironmentalHazards/Source/`:**

- **`RM_MapComponent_VaporColumns : MapComponent`** — the column field.
  Generic emitter detection, not Forge-hardcoded: any spawned
  `RimWorld.Building_SteamGeyser` (native geysers, and this repo's own
  `RUT_ScaldVent` clone, which shares that thingClass verbatim), any
  spawned Thing carrying `CompActiveGasEmitter`, and any terrain cell
  flagged `dangerous && avoidWander` — the exact two fields the F1 spike
  confirmed on vanilla `LavaShallow` (open, walkable melt), read generically
  rather than by a `"Lava"` defName substring so any biome's own hazardous
  open-melt terrain qualifies without this class knowing its name. Checked
  this pass: no Forge vent content actually carries `CompActiveGasEmitter`
  yet (`RUT_ScaldVent.xml`'s own header explicitly says it does NOT — that
  was a stale brief-vs-spec correction on a different, earlier item) — the
  comp-based route is real but forward-looking, not dead code; the terrain
  flag and native `Building_SteamGeyser` routes are live today against any
  map with vanilla/Odyssey geysers or Scald's own vent clone.
  `InColumn(IntVec3)` (spec's own required public API) and
  `NearestColumnCell(from, maxDist)` (the wander-root lookup). "At map init
  + on-change" (spec's own line) is implemented as a full rebuild on
  `FinalizeInit` plus an hourly rescan (2500 ticks, the same
  ticks/hour conversion `RM_GameCondition_WeatherPulse` and
  `RM_CompScriptedDieOff` already use) rather than push notifications from
  every emitter/terrain-change source — emitters are near-static once
  placed, and wiring spawn/despawn callbacks into the shared
  `CompActiveGasEmitter` (a cross-kit reuse F1/F2/F6 all also depend on)
  would be exactly the kind of fork this task's brief said not to do for
  F3's sake. `RebuildNow()` is public for a future quicktest or GenStep to
  force an immediate rebuild. Not Scribe-saved — the field is entirely
  derived from map content, so `FinalizeInit`'s own rebuild reconstructs it
  identically on load, same reasoning `RM_MapComponent_GradientAxis`'s own
  header gives for deferring a per-cell save format.
- **`RM_CompVaporDrifter : ThingComp`** (+ `CompProperties_VaporDrifter`,
  `RM_JobGiver_ColumnWander : JobGiver_Wander`) — the pasture-binding comp
  and its wander-root override, generalizing `RM_CompTerritorialAnchor`'s
  own `RM_JobGiver_AnchorWander` pattern exactly as the spec's own F3
  resolution names ("a sibling `RM_JobGiver_ColumnWander`... No new C#
  class is needed to prove this seam; it already compiles as
  `RM_CompTerritorialAnchor`'s own JobGivers"). Two seams constrain
  destinations, not one: `GetWanderRoot` picks the nearest column cell to
  wander around, and a `wanderDestValidator` (a real `JobGiver_Wander`
  field) rejects any candidate destination that is neither in a column nor
  within the pawn's own `forageRadiusBeyondColumns` of one — this is what
  actually keeps a column-bound species off the open ash even when
  `RCellFinder.RandomWanderDestFor` rolls a candidate outside the column
  proper, not just the root. `wanderRadius` itself is left untouched
  (protected, JobGiver_Wander's own field) so a concrete kind's
  ThinkTreeDef XML can set it directly per the vanilla idiom stock animal
  wander JobGivers already use — deliberately not hardcoded in the
  constructor the way `RM_JobGiver_AnchorWander` does, since that class
  serves one anchored-creature family and this one is meant for every
  future sky kind.
- **Ground-hazard immunity** — `RM_GameCondition_WeatherPulse.
  DoScaldDamageOnMap` (F1) gets one added exemption check reading
  `RM_CompVaporDrifter.Props.groundHazardImmune` (default true) alongside
  its existing `onlyUnroofed`/`HazardTargeting.Affects` checks — not a fork
  of the damage shape, the one line this task's own brief pointed at
  ("add the exemption check there... don't fork the damage logic"). F1's
  own file is otherwise untouched.

**Float-draw-offset decision: SKIPPED, per the spec's own already-resolved
line.** forge_kit_spec.md F3 was RESOLVED at the spike pass, before this
build pass started: "No float-draw offset of its own is needed: the
Aerofleet float route is CONFIRMED class-side... so any sky kind wearing
VEF's own `CompProperties_Floating` already floats without this comp
touching draw code at all." This build pass re-verified the claim directly
against the live install rather than trusting the spike's citation
blind — read `Races_Aerofleet.xml` from both
`.../workshop/content/294100/1541721856/1.5/` and `.../1.6/` on the
owner's actual Steam install: the 1.5 copy carries plain
`AnimalBehaviours.CompProperties_Floating` (Alpha Animals' own
`AnimalBehaviours.dll`) but the **1.6** copy — the live, active version —
carries `VEF.AnimalBehaviours.CompProperties_Floating`, confirming the
spike's citation exactly. `RM_CompVaporDrifter` therefore ships no draw
code, exactly as the spec allows.

**Fireweed gap — flagged, not invented.** Checked this pass: no
`RUT_Fireweed`-family plant or item ThingDef exists anywhere in this repo
(`design/` mentions it as flora-roster intent in several worldbuilding
docs; `src/` has none). Per this task's own instruction, no fireweed def
was invented — the fleet-flier diet XML (fireweed in the food filter) is
**owed to the roster/biome flora pass**, same as every other kind's own
diet content. `CompProperties_VaporDrifter.forageRadiusBeyondColumns`
(INVENTED default 0, spec's own "12 beyond columns" figure for fleet
fliers) ships so that pass has the field ready to set once a fleet-flier
kind and its diet exist.

**Kind-attachment gap — flagged, PLACEHOLDER shipped, not invented.** No
Forge-specific flying PawnKindDef exists yet (expected — kinds are a
roster-pass job per every sibling kit's own scope discipline, same as F1's
flash-flora and F2's beldon). `RUT_VaporDrifter_AerofleetWiring.xml`
(`src/RimUtinni/UtinniPatches/Patches/`) patches
`CompProperties_VaporDrifter` onto the ALREADY-SHIPPED `AA_Aerofleet` — the
one sky-capable kind `RUT_TheForge.xml`'s own `<wildAnimals>` list already
carries (`MayRequire="sarg.alphaanimals"`, commonality 0.4) — via
`PatchOperationAdd` with `MayRequire="mandrake.rm.environmentalhazards"`
only (the xpath itself no-ops if Alpha Animals is absent; the class-missing
risk is the one that silently discards the whole parent def, per
`modextension-missing-type-discards-def`), never a hand-edit of the vendor
file. Validated live: `validate_patch.py` finds exactly 1 xpath match in
Alpha Animals' own `Races_Aerofleet.xml`. Clearly commented PLACEHOLDER —
whether the Forge's real sky fauna IS a renamed Aerofleet (the kit spec's
own XML-only ledger already lists "Aerofleet→Fumerider rename" as roster
work) is that pass's call, not this one's.

🔴 **What this ships short of full "constrains wander" behaviour, stated
plainly**: this patch attaches the DATA comp only (grants ground-hazard
immunity today, live). It does **not** wire `RM_JobGiver_ColumnWander` into
any ThinkTreeDef — `AA_Aerofleet` inherits vanilla's shared `Animal`
ThinkTreeDef (confirmed this pass, no `thinkTree` override in
`Races_Aerofleet.xml`), and splicing a wander-root override into that
shared tree is an authoring judgment call (every Aerofleet everywhere vs.
only a Forge-specific clone) the spec's own F3 resolution already deferred
to "the full build... not a further engine question" — exactly the same
deferral MIASMA_MECHANICS_1's M6 spike made for `RM_JobGiver_AnchorWander`,
which also still has no live ThinkTreeDef wiring. So today: AA_Aerofleet on
a Forge map is immune to scald bursts, but does not yet wander preferentially
into columns. The JobGiver class compiles and is ready; wiring it is roster
work, named here rather than silently short.

**Validate**: `skills/rimworld-modding/scripts/validate_patch.py` on the
one new patch file against the live installed set (`--defs` Data + Mods +
Workshop root + `src/RimUtinni` + `src/RimMandrake` + `src/RimStarWars`,
99 active mods on the currently-live minimal list) — **0 errors**, 1
advisory warning (`PatchOperationAdd` not wrapped in
`PatchOperationConditional`/`PatchOperationFindMod` — the same accepted
posture as every sibling patch in this build, `MayRequire` is the real
guard).

**Build**: `RM_EnvironmentalHazards.csproj` rebuilds clean with 2 new
`<Compile>` entries (`RM_MapComponent_VaporColumns.cs`,
`RM_CompVaporDrifter.cs`) — **0 warnings, 0 errors**. (This shared
`.csproj` was edited by a concurrent FOUNDRY/BENCH agent between this
pass's read and write — re-read and re-applied against the live file,
same "whole staged index" discipline this repo's own history already
documents for F2/F5/F6.)

**Explicitly NOT done, per this task's own scope**: F4 (towers) —
untouched. `ModsConfig.xml` untouched. No bridge/game/quicktest run.
Fireweed diet content and the real Forge sky-kind roster/ThinkTreeDef
wiring are both owed to later passes, named above rather than invented.
Live verification of the column field's actual shape on a real Forge map,
the wander-constraint behaviour once ThinkTree wiring lands, and the
scald-immunity exemption are all owed to a live quicktest pass.

### files (F3 build pass)

- `src/RimMandrake/EnvironmentalHazards/Source/RM_MapComponent_VaporColumns.cs` (new, F3)
- `src/RimMandrake/EnvironmentalHazards/Source/RM_CompVaporDrifter.cs` (new, F3)
- `src/RimMandrake/EnvironmentalHazards/Source/RM_GameCondition_WeatherPulse.cs` (edit, F3: drifter ground-hazard-immunity exemption in `DoScaldDamageOnMap`)
- `src/RimMandrake/EnvironmentalHazards/Source/RM_EnvironmentalHazards.csproj` (2 new `<Compile>` entries)
- `src/RimMandrake/EnvironmentalHazards/Assemblies/RimMandrake.EnvironmentalHazards.dll` (rebuilt, 0 warnings/errors)
- `src/RimUtinni/UtinniPatches/Patches/RUT_VaporDrifter_AerofleetWiring.xml` (new, F3 — PLACEHOLDER wiring pattern)

## F4 build pass — 2026-09-14

Build order step 7, last (forge_kit_spec.md's own "Build order": F1/F2/F5/F6
already shipped; F3 landed concurrently this same day). Wires F4 "the
foundry tower dungeon shell" — single-floor towers only, per owner card 1
(RULED 2026-09-12: "one large deep floor per tower in v1. Portal-chained
multi-floor lands later only if a quicktest proves the seam clean" — no
bridge access this pass, so no chaining was attempted or designed, exactly
as ruled).

**The portal shell — nearly free, as the spec predicted.** `MapPortal`/
`PocketMapExit`/`pocketMapProperties` are entirely stock (verified
`Source/RimWorld/MapPortal.cs`, `MapPortalProperties.cs`,
`Source/Verse/PocketMapUtility.cs`, `Verse/PocketMapExit.cs:8` this pass);
the whole shape was already proven working precedent in this same repo —
`RimUtinni/LanternDeeps/Defs/ThingDefs_Buildings/RUT_LanternDeepMineshaft.xml`
/ `RUT_LanternDeepEmergence.xml` + `Defs/MapGeneration/
RUT_LanternDeepGenerator.xml` — read in full before writing anything, and
cribbed directly rather than re-derived. `RUT_FoundryTowerEntrance.xml`
(ThingDefs_Buildings/) is the door: `ParentName="BuildingBase"`,
`thingClass MapPortal`, `portal.pocketMapGenerator RUT_FoundryFloor`,
`portal.pocketMapSize 80`, `portal.exitDef CaveExit` — the exit is vanilla
`CaveExit` reused AS-IS, same "no new exit def, loosely-thematic borrowed
art" posture LanternDeeps' own two entrances already established. Owner
card 1 followed exactly: one deep floor, no chaining.

**The floor — `RUT_FoundryFloor` MapGeneratorDef**
(Defs/MapGeneration/RUT_FoundryFloor.xml), `pocketMapProperties.temperature
70` (INVENTED per spec, native field per `Source/Verse/
MapTemperature.cs:33-36`, no C#). `pocketMapProperties.biome` is
**`RUT_TheForge`, not vanilla `LavaField`** — a deliberate departure from
what a literal reading of the spec's own donor-biome list might suggest:
`LavaField.xml` lives under `Data/Odyssey/`, DLC-folder-gated (this item's
own spike-pass finding), so citing it here would make the whole floor
generator unable to resolve without Odyssey active. `RUT_TheForge` is this
mod's own always-shipped merged Forge biome (`BIOME_OWNERSHIP_WAVE_1`) —
carries no fragility, and ties the floor's base ground look back to the
Forge's own already-established terrain identity
(`AB_BlackPebbles`/`AB_HardenedGrass`, confirmed reading the raw def this
pass). "Open melt" itself does NOT come from this biome's own
`terrainPatchMakers` (it has none) — it comes from the new GenStep below,
painting vanilla `LavaDeep` explicitly.

**GenSteps, four new/reused per the spec's own "forge-works rooms, melt
channels, salvage caches, tender spawns" line:**

1. **Melt channels** — `RM_GenStep_TerrainChannels` (new C#, generic: a
   random-walk terrain painter — terrainDef + channel count/length/width,
   all XML-settable — not Forge-specific, reusable by any future kit
   wanting a scripted vein/crack/channel). Paints vanilla **`LavaDeep`**
   (searched this pass: no existing lava/melt TerrainDef anywhere in this
   repo's own RUT_/RM_ content — confirmed via RimSage `search_defs`
   before writing anything). LavaDeep, CONFIRMED via RimSage raw read this
   pass: `ParentName="LavaBase"`, `passability Impassable`, `dangerous
   true`, native `burnDamage`/`burnIntervalTicks`/
   `ignitePawnsIntervalTicks` fields read every tick by the stock
   `Verse/HediffGiver_Terrain.cs` — no C# of this mod's own involved,
   exactly the spike pass's own already-resolved finding 1 ("open melt as
   the wall... no C# needed for either behaviour"). LavaDeep chosen over
   the walkable `LavaShallow` specifically because it is Impassable — see
   the ban #1 mechanism below. `RUT_FoundryFloor_MeltChannels.xml`, order
   300 (after vanilla `Terrain` 210, before every later scatterer).
2. **Forge-works rooms** — vanilla `ScatterRuinsSimple` (order 750,
   unmodified, listed by defName only) stands in for authored room
   content: an honest SHELL-only substitution, not a new room-layout
   system — real forge-works room content is owed, named here rather than
   silently substituted.
3. **Salvage caches** — `RUT_FoundrySalvageCache` (new ThingDef, inert
   visible marker, no loot table — same "shell, not content" scope as
   every other placeholder this item has shipped) placed via the already-
   built `RM_GenStep_PlacedSetPieces` / `RM_SetPieceElement_SpawnMarker`
   (`RUT_FoundryFloor_SalvageCache.xml`, order 850, count 2 INVENTED).
4. **Tender spawns** — `RM_GenStep_PlacedSetPieces` /
   `RM_SetPieceElement_AnchoredPawn` (both already built, MIASMA_MECHANICS_1
   M6 — consumed, not rebuilt) spawning **`Mech_Pikeman`** (vanilla
   Biotech, unmodified) as the PLACEHOLDER tender kind
   (`RUT_FoundryFloor_TenderSpawn.xml`, order 860, count 3 INVENTED).
   Faction null (`RM_SetPieceElement_AnchoredPawn`'s own fixed shape) — the
   same accepted "wiring placeholder ahead of the roster pass" posture its
   own header already documents.

**Hard-ban #1 (nothing lives in the lava) — PASS, mechanism-checked.**
`GenStep_Scatterer.spotMustBeStandable` (`Verse/GenStep_Scatterer.cs`, read
in full this pass) defaults to **false** — NOT automatically enforced, a
finding worth stating plainly since an unchecked assumption here would have
been a silent ban violation. Set `<spotMustBeStandable>true</
spotMustBeStandable>` explicitly on both `RUT_FoundryFloor_SalvageCache.xml`
and `RUT_FoundryFloor_TenderSpawn.xml` (the tender one is the only
GenStepDef in this pass that places a PawnKindDef, so this field is
load-bearing there, not tidy) — combined with melt channels running first
(order 300, before 850/860) and LavaDeep's native `Impassable` always
failing `IntVec3.Standable`, no PawnKindDef this kit places can land on the
melt. Verified by mechanism, not merely asserted.

**Hard-ban #2 (lava-machines never revealed) — PASS, string-checked.** The
tender GenStepDef carries exactly one new field value,
`<pawnKind>Mech_Pikeman</pawnKind>` — a bare cross-reference to an
unmodified vanilla PawnKindDef, no new label/description/letter/quest
string written anywhere about it. `RUT_FoundryTowerEntrance.xml`'s and
`RUT_FoundrySalvageCache.xml`'s own flavor text ("whatever forged the tower
above is still forging, somewhere below"; "whoever — whatever — stacked it
here") were written deliberately vague, naming no mechanism or identity.
Grepped this pass's own new files for the tender/mechanoid content: no
other string touches them.

**Placement (outer map) — `RUT_FoundryTowerScatter.xml`.** Gated on
**`RUT_TheForge` only**, not the three donor defNames the spec names
(`Volcano`/`LavaField`/`AB_PyroclasticConflagration`) — this item's own
F2/F5/F6 build pass already found, and this pass rechecked directly against
`RUT_TheForge.xml`, that `BIOME_OWNERSHIP_WAVE_1` merged all three into one
owned BiomeDef; the donor defNames back no BiomeDef any map in this
campaign can actually generate with, so gating on them would gate on dead
references, not "the real biome defNames." New C# this pass:
`RM_ScattererValidator_Biome` (generic biome-membership gate, the exact
extension point `RM_GenStep_PlacedSetPieces.cs`'s own header invites — "each
kit writes its own ScattererValidator subclass"). **The spec's own "0-2
Volcano/LavaField vs 0-1 Pyroclastic" split collapses to one uniform count
(2, the higher figure, as a ceiling) for the whole biome** — stated
plainly, not silently dropped: `RUT_TheForge.xml`'s own header records the
three donor zones as an ELEVATION split (Volcano median 1,875m/LavaField
2,010m/Pyroclastic 1,382m, "all inside this ONE def now"), and this def
carries no elevation or TileMutatorDef signal to re-derive that split from
— the exact same situation F5's own edge-band ring (`RUT_ContagionRingScatter.xml`)
already hit and collapsed for, restated here rather than re-litigated.
Re-splitting by zone is owed to a future pass once a zone signal exists on
`RUT_TheForge`. Registered onto `Base_Player` via
`RUT_FoundryTowerScatter_Register.xml` (same `PatchOperationConditional`/
`PatchOperationAdd` shape as every sibling registration this item ships;
validator confirms the patch matches 1 site in `Core: BasePlayerMapGenerator.xml`).

**Build**: `RM_EnvironmentalHazards.csproj` rebuilds clean with 2 new
`<Compile>` entries (`RM_GenStep_TerrainChannels.cs`,
`RM_ScattererValidator_Biome.cs`) — **0 warnings, 0 errors**. (This shared
`.csproj` had three more entries land from a concurrent agent — `RM_GradientAxisRepaint.cs`
/ `RM_GradientSurgeExtension.cs` / `RM_GameCondition_GradientSurge.cs` —
between this pass's edit and its build; left untouched, this pass's own two
entries confirmed present and compiling.)

**Validate**: `skills/rimworld-modding/scripts/validate_patch.py` on all 8
new files against the live installed set (`--defs` Data + Mods + Workshop
root + `src/RimMandrake` + `src/RimUtinni`, 99 active mods on the
currently-live list) — **2 errors** (the two new visible ThingDefs'
placeholder texPaths, held below — the same accepted shape every prior
DEPLOY_HOLD in this item's own history), 0 warnings, several expected
pre-deploy "class not yet resolvable" info lines (assembly freshly rebuilt
in `src/`, not yet deployed to the live `Mods/` folder — deployment is
explicitly out of this task's scope). `RUT_FoundryTowerScatter_Register.xml`
confirmed its `Base_Player` xpath matches live.

**Art.** `RUT_FoundryTowerEntrance` and `RUT_FoundrySalvageCache` both
repointed to their own new RUT_-named texPaths and DEPLOY_HOLD'd
(`src/DEPLOY_HOLD.txt`) — same "validate_patch.py refuses a cross-mod
vanilla-art reuse as a hard ERROR" shape the F2/F5/F6 hold already
documents in full, not re-litigated here.

**Explicitly NOT done, per this item's own scope and owner card 1**:
multi-floor/portal-chaining (ruled out — no bridge access to prove the seam
clean, exactly as the ruling anticipated); real forge-works room content
(vanilla `ScatterRuinsSimple` stands in); real salvage loot content (marker
only); the real tender PawnKindDef/faction (roster/faction pass); tower
exterior art (explicitly not this kit's C#, per the spec's own line); F1-F3/
F5/F6 — untouched. `ModsConfig.xml` untouched. No bridge/game/quicktest run
— offline only. Live verification of channel density/legibility, the
salvage/tender site counts, and the outer-map tower placement rate are all
owed to a live quicktest pass.

### files (F4 build pass)

- `src/RimMandrake/EnvironmentalHazards/Source/RM_GenStep_TerrainChannels.cs` (new, F4)
- `src/RimMandrake/EnvironmentalHazards/Source/RM_ScattererValidator_Biome.cs` (new, F4)
- `src/RimMandrake/EnvironmentalHazards/Source/RM_EnvironmentalHazards.csproj` (2 new `<Compile>` entries)
- `src/RimMandrake/EnvironmentalHazards/Assemblies/RimMandrake.EnvironmentalHazards.dll` (rebuilt, 0 warnings/errors)
- `src/RimUtinni/UtinniPatches/Defs/ThingDefs_Buildings/RUT_FoundryTowerEntrance.xml` (new, F4)
- `src/RimUtinni/UtinniPatches/Defs/ThingDefs_Buildings/RUT_FoundrySalvageCache.xml` (new, F4)
- `src/RimUtinni/UtinniPatches/Defs/MapGeneration/RUT_FoundryFloor.xml` (new, F4)
- `src/RimUtinni/UtinniPatches/Defs/MapGeneration/RUT_FoundryFloor_MeltChannels.xml` (new, F4)
- `src/RimUtinni/UtinniPatches/Defs/MapGeneration/RUT_FoundryFloor_SalvageCache.xml` (new, F4)
- `src/RimUtinni/UtinniPatches/Defs/MapGeneration/RUT_FoundryFloor_TenderSpawn.xml` (new, F4)
- `src/RimUtinni/UtinniPatches/Defs/MapGeneration/RUT_FoundryTowerScatter.xml` (new, F4)
- `src/RimUtinni/UtinniPatches/Patches/RUT_FoundryTowerScatter_Register.xml` (new, F4)
- `src/DEPLOY_HOLD.txt` (edit — 2 new held entries)
