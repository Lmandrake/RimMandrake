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

**8 families · 24 biomes · 546 plants, all distinct.** 4 biomes carry no flora by design: `IceSheet`, `Lake`, `Ocean`, `SeaIce`.

## A. dayside desert

### `Desert` — 4,648 tiles · -15 … 62 °C (median 24) · plantDensity 0.45

*was 21 inherited plants → now **27** assigned*

| commonality | plant | | mod |
|---:|---|---|---|
| 2.2 | **hardy grass** |  | `AB_HardyGrass` · Alpha Biomes |
| 0.8 | **pincushion cactus** |  | `Plant_PincushionCactus` · Core |
| 0.6 | **agave** |  | `Plant_Agave` · Core |
| 0.6 | **grass** |  | `GRimYellowGrass` · GRiNDTerra Biomes |
| 0.45 | **dandelions** |  | `Plant_DesertDandelion` · ReGrowth 2 |
| 0.35 | **pebble cactus** | 🌳 | `Plant_PebbleCactus` · Biotech |
| 0.35 | **pincushion cactus** |  | `GRimPincushionCactus` · GRiNDTerra Biomes |
| 0.3 | **Cactus** |  | `AreebianCactus` · GRiNDTerra Biomes |
| 0.3 | **pincushion cactus** |  | `GRim1PincushionCactus` · GRiNDTerra Biomes |
| 0.3 | **agave** |  | `GRimAgave` · GRiNDTerra Biomes |
| 0.3 | **wild chak-root plant** |  | `Plant_Chakroot_Wild` · Star Wars Animal Collection (Continued) |
| 0.25 | **brown barrel cactus** |  | `AB_BrownBarrelCactus` · Alpha Biomes |
| 0.25 | **flower cactus** |  | `RG_FlowerCactus` · ReGrowth 2 |
| 0.25 | **wild hubba gourd plant** |  | `Plant_HubbaGourd_Wild` · Star Wars Animal Collection (Continued) |
| 0.24 | **bush** |  | `GRimAgavePlant` · GRiNDTerra Biomes |
| 0.22 | **pebble cactus** | 🌳 | `GRimPebbleCactus` · GRiNDTerra Biomes |
| 0.2 | **pebble cactus** | 🌳 | `GRim1PebbleCactus` · GRiNDTerra Biomes |
| 0.18 | **hoodia cactus** | 🌳 | `VEE_Plant_HoodiaCactus` · Vanilla Landmarks Expanded |
| 0.15 | **Dragoberry tree** |  | `TreeDragoberry` · GRiNDTerra Biomes |
| 0.12 | **saguaro cactus** | 🌳 | `Plant_SaguaroCactus` · Core |
| 0.12 | **aaklac** |  | `AB_Aaklac` · Alpha Biomes |
| 0.1 | **saguaro cactus** | 🌳 | `GRimSaguaroCactus` · GRiNDTerra Biomes |
| 0.1 | **saguaro cactus** | 🌳 | `GRim1SaguaroCactus` · GRiNDTerra Biomes |
| 0.08 | **drago tree** | 🌳 | `Plant_TreeDrago` · Core |
| 0.06 | **dessert tree** | 🌳 | `AB_DessertTree` · Alpha Biomes |
| 0.05 | **hubba gourd** |  | `Plant_HubbaGourd` · Star Wars Animal Collection (Continued) |
| 0.05 | **chak-root plant** |  | `Plant_Chakroot` · Star Wars Animal Collection (Continued) |

### `ExtremeDesert` — 3,214 tiles · 16 … 66 °C (median 48) · plantDensity 0.008 🔴 **`plantDensity` is near zero — this roster will almost never be seen**

*was 25 inherited plants → now **9** assigned*

| commonality | plant | | mod |
|---:|---|---|---|
| 0.3 | **euphorbia rimworldia** |  | `AB_EuphorbiaRimworldia` · Alpha Biomes |
| 0.25 | **pincushion plant** |  | `VCE_Plant_PincushionPlant` · Vanilla Plants Expanded - Succulents |
| 0.2 | **gargantuan lithops** |  | `AB_GargantuanLithops` · Alpha Biomes |
| 0.1 | **bloddle plant** |  | `Plant_Bloddle` · Star Wars Animal Collection (Continued) |
| 0.06 | **euphorbia desiccata** | 🌳 | `AB_EuphorbiaDesiccata` · Alpha Biomes |
| 0.05 | **dead bower tree** | 🌳 | `AB_DeadBowerTree` · Alpha Biomes |
| 0.04 | **dead tree** | 🌳 | `TreeDead` · Advanced Biomes (Continued) |
| 0.04 | **Dead tree** | 🌳 | `GRimTreeDead` · GRiNDTerra Biomes |
| 0.04 | **giant stikehr** |  | `AB_GiantStikehr` · Alpha Biomes |

### `AridShrubland` — 709 tiles · -15 … 60 °C (median 26) · plantDensity 0.72

*was 23 inherited plants → now **61** assigned*

