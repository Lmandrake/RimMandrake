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

**5 families · 23 biomes · 143 plants, all distinct.** 10 biomes carry no flora by design: `AB_MechanoidIntrusion`, `IceSheet`, `Lake`, `Ocean`, `RUT_BlueDesert`, `RUT_GreySea`, `RUT_NightsideIce`, `RUT_TheScald`, `RUT_TwilightSea`, `SeaIce`.

## A. dayside desert, badlands and the river jungles

### `Desert` — 3,932 tiles · -16 … 62 °C (median 26) · plantDensity 0.45

*was 30 inherited plants → now **5** assigned*

| commonality | plant | | mod |
|---:|---|---|---|
| 0.6 | **hardy grass** |  | `AB_HardyGrass` · Alpha Biomes |
| 0.3 | **wild chak-root plant** |  | `Plant_Chakroot_Wild` · Star Wars Animal Collection (Continued) |
| 0.2 | **wild hubba gourd plant** |  | `Plant_HubbaGourd_Wild` · Star Wars Animal Collection (Continued) |
| 0.12 | **aaklac** |  | `AB_Aaklac` · Alpha Biomes |
| 0.06 | **dessert tree** | 🌳 | `AB_DessertTree` · Alpha Biomes |

### `AB_PropaneLakes` — 2,531 tiles · -82 … -42 °C (median -62) · plantDensity 0.75

*was 6 inherited plants → now **4** assigned*

| commonality | plant | | mod |
|---:|---|---|---|
| 1 | **crystal horn** |  | `AB_CrystalHorn` · Alpha Biomes |
| 0.8 | **crystal flower** |  | `AB_CrystalFlower` · Alpha Biomes |
| 0.6 | **frost leaf** |  | `AB_FrostLeaf` · Alpha Biomes |
| 0.4 | **rime nodules** |  | `AB_RimeNodules` · Alpha Biomes |

### `ZBiome_Badlands` — 985 tiles · -21 … 59 °C (median 27) · plantDensity 0.3

*was 23 inherited plants → now **6** assigned*

| commonality | plant | | mod |
|---:|---|---|---|
| 1 | **hardy grass** |  | `AB_HardyGrass` · Alpha Biomes |
| 0.8 | **moss** |  | `GRimMoss` · GRiNDTerra Biomes |
| 0.5 | **twisting thorngrass** |  | `BMT_Plant_TwistingThorngrass` · Biomes! Polluted Lands |
| 0.4 | **twisting thornweed** |  | `BMT_Plant_TwistingThornweed` · Biomes! Polluted Lands |
| 0.2 | **twisting thornwood** | 🌳 | `BMT_Plant_TreeTwistingThornwood` · Biomes! Polluted Lands |
| 0.15 | **gargantuan lithops** |  | `AB_GargantuanLithops` · Alpha Biomes |

### `PoisonForest` — 557 tiles · -10 … 41 °C (median 11) · plantDensity 0.85

*was 35 inherited plants → now **9** assigned*

| commonality | plant | | mod |
|---:|---|---|---|
| 0.6 | **twisting thornwood** | 🌳 | `BMT_Plant_TreeTwistingThornwood` · Biomes! Polluted Lands |
| 0.5 | **crystal flower** |  | `AB_CrystalFlower` · Alpha Biomes |
| 0.5 | **martyr tree** | 🌳 | `BMT_Plant_TreeMartyr` · Biomes! Polluted Lands |
| 0.4 | **blood bouquet** |  | `AB_BloodBouquet` · Alpha Biomes |
| 0.4 | **crystal horn** |  | `AB_CrystalHorn` · Alpha Biomes |
| 0.4 | **raven nettle** |  | `AB_RavenNettle` · Alpha Biomes |
| 0.3 | **agaritox** | 🌳 | `AB_GiantAgariTox` · Alpha Biomes |
| 0.3 | **red bugloss** |  | `AB_RedBugloss` · Alpha Biomes |
| 0.2 | **keening cordax** | 🌳 | `AB_KeeningCordax` · Alpha Biomes |

