# VEE world layers: port plan (2026-10-22)

Owner ruling (card, 2026-10-22, already on `VEE_WORLD_MUTATORS_DECIDE_FOURTEEN_THOUSAND`; not to be asked again):
*"Port all to our own mod"* (solar, other features and landmarks), then drop `vanillaexpanded.vexploratione`
(Vanilla Exploration Expanded, "VEE"). This plan is offline only: it builds nothing and writes to no def or save.
Precedent and machinery: `design/RimMandrake/retired_mutators_port_2026-10-19.md` (the Alpha Biomes and SW Animal
Collection port of 2026-10-19: map JSON, `save_donor_rewrite.py --mutators-only`, the
`selftest_retired_mutator_ports.py` guard). This port follows the same pattern.

Items filed for this plan are listed in §7.

## 1. Inventory (measured)

**Instrument.** Measured with the `repaint_biomes.py` decode (`worldmap.WorldGrid` + `WorldObjects`). It reads
`Saves\ASHKARR_DEV_START_2026-10-20_PARITY_QUIET_R3.rws` (R3, the de facto dev start) against the def dump
`DefDump\captures\2026-10-21T11-18-41Z`. The save and the dump carry the same 325-mod set, sha16
`f1c87543b447bab6`. **Sanity probe:** the same instrument reproduces the big-repaint plan's §1c numbers exactly:
27,913 mutator entries (DONOR 14,413, vanilla/DLC 11,040, ours 2,460) and 3,008 landmarks (DONOR 805,
vanilla/DLC 2,101, ours 102). A second, independent check is a literal count of `<def>VEE_Cenotes</def>` in the
save text, which gives 339, the decoded count. Scratch scripts were used only to count; no tool was committed.

**VEE in the dump:** 141 TileMutatorDefs, 59 LandmarkDefs, 87 ThingDefs, 59 RulePackDefs, 51 TerrainDefs,
11 GenStepDefs, 9 GameConditionDefs, 8 PrefabDefs, 7 IncidentDefs, 6 HediffDefs, 5 ThoughtDefs, 2 WeatherDefs,
1 FleckDef and 1 ModDef. **The planet uses 58 mutator defs and 24 landmark defs.** The other 83 mutators and
35 landmarks are on no tile. Since there is no worldgen (CLAUDE.md), they are not ported: no tile can ever gain
one, so "port all" is read as "everything the frozen planet carries".

### 1a. Mutators on R3 (14,413 entries; every entry is on its own tile, so entries = tiles)