| commonality | plant | | mod |
|---:|---|---|---|
| 1.4 | **low shrubs** |  | `Plant_ShrubLow` · Core |
| 0.7 | **gorse** |  | `VEE_Gorse` · Vanilla Landmarks Expanded |
| 0.7 | **grass** |  | `RG_Plant_AridGrass` · ReGrowth 2 |
| 0.6 | **heather** |  | `VEE_Heather` · Vanilla Landmarks Expanded |
| 0.5 | **juniper bush** |  | `VEE_Plant_JuniperBush` · Vanilla Landmarks Expanded |
| 0.4 | **low shrubs** |  | `GRim1ShrubLow` · GRiNDTerra Biomes |
| 0.4 | **low shrubs** |  | `GRim2ShrubLow` · GRiNDTerra Biomes |
| 0.4 | **low shrubs** |  | `GRimShrubLow` · GRiNDTerra Biomes |
| 0.35 | **bush** |  | `GRim1Bush` · GRiNDTerra Biomes |
| 0.35 | **bush** |  | `GRim2Bush` · GRiNDTerra Biomes |
| 0.35 | **bush** |  | `GRimBush` · GRiNDTerra Biomes |
| 0.3 | **ripthorn** |  | `Plant_Ripthorn` · Biotech |
| 0.3 | **bush** |  | `GRim3Bush` · GRiNDTerra Biomes |
| 0.3 | **bush** |  | `GRim4Bush` · GRiNDTerra Biomes |
| 0.3 | **bush** |  | `AreebianBush` · GRiNDTerra Biomes |
| 0.3 | **bush** |  | `Plant_Bush` · Core |
| 0.3 | **brambles** |  | `Plant_Brambles` · ReGrowth 2 |
| 0.3 | **knapweed** |  | `VEE_Knapweed` · Vanilla Landmarks Expanded |
| 0.3 | **loosestrife** |  | `VEE_Loosestrife` · Vanilla Landmarks Expanded |
| 0.28 | **bush** |  | `GRim1BushPoplar` · GRiNDTerra Biomes |
| 0.28 | **bush** |  | `GRim2BushPoplar` · GRiNDTerra Biomes |
| 0.28 | **bush** |  | `GRimBushPoplar` · GRiNDTerra Biomes |
| 0.25 | **wild healroot** |  | `Plant_HealrootWild` · Core |
| 0.25 | **bush** |  | `BushDandys` · GRiNDTerra Biomes |
| 0.25 | **bush** |  | `Grim3Shrub` · GRiNDTerra Biomes |
| 0.25 | **bush** |  | `NewGreenBush` · GRiNDTerra Biomes |
| 0.25 | **brambles** |  | `RG_Plant_BramblesRed` · ReGrowth 2 |
| 0.25 | **brambles** |  | `RG_Plant_BramblesYellow` · ReGrowth 2 |
| 0.25 | **brambles** |  | `GRimBrambles` · GRiNDTerra Biomes |
| 0.25 | **buttercup** |  | `VEE_ButtercupFlower` · Vanilla Landmarks Expanded |
| 0.25 | **forget-me-not** |  | `VEE_ForgetMeNot` · Vanilla Landmarks Expanded |
| 0.25 | **oxalis** |  | `RG_Plant_Oxalis` · ReGrowth 2 |
| 0.25 | **astragalus** |  | `Plant_Astragalus` · Core |
| 0.25 | **juniper shrub** |  | `IronScruff_Juniper` · Primordial Geysers |
| 0.24 | **brambles** |  | `Plant_Brambles_Leafless` · Odyssey |
| 0.24 | **bush** |  | `Plant_Bush_Leafless` · Odyssey |
| 0.22 | **wild muja fruit bush** |  | `Plant_MujaFruit_Wild` · Star Wars Animal Collection (Continued) |
| 0.22 | **wild nysyllin plant** |  | `Plant_Nysyllin_Wild` · Star Wars Animal Collection (Continued) |
| 0.2 | **dervish** |  | `RG_Plant_Dervish` · ReGrowth 2 |
| 0.2 | **creep stern** |  | `RG_Plant_CreepStern` · ReGrowth 2 |
| 0.2 | **crimson cushion** |  | `RG_Plant_CrimsonCushion` · ReGrowth 2 |
| 0.2 | **lupine** |  | `RG_Plant_LupineIceland` · ReGrowth 2 |
| 0.2 | **clivia** |  | `Plant_Clivia` · Core |
| 0.2 | **daylily** |  | `Plant_Daylily` · Core |
| 0.2 | **berry bush** |  | `Plant_Berry` · Core |
| 0.2 | **healroot** |  | `Plant_Healroot` · Core |
| 0.18 | **tiger lily** |  | `RG_Plant_TigerLily` · ReGrowth 2 |
| 0.18 | **Cyprivia** |  | `GRimClivia` · GRiNDTerra Biomes |
| 0.18 | **berry bush** |  | `GRimBerryBush` · GRiNDTerra Biomes |
| 0.16 | **daylily** |  | `ZBiome_Plant_WildDaylily` · More Vanilla Biomes |
| 0.16 | **berry bush** |  | `Plant_Berry_Leafless` · Odyssey |
| 0.15 | **rose** |  | `Plant_Rose` · Core |
| 0.15 | **plumeria** |  | `RG_Plant_Plumeria` · ReGrowth 2 |
| 0.15 | **berry bush** |  | `GRim1BerryBush` · GRiNDTerra Biomes |
| 0.15 | **berry bush** |  | `GRim2BerryBush` · GRiNDTerra Biomes |
| 0.15 | **berry bush** |  | `GRim3BerryBush` · GRiNDTerra Biomes |
| 0.15 | **berry bush** |  | `GRim4BerryBush` · GRiNDTerra Biomes |
| 0.15 | **berry bush** |  | `GRim5BerryBush` · GRiNDTerra Biomes |
| 0.12 | **rose** |  | `ZBiome_Plant_WildRose` · More Vanilla Biomes |
| 0.05 | **muja fruit bush** |  | `Plant_MujaFruit` · Star Wars Animal Collection (Continued) |
| 0.05 | **nysyllin plant** |  | `Plant_Nysyllin` · Star Wars Animal Collection (Continued) |

### `ZBiome_Badlands` — 545 tiles · -21 … 58 °C (median 27) · plantDensity 0.3

*was 13 inherited plants → now **20** assigned*

| commonality | plant | | mod |
|---:|---|---|---|
| 0.4 | **cholla cactus** | 🌳 | `VEE_Plant_ChollaCactus` · Vanilla Landmarks Expanded |
| 0.4 | **hedgehog cactus** | 🌳 | `VEE_Plant_HedgehogCactus` · Vanilla Landmarks Expanded |
| 0.35 | **beavertail cactus** | 🌳 | `VEE_Plant_BeavertailCactus` · Vanilla Landmarks Expanded |
| 0.3 | **barrel cactus** | 🌳 | `VEE_Plant_BarrelCactus` · Vanilla Landmarks Expanded |
| 0.3 | **ripthorn** |  | `GRim1Ripthorn` · GRiNDTerra Biomes |
| 0.3 | **ripthorn** |  | `GRim2Ripthorn` · GRiNDTerra Biomes |
| 0.3 | **ripthorn** |  | `GRimRipthorn` · GRiNDTerra Biomes |
| 0.28 | **thornvine** |  | `GRim1Thornvine` · GRiNDTerra Biomes |
| 0.28 | **thornvine** |  | `GRim2Thornvine` · GRiNDTerra Biomes |
| 0.28 | **thornvine** |  | `GRimThornvine` · GRiNDTerra Biomes |
| 0.25 | **organ pipe cactus** | 🌳 | `VEE_Plant_OrganPipeCactus` · Vanilla Landmarks Expanded |
| 0.25 | **raven nettle** |  | `AB_RavenNettle` · Alpha Biomes |
| 0.25 | **red bugloss** |  | `AB_RedBugloss` · Alpha Biomes |
| 0.22 | **thornvine** |  | `Plant_Thornvine` · Odyssey |
| 0.2 | **wild psychoid plant** |  | `Plant_Psychoid_Wild` · Odyssey |
| 0.2 | **lure weed** |  | `RG_Plant_LureWeed` · ReGrowth 2 |
| 0.2 | **wild tooke-trap plant** |  | `Plant_TookeTrap_Wild` · Star Wars Animal Collection (Continued) |
| 0.16 | **psychoid plant** |  | `Plant_Psychoid` · Core |
| 0.15 | **mantrap** |  | `BMT_Plant_Mantrap` · Biomes! Polluted Lands |
| 0.05 | **tooke-trap plant** |  | `Plant_TookeTrap` · Star Wars Animal Collection (Continued) |

### `ZBiome_Grasslands` — 233 tiles · 28 … 65 °C (median 50) · plantDensity 0.95

*was 21 inherited plants → now **41** assigned*