### `BiomeCypreJungle` — 235 tiles · 36 … 64 °C (median 46) · plantDensity 0.85

*was 18 inherited plants → now **11** assigned*

| commonality | plant | | mod |
|---:|---|---|---|
| 3 | **deep jungle tree** | 🌳 | `AB_JungleTree` · Alpha Biomes |
| 1.5 | **wild hydenock tree** | 🌳 | `Plant_HydenockTree_Wild` · Star Wars Animal Collection (Continued) |
| 1.2 | **wild jogan tree** | 🌳 | `Plant_JoganTree_Wild` · Star Wars Animal Collection (Continued) |
| 1 | **giant leaf** |  | `BMT_GiantLeaf` · Biomes! Caverns |
| 1 | **wild muja fruit bush** |  | `Plant_MujaFruit_Wild` · Star Wars Animal Collection (Continued) |
| 0.8 | **wild hubba gourd plant** |  | `Plant_HubbaGourd_Wild` · Star Wars Animal Collection (Continued) |
| 0.6 | **sugar famewort** |  | `AB_SugarFamewort` · Alpha Biomes |
| 0.6 | **wild felucian glowspore** | 🌳 | `Plant_FelucianGlowspore_Wild` · Star Wars Animal Collection (Continued) |
| 0.5 | **wild bubble spore plant** |  | `Plant_Bubblespore_Wild` · Star Wars Animal Collection (Continued) |
| 0.5 | **wild chak-root plant** |  | `Plant_Chakroot_Wild` · Star Wars Animal Collection (Continued) |
| 0.5 | **wild tooke-trap plant** |  | `Plant_TookeTrap_Wild` · Star Wars Animal Collection (Continued) |

### `ZBiome_Grasslands` — 222 tiles · 28 … 65 °C (median 54) · plantDensity 0.95

*was 45 inherited plants → now **3** assigned*

| commonality | plant | | mod |
|---:|---|---|---|
| 2.4 | **ochreskal** |  | `Plant_YellowGrass` · Odyssey |
| 2 | **tall ochreskal** |  | `Plant_YellowTallGrass` · Odyssey |
| 0.4 | **hardy grass** |  | `AB_HardyGrass` · Alpha Biomes |

### `AB_OcularForest` — 179 tiles · 23 … 57 °C (median 32) · plantDensity 0.35

*was 17 inherited plants → now **10** assigned*

| commonality | plant | | mod |
|---:|---|---|---|
| 1 | **ocular grass** |  | `AB_AlienGrass` · Alpha Biomes |
| 1 | **ocular tree** | 🌳 | `AB_AlienTree` · Alpha Biomes |
| 0.6 | **flowering ocular grass** |  | `AB_EyeGrass` · Alpha Biomes |
| 0.6 | **ocular plant** |  | `AB_RedLeaves` · Alpha Biomes |
| 0.5 | **half transformed ocular tree** | 🌳 | `AB_HalfAlienTree` · Alpha Biomes |
| 0.5 | **ocular plant** |  | `AB_RedPlantsTall` · Alpha Biomes |
| 0.4 | **globular aberration** |  | `AB_GlobularPlant` · Alpha Biomes |
| 0.4 | **tentacular aberration** |  | `AB_TentacularPlant` · Alpha Biomes |
| 0.3 | **blood bouquet** |  | `AB_BloodBouquet` · Alpha Biomes |
| 0.15 | **mutated ocular tree** | 🌳 | `AB_AlienTree_Polluted` · Alpha Biomes |

### `AB_FeraliskInfestedJungle` — 161 tiles · 36 … 63 °C (median 49) · plantDensity 0.9

*was 39 inherited plants → now **7** assigned*

