# Ash'karr's flora — what grows where, and why

> 🔴 **GENERATED** by `design/Jawa/mods/biome_flora.py --doc`. The rosters live in that
> file's `FAMILIES` dict; edit there and regenerate, never here.

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

⛔ **Four plants are CUT and appear nowhere below** — `Plant_TreePine`, `Plant_TreeBirch`,
`Plant_TreePoplar`, `RG_Plant_Raspberry`. The owner removed them with Cherry Picker, which
deletes the ThingDef at load; a BiomeDef still naming one throws a red cross-reference error
on every load. The full list of everything left unplaced ON PURPOSE — anima, Gauranlen,
event-spawned and hydroponics-only flora — is the comment block at the foot of `FAMILIES`.

⚠️ **Climate was deliberately NOT a filter.** He ruled *"we can set the appropriate
temperatures later"* — 650 of 669 plants will not grow below 0 °C and half this planet is
colder than that. Making these rosters actually live is `NORMALIZE_TEMPERATURE_TOLERANCES_1`.

**8 families · 24 biomes · 604 plants, all distinct.** 4 biomes carry no flora by design: `IceSheet`, `Lake`, `Ocean`, `SeaIce`.

## A. dayside desert

### `Desert` — 4,648 tiles · -15 … 62 °C (median 24) · plantDensity 0.45

*was 21 inherited plants → now **30** assigned*

| commonality | plant | | mod |
|---:|---|---|---|
| 2.2 | **hardy grass** |  | `AB_HardyGrass` · Alpha Biomes |
| 0.5829 | **pincushion cactus** |  | `Plant_PincushionCactus` · Core |
| 0.3996 | **agave** |  | `Plant_Agave` · Core |
| 0.3996 | **grass** |  | `GRimYellowGrass` · GRiNDTerra Biomes |
| 0.2739 | **dandelions** |  | `Plant_DesertDandelion` · ReGrowth 2 |
| 0.1969 | **pebble cactus** | 🌳 | `Plant_PebbleCactus` · Biotech |
| 0.1969 | **pincushion cactus** |  | `GRimPincushionCactus` · GRiNDTerra Biomes |
| 0.1608 | **Cactus** |  | `AreebianCactus` · GRiNDTerra Biomes |
| 0.1608 | **pincushion cactus** |  | `GRim1PincushionCactus` · GRiNDTerra Biomes |
| 0.1608 | **agave** |  | `GRimAgave` · GRiNDTerra Biomes |
| 0.1608 | **wild chak-root plant** |  | `Plant_Chakroot_Wild` · Star Wars Animal Collection (Continued) |
| 0.1608 | **jade plant** |  | `VCE_Plant_JadePlant` · Vanilla Plants Expanded - Succulents |
| 0.1469 | **aloe vera plant** |  | `VCE_Plant_AloeVera` · Vanilla Plants Expanded - Succulents |
| 0.1266 | **brown barrel cactus** |  | `AB_BrownBarrelCactus` · Alpha Biomes |
| 0.1266 | **flower cactus** |  | `RG_FlowerCactus` · ReGrowth 2 |
| 0.1266 | **wild hubba gourd plant** |  | `Plant_HubbaGourd_Wild` · Star Wars Animal Collection (Continued) |
| 0.1266 | **snake plant** |  | `VCE_Plant_SnakePlant` · Vanilla Plants Expanded - Succulents |
| 0.12 | **bush** |  | `GRimAgavePlant` · GRiNDTerra Biomes |
| 0.107 | **pebble cactus** | 🌳 | `GRimPebbleCactus` · GRiNDTerra Biomes |
| 0.0944 | **pebble cactus** | 🌳 | `GRim1PebbleCactus` · GRiNDTerra Biomes |
| 0.0822 | **hoodia cactus** | 🌳 | `VEE_Plant_HoodiaCactus` · Vanilla Landmarks Expanded |
| 0.0647 | **Dragoberry tree** |  | `TreeDragoberry` · GRiNDTerra Biomes |
| 0.0483 | **saguaro cactus** | 🌳 | `Plant_SaguaroCactus` · Core |
| 0.0483 | **aaklac** |  | `AB_Aaklac` · Alpha Biomes |
| 0.038 | **saguaro cactus** | 🌳 | `GRimSaguaroCactus` · GRiNDTerra Biomes |
| 0.038 | **saguaro cactus** | 🌳 | `GRim1SaguaroCactus` · GRiNDTerra Biomes |
| 0.0284 | **drago tree** | 🌳 | `Plant_TreeDrago` · Core |
| 0.0194 | **dessert tree** | 🌳 | `AB_DessertTree` · Alpha Biomes |
| 0.0153 | **hubba gourd** |  | `Plant_HubbaGourd` · Star Wars Animal Collection (Continued) |
| 0.0153 | **chak-root plant** |  | `Plant_Chakroot` · Star Wars Animal Collection (Continued) |

### `ExtremeDesert` — 3,214 tiles · 16 … 66 °C (median 48) · plantDensity 0.008  🔴 **`plantDensity` is near zero — this roster will almost never be seen**

*was 25 inherited plants → now **12** assigned*

| commonality | plant | | mod |
|---:|---|---|---|
| 0.3 | **euphorbia rimworldia** |  | `AB_EuphorbiaRimworldia` · Alpha Biomes |
| 0.25 | **pincushion plant** |  | `VCE_Plant_PincushionPlant` · Vanilla Plants Expanded - Succulents |
| 0.25 | **echeveria plant** |  | `VCE_Plant_Echeveria` · Vanilla Plants Expanded - Succulents |
| 0.22 | **fairy washboard plant** |  | `VCE_Plant_FairyWashboard` · Vanilla Plants Expanded - Succulents |
| 0.2 | **gargantuan lithops** |  | `AB_GargantuanLithops` · Alpha Biomes |
| 0.2 | **sweetheart plant** |  | `VCE_Plant_SweetheartPlant` · Vanilla Plants Expanded - Succulents |
| 0.1 | **bloddle plant** |  | `Plant_Bloddle` · Star Wars Animal Collection (Continued) |
| 0.06 | **euphorbia desiccata** | 🌳 | `AB_EuphorbiaDesiccata` · Alpha Biomes |
| 0.05 | **dead bower tree** | 🌳 | `AB_DeadBowerTree` · Alpha Biomes |
| 0.04 | **dead tree** | 🌳 | `TreeDead` · Advanced Biomes (Continued) |
| 0.04 | **Dead tree** | 🌳 | `GRimTreeDead` · GRiNDTerra Biomes |
| 0.04 | **giant stikehr** |  | `AB_GiantStikehr` · Alpha Biomes |

### `AridShrubland` — 709 tiles · -15 … 60 °C (median 26) · plantDensity 0.72

*was 23 inherited plants → now **66** assigned*