| commonality | plant | | mod |
|---:|---|---|---|
| 2.4 | **yellow grass** |  | `Plant_YellowGrass` · Odyssey |
| 2.0 | **tall yellow grass** |  | `Plant_YellowTallGrass` · Odyssey |
| 0.8 | **grass** |  | `Plant_Grass` · ReGrowth 2 |
| 0.7 | **tall grass** |  | `Plant_TallGrass` · ReGrowth 2 |
| 0.5 | **haygrass** |  | `Plant_Haygrass` · Core |
| 0.5 | **grass** |  | `GRimBlackGrass` · GRiNDTerra Biomes |
| 0.5 | **grass** |  | `GRimBlueGrass` · GRiNDTerra Biomes |
| 0.5 | **grass** |  | `GRimGreenGrass` · GRiNDTerra Biomes |
| 0.5 | **grass** |  | `GRimNavyGrass` · GRiNDTerra Biomes |
| 0.5 | **grass** |  | `GRimOrangeGrass` · GRiNDTerra Biomes |
| 0.5 | **grass** |  | `GRimPurpleGrass` · GRiNDTerra Biomes |
| 0.5 | **grass** |  | `GRimRedGrass` · GRiNDTerra Biomes |
| 0.5 | **grass** |  | `GRimTealGrass` · GRiNDTerra Biomes |
| 0.5 | **tall grass** |  | `PlantTallYellowGrass` · Advanced Biomes (Continued) |
| 0.45 | **grass** |  | `DandyGrass` · GRiNDTerra Biomes |
| 0.4 | **tall grass** |  | `GRimBlackTallGrass` · GRiNDTerra Biomes |
| 0.4 | **tall grass** |  | `GRimBlueTallGrass` · GRiNDTerra Biomes |
| 0.4 | **tall grass** |  | `GRimGreenTallGrass` · GRiNDTerra Biomes |
| 0.4 | **tall grass** |  | `GRimNavyTallGrass` · GRiNDTerra Biomes |
| 0.4 | **tall grass** |  | `GRimOrangeTallGrass` · GRiNDTerra Biomes |
| 0.4 | **tall grass** |  | `GRimPurpleTallGrass` · GRiNDTerra Biomes |
| 0.4 | **tall grass** |  | `GRimRedTallGrass` · GRiNDTerra Biomes |
| 0.4 | **tall grass** |  | `GRimTealTallGrass` · GRiNDTerra Biomes |
| 0.4 | **tall grass** |  | `GRimYellowTallGrass` · GRiNDTerra Biomes |
| 0.4 | **tall grass** |  | `DandyTallGrass` · GRiNDTerra Biomes |
| 0.35 | **flowers** |  | `Dandys` · GRiNDTerra Biomes |
| 0.35 | **dandelions** |  | `Plant_Dandelion` · Core |
| 0.3 | **wild tinctoria** |  | `Plant_Tinctoria_Wild` · Odyssey |
| 0.3 | **wild cotton plant** |  | `Plant_Cotton_Wild` · Odyssey |
| 0.3 | **bush** |  | `SavannaBush` · Advanced Biomes (Continued) |
| 0.25 | **dandelions** |  | `RG_Plant_BlueDandelion` · ReGrowth 2 |
| 0.25 | **dandelions** |  | `RG_Plant_RedDandelion` · ReGrowth 2 |
| 0.24 | **cotton plant** |  | `Plant_Cotton` · Core |
| 0.24 | **tinctoria** |  | `Plant_Tinctoria` · Core |
| 0.2 | **wild dantuber plant** |  | `Plant_Dantuber_Wild` · Star Wars Animal Collection (Continued) |
| 0.1 | **corn plant** |  | `Plant_Corn` · Core |
| 0.1 | **potato plant** |  | `Plant_Potato` · Core |
| 0.1 | **acacia tree** | 🌳 | `SavannaTreeAcacia` · Advanced Biomes (Continued) |
| 0.08 | **rice plant** |  | `Plant_Rice` · Core |
| 0.06 | **baobab tree** | 🌳 | `SavannaTreeBaobab` · Advanced Biomes (Continued) |
| 0.05 | **dantuber plant** |  | `Plant_Dantuber` · Star Wars Animal Collection (Continued) |

### `ZBiome_DesertOasis` — 227 tiles · 18 … 64 °C (median 35) · plantDensity 0.7

*was 27 inherited plants → now **36** assigned*

| commonality | plant | | mod |
|---:|---|---|---|
| 1.2 | **reeds** |  | `Plant_Reeds` · Odyssey |
| 1.0 | **bulrush** |  | `Plant_Bulrush` · Odyssey |
| 0.6 | **alocasia** |  | `Plant_Alocasia` · Core |
| 0.6 | **reeds** |  | `GRimReeds` · GRiNDTerra Biomes |
| 0.6 | **reeds** |  | `GRim1Reeds` · GRiNDTerra Biomes |
| 0.55 | **bulrush** |  | `GRimBulrush` · GRiNDTerra Biomes |
| 0.35 | **date palm** | 🌳 | `VEE_Plant_DatePalm` · Vanilla Landmarks Expanded |
| 0.35 | **alocasia** |  | `GRim1Alocasia` · GRiNDTerra Biomes |
| 0.35 | **alocasia** |  | `GRim2Alocasia` · GRiNDTerra Biomes |
| 0.35 | **alocasia** |  | `GRimAlocasia` · GRiNDTerra Biomes |
| 0.3 | **fan palm** | 🌳 | `AB_FanPalm` · Alpha Biomes |
| 0.2 | **wild smokeleaf plant** |  | `Plant_Smokeleaf_Wild` · Odyssey |
| 0.2 | **Palma tree** | 🌳 | `TreePalma` · GRiNDTerra Biomes |
| 0.2 | **tidalis** |  | `RG_Plant_Tidalis` · ReGrowth 2 |
| 0.18 | **rat palm tree** | 🌳 | `GRim1RatPalm` · GRiNDTerra Biomes |
| 0.18 | **rat palm tree** | 🌳 | `GRim2RatPalm` · GRiNDTerra Biomes |
| 0.18 | **rat palm tree** | 🌳 | `GRimRatPalm` · GRiNDTerra Biomes |
| 0.18 | **rat palm tree** | 🌳 | `Plant_RatPalm` · Biotech |
| 0.18 | **wild jogan tree** | 🌳 | `Plant_JoganTree_Wild` · Star Wars Animal Collection (Continued) |
| 0.18 | **wild meiloorun plant** |  | `Plant_Meiloorun_Wild` · Star Wars Animal Collection (Continued) |
| 0.16 | **smokeleaf plant** |  | `Plant_Smokeleaf` · Core |
| 0.15 | **palm tree** | 🌳 | `RG_Plant_TallPalmTree` · ReGrowth 2 |
| 0.15 | **dwarf palm tree** | 🌳 | `RG_Plant_TreeDwarfPalm` · ReGrowth 2 |
| 0.15 | **palm tree** | 🌳 | `Plant_TreePalm` · Core |
| 0.15 | **wild hydenock tree** | 🌳 | `Plant_HydenockTree_Wild` · Star Wars Animal Collection (Continued) |
| 0.15 | **raspberry bush** |  | `RG_Plant_Raspberry` · ReGrowth 2 |
| 0.12 | **ambrosia bush** |  | `Plant_Ambrosia` · Core |
| 0.12 | **screw pine** | 🌳 | `VEE_Plant_ScrewPine` · Vanilla Landmarks Expanded |
| 0.12 | **hop plant** |  | `Plant_Hops` · Core |
| 0.1 | **giant rafflesia** |  | `Plant_Rafflesia` · Core |
| 0.1 | **strawberry plant** |  | `Plant_Strawberry` · Core |
| 0.1 | **ambrosia bush** |  | `Plant_MotherAmbrosiaLGE` · Go Explore! |
| 0.08 | **wild strawberry plant** |  | `Plant_Strawberry_Wild` · Odyssey |
| 0.05 | **jogan tree** | 🌳 | `Plant_JoganTree` · Star Wars Animal Collection (Continued) |
| 0.05 | **meiloorun plant** |  | `Plant_Meiloorun` · Star Wars Animal Collection (Continued) |
| 0.04 | **hydenock tree** | 🌳 | `Plant_HydenockTree` · Star Wars Animal Collection (Continued) |

## B. contamination

### `Wasteland` — 1,721 tiles · -45 … 54 °C (median 1) · plantDensity 0.01 🔴 **`plantDensity` is near zero — this roster will almost never be seen**

*was 9 inherited plants → now **37** assigned*

