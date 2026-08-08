# biome_terrain_palette.md — Authoritative Biome + Terrain Palette

_The single coherent list of every **biome** (world-tile type) and every notable **terrain**
(in-map floor) available across the campaign's confirmed/candidate mod stack, for building the
"mostly desert, highly volcanic, rare rivers, tiny oceans ringed by vicious jungle, alien terrain
welcome" world. Companion to `desert_world_design.md` (the four-axis "why land here?" layer),
`Custom_World.md` (director-mod toolkit), and `setup_checklist.md` §5–§6._

**Created:** 2026-08-04. **RimWorld 1.6 + Odyssey, all DLC present, personal single-player build.**

---

## 0. Read this first — biome vs terrain (they are different defTypes)

These two words were previously blurred in the docs. They are **separate `Def` types** edited by
**separate tools**, and keeping them apart is what makes controlled world-authoring possible:

- **Biome** (`BiomeDef`) = the *world-tile* category on the planet grid (desert, tropical
  rainforest, pyroclastic conflagration). It sets climate, flora/fauna, diseases, foraging, and
  which terrains the local map generator paints. You influence biome **placement** via **Choose
  Biome Commonality** (per-biome selection weight) + the world-save, and each modded biome carries
  its own `workerClass` that decides *where on the planet* it may appear.
- **Terrain** (`TerrainDef`) = the *in-map floor material* under each cell (sand, rich soil, lava
  rock, deep water, alien red-water). It sets fertility, walk speed, buildability, and — critically
  for us — **water form** (surface / groundwater / none). You influence terrain via **Map Designer**
  (per-map density of sand/soil/water/ruins) and by authoring/patching `TerrainDef`s.

**Landforms** (rivers, coastlines, mountains, cliffs) are deliberately **left to happen
independently** (user 2026-08-04) — Geological Landforms + vanilla worldgen place them; we do not
enumerate or micro-author them here.

**Verification legend:** ✅ verified from the actual 1.6 `Def` XML in-hand · 🔎 defName from stable
base-game knowledge, spot-check in a dev world before authoring. **(All biome mods —
Alpha Biomes, Advanced Biomes, Biomes! Oasis, More Vanilla Biomes, and the newly-adopted Biomes!
family (Core/Framework/Caverns/Polluted Lands/Fossils, see §A7) — are now ✅ defName-verified from
their 1.6 sources; only the vanilla/Odyssey rows remain 🔎.)**

---

## TABLE A — BIOMES (world-tile types)

### A1. Vanilla + Odyssey base biomes (the grounded strand)

The "mostly desert" world is built from these by weighting the three dry biomes **up** (via Choose
Biome Commonality) and everything else **down**. defNames below are the long-stable base-game
identifiers.

| Biome | defName | Climate niche | Role in our desert world | Four-axis fit (see design doc) |
|---|---|---|---|---|
| Extreme Desert | `ExtremeDesert` 🔎 | Hottest, near-zero rainfall, almost no flora | **Primary sea to cross** — weight HIGH | ①salvage/stone ②✗water,✗food ③buried wrecks ④heat + no-water exit timer |
| Desert | `Desert` 🔎 | Hot, very low rainfall, sparse | **Primary terrain** — weight HIGH | ①stone/salvage ②water scarce ③ruins ④heat/sandstorm |
| Arid Shrubland | `AridShrubland` 🔎 | Warm, low rainfall, some grass/shrubs | Transitional "shore" of the desert sea — weight MED | ①modest forage ②limited water ③— ④manhunter packs |
| Temperate Forest | `TemperateForest` 🔎 | Mild, moderate rainfall | Rare — weight LOW | ①wood/food ②exposure to raids ③— ④raid corridor |
| Tropical Rainforest | `TropicalRainforest` 🔎 | Hot, very wet, dense | **The vicious jungle** ringing water — weight LOW, tie to water landforms | ①biomass ②movement/heatstroke ③exotic flora ④disease + killer plants |
| Tropical Swamp | `TropicalSwamp` 🔎 | Hot, waterlogged | Jungle-water fringe — weight LOW | ①water+biomass ②build space, malaria ③— ④disease/movement |
| Temperate Swamp | `TemperateSwamp` 🔎 | Mild, waterlogged | Rare water fringe — weight LOW | ①water ②buildable ground ③— ④movement |
| Cold Bog | `ColdBog` 🔎 | Cool, waterlogged | Off-theme — weight ~0 | — |
| Boreal Forest | `BorealForest` 🔎 | Cool, moderate | Off-theme — weight LOW/0 | — |
| Tundra | `Tundra` 🔎 | Cold, low growth | Off-theme — weight ~0 | — |
| Ice Sheet | `IceSheet` 🔎 | Frozen, lifeless | Off-theme — weight 0 | — |
| Sea Ice | `SeaIce` 🔎 | Frozen ocean | Off-theme — weight 0 | — |
| Ocean | `Ocean` 🔎 | Deep saltwater tile | The **tiny oceans** (keep few) | water source (saline) |
| Lake | `Lake` 🔎 | Inland freshwater tile | **Rare rivers/lakes** (keep few) | fresh surface water |

