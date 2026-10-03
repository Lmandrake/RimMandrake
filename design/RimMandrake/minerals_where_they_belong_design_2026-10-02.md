# MINERALS_WHERE_THEY_BELONG_1 — design (2026-10-02, BENCH design helper, DRAFT for the owner to rule on)

Item: `MINERALS_WHERE_THEY_BELONG_1`. Census it rests on: `design/RimMandrake/minerals_census_2026-09-25.md`
(re-measured below; parts of it are stale). Design only: nothing here is built or filed.

## 1. What exists (measured)

Instruments: `measure` over the live def dump (`defs.sqlite`, captured 2026-09-26T01:08Z, 628 mods,
fingerprint `78163f2e60414f28`; `MEASURED 25115 ThingDef`), parsed in python (sanity probe:
`MineableGold` and `Steel`-as-deep-resource both found). Mod presence is parsed from
`infrastructure/state/modlists/ModsConfig.FULL.LATEST.xml` (610 active, 2026-10-02 07:33). The live
`ModsConfig.xml` currently holds a 9-mod test list, so it says nothing about what ships.

### 1a. The census of 2026-09-25 is partly stale

- ⛔ **Armoury is no longer "ported, not deployed".** `mandrake.rsw.armoury` is active in
  `ModsConfig.FULL.LATEST.xml`, and the dump attributes the KotOR ores to mod name
  `Jawa Armoury Rebalance`. So the KotOR mineables (Beskar, Cortosis, Rhydonium, Bronzium,
  Durasteel slag, Spice) **ship from our own mod today**, scattering on every rocky map.
- The census missed our own mineables entirely (1c below) and the global-scatter rows (1b).

### 1b. What scatters into EVERY rocky map today (the "random outcrop" problem)

Engine fact (RimSage, decompiled 1.6): `GenStep_RocksFromGrid.Generate` builds a
`GenStep_ScatterLumpsMineable` with no forced def, and `ChooseThingDef()` picks
`DefDatabase<ThingDef>.AllDefs.RandomElementByWeight(building.mineableScatterCommonality)`
(excluding only things worth more than `maxMineableValue`). **There is no biome filter anywhere
in that path.** Every def with a nonzero `mineableScatterCommonality` competes on every rocky map
on the planet.

Defs with `mineableScatterCommonality > 0` in the dump (25 rows, `GravTide_CrossableRock_*` clones
are not in this list — they carry 0):

| def | mod | yields | yield/cell | scatter weight |
|---|---|---|---|---|
| MineableSteel | Core | Steel | 40 | 1.0 |
| MineableComponentsIndustrial | Core | ComponentIndustrial | 2 | **1.0** |
| MineableUranium | Core | Uranium | 40 | 0.12 |
| MineableSilver | Core | Silver | 40 | 0.10 |
| MineableGold | Core | Gold | 40 | 0.07 |
| MineableJade | Core | Jade | 40 | 0.065 |
| MineablePlasteel | Core | **Plasteel** | 40 | 0.05 |
| KOTOR_MineableDurasteel | Armoury (ours) | KotORChunk_durasteel | 2 | 0.15 |
| KOTOR_MineableBronzium | Armoury (ours) | KOTOR_AlloyBronzium | 40 | 0.10 |
| KOTOR_MineableRhydonium | Armoury (ours) | KOTOR_RawRhydonium | 20 | 0.0875 |
| KOTOR_MineableCortosis | Armoury (ours) | KOTOR_IngotCortosis | 20 | 0.065 |
| KOTOR_MineableSpice | Armoury (ours) | KOTOR_Spice | 40 | 0.05 |
| KOTOR_MineableBeskar | Armoury (ours) | KOTOR_RawBeskar | 40 | 0.001 |
| LKDurasteel_Ore | leutiankane.mineablesor | OuterRim_Durasteel | 40 | 0.5 |
| LKBeskar_Ore | leutiankane.mineablesor | OuterRim_Beskar | 20 | 0.3 |
| LKPureBeskar_Ore | leutiankane.mineablesor | OuterRim_PureBeskar | 10 | 0.3 |
| LKORComponent_Ore | leutiankane.mineablesor | OuterRim_ComponentHypertech | 5 | 0.3 |
| MineableDiamond / Ruby / Sapphire | kikohi.jewelry | gems | 20 | 0.06 / 0.08 / 0.08 |
| BMT_MineableAmber / BMT_MineableFossils | biomesteam.biomesfossils | amber, fossils | 20 | 0.12 / 0.09 |
| GLO_MineableGlowstone | zav.glowstoneforked | glowstone cluster | 3 | 0.5 |
| DA_MineableSteelBeetle | Dark Ages (in the 09-26 dump; not found in LATEST list by package id — UNMEASURED whether active) | Steel | 40 | 0.3 |
| **RUT_Webwork_SilkKnot** | RimUtinni: Shokkweave Economy (ours) | **Hyperweave** | 4 | **0.6** |