What each one does was read from its dump fields (`workerClass`, `modExtensions`, `extraGenSteps`, description).
Workers in `VanillaExplorationExpanded.*` are VEE C# and die when VEE is dropped. Workers in `VEF.Maps.*`
belong to Vanilla Expanded Framework, which **stays** (`01_mod_inventory.md`: "keep: our content hard-depends
on it"). Workers in `RimWorld.*` are vanilla.

| # | VEE def | tiles | mechanism (dump) | group |
|---|---|---:|---|---|
| 1 | `VEE_MoreSolarPower` | 4,362 | no worker. A VEE Harmony transpiler on `CompPowerPlantSolar.DesiredPowerOutput` (`MultiplySolarOutput`) applies ×1.25 | S |
| 2 | `VEE_LessSolarPower` | 3,900 | the same transpiler, ×0.75 | S |
| 3 | `VEE_DeepOreDevoid` | 1,534 | `TileMutatorExtension.deepOresMultiplier` 0 (VEE C#) | O |
| 4 | `VEE_MineralDevoid` | 1,533 | `VEE.TileMutatorWorker_MineralDevoid` (no mineable ore lumps) | O |
| 5 | `VEE_Cenotes` | 413 | GenSteps `VEE_Cenotes_Large`, `_Small` (water-filled sinkholes) | L |
| 6 | `VEE_SaltPlains` | 370 | `VEE…SaltPlains` (Lake category; salt terrain, sterile) | L |
| 7 | `VEE_Cactus_OrganPipe` | 214 | `VEF.Maps.TileMutatorWorker_PlantsWithCommonality` + VEE cactus plant | F |
| 8 | `VEE_Cactus_Beavertail` | 211 | same | F |
| 9 | `VEE_DryRiver` | 175 | `VEE…DryRiver` (River category; dry riverbed terrain) | L |
| 10 | `VEE_DeepOreRich` | 163 | `deepOresMultiplier` 1.25 | O |
| 11 | `VEE_FloodPlains` | 158 | `VEE…LargeRiverBanks`, `VEE_FertileRiverbank`, riverbank ×4 | L |
| 12 | `VEE_SulfuricLake` | 110 | `VEE…SulfuricLake` + GenStep `VEE_SulfurVents` | L |
| 13 | `VEE_StagnantRivulet` | 100 | `VEE…StagnantRivulet` | L |
| 14 | `VEE_MechanoidShipChunks` | 99 | GenStep `VEE_MechanoidShipChunks` (**the home tile 17011 carries it**) | F |
| 15 | `VEE_ToxicVents` | 91 | `VEF…GenericPrefabSpawner`, `VEE_ToxicVent_Prefab` ×6–12 | V |
| 16 | `VEE_RisingWaters` | 90 | vanilla `TileMutatorWorker_Coast` + VEE tide C# | L |
| 17 | `VEE_PlantLife_Overgrown` | 89 | no worker (plant density factor) | F |
| 18 | `VEE_Sinkholes` | 76 | GenStep `VEE_Sinkholes` | L |
| 19 | `VEE_Mycelium` | 70 | `VEF…PlantsWithCommonality` | F |
| 20 | `VEE_SerpentineCanyons` | 68 | `VEE…SerpentineCanyons` (mountain fissures) | L |
| 21 | `VEE_PoisonousFlora` | 61 | `VEE…PoisonousFlora` (harvest gives toxic buildup) | F |
| 22 | `VEE_DustBowl` | 42 | `VEE…DustBowl` | L |
| 23 | `VEE_RottenStench` | 34 | no worker; GameCondition, Hediff and Thought `VEE_RottenStench` | W |
| 24 | `VEE_JaggedRocks` | 34 | `VEE…JaggedRocks` (thin rock ridges) | L |
| 25 | `VEE_GravelBeach` | 32 | vanilla `TileMutatorWorker_Coast` + VEE terrain | L |
| 26 | `VEE_MeteorCrater` | 31 | `VEE…Crater` | L |
| 27 | `VEE_IncreasedInfestations` | 31 | no worker (VEE C#; `VEE_Infestation` incident) | W |
| 28 | `VEE_RockRidge` | 24 | `VEE…Ridge` | L |
| 29 | `VEE_QuicksandPits` | 22 | `VEE…QuicksandPits` | L |
| 30 | `VEE_MineableComponentSpacer` | 21 | `VEE…AdvancedComponentDeposits` | O |
| 31 | `VEE_PebbleDunes` | 19 | `VEE…PebbleDunes` | L |
| 32 | `VEE_Fertility_Reduced` | 18 | `VEE…RemoveFertileSoils` | F |
| 33 | `VEE_PlantLife_Decimated` | 17 | no worker (plant density factor) | F |
| 34 | `VEE_DustStorms` | 16 | vanilla `IncreaseWeatherFrequency` + WeatherDef `VEE_DustStorm` | W |
| 35 | `VEE_IncreasedDiseases` | 16 | `diseaseMTBMultiplier` 0.75 (VEE C#) | W |
| 36 | `VEE_RotstinkVents` | 16 | `VEF…GenericPrefabSpawner` | V |
| 37 | `VEE_MarineSanctuary` | 15 | `VEE…MarineSanctuary` (more coastal animals); placed on the Scald by `world/_scald/apply_scald_mutators.py` | F |
| 38 | `VEE_QuicksandDunes` | 14 | `VEE…QuicksandDunes` | L |
| 39 | `VEE_Sandstorms` | 12 | vanilla `IncreaseWeatherFrequency` | W |
| 40 | `VEE_DeepSnow` | 12 | `VEE…DeepSnow` | L |
| 41 | `VEE_DeadlifeVents` | 10 | `VEF…GenericPrefabSpawner`, `VEE_DeadlifeVent_Prefab` (raises the dead) | V, **owner** |
| 42 | `VEE_FleshPits` | 9 | `VEE…Fleshpits` + GenSteps | L |
| 43 | `VEE_RelictDelta` | 8 | `VEE…RelictDelta` | L |
| 44 | `VEE_RedDesert` | 8 | `VEE…RedDesert` | L |
| 45 | `VEE_RedDesertPlants` | 8 | `VEF…PlantsWithCommonality` | F |
| 46 | `VEE_NoTrees` | 8 | `VEE…RemoveTrees` | F |
| 47 | `VEE_Cactus_Barrel` | 7 | `VEF…PlantsWithCommonality` | F |
| 48 | `VEE_Cactus_Hedgehog` | 7 | same | F |
| 49 | `VEE_ContaminatedRiver` | 7 | `VEE…ContaminatedRiver`, `VEE_IrradiatedSoil`, `VEE_RadioactiveBarrel` | L |
| 50 | `VEE_AlluvialFan` | 7 | `VEE…AlluvialFan` | L |
| 51 | `VEE_SmokeVents` | 5 | `VEF…GenericPrefabSpawner` | V |
| 52 | `VEE_StoneForest` | 4 | `VEE…StoneForest` | L |
| 53 | `VEE_ContaminatedReservoir` | 4 | `VEE…ContaminatedReservoir` (100–200 `VEE_RadioactiveBarrel`) | L |
| 54 | `VEE_LoneIsland` | 3 | `VEE…LoneIsland` | L |
| 55 | `VEE_SulfuricRiver` | 2 | `VEE…SulfuricRiver`, `VEE_SaltySand` banks | L |
| 56 | `VEE_Volcano` | 1 | `VEE…Volcano` | L |
| 57 | `VEE_ResurgentCaldera` | 1 | `VEE…ResurgentCaldera` | L |
| 58 | `VEE_ToxicCrater` | 1 | `VEE…ToxicCrater` | L |

Groups: **S** solar (2 defs, 8,262 tiles) · **O** ore and resources (4 defs, 3,251) · **L** landforms and terrain
(30 defs, 1,845) · **F** flora and fauna (13 defs, 824) · **W** weather, conditions and incidents (5 defs, 109) ·
**V** vents (4 defs, 122; the Deadlife row needs the owner, §4b). Total 58 defs, 14,413 tiles.

### 1b. Landmarks on R3 (805)

`VEE_Cenotes` 339 · `VEE_DryRiver` 120 · `VEE_JaggedRocks` 111 · `VEE_GravelBeach` 31 · `VEE_SerpentineCanyons` 29 ·
`VEE_MeteorCrater` 25 · `VEE_SaltPlains` 22 · `VEE_PebbleDunes` 19 · `VEE_DustBowl` 18 · `VEE_StagnantRivulet` 18 ·
`VEE_QuicksandDunes` 14 · `VEE_RockRidge` 12 · `VEE_SulfuricLake` 10 · `VEE_FleshPits` 9 · `VEE_AlluvialFan` 5 ·
`VEE_CactusFields` 5 · `VEE_QuicksandPits` 4 · `VEE_StoneForest` 4 · `VEE_RelictDelta` 3 ·
`VEE_ContaminatedReservoir` 2 · `VEE_RedDesert` 2 · `VEE_CraterLake` 1 · `VEE_ResurgentCaldera` 1 ·
`VEE_ToxicCrater` 1. That is 24 defs. A landmark is a named world object: it carries a `<def>` and a stored
`<name>`, and its `mutatorChances` name the mutator it requires (for example, `VEE_DustBowl` requires
`VEE_DustBowl`, `VEE_PlantLife_Decimated`, `VEE_Fertility_Reduced` and `VEE_DustStorms`). Since there is no
worldgen, only the required mutator and the icon matter. The optional chances (Stockpile, AncientUplink and so
on) never roll again.

### 1c. Already ported, or ours already covers it (searched `src/` first)

- `VEE_QuicksandPits` (mutator 22, landmark 4) → **reuse `RM_QuicksandPits`** (EnvironmentalHazards, ported from
  `AB_QuicksandPits` on 2026-10-19: FlowWorks' `RM_DeepSand` pools). Same concept, so no new def.
- **Icons are ours already.** `src/RimUtinni/AshkarrLandmarkArt/Patches/LandmarkIcons.xml` patches Ash'karr icons
  onto 18 VEE landmark defs. The textures are at `Textures/World/Landmarks/Ashkarr/VEE_*.png` (18 files). The port
  keeps this art and only re-points the patch (§2).
- Vent buildings: EnvironmentalHazards already has 3 vent buildings and the vanilla vent layout from the 10-19 port.
  Toxic, Rotstink and Smoke vents follow that same pattern and reuse its C# where they can.
- Weather: `RSW_SW_Sandstorm` and `RSW_SW_DrySandstorm` exist in the Star Wars layer. Any dust or sandstorm weather
  of ours has to be found before `VEE_DustStorm` is cloned (step W1).
- 0 VEE cactus plant twins of ours were found. `RSW_CactusMeat`/`Hide` are animal products, not plants.

### 1d. VEE outside the tile layers (this affects §6, retirement)

- **R3 save text** holds 72 distinct `VEE_` names. Beyond the landmark `<def>`s these are:
  (i) **10 `VEE_DeadlifeVent` buildings** (`Class="VanillaExplorationExpanded.Building_DeadlifeVent"`) on a map
  inside the save. They are deleted on load once VEE is gone. Under the no-zombies ruling that loss is intended,
  but it needs a look (§4b).
  (ii) 36 VEE plant and food names in `foodRestrictionDatabase` `allowedDefs`, 6 each. These are harmless: the
  filter drops unknown defs.
- Map **terrain grids** may hold VEE TerrainDef shortHashes (`VEE_Salt`, `VEE_DryRiverBed` and others) on any map
  generated on a VEE tile. This is **UNMEASURED.** Before retirement, it is measured with `rimbench/savemap.py`
  against the matching dump.
- `src/`: `UtinniPatches/Patches/OasisMutator_DesertOasis.xml` names `VEE_Plant_DatePalm` (the one
  "unguarded name" in `01_mod_inventory.md`). `StarWarsPatches/Patches/PsychicToForceDisturbance.xml`'s
  `VEE_Psychic*` defs belong to **`vanillaexpanded.vee` (Vanilla Events Expanded), not this mod**; they are out of
  scope.
- World authoring scripts under `world/` (`audit_2026-08-26/plan.py`, `_scald/`, `_twilight/`, `_grey/`,
  `_mountain_plan*.py` and others) name VEE defs. They are history, not live inputs. If one is ever re-run it must
  use the map in §3. They are not edited.

## 2. Target mods and def mapping

All names are invented, not canon, so every port is in the **`RM_`** tier (CLAUDE.md naming tiers). Nothing routes
through Utinni except the existing Ash'karr icon patch and any RUT_ biome whitelist (the same rule as on
2026-10-19: RM_ defs name no RUT_/RSW_ def). Biome white/blacklists are **left empty**: with no worldgen they never
act, and the VEE lists name vanilla biomes the planet does not have. Each port keeps its `chanceOnNonLandmarkTile`
at **0**, which closes the worldgen door.

| group | home | why there |
|---|---|---|
| S solar | **`SolarMirrors`** (`mandrake.rm.solarmirrors`, `RimMandrake.SolarMirrors`) | the mod that already reasons about sunlight on panels, and already reads `RM_MapComponent_PinnedSun` |
| O ores | **`DeepDrill`** (`mandrake.rm.deepdrill`) | deep-resource yield is its subject |
| L, F, W, V | **new mod `TileFeatures`**: folder `src/RimMandrake/TileFeatures`, packageId `mandrake.rm.tilefeatures`, namespace `RimMandrake.TileFeatures`, name "RimMandrake: Tile Features" | ~50 defs and ~25 map-shaping workers is too much to add to EnvironmentalHazards ("Hazards Kit"). Depends on VEF (kept), Harmony, FlowWorks (terrains and liquids) and EnvironmentalHazards (vent C#) |
| landmarks | `TileFeatures` (with its mutators); `RM_QuicksandPits` stays in EnvironmentalHazards | |

**defName scheme:** `VEE_<Stem>` → `RM_<Stem>` with the same stem (`VEE_Cenotes` → `RM_Cenotes`;
`VEE_Cactus_OrganPipe` → `RM_Cactus_OrganPipe`), except for:
- solar: `VEE_MoreSolarPower` → **`RM_StrongInsolation`** and `VEE_LessSolarPower` → **`RM_Sunless`**. These are
  derived labels (§4);
- `VEE_QuicksandPits` → `RM_QuicksandPits` (existing);
- `VEE_DeadlifeVents` → `RM_DeadlifeVents` **or dropped** (§4b).

Before any `RM_<Stem>` is created, the build step checks the name for collisions: RimSage/the def dump
and a `src/` grep. Supporting defs follow the same rule, created only where nothing of ours fits: terrains
(`RM_Salt`, `RM_SaltySand`, `RM_DryRiverBed`, `RM_DryRiverBank`, `RM_FertileRiverbank`, `RM_IrradiatedSoil`;
FlowWorks is checked first for salt and brine terrains), plants (four cacti, mycelium kinds, red-desert plants),
things (`RM_RadioactiveBarrel`, vent buildings, `RM_MineableComponentsSpacer`), GenSteps, prefabs, weather
(`RM_DustStorm` only if no storm of ours fits), conditions, hediffs and thoughts (`RM_RottenStench`).
Landmark namer RulePacks are **not** ported. Each of the 805 landmarks already stores its `<name>`, and with no
worldgen no new landmark is ever named. The port's LandmarkDefs fall back to a vanilla namer.

**How each group is rebuilt** (from fields, descriptions and vanilla workers read with RimSage; as on 10-19,
no VEE C# is read or copied):
- **S**: see §4.
- **O**: one `RM_TileResourceExtension` (`deepOreFactor`) read by a Harmony postfix on vanilla deep-resource
  generation (the exact method is located with RimSage at build). `RM_MineralDevoid` is a worker that removes
  mineable ore after generation. `RM_MineableComponentSpacer` is a vanilla `GenStep_ScatterLumpsMineable` with a
  spacer-component mineable.
- **F**: cacti, mycelium and red-desert plants use the VEF `PlantsWithCommonality` worker, pointed at our plants.
  Plant life overgrown and decimated use vanilla `plantDensityFactor`. `RM_NoTrees`, `RM_Fertility_Reduced` and
  `RM_PoisonousFlora` (a harvest hediff, crops exempt) are small workers. `RM_MechanoidShipChunks` is vanilla
  `GenStep_ScatterThings` with ship-chunk things. `RM_MarineSanctuary` uses vanilla's animal-density extension
  where it can, and a worker if it cannot.
- **W**: `RM_Sandstorms` and `RM_DustStorms` use vanilla `TileMutatorWorker_IncreaseWeatherFrequency`. An RSW
  weather is added from the Star Wars layer by patch, never named in RM_. `RM_RottenStench` is a permanent
  condition with a thought. `RM_IncreasedDiseases` is a disease-MTB factor and `RM_IncreasedInfestations` is an
  infestation-MTB factor, both small Harmony postfixes.
- **V**: the VEF `GenericPrefabSpawner` with our prefab and vent building, each vent using our gas (EnvironmentalHazards
  `CompActiveGasEmitter`, which already exists).
- **L**: new workers in `TileFeatures`, one per row. Ridges, craters, canyons, rivers, lakes, sinkholes and cenotes
  share a small toolkit (flood-fill pits, ring walls, carving lines). The big ones by tiles come first: Cenotes 413,
  SaltPlains 370, DryRiver 175, FloodPlains 158 and SulfuricLake 110 together cover 1,226 of the 1,845 L tiles.
- **Landmarks**: 23 new `RM_` LandmarkDefs, each requiring its ported mutator, plus `RM_QuicksandPits`.
  `LandmarkIcons.xml` is re-pointed from `VEE_*` defNames to `RM_*` and the icon textures keep their files.
  Renaming the PNGs is optional and is done only with `art install`.

## 3. Re-pointing the world's existing entries

The live planet is R3 (the dev save). Its mutators are 2-byte shortHashes, assigned at load by sorting every
TileMutatorDef by defName (`Verse.ShortHashGiver`). Two routes exist. Only the first is planned.

1. **The map file, then one stamp (planned).** Write `design/RimMandrake/vee_port_map.json` in the same shape as
   `retired_mutators_port_map.json`: `{"TileMutatorDef": {"VEE_x": {"new": "RM_x"}}, "LandmarkDef": {...}}`, with
   `drop: true` for anything the owner cuts. Then:
   - **Offline:** extend `save_donor_rewrite.py --mutators-only` to take `--map <json>` (it reads the 10-19 map
     today). Run it on a **copy** of R3 to prove the rename: entry counts kept, each port carries exactly its
     donor's tile set, every other byte identical, and a shortHash simulation over a capture that includes the
     ports. This proves the rename; it does not swap the save (owner 2026-08-18/19: no save writes).
   - **The one stamp, live, at the end:** the planet is painted once (`BIOME_PAINT_ONCE_AT_THE_END_1`, carried by
     `BIG_REPAINT_FINISH_ONCE_AND_FOR_ALL`). The ported mutators are written by bridge in
     the same sitting as the biome stamp. `jawa/world_mutators_set` takes one def list and one tile list per call,
     and is followed by exactly one `jawa/world_commit` (trap: `world/_scald/apply_scald_mutators.py` header).
     The tile lists come from the map plus a fresh `jawa/world_mutators_get` / the census, never from an old CSV.
     Landmark `<def>`s are re-pointed by bridge or by the same rewrite. **Order:** add each `RM_` mutator to its
     tiles while VEE is still loaded, verify, then remove the `VEE_` one. The tile is never left bare.
     ⚠️ `AddMutator` silently displaces a mutator in the same category. Each port keeps the VEE category set so
     the displacement is like-for-like, and verification checks "carries the RM_ port", not "kept the old set".
2. **"Replicate the unguarded names" (alias; rejected for the world layers).** Shipping defs that keep the `VEE_`
   defName would make the save load unchanged. But it puts a donor prefix into our shipping names (against the
   three-tier naming rule) and leaves the debt in place. It is used only for the one `src/` reference,
   `VEE_Plant_DatePalm` in `OasisMutator_DesertOasis.xml`. That reference is re-pointed to our own date palm, or
   to `Plant_TreePalm` if none exists, when F is built.

## 4. Solar power under One Direct Sun

**Finding: the 8,262 solar entries are already a function of geometry, not of biome-specific sun, except for one
biome exclusion.** They were painted by `world/audit_2026-08-26/plan.py` (section "A. SOLAR"):
`VEE_MoreSolarPower` on every tile within arc ≤ 55° of the substellar point, `VEE_LessSolarPower` on every tile at
arc ≥ 125°, and the terminator belt left bare. Measured on R3 against engine lat/long (`world/world_tiles_sub7b.csv`,
`world_physics_audit.arc_deg`): More covers sun elevation 34.96°…89.22°, all 4,362 on the day side. Less covers
−89.22°…−34.96°, all 3,900 on the night side. 0 tiles carry both. Of the 4,674 tiles at elevation ≥ 34.95° (4,664 at ≥ 35° exactly), the
unmarked ones are `RM_TheScald` 312 and `RM_Stillsand` 4. Of the 4,674 at ≤ −34.95°, the unmarked ones are
`RUT_Umbra` 662, `RM_BlueDesert` 89, `RM_TheChill` 18, `RM_NightsideIce` 6 and `RM_TheRot` 3. Those gaps come from
the script's biome blacklist (`Glowforest`, `AB_RockyCrags`, water), which is the only biome-specific part.

**What the game already does (RimSage, `RimWorld.CompPowerPlantSolar`):** output =
`Lerp(0, full, map.skyManager.CurSkyGlow) × unroofed fraction`. Our `RM_TidalSunGlowPatch` makes that glow a pure
function of sun elevation e: `0.6 + 0.4·min(1, sin e / sin 30°)` for e > 0, a 12° dusk band, and 0 beyond it.
Solar output therefore already follows geometry. VEE's ×0.75 on the night side multiplies a zero and does nothing.
VEE's ×1.25 on the day side is the only effect left.

**Resolution (within his ruling; no question for the owner):**
- **The effect moves out of the tile and into geometry.** SolarMirrors gets a Harmony postfix on
  `CompPowerPlantSolar.DesiredPowerOutput` that multiplies by `InsolationFactor(e)`, where `e` is the map's
  geometric sun elevation from `RM_MapComponent_PinnedSun.SunGeometry`. It uses the single `[0°, 90°]` clamp of
  `unified_direct_sun_heat_2026-10-19.md`, not a per-biome min/max. The proposed formula is
  `InsolationFactor = 1 + 0.25 · smoothstep(20°, 35°, e)`: 1.00 at low sun, 1.25 from 35° up. That reproduces
  VEE's ×1.25 on every tile it marked, and the smooth ramp avoids a seam at the old 55° arc. The code never reads
  a mutator, a biome or a per-tile number. Low sun is weaker and high sun is stronger, as his ruling says.
- **The mutators survive as derived labels**, so "port all" holds and the world-map inspector still says
  something. `RM_StrongInsolation` ("strong sun: solar panels at full strength", where e ≥ 35°) and `RM_Sunless`
  ("the sun never rises here", where e ≤ −35°) have no worker and no extension. At the stamp they are painted from
  the same geometry, **with no biome exclusions**: 4,664 + 4,664 tiles at exactly ±35° (`Utils/remake/solar_insolation.py`), including the 316 and 778 that the old
  blacklist skipped. A selftest proves that label = f(e) on every tile, so the label cannot drift from the effect.
- Mod Settings (SolarMirrors): "Solar output follows sun height" (on/off, default on) and "high-sun bonus"
  (0–50%, default 25%). With the setting off, panels run at vanilla glow-only output and the labels remain
  descriptive text.
- On a day/night world (not ours, and not our deliverable) e is the live sun height, so the same function still
  holds.

### 4b. Owner question: Deadlife vents (the only conflict found)

`VEE_DeadlifeVents` (10 tiles; 10 `VEE_DeadlifeVent` buildings saved on a map in R3) breathes the dust that raises
the dead. His 2026-10-19 ruling, *"No death pall, freezing vents are ok. We don't have zombies in Utinni."*, dropped
the equivalent `AB_AncientDeathPallVent`. His 2026-10-22 card said "port all". **Options:** (a) drop it, as with
the death pall: strip the 10 tiles and let the 10 buildings die on load (recommended, following the precedent);
(b) port it as `RM_DeadlifeVents`; (c) port it as a harmless gas vent (smoke or rot). This has not been decided
here. Item `VEE_DEADLIFE_VENTS_ASK_ZOMBIES_AGAIN` (needs owner).

## 5. Order of work, acceptance, risks, Mod Settings, first script

**Order** (each step is an item, §7):
1. **S** `VEE_SOLAR_REWIRE_GEOMETRY_PAINTS_IT`: SolarMirrors postfix, 2 label defs, settings, selftest. Offline
   build, then deploy.
2. **O** `VEE_DEEP_ORES_MIGRATE_RICH_AND_POOR`: DeepDrill extension and 4 defs.
3. **F + W + V** `VEE_FLORA_VENTS_BUILD_XML_FIRST`: creates the `TileFeatures` mod with About, Settings and the
   first `validation.py`, and the mostly-XML ports (22 defs).
4. **L** `VEE_LANDFORMS_BUILD_CRATERS_AND_COMPANY`: the ~29 map-shaping workers plus terrains, largest tile count
   first.
5. **Landmarks** `VEE_LANDMARKS_MIGRATE_KEEP_THE_ICONS`: 23 LandmarkDefs, re-point `LandmarkIcons.xml`.
6. **Map + stamp** `VEE_WORLD_RENAME_ONE_STAMP_AT_END`: `vee_port_map.json`, `save_donor_rewrite.py --map`, the
   offline proof on a copy, then the live stamp inside the big repaint.
7. **Retire** `VEE_MOD_RETIRE_LAST_ONE_OUT` (§6).

**Acceptance, by validation level:**
- **L0 offline:** every row of `vee_port_map.json` has a port def in `src/` of the right element type (extend
  `selftest_retired_mutator_ports.py` to read both maps). No def or patch of ours names a `VEE_` world def, with a
  planted negative to prove the scan can see. `validate_patch.py --defs` is clean. The solar selftest proves the
  label equals f(e) on all 21,872 tiles against an independent arc implementation, with a probe that the old
  paint's biome blacklist removes tiles on the same instrument (`selftest_solar_insolation.py`; R3's per-tile solar set is
  not in the repo, so the 4,362/3,900 split itself is re-checked only against the live census at the stamp). The landform workers' pure geometry has unit tests (`SelfTest/`).
- **L1 rename proof (offline, on a copy):** the rewrite keeps 27,913 entries minus the drops, each port carries
  exactly its donor's tile set, and other bytes are identical. The shortHash simulation reproduces every live hash
  of a capture made with the ports deployed.
- **L2 load:** after a deploy and a cold load (minimal list where possible, `rimworld-load-round`), 0 config
  errors, a fresh capture lists every `RM_` port, and the hashes match L1's prediction.
- **L3 live:** on throwaway quicktest maps (not the campaign), generate one map per port on a tile of the right
  kind, and capture the zoomed result. A judge agent compares each against the VEE description ("Nothing reaches
  the owner unread"). For solar, the state read `DesiredPowerOutput` on a panel at a high-sun and a low-sun tile
  matches f(e). After the stamp, `jawa/world_mutators_get` on sample tiles shows only `RM_` names.
- **L4 owner:** only §4b, and anything the judge cannot settle. Art for new plants and vents is delegated to the
  art judge (`delegation_policy.md`), never shown to him unread.

**Live risks:**
- The stamp displaces same-category mutators (`AddMutator`). Mitigation: keep the categories and verify by family.
- Hash drift: if any TileMutatorDef appears or disappears between the L1 simulation and the stamp, hashes move.
  Re-run L1 against the capture of the exact mod set that loads the stamp.
- Maps already generated keep VEE terrain and things in their grids. This is UNMEASURED (§1d) and is measured
  before §6.
- The home tile 17011 carries `VEE_MechanoidShipChunks` and `VEE_MoreSolarPower`. Its map already exists, so the
  port changes only its label and the solar factor. Nothing on the home map is regenerated.
- Load cost: a cold load on the full list is ~15 min. Batch L2 with other deploys.

**Mod Settings** (every mod, owner 2026-09-12): SolarMirrors gets the two switches in §4. TileFeatures gets one
toggle per group (landforms, flora, vents, weather and conditions, disease/infestation factors) and the
numbers that matter (disease and infestation factors, vent count). DeepDrill gets the ore factors. Defaults are
the shipped behaviour, everything off degrades to plain maps, and nothing affects worldgen (there is none).

**First validation script:** `src/RimMandrake/TileFeatures/validation.py`, written with the mod (owner,
2026-10-01: every mod ships with its first script). It runs the L0 checks offline and, given the bridge, the L3
quicktest per port. The solar check goes into SolarMirrors' existing `validation.py`.

## 6. Retirement of `vanillaexpanded.vexploratione`

It can leave the load list only when **all** of the following are proven, in this order:
1. L0–L2 pass for every port, so the ports load beside VEE without collision.
2. The stamp (§3) is done and verified: a fresh census of the live world shows **0** `VEE_` mutators and **0**
   `VEE_` landmarks. The instrument is proven by the sanity probe in §1, and the count is re-run on the post-stamp
   save.
3. Saved maps are measured with `savemap.py` for VEE terrain and thing hashes (§1d). Every hit is either renamed
   by `save_donor_rewrite.py` (terrain to its `RM_` twin) or accepted as a known loss (the 10 Deadlife vents, if
   §4b is (a)).
4. `src/` names no `vanillaexpanded.vexploratione` def: the DatePalm reference is gone, and
   `LandmarkIcons.xml` and its loadFolders/About entries are cleaned. `01_mod_inventory.md`'s row is updated.
5. A load with VEE removed from a **copy** of the list (`modlist_swap.py`; `modcheck run` rewrites the live
   ModsConfig, so not that) shows 0 errors naming VEE and 0 `Could not load reference` lines for `VEE_` defs.
   This is followed by one owner-free walk of the dev save.
Only then is VEE taken out of the live ModsConfig, and it is taken out together with the next planned load.

## 7. Items filed

| item | what | needs |
|---|---|---|
| `VEE_SOLAR_REWIRE_GEOMETRY_PAINTS_IT` | §4: SolarMirrors insolation factor, 2 label defs, settings, selftest | offline |
| `VEE_DEEP_ORES_MIGRATE_RICH_AND_POOR` | group O, DeepDrill | offline |
| `VEE_FLORA_VENTS_BUILD_XML_FIRST` | new mod TileFeatures + groups F, W, V + first validation.py | offline |
| `VEE_LANDFORMS_BUILD_CRATERS_AND_COMPANY` | group L, the map-shaping workers and terrains | offline |
| `VEE_LANDMARKS_MIGRATE_KEEP_THE_ICONS` | 23 LandmarkDefs + icon patch re-point | offline |
| `VEE_WORLD_RENAME_ONE_STAMP_AT_END` | the map JSON, rewrite tool `--map`, L1 proof, the live stamp | bridge |
| `VEE_DEADLIFE_VENTS_ASK_ZOMBIES_AGAIN` | §4b | owner |
| `VEE_MOD_RETIRE_LAST_ONE_OUT` | §6 | game-up |

All are caused by `VEE_WORLD_MUTATORS_DECIDE_FOURTEEN_THOUSAND`, which is closed by this plan, since the decision is
recorded.