**Odyssey note:** Multiple independent sources (Ludeon blog,
RimWorld Wiki, SteamDB patch notes) confirm **Odyssey adds FIVE new planet-surface biomes** plus
40+ new animals and reworked map generation. Three are named directly in the sources and are ⭐
highly relevant to this campaign; the other two are not named in the snippets pulled:

| Odyssey biome | label (search-confirmed) | defName | Relevance |
|---|---|---|---|
| **Glowforest** | glowforest | `⏳ confirm at machine` | ⭐ **perpetual-night / fungal-light biome** — prime **dark-biome** candidate for the §3(e) low-visibility layer (see new §A6). Vanilla-DLC, zero mod dependency. |
| **Lava fields** | lava fields | `⏳ confirm` | ⭐ **third native volcanic biome** alongside Alpha's Pyroclastic + Advanced Biomes' Volcano — reinforces the "highly volcanic" read with no mod. |
| **Toxic scarlands** | toxic scarlands | `⏳ confirm` | ⭐⭐ **native toxic/polluted terrain we already own** — candidate to carry the §4 rogue-android *water-poisoning / terrain-souring* role with ZERO mods (may make Sustainable Toxic Environment optional; see `desert_world_design.md` §3(c)). |
| (2 more, unnamed in sources) | ⏳ | ⏳ | Enumerate off the loaded Odyssey def list in a dev world. |

These are **evidence-backed labels but unverified defNames** — enumerate all five off the loaded
1.6+Odyssey def list at the machine and fill the defName column. This does not block desert
authoring (which rests on the vanilla dry biomes above), but glowforest + lava fields + toxic
scarlands are now first-class parts of the palette, not "confirm later" afterthoughts.

### A2. Alpha Biomes — WS 1841354677 · juanosarg/AlphaBiomes ✅ (all 12 verified from 1.6 defs)

Verified directly from `AlphaBiomes/1.6/Defs/BiomeDefs/`. **Placement is code-driven** (each has a
`workerClass`, e.g. `AlphaBiomes.BiomeWorker_PyroclasticConflagration`) rather than vanilla
temp/rainfall whitelisting — so you tune their frequency through **Choose Biome Commonality** +
`settlementSelectionWeight`, not by editing temperature bands.