Read it as shares (weights from the dump, summed in python: total 6.09): on an ordinary rocky map
about **1 lump in 5 is components** (Core industrial + Outer Rim hypertech, 21%), **about 1 in 3 is
a Star Wars metal** (Beskar / Durasteel / Cortosis / Rhydonium / Bronzium / Spice, 30%), about 1 in 10
is a knotted-silk vein yielding Hyperweave (10%), and plasteel is under 1%. The number of lumps per
map comes from `GetResourceBlotchesPer10KCellsForMap` and is not measured here.

🔴 **Two of these are our own leaks, same class as the kyber/pyrinth leak already fixed**
(`src/RimUtinni/UtinniPatches/Patches/RUT_LanternDeepGateKyber.xml`,
`src/RimMandrake/LanternDeeps/Patches/RM_LanternDeepGatePyrinth.xml` — both zero the global weight
and re-scatter inside the Lantern Deeps generator): `RUT_Webwork_SilkKnot` (a Webwork material) at
0.6 and the whole Armoury KotOR ore set.

Deep resources (ground-penetrating scanner) — engine fact: `CompDeepScanner.ChooseLumpThingDef()`
is `DefDatabase<ThingDef>.AllDefs.RandomElementByWeight(deepCommonality)`; deep lumps are created
**at scan time, not at map generation**, and again with **no biome filter** (only `hasBedrock`
gates the scanner). 26 defs carry `deepCommonality > 0` in the dump: Core Steel 4, Plasteel 1,
Uranium 1, Gold/Silver/Jade 0.5; KOTOR_Tibanna 2, OuterRim_Tibanna 2, KOTOR_RawRhydonium 1,
KOTOR_IngotCortosis 0.75, OuterRim_Beskar/PureBeskar/Durasteel 0.75 each; RSW_ResourceBlueCrystal 1;
RUT_Lanternstone 1 (src: `RM_Lanternstone` also 1); Gravitonium 0.4; DV_Pyrinth 0.4; jewelry gems
0.4–0.5; amber 0.4, fossils 0.8; VCHE_Deepchem 2; VHGE_Helixien 1; VCE_Salt 0.5; Glowstone 0.1.
In src (not in the 09-26 dump): `RUT_LivePatternMetal` deep 4 (`src/RimMandrake/RustCathedral`).
So **a drill anywhere on the planet can strike beskar, lanternstone or live pattern metal.**

### 1c. Our own mineral-ish content (parse of `src/**/Defs`, 3394 defs scanned)

Already in a non-vein form (these are the precedents the design builds on):