| commonality | plant | | mod |
|---:|---|---|---|
| 1.1 | **deep jungle tree** | 🌳 | `AB_JungleTree` · Alpha Biomes |
| 1 | **chokevine** |  | `RG_Plant_TropicalChokevine` · ReGrowth 2 |
| 0.4 | **tangle tea** |  | `AB_TangleTea` · Alpha Biomes |
| 0.3 | **wild tooke-trap plant** |  | `Plant_TookeTrap_Wild` · Star Wars Animal Collection (Continued) |
| 0.15 | **gomphoeria** |  | `AB_Gomphoeria` · Alpha Biomes |
| 0.07 | **red bugloss** |  | `AB_RedBugloss` · Alpha Biomes |
| 0.05 | **aaklac** |  | `AB_Aaklac` · Alpha Biomes |

### `RUT_PropaneLake` — 57 tiles · -82 … -75 °C (median -79) · plantDensity 0  🔴 **`plantDensity` is near zero — this roster will almost never be seen**

*was 0 inherited plants → now **4** assigned*

| commonality | plant | | mod |
|---:|---|---|---|
| 1 | **crystal horn** |  | `AB_CrystalHorn` · Alpha Biomes |
| 0.8 | **crystal flower** |  | `AB_CrystalFlower` · Alpha Biomes |
| 0.6 | **frost leaf** |  | `AB_FrostLeaf` · Alpha Biomes |
| 0.4 | **rime nodules** |  | `AB_RimeNodules` · Alpha Biomes |

### `COMIGO_GreaterSwamp_Tropical` — 43 tiles · 38 … 52 °C (median 46) · plantDensity 0.99

*was 11 inherited plants → now **7** assigned*

| commonality | plant | | mod |
|---:|---|---|---|
| 1.5 | **wild hydenock tree** | 🌳 | `Plant_HydenockTree_Wild` · Star Wars Animal Collection (Continued) |
| 1.2 | **keening cordax** | 🌳 | `AB_KeeningCordax` · Alpha Biomes |
| 0.8 | **giant leaf** |  | `BMT_GiantLeaf` · Biomes! Caverns |
| 0.6 | **wild jogan tree** | 🌳 | `Plant_JoganTree_Wild` · Star Wars Animal Collection (Continued) |
| 0.5 | **iashiphus** |  | `AB_Iashiphus` · Alpha Biomes |
| 0.4 | **gomphoeria** |  | `AB_Gomphoeria` · Alpha Biomes |
| 0.4 | **wild chak-root plant** |  | `Plant_Chakroot_Wild` · Star Wars Animal Collection (Continued) |

## B. the mycoid and fire massif

### `ExtremeDesert` — 3,172 tiles · 16 … 66 °C (median 48) · plantDensity 0.008  🔴 **`plantDensity` is near zero — this roster will almost never be seen**

*was 12 inherited plants → now **2** assigned*

| commonality | plant | | mod |
|---:|---|---|---|
| 0.05 | **bloddle plant** |  | `Plant_Bloddle` · Star Wars Animal Collection (Continued) |
| 0.04 | **giant stikehr** |  | `AB_GiantStikehr` · Alpha Biomes |

### `AB_MycoticJungle` — 2,258 tiles · -42 … 24 °C (median -19) · plantDensity 0.2

*was 35 inherited plants → now **32** assigned*