| Biome | defName | label | Fit for our world | Notes (verified) |
|---|---|---|---|---|
| **Pyroclastic Conflagration** | `AB_PyroclasticConflagration` | pyroclastic conflagration | ⭐ **CORNERSTONE volcanic biome** | Permanent +30 °C heat wave (`AB_VolcanicHeatWave`), periodic acid rain, fire-starting fauna; `allowRivers=false`; obsidian/lava terrain. "Very hard." |
| **Feralisk Infested Jungle** | `AB_FeraliskInfestedJungle` | feralisk infested jungle | ⭐ **the "vicious jungle"** candidate | movementDifficulty 2, forageability 1; giant-spider predators + webbing terrain |
| **Miasmic Mangrove** | `AB_MiasmicMangrove` | miasmic mangrove | ⭐ jungle-water fringe | movementDifficulty 4 (very slow), forageability 1; disease-heavy wetland |
| **Mycotic Jungle** | `AB_MycoticJungle` | mycotic jungle | jungle variant near water | movementDifficulty 1, forageability 0.5; giant mushrooms, mycotic soil |
| **Tar Pits** | `AB_TarPits` | tar pits | volcanic/arid exotic | movementDifficulty 4; tar lakes + fertile patches; bumbledrone hives; **tar = harvestable exotic** |
| **Propane Lakes** | `AB_PropaneLakes` | propane lakes | alien fuel terrain | `canAutoChoose=false` (won't self-place — must be seeded); flammable propane lakes/solids |
| **Rocky Crags / Forsaken Crags** | `AB_RockyCrags` (label "forsaken crags") | forsaken crags | arid alien badland | movementDifficulty 1, forageability 0.5; forsaken sand/rock, rose-quartz stone |
| **Gallatross Graveyard** | `AB_GallatrossGraveyard` | gallatross graveyard | arid exotic | forageability 0.5; giant-creature bone terrain |
| **Ocular Forest** | `AB_OcularForest` | ocular forest | alien, low value | forageability 0.1 (near-barren for forage); eye-creature biome |
| **Gelatinous Superorganism** | `AB_GelatinousSuperorganism` | gelatinous superorganism | 🚫 **CUT from roster (user 2026-08-04)** — wrong genre; salvage its mineable nutrient blocks → re-home as *strange growths inside caverns* (Biomes! Caverns / CaveBiome) | movementDifficulty 4; slime terrain (`AB_Slime`, `AB_RichSlime`) |
| **Idyllic Meadows** | `AB_IdyllicMeadows` | idyllic meadows | 🚫 **CUT from roster (user 2026-08-04)** — resource-rich + safe breaks the scarcity thesis; do not place | forageability 1.2 (resource-rich); off the scarcity theme |
| **Mechanoid Intrusion** | `AB_MechanoidIntrusion` | mechanoid intrusion | ⭐ ties to android/mech threat; IN as ONE hand-seeded "Shipyards" cluster (§2D) | `canAutoChoose=false` (seed only); forageability 0; mechanoid substructure terrain |

### A3. Advanced Biomes (Continued) — WS 3541022508 · emipa606/AdvancedBiomes ✅ (5 biomes verified from 1.6 defs)

1.6-only build (`supportedVersions` = 1.6 alone; re-released as Asset Bundles Nov 2025). Adds
exactly **5** biomes. ⚠️ **defNames are UNPREFIXED** (bare `Volcano`, `Wasteland`, `Lava` etc.) —
a real collision/legibility risk in a big load order; note it when authoring and when using Choose
Biome Commonality (they'll appear under plain names). ("Toxic spores" is a `GameConditionDef`, not a
biome.)

| Biome | defName | label | Fit for our world |
|---|---|---|---|
| **Volcano** | `Volcano` | volcano | ⭐ **second volcanic biome** alongside Alpha's Pyroclastic; lava + obsidian terrain, ActiveTerrain lava dynamics |
| **Poison Forest** | `PoisonForest` | poison forest | ⭐ **vicious-jungle candidate** near water — spore air, scum/muck floor, poison terrain family |
| **Wasteland** | `Wasteland` | wasteland | ⭐ **rogue-android home candidate** — asphalt/nuclear-waste terrain, desolate |
| **Savanna** | `Savanna` | savanna | dry grassland — transitional desert edge |
| **Wetland** | `Wetland` | wetland | rare water fringe |

### A4. Biomes! Oasis — WS 2538518381 · biomes-team/BiomesOasis ✅ (verified from 1.6 defs)

1.6 verified (`supportedVersions` 1.2–1.6). Adds exactly **one** biome: the **Chromatic Oasis**
(`BMT_ChromaticOasis`, label "chromatic oasis") — groundwater-rich desert oasis with rare
plants/animals (gem scorpion, aquamelon). ⭐ **ideal "rare water ringed by exotic life" tile** —
directly serves the rare-rivers/tiny-oceans intent. Requires **Biomes! Core / Framework**
(biomes-team/BiomesCore) — confirm that dependency is in the stack if adopted. No standalone
`TerrainDef`s in its 1.6 folder (uses vanilla/Core water + soil terrains).

### A5. More Vanilla Biomes — WS 1931453053 · Zylleon/MoreVanillaBiomes ✅ (10 biomes verified from 1.6 defs)

1.6 verified (`supportedVersions` 1.0–1.6). Ten vanilla-friendly biomes, `ZBiome_`-prefixed. The
desert-relevant ones are starred; the cold/off-theme ones weight toward 0.

| Biome | defName | label | Fit |
|---|---|---|---|
| **Desert Oasis** | `ZBiome_DesertOasis` | desert oasis | ⭐ vanilla-toned oasis (groundwater near surface, small lakes + vegetation) |
| **Badlands** | `ZBiome_Badlands` | badlands | ⭐ rocky/dry/desolate temperate — strong desert texture |
| **Coastal Dunes** | `ZBiome_CoastalDunes` | coastal dunes | ⭐ sandy low-lying coast — tiny-ocean fringe |
| **Sandbar** | `ZBiome_Sandbar_NoBeach` | sandbar | flat sandy island, near-barren |
| **Marsh** | `ZBiome_Marsh` | marsh | water fringe, dense low plants |
| **Stormy Savanna** | `ZBiome_Grasslands` | stormy savanna | dry grassland (note defName says Grasslands) |
| **Cloud Forest** | `ZBiome_CloudForest` | cloud forest | off-theme, weight LOW |
| **Alpine Meadow** | `ZBiome_AlpineMeadow` | alpine meadow | off-theme, weight LOW/0 |
| **Glacial Shield** | `ZBiome_GlacialShield` | glacial shield | off-theme, weight 0 |
| **Ice Floes** | `ZBiome_Iceberg_NoBeach` | ice floes | off-theme, weight 0 |

Terrains: two water floors only — `ZBiome_WaterChestDeep`, `ZBiome_WaterOceanChestDeep` (added to §B4).

### A6. Dark biomes — the low-visibility strand (NEW 2026-08-04, design in `desert_world_design.md` §3(e))

A deliberately **rare** strand where **vision is the scarce resource** — perpetual-dark tiles that
pair with the fog-of-war layer (below) to make "you only see it when you see it" tension. Keep
commonality LOW (same discipline as alien biomes; if dark tiles are everywhere the tension dies).
All pillar-clean (environment/info-side, no buildable economy). **Route = MOD, ≈ zero new dependency.**

| Dark biome | Source | Status | Notes |
|---|---|---|---|
| **Glowforest** | ⭐ **Odyssey (vanilla DLC)** | evidence-backed, defName ⏳ | Perpetual night + fungal bioluminescence; **already owned, zero mod**. First choice — enumerate defName at machine. |
| **CaveBiome** | emipa606 (WS) | 🔎 1.6 appears live | Permanent darkness; **requires Caveworld Flora**. Verify supportedVersions in RimSort. |
| **⭐ Biomes! Caverns** | `BiomesTeam.BiomesCaverns` | ✅ **1.6 CONFIRMED FROM SOURCE (2026-08-07)** | **FULLY ADOPTED** (see `required_mods.md` "Biomes! FAMILY"). Cavern biomes `BMT_CrystalCaverns` / `BMT_EarthenDepths` / `BMT_FungalForest` + ~71 cavern animals. Deps: Biomes! Core + Geological Landforms (both in stack). Now the confirmed dark-tile source; keep commonality LOW. |
| **Ocular Forest** | `AB_OcularForest` (Alpha Biomes, already in stack) | 🔎 low-light NOT confirmed | Confirmed weird/transdimensional but NOT confirmed to darken the map — **in-game check**; if it darkens, it doubles as a dark biome for free. |

**Fog of war (the LOS-reveal companion, not a biome):** two candidate sources, **run only ONE** —
(1) **CAI-5000** (already in the stack for smart raid AI) **bundles its own fog of war** → likely
free with AI built to path through it; or (2) **(NWN) Real Fog of War Continued** (WS 3391128917),
whose edge is **symmetric FoV** (players + AI + animals + mechs all have LOS, so it can't blind only
the player) and **FoV shrinks with the Sight stat + darkness + weather** — meaning it stacks
multiplicatively with these dark biomes AND the extracted SW sandstorm/red-fog weather (a dark biome
in a sandstorm ≈ near-blind for everyone). Decision + the three in-game checks live in
`setup_checklist.md` §6. **Combining a dark biome + LOS fog + an unseen spore hazard (§B5 below) =
the purest qualitative-danger stack in the design.**

### A7. Biomes! family — FULLY ADOPTED 2026-08-07 (all ✅ 1.6 confirmed from source in `mod_sources/`)

The BiomesTeam stack, adopted whole (adoption decision + deps + pillar audit live in `required_mods.md`
"Biomes! FAMILY"; this is the defName-level palette side). **Load order: Framework → Core → packs.**

| Biome / content | defName(s) | Source (pkgId) | Notes |
|---|---|---|---|
| Biomes! **Framework** | *(no biomes — code module)* | `BiomesTeam.CoreFramework` (1.6-only) | Shared backbone Core v1.6 hard-depends on; also bundles WaterWalker (`Draegon.WaterWalker`). No palette content. |
| Biomes! **Core** | *(scaffolding + ~10 base animals)* | `BiomesTeam.BiomesCore` (→1.6) | Base dep for the packs; shared terrains/fauna. |
| Biomes! **Caverns** | `BMT_CrystalCaverns` (crystalline caverns), `BMT_EarthenDepths` (earthen depths), `BMT_FungalForest` (fungal forest) | `BiomesTeam.BiomesCaverns` (1.4–1.6) | ⭐ underground biomes — the confirmed **dark-tile** source (see §A6). ~71 cavern animals. Needs Core + Geological Landforms. Keep commonality LOW. |
| Biomes! **Polluted Lands** | ⚠️ **no BiomeDef** — patches `pollutionWildAnimals`/`wildPlants` into existing biomes (AridShrubland, BorealForest, ColdBog, the Caverns biomes, Ashlands, ReGrowth wastelands) | `BiomesTeam.BiomesPollutedLands` (1.5–1.6) | ~31 polluted creatures (barbed pangolin, bilious varog, lyncus seal, tox-wool sheep, pustule hornet+queen, tainted turtle, sludge crawler, glowtail, mutating tumorfish, varmot, waste hound, …) + mutated plants. Rides the pollution mechanic = the §4 android-souring layer. ⚠️ tox-wool sheep is a fast breeder — keep wild. Terrain `BMT_ToxWoodPlankFloor`. Needs Core + Biotech. |
| Biomes! **Fossils** | `BMT_MineableFossils`, `BMT_MineableAmber` (global mineables) | `BiomesTeam.BiomesFossils` (1.4–1.6) | Terrain-treasure Exotic ③ (full entry in `required_mods.md`). No biome of its own. |

---

## TABLE B — TERRAINS (in-map floor materials)

### B1. Vanilla + Odyssey terrains that carry the desert/water model

Water form drives the §3A resource-partition scheme: **surface** = pump/haul directly · **groundwater**
= well only · **none** = carry from the ship. defNames are stable base-game identifiers (🔎 spot-check).

| Terrain | defName | Water form | Fertility / use | Role |
|---|---|---|---|---|
| Sand | `Sand` 🔎 | none | 0 fertility, buildable | Desert default floor |
| Soft Sand | `SoftSand` 🔎 | none | 0, slows movement | Dune interiors |
| Soil | `Soil` 🔎 | groundwater (shallow) | ~1.0 fertility | Farmable pockets |
| Rich Soil | `SoilRich` 🔎 | groundwater | ~1.4 fertility | Rare fertile ground (river/oasis) |
| Mossy Soil | `MossyTerrain` 🔎 | groundwater | mid fertility | Shaded/forest floor |
| Gravel | `Gravel` 🔎 | none | low | Rocky/arid maps, mineable base |
| Mud | `Mud` 🔎 | surface (waterlogged) | slows, unbuildable-ish | Swamp/river edge |
| Marsh / Marshy Soil | `Marsh` / `MarshySoil` 🔎 | surface | fertile but soft | Wetland fringe |
| Shallow Water | `WaterShallow` 🔎 | **surface** | fordable | Pumpable freshwater edge |
| Deep Water | `WaterDeep` 🔎 | surface | impassable | Lake/river core |
| Moving Shallow | `WaterMovingShallow` 🔎 | **surface (fresh)** | river shallows | ⭐ river fill point |
| Moving Deep | `WaterMovingChestDeep` 🔎 | surface (fresh) | river core | River |
| Ocean Shallow | `WaterOceanShallow` 🔎 | surface (**saline**) | coast | Pump→desalinate |
| Ocean Deep | `WaterOceanDeep` 🔎 | surface (saline) | impassable | Tiny-ocean core |
| Ice | `Ice` 🔎 | frozen | impassable | Off-theme |

**Odyssey terrains:** any Odyssey-added surface floors → ⏳ confirm off the loaded def list; not
required for the desert model above.

### B2. VGE — gravship substructure floors ✅ (from VanillaGravshipExpanded 1.6 Terrains.xml)

These are the **onboard** floors (the ship deck), not planet terrain — included so the palette is
complete and nothing mistakes them for landable ground.

`VGE_DamagedSubstructure` (damaged gravship substructure) · `VGE_GravshipSubscaffold` (gravship
subscaffold) · `VGE_MechanoidSubstructure` (mechanoid substructure) · `VGE_AncientOrbitalPlatform`
(ancient orbital platform) · `VGE_AsteroidIce` (asteroid ice) · `VGE_Compressed_Vacstone_Floor`
(compressed vacstone) · `VGE_FakeTerrain` (fake terrain — internal/utility).

### B3. Alpha Biomes terrains ✅ (from AlphaBiomes 1.6 TerrainDefs — the alien-terrain palette)

Grouped by use. **Alien terrain welcome** (user) — this is where it lives:

- **Volcanic / lava (⭐ for the volcanic world):** `AB_LiquidLava`, `AB_SolidifiedLava`, `AB_Obsidian`,
  `AB_VolcanicGravel`, `AB_BlackPebbles`, `AB_ParchedEarth`, `AB_TileObsidian`, `AB_FlagstoneObsidian`
- **Sand / arid (⭐ desert texture):** `AB_FineSand`, `AB_CompactedSand`, `AB_GrassySand`,
  `AB_ForsakenSand`, `AB_FineForsakenSand`, `AB_ForsakenRock`, `AB_CrackedMud`, `AB_RichCrackedMud`
- **Alien red-water (⭐ "tiny oceans" with alien flavor — Gunk submod, `GU_` prefix):**
  `GU_RedWaterShallow`, `GU_RedWaterDeep`, `GU_RedWaterMovingShallow`, `GU_RedWaterMovingChestDeep`,
  `GU_RedWaterOceanShallow`, `GU_RedWaterOceanDeep`; alien sand/soil: `GU_AlienSand`, `GU_AlienSandFine`,
  `GU_AlienSoftSand`, `GU_RichAlienSand`, `GU_MossyRed`; alien tech floors: `GU_MetalFloor1/2/3`, `GU_Piping`
- **Tar / propane (exotic fuel terrain):** `AB_Tar`, `AB_ArtificialTar`, `AB_TarMud`, `AB_PropaneLake`,
  `AB_SolidPropane`
- **Slime (gelatinous biome):** `AB_Slime`, `AB_RichSlime`, `AB_SlimeGrass`, `AB_SlimyMud`, `AB_LiquidSlime`
- **Mycotic / alien-wood:** `AB_MycoticSoil`, `AB_MycoticSoilRich`, `AB_MycoticGrass`,
  `AB_AlienWoodFloors_CrystalWood`, `AB_AlienWoodFloors_MushroomStalks`, `AB_AlienWoodFloors_RedWood`
- **Fertile/grass (keep sparse — off-theme abundance):** `AB_FertileMarsh`, `AB_FertileMud`,
  `AB_FertileGrassyFlowerySoil`(+`_Oversaturated`), `AB_GrassyFlowerySoil`, `AB_LushGrass`, `AB_DenseGrass`
- **Stone tiles/flagstone (crafted floors, not natural):** `AB_TileCragstone/Mudstone/RoseQuartz`,
  `AB_FlagstoneCragstone/Mudstone/RoseQuartz`, `AB_AsphaltFloor`, `AB_AsphaltBridge`
- **Cold (off-theme):** `AB_PackedIce`, `AB_PackedSnow`, `AB_SnowOverRocks`

### B4. Advanced Biomes / More Vanilla Biomes terrains ✅ (from 1.6 defs)

- **Advanced Biomes** (⚠️ unprefixed defNames — collision-watch):
  - Volcanic: `Lava`, `VolcanoObsidian`, `VolcanoSoil`, `VolcanoSoilRich`
  - Poison Forest: `PoisonSoil`, `PoisonSoilRich`, `PoisonMud`, `PoisonMarsh`, `PoisonMarshyTerrain`,
    `PoisonMossyTerrain` (the "scum/muck" floors — surface water, but **fouled** — thematically close
    to the android water-denial doctrine)
  - Wasteland: `WastelandAsphalt`, `NuclearWaste` (⭐ android-tile flavor)
  - Savanna: `SavannaSoil`, `SavannaSoilRich`
  - Plus `ActiveTerrain` dynamics for Volcano + Wasteland (lava spread / hazard tiles).
- **More Vanilla Biomes:** `ZBiome_WaterChestDeep`, `ZBiome_WaterOceanChestDeep` (surface water — the
  latter saline; both deep/impassable cores).
- **Biomes! Oasis:** no standalone TerrainDefs in 1.6 (uses vanilla + Biomes! Core terrains).

### B5. Hostile flora — the threat-axis ④ plant layer (NEW 2026-08-04, design in `desert_world_design.md` §3(c))

Not terrain per se, but map-placed **plant hazards** that sit ON these terrains and give the coast/
oasis/mycotic tiles their §④ threat. Resolved after a full 1.6 search + source audit:

- **⭐ Agarilux Prime** (`AB_AgariluxPrime`, Alpha Biomes — already in stack, ✅ source-verified) —
  the **single best confirmed hostile plant**. Stationary radius-8 toxic-spore emitter
  (`CompProperties_GasProducer` → `AB_MycoticSpores`; gas `AlphaBiomes.Gas_Mycotic.Tick()` deals
  Cut+ToxicBuildup to non-AlphaAnimals pawns and Cut(50) to competing plants). **ADOPTED** as the
  free "clear-before-you-harvest" area-denial set-piece for **coast AND oasis** (user 2026-08-04),
  explicitly including the spore **mushrooms** (Mycotic fungi). NOT a map-creeper — a fixed radius-8
  bubble, so true tile-to-tile map-creep stays an AUTHOR/RimBridge fallback, not a launch blocker.
- **Strange Fungus** (`RRY_Plant_Neomorph_Fungus`, AvP mod) — **REJECTED, do NOT extract or
  cherry-pick** (source-audited 2026-08-04). Uses custom C# assembly classes (`RRYautja.Plant_Neomorph`,
  `RRYautja.Thing_AddsHediff`) so it won't load as pure XML, and its spore is a *pregnancy vector*
  (injects `RRY_NeomorphImpregnation` = the xenomorph lifecycle) — reintroducing the rejected
  franchise's core creature by the back door. If a proximity-*triggered* spore plant is wanted (the
  one thing Agarilux doesn't do), **AUTHOR it** by cloning the `Gas_Mycotic` mechanic with a
  proximity trigger + pure toxic payload (no impregnation).
