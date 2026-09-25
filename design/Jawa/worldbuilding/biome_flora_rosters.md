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
temperatures later"* — 670 of 696 plants will not grow below 0 °C and half this planet is
colder than that. Making these rosters actually live is `NORMALIZE_TEMPERATURE_TOLERANCES_1`.

**5 families · 21 biomes · 137 plants, all distinct.** 10 biomes carry no flora by design: `IceSheet`, `Lake`, `Ocean`, `RUT_GreySea`, `RUT_NightsideIce`, `RUT_PropaneLake`, `RUT_RustCathedral`, `RUT_TheScald`, `RUT_TwilightSea`, `SeaIce`.

## A. dayside desert, badlands and the river jungles

### `RUT_Umbra` — 2,531 tiles · -82 … -42 °C (median -62) · plantDensity 0.75

*was 4 inherited plants → now **4** assigned*

| commonality | plant | | mod |
|---:|---|---|---|
| 1 | **crystal horn** |  | `AB_CrystalHorn` · Alpha Biomes |
| 0.6 | **frost leaf** |  | `AB_FrostLeaf` · Alpha Biomes |
| 0.4 | **rime nodules** |  | `AB_RimeNodules` · Alpha Biomes |
| 0.35 | **poison shrub** |  | `PoisonShrub` · Advanced Biomes (Continued) |

### `RUT_Desert` — 2,390 tiles · -4 … 51 °C (median 25) · plantDensity 0.05

*was 4 inherited plants → now **9** assigned*

| commonality | plant | | mod |
|---:|---|---|---|
| 1.5 | **RM_Leachmoss** | | `RM_Leachmoss` · newer than the def dump |
| 0.8 | **ultracactus** |  | `RSW_Ultracactus` · RimMandrake: SW — Bestiary |
| 0.6 | **surra grass** |  | `RSW_Dunegrass` · RimMandrake: SW — Bestiary |
| 0.3 | **wild chak-root plant** |  | `RSW_Plant_Chakroot_Wild` · RimMandrake: SW — Bestiary |
| 0.25 | **RM_Venomvine** | | `RM_Venomvine` · newer than the def dump |
| 0.2 | **wild hubba gourd plant** |  | `RSW_Plant_HubbaGourd_Wild` · RimMandrake: SW — Bestiary |
| 0.12 | **vellara bloom** |  | `RSW_VellaraBloom` · RimMandrake: SW — Bestiary |
| 0.1 | **RUT_Vorrel** | | `RUT_Vorrel` · newer than the def dump |
| 0.06 | **dommo tree** | 🌳 | `RSW_SweetbarkTree` · RimMandrake: SW — Bestiary |

### `RUT_BlueDesert` — 1,029 tiles · -58 … -19 °C (median -43) · plantDensity 0  🔴 **`plantDensity` is near zero — this roster will almost never be seen**

*was 3 inherited plants → now **3** assigned*

| commonality | plant | | mod |
|---:|---|---|---|
| 0.6 | **toxi grass** |  | `AB_ToxiGrass` · Alpha Biomes |
| 0.4 | **crystal horn** |  | `AB_CrystalHorn` · Alpha Biomes |
| 0.4 | **tall grass** |  | `PoisonPlantTallGrass` · Advanced Biomes (Continued) |

### `RUT_CrackedLands` — 970 tiles · -21 … 59 °C (median 28) · plantDensity 0.15

*was 6 inherited plants → now **6** assigned*

| commonality | plant | | mod |
|---:|---|---|---|
| 1 | **hardy grass** |  | `AB_HardyGrass` · Alpha Biomes |
| 0.8 | **moss** |  | `GRimMoss` · GRiNDTerra Biomes |
| 0.5 | **twisting thorngrass** |  | `RUT_TwistingThorngrass` · RimUtinni Patches (Jawa campaign) |
| 0.4 | **twisting thornweed** |  | `RUT_TwistingThornweed` · RimUtinni Patches (Jawa campaign) |
| 0.2 | **twisting thornwood** | 🌳 | `RUT_TwistingThornwood` · RimUtinni Patches (Jawa campaign) |
| 0.15 | **gargantuan lithops** |  | `AB_GargantuanLithops` · Alpha Biomes |

### `RUT_PoisonForest` — 546 tiles · -10 … 41 °C (median 11) · plantDensity 0.5

*was 9 inherited plants → now **9** assigned*