| commonality | plant | | mod |
|---:|---|---|---|
| 10 | **bryolux** |  | `AB_Bryolux` · Alpha Biomes |
| 3 | **glowstool** |  | `AB_Glowstool` · Alpha Biomes |
| 2 | **agarilux** |  | `AB_Agarilux` · Alpha Biomes |
| 2 | **giant agarilux** |  | `AB_GiantAgarilux` · Alpha Biomes |
| 1 | **glowing agarilux** |  | `AB_GlowingAgarilux` · Alpha Biomes |
| 0.5 | **lilac beacon** |  | `AB_LilacBeacon` · Alpha Biomes |
| 0.5 | **witches' oyster** |  | `AB_WitchesOyster` · Alpha Biomes |
| 0.5 | **dewshrooms** |  | `BMT_Dewshrooms` · Biomes! Caverns |
| 0.5 | **mold fruiting bodies** |  | `BMT_FruitingBodies` · Biomes! Caverns |
| 0.5 | **nuitae** |  | `BMT_Nuitae` · Biomes! Caverns |
| 0.5 | **wrinklecap** |  | `BMT_Wrinklecap` · Biomes! Caverns |
| 0.4 | **arpeau** | 🌳 | `BMT_Arpeau` · Biomes! Caverns |
| 0.4 | **nogtyl** | 🌳 | `BMT_Nogtyl` · Biomes! Caverns |
| 0.3 | **recurved stropharia** |  | `AB_RecurvedStropharia` · Alpha Biomes |
| 0.3 | **flakespire fungus** | 🌳 | `BMT_FlakespireFungus` · Biomes! Caverns |
| 0.3 | **pusmelon** |  | `BMT_Pusmelon` · Biomes! Caverns |
| 0.3 | **rustpuff** |  | `BMT_RustPuff` · Biomes! Caverns |
| 0.3 | **sagecrust** |  | `BMT_Sagecrust` · Biomes! Caverns |
| 0.2 | **arbuscular mycorrhiza** |  | `AB_ArbuscularMycorrhiza` · Alpha Biomes |
| 0.2 | **slimy pholiota** |  | `AB_SlimyPholiota` · Alpha Biomes |
| 0.2 | **bleeding tooth** |  | `BMT_BleedingTooth` · Biomes! Caverns |
| 0.2 | **brightbells** |  | `BMT_Brightbells` · Biomes! Caverns |
| 0.2 | **crimson cap** |  | `BMT_CrimsonCap` · Biomes! Caverns |
| 0.2 | **Grey Lady** |  | `BMT_GreyLady` · Biomes! Caverns |
| 0.2 | **shine cap** | 🌳 | `BMT_Shinecap` · Biomes! Caverns |
| 0.2 | **violet wimple** |  | `BMT_VioletWimple` · Biomes! Caverns |
| 0.15 | **mortal morel** |  | `BMT_MortalMorelPlant` · Biomes! Caverns |
| 0.1 | **agaricus domecap** |  | `AB_AgaricusDomeCap` · Alpha Biomes |
| 0.1 | **dribbling cap** |  | `AB_DribblingCap` · Alpha Biomes |
| 0.1 | **skulltop** | 🌳 | `BMT_Skulltop` · Biomes! Caverns |
| 0.05 | **blastpod shroom** |  | `BMT_Blastpod` · Biomes! Caverns |
| 0.01 | **Agarilux Prime** |  | `AB_AgariluxPrime` · Alpha Biomes |

### `AB_RockyCrags` — 1,170 tiles · -24 … 31 °C (median -10) · plantDensity 0.085

*was 27 inherited plants → now **6** assigned*

| commonality | plant | | mod |
|---:|---|---|---|
| 1 | **grass** |  | `AB_GlowingGrass` · Alpha Biomes |
| 0.6 | **toxic gamma** | 🌳 | `AB_ToxicGamma` · Alpha Biomes |
| 0.5 | **giant gamma** |  | `AB_GiantGamma` · Alpha Biomes |
| 0.5 | **wild ragadast** |  | `AB_WildRadagast` · Alpha Biomes |
| 0.3 | **giant stikehr** |  | `AB_GiantStikehr` · Alpha Biomes |
| 0.2 | **giant septimum** | 🌳 | `AB_GiantSeptimum` · Alpha Biomes |

### `ZBiome_DesertOasis` — 223 tiles · 18 … 64 °C (median 35) · plantDensity 0.7

*was 50 inherited plants → now **4** assigned*

| commonality | plant | | mod |
|---:|---|---|---|
| 1 | **sarnreed** |  | `Plant_Reeds` · Odyssey |
| 0.4 | **green rock fern** |  | `AB_GreenRockFern` · Alpha Biomes |
| 0.4 | **dewshrooms** |  | `BMT_Dewshrooms` · Biomes! Caverns |
| 0.12 | **ambrosia bush** |  | `Plant_Ambrosia` · Core |