- **Wider hostile-flora roster** (carnivorous trees / brambles / man-eating vines) — **no clean
  standalone 1.6 mod exists** (searched; useful negative). Vanilla Brambles are passive. Wider roster
  = AUTHOR/RimBridge (reskin/extend the Prime spore mechanic to more plant defs), not a mod hunt.
- **Toxifier / polluted-fauna layer** — ⭐ **now carried by Biomes! Polluted Lands (`BiomesTeam.BiomesPollutedLands`, FULLY ADOPTED 2026-08-07, 1.6 confirmed from source; see `required_mods.md` "Biomes! FAMILY").** It adds **no BiomeDef of its own** — it patches `pollutionWildAnimals` + `wildPlants` into existing biomes (incl. **AridShrubland** = desert-adjacent, plus the Biomes! Caverns biomes, BorealForest, ColdBog, Ashlands, ReGrowth wastelands), so its ~31 polluted creatures + mutated plants appear on toxic/polluted tiles the rogue-android faction sours — the §4 water-poisoning doctrine (design in `desert_world_design.md` §3(c)). Its one floor is cosmetic `BMT_ToxWoodPlankFloor`. **Sustainable Toxic Environment + More Toxplants drop to optional extras.** ⚠️ **Pillar watch: the tox-wool sheep (`BMT_ToxSheep`, gestation 5.661 d, shearable/9 d) is a fast breeder — keep it wild, don't ranch a tamed flock into a wool printer** (Alpha Animals/Megafauna grazer rule). Advanced Biomes Poison* floors + Odyssey's toxic scarlands can still carry the souring role natively where no fauna is wanted.

