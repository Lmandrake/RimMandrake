# Ash'karr's flora — what grows where, and why

> 🔴 **GENERATED** by `design/Jawa/mods/biome_flora.py`. The rosters live in that file's
> `FAMILIES` dict; edit there and regenerate, never here.

**Owner's brief, 2026-08-23, verbatim:** *"distribute the plants per biome… You, agent Decide,
make those calls right now… Try to avoid using the same plant across different biome types.
It's ok to draw from Tinctora, Healroot, and other normally player-grown plants as you
decorate the biomes."*

🔑 **The rule that shapes everything below: no plant appears in two FAMILIES.** Inside one
family a shared plant is kinship; across two it is the zoo effect he objected to. The
generator refuses to build if any plant crosses.

⭐ **His three named favourites all have a home** — `Plant_TreeDrago` in `Desert`,
`BMT_Plant_TreeTwistingThornwood` and `BMT_Plant_TreeMartyr` in `PoisonForest`, where the
rest of the Polluted Lands trees live.

⚠️ **Climate was deliberately NOT a filter.** He ruled *"we can set the appropriate
temperatures later"* — 642 of 669 plants will not grow below 0 °C and half this planet is
colder than that. Making these rosters actually live is `NORMALIZE_TEMPERATURE_TOLERANCES_1`.

**8 families · 24 biomes · 134 plants, all distinct.** 4 biomes carry no flora by design: `IceSheet`, `Lake`, `Ocean`, `SeaIce`.

## A. dayside desert

### `Desert` — 4,648 tiles · -15 … 62 °C (median 24) · plantDensity 0.45

*was 21 inherited plants → now **8** assigned*

| commonality | plant | | mod |
|---:|---|---|---|
| 2.2 | **hardy grass** |  | `AB_HardyGrass` · Alpha Biomes |
| 0.8 | **pincushion cactus** |  | `Plant_PincushionCactus` · Core |
| 0.6 | **agave** |  | `Plant_Agave` · Core |
| 0.45 | **dandelions** |  | `Plant_DesertDandelion` · ReGrowth 2 |
| 0.35 | **pebble cactus** | 🌳 | `Plant_PebbleCactus` · Biotech |
| 0.25 | **brown barrel cactus** |  | `AB_BrownBarrelCactus` · Alpha Biomes |
| 0.12 | **saguaro cactus** | 🌳 | `Plant_SaguaroCactus` · Core |
| 0.08 | **drago tree** | 🌳 | `Plant_TreeDrago` · Core |

### `ExtremeDesert` — 3,214 tiles · 16 … 66 °C (median 48) · plantDensity 0.008 🔴 **`plantDensity` is near zero — this roster will almost never be seen**

*was 25 inherited plants → now **4** assigned*

| commonality | plant | | mod |
|---:|---|---|---|
| 0.3 | **euphorbia rimworldia** |  | `AB_EuphorbiaRimworldia` · Alpha Biomes |
| 0.25 | **pincushion plant** |  | `VCE_Plant_PincushionPlant` · Vanilla Plants Expanded - Succulents |
| 0.2 | **gargantuan lithops** |  | `AB_GargantuanLithops` · Alpha Biomes |
| 0.06 | **euphorbia desiccata** | 🌳 | `AB_EuphorbiaDesiccata` · Alpha Biomes |

### `AridShrubland` — 709 tiles · -15 … 60 °C (median 26) · plantDensity 0.72

*was 23 inherited plants → now **6** assigned*

| commonality | plant | | mod |
|---:|---|---|---|
| 1.4 | **low shrubs** |  | `Plant_ShrubLow` · Core |
| 0.7 | **gorse** |  | `VEE_Gorse` · Vanilla Landmarks Expanded |
| 0.6 | **heather** |  | `VEE_Heather` · Vanilla Landmarks Expanded |
| 0.5 | **juniper bush** |  | `VEE_Plant_JuniperBush` · Vanilla Landmarks Expanded |
| 0.3 | **ripthorn** |  | `Plant_Ripthorn` · Biotech |
| 0.25 | **wild healroot** |  | `Plant_HealrootWild` · Core |

### `ZBiome_Badlands` — 545 tiles · -21 … 58 °C (median 27) · plantDensity 0.3

*was 13 inherited plants → now **6** assigned*