| commonality | plant | | mod |
|---:|---|---|---|
| 1.4 | **low shrubs** |  | `Plant_ShrubLow` · Core |
| 0.2846 | **gorse** |  | `VEE_Gorse` · Vanilla Landmarks Expanded |
| 0.2846 | **grass** |  | `RG_Plant_AridGrass` · ReGrowth 2 |
| 0.1997 | **heather** |  | `VEE_Heather` · Vanilla Landmarks Expanded |
| 0.1313 | **juniper bush** |  | `VEE_Plant_JuniperBush` · Vanilla Landmarks Expanded |
| 0.0786 | **low shrubs** |  | `GRim1ShrubLow` · GRiNDTerra Biomes |
| 0.0786 | **low shrubs** |  | `GRim2ShrubLow` · GRiNDTerra Biomes |
| 0.0786 | **low shrubs** |  | `GRimShrubLow` · GRiNDTerra Biomes |
| 0.0579 | **bush** |  | `GRim1Bush` · GRiNDTerra Biomes |
| 0.0579 | **bush** |  | `GRim2Bush` · GRiNDTerra Biomes |
| 0.0579 | **bush** |  | `GRimBush` · GRiNDTerra Biomes |
| 0.0406 | **ripthorn** |  | `Plant_Ripthorn` · Biotech |
| 0.0406 | **bush** |  | `GRim3Bush` · GRiNDTerra Biomes |
| 0.0406 | **bush** |  | `GRim4Bush` · GRiNDTerra Biomes |
| 0.0406 | **bush** |  | `AreebianBush` · GRiNDTerra Biomes |
| 0.0406 | **bush** |  | `Plant_Bush` · Core |
| 0.0406 | **brambles** |  | `Plant_Brambles` · ReGrowth 2 |
| 0.0406 | **knapweed** |  | `VEE_Knapweed` · Vanilla Landmarks Expanded |
| 0.0406 | **loosestrife** |  | `VEE_Loosestrife` · Vanilla Landmarks Expanded |
| 0.0346 | **bush** |  | `GRim1BushPoplar` · GRiNDTerra Biomes |
| 0.0346 | **bush** |  | `GRim2BushPoplar` · GRiNDTerra Biomes |
| 0.0346 | **bush** |  | `GRimBushPoplar` · GRiNDTerra Biomes |
| 0.0267 | **wild healroot** |  | `Plant_HealrootWild` · Core |
| 0.0267 | **bush** |  | `BushDandys` · GRiNDTerra Biomes |
| 0.0267 | **bush** |  | `Grim3Shrub` · GRiNDTerra Biomes |
| 0.0267 | **bush** |  | `NewGreenBush` · GRiNDTerra Biomes |
| 0.0267 | **brambles** |  | `RG_Plant_BramblesRed` · ReGrowth 2 |
| 0.0267 | **brambles** |  | `RG_Plant_BramblesYellow` · ReGrowth 2 |
| 0.0267 | **brambles** |  | `GRimBrambles` · GRiNDTerra Biomes |
| 0.0267 | **buttercup** |  | `VEE_ButtercupFlower` · Vanilla Landmarks Expanded |
| 0.0267 | **forget-me-not** |  | `VEE_ForgetMeNot` · Vanilla Landmarks Expanded |
| 0.0267 | **oxalis** |  | `RG_Plant_Oxalis` · ReGrowth 2 |
| 0.0267 | **astragalus** |  | `Plant_Astragalus` · Core |
| 0.0267 | **juniper shrub** |  | `IronScruff_Juniper` · Primordial Geysers |
| 0.0243 | **brambles** |  | `Plant_Brambles_Leafless` · Odyssey |
| 0.0243 | **bush** |  | `Plant_Bush_Leafless` · Odyssey |
| 0.0199 | **wild muja fruit bush** |  | `Plant_MujaFruit_Wild` · Star Wars Animal Collection (Continued) |
| 0.0199 | **wild nysyllin plant** |  | `Plant_Nysyllin_Wild` · Star Wars Animal Collection (Continued) |
| 0.016 | **dervish** |  | `RG_Plant_Dervish` · ReGrowth 2 |
| 0.016 | **creep stern** |  | `RG_Plant_CreepStern` · ReGrowth 2 |
| 0.016 | **crimson cushion** |  | `RG_Plant_CrimsonCushion` · ReGrowth 2 |
| 0.016 | **lupine** |  | `RG_Plant_LupineIceland` · ReGrowth 2 |
| 0.016 | **clivia** |  | `Plant_Clivia` · Core |
| 0.016 | **daylily** |  | `Plant_Daylily` · Core |
| 0.016 | **berry bush** |  | `Plant_Berry` · Core |
| 0.016 | **healroot** |  | `Plant_Healroot` · Core |
| 0.0125 | **tiger lily** |  | `RG_Plant_TigerLily` · ReGrowth 2 |
| 0.0125 | **Cyprivia** |  | `GRimClivia` · GRiNDTerra Biomes |
| 0.0125 | **berry bush** |  | `GRimBerryBush` · GRiNDTerra Biomes |
| 0.01 | **rose** |  | `Plant_Rose` · Core |
| 0.01 | **plumeria** |  | `RG_Plant_Plumeria` · ReGrowth 2 |
| 0.01 | **muja fruit bush** |  | `Plant_MujaFruit` · Star Wars Animal Collection (Continued) |
| 0.01 | **nysyllin plant** |  | `Plant_Nysyllin` · Star Wars Animal Collection (Continued) |
| 0.01 | **berry bush** |  | `GRim1BerryBush` · GRiNDTerra Biomes |
| 0.01 | **berry bush** |  | `GRim2BerryBush` · GRiNDTerra Biomes |
| 0.01 | **berry bush** |  | `GRim3BerryBush` · GRiNDTerra Biomes |
| 0.01 | **berry bush** |  | `GRim4BerryBush` · GRiNDTerra Biomes |
| 0.01 | **berry bush** |  | `GRim5BerryBush` · GRiNDTerra Biomes |
| 0.01 | **daylily** |  | `ZBiome_Plant_WildDaylily` · More Vanilla Biomes |
| 0.01 | **rose** |  | `ZBiome_Plant_WildRose` · More Vanilla Biomes |
| 0.01 | **berry bush** |  | `Plant_Berry_Leafless` · Odyssey |
| 0.01 | **bluebell** |  | `VEE_Plant_Bluebell` · Vanilla Events Expanded |
| 0.01 | **gardenia** |  | `VEE_Plant_Gardenia` · Vanilla Events Expanded |
| 0.01 | **gentian** |  | `VEE_Plant_Gentian` · Vanilla Events Expanded |
| 0.01 | **petunia** |  | `VEE_Plant_Petunia` · Vanilla Events Expanded |
| 0.01 | **rose of rebirth** |  | `RotR_RoseOfRebirth` · Romance On The Rim |

### `ZBiome_Badlands` — 545 tiles · -21 … 58 °C (median 27) · plantDensity 0.3

*was 13 inherited plants → now **23** assigned*

| commonality | plant | | mod |
|---:|---|---|---|
| 0.4 | **cholla cactus** | 🌳 | `VEE_Plant_ChollaCactus` · Vanilla Landmarks Expanded |
| 0.4 | **hedgehog cactus** | 🌳 | `VEE_Plant_HedgehogCactus` · Vanilla Landmarks Expanded |
| 0.2107 | **beavertail cactus** | 🌳 | `VEE_Plant_BeavertailCactus` · Vanilla Landmarks Expanded |
| 0.137 | **bunny ears cactus** |  | `VCE_Plant_BunnyEarsCactus` · Vanilla Plants Expanded - Succulents |
| 0.1005 | **barrel cactus** | 🌳 | `VEE_Plant_BarrelCactus` · Vanilla Landmarks Expanded |
| 0.1005 | **ripthorn** |  | `GRim1Ripthorn` · GRiNDTerra Biomes |
| 0.1005 | **ripthorn** |  | `GRim2Ripthorn` · GRiNDTerra Biomes |
| 0.1005 | **ripthorn** |  | `GRimRipthorn` · GRiNDTerra Biomes |
| 0.0722 | **thornvine** |  | `GRim1Thornvine` · GRiNDTerra Biomes |
| 0.0722 | **thornvine** |  | `GRim2Thornvine` · GRiNDTerra Biomes |
| 0.0722 | **thornvine** |  | `GRimThornvine` · GRiNDTerra Biomes |
| 0.0722 | **peyote plant** |  | `VCE_Plant_PeyotePlant` · Vanilla Plants Expanded - Succulents |
| 0.0419 | **organ pipe cactus** | 🌳 | `VEE_Plant_OrganPipeCactus` · Vanilla Landmarks Expanded |
| 0.0419 | **raven nettle** |  | `AB_RavenNettle` · Alpha Biomes |
| 0.0419 | **red bugloss** |  | `AB_RedBugloss` · Alpha Biomes |
| 0.0419 | **schlumbergera plant** |  | `VCE_Plant_Schlumbergera` · Vanilla Plants Expanded - Succulents |
| 0.0227 | **thornvine** |  | `Plant_Thornvine` · Odyssey |
| 0.0144 | **wild psychoid plant** |  | `Plant_Psychoid_Wild` · Odyssey |
| 0.0144 | **lure weed** |  | `RG_Plant_LureWeed` · ReGrowth 2 |
| 0.0144 | **wild tooke-trap plant** |  | `Plant_TookeTrap_Wild` · Star Wars Animal Collection (Continued) |
| 0.01 | **tooke-trap plant** |  | `Plant_TookeTrap` · Star Wars Animal Collection (Continued) |
| 0.01 | **mantrap** |  | `BMT_Plant_Mantrap` · Biomes! Polluted Lands |
| 0.01 | **psychoid plant** |  | `Plant_Psychoid` · Core |