---

## 3. How this palette drives the "mostly desert, volcanic, rare water, jungle-ringed" world

- **Desert dominance:** weight `ExtremeDesert` + `Desert` + `AridShrubland` HIGH in Choose Biome
  Commonality; push all cold/temperate biomes toward 0. This alone yields the desert sea.
- **Volcanic character:** seed `AB_PyroclasticConflagration` (⭐) and Advanced Biomes' Volcano at a
  low-but-present commonality; their `AB_LiquidLava`/`AB_Obsidian`/`AB_VolcanicGravel` terrains give
  the "highly volcanic" read even inside otherwise-desert tiles.
- **Rare water, jungle-ringed:** keep `Lake`/`Ocean` tiles few; where they occur, favor
  `TropicalRainforest` / `AB_FeraliskInfestedJungle` / `AB_MiasmicMangrove` / `BMT_ChromaticOasis`
  as the surrounding ring (the vicious jungle around scarce water). This is a **placement pattern**
  Map Designer + biome commonality can bias, and the natural payoff of the Tier-2b world-authoring
  process to be designed next.
- **Alien terrain welcome:** the `AB_*` / `GU_*` terrain families (B3) are the alien-floor reservoir —
  red alien oceans, obsidian flats, slime, tar — to sprinkle for strangeness without new biomes.