| form already used | defs | where |
|---|---|---|
| organism-produced bed (mine the colony) | `RM_BrineDeposit_{BrinePlate,Drazz,Tekk}` (+ `RUT_` twins) | `src/RimMandrake/Wasteland` |
| carcass seam | `RM_MiddenshellSeam`, `RM_MiddenshellVitrifiedSeam` → bezoars | `src/RimMandrake/Wasteland` |
| giant crystal formation | `RM_GreatSaltCrystal_{Amber,Pink,Violet,White}`, `RM_SaltDome`, `RM_SaltPillar`, `RM_BrineJacket` | `src/RimMandrake/TerminalBiomes` |
| fossil seam (stratum wall) | `RM_FossilSeam_{Impression,Skeleton,Unique}` | `src/RimMandrake/FloodedCanyon` |
| mineable wood blob | `RUT_GreatboleHeartwood`, `RUT_FeverTrunkHeartwood` | `src/RimUtinni/UtinniPatches` |
| biome rock wall | `RM_LanternstoneWall`, `RM_BlueIceMineable` | LanternDeeps, BlueDesert |
| salvage seam (ruin metal) | `RUT_MineableDeadSmartsteel`, `RUT_CathedralDeckPlate` (→ Steel) | `src/RimMandrake/RustCathedral` |
| hand-scraped crust / precipitate | `RM_SeepSalt`, `RM_SeepStone`, `RM_GlowerCrust`, `RM_DeltaSalt` | WeepingStones, Scarlands, Miasma |
| sieve / sand product | `RM_FineSand`, `RM_GlassSand`, `RM_BiosilicaGrit`, `RM_GlassPearl` + recipes `RM_MeltLensGlass`, `RM_MeltSunGlass` | `src/RimMandrake/Stillsand` |
| creature-produced item | `RM_ContaminantBezoar`, `RUT_MetalSaltBezoar`, `RM_CrestPlate` | Wasteland, UtinniPatches, Stillsand |
| world-site salvage | TileMutators `RSW_CrashedShip`, `RSW_DeadCrawler`, `RSW_MiningSite`, `RUT_GlassSea`, `RUT_Kiln` | StructureInjections* |
| heat-formed glass | `RM_FE_Fulgurite` | Pyrelands |

Our biomes: 28 `RM_` BiomeDefs (parse of `src/**`), each with a `RUT_` twin plus RUT-only biomes
(arid shrubland, desert, extreme desert, fuel snows, Umbra).

### 1d. Engine mechanisms available (RimSage, decompiled 1.6)

- `GenStep_ScatterLumpsMineable.forcedDefToScatter` — a GenStep can scatter ONE named mineable;
  used by Core for Glaciers (`SolidIce`), Odyssey's `TileMutatorWorker_ObsidianDeposits`, asteroids
  and `GenStep_PreciousLump`. ⇒ per-biome veins need only a per-biome GenStep with this field set
  plus the def's global weight zeroed. No C# for veins.
- `TileMutatorWorker_MineralRich` (Odyssey) picks one `isResourceRock` mineable per tile by Perlin
  noise and honours `TileMutatorDef.resourceBlacklist`. ⚠️ It is **not** biome-aware either; every
  ore we keep must either be blacklisted on that mutator or accept it.
- `GenStep_PreciousLump` / `SitePartParams.preciousLumpResources` + `CompLongRangeMineralScanner`
  (player picks `targetMineable`) — the vanilla "custom location" route: a quest site holding one
  big lump. Its candidate list is the scanner's, independent of map scatter.
- `ThingSetMaker_Meteorite` draws from **all** non-smoothed `isResourceRock` mineables (cheap <5
  MV vs valuable ≥5 MV) — a meteorite can still drop Beskar unless that def stops being
  `isResourceRock` or is excluded.
- `CompDeepScanner` — deep lumps by global `deepCommonality`, scan-time, no biome gate (above).


## 2. Node-form vocabulary

The owner's typed ruling (item note, 2026-09-25): *"they shouldn't just be lying around the planet
in veins to mine from random outcroppings like Vanilla does it. Actually no significant ore should
other than things like iron."* And for the Scald floor (`design/RimMandrake/sea_dive_maps_spec.md`
:386): *"Ore is NODULES you simply gather — not rock walls to mine."*

Each form below names the engine mechanism that carries it and whether we already ship one. A form
with no shipped precedent costs C#; the rest are XML.