### `ZBiome_Grasslands` — 233 tiles · 28 … 65 °C (median 50) · plantDensity 0.95

*was 21 inherited plants → now **45** assigned*

| commonality | plant | | mod |
|---:|---|---|---|
| 2.4 | **yellow grass** |  | `Plant_YellowGrass` · Odyssey |
| 1.7405 | **tall yellow grass** |  | `Plant_YellowTallGrass` · Odyssey |
| 0.3462 | **grass** |  | `Plant_Grass` · ReGrowth 2 |
| 0.2736 | **tall grass** |  | `Plant_TallGrass` · ReGrowth 2 |
| 0.1512 | **haygrass** |  | `Plant_Haygrass` · Core |
| 0.1512 | **grass** |  | `GRimBlackGrass` · GRiNDTerra Biomes |
| 0.1512 | **grass** |  | `GRimBlueGrass` · GRiNDTerra Biomes |
| 0.1512 | **grass** |  | `GRimGreenGrass` · GRiNDTerra Biomes |
| 0.1512 | **grass** |  | `GRimNavyGrass` · GRiNDTerra Biomes |
| 0.1512 | **grass** |  | `GRimOrangeGrass` · GRiNDTerra Biomes |
| 0.1512 | **grass** |  | `GRimPurpleGrass` · GRiNDTerra Biomes |
| 0.1512 | **grass** |  | `GRimRedGrass` · GRiNDTerra Biomes |
| 0.1512 | **grass** |  | `GRimTealGrass` · GRiNDTerra Biomes |
| 0.1512 | **tall grass** |  | `PlantTallYellowGrass` · Advanced Biomes (Continued) |
| 0.1256 | **grass** |  | `DandyGrass` · GRiNDTerra Biomes |
| 0.102 | **tall grass** |  | `GRimBlackTallGrass` · GRiNDTerra Biomes |
| 0.102 | **tall grass** |  | `GRimBlueTallGrass` · GRiNDTerra Biomes |
| 0.102 | **tall grass** |  | `GRimGreenTallGrass` · GRiNDTerra Biomes |
| 0.102 | **tall grass** |  | `GRimNavyTallGrass` · GRiNDTerra Biomes |
| 0.102 | **tall grass** |  | `GRimOrangeTallGrass` · GRiNDTerra Biomes |
| 0.102 | **tall grass** |  | `GRimPurpleTallGrass` · GRiNDTerra Biomes |
| 0.102 | **tall grass** |  | `GRimRedTallGrass` · GRiNDTerra Biomes |
| 0.102 | **tall grass** |  | `GRimTealTallGrass` · GRiNDTerra Biomes |
| 0.102 | **tall grass** |  | `GRimYellowTallGrass` · GRiNDTerra Biomes |
| 0.102 | **tall grass** |  | `DandyTallGrass` · GRiNDTerra Biomes |
| 0.0806 | **flowers** |  | `Dandys` · GRiNDTerra Biomes |
| 0.0806 | **dandelions** |  | `Plant_Dandelion` · Core |
| 0.0615 | **wild tinctoria** |  | `Plant_Tinctoria_Wild` · Odyssey |
| 0.0615 | **wild cotton plant** |  | `Plant_Cotton_Wild` · Odyssey |
| 0.0615 | **bush** |  | `SavannaBush` · Advanced Biomes (Continued) |
| 0.0615 | **wheat plant** |  | `VCE_Wheat` · Vanilla Cooking Expanded |
| 0.0446 | **dandelions** |  | `RG_Plant_BlueDandelion` · ReGrowth 2 |
| 0.0446 | **dandelions** |  | `RG_Plant_RedDandelion` · ReGrowth 2 |
| 0.0446 | **sugarcane plant** |  | `VCE_Sugarcane` · Vanilla Cooking Expanded |
| 0.0446 | **wild fibercorn** |  | `Plant_Fibercorn_Wild` · Odyssey |
| 0.0415 | **cotton plant** |  | `Plant_Cotton` · Core |
| 0.0415 | **tinctoria** |  | `Plant_Tinctoria` · Core |
| 0.0301 | **wild dantuber plant** |  | `Plant_Dantuber_Wild` · Star Wars Animal Collection (Continued) |
| 0.0301 | **fibercorn** |  | `Plant_Fibercorn` · Ideology |
| 0.01 | **corn plant** |  | `Plant_Corn` · Core |
| 0.01 | **rice plant** |  | `Plant_Rice` · Core |
| 0.01 | **potato plant** |  | `Plant_Potato` · Core |
| 0.01 | **dantuber plant** |  | `Plant_Dantuber` · Star Wars Animal Collection (Continued) |
| 0.01 | **acacia tree** | 🌳 | `SavannaTreeAcacia` · Advanced Biomes (Continued) |
| 0.01 | **baobab tree** | 🌳 | `SavannaTreeBaobab` · Advanced Biomes (Continued) |

### `ZBiome_DesertOasis` — 227 tiles · 18 … 64 °C (median 35) · plantDensity 0.7

*was 27 inherited plants → now **50** assigned*

| commonality | plant | | mod |
|---:|---|---|---|
| 1.2 | **reeds** |  | `Plant_Reeds` · Odyssey |
| 0.8661 | **bulrush** |  | `Plant_Bulrush` · Odyssey |
| 0.3474 | **alocasia** |  | `Plant_Alocasia` · Core |
| 0.3474 | **reeds** |  | `GRimReeds` · GRiNDTerra Biomes |
| 0.3474 | **reeds** |  | `GRim1Reeds` · GRiNDTerra Biomes |
| 0.2974 | **bulrush** |  | `GRimBulrush` · GRiNDTerra Biomes |
| 0.1325 | **date palm** | 🌳 | `VEE_Plant_DatePalm` · Vanilla Landmarks Expanded |
| 0.1325 | **alocasia** |  | `GRim1Alocasia` · GRiNDTerra Biomes |
| 0.1325 | **alocasia** |  | `GRim2Alocasia` · GRiNDTerra Biomes |
| 0.1325 | **alocasia** |  | `GRimAlocasia` · GRiNDTerra Biomes |
| 0.1006 | **fan palm** | 🌳 | `AB_FanPalm` · Alpha Biomes |
| 0.1006 | **lily pad** |  | `Plant_LilyPad` · Odyssey |
| 0.0726 | **coffee plant** |  | `VBE_Plant_Coffee` · Vanilla Brewing Expanded |
| 0.0726 | **tea grass** |  | `VBE_Plant_Tea` · Vanilla Brewing Expanded |
| 0.0726 | **lotus** |  | `Plant_Lotus` · Odyssey |
| 0.0578 | **tobacco plant** |  | `VBE_Plant_Tobacco` · Vanilla Brewing Expanded |
| 0.0487 | **wild smokeleaf plant** |  | `Plant_Smokeleaf_Wild` · Odyssey |
| 0.0487 | **Palma tree** | 🌳 | `TreePalma` · GRiNDTerra Biomes |
| 0.0487 | **tidalis** |  | `RG_Plant_Tidalis` · ReGrowth 2 |
| 0.0487 | **allspice plant** |  | `VCE_Allspice` · Vanilla Cooking Expanded |
| 0.0404 | **rat palm tree** | 🌳 | `GRim1RatPalm` · GRiNDTerra Biomes |
| 0.0404 | **rat palm tree** | 🌳 | `GRim2RatPalm` · GRiNDTerra Biomes |
| 0.0404 | **rat palm tree** | 🌳 | `GRimRatPalm` · GRiNDTerra Biomes |
| 0.0404 | **rat palm tree** | 🌳 | `Plant_RatPalm` · Biotech |
| 0.0404 | **wild jogan tree** | 🌳 | `Plant_JoganTree_Wild` · Star Wars Animal Collection (Continued) |
| 0.0404 | **wild meiloorun plant** |  | `Plant_Meiloorun_Wild` · Star Wars Animal Collection (Continued) |
| 0.0327 | **smokeleaf plant** |  | `Plant_Smokeleaf` · Core |
| 0.0291 | **palm tree** | 🌳 | `RG_Plant_TallPalmTree` · ReGrowth 2 |
| 0.0291 | **dwarf palm tree** | 🌳 | `RG_Plant_TreeDwarfPalm` · ReGrowth 2 |
| 0.0291 | **palm tree** | 🌳 | `Plant_TreePalm` · Core |
| 0.0291 | **wild hydenock tree** | 🌳 | `Plant_HydenockTree_Wild` · Star Wars Animal Collection (Continued) |
| 0.0195 | **ambrosia bush** |  | `Plant_Ambrosia` · Core |
| 0.0195 | **screw pine** | 🌳 | `VEE_Plant_ScrewPine` · Vanilla Landmarks Expanded |
| 0.0195 | **hop plant** |  | `Plant_Hops` · Core |
| 0.0141 | **giant rafflesia** |  | `Plant_Rafflesia` · Core |
| 0.0141 | **strawberry plant** |  | `Plant_Strawberry` · Core |
| 0.0141 | **ambrosia bush** |  | `Plant_MotherAmbrosiaLGE` · Go Explore! |
| 0.01 | **jogan tree** | 🌳 | `Plant_JoganTree` · Star Wars Animal Collection (Continued) |
| 0.01 | **meiloorun plant** |  | `Plant_Meiloorun` · Star Wars Animal Collection (Continued) |
| 0.01 | **hydenock tree** | 🌳 | `Plant_HydenockTree` · Star Wars Animal Collection (Continued) |
| 0.01 | **wild strawberry plant** |  | `Plant_Strawberry_Wild` · Odyssey |
| 0.01 | **oak tree** | 🌳 | `Plant_TreeOak` · Core |
| 0.01 | **maple tree** | 🌳 | `Plant_TreeMaple` · Core |
| 0.01 | **auburn oak tree** | 🌳 | `VEE_Plant_TreeOak_Auburn` · Vanilla Landmarks Expanded |
| 0.01 | **auburn maple tree** | 🌳 | `VEE_Plant_TreeMaple_Auburn` · Vanilla Landmarks Expanded |
| 0.01 | **auburn birch tree** | 🌳 | `VEE_Plant_TreeBirch_Auburn` · Vanilla Landmarks Expanded |
| 0.01 | **auburn poplar tree** | 🌳 | `VEE_Plant_TreePoplar_Auburn` · Vanilla Landmarks Expanded |
| 0.01 | **laurel tree** | 🌳 | `VEE_Plant_Laurel` · Vanilla Landmarks Expanded |
| 0.01 | **firewood tree** | 🌳 | `VEE_Plant_Firewood` · Vanilla Landmarks Expanded |
| 0.01 | **splitpine tree** | 🌳 | `RG_Plant_TreeSplitpine` · ReGrowth 2 |