- **Water model intact:** every water terrain above is tagged surface/groundwater/none so the §3A
  partition and the no-free-generator guardrail hold — a `Sand`/`ExtremeDesert` tile is genuinely
  ✗-water (carry from the ship), while `WaterMovingShallow`/`BMT_ChromaticOasis` are fill points.

## 4. Open items before this palette is "final"
1. ✅ **DONE 2026-08-04:** `2026-08-04l` ingested — Advanced Biomes (5 biomes, unprefixed defNames),
   Biomes! Oasis (`BMT_ChromaticOasis`), More Vanilla Biomes (10 `ZBiome_*`) all verified from 1.6
   defs; A3/A4/A5 + B4 now hold real defNames. **All four biome mods are now defName-verified.**
2. ⚠️ **Advanced Biomes uses unprefixed defNames** (`Volcano`, `Wasteland`, `Lava`, `Savanna`,
   `PoisonSoil`, …). In a large load order this is a legibility/collision hazard — watch for def
   overwrites and, if a clash appears, patch-rename via the compat mod. Not blocking, but flagged.
3. ⭐ **Dev-world pass — enumerate the 5 Odyssey surface biomes** (glowforest, lava fields, toxic
   scarlands + 2 unnamed) and fill their defName columns in A1/A6/A2-adjacent; these are now
   evidence-confirmed to exist (not "maybe"), only their defNames need capture. Also spot-check the
   stable vanilla defNames in A1/B1 while in the dev world.