| # | form | what the player sees and does | engine mechanism (checked) | precedent we ship |
|---|---|---|---|---|
| F1 | **common vein** | ore streaks in ordinary rock walls, mined | vanilla global scatter (`mineableScatterCommonality`) — the ONLY form allowed planet-wide, and only for iron/steel and plain stone | `MineableSteel` |
| F2 | **biome vein** | a vein that occurs only in one biome's rock | zero the global weight; a per-biome `GenStepDef` with `GenStep_ScatterLumpsMineable.forcedDefToScatter` (Core uses it for Glaciers/obsidian) added through the BiomeDef/map generator. No C# | pyrinth and kyber gates in the Lantern Deeps generator |
| F3 | **nodule / loose lump** | lumps lying on the ground, picked up (haul/gather), no wall | a plain item scattered by `GenStep_ScatterThings`, or a 1×1 minable "boulder" building with tiny yield | Scald-floor spec (`RM_Nodule*`, unbuilt); Minerals Rock `RiverRock`/`BeachRock` |
| F4 | **crystal cluster / formation** | free-standing crystals on open ground, cut for a drop table | MineralsFramework `StaticMineral` (`allowedTerrains`, `allowedBiomes`, `randomlyDropResources`) or our own building + scatter | Minerals Sparkle crystals; `RM_GreatSaltCrystal_*` (Grey Sea) |
| F5 | **surface crust / precipitate** | a crust on rock, vent rim or pool edge, scraped | a harvestable plant-class or filth-like thing that regrows; or a mineable 1×1 with small yield | `RM_SeepSalt` (steamfrond vents), `RM_GlowerCrust`, `RM_BrineJacket` |
| F6 | **vent deposit** | mineral that grows back near a heat/steam source | F4/F5 thing placed by a vent's own scatter, with a regrowth MapComponent | Scald floor `noduleRegrowth` in `RM_MapComponent_SeaFloor` (spec'd); `RUT_ScaldVent` exists but yields nothing |
| F7 | **organism-produced** | a plant or creature makes it: second yield, shed, bezoar, butchery, colony bed | `RM_CompMetalYield` (plant second yield), butcher products, `CompSpawner`, mineable colony beds | Cauldron thornwood/martyr steel yield; Wasteland brine beds; bezoars |
| F8 | **sieve / sand** | sift loose ground material for a trickle of grains | carried tool + WorkGiver (C#, built) | `RM_SandSieve` → `RM_GlassSand`/`RM_FineSand` (Stillsand) |
| F9 | **strata / dig table** | dig a shaft, roll a stratum loot table | built C# dig | Sump `RUT_DigShaft` + `RUT_DigStratumTable`; Flooded Canyon fossil seams |
| F10 | **salvage** | strip wrecks, ruin walls, crashed ships for refined materials | mineable ruin walls, deconstructable wreck buildings, TileMutator sites, loot tables | `RUT_CathedralDeckPlate`, `RUT_MineableDeadSmartsteel`, `RSW_CrashedShip`/`RSW_DeadCrawler`/`RSW_MiningSite` mutators, Scald wrecks |
| F11 | **deep deposit** | found by ground-penetrating scanner, drilled | `deepCommonality` — ⚠️ global, chosen at scan time (`CompDeepScanner.ChooseLumpThingDef`). A biome-gated deep resource needs a Harmony postfix on that method (C#) | `RUT_LivePatternMetal` (deep 4, but leaks planet-wide today) |
| F12 | **custom location** | a quest/world site holding one rich lump or a mine | `GenStep_PreciousLump` + `SitePartParams.preciousLumpResources`; long-range mineral scanner quest; our structure-injection mutators | `RSW_MiningSite`; Lantern Deeps Rakatan kyber mines (promised) |
| F13 | **trader / faction** | bought, never found | trader stock gen | Bazaar (TheBazaar) |

Not a form: **meteorites**. `ThingSetMaker_Meteorite` draws from every non-smoothed
`isResourceRock` mineable on the planet, so any ore we confine to a biome must also leave that pool
(clear `isResourceRock`, or a small Harmony filter), or a meteor delivers it anywhere.


## 3. Per-biome allocation

**Status key.** BUILT means it ships in `src/` today. PROMISED means a biome doc already says it
(path given). PROPOSED is new in this design and goes to that biome's own sitting for ruling, the
same way multi-homed creatures do. ⛔ This table is not a sweep: nothing here overrules a sitting
that has already ruled. The biome-to-tile paint happens once, at the end, so this allocates by
BiomeDef and never by tile.

**Planet-wide (every rocky map), and nothing else:** plain stone, Steel common vein (F1),
Steel deep deposit (F11). That is the whole of "things like iron".

| biome | material | form | source / def | status |
|---|---|---|---|---|
| **Scald (sea floor)** | gold, silver | F3 nodule, zones 1–2 | `RM_NoduleGold`, `RM_NoduleSilver` | PROMISED, `sea_dive_maps_spec.md:517-518` |
| | uranium | F3 nodule, zone 2 | `RM_NoduleUranium` | PROMISED :519 |
| | Chimney Iron (smelts to steel only) | F3/F6 nodule at chimneys | `RM_ChimneyIronNodule` | PROMISED :520 |
| | Mother-of-Scaldpearl | F6 vent growth (plant-class, `growDays` ~20) | `RM_ScaldpearlGrowth` → `RM_Scaldpearl` | PROMISED :521 |
| | magnetite, uraninite | F4 crystal item | `RM_MagnetiteCrystal`, `RM_UraniniteCrystal` | PROMISED :522-523 |
| | seep-salt, pyrinth | F3 scatter | `RM_SeepSalt`, `DV_Pyrinth` | PROMISED :524-525 |
| | Rakatan hull shard | F10 wreck salvage | `RUT_RakatanHullShard` | PROMISED :570 |
| **Grey Sea (floor)** | coloured salts, coarse salt | F4 great salt crystals, pillars, domes; F5 chipped brine jacket | `RM_GreatSaltCrystal_*`, `RM_SaltPillar`, `RM_SaltDome`, `RM_BrineJacket` | BUILT `src/RimMandrake/TerminalBiomes` |
| **Lantern Deeps** | kyber | F2/F4 formations, Deeps generator only | `Force_CrystalFormation_*` | BUILT gate (`RUT_LanternDeepGateKyber.xml`) |
| | pyrinth | F2 biome vein | `DV_MineablePyrinth` | BUILT gate (`RM_LanternDeepGatePyrinth.xml`) |
| | lanternstone | biome rock wall + F11 deep | `RM_LanternstoneWall`, `RM_Lanternstone` | BUILT; deep leaks planet-wide (§4) |
| | gems: diamond, ruby, sapphire; rough gem | F4 crystal clusters (Minerals Sparkle `allowedBiomes`) + F2 vein | `MineableDiamond/Ruby/Sapphire`, `*Crystal` | PROPOSED — the cave is where crystals belong in the docs already |
| | glowstone | F4 cluster | `GLO_MineableGlowstone` | PROPOSED |
| | Rakatan kyber mine; mindstone | F12 custom location | none yet | PROMISED `the_lantern_deeps.md:157,168` |
| **Rust Cathedral** | steel | deck plate walls (free bulk) | `RUT_CathedralDeckPlate` | BUILT |
| | dead smartsteel | F10 salvage seam | `RUT_MineableDeadSmartsteel` | BUILT |
| | live pattern metal | F11 deep, this biome only | `RUT_LivePatternMetal` | BUILT; deep leaks planet-wide (§4) |
| | components (industrial, spacer) | F10 ruin salvage | loot on deconstruct | PROPOSED |
| **Cauldron** | steel | F7 tree second yield | `RM_CompMetalYield` on thornwood/martyr | BUILT |
| | vexxith | F7 shear from the vexxiss | working name | PROMISED (turn-4 ruling) |
| **The Forge** | obsidian | F2 biome vein | Odyssey `MineableObsidian` (a forced-def GenStep already exists in `TileMutatorWorker_ObsidianDeposits`) | PROPOSED; obsidian PROMISED `the_forge.md:140` |
| | components, plasteel/durasteel | F10 tower salvage | loot | PROMISED `the_forge.md:143,148` |
| | tibanna | F7 beldon herds ONLY | `RUT_TibannaGas` | RULED `the_forge.md:127` |
| **Flooded Canyon (Cracked Lands)** | fossils, amber | F9 stratum seams | `RM_FossilSeam_*`; donor `BMT_MineableAmber/Fossils` confined here | seams BUILT; amber PROPOSED |
| | jade | F2 biome vein in canyon walls | `MineableJade` | PROPOSED |
| **Wasteland (the Wastes)** | brine plate, drazz, tekk | F7 colony beds | `RM_BrineDeposit_*` | BUILT |
| | bezoars | F7 carcass seams | `RM_MiddenshellSeam`, `RM_MiddenshellVitrifiedSeam` | BUILT |
| | salt, glass | F5 basin crust | none | PROMISED `wasteland.md:246` |
| | uranium, components | F10 warcasket cores, war salvage | loot | PROPOSED (`wasteland.md:247-253` names the salvage) |
| **Warscar** | Beskar, durasteel, spacer components | F10/F12 sealed salvage trove, stripped fleet | loot table | PROPOSED; trove PROMISED `the_scarlands.md:190,233` |
| **Weeping Stones** | seep-salt | F5 crust off steamfrond vents (the only source) | `RM_SeepSalt` | BUILT |
| **Miasma** | delta salt | F5/F7 | `RM_DeltaSalt` | BUILT |
| **Stillsand** | glass sand, fine sand | F8 sieve | `RM_SandSieve` | BUILT |
| | fulgurite | heat-formed item | `RM_FE_Fulgurite` | BUILT |
| **Pyrelands** | fulgurite | lightning glass | `RM_FE_Fulgurite` | BUILT |
| **Blue Desert** | blue ice | biome wall | `RM_BlueIceMineable` | BUILT |
| | meteoritic metal (silver, gold, a little uranium) | F3 nodules + F10 wreckage at the ablation line | none | PROMISED `the_blue_desert.md:221,251`; metals PROPOSED |
| **Contagion** | gallium | F7 off Red Spore shells | none | PROMISED `the_contagion.md:210` |
| **Sump** | mixed (bones, sunken machines) | F9 dig strata | `RUT_DigShaft`, `RUT_DigStratumTable` | BUILT |
| | deepchem | F11 deep, this biome only | `VCHE_Deepchem` | PROPOSED (tar country) |
| **Propane Lake (the Chill)** | rime nodules (propane) | F7 plant | none | PROMISED `the_propane_lakes.md:47,140` |
| | helixien gas | F11 deep, this biome only | `VHGE_Helixien` | PROPOSED |
| | ⛔ kyber | — | — | RULED out `the_propane_lakes.md:141` |
| **Webwork** | hyperweave | F7 knotted silk vein, this biome only | `RUT_Webwork_SilkKnot` | BUILT; leaks planet-wide (§4) |
| **Greentide / Fever Wood** | hardwood, wood | mineable heartwood (not a mineral) | `RUT_GreatboleHeartwood`, `RUT_FeverTrunkHeartwood` | BUILT |
| **All other biomes** | steel, stone | F1 | Core | — |

**Advanced and canon materials have no natural home at all** (owner: *"SALVAGE (a major source of
advanced materials)"*; *"Beskar, Duranium, Doonium are almost certainly salvage-only"*):

| material | sources after this design |
|---|---|
| industrial components | F10 salvage (ruins, wrecks, Rust Cathedral, Forge towers), traders, crafting. Never mined |
| spacer / hypertech components | F10 at named wreck and trove sites, traders. Never mined |
| plasteel (see Q2 on its name) | F10 salvage, mech remains, traders. Never mined |
| Beskar (all three defs) | F10/F12 only: Warscar trove, crashed-ship mutator, Scald wrecks. Never mined, never deep |
| Durasteel (all three defs) | F10 salvage. Never mined |
| Cortosis, Rhydonium, Bronzium, KotOR spice (Armoury) | trader and salvage only until a biome sitting claims one. Not mined |
| tibanna (both donors' deep defs) | Forge beldons only (owner ruling); deep weight removed |
| `RSW_ResourceBlueCrystal`, `Gravitonium` (deep 1, 0.4) | UNMEASURED purpose; held as is, flagged to their own mods' next sitting |


## 4. What is removed from where

All of these are weight changes (zeroing a field), never def deletions, so saves keep loading.

| change | defs | why |
|---|---|---|
| global scatter → 0 | `MineableComponentsIndustrial`, `MineablePlasteel`, `LKORComponent_Ore` | owner: components and plasteel from rock "made NO sense at all" |
| global scatter → 0 | `MineableGold`, `MineableSilver`, `MineableUranium`, `MineableJade`, `MineableDiamond/Ruby/Sapphire`, `BMT_MineableAmber/Fossils`, `GLO_MineableGlowstone` | moved to biome forms (§3) |
| global scatter → 0 | all six `KOTOR_Mineable*` (ours, Armoury), `LKBeskar_Ore`, `LKPureBeskar_Ore`, `LKDurasteel_Ore` | canon metals are salvage-only |
| global scatter → 0, biome GenStep instead | `RUT_Webwork_SilkKnot` | our own leak: a Webwork material on every map |
| `DA_MineableSteelBeetle` | — | yields Steel; harmless, leave (and its mod is UNMEASURED in the current list) |
| deep weight → home biome only (C#) | Gold, Silver, Uranium, Jade, Plasteel → 0 or home; `RUT_Lanternstone`/`RM_Lanternstone` → Lantern Deeps; `RUT_LivePatternMetal` → Rust Cathedral; `VCHE_Deepchem` → Sump; `VHGE_Helixien` → Propane Lake; jewelry gems → Lantern Deeps; amber/fossil → Flooded Canyon | deep resources are chosen at scan time with no biome gate |
| deep weight → 0 | `OuterRim_Beskar`, `OuterRim_PureBeskar`, `OuterRim_Durasteel`, `KOTOR_IngotCortosis`, `KOTOR_RawRhydonium`, `KOTOR_Tibanna`, `OuterRim_Tibanna` | salvage-only metals; tibanna is beldon-only |
| meteorite pool | every confined or salvage-only mineable leaves `ThingSetMaker_Meteorite`'s pool | otherwise a meteor drops Beskar anywhere |
| Odyssey "mineral rich" mutator | add the same defs to `TileMutatorDef.resourceBlacklist` | the mutator picks any `isResourceRock` mineable per tile |
| GravTide clones | `GravTide_CrossableRock_*` carry 0 scatter already; no change | measured 0 in the dump |

Kept untouched: Steel scatter and deep, all plain stones, every biome wall we already ship, every
already-built gate.


## 5. Mod Settings

Home: a small new mod, `mandrake.rm.minerals` (`RimMandrake.Minerals`), because the change touches
Core and five donors, not one biome. The per-biome forms (nodules, GenSteps) stay in each biome's
own mod inside the unified `RimMandrake.Biomes` (`BIOME_MOD_UNIFICATION_1`), so each biome toggle
also turns its minerals off. The allocation itself is **data**: one `RM_MineralAllocationDef` per
material (global scatter, home biomes, deep allowed where, meteorite yes/no). Owner rules then live
in a file a generator cannot quietly reverse.

| setting | default (= shipped behaviour) | off means | worldgen/mapgen? |
|---|---|---|---|
| Minerals where they belong (master) | on | vanilla's global scatter and deep tables come back unchanged | **mapgen** — new maps only |
| No components or plasteel from rock | on | Core's two mineables scatter again | mapgen |
| Canon Star Wars metals are salvage-only | on | Beskar/Durasteel/KotOR ores scatter at their donor weights | mapgen |
| Precious ores only in their home biomes | on | gold/silver/uranium/jade/gems scatter planet-wide | mapgen |
| Deep deposits follow the biome | on | `CompDeepScanner` uses the global table | scan time, any map |
| Meteorites carry only common ore | on | vanilla meteorite pool | event time |
| Nodule regrowth speed | 1.0× (slider 0–3) | 0 = nodules never regrow | live |
| Salvage yield | 1.0× (slider 0.25–3) | tunes how rich wrecks and troves are | live |

All-off degrades to vanilla behaviour, not to "no ore". ⚠️ XML patches cannot read Mod Settings, so
the weight changes are applied by C# at startup from the allocation defs (and therefore need a
restart to change, which the settings screen says). That is also what lets the master toggle exist
at all.


## 6. Build plan (FOUNDRY)

Sizes: S = under a day, M = one to two days. Sonnet-tier for all but W1 (Opus: it sets the data
shape every other wave reads).

| wave | what | size | needs |
|---|---|---|---|
| W1 | `RimMandrake.Minerals` mod: `RM_MineralAllocationDef` + loader that zeroes/sets `mineableScatterCommonality` and `deepCommonality` at startup per settings; settings screen (§5) | M, C# | — |
| W2 | allocation data for every row of §4 (Core, jewelry, fossils, glowstone, Outer Rim, LK, Armoury, Webwork silk) | S, XML | W1 |
| W3 | Harmony postfix on `CompDeepScanner.ChooseLumpThingDef` filtering by `map.Biome` against the allocation; same filter for `ThingSetMaker_Meteorite`; add confined defs to the Odyssey mineral-rich mutator's `resourceBlacklist` | M, C# | W1 |
| W4 | per-biome vein GenStepDefs (`GenStep_ScatterLumpsMineable` + `forcedDefToScatter`) for the PROPOSED rows once each sitting rules: Lantern Deeps gems/glowstone, Forge obsidian, Flooded Canyon jade/amber, Webwork silk knot. Minerals Sparkle crystals confined by filling their `allowedBiomes` (the field exists, empty, on `MagnetiteCrystal` in the dump; that empty means "all biomes" is UNMEASURED because the framework's C# is not in RimSage, so read it first) | S each, XML | W2, sitting |
| W5 | Scald floor nodules and vent growth — already its own work (`SEA_DIVE_MAPS_BUILD_1`, spec S1–S9); this design only confirms it as the worked example | — | — |
| W6 | salvage tables: components, plasteel, Beskar, Durasteel into existing salvage (Rust Cathedral walls, `RSW_CrashedShip`, Warscar trove, Forge towers, Scald wrecks) | M, XML | W2 |
| W7 | first functional script for the mod (debug process §2): new map on a plain biome shows no gold/component/Beskar lumps; Lantern Deeps map shows gems; deep scan on a plain map never returns Beskar or lanternstone; master toggle off restores vanilla | S | W1–W3 |

Verification is source-first: the allocation and the leak list are checkable offline against the
def dump (`measure`) with no game load. Only W3 and W7 need a live run.

**Economy check before shipping W2:** removing mineable components takes away a vanilla early
supply. The remaining sources (salvage, traders, crafting at the fabrication bench) must be present
on the starting map's region. UNMEASURED today; W6 must land with or before W2.


## 7. Questions for the owner

**Q1. Gold, silver, uranium and jade — how strict?**
- **(A, recommended) Only in their home biomes**, in the forms in §3 (Scald nodules, Blue Desert
  meteoritic metal, canyon jade, cave gems). Every ordinary map has iron and stone only. Trade-off:
  a colony far from those biomes buys or travels for precious metals.
- (B) Home biomes plus a thin trace everywhere (about a fifth of today's rate). Softer, but it keeps a
  little of the "random outcrop" you called absurd.
- (C) No natural gold or silver at all; salvage and trade only. Strongest flavour, harshest economy.

**Q2. Plasteel's name, now that three "durasteel" materials already exist** (Outer Rim's, the
KotOR alloy in our Armoury, and the Outer Rim mining ore).
- **(A, recommended) Rename vanilla plasteel to "durasteel" and retire the three donor durasteels**
  into it with conversion recipes. One material, a canon name, nothing to explain. Costs a
  migration pass on any recipe that names the donor defs.
- (B) Keep plasteel as plasteel; the donor durasteels stay as salvage curiosities. Least work;
  two "super-metals" side by side.
- (C) Leave everything as it is now and only stop the mining. No naming decision at all.

**Q3. Duranium and doonium do not exist in any mod we load.** Make them?
- **(A, recommended) No. Beskar is the one canon salvage metal**, found only in troves and wrecks.
  Nothing new to balance.
- (B) Yes, both as rare salvage-only relic metals with their own uses. More treasure to find; two
  new materials to design and give art.
- (C) Yes, but trader-only, bought at the Bazaar. Keeps them out of the world entirely.

**Q4. Deep drilling (the ground-penetrating scanner).**
- **(A, recommended) Iron everywhere; every other deep deposit only in its home biome** (needs one
  small code change). Drilling matches what the surface says about a place.
- (B) Keep the vanilla deep table but strip the Star Wars metals out of it. No code; deep drilling
  still finds gold and lanternstone anywhere.
- (C) Deep drilling finds iron and fuels only. Simplest; drilling stops being a treasure hunt.