## B. contamination

### `Wasteland` — 1,721 tiles · -45 … 54 °C (median 1) · plantDensity 0.01  🔴 **`plantDensity` is near zero — this roster will almost never be seen**

*was 9 inherited plants → now **44** assigned*

| commonality | plant | | mod |
|---:|---|---|---|
| 2 | **toxigrass** |  | `RG_Plant_ToxiGrass` · ReGrowth 2 |
| 0.9081 | **tall toxigrass** |  | `RG_Plant_TallToxiGrass` · ReGrowth 2 |
| 0.3111 | **gutter plantain** |  | `BMT_Plant_GutterPlantain` · Biomes! Polluted Lands |
| 0.3111 | **toxi grass** |  | `AB_ToxiGrass` · Alpha Biomes |
| 0.2347 | **toxic ivy** |  | `BMT_Plant_ToxicIvy` · Biomes! Polluted Lands |
| 0.2347 | **twisted dandelion** |  | `BMT_Plant_TwistedDandelion` · Biomes! Polluted Lands |
| 0.2347 | **tall grass** |  | `PoisonPlantTallGrass` · Advanced Biomes (Continued) |
| 0.1352 | **poison shrub** |  | `PoisonShrub` · Advanced Biomes (Continued) |
| 0.1352 | **gray grass** |  | `Plant_GrayGrass` · Biotech |
| 0.1066 | **scorched stars** |  | `BMT_Plant_ScorchedStars` · Biomes! Polluted Lands |
| 0.1066 | **poison alocasia** |  | `PoisonAlocasia` · Advanced Biomes (Continued) |
| 0.1066 | **poison brambles** |  | `PoisonBrambles` · Advanced Biomes (Continued) |
| 0.1066 | **bush** |  | `PoisonPlantBush` · Advanced Biomes (Continued) |
| 0.1066 | **dandelions** |  | `PoisonPlantDandelion` · Advanced Biomes (Continued) |
| 0.1066 | **grey fern** |  | `BMT_Plant_GreyFern` · Biomes! Polluted Lands |
| 0.1066 | **snaketails** |  | `BMT_Plant_Snaketails` · Biomes! Polluted Lands |
| 0.0804 | **pigs ears** |  | `BMT_Plant_PigsEars` · Biomes! Polluted Lands |
| 0.0804 | **pox sorghum** |  | `BMT_Plant_PoxSorghum` · Biomes! Polluted Lands |
| 0.0804 | **tumorbulb hyacinth** |  | `BMT_Plant_TumorbulbHyacinth` · Biomes! Polluted Lands |
| 0.066 | **spiny hop** |  | `BMT_SpinyHops` · Biomes! Polluted Lands |
| 0.0569 | **wild rashroot** |  | `BMT_Plant_WildRashroot` · Biomes! Polluted Lands |
| 0.0569 | **wild mushroom** |  | `PoisonMushroom` · Advanced Biomes (Continued) |
| 0.0569 | **weeping toxberry** |  | `AB_WeepingToxberry` · Alpha Biomes |
| 0.0569 | **cotton cap** |  | `BMT_Plant_CottonCap` · Biomes! Polluted Lands |
| 0.0569 | **toxipotato plant** |  | `Plant_Toxipotato` · Biotech |
| 0.0403 | **rashroot** |  | `BMT_Plant_Rashroot` · Biomes! Polluted Lands |
| 0.0365 | **doomsprout** |  | `BMT_Plant_Doomsprout` · Biomes! Polluted Lands |
| 0.0365 | **raspberry bush** |  | `PoisonPlantRaspberry` · Advanced Biomes (Continued) |
| 0.0365 | **rainbow tongue** |  | `BMT_RainbowTongue` · Biomes! Polluted Lands |
| 0.0365 | **eclipsus** |  | `BMT_Plant_EclipsusFlower` · Biomes! Polluted Lands |
| 0.0365 | **eclipsus** |  | `BMT_Plant_EclipsusLeaves` · Biomes! Polluted Lands |
| 0.0259 | **poison rafflesia** |  | `PoisonRafflesia` · Advanced Biomes (Continued) |
| 0.0195 | **toxibulb** | 🌳 | `AB_ToxiBulb` · Alpha Biomes |
| 0.0195 | **toxipine tree** | 🌳 | `RG_Plant_TreeToxipine` · ReGrowth 2 |
| 0.0195 | **toxiteak tree** | 🌳 | `RG_Plant_TreeToxiTeak` · ReGrowth 2 |
| 0.0195 | **polux tree** | 🌳 | `Plant_TreePolux` · Biotech |
| 0.0138 | **giant toxic flower** | 🌳 | `AB_GiantToxicFlower` · Alpha Biomes |
| 0.0138 | **cecropia tree** | 🌳 | `PoisonPlantTreeCecropia` · Advanced Biomes (Continued) |
| 0.0138 | **cypress tree** | 🌳 | `PoisonTreeCypress` · Advanced Biomes (Continued) |
| 0.0138 | **palm tree** | 🌳 | `PoisonTreePalm` · Advanced Biomes (Continued) |
| 0.0138 | **teak tree** | 🌳 | `PoisonPlantTreeTeak` · Advanced Biomes (Continued) |
| 0.0138 | **willow tree** | 🌳 | `PoisonTreeWillow` · Advanced Biomes (Continued) |
| 0.0138 | **polux bush** | 🌳 | `VRE_PoluxBush` · Vanilla Races Expanded - Phytokin |
| 0.01 | **cypress tree** | 🌳 | `Plant_TreeCypress` · Core |

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
| 0.2976 | **glowing agarilux** |  | `AB_GlowingAgarilux` · Alpha Biomes |
| 0.2063 | **agaricus domecap** |  | `AB_AgaricusDomeCap` · Alpha Biomes |
| 0.2063 | **grass** |  | `AB_GlowingGrass` · Alpha Biomes |
| 0.1317 | **recurved stropharia** |  | `AB_RecurvedStropharia` · Alpha Biomes |
| 0.1317 | **slimy pholiota** |  | `AB_SlimyPholiota` · Alpha Biomes |
| 0.1317 | **glowstool** |  | `AB_Glowstool` · Alpha Biomes |
| 0.1317 | **bryolux** |  | `AB_Bryolux` · Alpha Biomes |
| 0.1007 | **witches' oyster** |  | `AB_WitchesOyster` · Alpha Biomes |
| 0.1007 | **tinkle grass** |  | `AB_TinkleGrass` · Alpha Biomes |
| 0.0738 | **giant agarilux** |  | `AB_GiantAgarilux` · Alpha Biomes |
| 0.0738 | **Agarilux Prime** |  | `AB_AgariluxPrime` · Alpha Biomes |
| 0.0738 | **flowers** |  | `AB_Flowers` · Alpha Biomes |
| 0.0512 | **amethyst land coral fungus** |  | `AB_LandCoral` · Alpha Biomes |
| 0.0512 | **gomphoeria** |  | `AB_Gomphoeria` · Alpha Biomes |
| 0.0512 | **lilac beacon** |  | `AB_LilacBeacon` · Alpha Biomes |
| 0.0512 | **manax fungus** |  | `Plant_ManaxFungus` · Star Wars Animal Collection (Continued) |
| 0.0396 | **wild munch-fungus** |  | `Plant_MunchFungus_Wild` · Star Wars Animal Collection (Continued) |
| 0.0396 | **wild bubble spore plant** |  | `Plant_Bubblespore_Wild` · Star Wars Animal Collection (Continued) |
| 0.0327 | **dribbling cap** |  | `AB_DribblingCap` · Alpha Biomes |
| 0.0327 | **arbuscular mycorrhiza** |  | `AB_ArbuscularMycorrhiza` · Alpha Biomes |
| 0.0327 | **iashiphus** |  | `AB_Iashiphus` · Alpha Biomes |
| 0.0327 | **wild ragadast** |  | `AB_WildRadagast` · Alpha Biomes |
| 0.0327 | **sugar famewort** |  | `AB_SugarFamewort` · Alpha Biomes |
| 0.0327 | **tangle tea** |  | `AB_TangleTea` · Alpha Biomes |
| 0.0183 | **agaritox** | 🌳 | `AB_GiantAgariTox` · Alpha Biomes |
| 0.0159 | **wild felucian glowspore** | 🌳 | `Plant_FelucianGlowspore_Wild` · Star Wars Animal Collection (Continued) |
| 0.01 | **devilstrand** |  | `Plant_Devilstrand` · Core |
| 0.01 | **giant septimum** | 🌳 | `AB_GiantSeptimum` · Alpha Biomes |
| 0.01 | **luminescent tree** | 🌳 | `AB_LuminescentTree` · Alpha Biomes |
| 0.01 | **giant sunflower** | 🌳 | `AB_GiantSunflower` · Alpha Biomes |
| 0.01 | **giant tulips** | 🌳 | `AB_GiantTulip` · Alpha Biomes |
| 0.01 | **munch-fungus** |  | `Plant_MunchFungus` · Star Wars Animal Collection (Continued) |
| 0.01 | **bubble spore plant** |  | `Plant_Bubblespore` · Star Wars Animal Collection (Continued) |
| 0.01 | **felucian glowspore** | 🌳 | `Plant_FelucianGlowspore` · Star Wars Animal Collection (Continued) |