| commonality | plant | | mod |
|---:|---|---|---|
| 2.0 | **toxigrass** |  | `RG_Plant_ToxiGrass` · ReGrowth 2 |
| 1.2 | **tall toxigrass** |  | `RG_Plant_TallToxiGrass` · ReGrowth 2 |
| 0.6 | **gutter plantain** |  | `BMT_Plant_GutterPlantain` · Biomes! Polluted Lands |
| 0.6 | **toxi grass** |  | `AB_ToxiGrass` · Alpha Biomes |
| 0.5 | **toxic ivy** |  | `BMT_Plant_ToxicIvy` · Biomes! Polluted Lands |
| 0.5 | **twisted dandelion** |  | `BMT_Plant_TwistedDandelion` · Biomes! Polluted Lands |
| 0.5 | **tall grass** |  | `PoisonPlantTallGrass` · Advanced Biomes (Continued) |
| 0.35 | **poison shrub** |  | `PoisonShrub` · Advanced Biomes (Continued) |
| 0.3 | **scorched stars** |  | `BMT_Plant_ScorchedStars` · Biomes! Polluted Lands |
| 0.3 | **poison alocasia** |  | `PoisonAlocasia` · Advanced Biomes (Continued) |
| 0.3 | **poison brambles** |  | `PoisonBrambles` · Advanced Biomes (Continued) |
| 0.3 | **bush** |  | `PoisonPlantBush` · Advanced Biomes (Continued) |
| 0.3 | **dandelions** |  | `PoisonPlantDandelion` · Advanced Biomes (Continued) |
| 0.3 | **grey fern** |  | `BMT_Plant_GreyFern` · Biomes! Polluted Lands |
| 0.25 | **pigs ears** |  | `BMT_Plant_PigsEars` · Biomes! Polluted Lands |
| 0.25 | **pox sorghum** |  | `BMT_Plant_PoxSorghum` · Biomes! Polluted Lands |
| 0.2 | **wild rashroot** |  | `BMT_Plant_WildRashroot` · Biomes! Polluted Lands |
| 0.2 | **wild mushroom** |  | `PoisonMushroom` · Advanced Biomes (Continued) |
| 0.2 | **weeping toxberry** |  | `AB_WeepingToxberry` · Alpha Biomes |
| 0.2 | **cotton cap** |  | `BMT_Plant_CottonCap` · Biomes! Polluted Lands |
| 0.16 | **rashroot** |  | `BMT_Plant_Rashroot` · Biomes! Polluted Lands |
| 0.15 | **doomsprout** |  | `BMT_Plant_Doomsprout` · Biomes! Polluted Lands |
| 0.15 | **raspberry bush** |  | `PoisonPlantRaspberry` · Advanced Biomes (Continued) |
| 0.15 | **rainbow tongue** |  | `BMT_RainbowTongue` · Biomes! Polluted Lands |
| 0.15 | **eclipsus** |  | `BMT_Plant_EclipsusFlower` · Biomes! Polluted Lands |
| 0.15 | **eclipsus** |  | `BMT_Plant_EclipsusLeaves` · Biomes! Polluted Lands |
| 0.12 | **poison rafflesia** |  | `PoisonRafflesia` · Advanced Biomes (Continued) |
| 0.1 | **toxibulb** | 🌳 | `AB_ToxiBulb` · Alpha Biomes |
| 0.1 | **toxipine tree** | 🌳 | `RG_Plant_TreeToxipine` · ReGrowth 2 |
| 0.1 | **toxiteak tree** | 🌳 | `RG_Plant_TreeToxiTeak` · ReGrowth 2 |
| 0.08 | **giant toxic flower** | 🌳 | `AB_GiantToxicFlower` · Alpha Biomes |
| 0.08 | **cecropia tree** | 🌳 | `PoisonPlantTreeCecropia` · Advanced Biomes (Continued) |
| 0.08 | **cypress tree** | 🌳 | `PoisonTreeCypress` · Advanced Biomes (Continued) |
| 0.08 | **palm tree** | 🌳 | `PoisonTreePalm` · Advanced Biomes (Continued) |
| 0.08 | **teak tree** | 🌳 | `PoisonPlantTreeTeak` · Advanced Biomes (Continued) |
| 0.08 | **willow tree** | 🌳 | `PoisonTreeWillow` · Advanced Biomes (Continued) |
| 0.06 | **cypress tree** | 🌳 | `Plant_TreeCypress` · Core |

### `AB_TarPits` — 57 tiles · -6 … 21 °C (median 3) · plantDensity 0.25

*was 10 inherited plants → now **9** assigned*

| commonality | plant | | mod |
|---:|---|---|---|
| 1.5 | **tar puddle** |  | `AB_TarPuddle` · Alpha Biomes |
| 0.3 | **blooming corpse** |  | `BMT_Plant_BloomingCorpse` · Biomes! Polluted Lands |
| 0.2 | **swamp pod** |  | `RG_Plant_SwampPod` · ReGrowth 2 |
| 0.15 | **snake willow** | 🌳 | `BMT_Plant_TreeSnakeWillow` · Biomes! Polluted Lands |
| 0.12 | **seeping eucalyptus** | 🌳 | `BMT_Plant_TreeSeepingEucalyptus` · Biomes! Polluted Lands |
| 0.12 | **crying wolfberry bush** | 🌳 | `BMT_Plant_CryingWolfberryBush` · Biomes! Polluted Lands |
| 0.1 | **polluted stikehr** | 🌳 | `AB_PollutedStikehr` · Alpha Biomes |
| 0.1 | **barbed larch tree** | 🌳 | `BMT_Plant_TreeBarbedLarch` · Biomes! Polluted Lands |
| 0.1 | **clawhand citron** | 🌳 | `BMT_Plant_TreeClawhandCitron` · Biomes! Polluted Lands |

## C. mycoid belt

### `AB_MycoticJungle` — 1,939 tiles · -54 … 24 °C (median -19) · plantDensity 0.2

*was 15 inherited plants → now **35** assigned*

| commonality | plant | | mod |
|---:|---|---|---|
| 1.2 | **agarilux** |  | `AB_Agarilux` · Alpha Biomes |
| 0.6 | **glowing agarilux** |  | `AB_GlowingAgarilux` · Alpha Biomes |
| 0.5 | **agaricus domecap** |  | `AB_AgaricusDomeCap` · Alpha Biomes |
| 0.5 | **grass** |  | `AB_GlowingGrass` · Alpha Biomes |
| 0.4 | **recurved stropharia** |  | `AB_RecurvedStropharia` · Alpha Biomes |
| 0.4 | **slimy pholiota** |  | `AB_SlimyPholiota` · Alpha Biomes |
| 0.4 | **glowstool** |  | `AB_Glowstool` · Alpha Biomes |
| 0.4 | **bryolux** |  | `AB_Bryolux` · Alpha Biomes |
| 0.35 | **witches' oyster** |  | `AB_WitchesOyster` · Alpha Biomes |
| 0.35 | **tinkle grass** |  | `AB_TinkleGrass` · Alpha Biomes |
| 0.3 | **giant agarilux** |  | `AB_GiantAgarilux` · Alpha Biomes |
| 0.3 | **Agarilux Prime** |  | `AB_AgariluxPrime` · Alpha Biomes |
| 0.3 | **flowers** |  | `AB_Flowers` · Alpha Biomes |
| 0.25 | **amethyst land coral fungus** |  | `AB_LandCoral` · Alpha Biomes |
| 0.25 | **gomphoeria** |  | `AB_Gomphoeria` · Alpha Biomes |
| 0.25 | **lilac beacon** |  | `AB_LilacBeacon` · Alpha Biomes |
| 0.25 | **manax fungus** |  | `Plant_ManaxFungus` · Star Wars Animal Collection (Continued) |
| 0.22 | **wild munch-fungus** |  | `Plant_MunchFungus_Wild` · Star Wars Animal Collection (Continued) |
| 0.22 | **wild bubble spore plant** |  | `Plant_Bubblespore_Wild` · Star Wars Animal Collection (Continued) |
| 0.2 | **dribbling cap** |  | `AB_DribblingCap` · Alpha Biomes |
| 0.2 | **arbuscular mycorrhiza** |  | `AB_ArbuscularMycorrhiza` · Alpha Biomes |
| 0.2 | **iashiphus** |  | `AB_Iashiphus` · Alpha Biomes |
| 0.2 | **wild ragadast** |  | `AB_WildRadagast` · Alpha Biomes |
| 0.2 | **sugar famewort** |  | `AB_SugarFamewort` · Alpha Biomes |
| 0.2 | **tangle tea** |  | `AB_TangleTea` · Alpha Biomes |
| 0.15 | **agaritox** | 🌳 | `AB_GiantAgariTox` · Alpha Biomes |
| 0.14 | **wild felucian glowspore** | 🌳 | `Plant_FelucianGlowspore_Wild` · Star Wars Animal Collection (Continued) |
| 0.1 | **devilstrand** |  | `Plant_Devilstrand` · Core |
| 0.08 | **giant septimum** | 🌳 | `AB_GiantSeptimum` · Alpha Biomes |
| 0.08 | **luminescent tree** | 🌳 | `AB_LuminescentTree` · Alpha Biomes |
| 0.06 | **giant sunflower** | 🌳 | `AB_GiantSunflower` · Alpha Biomes |
| 0.06 | **giant tulips** | 🌳 | `AB_GiantTulip` · Alpha Biomes |
| 0.05 | **munch-fungus** |  | `Plant_MunchFungus` · Star Wars Animal Collection (Continued) |
| 0.05 | **bubble spore plant** |  | `Plant_Bubblespore` · Star Wars Animal Collection (Continued) |
| 0.04 | **felucian glowspore** | 🌳 | `Plant_FelucianGlowspore` · Star Wars Animal Collection (Continued) |