| commonality | plant | | mod |
|---:|---|---|---|
| 0.4 | **cholla cactus** | 🌳 | `VEE_Plant_ChollaCactus` · Vanilla Landmarks Expanded |
| 0.4 | **hedgehog cactus** | 🌳 | `VEE_Plant_HedgehogCactus` · Vanilla Landmarks Expanded |
| 0.35 | **beavertail cactus** | 🌳 | `VEE_Plant_BeavertailCactus` · Vanilla Landmarks Expanded |
| 0.3 | **barrel cactus** | 🌳 | `VEE_Plant_BarrelCactus` · Vanilla Landmarks Expanded |
| 0.25 | **organ pipe cactus** | 🌳 | `VEE_Plant_OrganPipeCactus` · Vanilla Landmarks Expanded |
| 0.2 | **wild psychoid plant** |  | `Plant_Psychoid_Wild` · Odyssey |

### `ZBiome_Grasslands` — 233 tiles · 28 … 65 °C (median 50) · plantDensity 0.95

*was 21 inherited plants → now **5** assigned*

| commonality | plant | | mod |
|---:|---|---|---|
| 2.4 | **yellow grass** |  | `Plant_YellowGrass` · Odyssey |
| 2.0 | **tall yellow grass** |  | `Plant_YellowTallGrass` · Odyssey |
| 0.5 | **haygrass** |  | `Plant_Haygrass` · Core |
| 0.3 | **wild tinctoria** |  | `Plant_Tinctoria_Wild` · Odyssey |
| 0.3 | **wild cotton plant** |  | `Plant_Cotton_Wild` · Odyssey |

### `ZBiome_DesertOasis` — 227 tiles · 18 … 64 °C (median 35) · plantDensity 0.7

*was 27 inherited plants → now **7** assigned*

| commonality | plant | | mod |
|---:|---|---|---|
| 1.2 | **reeds** |  | `Plant_Reeds` · Odyssey |
| 1.0 | **bulrush** |  | `Plant_Bulrush` · Odyssey |
| 0.6 | **alocasia** |  | `Plant_Alocasia` · Core |
| 0.35 | **date palm** | 🌳 | `VEE_Plant_DatePalm` · Vanilla Landmarks Expanded |
| 0.3 | **fan palm** | 🌳 | `AB_FanPalm` · Alpha Biomes |
| 0.2 | **wild smokeleaf plant** |  | `Plant_Smokeleaf_Wild` · Odyssey |
| 0.12 | **ambrosia bush** |  | `Plant_Ambrosia` · Core |

## B. contamination

### `Wasteland` — 1,721 tiles · -45 … 54 °C (median 1) · plantDensity 0.01 🔴 **`plantDensity` is near zero — this roster will almost never be seen**

*was 9 inherited plants → now **8** assigned*

| commonality | plant | | mod |
|---:|---|---|---|
| 2.0 | **toxigrass** |  | `RG_Plant_ToxiGrass` · ReGrowth 2 |
| 1.2 | **tall toxigrass** |  | `RG_Plant_TallToxiGrass` · ReGrowth 2 |
| 0.6 | **gutter plantain** |  | `BMT_Plant_GutterPlantain` · Biomes! Polluted Lands |
| 0.5 | **toxic ivy** |  | `BMT_Plant_ToxicIvy` · Biomes! Polluted Lands |
| 0.5 | **twisted dandelion** |  | `BMT_Plant_TwistedDandelion` · Biomes! Polluted Lands |
| 0.3 | **scorched stars** |  | `BMT_Plant_ScorchedStars` · Biomes! Polluted Lands |
| 0.2 | **wild rashroot** |  | `BMT_Plant_WildRashroot` · Biomes! Polluted Lands |
| 0.15 | **doomsprout** |  | `BMT_Plant_Doomsprout` · Biomes! Polluted Lands |

### `AB_TarPits` — 57 tiles · -6 … 21 °C (median 3) · plantDensity 0.25

*was 10 inherited plants → now **4** assigned*

| commonality | plant | | mod |
|---:|---|---|---|
| 1.5 | **tar puddle** |  | `AB_TarPuddle` · Alpha Biomes |
| 0.3 | **blooming corpse** |  | `BMT_Plant_BloomingCorpse` · Biomes! Polluted Lands |
| 0.15 | **snake willow** | 🌳 | `BMT_Plant_TreeSnakeWillow` · Biomes! Polluted Lands |
| 0.12 | **seeping eucalyptus** | 🌳 | `BMT_Plant_TreeSeepingEucalyptus` · Biomes! Polluted Lands |