### `PoisonForest` — 604 tiles · -52 … 39 °C (median -18) · plantDensity 0.85

*was 19 inherited plants → now **35** assigned*

| commonality | plant | | mod |
|---:|---|---|---|
| 0.8 | **pagan thorns** |  | `BMT_Plant_PaganThorns` · Biomes! Polluted Lands |
| 0.6344 | **plague fans** |  | `BMT_Plant_PlagueFans` · Biomes! Polluted Lands |
| 0.4855 | **toxcaps** |  | `BMT_Plant_Toxcaps` · Biomes! Polluted Lands |
| 0.3537 | **pestia** |  | `BMT_Plant_Pestia` · Biomes! Polluted Lands |
| 0.1457 | **weeping hagbloom** |  | `BMT_Plant_WeepingHagbloom` · Biomes! Polluted Lands |
| 0.1457 | **Mushrooms** |  | `GrimMush` · GRiNDTerra Biomes |
| 0.1457 | **Mushrooms** |  | `GrimShroom` · GRiNDTerra Biomes |
| 0.1457 | **twisting thorngrass** |  | `BMT_Plant_TwistingThorngrass` · Biomes! Polluted Lands |
| 0.1062 | **mutated fern** |  | `RG_Plant_MutatedFern` · ReGrowth 2 |
| 0.1062 | **mutated fungus** |  | `RG_Plant_MutatedFungus` · ReGrowth 2 |
| 0.1062 | **twisting thornweed** |  | `BMT_Plant_TwistingThornweed` · Biomes! Polluted Lands |
| 0.0721 | **pilocap** |  | `GRimPsilocap` · GRiNDTerra Biomes |
| 0.0721 | **glow leaf** |  | `RG_Plant_GlowLeaf` · ReGrowth 2 |
| 0.06 | **twisting thornwood** | 🌳 | `BMT_Plant_TreeTwistingThornwood` · Biomes! Polluted Lands |
| 0.0437 | **blot birch tree** | 🌳 | `BMT_Plant_TreeBlotBirch` · Biomes! Polluted Lands |
| 0.0437 | **light-resistant boomshroom** |  | `VEE_DayBoomshroom` · Vanilla Landmarks Expanded |
| 0.0437 | **light-resistant psilocap** |  | `VEE_DayPsilocap` · Vanilla Landmarks Expanded |
| 0.0437 | **light-resistant willowgill** |  | `VEE_DayWillowgill` · Vanilla Landmarks Expanded |
| 0.0437 | **cathedralis** |  | `RG_Plant_Cathedralis` · ReGrowth 2 |
| 0.0297 | **scalped cypress** | 🌳 | `BMT_Plant_TreeScalpedCypress` · Biomes! Polluted Lands |
| 0.0297 | **witchwood tree** | 🌳 | `GRim1Witchwood` · GRiNDTerra Biomes |
| 0.0297 | **witchwood tree** | 🌳 | `GRim2Witchwood` · GRiNDTerra Biomes |
| 0.0297 | **witchwood tree** | 🌳 | `GRimWitchwood` · GRiNDTerra Biomes |
| 0.0297 | **snagroot tree** | 🌳 | `GRim1TreeSnagroot` · GRiNDTerra Biomes |
| 0.0297 | **snagroot tree** | 🌳 | `GRimTreeSnagroot` · GRiNDTerra Biomes |
| 0.0297 | **Mushroom tree** | 🌳 | `Mushpine` · GRiNDTerra Biomes |
| 0.0297 | **boomshroom** |  | `Boomshroom` · Odyssey |
| 0.0297 | **wild psilocap** |  | `Plant_Psilocap` · Odyssey |
| 0.0297 | **willowgill** |  | `Plant_Willowgill` · Odyssey |
| 0.0297 | **psilocap** |  | `Plant_Psilocap_Farmed` · Psilocap Cultivation |
| 0.0216 | **martyr tree** | 🌳 | `BMT_Plant_TreeMartyr` · Biomes! Polluted Lands |
| 0.0216 | **wormoak tree** | 🌳 | `BMT_Plant_TreeWormoak` · Biomes! Polluted Lands |
| 0.0216 | **witchwood tree** | 🌳 | `Plant_Witchwood` · Biotech |
| 0.0216 | **snagroot tree** | 🌳 | `Plant_TreeSnagroot` · Odyssey |
| 0.0216 | **whistling cane** | 🌳 | `BMT_Plant_TreeWhistlingCane` · Biomes! Polluted Lands |

### `BMT_FungalForest` — 425 tiles · -44 … 24 °C (median -24) · plantDensity 1

*was 27 inherited plants → now **69** assigned*