### `PoisonForest` — 604 tiles · -52 … 39 °C (median -18) · plantDensity 0.85

*was 19 inherited plants → now **32** assigned*

| commonality | plant | | mod |
|---:|---|---|---|
| 0.8 | **pagan thorns** |  | `BMT_Plant_PaganThorns` · Biomes! Polluted Lands |
| 0.7 | **plague fans** |  | `BMT_Plant_PlagueFans` · Biomes! Polluted Lands |
| 0.6 | **toxcaps** |  | `BMT_Plant_Toxcaps` · Biomes! Polluted Lands |
| 0.5 | **pestia** |  | `BMT_Plant_Pestia` · Biomes! Polluted Lands |
| 0.3 | **weeping hagbloom** |  | `BMT_Plant_WeepingHagbloom` · Biomes! Polluted Lands |
| 0.3 | **Mushrooms** |  | `GrimMush` · GRiNDTerra Biomes |
| 0.3 | **Mushrooms** |  | `GrimShroom` · GRiNDTerra Biomes |
| 0.25 | **mutated fern** |  | `RG_Plant_MutatedFern` · ReGrowth 2 |
| 0.25 | **mutated fungus** |  | `RG_Plant_MutatedFungus` · ReGrowth 2 |
| 0.2 | **pilocap** |  | `GRimPsilocap` · GRiNDTerra Biomes |
| 0.2 | **glow leaf** |  | `RG_Plant_GlowLeaf` · ReGrowth 2 |
| 0.18 | **twisting thornwood** | 🌳 | `BMT_Plant_TreeTwistingThornwood` · Biomes! Polluted Lands |
| 0.15 | **blot birch tree** | 🌳 | `BMT_Plant_TreeBlotBirch` · Biomes! Polluted Lands |
| 0.15 | **light-resistant boomshroom** |  | `VEE_DayBoomshroom` · Vanilla Landmarks Expanded |
| 0.15 | **light-resistant psilocap** |  | `VEE_DayPsilocap` · Vanilla Landmarks Expanded |
| 0.15 | **light-resistant willowgill** |  | `VEE_DayWillowgill` · Vanilla Landmarks Expanded |
| 0.15 | **cathedralis** |  | `RG_Plant_Cathedralis` · ReGrowth 2 |
| 0.12 | **scalped cypress** | 🌳 | `BMT_Plant_TreeScalpedCypress` · Biomes! Polluted Lands |
| 0.12 | **witchwood tree** | 🌳 | `GRim1Witchwood` · GRiNDTerra Biomes |
| 0.12 | **witchwood tree** | 🌳 | `GRim2Witchwood` · GRiNDTerra Biomes |
| 0.12 | **witchwood tree** | 🌳 | `GRimWitchwood` · GRiNDTerra Biomes |
| 0.12 | **snagroot tree** | 🌳 | `GRim1TreeSnagroot` · GRiNDTerra Biomes |
| 0.12 | **snagroot tree** | 🌳 | `GRimTreeSnagroot` · GRiNDTerra Biomes |
| 0.12 | **Mushroom tree** | 🌳 | `Mushpine` · GRiNDTerra Biomes |
| 0.12 | **boomshroom** |  | `Boomshroom` · Odyssey |
| 0.12 | **wild psilocap** |  | `Plant_Psilocap` · Odyssey |
| 0.12 | **willowgill** |  | `Plant_Willowgill` · Odyssey |
| 0.12 | **psilocap** |  | `Plant_Psilocap_Farmed` · Psilocap Cultivation |
| 0.1 | **martyr tree** | 🌳 | `BMT_Plant_TreeMartyr` · Biomes! Polluted Lands |
| 0.1 | **wormoak tree** | 🌳 | `BMT_Plant_TreeWormoak` · Biomes! Polluted Lands |
| 0.1 | **witchwood tree** | 🌳 | `Plant_Witchwood` · Biotech |
| 0.1 | **snagroot tree** | 🌳 | `Plant_TreeSnagroot` · Odyssey |

### `BMT_FungalForest` — 425 tiles · -44 … 24 °C (median -24) · plantDensity 1

*was 27 inherited plants → now **67** assigned*