| commonality | plant | | mod |
|---:|---|---|---|
| 0.6 | **twisting thornwood** | 🌳 | `RUT_TwistingThornwood` · RimUtinni Patches (Jawa campaign) |
| 0.5 | **martyr tree** | 🌳 | `RUT_TreeMartyr` · RimUtinni Patches (Jawa campaign) |
| 0.5 | **crystal flower** |  | `AB_CrystalFlower` · Alpha Biomes |
| 0.4 | **blood bouquet** |  | `AB_BloodBouquet` · Alpha Biomes |
| 0.4 | **raven nettle** |  | `AB_RavenNettle` · Alpha Biomes |
| 0.3 | **red bugloss** |  | `AB_RedBugloss` · Alpha Biomes |
| 0.3 | **agaritox** | 🌳 | `AB_GiantAgariTox` · Alpha Biomes |
| 0.2 | **keening cordax** | 🌳 | `AB_KeeningCordax` · Alpha Biomes |
| 0.08 | **giant toxic flower** | 🌳 | `AB_GiantToxicFlower` · Alpha Biomes |

### `RUT_Greentide` — 235 tiles · 36 … 64 °C (median 46) · plantDensity 0.9

*was 11 inherited plants → now **11** assigned*

| commonality | plant | | mod |
|---:|---|---|---|
| 3 | **deep jungle tree** | 🌳 | `AB_JungleTree` · Alpha Biomes |
| 1.5 | **wild hydenock tree** | 🌳 | `Plant_HydenockTree_Wild` · Star Wars Animal Collection (Continued) |
| 1.2 | **wild jogan tree** | 🌳 | `Plant_JoganTree_Wild` · Star Wars Animal Collection (Continued) |
| 1 | **wild muja fruit bush** |  | `Plant_MujaFruit_Wild` · Star Wars Animal Collection (Continued) |
| 1 | **giant leaf** |  | `RUT_GiantLeaf` · RimUtinni Patches (Jawa campaign) |
| 0.8 | **wild hubba gourd plant** |  | `Plant_HubbaGourd_Wild` · Star Wars Animal Collection (Continued) |
| 0.6 | **wild felucian glowspore** | 🌳 | `Plant_FelucianGlowspore_Wild` · Star Wars Animal Collection (Continued) |
| 0.6 | **sugar famewort** |  | `AB_SugarFamewort` · Alpha Biomes |
| 0.5 | **wild tooke-trap plant** |  | `Plant_TookeTrap_Wild` · Star Wars Animal Collection (Continued) |
| 0.5 | **wild bubble spore plant** |  | `Plant_Bubblespore_Wild` · Star Wars Animal Collection (Continued) |
| 0.5 | **wild chak-root plant** |  | `Plant_Chakroot_Wild` · Star Wars Animal Collection (Continued) |

### `ZBiome_Grasslands` — 222 tiles · 28 … 65 °C (median 54) · plantDensity 0.95

*was 1 inherited plants → now **1** assigned*

| commonality | plant | | mod |
|---:|---|---|---|
| 4 | **quickgrass** |  | `RM_FE_Plant_Quickgrass` · Pyrelands |

### `RUT_Contagion` — 179 tiles · 23 … 57 °C (median 32) · plantDensity 0.35

*was 10 inherited plants → now **10** assigned*

| commonality | plant | | mod |
|---:|---|---|---|
| 1 | **ocular tree** | 🌳 | `AB_AlienTree` · Alpha Biomes |
| 1 | **ocular grass** |  | `AB_AlienGrass` · Alpha Biomes |
| 0.6 | **ocular plant** |  | `AB_RedLeaves` · Alpha Biomes |
| 0.5 | **ocular plant** |  | `AB_RedPlantsTall` · Alpha Biomes |
| 0.5 | **half transformed ocular tree** | 🌳 | `AB_HalfAlienTree` · Alpha Biomes |
| 0.4 | **tentacular aberration** |  | `AB_TentacularPlant` · Alpha Biomes |
| 0.4 | **globular aberration** |  | `AB_GlobularPlant` · Alpha Biomes |
| 0.3 | **blood bouquet** |  | `AB_BloodBouquet` · Alpha Biomes |
| 0.3 | **rustpuff** |  | `RUT_RustPuff` · RimUtinni: Rot Spore Kit |
| 0.15 | **mutated ocular tree** | 🌳 | `AB_AlienTree_Polluted` · Alpha Biomes |