| commonality | plant | | mod |
|---:|---|---|---|
| 1 | **wrinklecap** |  | `BMT_Wrinklecap` · Biomes! Caverns |
| 0.5584 | **fibershroom** |  | `BMT_Fibershroom` · Biomes! Caverns |
| 0.2635 | **gleamtip** |  | `BMT_Gleamtip` · Biomes! Caverns |
| 0.1637 | **chromacap** |  | `BMT_Chromacap` · Biomes! Caverns |
| 0.0914 | **greatbulb** |  | `BMT_Greatbulb` · Biomes! Caverns |
| 0.0914 | **floor mold** |  | `BMT_FloorMold` · Biomes! Caverns |
| 0.0914 | **mycelium** |  | `BMT_Mycelium` · Biomes! Caverns |
| 0.0645 | **fungusfern** |  | `BMT_Fungusfern` · Biomes! Caverns |
| 0.0645 | **mold fruiting bodies** |  | `BMT_FruitingBodies` · Biomes! Caverns |
| 0.0645 | **mycelium** |  | `BMT_CavernMycelium` · Biomes! Caverns |
| 0.0431 | **bright wispcap** |  | `BMT_BrightWispcap` · Biomes! Caverns |
| 0.0431 | **dark wispcap** |  | `BMT_DarkWispcap` · Biomes! Caverns |
| 0.0431 | **chubshroom** |  | `BMT_Chubshroom` · Biomes! Caverns |
| 0.0431 | **dewshrooms** |  | `BMT_Dewshrooms` · Biomes! Caverns |
| 0.0431 | **tendralus** |  | `BMT_FungalTendril` · Biomes! Caverns |
| 0.0268 | **shimbershroom** | 🌳 | `BMT_Shimbershroom` · Biomes! Caverns |
| 0.0268 | **baleful bolete** |  | `BMT_BalefulBolete` · Biomes! Caverns |
| 0.0268 | **bleeding tooth** |  | `BMT_BleedingTooth` · Biomes! Caverns |
| 0.0268 | **carvefungus** |  | `BMT_CarveShroom` · Biomes! Caverns |
| 0.0268 | **coral club** |  | `BMT_CoralClub` · Biomes! Caverns |
| 0.0268 | **crimson cap** |  | `BMT_CrimsonCap` · Biomes! Caverns |
| 0.0268 | **glittercap** |  | `BMT_Glittercap` · Biomes! Caverns |
| 0.0268 | **luminous spout** |  | `BMT_LuminousSpout` · Biomes! Caverns |
| 0.0268 | **nuitae** |  | `BMT_Nuitae` · Biomes! Caverns |
| 0.0268 | **shinebell** |  | `BMT_Brightbell` · Biomes! Caverns |
| 0.0268 | **violet wimple** |  | `BMT_VioletWimple` · Biomes! Caverns |
| 0.0268 | **watorbs** |  | `BMT_WatOrbs` · Biomes! Caverns |
| 0.0268 | **wheelshroom** |  | `BMT_Wheelshroom` · Biomes! Caverns |
| 0.0268 | **wrinklecap** |  | `BMT_WrinklecapMarsh` · Biomes! Caverns |
| 0.0268 | **healroot grass** |  | `BMT_HealrootGrass` · Biomes! Caverns |
| 0.0192 | **yum bulbs** |  | `BMT_YumBulbs` · Biomes! Caverns |
| 0.015 | **poptop** | 🌳 | `BMT_Poptop` · Biomes! Caverns |
| 0.015 | **dish cap** | 🌳 | `BMT_Dishcap` · Biomes! Caverns |
| 0.015 | **giant leaf** |  | `BMT_GiantLeaf` · Biomes! Caverns |
| 0.015 | **glimmering cactus** |  | `BMT_GlowingSucculent` · Biomes! Caverns |
| 0.015 | **nuitae** |  | `BMT_NuitaeMarsh` · Biomes! Caverns |
| 0.015 | **power fungus** |  | `BMT_PowerFungus` · Biomes! Caverns |
| 0.015 | **pusmelon** |  | `BMT_Pusmelon` · Biomes! Caverns |
| 0.015 | **bioluminescence algae** |  | `BMT_BiolumiAlgaeCarnelian` · Biomes! Caverns |
| 0.015 | **bioluminescence algae** |  | `BMT_BiolumiAlgaeChrysoberyl` · Biomes! Caverns |
| 0.015 | **bioluminescence algae** |  | `BMT_BiolumiAlgaeCitrine` · Biomes! Caverns |
| 0.015 | **bioluminescence algae** |  | `BMT_BiolumiAlgaeKunzite` · Biomes! Caverns |
| 0.015 | **bioluminescence algae** |  | `BMT_BiolumiAlgaeTanzanite` · Biomes! Caverns |
| 0.015 | **bioluminescence algae** |  | `BMT_BiolumiAlgaeTurquoise` · Biomes! Caverns |
| 0.015 | **black lily** |  | `BMT_BlackLily` · Biomes! Caverns |
| 0.015 | **Sychi cap** |  | `RG_SychiCap` · ReGrowth 2 |
| 0.015 | **cibarius** |  | `RG_Cibarius` · ReGrowth 2 |
| 0.015 | **neo amanita** |  | `RG_NeoAmanita` · ReGrowth 2 |
| 0.015 | **potokus** |  | `RG_Potokus` · ReGrowth 2 |
| 0.015 | **tripaloski** |  | `RG_Tripaloski` · ReGrowth 2 |
| 0.0114 | **shine cap** | 🌳 | `BMT_Shinecap` · Biomes! Caverns |
| 0.01 | **bright wisptoll** | 🌳 | `BMT_BrightWisptoll` · Biomes! Caverns |
| 0.01 | **dark wisptoll** | 🌳 | `BMT_DarkWisptoll` · Biomes! Caverns |
| 0.01 | **candlesnuff** | 🌳 | `BMT_Candlesnuff` · Biomes! Caverns |
| 0.01 | **curlbranch** | 🌳 | `BMT_Curlbranch` · Biomes! Caverns |
| 0.01 | **exploding angel** | 🌳 | `BMT_ExplodingAngel` · Biomes! Caverns |
| 0.01 | **flakespire fungus** | 🌳 | `BMT_FlakespireFungus` · Biomes! Caverns |
| 0.01 | **frigu** | 🌳 | `BMT_Frigu` · Biomes! Caverns |
| 0.01 | **nogtyl** | 🌳 | `BMT_Nogtyl` · Biomes! Caverns |
| 0.01 | **nogtyl** | 🌳 | `BMT_NogtylMarsh` · Biomes! Caverns |
| 0.01 | **ravelmush** | 🌳 | `BMT_Ravelmush` · Biomes! Caverns |
| 0.01 | **skulltop** | 🌳 | `BMT_Skulltop` · Biomes! Caverns |
| 0.01 | **stink lattice** | 🌳 | `BMT_StinkLattice` · Biomes! Caverns |
| 0.01 | **arpeau** | 🌳 | `BMT_Arpeau` · Biomes! Caverns |
| 0.01 | **arpeau** | 🌳 | `BMT_GreenArpeau` · Biomes! Caverns |
| 0.01 | **mystic cap** |  | `VEE_Plant_MysticCap` · Vanilla Landmarks Expanded |
| 0.01 | **juice cactus** |  | `BMT_JuiceCactus` · Biomes! Caverns |
| 0.01 | **blooming cactus** |  | `BMT_BloomingCactus` · Biomes! Caverns |
| 0.01 | **timbershroom** | 🌳 | `Plant_Timbershroom` · Core |

## D. river jungle

### `AB_FeraliskInfestedJungle` — 534 tiles · 36 … 64 °C (median 46) · plantDensity 0.9

*was 13 inherited plants → now **39** assigned*