## C. mycoid belt

### `AB_MycoticJungle` — 1,939 tiles · -54 … 24 °C (median -19) · plantDensity 0.2

*was 15 inherited plants → now **10** assigned*

| commonality | plant | | mod |
|---:|---|---|---|
| 1.2 | **agarilux** |  | `AB_Agarilux` · Alpha Biomes |
| 0.6 | **glowing agarilux** |  | `AB_GlowingAgarilux` · Alpha Biomes |
| 0.5 | **agaricus domecap** |  | `AB_AgaricusDomeCap` · Alpha Biomes |
| 0.4 | **recurved stropharia** |  | `AB_RecurvedStropharia` · Alpha Biomes |
| 0.4 | **slimy pholiota** |  | `AB_SlimyPholiota` · Alpha Biomes |
| 0.35 | **witches' oyster** |  | `AB_WitchesOyster` · Alpha Biomes |
| 0.3 | **giant agarilux** |  | `AB_GiantAgarilux` · Alpha Biomes |
| 0.2 | **dribbling cap** |  | `AB_DribblingCap` · Alpha Biomes |
| 0.15 | **agaritox** | 🌳 | `AB_GiantAgariTox` · Alpha Biomes |
| 0.1 | **devilstrand** |  | `Plant_Devilstrand` · Core |

### `PoisonForest` — 604 tiles · -52 … 39 °C (median -18) · plantDensity 0.85

*was 19 inherited plants → now **10** assigned*

| commonality | plant | | mod |
|---:|---|---|---|
| 0.8 | **pagan thorns** |  | `BMT_Plant_PaganThorns` · Biomes! Polluted Lands |
| 0.7 | **plague fans** |  | `BMT_Plant_PlagueFans` · Biomes! Polluted Lands |
| 0.6 | **toxcaps** |  | `BMT_Plant_Toxcaps` · Biomes! Polluted Lands |
| 0.5 | **pestia** |  | `BMT_Plant_Pestia` · Biomes! Polluted Lands |
| 0.3 | **weeping hagbloom** |  | `BMT_Plant_WeepingHagbloom` · Biomes! Polluted Lands |
| 0.18 | **twisting thornwood** | 🌳 | `BMT_Plant_TreeTwistingThornwood` · Biomes! Polluted Lands |
| 0.15 | **blot birch tree** | 🌳 | `BMT_Plant_TreeBlotBirch` · Biomes! Polluted Lands |
| 0.12 | **scalped cypress** | 🌳 | `BMT_Plant_TreeScalpedCypress` · Biomes! Polluted Lands |
| 0.1 | **martyr tree** | 🌳 | `BMT_Plant_TreeMartyr` · Biomes! Polluted Lands |
| 0.1 | **wormoak tree** | 🌳 | `BMT_Plant_TreeWormoak` · Biomes! Polluted Lands |

### `BMT_FungalForest` — 425 tiles · -44 … 24 °C (median -24) · plantDensity 1

*was 27 inherited plants → now **9** assigned*

| commonality | plant | | mod |
|---:|---|---|---|
| 1.0 | **wrinklecap** |  | `BMT_Wrinklecap` · Biomes! Caverns |
| 0.8 | **fibershroom** |  | `BMT_Fibershroom` · Biomes! Caverns |
| 0.6 | **gleamtip** |  | `BMT_Gleamtip` · Biomes! Caverns |
| 0.5 | **chromacap** |  | `BMT_Chromacap` · Biomes! Caverns |
| 0.4 | **greatbulb** |  | `BMT_Greatbulb` · Biomes! Caverns |
| 0.25 | **shimbershroom** | 🌳 | `BMT_Shimbershroom` · Biomes! Caverns |
| 0.2 | **poptop** | 🌳 | `BMT_Poptop` · Biomes! Caverns |
| 0.2 | **dish cap** | 🌳 | `BMT_Dishcap` · Biomes! Caverns |
| 0.18 | **shine cap** | 🌳 | `BMT_Shinecap` · Biomes! Caverns |

## D. river jungle

### `AB_FeraliskInfestedJungle` — 534 tiles · 36 … 64 °C (median 46) · plantDensity 0.9

*was 13 inherited plants → now **6** assigned*