| commonality | plant | | mod |
|---:|---|---|---|
| 1.0 | **wrinklecap** |  | `BMT_Wrinklecap` · Biomes! Caverns |
| 0.8 | **fibershroom** |  | `BMT_Fibershroom` · Biomes! Caverns |
| 0.6 | **gleamtip** |  | `BMT_Gleamtip` · Biomes! Caverns |
| 0.5 | **chromacap** |  | `BMT_Chromacap` · Biomes! Caverns |
| 0.4 | **greatbulb** |  | `BMT_Greatbulb` · Biomes! Caverns |
| 0.4 | **floor mold** |  | `BMT_FloorMold` · Biomes! Caverns |
| 0.4 | **mycelium** |  | `BMT_Mycelium` · Biomes! Caverns |
| 0.35 | **fungusfern** |  | `BMT_Fungusfern` · Biomes! Caverns |
| 0.35 | **mold fruiting bodies** |  | `BMT_FruitingBodies` · Biomes! Caverns |
| 0.35 | **mycelium** |  | `BMT_CavernMycelium` · Biomes! Caverns |
| 0.3 | **bright wispcap** |  | `BMT_BrightWispcap` · Biomes! Caverns |
| 0.3 | **dark wispcap** |  | `BMT_DarkWispcap` · Biomes! Caverns |
| 0.3 | **chubshroom** |  | `BMT_Chubshroom` · Biomes! Caverns |
| 0.3 | **dewshrooms** |  | `BMT_Dewshrooms` · Biomes! Caverns |
| 0.3 | **tendralus** |  | `BMT_FungalTendril` · Biomes! Caverns |
| 0.25 | **shimbershroom** | 🌳 | `BMT_Shimbershroom` · Biomes! Caverns |
| 0.25 | **baleful bolete** |  | `BMT_BalefulBolete` · Biomes! Caverns |
| 0.25 | **bleeding tooth** |  | `BMT_BleedingTooth` · Biomes! Caverns |
| 0.25 | **carvefungus** |  | `BMT_CarveShroom` · Biomes! Caverns |
| 0.25 | **coral club** |  | `BMT_CoralClub` · Biomes! Caverns |
| 0.25 | **crimson cap** |  | `BMT_CrimsonCap` · Biomes! Caverns |
| 0.25 | **glittercap** |  | `BMT_Glittercap` · Biomes! Caverns |
| 0.25 | **luminous spout** |  | `BMT_LuminousSpout` · Biomes! Caverns |
| 0.25 | **nuitae** |  | `BMT_Nuitae` · Biomes! Caverns |
| 0.25 | **shinebell** |  | `BMT_Brightbell` · Biomes! Caverns |
| 0.25 | **violet wimple** |  | `BMT_VioletWimple` · Biomes! Caverns |
| 0.25 | **watorbs** |  | `BMT_WatOrbs` · Biomes! Caverns |
| 0.25 | **wheelshroom** |  | `BMT_Wheelshroom` · Biomes! Caverns |
| 0.25 | **wrinklecap** |  | `BMT_WrinklecapMarsh` · Biomes! Caverns |
| 0.2 | **poptop** | 🌳 | `BMT_Poptop` · Biomes! Caverns |
| 0.2 | **dish cap** | 🌳 | `BMT_Dishcap` · Biomes! Caverns |
| 0.2 | **giant leaf** |  | `BMT_GiantLeaf` · Biomes! Caverns |
| 0.2 | **glimmering cactus** |  | `BMT_GlowingSucculent` · Biomes! Caverns |
| 0.2 | **nuitae** |  | `BMT_NuitaeMarsh` · Biomes! Caverns |
| 0.2 | **power fungus** |  | `BMT_PowerFungus` · Biomes! Caverns |
| 0.2 | **pusmelon** |  | `BMT_Pusmelon` · Biomes! Caverns |
| 0.2 | **bioluminescence algae** |  | `BMT_BiolumiAlgaeCarnelian` · Biomes! Caverns |
| 0.2 | **bioluminescence algae** |  | `BMT_BiolumiAlgaeChrysoberyl` · Biomes! Caverns |
| 0.2 | **bioluminescence algae** |  | `BMT_BiolumiAlgaeCitrine` · Biomes! Caverns |
| 0.2 | **bioluminescence algae** |  | `BMT_BiolumiAlgaeKunzite` · Biomes! Caverns |
| 0.2 | **bioluminescence algae** |  | `BMT_BiolumiAlgaeTanzanite` · Biomes! Caverns |
| 0.2 | **bioluminescence algae** |  | `BMT_BiolumiAlgaeTurquoise` · Biomes! Caverns |
| 0.2 | **black lily** |  | `BMT_BlackLily` · Biomes! Caverns |
| 0.2 | **Sychi cap** |  | `RG_SychiCap` · ReGrowth 2 |
| 0.2 | **cibarius** |  | `RG_Cibarius` · ReGrowth 2 |
| 0.2 | **neo amanita** |  | `RG_NeoAmanita` · ReGrowth 2 |
| 0.2 | **potokus** |  | `RG_Potokus` · ReGrowth 2 |
| 0.2 | **tripaloski** |  | `RG_Tripaloski` · ReGrowth 2 |
| 0.18 | **shine cap** | 🌳 | `BMT_Shinecap` · Biomes! Caverns |
| 0.15 | **mystic cap** |  | `VEE_Plant_MysticCap` · Vanilla Landmarks Expanded |
| 0.15 | **juice cactus** |  | `BMT_JuiceCactus` · Biomes! Caverns |
| 0.15 | **blooming cactus** |  | `BMT_BloomingCactus` · Biomes! Caverns |
| 0.12 | **bright wisptoll** | 🌳 | `BMT_BrightWisptoll` · Biomes! Caverns |
| 0.12 | **dark wisptoll** | 🌳 | `BMT_DarkWisptoll` · Biomes! Caverns |
| 0.12 | **candlesnuff** | 🌳 | `BMT_Candlesnuff` · Biomes! Caverns |
| 0.12 | **curlbranch** | 🌳 | `BMT_Curlbranch` · Biomes! Caverns |
| 0.12 | **flakespire fungus** | 🌳 | `BMT_FlakespireFungus` · Biomes! Caverns |
| 0.12 | **frigu** | 🌳 | `BMT_Frigu` · Biomes! Caverns |
| 0.12 | **nogtyl** | 🌳 | `BMT_Nogtyl` · Biomes! Caverns |
| 0.12 | **ravelmush** | 🌳 | `BMT_Ravelmush` · Biomes! Caverns |
| 0.12 | **skulltop** | 🌳 | `BMT_Skulltop` · Biomes! Caverns |
| 0.12 | **stink lattice** | 🌳 | `BMT_StinkLattice` · Biomes! Caverns |
| 0.12 | **arpeau** | 🌳 | `BMT_Arpeau` · Biomes! Caverns |
| 0.12 | **arpeau** | 🌳 | `BMT_GreenArpeau` · Biomes! Caverns |
| 0.1 | **exploding angel** | 🌳 | `BMT_ExplodingAngel` · Biomes! Caverns |
| 0.1 | **nogtyl** | 🌳 | `BMT_NogtylMarsh` · Biomes! Caverns |
| 0.1 | **timbershroom** | 🌳 | `Plant_Timbershroom` · Core |

## D. river jungle

### `AB_FeraliskInfestedJungle` — 534 tiles · 36 … 64 °C (median 46) · plantDensity 0.9

*was 13 inherited plants → now **37** assigned*

| commonality | plant | | mod |
|---:|---|---|---|
| 1.8 | **tall slimy grass** |  | `AB_TallSlimyGrass` · Alpha Biomes |
| 0.7 | **green rock fern** |  | `AB_GreenRockFern` · Alpha Biomes |
| 0.4 | **fern** |  | `RG_Plant_TropicalFern` · ReGrowth 2 |
| 0.35 | **ivy** |  | `RG_Plant_TropicalIvy` · ReGrowth 2 |
| 0.35 | **bush** |  | `JungleShrub` · GRiNDTerra Biomes |
| 0.35 | **sword fern** |  | `SwordFern` · Advanced Biomes (Continued) |
| 0.3 | **deep jungle tree** | 🌳 | `AB_JungleTree` · Alpha Biomes |
| 0.3 | **brambles** |  | `RG_Plant_TropicalBrambles` · ReGrowth 2 |
| 0.3 | **chokevine** |  | `RG_Plant_TropicalChokevine` · ReGrowth 2 |
| 0.3 | **chokevine** |  | `Plant_Chokevine` · Core |
| 0.3 | **fern** |  | `RG_Plant_TemperateFern` · ReGrowth 2 |
| 0.3 | **fern** |  | `VEE_Plant_Fern` · Vanilla Landmarks Expanded |
| 0.28 | **ivy** |  | `RG_Plant_TemperateIvy` · ReGrowth 2 |
| 0.25 | **chokevine** |  | `GRim1Chokevine` · GRiNDTerra Biomes |
| 0.25 | **chokevine** |  | `GRim2Chokevine` · GRiNDTerra Biomes |
| 0.25 | **chokevine** |  | `GRim3Chokevine` · GRiNDTerra Biomes |
| 0.25 | **chokevine** |  | `GRimChokevine` · GRiNDTerra Biomes |
| 0.25 | **fern** |  | `RG_Plant_BorealFern` · ReGrowth 2 |
| 0.25 | **bush** |  | `GRim1BambooBush` · GRiNDTerra Biomes |
| 0.25 | **bush** |  | `GRimBambooBush` · GRiNDTerra Biomes |
| 0.15 | **deep jungle polux** | 🌳 | `AB_JungleTree_Polluted` · Alpha Biomes |
| 0.15 | **Grimpepper plant** |  | `GrimPepper` · GRiNDTerra Biomes |
| 0.12 | **keening cordax** | 🌳 | `AB_KeeningCordax` · Alpha Biomes |
| 0.12 | **cecropia tree** | 🌳 | `Plant_TreeCecropia` · Core |
| 0.12 | **bamboo tree** | 🌳 | `Plant_TreeBamboo` · Core |
| 0.1 | **giant mutant hibiscus** | 🌳 | `AB_GiantFlower` · Alpha Biomes |
| 0.1 | **teak tree** | 🌳 | `Plant_TreeTeak` · Core |
| 0.1 | **Areeb tree** | 🌳 | `TreeAreeb` · GRiNDTerra Biomes |
| 0.1 | **Blareebian tree** | 🌳 | `TreeBlareebian` · GRiNDTerra Biomes |
| 0.08 | **redcedar tree** | 🌳 | `TreeCedar` · Advanced Biomes (Continued) |
| 0.08 | **Cypre tree** | 🌳 | `TreeCypre` · GRiNDTerra Biomes |
| 0.08 | **Gralma tree** | 🌳 | `TreeGralma` · GRiNDTerra Biomes |
| 0.08 | **Grimber tree** | 🌳 | `TreeGrimber` · GRiNDTerra Biomes |
| 0.08 | **GRim tree** | 🌳 | `GRimTreePolux` · GRiNDTerra Biomes |
| 0.08 | **cocoa tree** | 🌳 | `Plant_TreeCocoa` · Core |
| 0.06 | **wild cocoa tree** | 🌳 | `Plant_TreeCocoa_Wild` · Odyssey |
| 0.06 | **cocoa bush** |  | `VCE_ChocolateBush` · Vanilla Ideology Expanded - Memes and Structures |