| commonality | plant | | mod |
|---:|---|---|---|
| 1.8 | **tall slimy grass** |  | `AB_TallSlimyGrass` · Alpha Biomes |
| 0.3928 | **green rock fern** |  | `AB_GreenRockFern` · Alpha Biomes |
| 0.1594 | **fern** |  | `RG_Plant_TropicalFern` · ReGrowth 2 |
| 0.1285 | **ivy** |  | `RG_Plant_TropicalIvy` · ReGrowth 2 |
| 0.1285 | **bush** |  | `JungleShrub` · GRiNDTerra Biomes |
| 0.1285 | **sword fern** |  | `SwordFern` · Advanced Biomes (Continued) |
| 0.1002 | **deep jungle tree** | 🌳 | `AB_JungleTree` · Alpha Biomes |
| 0.1002 | **brambles** |  | `RG_Plant_TropicalBrambles` · ReGrowth 2 |
| 0.1002 | **chokevine** |  | `RG_Plant_TropicalChokevine` · ReGrowth 2 |
| 0.1002 | **chokevine** |  | `Plant_Chokevine` · Core |
| 0.1002 | **fern** |  | `RG_Plant_TemperateFern` · ReGrowth 2 |
| 0.1002 | **fern** |  | `VEE_Plant_Fern` · Vanilla Landmarks Expanded |
| 0.1002 | **tendrilmoss vines** |  | `VFEI2_TendrilmossVines` · Vanilla Factions Expanded - Insectoids 2 |
| 0.0897 | **ivy** |  | `RG_Plant_TemperateIvy` · ReGrowth 2 |
| 0.0747 | **chokevine** |  | `GRim1Chokevine` · GRiNDTerra Biomes |
| 0.0747 | **chokevine** |  | `GRim2Chokevine` · GRiNDTerra Biomes |
| 0.0747 | **chokevine** |  | `GRim3Chokevine` · GRiNDTerra Biomes |
| 0.0747 | **chokevine** |  | `GRimChokevine` · GRiNDTerra Biomes |
| 0.0747 | **fern** |  | `RG_Plant_BorealFern` · ReGrowth 2 |
| 0.0747 | **bush** |  | `GRim1BambooBush` · GRiNDTerra Biomes |
| 0.0747 | **bush** |  | `GRimBambooBush` · GRiNDTerra Biomes |
| 0.0328 | **deep jungle polux** | 🌳 | `AB_JungleTree_Polluted` · Alpha Biomes |
| 0.0328 | **Grimpepper plant** |  | `GrimPepper` · GRiNDTerra Biomes |
| 0.0229 | **keening cordax** | 🌳 | `AB_KeeningCordax` · Alpha Biomes |
| 0.0229 | **cecropia tree** | 🌳 | `Plant_TreeCecropia` · Core |
| 0.0229 | **bamboo tree** | 🌳 | `Plant_TreeBamboo` · Core |
| 0.0171 | **giant mutant hibiscus** | 🌳 | `AB_GiantFlower` · Alpha Biomes |
| 0.0171 | **teak tree** | 🌳 | `Plant_TreeTeak` · Core |
| 0.0171 | **Areeb tree** | 🌳 | `TreeAreeb` · GRiNDTerra Biomes |
| 0.0171 | **Blareebian tree** | 🌳 | `TreeBlareebian` · GRiNDTerra Biomes |
| 0.0119 | **redcedar tree** | 🌳 | `TreeCedar` · Advanced Biomes (Continued) |
| 0.0119 | **Cypre tree** | 🌳 | `TreeCypre` · GRiNDTerra Biomes |
| 0.0119 | **Gralma tree** | 🌳 | `TreeGralma` · GRiNDTerra Biomes |
| 0.0119 | **Grimber tree** | 🌳 | `TreeGrimber` · GRiNDTerra Biomes |
| 0.0119 | **GRim tree** | 🌳 | `GRimTreePolux` · GRiNDTerra Biomes |
| 0.0119 | **cocoa tree** | 🌳 | `Plant_TreeCocoa` · Core |
| 0.01 | **wild cocoa tree** | 🌳 | `Plant_TreeCocoa_Wild` · Odyssey |
| 0.01 | **cocoa bush** |  | `VCE_ChocolateBush` · Vanilla Ideology Expanded - Memes and Structures |
| 0.01 | **archean tree** | 🌳 | `Plant_TreeArchean` · Odyssey |

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

*was 7 inherited plants → now **27** assigned*

| commonality | plant | | mod |
|---:|---|---|---|
| 0.9 | **frost leaf** |  | `AB_FrostLeaf` · Alpha Biomes |
| 0.368 | **rime nodules** |  | `AB_RimeNodules` · Alpha Biomes |
| 0.1951 | **grass** |  | `RG_Plant_TundraGrass` · ReGrowth 2 |
| 0.1505 | **rime flower** |  | `BMT_RimeFlower` · Biomes! Caverns |
| 0.1505 | **reindeer moss** |  | `BMT_ReindeerMoss` · Biomes! Caverns |
| 0.1505 | **moss** |  | `Plant_Moss` · Core |
| 0.1121 | **tall grass** |  | `RG_Plant_TundraTallGrass` · ReGrowth 2 |
| 0.1121 | **moss** |  | `GRim1Moss` · GRiNDTerra Biomes |
| 0.1121 | **moss** |  | `GRim2Moss` · GRiNDTerra Biomes |
| 0.1121 | **moss** |  | `GRim3Moss` · GRiNDTerra Biomes |
| 0.1121 | **moss** |  | `GRim4Moss` · GRiNDTerra Biomes |
| 0.1121 | **moss** |  | `GRimMoss` · GRiNDTerra Biomes |
| 0.1121 | **night grass** |  | `Plant_Nightgrass` · Odyssey |
| 0.0798 | **coldheart** |  | `RG_Plant_Coldheart` · ReGrowth 2 |
| 0.0534 | **tundra cotton** |  | `RG_Plant_TundraCotton` · ReGrowth 2 |
| 0.0534 | **nightguide** |  | `RG_Plant_Nightguide` · ReGrowth 2 |
| 0.0326 | **night rafflesia** |  | `Plant_NightRafflesia` · Odyssey |
| 0.01 | **flash frozen tree** |  | `AB_FlashFrozenTree` · Alpha Biomes |
| 0.01 | **pine tree** | 🌳 | `RG_Tree_TundraTreePine` · ReGrowth 2 |
| 0.01 | **gnarled pine tree** | 🌳 | `VEE_Plant_GnarledPine` · Vanilla Landmarks Expanded |
| 0.01 | **gray pine tree** | 🌳 | `GRim1TreeGrayPine` · GRiNDTerra Biomes |
| 0.01 | **gray pine tree** | 🌳 | `GRim2TreeGrayPine` · GRiNDTerra Biomes |
| 0.01 | **gray pine tree** | 🌳 | `GRimTreeGrayPine` · GRiNDTerra Biomes |
| 0.01 | **gray pine tree** | 🌳 | `Plant_TreeGrayPine` · Biotech |
| 0.01 | **pine tree** | 🌳 | `RG_Plant_BlueTreePine` · ReGrowth 2 |
| 0.01 | **pine tree** | 🌳 | `RG_Plant_LargeTreePine` · ReGrowth 2 |
| 0.01 | **pine tree** | 🌳 | `RG_Plant_OrangeTreePine` · ReGrowth 2 |

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

*was 1 inherited plants → now **8** assigned*

| commonality | plant | | mod |
|---:|---|---|---|
| 1.2 | **horrorweb** |  | `HorrorWeb` · Horrors (Continued) |
| 0.55 | **Tentacle** |  | `Grimtacle` · GRiNDTerra Biomes |
| 0.5 | **blood bouquet** |  | `AB_BloodBouquet` · Alpha Biomes |
| 0.4 | **globular aberration** |  | `AB_GlobularPlant` · Alpha Biomes |
| 0.35 | **tentacular aberration** |  | `AB_TentacularPlant` · Alpha Biomes |
| 0.25 | **fermented rotting mound** |  | `AA_RottingMound` · Alpha Animals |
| 0.18 | **polluted globular aberration** | 🌳 | `AB_GlobularPlant_Polluted` · Alpha Biomes |
| 0.12 | **flesh tree** | 🌳 | `AB_FleshTree` · Alpha Biomes |

### `BMT_CrystalCaverns` — 127 tiles · -71 … -54 °C (median -62) · plantDensity 1

*was 12 inherited plants → now **42** assigned*