### `AB_GelatinousSuperorganism` — 96 tiles · -3 … 22 °C (median 13) · plantDensity 0.2

*was 7 inherited plants → now **6** assigned*

| commonality | plant | | mod |
|---:|---|---|---|
| 1 | **tall slimy grass** |  | `AB_TallSlimyGrass` · Alpha Biomes |
| 0.5 | **slimy fern** |  | `AB_SlimyFern` · Alpha Biomes |
| 0.5 | **slimy tree** |  | `AB_SlimyTree` · Alpha Biomes |
| 0.4 | **slimecasia** |  | `AB_Slimecasia` · Alpha Biomes |
| 0.4 | **slimy pholiota** |  | `AB_SlimyPholiota` · Alpha Biomes |
| 0.3 | **large slimy tree** |  | `AB_LargeSlimyTree` · Alpha Biomes |

### `AB_PyroclasticConflagration` — 31 tiles · 43 … 56 °C (median 50) · plantDensity 0.4

*was 5 inherited plants → now **13** assigned*

| commonality | plant | | mod |
|---:|---|---|---|
| 0.9 | **fireweed** |  | `Plant_Fireweed` · Odyssey |
| 0.7 | **magma cactus** |  | `Plant_MagmaCactus` · Odyssey |
| 0.6 | **fire lavender** |  | `BMT_FireLavender` · Biomes! Caverns |
| 0.5 | **gamma** |  | `AG_Gamma` · Alpha Genes |
| 0.4 | **sagecrust** |  | `BMT_Sagecrust` · Biomes! Caverns |
| 0.35 | **primordial grass** |  | `IronScruff_PrimordialGrass` · Primordial Geysers |
| 0.3 | **giant gamma** |  | `AB_GiantGamma` · Alpha Biomes |
| 0.3 | **tinkle grass** |  | `AB_TinkleGrass` · Alpha Biomes |
| 0.3 | **primordial tall grass** |  | `IronScruff_PrimordialTallGrass` · Primordial Geysers |
| 0.25 | **septimum** |  | `AG_Septimum` · Alpha Genes |
| 0.25 | **bindweed** |  | `IronScruff_Bindweed` · Primordial Geysers |
| 0.2 | **firevine tree** | 🌳 | `AB_FirevineTree` · Alpha Biomes |
| 0.2 | **heatsink fungus** | 🌳 | `BMT_HeatsinkFungus` · Biomes! Caverns |

### `LavaField` — 8 tiles · 42 … 47 °C (median 44) · plantDensity 0.5

*was 4 inherited plants → now **13** assigned*

| commonality | plant | | mod |
|---:|---|---|---|
| 0.9 | **fireweed** |  | `Plant_Fireweed` · Odyssey |
| 0.7 | **magma cactus** |  | `Plant_MagmaCactus` · Odyssey |
| 0.6 | **fire lavender** |  | `BMT_FireLavender` · Biomes! Caverns |
| 0.5 | **gamma** |  | `AG_Gamma` · Alpha Genes |
| 0.4 | **sagecrust** |  | `BMT_Sagecrust` · Biomes! Caverns |
| 0.35 | **primordial grass** |  | `IronScruff_PrimordialGrass` · Primordial Geysers |
| 0.3 | **giant gamma** |  | `AB_GiantGamma` · Alpha Biomes |
| 0.3 | **tinkle grass** |  | `AB_TinkleGrass` · Alpha Biomes |
| 0.3 | **primordial tall grass** |  | `IronScruff_PrimordialTallGrass` · Primordial Geysers |
| 0.25 | **septimum** |  | `AG_Septimum` · Alpha Genes |
| 0.25 | **bindweed** |  | `IronScruff_Bindweed` · Primordial Geysers |
| 0.2 | **firevine tree** | 🌳 | `AB_FirevineTree` · Alpha Biomes |
| 0.2 | **heatsink fungus** | 🌳 | `BMT_HeatsinkFungus` · Biomes! Caverns |