### `AB_MiasmicMangrove` — 65 tiles · 29 … 59 °C (median 41) · plantDensity 0.7

*was 13 inherited plants → now **16** assigned*

| commonality | plant | | mod |
|---:|---|---|---|
| 1.2 | **sewer reed** |  | `BMT_Plant_SewerReed` · Biomes! Polluted Lands |
| 0.4 | **parasitic mangrove** |  | `AB_ParasiticMangrove` · Alpha Biomes |
| 0.35 | **mangrove tree** | 🌳 | `AB_MangroveTree` · Alpha Biomes |
| 0.3 | **mangrove palm** | 🌳 | `AB_MangrovePalm` · Alpha Biomes |
| 0.25 | **Coral** |  | `GrimCoral` · GRiNDTerra Biomes |
| 0.2 | **tangleroot mangrove** | 🌳 | `BMT_Plant_TreeTanglerootMangrove` · Biomes! Polluted Lands |
| 0.2 | **mangrove** | 🌳 | `VEE_Mangrove` · Vanilla Landmarks Expanded |
| 0.15 | **mangrove tree** | 🌳 | `WetlandTreeMangrove` · Advanced Biomes (Continued) |
| 0.15 | **coral coconut tree** |  | `BiomesIslands_CoconutPalm` · Biomes! Core |
| 0.12 | **Coral Tree** |  | `CoralTreeBlack` · GRiNDTerra Biomes |
| 0.12 | **Coral Tree** |  | `CoralTreeBlue` · GRiNDTerra Biomes |
| 0.12 | **Coral Tree** |  | `CoralTreeOrange` · GRiNDTerra Biomes |
| 0.1 | **willow tree** | 🌳 | `GRimTreeWillow` · GRiNDTerra Biomes |
| 0.1 | **willow tree** | 🌳 | `Plant_TreeWillow` · Core |
| 0.1 | **willow tree** | 🌳 | `RG_Plant_TreeWhiteWillow` · ReGrowth 2 |
| 0.08 | **cornish tree** | 🌳 | `RG_Plant_TreeCornish` · ReGrowth 2 |

## E. frozen nightside

### `AB_RockyCrags` — 3,816 tiles · -82 … -0 °C (median -45) · plantDensity 0.085

*was 7 inherited plants → now **26** assigned*

| commonality | plant | | mod |
|---:|---|---|---|
| 0.9 | **frost leaf** |  | `AB_FrostLeaf` · Alpha Biomes |
| 0.6 | **rime nodules** |  | `AB_RimeNodules` · Alpha Biomes |
| 0.45 | **grass** |  | `RG_Plant_TundraGrass` · ReGrowth 2 |
| 0.4 | **rime flower** |  | `BMT_RimeFlower` · Biomes! Caverns |
| 0.4 | **reindeer moss** |  | `BMT_ReindeerMoss` · Biomes! Caverns |
| 0.4 | **moss** |  | `Plant_Moss` · Core |
| 0.35 | **tall grass** |  | `RG_Plant_TundraTallGrass` · ReGrowth 2 |
| 0.35 | **moss** |  | `GRim1Moss` · GRiNDTerra Biomes |
| 0.35 | **moss** |  | `GRim2Moss` · GRiNDTerra Biomes |
| 0.35 | **moss** |  | `GRim3Moss` · GRiNDTerra Biomes |
| 0.35 | **moss** |  | `GRim4Moss` · GRiNDTerra Biomes |
| 0.35 | **moss** |  | `GRimMoss` · GRiNDTerra Biomes |
| 0.3 | **coldheart** |  | `RG_Plant_Coldheart` · ReGrowth 2 |
| 0.25 | **tundra cotton** |  | `RG_Plant_TundraCotton` · ReGrowth 2 |
| 0.25 | **nightguide** |  | `RG_Plant_Nightguide` · ReGrowth 2 |
| 0.1 | **flash frozen tree** |  | `AB_FlashFrozenTree` · Alpha Biomes |
| 0.06 | **pine tree** | 🌳 | `RG_Tree_TundraTreePine` · ReGrowth 2 |
| 0.05 | **gnarled pine tree** | 🌳 | `VEE_Plant_GnarledPine` · Vanilla Landmarks Expanded |
| 0.05 | **gray pine tree** | 🌳 | `GRim1TreeGrayPine` · GRiNDTerra Biomes |
| 0.05 | **gray pine tree** | 🌳 | `GRim2TreeGrayPine` · GRiNDTerra Biomes |
| 0.05 | **gray pine tree** | 🌳 | `GRimTreeGrayPine` · GRiNDTerra Biomes |
| 0.05 | **pine tree** | 🌳 | `Plant_TreePine` · Core |
| 0.05 | **pine tree** | 🌳 | `RG_Plant_BlueTreePine` · ReGrowth 2 |
| 0.05 | **pine tree** | 🌳 | `RG_Plant_LargeTreePine` · ReGrowth 2 |
| 0.05 | **pine tree** | 🌳 | `RG_Plant_OrangeTreePine` · ReGrowth 2 |
| 0.0 | **gray pine tree** | 🌳 | `Plant_TreeGrayPine` · Biotech |

### `AB_PropaneLakes` — 554 tiles · -82 … -49 °C (median -60) · plantDensity 0.75

*was 5 inherited plants → now **6** assigned*

| commonality | plant | | mod |
|---:|---|---|---|
| 0.5 | **crystal flower** |  | `AB_CrystalFlower` · Alpha Biomes |
| 0.45 | **Cave crystals** |  | `CaveCrystal` · GRiNDTerra Biomes |
| 0.4 | **crystal horn** |  | `AB_CrystalHorn` · Alpha Biomes |
| 0.3 | **fast growing crystal** |  | `BMT_Crystal_BlueSowable` · Biomes! Caverns |
| 0.2 | **rime flower** |  | `BMT_RimeFlowerGrowable` · Biomes! Caverns |
| 0.1 | **Crystal tree** | 🌳 | `TreeCrystal` · GRiNDTerra Biomes |

### `HorrorWastes` — 468 tiles · -75 … -34 °C (median -49) · plantDensity 0.5

*was 1 inherited plants → now **7** assigned*