### `RUT_Webwork` — 161 tiles · 36 … 63 °C (median 49) · plantDensity 0.9

*was 7 inherited plants → now **7** assigned*

| commonality | plant | | mod |
|---:|---|---|---|
| 1.1 | **deep jungle tree** | 🌳 | `AB_JungleTree` · Alpha Biomes |
| 1 | **chokevine** |  | `RG_Plant_TropicalChokevine` · ReGrowth 2 |
| 0.4 | **tangle tea** |  | `AB_TangleTea` · Alpha Biomes |
| 0.3 | **wild tooke-trap plant** |  | `Plant_TookeTrap_Wild` · Star Wars Animal Collection (Continued) |
| 0.15 | **gomphoeria** |  | `AB_Gomphoeria` · Alpha Biomes |
| 0.07 | **red bugloss** |  | `AB_RedBugloss` · Alpha Biomes |
| 0.05 | **aaklac** |  | `AB_Aaklac` · Alpha Biomes |

### `RUT_FeverWood` — 43 tiles · 38 … 52 °C (median 46) · plantDensity 0.7

*was 7 inherited plants → now **7** assigned*

| commonality | plant | | mod |
|---:|---|---|---|
| 1.5 | **wild hydenock tree** | 🌳 | `Plant_HydenockTree_Wild` · Star Wars Animal Collection (Continued) |
| 1.2 | **keening cordax** | 🌳 | `AB_KeeningCordax` · Alpha Biomes |
| 0.8 | **giant leaf** |  | `RUT_GiantLeaf` · RimUtinni Patches (Jawa campaign) |
| 0.6 | **wild jogan tree** | 🌳 | `Plant_JoganTree_Wild` · Star Wars Animal Collection (Continued) |
| 0.5 | **iashiphus** |  | `AB_Iashiphus` · Alpha Biomes |
| 0.4 | **gomphoeria** |  | `AB_Gomphoeria` · Alpha Biomes |
| 0.4 | **wild chak-root plant** |  | `Plant_Chakroot_Wild` · Star Wars Animal Collection (Continued) |

## B. the mycoid and fire massif

### `RUT_ExtremeDesert` — 3,969 tiles · 16 … 66 °C (median 46) · plantDensity 0.008  🔴 **`plantDensity` is near zero — this roster will almost never be seen**

*was 2 inherited plants → now **3** assigned*

| commonality | plant | | mod |
|---:|---|---|---|
| 0.1 | **light-pipe nub** |  | `RSW_LightPipeNub` · RimMandrake: SW — Bestiary |
| 0.05 | **bloddle plant** |  | `RSW_Plant_Bloddle` · RimMandrake: SW — Bestiary |
| 0.01 | **ollim** | 🌳 | `RSW_Ollim` · RimMandrake: SW — Bestiary |

### `RM_TheRot` — 2,204 tiles · -42 … 24 °C (median -19) · plantDensity 0.6

*was 34 inherited plants → now **30** assigned*