### `Volcano` — 5 tiles · 42 … 47 °C (median 42) · plantDensity 0.16

*was 7 inherited plants → now **13** assigned*

| commonality | plant | | mod |
|---:|---|---|---|
| 0.9 | **fireweed** |  | `Plant_Fireweed` · Odyssey |
| 0.7 | **magma cactus** |  | `Plant_MagmaCactus` · Odyssey |
| 0.6 | **fire lavender** |  | `BMT_FireLavender` · Biomes! Caverns |
| 0.5 | **gamma** |  | `AG_Gamma` · Alpha Genes |
| 0.4 | **sagecrust** |  | `BMT_Sagecrust` · Biomes! Caverns |
| 0.35 | **primordial grass** |  | `IronScruff_PrimordialGrass` · Primordial Geysers |
| 0.3 | **giant gamma** |  | `AB_GiantGamma` · Alpha Biomes |
| 0.3 | **tinkle grass** |  | `AB_TinkleGrass` · Alpha Biomes |
| 0.3 | **primordial tall grass** |  | `IronScruff_PrimordialTallGrass` · Primordial Geysers |
| 0.25 | **septimum** |  | `AG_Septimum` · Alpha Genes |
| 0.25 | **bindweed** |  | `IronScruff_Bindweed` · Primordial Geysers |
| 0.2 | **firevine tree** | 🌳 | `AB_FirevineTree` · Alpha Biomes |
| 0.2 | **heatsink fungus** | 🌳 | `BMT_HeatsinkFungus` · Biomes! Caverns |

## C. contamination

### `Wasteland` — 1,126 tiles · -23 … 54 °C (median 14) · plantDensity 0.12

*was 44 inherited plants → now **25** assigned*

| commonality | plant | | mod |
|---:|---|---|---|
| 1.2 | **toxigrass** |  | `RG_Plant_ToxiGrass` · ReGrowth 2 |
| 0.6271 | **tall toxigrass** |  | `RG_Plant_TallToxiGrass` · ReGrowth 2 |
| 0.3957 | **toxi grass** |  | `AB_ToxiGrass` · Alpha Biomes |
| 0.2956 | **gutter plantain** |  | `BMT_Plant_GutterPlantain` · Biomes! Polluted Lands |
| 0.2956 | **toxic ivy** |  | `BMT_Plant_ToxicIvy` · Biomes! Polluted Lands |
| 0.2956 | **twisted dandelion** |  | `BMT_Plant_TwistedDandelion` · Biomes! Polluted Lands |
| 0.2068 | **tall grass** |  | `PoisonPlantTallGrass` · Advanced Biomes (Continued) |
| 0.167 | **ashskal** |  | `Plant_GrayGrass` · Biotech |
| 0.167 | **poison shrub** |  | `PoisonShrub` · Advanced Biomes (Continued) |
| 0.1305 | **scorched stars** |  | `BMT_Plant_ScorchedStars` · Biomes! Polluted Lands |
| 0.1305 | **snaketails** |  | `BMT_Plant_Snaketails` · Biomes! Polluted Lands |
| 0.1305 | **bush** |  | `PoisonPlantBush` · Advanced Biomes (Continued) |
| 0.0975 | **pox sorghum** |  | `BMT_Plant_PoxSorghum` · Biomes! Polluted Lands |
| 0.0975 | **tumorbulb hyacinth** |  | `BMT_Plant_TumorbulbHyacinth` · Biomes! Polluted Lands |
| 0.0682 | **weeping toxberry** |  | `AB_WeepingToxberry` · Alpha Biomes |
| 0.0682 | **wild rashroot** |  | `BMT_Plant_WildRashroot` · Biomes! Polluted Lands |
| 0.0682 | **toxipotato plant** |  | `Plant_Toxipotato` · Biotech |
| 0.043 | **doomsprout** |  | `BMT_Plant_Doomsprout` · Biomes! Polluted Lands |
| 0.043 | **eclipsus** |  | `BMT_Plant_EclipsusFlower` · Biomes! Polluted Lands |
| 0.043 | **eclipsus** |  | `BMT_Plant_EclipsusLeaves` · Biomes! Polluted Lands |
| 0.043 | **rainbow tongue** |  | `BMT_RainbowTongue` · Biomes! Polluted Lands |
| 0.0225 | **toxibulb** | 🌳 | `AB_ToxiBulb` · Alpha Biomes |
| 0.0225 | **polux tree** | 🌳 | `Plant_TreePolux` · Biotech |
| 0.0157 | **giant toxic flower** | 🌳 | `AB_GiantToxicFlower` · Alpha Biomes |
| 0.0157 | **polux bush** | 🌳 | `VRE_PoluxBush` · Vanilla Races Expanded - Phytokin |