| commonality | plant | | mod |
|---:|---|---|---|
| 1.8 | **tall slimy grass** |  | `AB_TallSlimyGrass` · Alpha Biomes |
| 0.7 | **green rock fern** |  | `AB_GreenRockFern` · Alpha Biomes |
| 0.3 | **deep jungle tree** | 🌳 | `AB_JungleTree` · Alpha Biomes |
| 0.15 | **deep jungle polux** | 🌳 | `AB_JungleTree_Polluted` · Alpha Biomes |
| 0.12 | **keening cordax** | 🌳 | `AB_KeeningCordax` · Alpha Biomes |
| 0.1 | **giant mutant hibiscus** | 🌳 | `AB_GiantFlower` · Alpha Biomes |

### `AB_MiasmicMangrove` — 65 tiles · 29 … 59 °C (median 41) · plantDensity 0.7

*was 13 inherited plants → now **6** assigned*

| commonality | plant | | mod |
|---:|---|---|---|
| 1.2 | **sewer reed** |  | `BMT_Plant_SewerReed` · Biomes! Polluted Lands |
| 0.4 | **parasitic mangrove** |  | `AB_ParasiticMangrove` · Alpha Biomes |
| 0.35 | **mangrove tree** | 🌳 | `AB_MangroveTree` · Alpha Biomes |
| 0.3 | **mangrove palm** | 🌳 | `AB_MangrovePalm` · Alpha Biomes |
| 0.2 | **tangleroot mangrove** | 🌳 | `BMT_Plant_TreeTanglerootMangrove` · Biomes! Polluted Lands |
| 0.2 | **mangrove** | 🌳 | `VEE_Mangrove` · Vanilla Landmarks Expanded |

## E. frozen nightside

### `AB_RockyCrags` — 3,816 tiles · -82 … -0 °C (median -45) · plantDensity 0.085

*was 7 inherited plants → now **4** assigned*

| commonality | plant | | mod |
|---:|---|---|---|
| 0.9 | **frost leaf** |  | `AB_FrostLeaf` · Alpha Biomes |
| 0.6 | **rime nodules** |  | `AB_RimeNodules` · Alpha Biomes |
| 0.4 | **rime flower** |  | `BMT_RimeFlower` · Biomes! Caverns |
| 0.1 | **flash frozen tree** |  | `AB_FlashFrozenTree` · Alpha Biomes |

### `AB_PropaneLakes` — 554 tiles · -82 … -49 °C (median -60) · plantDensity 0.75

*was 5 inherited plants → now **3** assigned*

| commonality | plant | | mod |
|---:|---|---|---|
| 0.5 | **crystal flower** |  | `AB_CrystalFlower` · Alpha Biomes |
| 0.4 | **crystal horn** |  | `AB_CrystalHorn` · Alpha Biomes |
| 0.3 | **fast growing crystal** |  | `BMT_Crystal_BlueSowable` · Biomes! Caverns |

### `HorrorWastes` — 468 tiles · -75 … -34 °C (median -49) · plantDensity 0.5

*was 1 inherited plants → now **5** assigned*

| commonality | plant | | mod |
|---:|---|---|---|
| 1.2 | **horrorweb** |  | `HorrorWeb` · Horrors (Continued) |
| 0.5 | **blood bouquet** |  | `AB_BloodBouquet` · Alpha Biomes |
| 0.4 | **globular aberration** |  | `AB_GlobularPlant` · Alpha Biomes |
| 0.35 | **tentacular aberration** |  | `AB_TentacularPlant` · Alpha Biomes |
| 0.12 | **flesh tree** | 🌳 | `AB_FleshTree` · Alpha Biomes |

### `BMT_CrystalCaverns` — 127 tiles · -71 … -54 °C (median -62) · plantDensity 1

*was 12 inherited plants → now **5** assigned*

| commonality | plant | | mod |
|---:|---|---|---|
| 1.0 | **Crystal Small** |  | `CrystalSmall` · GRiNDTerra Biomes |
| 0.8 | **crystaltip brambles** |  | `BMT_CrystaltipBrambles` · Biomes! Caverns |
| 0.6 | **Crystal Shards** |  | `CrystalShard` · GRiNDTerra Biomes |
| 0.3 | **Crystal Big** |  | `CrystalBig` · GRiNDTerra Biomes |
| 0.3 | **crystalcap** | 🌳 | `BMT_Crystalcap` · Biomes! Caverns |

## F. volcanic

### `AB_PyroclasticConflagration` — 31 tiles · 43 … 56 °C (median 50) · plantDensity 0.4