4. 🔎 **In-game visibility checks** (the §A6 dark/fog strand): (a) CAI-5000 built-in fog of war vs
   NWN Real FoW — pick one, never both; (b) confirm a 1.6 dark-biome mod (CaveBiome looks live) or
   just use Odyssey glowforest; (c) does `AB_OcularForest` actually impose low light? Keep dark
   biomes RARE. All tracked in setup_checklist §6.
5. ✅ **RESOLVED 2026-08-07 — Toxic-souring source** (§B5 / design §3(c)): now carried by **Biomes!
   Polluted Lands** (FULLY ADOPTED, 1.6 confirmed from source; see §A7 + `required_mods.md`). STE +
   More Toxplants drop to optional extras; Odyssey toxic scarlands / Advanced Biomes Poison* floors
   remain a zero-mod fallback where fauna isn't wanted.
6. Decide final **commonality weights** per biome (setup_checklist §6) — this palette lists roles,
   not the numeric profile yet. **Include the Biomes! Caverns dark tiles + Polluted-tile pollution
   weight in this pass; keep both LOW.**
7. ✅ **Biomes! Core/Framework dependency confirmed required** and now in the stack (the whole Biomes!
   family is adopted, §A7) — needed for Chromatic Oasis, Caverns, and Polluted Lands alike. Load
   order Framework → Core → packs.

---

## 5. Candidate scan — other biome mods evaluated 2026-08-04 (Fetcher `2026-08-04m` + `2026-08-04n`)

Ran a 10-query sweep (Star Wars / desert / alien / sand / volcanic / exotic-fungal / GitHub
`BiomeDef`) plus a source-verification pull. Verdicts, distinguishing **verified-from-source** from
**listing-text-only**:

**DIRECTION (user 2026-08-04):** Do **not** re-label existing biomes to fake Star Wars planets — a
rename patch is off the table. Instead, **release Star Wars – Biomes as a proper 1.6 mod** (bring the
real mod's biome content forward to 1.6). And the **Alien franchise is out** — the xenomorph creature
layer would pollute the crashed-Factory-ship / Jawa concept, so Alien | RimWorld is rejected despite
being verified 1.6.

**Star Wars – Biomes — EVALUATED + RESOLVED 2026-08-04 (source audited, Fetcher `2026-08-04p`):**

Source pulled and audited (Ferreira312/Star-Wars---Biomes-Addon, `supportedVersions` 1.1/1.2, dated
Nov 2020 — confirmed **not 1.6**). Goal was **new mechanics, not planet names** (user). Scorecard:

- **15 planet biomes** (Tatooine, Mustafar, Hoth, Geonosis, Dagobah, Kashyyyk, Naboo, Dathomir,
  Kamino, Crait, Bespin, Felucia, Scarif, Yavin IV, Endor). They *are* differentiated from each other
  (`movementDifficulty` 1.0→4.0, `forageability` 0→1.0, `animalDensity`, per-biome diseases,
  terrain-by-fertility) — but their *behavior* mostly duplicates biomes we already own (Tatooine≈
  desert, Mustafar≈lava, Hoth/Crait≈ice, Felucia≈mycotic jungle). Each uses a **C# `workerClass`**
  (`SWWO.Biomes.BiomeWorker_*`) for placement → a full port needs an assembly recompile against 1.6,
  not just an XML bump. **Verdict: not worth porting all 15 reskin-biomes.**
- **Custom weather = the one genuinely-new mechanic.** Four real `WeatherDef`s with combat teeth:
  Sandstorm / Dry sandstorm (`accuracyMultiplier` **0.25**, 2× wind, VeryBad; dry one throws
  lightning), Red fog (accuracy 0.5), Red foggy rain (accuracy 0.5 + move 0.9). Bespin weather is
  cosmetic/Good-favorability → dropped.
- Also ships custom Felucia flora (4 plants) + aquatic fauna (Krill, Aiwha); `wildAnimals` blocks are
  empty (delegates fauna to animal mods — why it advertises Megafauna/Alpha Animals compat).

**ACTION TAKEN (user "extract"):** the four weathers were **extracted into `custom_patches/
GravshipCompat`** as pure XML (task #63) — `Defs/WeatherDefs/SWDesertWeather.xml` (defNames
`SW_Sandstorm`/`SW_DrySandstorm`/`SW_RedFog`/`SW_RedFoggyRain`; custom C# overlays swapped for vanilla
`WeatherOverlay_Fog`, all gameplay fields preserved) + `Patches/SWDesertWeather_Attach.xml`
(conditional-wrapped injection into `baseWeatherCommonalities` of Desert/ExtremeDesert/AridShrubland/
`ZBiome_DesertOasis`/`ZBiome_Badlands` → sandstorms, and `AB_PyroclasticConflagration`/`Volcano` →
red fog). All 3 XML files validated well-formed. **No biomes ported** — the existing palette carries
biome variety; only the sandstorm-guts-accuracy mechanic was worth taking.

**WATCH — 1.6 listing but defs unverified:**

- **Standalone Tribal Fungi Biome** (WS 2182438464) — tagged **[1.6]**; self-contained fungal forest
  with a toggle to disable world placement (→ seed-able exotic pocket, pillar-safe). Source fetch
  returned no version detail this pass; **listing-text only.** Low-priority; verify defs before adding
  if a fungal pocket beyond Alpha Biomes' `AB_MycoticJungle` is wanted. (Not Alien-related — kept.)

**REJECTED (with reason):**

- **Alien | RimWorld** (WS 3596077324 / nighzmarquls) — verified 1.6, but **OUT by design**: the
  Alien/Xenomorph creature + lifecycle layer rides along with its biome and would pollute the Star
  Wars / crashed-Factory-ship concept. Not adopted.
- **Terra Project (Core)** (Lanilor) — **DEAD.** Source pulled: `targetVersion 0.19.0` (RimWorld 1.0,
  files dated 2018). No 1.6 folder. Its 13 biomes/caves/islands are superseded by Alpha Biomes +
  Geological Landforms. Drop.
- **Realistic Planets 1.6** (WS 3533147031) — author-marked **[DISCONTINUED]**, and it's a *worldgen /
  biome-placement overhaul* that would fight the hand-authored Tier-2b world you want + Choose Biome
  Commonality. Avoid (automates the thing we intend to author). Same logic rejects **ReGrowth Expanded
  World Generation** and **Tilt the Planet**.
- **ReGrowth: Wastelands** — Workshop-tagged **[Deprecated]**. Its always-polluted wasteland biomes
  are already covered by Advanced Biomes (`Wasteland`/`NuclearWaste`) + Biotech native pollution.
  Skip. (ReGrowth 2/Core, 1.4–1.6, is a plant/weather/texture enhancement framework, not a biome
  adder — off the minimalist path unless HD retextures are wanted.)

**RECLASSIFIED (not a biome — moved to treasure catalogue):**

- **MineralsSparkle** (GitHub zachary-foster) — crystals/giant crystals extractable by skilled miners,
  rarer in extreme biomes. Belongs in the four-axis **Exotic** column (`desert_world_design.md`
  treasure catalogue), not this palette. Flagged there, 1.6 status still to verify if pursued.

**Net result:** the palette's four verified biome mods stand. The new work item is **porting Star
Wars – Biomes to 1.6** (real planet biomes, no rename shortcut). Alien | RimWorld is rejected to keep
the concept clean; everything else is dead, placement-overhaul (conflicts with manual authoring), or
reclassified.