| commonality | plant | | mod |
|---:|---|---|---|
| 1 | **Crystal Small** |  | `CrystalSmall` · GRiNDTerra Biomes |
| 0.6071 | **crystaltip brambles** |  | `BMT_CrystaltipBrambles` · Biomes! Caverns |
| 0.3191 | **Crystal Shards** |  | `CrystalShard` · GRiNDTerra Biomes |
| 0.0956 | **gleamcap** |  | `BMT_Gleamcap` · Biomes! Caverns |
| 0.0956 | **glowbulb** |  | `BMT_Glowbulb` · Biomes! Caverns |
| 0.0677 | **Crystal Big** |  | `CrystalBig` · GRiNDTerra Biomes |
| 0.0677 | **crystalcap** | 🌳 | `BMT_Crystalcap` · Biomes! Caverns |
| 0.0677 | **brightbells** |  | `BMT_Brightbells` · Biomes! Caverns |
| 0.0677 | **greyfields** |  | `BMT_Greyfields` · Biomes! Caverns |
| 0.0677 | **shimmershroom** |  | `BMT_Shimmershroom` · Biomes! Caverns |
| 0.0677 | **agarilux** |  | `Agarilux` · Core |
| 0.0677 | **bryolux** |  | `Bryolux` · Core |
| 0.0677 | **glowstool** |  | `Glowstool` · Core |
| 0.0677 | **Caveshrooms** |  | `CaveShroom` · GRiNDTerra Biomes |
| 0.045 | **royal bracket** |  | `BMT_RoyalBracket` · Biomes! Caverns |
| 0.045 | **moonless stripes** |  | `BMT_MoonlessStripesPlant` · Biomes! Caverns |
| 0.045 | **mortal morel** |  | `BMT_MortalMorelPlant` · Biomes! Caverns |
| 0.045 | **starchstalk** |  | `BMT_StarchstalkPlant` · Biomes! Caverns |
| 0.045 | **Fiber shroom** |  | `Plant_Fibershroom` · ? |
| 0.0273 | **stimquill** |  | `BMT_Stimquill` · Biomes! Caverns |
| 0.0273 | **kessinger** |  | `BMT_KessingerPlant` · Biomes! Caverns |
| 0.0273 | **jade glint fungus** |  | `BMT_JadeGlintsCrop` · Biomes! Caverns |
| 0.0273 | **dulcis** |  | `BMT_DulcisPlant` · Biomes! Caverns |
| 0.0273 | **capscool** |  | `BMT_CapscoolFungus` · Biomes! Caverns |
| 0.0273 | **ambrosyx fungus** |  | `BMT_AmbrosyxFungus` · Biomes! Caverns |
| 0.0273 | **abyssal grapes** |  | `BMT_AbyssalGrapesVine` · Biomes! Caverns |
| 0.0273 | **Cotton shroom** |  | `Plant_Cottonshroom` · Tunneler Expanded |
| 0.0273 | **Devil shroom** |  | `Plant_DevilShroom` · Tunneler Expanded |
| 0.0273 | **Gold shroom** |  | `Plant_GoldShroom` · Tunneler Expanded |
| 0.0273 | **Neutro shroom** |  | `Plant_NeutroShroom` · Tunneler Expanded |
| 0.0273 | **Psychoid shroom** |  | `Plant_PsychoidShroom` · Tunneler Expanded |
| 0.0273 | **Steel shroom** |  | `Plant_SteelShroom` · Tunneler Expanded |
| 0.0273 | **psyshroom** |  | `Plant_Psykshroom` · Psyshrooms |
| 0.0273 | **Giant shroom** |  | `Plant_Giantshroom` · ? |
| 0.0273 | **Heal shroom** |  | `Plant_Healshroom` · ? |
| 0.0273 | **Jelly shroom** |  | `Plant_Jellyshroom` · ? |
| 0.0273 | **Meatshroom** |  | `Plant_Meatshroom` · ? |
| 0.0273 | **Micro shroom** |  | `Plant_Microshroom` · ? |
| 0.0144 | **blastpod shroom** |  | `BMT_Blastpod` · Biomes! Caverns |
| 0.0144 | **Grey Lady** |  | `BMT_GreyLady` · Biomes! Caverns |
| 0.0144 | **Timbercap** |  | `Plant_Timbercap` · ? |
| 0.0144 | **nutrifungus** |  | `Plant_Nutrifungus` · Ideology |

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

*was 8 inherited plants → now **7** assigned*

| commonality | plant | | mod |
|---:|---|---|---|
| 0.9 | **fireweed** |  | `Plant_Fireweed` · Odyssey |
| 0.72 | **fireweed** |  | `GRim1Fireweed` · GRiNDTerra Biomes |
| 0.6 | **magma cactus** |  | `GRimMagmaCactus` · GRiNDTerra Biomes |
| 0.5 | **fireweed** |  | `GRimFireweed` · GRiNDTerra Biomes |
| 0.4 | **sagecrust** |  | `BMT_Sagecrust` · Biomes! Caverns |
| 0.35 | **primordial grass** |  | `IronScruff_PrimordialGrass` · Primordial Geysers |
| 0.3 | **primordial tall grass** |  | `IronScruff_PrimordialTallGrass` · Primordial Geysers |

### `LavaField` — 15 tiles · 38 … 47 °C (median 42) · plantDensity 0.5

*was 12 inherited plants → now **4** assigned*

| commonality | plant | | mod |
|---:|---|---|---|
| 0.7 | **magma cactus** |  | `Plant_MagmaCactus` · Odyssey |
| 0.6 | **fire lavender** |  | `BMT_FireLavender` · Biomes! Caverns |
| 0.25 | **bindweed** |  | `IronScruff_Bindweed` · Primordial Geysers |
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

### `Scarlands` — 90 tiles · 58 … 66 °C (median 60) · plantDensity 0.4

*was 16 inherited plants → now **4** assigned*

| commonality | plant | | mod |
|---:|---|---|---|
| 0.8 | **rustpuff** |  | `BMT_RustPuff` · Biomes! Caverns |
| 0.6 | **burned shroom** |  | `BMT_BurnedMushroom` · Biomes! Caverns |
| 0.4 | **dark gamma** |  | `AG_DarkGamma` · Alpha Genes |
| 0.2 | **burned stump** |  | `BurnedTree` · Core |

## H. alien

### `AB_GelatinousSuperorganism` — 96 tiles · -3 … 22 °C (median 13) · plantDensity 0.2

*was 7 inherited plants → now **7** assigned*

| commonality | plant | | mod |
|---:|---|---|---|
| 0.9 | **slimy fern** |  | `AB_SlimyFern` · Alpha Biomes |
| 0.6 | **slimecasia** |  | `AB_Slimecasia` · Alpha Biomes |
| 0.3 | **slimy tree** |  | `AB_SlimyTree` · Alpha Biomes |
| 0.3 | **vysp strands** |  | `VEE_Plant_VyspStrands` · Vanilla Events Expanded |
| 0.25 | **cyllen cluster** |  | `VEE_Plant_CyllenCluster` · Vanilla Events Expanded |
| 0.2 | **large slimy tree** |  | `AB_LargeSlimyTree` · Alpha Biomes |
| 0.2 | **myrlox tree** |  | `VEE_Plant_MyrloxTree` · Vanilla Events Expanded |

### `AB_OcularForest` — 3 tiles · 23 … 23 °C (median 23) · plantDensity 0.35

*was 11 inherited plants → now **17** assigned*

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
| 0.35 | **pink grass** |  | `VEE_Plant_PinkGrass` · Vanilla Events Expanded |
| 0.3 | **tall pink grass** |  | `VEE_Plant_TallPinkGrass` · Vanilla Events Expanded |
| 0.22 | **phorax tree** |  | `VEE_Plant_PhoraxTree` · Vanilla Events Expanded |
| 0.2 | **mutated ocular tree** | 🌳 | `AB_AlienTree_Polluted` · Alpha Biomes |
| 0.2 | **ocular tree** | 🌳 | `AA_AlienTree` · Alpha Animals |
| 0.2 | **pollen trumpet** |  | `AA_Plant_PollenTrumpet` · Alpha Animals |
| 0.2 | **xyril tree** |  | `VEE_Plant_XyrilTree` · Vanilla Events Expanded |
| 0.15 | **half transformed ocular tree** | 🌳 | `AB_HalfAlienTree` · Alpha Biomes |
| 0.1 | **heat resistant ambrosia bush** |  | `AA_Heat_Ambrosia` · Alpha Animals |