### `AB_MiasmicMangrove` — 93 tiles · 26 … 59 °C (median 43) · plantDensity 0.7

*was 16 inherited plants → now **7** assigned*

| commonality | plant | | mod |
|---:|---|---|---|
| 25 | **mangrove tree** | 🌳 | `AB_MangroveTree` · Alpha Biomes |
| 8 | **parasitic mangrove** |  | `AB_ParasiticMangrove` · Alpha Biomes |
| 6 | **mangrove palm** | 🌳 | `AB_MangrovePalm` · Alpha Biomes |
| 1.5 | **tangleroot mangrove** | 🌳 | `BMT_Plant_TreeTanglerootMangrove` · Biomes! Polluted Lands |
| 0.8 | **sewer reed** |  | `BMT_Plant_SewerReed` · Biomes! Polluted Lands |
| 0.6 | **rainbow tongue** |  | `BMT_RainbowTongue` · Biomes! Polluted Lands |
| 0.5 | **snaketails** |  | `BMT_Plant_Snaketails` · Biomes! Polluted Lands |

### `Scarlands` — 90 tiles · 58 … 66 °C (median 60) · plantDensity 0.4

*was 4 inherited plants → now **1** assigned*

| commonality | plant | | mod |
|---:|---|---|---|
| 0.25 | **scorched stars** |  | `BMT_Plant_ScorchedStars` · Biomes! Polluted Lands |

## D. the shrub belt

### `AridShrubland` — 665 tiles · -15 … 59 °C (median 20) · plantDensity 0.72

*was 66 inherited plants → now **10** assigned*

| commonality | plant | | mod |
|---:|---|---|---|
| 0.9 | **low grell** |  | `Plant_ShrubLow` · Core |
| 0.5 | **grass** |  | `RG_Plant_AridGrass` · ReGrowth 2 |
| 0.3 | **brambles** |  | `Plant_Brambles` · ReGrowth 2 |
| 0.3 | **grellbush** |  | `Plant_Bush` · Core |
| 0.3 | **ripthorn** |  | `Plant_Ripthorn` · Biotech |
| 0.25 | **wild healroot** |  | `Plant_HealrootWild` · Core |
| 0.22 | **wild nysyllin plant** |  | `Plant_Nysyllin_Wild` · Star Wars Animal Collection (Continued) |
| 0.2 | **creep stern** |  | `RG_Plant_CreepStern` · ReGrowth 2 |
| 0.2 | **crimson cushion** |  | `RG_Plant_CrimsonCushion` · ReGrowth 2 |
| 0.2 | **dervish** |  | `RG_Plant_Dervish` · ReGrowth 2 |

## E. the tar

### `AB_TarPits` — 42 tiles · -6 … 20 °C (median 1) · plantDensity 0.25

*was 9 inherited plants → now **1** assigned*

| commonality | plant | | mod |
|---:|---|---|---|
| 0.6 | **tar puddle** |  | `AB_TarPuddle` · Alpha Biomes |