| commonality | plant | | mod |
|---:|---|---|---|
| 10 | **hessuk moss** |  | `AB_Bryolux` · Alpha Biomes |
| 3 | **nubbik stool** |  | `AB_Glowstool` · Alpha Biomes |
| 2 | **tolluk cap** |  | `AB_Agarilux` · Alpha Biomes |
| 2 | **vokkun pillar** |  | `AB_GiantAgarilux` · Alpha Biomes |
| 1 | **ithra glowcap** |  | `AB_GlowingAgarilux` · Alpha Biomes |
| 0.5 | **quessa spire** |  | `AB_LilacBeacon` · Alpha Biomes |
| 0.5 | **turrok shelf** |  | `AB_WitchesOyster` · Alpha Biomes |
| 0.5 | **sikkra lure** |  | `RUT_Dewshrooms` · RimUtinni: Rot Spore Kit |
| 0.5 | **pimmik mold** |  | `RUT_FruitingBodies` · RimUtinni: Rot Spore Kit |
| 0.5 | **nissik gill** |  | `RUT_Nuitae` · RimUtinni: Rot Spore Kit |
| 0.5 | **rukka cap** |  | `RUT_Wrinklecap` · RimUtinni: Rot Spore Kit |
| 0.4 | **churrun mast** | 🌳 | `RUT_Arpeau` · RimUtinni: Rot Spore Kit |
| 0.3 | **orrusk crook** |  | `AB_RecurvedStropharia` · Alpha Biomes |
| 0.3 | **tarrusk spire** | 🌳 | `RUT_FlakespireFungus` · RimUtinni: Rot Spore Kit |
| 0.3 | **gubbra gourd** |  | `RUT_Pusmelon` · RimUtinni: Rot Spore Kit |
| 0.3 | **tavvik crust** |  | `RUT_Sagecrust` · RimUtinni: Rot Spore Kit |
| 0.2 | **bollusk trunk** |  | `AB_ArbuscularMycorrhiza` · Alpha Biomes |
| 0.2 | **glissik slimecap** |  | `AB_SlimyPholiota` · Alpha Biomes |
| 0.2 | **rhukk tooth** |  | `RUT_BleedingTooth` · RimUtinni: Rot Spore Kit |
| 0.2 | **tinnik bell** |  | `RUT_Brightbell` · RimUtinni: Rot Spore Kit |
| 0.2 | **rhessa cap** |  | `RUT_CrimsonCap` · RimUtinni: Rot Spore Kit |
| 0.2 | **sylla lace** |  | `RUT_GreyLady` · RimUtinni: Rot Spore Kit |
| 0.2 | **dremmik cap** | 🌳 | `RUT_Shinecap` · RimUtinni: Rot Spore Kit |
| 0.2 | **pursk hood** |  | `RUT_VioletWimple` · RimUtinni: Rot Spore Kit |
| 0.15 | **vennik salve** |  | `RUT_MortalMorelPlant` · RimUtinni: Rot Spore Kit |
| 0.1 | **skarrow dome** |  | `AB_AgaricusDomeCap` · Alpha Biomes |
| 0.1 | **ruvvak weeper** |  | `AB_DribblingCap` · Alpha Biomes |
| 0.1 | **vekkra choker** | 🌳 | `RUT_Skulltop` · RimUtinni: Rot Spore Kit |
| 0.05 | **kabbrik pod** |  | `RUT_BlastpodShroom` · RimUtinni: Rot Spore Kit |
| 0.01 | **grath elder** |  | `AB_AgariluxPrime` · Alpha Biomes |

### `RUT_ForsakenCrags` — 1,135 tiles · -24 … 31 °C (median -11) · plantDensity 0.5

*was 8 inherited plants → now **8** assigned*

| commonality | plant | | mod |
|---:|---|---|---|
| 1 | **grass** |  | `AB_GlowingGrass` · Alpha Biomes |
| 0.6 | **toxic gamma** | 🌳 | `AB_ToxicGamma` · Alpha Biomes |
| 0.5 | **giant gamma** |  | `AB_GiantGamma` · Alpha Biomes |
| 0.5 | **wild ragadast** |  | `AB_WildRadagast` · Alpha Biomes |
| 0.5 | **gamma** |  | `AG_Gamma` · Alpha Genes |
| 0.3 | **giant stikehr** |  | `AB_GiantStikehr` · Alpha Biomes |
| 0.25 | **septimum** |  | `AG_Septimum` · Alpha Genes |
| 0.2 | **giant septimum** | 🌳 | `AB_GiantSeptimum` · Alpha Biomes |

### `RUT_WeepingStones` — 223 tiles · 18 … 64 °C (median 35) · plantDensity 0.4

*was 4 inherited plants → now **4** assigned*

| commonality | plant | | mod |
|---:|---|---|---|
| 1 | **sarnreed** |  | `Plant_Reeds` · Odyssey |
| 0.4 | **green rock fern** |  | `AB_GreenRockFern` · Alpha Biomes |
| 0.4 | **sikkra lure** |  | `RUT_Dewshrooms` · RimUtinni: Rot Spore Kit |
| 0.12 | **ambrosia bush** |  | `Plant_Ambrosia` · Core |

### `RUT_Slime` — 96 tiles · -3 … 22 °C (median 13) · plantDensity 0.2

*was 5 inherited plants → now **5** assigned*

| commonality | plant | | mod |
|---:|---|---|---|
| 1 | **tall slimy grass** |  | `AB_TallSlimyGrass` · Alpha Biomes |
| 0.5 | **slimy fern** |  | `AB_SlimyFern` · Alpha Biomes |
| 0.5 | **slimy tree** |  | `AB_SlimyTree` · Alpha Biomes |
| 0.4 | **slimecasia** |  | `AB_Slimecasia` · Alpha Biomes |
| 0.3 | **large slimy tree** |  | `AB_LargeSlimyTree` · Alpha Biomes |

