# Materials census: ores, gems, exotics — for the Scald sea floor decision

Owner wants to "put our arms around" every ore/gem/exotic material available across
active mods + our own Star Wars content, to pick which ones form near hydrothermal
chimneys on the Scald's sea floor.

Method: python + xml.etree.ElementTree over each source's Defs, resolving
`ParentName` inheritance (shallow, best-effort — flags UNRESOLVED where a parent
isn't found in the same pass). Sanity probe: count vanilla Gold/Silver ThingDefs
found via the same parser, to prove the parser actually reads content before
trusting any "found N materials" count elsewhere in this doc.

Status: DONE. Not committed (read-only census per task instructions).

## Sanity probe

Parser (`ElementTree` + shallow `ParentName` walk) run against vanilla Core's
`Items_Resource_Stuff.xml` (800 ThingDefs indexed total). Correctly recovered,
including inherited `MarketValue` and `stuffProps/categories`, and which rock
mines each:

| defName | label | MarketValue | stuff category | mined by rock |
|---|---|---|---|---|
| Gold | gold | 10.0 | Metallic | MineableGold |
| Silver | silver | 1.0 | Metallic | MineableSilver |
| Steel | steel | 1.9 | Metallic | MineableSteel |
| Plasteel | plasteel | 9.0 | Metallic | MineablePlasteel |
| Uranium | uranium | 6.0 | Metallic | MineableUranium |
| Jade | jade | 5.0 | Stony | MineableJade |

All six match known vanilla values. Parser trusted for the rest of this census.

## kikohi.jewelry
`3203280763` (Steam Workshop id). 22 ThingDefs, all under `Items_Resource_Manufactured.xml` off an abstract `GemstoneBase` (MV 6, stuff categories `Gemstones`+`Stony`).

| defName | label | kind | MV | stuff? | obtained |
|---|---|---|---|---|---|
| Diamond | diamond | gem/stuff | 7.5 | Gemstones, Stony | mineable rock `MineableDiamond` |
| Ruby | ruby | gem/stuff | 6.0 | Gemstones, Stony | mineable rock `MineableRuby` |
| Sapphire | sapphire | gem/stuff | 6.0 | Gemstones, Stony | mineable rock `MineableSapphire` |

All three are `stuff` — usable as a building/apparel material (gem furniture, jewelry), not just sold raw. Generic (no IP).

## kikohi.coloreddeepresources
`3203269467`. **Patches-only, adds no new resource.** Cosmetic: adds a `deepColor`/`transparencyMultiplier` `VEF.Things.ThingDefExtension` to *existing* deep-drillable resources (own + other mods', e.g. found a patch coloring VCE's `VCE_Salt`) so the deep-resource sonar readout shows a distinct colour blip per resource. No material census entry.

## zacharyfoster.mineralsframework
`3562390384`. **Zero standalone ThingDefs with a `defName`** — confirmed (framework files hold only `Abstract="True"` `Name=`-keyed base defs: `MF_StaticMineralBase`, `MF_DynamicMineralBase`, `BigMineralBase`, `BigMineralTrophyBase`, plus a stone-blocks base). It's shared plumbing (a `GenStepDef` for placing rock formations, research projects, base stat/graphic templates) that Rock/Frozen/Sparkle build on — not a resource source itself.

## zacharyfoster.mineralsrock
`3562391080`. 67 ThingDefs — alternate rock-formation buildings (Weathered/Hewn/Solid/Passable/Smoothed variants per stone) that **re-skin existing vanilla ore deposits** (Gold/Silver/Jade/Plasteel/Steel/Uranium — same defNames, i.e. these are visual variety on vanilla resources, not new materials) plus:
- **"Tech" ore** (`WeatheredOreTech`/`SolidOreTech`/`HewnOreTech`, "ancient compacted machinery") — random-drops `AluminiumBar`, `Plasteel`, `Mechanism`, `ElectronicComponents`, `ComponentIndustrial`, `ComponentSpacer`, `AdvMechanism`, `Electronics`, `Microchips`. Not itself a new raw material — a ruins-flavoured salvage node. `AluminiumBar`/`AdvMechanism`/`Electronics`/`Microchips` are **not defined by any of our 7 target mods** (grep-confirmed absent) — likely references to an unlisted dependency and inert no-ops in our mod set, same mechanism CLAUDE.md notes for patches matching nothing.
- Basalt/Granite/Limestone/Marble/Sandstone/Slate rock families, each dropping `RoughGem`/`CrushedStone`/`SandResource`/`SmallFossil`/`Amber`/`Jade` plus `MAU_*`-prefixed chunk types (SharpStoneShard, ChunkDunite, ChunkFlint, ChunkPegmatite, ChunkAlabaster). **None of `CrushedStone`, `SandResource`, `Amber`, `Pearl`, `BlocksSlate`, `MAU_*` are defined anywhere in our 7 target mods** (grep-confirmed) — these are references to some other/unlisted mineral-resource mod and are dead no-ops in the current mod set. Only `RoughGem`, `Jade`, `SmallFossil`, `Gold`, `Silver`, `Plasteel`, `Steel`, `Uranium` (all defined in-scope) actually drop.
- `BeachRock`/`RiverRock` (thingClass `MineralsRock.RiverRock`) are placeable loose decorative rocks near water, same drop-list mechanism.

## zacharyfoster.mineralsfrozen
`3562390973`. 9 ThingDefs, all cold-biome flavour, not ore/gem:
- `MF_IceBlocks` (MV 0.2, stuff cat `FrozenBuildingMaterial`), `MF_SnowBlocks` (MV 0.1, same stuff cat, minable from `ZF_SnowDrift`), `MF_ChunkIce`. Irrelevant to a hot hydrothermal floor.

## zacharyfoster.mineralssparkle
`3562390730`. 34 ThingDefs — **the crystal-cluster mod, most relevant of the seven for a vent floor.** Static mineral-crystal formations spawn as their own terrain-driven clusters (`perMapProbability`/`minClusterProbability`/`allowedTerrains` — no rock-wall required), each with `randomlyDropResources` yielding gem resources when mined:

| defName | label | drops | notes |
|---|---|---|---|
| DiamondCrystal | Diamonds embedded in rock | RoughGem, RoughUltrahardGem | |
| RubyCrystal | Rubies embedded in rock | RoughGem, RoughUltrahardGem | |
| SapphireCrystal | Sapphires embedded in rock | RoughGem, RoughUltrahardGem | |
| EmeraldCrystal | Emeralds embedded in rock | RoughGem | |
| AmethystCrystal, QuartzCrystal, CalciteCrystal, SchorlCrystal, RubelliteCrystal, IndicoliteCrystal | — | RoughGem (+CrushedStone, unlisted-mod, inert) | |
| MagnetiteCrystal | Magnetite Crystals | RoughGem, **Steel** | iron-bearing crystal — thematically close to a black-smoker sulfide chimney |
| UraniniteDeposit | Uranium Deposit | RoughGem, **Uranium** | "often associated with silver" per its own description |
| QuartzBase (BigQuartzCrystal) | Giant Quartz Crystal | GlassBatch | decorative giant crystal, MV 1000 as a trophy |
| BigAmethystCrystalTrophy | Giant Amethyst Crystal | (trophy, MV 2000) | decorative, not mined for resource |
| **RoughGem** | Rough Gem | — | MV 50, stuff cat `MS_Gemstones`, also minable via `BigQuartzBase` |
| **RoughUltrahardGem** | Rough Ultrahard Gem | — | MV 200 |
| **CutGem** / **CutUltrahardGem** | Cut Gem / Cut Ultrahard Gem | — | MV 200 / 500, crafted from Rough at a jeweller's bench (not raw-mined) |
| SmallFossil / MediumFossil / LargeFossil | fossils | SmallFossil MV 100 | paleontology flavour, not a mineral |

## xmb.ancientminingindustry.mo
`3141472661`. 48 ThingDefs — **adds zero new raw materials.** It's an ancient-ruins industrial-decay decoration/prop mod: drilling rigs, mining carriages (steel/plasteel/uranium-labelled but just flavour props), ore dressers, tunnel structural supports, mini shotgun turrets, a pickaxe/shovel. No ore, gem, or stuff ThingDef anywhere in it.

## src/RimStarWars/Armoury — KotOR absorption (Tibanna, Rhydonium, Beskar, Cortosis, Durasteel, crystals)

⚠️ **Deployment status matters for this whole section.** Every `Absorbed_*` file carries a
generator header: *"Source pack stays active in the live ModsConfig for now (rule 5); do NOT
deploy this file until it retires, or duplicate defNames result."* i.e. these are **ported,
not-yet-deployed copies** with defNames preserved verbatim from the still-active donor mods
(`guy762.MM.KotORCore`, KotOR Weapons, The Force Lightsabers). **Today, in the live game, these
materials exist via the donor mods, not via Armoury.** When Armoury cuts over, the same
defNames carry forward unchanged.

**Metals/alloys/resources** (`Absorbed_KotorCore_KotORResource_Metals2.xml`,
`_Rhydonium.xml`, `_Spice.xml`, `_TibannaPlasma.xml`, `_Kolto.xml`, `_MiscCraftingItems.xml`,
`_Stygium.xml`):

| defName | label | MV | stuff? | obtained |
|---|---|---|---|---|
| KOTOR_IngotBeskar | Beskar | 150.0 | — | crafted from `KOTOR_RawBeskar` (below) |
| KOTOR_RawBeskar | Mandalorian Iron | 100.0 | — | mineable rock `KOTOR_MineableBeskar` |
| KOTOR_IngotCortosis | Cortosis | 35.0 | — | mineable rock `KOTOR_MineableCortosis` |
| KOTOR_AlloyDurasteel | Durasteel | 5.0 | — | crafted (no direct mineable rock found) |
| KotORChunk_durasteel | Durasteel slag chunk | 65.0 | — | mineable rock `KOTOR_MineableDurasteel` |
| KOTOR_AlloyBronzium | Bronzium | 3.0 | — | mineable rock `KOTOR_MineableBronzium` |
| KOTOR_Metal / KOTOR_RawMetal | (generic) | — | Metallic | abstract bases |
| KOTOR_RawRhydonium | Rhydonium powder | 60.0 | — | mineable rock `KOTOR_MineableRhydonium`; **volatile fuel**, canon KotOR explosive/starship-fuel ore |
| KOTOR_Tibanna | Tibanna gas | 50.0 | — | canon blaster-gas resource, no mineable rock in this file (likely gas-vent/pod harvest elsewhere) |
| KOTOR_Spice | spice | 75.0 | — | mineable rock `KOTOR_MineableSpice`; canon KotOR drug/trade good |
| KOTOR_kolto | Kolto | 100.0 | — | Medicine-category resource, canon Bacta-equivalent healing fluid |
| KOTOR_Duracrete | Duracrete | 2.0 | Stony | stone-block-tier building material |
| KOTOR_FabricArmorweave | Armorweave | 6.0 | Fabric | — |
| KOTOR_Plastoid | Plastoid | 4.0 | Woody(!) | canon armor-plate polymer, oddly stuffed as Woody upstream |
| guy762_crystalitem_beskar | "Pride of Mandalore" | 30000.0 | — | unique named crystal/relic item |
| guy762_crystalitem_krayt | Krayt Dragon Pearl | 2500.0 | — | canon organic gem (krayt dragon gullet) |
| guy762_crystalitem_stygium | Crystal, Stygium | 2980.0 | — | canon cloaking-tech crystal |
| KOTOR_StygiumCrystal | Stygium crystal formation | — | mineable | the rock formation that yields the Stygium crystal above |

**Lightsaber crystals** (`Absorbed_KotorWeapons_ThingDefs_UpgradeItems_Lightsaber.xml`, ~40
defs, all `guy762_crystalitem_*`) — canon KotOR color-crystal roster (Adegan, Ankarres
Sapphire, Kaiburr, Solari, Qixoni, Ruusan, etc.), MV 230–25,000. These are **loot/craft
upgrade items, not mineable ore** in this file — no `minedBy` found. Not sea-floor candidates
as-is (they're per-weapon upgrade parts), but the naming pool is real canon IP.

**Kyber / Force crystals** (`Absorbed_TheForceLightsaber_Kyber.xml`,
`_ForceCrystal_Formations.xml`): `Force_KyberCrystal` (MV 100, canon lightsaber-core crystal)
mined from `Force_CrystalFormation_Small/Medium/Large` (each a `Mineable` building, MV 3000).
Genuinely canon (kyber crystals are core Star Wars lore) and a strong "grows in rock, glows"
visual — but tonally tied to the Jedi/lightsaber storyline, so using it on a random sea floor
would read as "there's a lightsaber crystal down there" rather than a generic gem.

**Generic (non-canon) crystal-formation variants** (`Absorbed_KotorWeapons_KotORResource_
CrystalFormations_{Small,Medium,Large}.xml`): `KOTOR_SmallCrystal_{blue,green,orange,purple,
red,white,yellow}`, `KOTOR_MediumCrystal_{cool,soft,warm}`, `KOTOR_LargeCrystal_{cool,warm}` —
colour/temperature-themed crystal-formation buildings, no MV/label text captured (decorative
mineable rock skins feeding the lightsaber-crystal crafting chain). Not IP-bound by name.

## src/ own resources (other RM_/RSW_/RUT_ ore/material defs found, outside Armoury)

The strongest, most on-theme hits for a hydrothermal-floor material — already-shipped or
in-flight RM_/RUT_ resources with vent/heat/mineral-precipitate flavor text:

| defName | label | mod | MV | obtained | notes |
|---|---|---|---|---|---|
| RM_SeepSalt | seep-salt | WeepingStones | 3.2 | scraped by hand, no mineable rock found | description literally says "scraped from the rim of a steamfrond vent" — a direct **hydrothermal vent precipitate already in our vocabulary**, only spice/preservative flavored so far |
| DV_Pyrinth | pyrinth | Pyrinth (absorbed EpochsPyrinth) | 7.0 | ResourcesRaw, no minedBy captured | "warm, bright orange crystal… glows and emits warmth innately" — a self-heating crystal, thematically a vent mineral |
| RM_FE_Fulgurite | fulgurite | Pyrelands | 3.0 | ThingWithComps, lightning-glass | sand fused to glass by heat — heat-formed but lightning-, not vent-, sourced; low value by design ("worthless to sell") |
| RUT_Lanternstone | lanternstone | LanternDeeps | 1.0 | stuff=[] (i.e. declared but empty categories — check before using as a building stuff) | glowing blue native crystal, "cut out of the Lantern Deeps" — home biome is Lantern Deeps, not the Scald |
| RUT_DeadSmartsteel | dead smartsteel | RustCathedralWalls | 8.0 | pulled from ruin walls | salvage alloy, industrial-ruin flavor, not geological |
| RUT_LivePatternMetal | live pattern metal | RustCathedralWalls | 14.0 | dug from deep deck plate | animate/nanite flavor ("this metal is not dead") — tonally off for a natural vent floor unless reflavored |
| RM_BrinePlate | brine plate | Wasteland | 28.0 | harvested from the `RM_Drazz` creature (or "found loose on a pool floor") | biological mineral wafer, not a rock-formed ore — precedent for "mineral deposit that's actually organic" if wanted |

No `LuminousPigment` ThingDefs found yet under `src/` — the design doc committed this session
(`design/RimMandrake/deepfire_luminous_pigment_spec.md` per recent commit) has not been
implemented as XML yet, so it's a design-stage candidate, not a built material.

## Plasteel relabel search

**No relabel found anywhere in the repo.** Searched for a `DefInjected`/`LanguageData` label
override, an xpath patch targeting `ThingDef[defName="Plasteel"]/label`, and any def literally
named `Plasteel` outside vanilla Core — none exist. Plasteel still ships under its vanilla
label ("plasteel") everywhere in the current mod set. The "more Utinni" rename the owner wants
is **unstarted work**, not something already done and missed.

## Candidates for the Scald floor

~15 materials that fit a hydrothermal-vent floor (sulfide/metal precipitates, heat-grown
crystals, vent-scraped minerals), generic-tier first:

1. **RM_SeepSalt** (ours, WeepingStones) — already-written vent-rim mineral precipitate; the closest direct precedent, just needs a Scald-specific reskin/second source.
2. **MagnetiteCrystal** (mineralssparkle) — iron-bearing crystal that drops Steel + RoughGem; magnetite is a real black-smoker mineral.
3. **UraniniteDeposit** (mineralssparkle) — "often associated with silver," drops Uranium + RoughGem; radioactive-vent flavor.
4. **DiamondCrystal / RubyCrystal / SapphireCrystal / EmeraldCrystal** (mineralssparkle) — static crystal-cluster formations, terrain-spawned (not rock-wall-bound), the right mechanic for "grew right on the vent floor."
5. **QuartzCrystal / CalciteCrystal / SchorlCrystal** (mineralssparkle) — cheaper filler crystals for the same cluster mechanic; good for common-tier vent mineral.
6. **RoughGem / CutGem / RoughUltrahardGem / CutUltrahardGem** (mineralssparkle) — the actual sellable resource all the above feed; MV 50–500, generic (no IP).
7. **DV_Pyrinth** (ours, Pyrinth) — self-heating orange crystal; unusually apt for "grows warm near a heat source."
8. **Gold / Silver** (vanilla) — real black-smoker sulfide-deposit metals; a Scald-flavored `MineableGold`/`MineableSilver` variant is the lowest-effort authentic option.
9. **Jade** (vanilla, +mineralsrock's Solid/Weathered/Hewn skins) — serpentine-family stone, plausible hydrothermal alteration product.
10. **KOTOR_AlloyBronzium / KOTOR_IngotBeskar / KOTOR_RawBeskar** (Armoury, not yet deployed) — if the tier line allows an invented-flavored metal alloy here (Beskar is IP — see list below, use with care).
11. **KOTOR_RawRhydonium** (Armoury) — volatile fuel-ore; a "gas seep beside the vent" reads well but it's canon IP (see below).
12. **Diamond / Ruby / Sapphire** (kikohi.jewelry) — simple stuff-capable gems, `MineableX` rock variants; lower-effort generic option than the sparkle-mod crystal clusters.
13. **BeachRock/RiverRock-style loose-rock drops** (mineralsrock's `RiverRock`/`BeachRock` mechanic) — a "rounded stones washed by the vent current" scatter-decoration precedent, drops Gold/Silver/Jade/RoughGem/Amber-if-defined.
14. **CrushedStone-equivalent rubble** — needs a real def (the referenced `CrushedStone` in mineralsrock's drop lists is undefined in our mod set); could be authored fresh as vent tailings.
15. **RM_BrinePlate** (ours, Wasteland) — precedent for a "mineral wafer" that's technically biological, if the owner wants an organic/mineral hybrid deposit near the vents (e.g. chemosynthetic crust).

## Star Wars canon ores (separate — IP notes)

- **Beskar / Mandalorian Iron** (`KOTOR_IngotBeskar`, `KOTOR_RawBeskar`) — core Mandalorian canon metal. IP.
- **Cortosis** (`KOTOR_IngotCortosis`) — canon lightsaber-resistant ore. IP.
- **Durasteel** (`KOTOR_AlloyDurasteel`, `KotORChunk_durasteel`) — canon standard SW construction alloy; less distinctive as IP (used as a generic "durable metal" name across the franchise) but still sourced from canon.
- **Rhydonium** (`KOTOR_RawRhydonium`) — canon volatile fuel/explosive ore (KotOR games). IP.
- **Tibanna gas** (`KOTOR_Tibanna`) — canon blaster-gas resource, mined famously at Bespin. IP.
- **Kolto** (`KOTOR_kolto`) — canon healing fluid (KotOR's bacta-equivalent). IP.
- **Stygium** (`guy762_crystalitem_stygium`, `KOTOR_StygiumCrystal`) — canon cloaking-device crystal. IP.
- **Krayt Dragon Pearl** (`guy762_crystalitem_krayt`) — canon organic gem from krayt dragon anatomy (Tatooine). IP, and thematically tied to a desert creature, not a sea vent.
- **Kyber crystal** (`Force_KyberCrystal`) — core Star Wars lightsaber/Death-Star-superlaser lore. IP, and tonally Jedi-coded.
- **~40 named lightsaber color crystals** (`guy762_crystalitem_*`: Adegan, Ankarres Sapphire, Kaiburr, Ruusan, Qixoni, Solari, etc.) — canon KotOR crystal-lore names. IP; these are loot/upgrade items, not mined ore, so a poor mechanical fit for a mineable vent floor regardless of IP status.
- **Plastoid, Duracrete, Armorweave** — generic SW-universe material *names* but describe common materials (polymer armor plate, reinforced concrete, armored cloth) used across countless canon sources without being tied to one specific IP holder — borderline, treat as low-risk generic-flavored rather than hard IP.