*was 4 inherited plants → now **4** assigned*

| commonality | plant | | mod |
|---:|---|---|---|
| 0.5 | **gamma** |  | `AG_Gamma` · Alpha Genes |
| 0.3 | **giant gamma** |  | `AB_GiantGamma` · Alpha Biomes |
| 0.2 | **firevine tree** | 🌳 | `AB_FirevineTree` · Alpha Biomes |
| 0.15 | **toxic gamma** | 🌳 | `AB_ToxicGamma` · Alpha Biomes |

### `Volcano` — 23 tiles · 40 … 47 °C (median 42) · plantDensity 0.16

*was 8 inherited plants → now **3** assigned*

| commonality | plant | | mod |
|---:|---|---|---|
| 0.9 | **fireweed** |  | `Plant_Fireweed` · Odyssey |
| 0.6 | **magma cactus** |  | `GRimMagmaCactus` · GRiNDTerra Biomes |
| 0.4 | **sagecrust** |  | `BMT_Sagecrust` · Biomes! Caverns |

### `LavaField` — 15 tiles · 38 … 47 °C (median 42) · plantDensity 0.5

*was 12 inherited plants → now **3** assigned*

| commonality | plant | | mod |
|---:|---|---|---|
| 0.7 | **magma cactus** |  | `Plant_MagmaCactus` · Odyssey |
| 0.6 | **fire lavender** |  | `BMT_FireLavender` · Biomes! Caverns |
| 0.2 | **heatsink fungus** | 🌳 | `BMT_HeatsinkFungus` · Biomes! Caverns |

## G. machine and scar

### `AB_MechanoidIntrusion` — 236 tiles · 58 … 66 °C (median 62) · plantDensity 0.2

*was 2 inherited plants → now **4** assigned*

| commonality | plant | | mod |
|---:|---|---|---|
| 0.3 | **voltaic fungus** | 🌳 | `BMT_VoltaicFungus` · Biomes! Caverns |
| 0.15 | **techno tree** | 🌳 | `AB_TechnoTree` · Alpha Biomes |
| 0.12 | **sessile mechanoid tree** | 🌳 | `AB_SessileMechanoid` · Alpha Biomes |
| 0.08 | **golden cube tree** | 🌳 | `AB_GoldenCubeTree` · Alpha Biomes |

### `Scarlands` — 90 tiles · 58 … 66 °C (median 59) · plantDensity 0.4

*was 16 inherited plants → now **4** assigned*

| commonality | plant | | mod |
|---:|---|---|---|
| 0.8 | **rustpuff** |  | `BMT_RustPuff` · Biomes! Caverns |
| 0.6 | **burned shroom** |  | `BMT_BurnedMushroom` · Biomes! Caverns |
| 0.4 | **dark gamma** |  | `AG_DarkGamma` · Alpha Genes |
| 0.2 | **burned stump** |  | `BurnedTree` · Core |

## H. alien

### `AB_GelatinousSuperorganism` — 96 tiles · -3 … 22 °C (median 13) · plantDensity 0.2

*was 7 inherited plants → now **4** assigned*

| commonality | plant | | mod |
|---:|---|---|---|
| 0.9 | **slimy fern** |  | `AB_SlimyFern` · Alpha Biomes |
| 0.6 | **slimecasia** |  | `AB_Slimecasia` · Alpha Biomes |
| 0.3 | **slimy tree** |  | `AB_SlimyTree` · Alpha Biomes |
| 0.2 | **large slimy tree** |  | `AB_LargeSlimyTree` · Alpha Biomes |

### `AB_OcularForest` — 3 tiles · 23 … 23 °C (median 23) · plantDensity 0.35

*was 11 inherited plants → now **6** assigned*

| commonality | plant | | mod |
|---:|---|---|---|
| 1.2 | **flowering ocular grass** |  | `AB_EyeGrass` · Alpha Biomes |
| 0.7 | **ocular plant** |  | `AB_RedLeaves` · Alpha Biomes |
| 0.5 | **ocular plant** |  | `AB_RedPlantsTall` · Alpha Biomes |
| 0.4 | **ocular tree** | 🌳 | `AB_AlienTree` · Alpha Biomes |
| 0.2 | **mutated ocular tree** | 🌳 | `AB_AlienTree_Polluted` · Alpha Biomes |
| 0.15 | **half transformed ocular tree** | 🌳 | `AB_HalfAlienTree` · Alpha Biomes |