### `RUT_TheForge` — 44 tiles · 42 … 56 °C (median 49) · plantDensity 0.4

*was 10 inherited plants → now **10** assigned*

| commonality | plant | | mod |
|---:|---|---|---|
| 0.9 | **fireweed** |  | `Plant_Fireweed` · Odyssey |
| 0.7 | **magma cactus** |  | `Plant_MagmaCactus` · Odyssey |
| 0.6 | **fire lavender** |  | `RUT_FireLavender` · RimUtinni Patches (Jawa campaign) |
| 0.4 | **tavvik crust** |  | `RUT_Sagecrust` · RimUtinni: Rot Spore Kit |
| 0.35 | **primordial grass** |  | `IronScruff_PrimordialGrass` · Primordial Geysers |
| 0.3 | **tinkle grass** |  | `AB_TinkleGrass` · Alpha Biomes |
| 0.3 | **primordial tall grass** |  | `IronScruff_PrimordialTallGrass` · Primordial Geysers |
| 0.25 | **bindweed** |  | `IronScruff_Bindweed` · Primordial Geysers |
| 0.2 | **firevine tree** | 🌳 | `AB_FirevineTree` · Alpha Biomes |
| 0.2 | **heatsink fungus** | 🌳 | `RUT_HeatsinkFungus` · RimUtinni Patches (Jawa campaign) |

## C. contamination

### `RUT_Wasteland` — 1,853 tiles · -23 … 54 °C (median 4) · plantDensity 0.12

*was 9 inherited plants → now **9** assigned*

| commonality | plant | | mod |
|---:|---|---|---|
| 1.2 | **toxigrass** |  | `RG_Plant_ToxiGrass` · ReGrowth 2 |
| 0.8 | **tall toxigrass** |  | `RG_Plant_TallToxiGrass` · ReGrowth 2 |
| 0.35 | **ashskal** |  | `Plant_GrayGrass` · Biotech |
| 0.3 | **scorched stars** |  | `RUT_ScorchedStars` · RimUtinni Patches (Jawa campaign) |
| 0.2 | **weeping toxberry** |  | `AB_WeepingToxberry` · Alpha Biomes |
| 0.2 | **toxipotato plant** |  | `Plant_Toxipotato` · Biotech |
| 0.1 | **toxibulb** | 🌳 | `AB_ToxiBulb` · Alpha Biomes |
| 0.1 | **polux tree** | 🌳 | `Plant_TreePolux` · Biotech |
| 0.08 | **polux bush** | 🌳 | `VRE_PoluxBush` · Vanilla Races Expanded - Phytokin |

### `RUT_Miasma` — 93 tiles · 26 … 59 °C (median 43) · plantDensity 0.7

*was 4 inherited plants → now **4** assigned*

| commonality | plant | | mod |
|---:|---|---|---|
| 25 | **mangrove tree** | 🌳 | `AB_MangroveTree` · Alpha Biomes |
| 8 | **parasitic mangrove** |  | `AB_ParasiticMangrove` · Alpha Biomes |
| 6 | **mangrove palm** | 🌳 | `AB_MangrovePalm` · Alpha Biomes |
| 0.4 | **brommok timber** | 🌳 | `RUT_Nogtyl` · RimUtinni: Rot Spore Kit |

### `RUT_Scarlands` — 90 tiles · 58 … 66 °C (median 60) · plantDensity 0.15

*was 1 inherited plants → now **1** assigned*

| commonality | plant | | mod |
|---:|---|---|---|
| 0.25 | **scorched stars** |  | `RUT_ScorchedStars` · RimUtinni Patches (Jawa campaign) |

## D. the shrub belt

### `RUT_AridShrubland` — 628 tiles · -15 … 59 °C (median 21) · plantDensity 0.35

*was 10 inherited plants → now **10** assigned*

| commonality | plant | | mod |
|---:|---|---|---|
| 0.9 | **RUT_Fuzz** | | `RUT_Fuzz` · newer than the def dump |
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

### `RUT_Sump` — 41 tiles · -6 … 20 °C (median 1) · plantDensity 0.15

*was 1 inherited plants → now **1** assigned*

| commonality | plant | | mod |
|---:|---|---|---|
| 0.6 | **tar puddle** |  | `AB_TarPuddle` · Alpha Biomes |