| commonality | plant | | mod |
|---:|---|---|---|
| 1.2 | **horrorweb** |  | `HorrorWeb` · Horrors (Continued) |
| 0.55 | **Tentacle** |  | `Grimtacle` · GRiNDTerra Biomes |
| 0.5 | **blood bouquet** |  | `AB_BloodBouquet` · Alpha Biomes |
| 0.4 | **globular aberration** |  | `AB_GlobularPlant` · Alpha Biomes |
| 0.35 | **tentacular aberration** |  | `AB_TentacularPlant` · Alpha Biomes |
| 0.18 | **polluted globular aberration** | 🌳 | `AB_GlobularPlant_Polluted` · Alpha Biomes |
| 0.12 | **flesh tree** | 🌳 | `AB_FleshTree` · Alpha Biomes |

### `BMT_CrystalCaverns` — 127 tiles · -71 … -54 °C (median -62) · plantDensity 1

*was 12 inherited plants → now **42** assigned*

| commonality | plant | | mod |
|---:|---|---|---|
| 1.0 | **Crystal Small** |  | `CrystalSmall` · GRiNDTerra Biomes |
| 0.8 | **crystaltip brambles** |  | `BMT_CrystaltipBrambles` · Biomes! Caverns |
| 0.6 | **Crystal Shards** |  | `CrystalShard` · GRiNDTerra Biomes |
| 0.35 | **gleamcap** |  | `BMT_Gleamcap` · Biomes! Caverns |
| 0.35 | **glowbulb** |  | `BMT_Glowbulb` · Biomes! Caverns |
| 0.3 | **Crystal Big** |  | `CrystalBig` · GRiNDTerra Biomes |
| 0.3 | **crystalcap** | 🌳 | `BMT_Crystalcap` · Biomes! Caverns |
| 0.3 | **brightbells** |  | `BMT_Brightbells` · Biomes! Caverns |
| 0.3 | **greyfields** |  | `BMT_Greyfields` · Biomes! Caverns |
| 0.3 | **shimmershroom** |  | `BMT_Shimmershroom` · Biomes! Caverns |
| 0.3 | **agarilux** |  | `Agarilux` · Core |
| 0.3 | **bryolux** |  | `Bryolux` · Core |
| 0.3 | **glowstool** |  | `Glowstool` · Core |
| 0.3 | **Caveshrooms** |  | `CaveShroom` · GRiNDTerra Biomes |
| 0.25 | **royal bracket** |  | `BMT_RoyalBracket` · Biomes! Caverns |
| 0.25 | **moonless stripes** |  | `BMT_MoonlessStripesPlant` · Biomes! Caverns |
| 0.25 | **mortal morel** |  | `BMT_MortalMorelPlant` · Biomes! Caverns |
| 0.25 | **starchstalk** |  | `BMT_StarchstalkPlant` · Biomes! Caverns |
| 0.25 | **Fiber shroom** |  | `Plant_Fibershroom` · Core |
| 0.2 | **stimquill** |  | `BMT_Stimquill` · Biomes! Caverns |
| 0.2 | **kessinger** |  | `BMT_KessingerPlant` · Biomes! Caverns |
| 0.2 | **jade glint fungus** |  | `BMT_JadeGlintsCrop` · Biomes! Caverns |
| 0.2 | **dulcis** |  | `BMT_DulcisPlant` · Biomes! Caverns |
| 0.2 | **capscool** |  | `BMT_CapscoolFungus` · Biomes! Caverns |
| 0.2 | **ambrosyx fungus** |  | `BMT_AmbrosyxFungus` · Biomes! Caverns |
| 0.2 | **abyssal grapes** |  | `BMT_AbyssalGrapesVine` · Biomes! Caverns |
| 0.2 | **Cotton shroom** |  | `Plant_Cottonshroom` · Tunneler Expanded |
| 0.2 | **Devil shroom** |  | `Plant_DevilShroom` · Tunneler Expanded |
| 0.2 | **Gold shroom** |  | `Plant_GoldShroom` · Tunneler Expanded |
| 0.2 | **Neutro shroom** |  | `Plant_NeutroShroom` · Tunneler Expanded |
| 0.2 | **Psychoid shroom** |  | `Plant_PsychoidShroom` · Tunneler Expanded |
| 0.2 | **Steel shroom** |  | `Plant_SteelShroom` · Tunneler Expanded |
| 0.2 | **psyshroom** |  | `Plant_Psykshroom` · Psyshrooms |
| 0.2 | **Giant shroom** |  | `Plant_Giantshroom` · Core |
| 0.2 | **Heal shroom** |  | `Plant_Healshroom` · Core |
| 0.2 | **Jelly shroom** |  | `Plant_Jellyshroom` · Core |
| 0.2 | **Meatshroom** |  | `Plant_Meatshroom` · Core |
| 0.2 | **Micro shroom** |  | `Plant_Microshroom` · Core |
| 0.15 | **blastpod shroom** |  | `BMT_Blastpod` · Biomes! Caverns |
| 0.15 | **Grey Lady** |  | `BMT_GreyLady` · Biomes! Caverns |
| 0.15 | **Timbercap** |  | `Plant_Timbercap` · Core |
| 0.15 | **nutrifungus** |  | `Plant_Nutrifungus` · Ideology |

## F. volcanic

### `AB_PyroclasticConflagration` — 31 tiles · 43 … 56 °C (median 50) · plantDensity 0.4

*was 4 inherited plants → now **5** assigned*

| commonality | plant | | mod |
|---:|---|---|---|
| 0.5 | **gamma** |  | `AG_Gamma` · Alpha Genes |
| 0.3 | **giant gamma** |  | `AB_GiantGamma` · Alpha Biomes |
| 0.25 | **septimum** |  | `AG_Septimum` · Alpha Genes |
| 0.2 | **firevine tree** | 🌳 | `AB_FirevineTree` · Alpha Biomes |
| 0.15 | **toxic gamma** | 🌳 | `AB_ToxicGamma` · Alpha Biomes |

### `Volcano` — 23 tiles · 40 … 47 °C (median 42) · plantDensity 0.16

*was 8 inherited plants → now **5** assigned*

| commonality | plant | | mod |
|---:|---|---|---|
| 0.9 | **fireweed** |  | `Plant_Fireweed` · Odyssey |
| 0.72 | **fireweed** |  | `GRim1Fireweed` · GRiNDTerra Biomes |
| 0.6 | **magma cactus** |  | `GRimMagmaCactus` · GRiNDTerra Biomes |
| 0.5 | **fireweed** |  | `GRimFireweed` · GRiNDTerra Biomes |
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

*was 11 inherited plants → now **13** assigned*

| commonality | plant | | mod |
|---:|---|---|---|
| 1.2 | **flowering ocular grass** |  | `AB_EyeGrass` · Alpha Biomes |
| 0.7 | **ocular plant** |  | `AB_RedLeaves` · Alpha Biomes |
| 0.6 | **ocular grass** |  | `AA_AlienGrass` · Alpha Animals |
| 0.5 | **ocular plant** |  | `AB_RedPlantsTall` · Alpha Biomes |
| 0.5 | **ocular grass** |  | `AB_AlienGrass` · Alpha Biomes |
| 0.4 | **ocular tree** | 🌳 | `AB_AlienTree` · Alpha Biomes |
| 0.4 | **ocular plant** |  | `AA_RedLeaves` · Alpha Animals |
| 0.35 | **ocular plant** |  | `AA_RedPlantsTall` · Alpha Animals |
| 0.2 | **mutated ocular tree** | 🌳 | `AB_AlienTree_Polluted` · Alpha Biomes |
| 0.2 | **ocular tree** | 🌳 | `AA_AlienTree` · Alpha Animals |
| 0.2 | **pollen trumpet** |  | `AA_Plant_PollenTrumpet` · Alpha Animals |
| 0.15 | **half transformed ocular tree** | 🌳 | `AB_HalfAlienTree` · Alpha Biomes |
| 0.1 | **heat resistant ambrosia bush** |  | `AA_Heat_Ambrosia` · Alpha Animals |

