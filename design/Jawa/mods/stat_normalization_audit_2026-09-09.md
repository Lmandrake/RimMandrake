<!-- status: evidence + wave plan for a BENCH ruling — nothing retired by this pass -->
# Stat-normalization conflict census — 2026-09-09

`STAT_NORMALIZATION_AUDIT_1`. **Scoping only. `ModsConfig.xml` was not touched,
no mod was retired, no def was edited.** Wave plan at the bottom; every wave is
follow-on work for a separate item.

Owner, verbatim: *"Assess our mod stack to see if anything is messing with the
numbers we might be about to normalize… We likely won't need any of those things
anymore now that we're just owning our whole loadout."* Scope was then **widened
by owner ruling, same day**, from fauna/flora to any third-party stat-balance
mod, with cosmetic-only and content-adding mods split into their own buckets.

---

## 0. Instruments — read this before citing any number below

| what | source | reading |
|---|---|---|
| **active mod list** | `infrastructure/state/modlists/ModsConfig_before_droid_donor_fix_2026-09-09.xml` (mtime **2026-09-09 13:38**) | **587 `<activeMods>`** |
| ⛔ **NOT used** | the live `ModsConfig.xml` | held **6** activeMods at census time — a minimal list another window swapped in for crash-recovery quicktests. Censusing against it would have reported "no third-party mods at all." |
| **campaign save** | `C:\Users\Mandrake\AppData\LocalLow\Ludeon Studios\RimWorld by Ludeon Studios\Saves\CANONICAL_ASHKARR_2026-09-09.rws` (25,670,511 bytes, 2026-09-09 12:43) | `<modIds>` = **590** |
| **mod folders** | fresh walk of the workshop + local trees, `<packageId>` read after stripping `modDependencies`/`loadAfter` blocks (`build_packageid_index.py`'s own correction) | **1,333** installed mods indexed; **587 / 587** active ids resolved to a folder, 0 unresolved |

**Snapshot ↔ save agreement, MEASURED**: the save's 590 `modIds` minus the
snapshot's 587 is exactly `neronix17.outerrim.droiddepot`, `neronix17.asimov`,
`mandrake.rsw.msedroidfix` — tonight's in-flight droid-retirement revert, and
nothing else. Nothing is in the snapshot that is absent from the save. So the
snapshot is the campaign list modulo one known, in-progress change.

⚠️ **A final cross-check against the live `ModsConfig.xml` is OWED** once another
window finishes restoring the full list. Every count here is against the 13:38
snapshot and no later.

**How each mod was classified**: every one of the 587 active mods had its own
XML walked and every `<xpath>` in every `PatchOperation` harvested — 🔴 **names
were never trusted**. A mod is in a table below because of an xpath or a def it
actually ships.

🔴 **Two blind spots, stated rather than hidden.**
1. **A pure-C# mod has no XML to harvest.** 90 of the 587 active mods carry an
   assembly and neither a `Defs/` nor a `Patches/` folder. Those were classified
   from their `About.xml` + `Languages/*/Keyed/*.xml` and their written-out
   settings file in `Config/`, and are marked **(C#)** below — read those rows as
   characterisations, not measurements. This is the same gap
   `outgrown_audit_2026-08-30.md` flagged in its own honesty note.
2. **Terrain and biome are grid-borne in a save.** Per the `rimworld-savegame`
   skill, terrain/biome live in base64 raw-DEFLATE grids of 2-byte shortHashes,
   not as text. The save cross-reference in §3 counts `<def>NAME</def>` THING
   instances and reference tokens; for any mod whose surface is `TerrainDef` or
   `BiomeDef` the save reading is **UNMEASURED**, not zero, and is written that
   way.

---

## 1. What "our numbers" actually are

The normalization pass this item protects has a concrete surface — the generated
and hand-authored patches in `src/RimUtinni/UtinniPatches/Patches/`:

| our file | operations | what it owns |
|---|---|---|
| `BiomeCastEvictions_WildBiomes.xml` | **2,998** | animal-side `race.wildBiomes` removals |
| `AnimalTolerances_Ashkarr.xml` | 410 | per-creature temperature bands |
| `AnimalBiomeDuplicates_Generated.xml` + `_Fix.xml` | 193 + 27 | duplicate-registration repairs |
| `BiomeCast_Ashkarr.xml` | 99 | `BiomeDef/wildAnimals` — the cast |
| `BiomeFlora_Ashkarr.xml` | 23 | `BiomeDef/wildPlants` |
| `BiomeFloraStatAdjustments_Generated.xml` | 11 | plant `Flammability` |
| `BiomeFaunaStatAdjustments_Generated.xml` | 5 | `MoveSpeed`, `race/predator` |
| `CreatureResize_Ashkarr.xml` | 1 | creature draw scale |

**23 BiomeDefs are painted as Ash'karr** and are the contested ground:
`AridShrubland` · `Desert` · `ExtremeDesert` · `LavaField` · `Scarlands` ·
`Volcano` · `Wasteland` · `PoisonForest` · `BiomeCypreJungle` ·
`COMIGO_GreaterSwamp_Tropical` · `ZBiome_Badlands` · `ZBiome_DesertOasis` ·
`ZBiome_Grasslands` · and ten `AB_*` Alpha Biomes.

🔑 **The 2,998-operation eviction file is the shape of the problem.** It exists
only because third-party mods write spawn weights into our biomes from the
*animal* side (`race.wildBiomes`), which the load-time padder materialises back
into `wildAnimals`, so replacing the cast alone under-enforces. That file is not
content — it is a **counter-patch**, and every operation in it is a third-party
injection we are paying to undo. Retiring an injector is the only thing that
makes its share of those 2,998 operations unnecessary; suppressing it is the
alternative we are already living with. Filed under
`BIOME_FAUNA_ASSIGNMENT_SITTING_1`, 2026-09-09 — this audit did not discover it,
it measures its cost.

---

## 2. The census

**131 of 587 active mods carry a PatchOperation whose xpath lands on a
balance-number surface.** Seven of those are our own (`mandrake.*`), leaving
**124 third-party**. Of those, **31 are real conflicts** (they land on a def or
biome we also patch, or turn a global knob); the rest either patch only their own
content or touch a surface no normalization pass will visit.

### 2A. 🔴 Pure knob-turners — nothing of their own would be lost

*Retiring one of these removes a number-edit and no content whatsoever.*

| mod | what it actually does (MEASURED unless marked) | conflicts with |
|---|---|---|
| `fluxilis.germanquality` — Quality Affects HP | adds a `StatPart_Quality` to `MaxHitPoints`: **0.5× awful → 10× legendary**, globally, on every quality-bearing thing in the game. 1,114-byte patch, two operations, zero content | 🔴 **the widest silent multiplier found.** Any HP number we set is re-scaled up to 10× |
| `zylle.moredangerousgame` — More Dangerous Game **(C#)** | Harmony overhaul of predator/prey and animal revenge. Settings ladder Vanilla → Dangerous → More → Most → Extreme; separate axes for "allowable prey" and "what counts as a predator" (up to *every animal is a predator*). **No `Mod_2364245786_*.xml` exists in `Config/`** → never configured, running at packaged defaults | 🔴 **this is the "dangerous animals" mod the owner remembered.** Sits directly on top of `race/predator`, which `BiomeFaunaStatAdjustments_Generated.xml` sets per-creature |
| `farhanfair.warcaskettweakspatch` | 279 apparel operations: 93× `Insulation_Cold`, 93× `Insulation_Heat`, 44× `equippedStatOffsets/VacuumResistance` replaced across `VFEPirates.WarcasketDef`. **Zero defs of its own** | warcasket armour numbers |
| `aelanna.fistnerf` — Fists Aren't Made of Steel | replaces `Blunt` with `BluntUnarmed` in the melee tool capacities of `Human` and every `HumanRace`-parented alien race. 2 defs, no content | unarmed melee damage on every pawn incl. Jawa |
| `coldcrow.betterkibble` | replaces vanilla `Kibble`'s `MarketValue` (→0.10) and `Nutrition`, plus recipe re-routing | food economy numbers |
| `mosi.rebalancedancientjunk` | 44 `fillPercent` + 25 `killedLeavings` replaces on ancient junk. Zero own defs | ruin salvage yields |
| `farxmai2.vanilladeconstructablevehicles` | **594 `costList` + 501 `statBases` + 108 `WorkToBuild`** replaces across vehicle defs. Zero own defs | vehicle build cost / work economy |
| `summersausages2ttv.techlevelenforcement` | 24 conditional ThingDef operations + a large assembly; gates equipment by faction tech level | weapon/apparel availability, not values |
| `doomdrvk.unlimitednuzzles` | replaces `stackLimit` + `stackedEffectMultiplier` on the nuzzle thought | mood numbers |
| `victor.buymore` — Settlements buy more | 76 `TraderKindDef/stockGenerators` adds + 12 `tradeTags` | trade economy |
| `mlie.harvestwhenbutchering` **(C#)** | changes what butchering yields | animal product yields |
| `archie.turrettargetpatch` **(C#)** | turrets fire on hunting predators | behavioural, not numeric |
| `mlie.choosebiomecommonality` **(C#)** | worldgen biome commonality slider; **its settings file `Mod_2582875043_ChooseBiomeCommonality_Mod.xml` DOES exist and holds a full custom commonality table** | ⚠️ **moot by ruling** — the planet is frozen and never regenerates (CLAUDE.md). It cannot affect the shipped world. Retire on "does nothing", not on "conflicts" |

### 2B. 🔴 Conflicts that ALSO add content — *"retiring this loses X unless ported first"*

*These are the same class as the donor-retirement items: a cut here is a port.*

| mod | numeric conflict, MEASURED | content lost if cut |
|---|---|---|
| `regrowth.botr.core` — ReGrowth 2 | **3× `plantDensity` + 3× `wildPlants` + 2× `baseWeatherCommonalities` each on `AridShrubland`/`Desert`/`ExtremeDesert`**, plus `Scarlands`/`LavaField`; 45 `ThingDef/plant` blocks; **25 `plant/visualSizeRange`** (plant SIZE); 30 `plant/sowResearchPrerequisites`; 60 `graphicData/texPath` overrides | 196 own defs, and **563 placed instances in the live save** (`RG_Plant_AridGrass` ×268, `Plant_Brambles` ×112, `RG_Plant_Brambles{Yellow,Red}`, `RG_Plant_Oxalis`, `RG_Plant_CreepStern`, `RG_Plant_Plumeria`, `RG_Plant_CrimsonCushion`, `RG_Plant_TigerLily`, boulders). **This mod's plants ARE the ground cover of the campaign map.** |
| `sarg.alphabiomes` — Alpha Biomes | 66 `BiomeDef/wildAnimals` adds and **482 `race/wildBiomes` injections into ten `AB_*` biomes we paint**; 82 TerrainDef operations incl. affordances | 688 own defs — and **23,830 placed instances in the save**, of which `AB_Obsidianstone` alone is **23,819**. 🔴 **Alpha Biomes' rock is literally the substrate of the campaign map.** Ten of our 23 painted biomes are its BiomeDefs. Retirement is not on the table without re-authoring the planet |
| `zylle.morevanillabiomes` — More Vanilla Biomes | **904 `race/wildBiomes` patch adds**, of which **1,300 entries land on `ZBiome_Badlands`/`ZBiome_Grasslands`/`ZBiome_DesertOasis`** — three biomes we paint; plus 48 `wildPlants` and 9 `pollutionWildAnimals` adds on those same three | 23 own defs; 3 of our 23 painted biomes are ITS BiomeDefs; 10 placed plant instances |
| `sarg.alphaanimals` — Alpha Animals | **323 `race/wildBiomes` patch adds** (598 entries into biomes we paint) plus 306 entries its own defs declare for `AridShrubland`/`Desert`/`ExtremeDesert` | 914 own defs; save holds `AA_Behemoth` ×5 placed and **307 reference-only kinds** |
| `mlie.starwarsanimalcollection` | 41 biome-spawn operations touching 13 (biome, field) pairs we own; 433 own-def `wildBiomes` entries for our three desert biomes | ⛔ **already owned by `MLIE_FAUNA_ABSORPTION_1`** (135 of 160 creatures must port). Do not re-plan it here |
| `biomesteam.biomespollutedlands` | `wildPlants` and `pollutionWildAnimals` on `AridShrubland`/`Desert`/`ExtremeDesert`; `wildAnimals` on `LavaField`/`Scarlands`; 4 `StatDef/parts` | 202 own defs, 131 reference-only kinds in the save |
| `biomesteam.biomescore` | **45 `TerrainDef/fertility` operations** — fertility is a direct multiplier on plant growth — plus `stuffProps` on chitin leathers | 258 own defs. ⚠️ terrain surface **UNMEASURED** in the save (grid-borne) |
| `biomesteam.biomescaverns` | 21 `BiomeDef/wildAnimals` + 19 `BiomeVariantDef` layer wildAnimals + 18 `ThingDef/plant` | 674 own defs, 376 reference-only kinds |
| `joe.cephaloids` | **1 `wildAnimals` add on each of `AridShrubland`, `Desert`, `ExtremeDesert`, `Scarlands`, `LavaField`** — 5 of our 23 painted biomes, and that is its ENTIRE patch surface (17 ops, 1 file) | 10 own defs, **0 placed instances**, 5 reference-only kinds |
| `vanillaexpanded.vplantsesucculents` | **24 `wildPlants` adds: 12 on `ExtremeDesert`, 6 on `Desert`, 6 on `AridShrubland`** — its entire patch surface (39 ops) | 12 own defs, **0 placed instances**, 11 reference-only kinds |
| `vanillaexpanded.vaewaste` | 12 `pollutionWildAnimals` adds on `AridShrubland`/`Desert`/`ExtremeDesert`/`AB_OcularForest` | 55 own defs, 0 placed |
| `spino.megafauna` | 231 own-def `wildBiomes` entries for our three desert biomes (161 `AridShrubland`) | 92 own defs, 0 placed, 63 reference-only |
| `mlie.beastsoftherim` | 84 own-def `wildBiomes` entries for our desert biomes | 45 own defs, 0 placed |
| `veterano.mythicages.megafaunabestiary` | 21 own-def `wildBiomes` entries for our desert biomes | 343 own defs, 0 placed, 138 reference-only |
| `van.beasts` — Dark Ages: Beasts | 18 own-def `wildBiomes` entries for our desert biomes; 3 `pollutionWildAnimals` adds | 218 own defs; **32 placed** (`DA_MineableSteelBeetle` ×31) |
| `erin.ffanimals` | 9 own-def `wildBiomes` entries; 105 `RecipeDef/recipeUsers` adds | 16 own defs, 0 placed |
| `tyrannidae.littlecritters` | 6 own-def `wildBiomes` entries; 1 `statBases` + 1 `tools` replace on its own critters | 5 own defs, 0 placed |
| `oskarpotocki.vfe.tribals` | **42 `ThingDef/plant` operations on vanilla crops** (`Plant_Corn`, `Plant_Cotton`, `Plant_Healroot`, `Plant_Haygrass`, `Plant_Fibercorn`…) + 12 `sowResearchPrerequisites` | 135 own defs, **312 placed** (the tech-advancement ritual set is baked into the campaign ideo) |
| `iforgotmysocks.caravanadventures` | 40× `ArmorRating_Sharp` + 40× `ArmorRating_Blunt` replaces, 43 `tools`, 8 `race/baseBodySize`, 11 `PawnKindDef` `drawSize`, 8 `combatPower`, `MeleeDodgeChance`/`MeleeHitChance` offsets | 177 own defs; 3 placed (`CAOutsiderRelation`, `CASacrilegHunters`) — a whole quest layer |
| `redmattis.*` (Big and Small: `betterprerequisites`, `bigsmall.core`, `bigsmall`, `bigweapons`, `optional`) | the deliberate size-scaling family — `GeneDef/statOffsets`, `PawnCapacityDef`, `ingestible/maxNumToIngestAtOnce`, gene exclusion tags | 724 + 332 + 105 + 15 own defs; **44 placed gene instances** (`BS_SmallFrame`, `BS_LargeFrame`, `JotunFrame`, `HalfJotunFrame`…). ⚠️ `mod_config_rulings.md` §3 already records this as a *"deliberate scaling experiment"* — **an existing ruling this audit does not override** |
| `petetimessix.researchreinvented.steppingstones` | **656 `ResearchProjectDef` operations** — the entire research cost/graph rewritten, 112 of them on projects our own patches also touch | 34 own defs, 0 placed, 13 reference-only |
| `als.gravtech` + `als.gravtech.bc` | 9 `ResearchProjectDef/baseCost` replaces, `damageAmountBase` on 2 projectiles, 14 `statBases` | 169 + 42 own defs, 0 placed |
| `gravenwitch.vsrexamined` — Vanilla Skills Rexamined | **51 `ExpertiseDef/statOffsets` replaces + 12 `StatDef/parts`** — work-speed multipliers across every skill | 5 own defs, 0 placed |
| `jellypowered.survivaltools` | 157 `modExtensions` adds gating work speed on tool possession, 13 `WorkGiverDef` `requiredStats`, 4 `statBases`, 3 `StatDef/description` | 62 own defs, **4 placed tools** |
| `frozensnowfox.complexjobs` | **702 `WorkGiverDef/workType` + 326 `priorityInType` replaces**, 249 `robotWorkTypes`, 66 alien-race inherent/forbidden work types | 28 own defs, 0 placed. Work *assignment*, not work *speed* — in scope only under the widened ruling |
| `zal.betterinfestations` | 18 `ThingDef/race` replaces on insects + `IncidentDef/baseChance` + `minRefireDays` | 19 own defs, **40 placed** (`BI_Infestation_SitePart` ×20, `BI_InfestationWorldObject` ×20) |
| `samael.npcmechsandanimals` | 50 `FactionDef/pawnGroupMakers/options` + 6 `guards` adds — injects animals into `Pirate`/`Empire` raid rosters | 0 own defs, 0 placed |
| `dizzyeevee.bettercrossbreeding` + `dizzyeevee.rheng` | 7 `ThingDef/race` + `canCrossBreedWith` | 0 / 3 own defs, 0 placed |
| `sarg.alphamemes` + `vanillaexpanded.vmemese` | `statOffsets`/`WORK` operations on thoughts and memes; 35 and 32 exact collisions with defs we patch | 2,080 and 1,001 own defs; **622 and 234 placed** — the campaign ideoligion is built on them. ⛔ Not retirable without re-authoring the religion |
| `grimterra.biomesmod` | 103 `TileMutatorDef/biomeWhitelist` adds, 15 `BiomeDef` ops | 279 own defs, **782 placed plants** (`GRim*Shrub`/`Bush`/`Brambles`, `AreebianBush`, `BushDandys`) — ground cover of the map |

### 2C. ✅ Named-suspect FALSE POSITIVES — measured, then cleared

Worth recording so nobody re-opens them.

- **`sihv.rombonesport` (Rim of Madness — Bones)** — 479 `statBases` adds looked
  like the largest animal-stat rewrite in the stack. Reading the operations:
  every one adds **`<BoneAmount>`, the mod's OWN stat**, to animals that would
  otherwise have none. It edits **no existing number**. Not a conflict.
- **`ali.growodysseyplants`** — 4 `ThingDef/plant` adds, all `<sowTags>`. No
  growth, yield or density number touched.
- **`memegoddess.giddyup`** — 38 `ThingDef/comps` adds on vanilla animals; the 16
  "exact collisions" are comp additions for mounting, not stat edits.
- **`zal.randomgrowthchoices`**, **`arkymn.bettergrowthmoments`** — the word
  "growth" is about **child growth moments**, not plants. Out of scope entirely.
- **`andrewraphaellukasik.allowdeadanimals`**, **`carnysenpai.enableoversizedweapons`**
  — designation QoL and weapon *draw* size respectively; no gameplay number.
- **`mlie.advancedbiomes`**, **`grimterra.terrainretexturemod`**,
  **`kopp.biomecompatibilityproject`**, **`zal.biomeskit`** — no operation on any
  wildAnimals/wildPlants/density field of a biome we paint. (`biomecompatibilityproject`
  is separately suspected upstream as the load-time padder in
  `biome_wildbiomes_evictions.py`'s header — that is a *mechanism* note, not a
  balance edit, and belongs to that item.)

### 2D. 🎨 Cosmetic-only bucket — lower priority, flagged not dropped

Per the owner's ruling these stay in their own bucket. **11 active third-party
mods ship no patch, no Def and no assembly at all** — pure texture/asset
overlays, provably incapable of changing a number:

`ks.aaretextured` (Alpha Animals Retextured) · `sirvan.mwretextured` ·
`sirvan.steelretexture` · `neronix17.retexture.charactereditor` ·
`aw.researchreinvented.retextured` · `halituisamaricanous.gravtechbigcannons` ·
`morphsassorted.biotechretex` · `sd.fa.reelsadjustments` · `sd.fa.vteadjustments` ·
`dubwise.dubsbadhygiene.thirst` · `zal.worldmapenhanced`

A further **12 mods patch only graphics fields** (`texPath`, `graphicData`,
`drawSize`, `color`) and no balance field: `lazyfridaystudio.genesexpandedeyes` ·
`jelheb.rusticmealretexture` · `bichang.moresculpture` · `zal.spaceports` ·
`vanillaexpanded.vcooke` · `nephlite.advexplosions` · `erdelf.humanoidalienraces` ·
`dizzy.candlesandmeditation` · `blues.forge` · `font.rimesis` ·
`flangopink.metalpipehorseshoe` · `adaptive.storage.framework`.

⚠️ **One mod does NOT belong in this bucket despite its name**:
`tidal.morevanilla.textures` ("More Vanilla Textures") replaces **15
`ThingDef/graphicData/drawSize`** values alongside 44 `texPath` swaps on vanilla
animals — `drawSize` is the same field `CreatureResize_Ashkarr.xml` owns. It is a
**numeric** conflict wearing a cosmetic name, and is the reason names were never
trusted in this census.

---

## 3. 🔴 Save cross-reference — done per mod, named per mod

Every retirement candidate was checked against the actual campaign save, not
against the mod-list dependency graph. **This is the check that tonight's two
reverted donor retirements (`STARWARS_DONOR_SUNSET_1` Wave 4,
`DROID_RETIRE_DEPOT_ASIMOV_1`) each passed a mod-graph check and still failed.**

Method: every candidate's own `<defName>`s were collected from its non-patch
XML, then counted in the save as `<def>NAME</def>` **thing instances** (the form
the `rimworld-savegame` skill requires — a bare defName grep returns 1 on a
world that does not contain the thing), and separately as **reference-only
tokens** in the save's other reference tags. Instances are placed objects;
reference-only means a bookkeeping roster entry — the class of residue Wave 4
already accepted and documented.

| mod | placed instances | reference-only kinds | verdict |
|---|---|---|---|
| `sarg.alphabiomes` | **23,830** (`AB_Obsidianstone` 23,819) | 211 | 🔴 **LANDMINE — do not retire** |
| `grimterra.biomesmod` | **782** (map ground cover) | 124 | 🔴 LANDMINE |
| `sarg.alphamemes` | **622** (ideo rituals/precepts) | 105 | 🔴 LANDMINE |
| `regrowth.botr.core` | **563** (map ground cover) | 73 | 🔴 LANDMINE |
| `oskarpotocki.vfe.tribals` | **312** (ideo rituals) | 26 | 🔴 LANDMINE |
| `vanillaexpanded.vmemese` | **234** (ideo precepts) | 56 | 🔴 LANDMINE |
| `redmattis.bigsmall.core` | **42** (genes on live pawns) | 64 | 🔴 LANDMINE |
| `zal.betterinfestations` | **40** (2 world objects) | 2 | ⚠️ real but small |
| `van.beasts` | **32** (`DA_MineableSteelBeetle` 31) | 83 | ⚠️ real but small |
| `vanillaexpanded.vgeneticse` | 14 | 435 | ⚠️ |
| `sarg.alphaanimals` | 12 | 307 | ⚠️ large reference residue |
| `zylle.morevanillabiomes` | 10 | 3 | ⚠️ + owns 3 painted biomes |
| `biomesteam.biomescore` | 6 | 45 | ⚠️ terrain **UNMEASURED** |
| `jellypowered.survivaltools` | 4 | 19 | ⚠️ |
| `iforgotmysocks.caravanadventures` | 3 | 16 | ⚠️ |
| `grimterra.terrainretexturemod` | 3 | 3 | terrain **UNMEASURED** |
| `redmattis.betterprerequisites` | 2 | 20 | ⚠️ |
| `biomesteam.biomespollutedlands` | 1 | 131 | reference residue only |
| `biomesteam.biomescaverns` | 0 | 376 | reference residue only |
| `veterano.mythicages.megafaunabestiary` | 0 | 138 | reference residue only |
| `chaoticenrico.bettertrees` | 0 | 83 | reference residue only |
| `biomesteam.biomesfossils` | 0 | 76 | reference residue only |
| `spino.megafauna` | 0 | 63 | reference residue only |
| `qux.comigo.bettertreesmod` | 0 | 50 | reference residue only |
| `mlie.beastsoftherim` | 0 | 45 | reference residue only |
| `mlie.advancedbiomes` | 0 | 33 | reference residue only |
| `als.gravtech` / `.bc` | 0 | 58 / 29 | reference residue only |
| `petetimessix.researchreinvented.steppingstones` | 0 | 13 | reference residue only |
| `vanillaexpanded.vaewaste` | 0 | 18 | reference residue only |
| `joe.cephaloids` | **0** | 5 | ✅ **save-clean** |
| `vanillaexpanded.vplantsesucculents` | **0** | 11 | ✅ **save-clean** |
| `tyrannidae.littlecritters` | **0** | 5 | ✅ save-clean |
| `erin.ffanimals` | **0** | 11 | ✅ save-clean |
| `dizzyeevee.rheng` | **0** | 2 | ✅ save-clean |
| `smxrez.makeshiftreexamined` | **0** | 2 | ✅ save-clean |
| `coldcrow.betterkibble` | **0** | 1 | ✅ save-clean |
| `frozensnowfox.complexjobs` | **0** | 0 | ✅ **save-clean, zero of either** |
| `gravenwitch.vsrexamined` | **0** | 0 | ✅ save-clean |
| `aelanna.fistnerf` | **0** | 0 | ✅ save-clean |
| `victor.buymore` | **0** | 0 | ✅ save-clean |
| `memegoddess.giddyup` | **0** | 0 | ✅ save-clean |
| `dizzyeevee.bettercrossbreeding` | **0** | 0 | ✅ save-clean (ships no defs) |
| `fluxilis.germanquality` | **0** | 0 | ✅ **save-clean — ships zero defs** |
| `zylle.moredangerousgame` | **0** | 0 | ✅ **save-clean — ships zero defs** |
| `mlie.choosebiomecommonality` | **0** | 0 | ✅ save-clean — ships zero defs |
| `mlie.harvestwhenbutchering` | **0** | 0 | ✅ save-clean — ships zero defs |
| `archie.turrettargetpatch` | **0** | 0 | ✅ save-clean — ships zero defs |
| `farhanfair.warcaskettweakspatch` | **0** | 0 | ✅ save-clean — ships zero defs |
| `farxmai2.vanilladeconstructablevehicles` | **0** | 0 | ✅ save-clean — ships zero defs |
| `mosi.rebalancedancientjunk` | **0** | 0 | ✅ save-clean — ships zero defs |
| `summersausages2ttv.techlevelenforcement` | **0** | 0 | ✅ save-clean — ships zero defs |
| `doomdrvk.unlimitednuzzles` | **0** | 0 | ✅ save-clean — ships zero defs |
| `ks.aaretextured` and the 10 other pure overlays | **0** | 0 | ✅ save-clean — ship zero defs |
| `samael.npcmechsandanimals` | **0** | 0 | ✅ save-clean — ships zero defs |
| `ali.growodysseyplants` | **0** | 0 | ✅ save-clean — ships zero defs |
| `daria40k.alphaanimalspatchoutposts` | **0** | 0 | ✅ save-clean — ships zero defs |

🔴 **The landmine this check found that a mod-graph check would have missed**:
**`sarg.alphabiomes` holds 23,819 placed `AB_Obsidianstone` instances in the
campaign save.** Ten of our 23 painted biomes are its BiomeDefs, its rock is the
map substrate, and its `wildBiomes` injections are the single largest share of
the 2,998 evictions we counter-patch. Nothing in the mod-dependency graph says
so — no active mod declares a dependency on it. It would have looked
retirable and taken the campaign with it. Same shape, one order down:
`grimterra.biomesmod` (782), `sarg.alphamemes` (622), `regrowth.botr.core` (563).

---

## 4. Waves, ordered by real measured risk

**Nothing below is executed by this item.** Each wave gets its own item, and per
`WEAPONS_DONOR_RETIREMENT_1`'s established discipline: back up
`ModsConfig.xml` to `infrastructure/state/modlists/`, retire ONE wave, cold-load
verify, `harvest_log.py` baseline unchanged, before the next. Never bundle two
waves into one restart — different risk classes.

### Wave 1 — zero content, zero save presence, biggest numeric win *(13 mods)*

Every mod here ships **no defs at all** or **zero placed instances and ≤2
reference tokens**, so retirement is a pure subtraction of number-edits.

`fluxilis.germanquality` · `zylle.moredangerousgame` · `farhanfair.warcaskettweakspatch` ·
`aelanna.fistnerf` · `mosi.rebalancedancientjunk` · `farxmai2.vanilladeconstructablevehicles` ·
`coldcrow.betterkibble` · `doomdrvk.unlimitednuzzles` · `victor.buymore` ·
`mlie.harvestwhenbutchering` · `archie.turrettargetpatch` · `samael.npcmechsandanimals` ·
`mlie.choosebiomecommonality` *(retire for doing nothing — the world is frozen)*

**Lead item for the wave**: `fluxilis.germanquality`. A 1,114-byte mod applying a
0.5×–10× multiplier to `MaxHitPoints` on everything with a quality level is the
single largest silent distortion of any number we would normalize, and it costs
nothing to remove.
⚠️ Verify before executing: whether **`summersausages2ttv.techlevelenforcement`**
belongs here — 0 defs and 0 save presence, but it carries a large assembly and
gates equipment availability rather than values; that is a design question, not a
numbers one.

### Wave 2 — save-clean but content-bearing: cut = lose creatures/plants *(9 mods)*

🟢 **RULED (owner, 2026-09-11, three cards at the bench).** Execution items:
`BMT_FAUNA_ABSORPTION_1` (port the 71 cast BMT creatures, then retire) and
`STAT_NORM_WAVE2_RETIRE_1` (port Cephaloids + VE Succulents + VAE Waste's used
animals, then retire those three; Megafauna / Mythic Ages / FF Animals /
Little Critters / the dizzyeevee crossbreeding pair are verify-then-retire —
per-def roster+save re-check each, any cast find escalates back to the owner).
Measured basis: BMT had 124 sitting rows (41 in / 30 move / 53 out); JOE_ 3
moves; VAEWaste_ 3 rows; the other five had zero rows under any known prefix.

Zero placed instances, but each ships real content that vanishes on retirement.
Each needs a keep-or-port call, not a delete.

| mod | what is lost |
|---|---|
| `joe.cephaloids` | 10 defs — and its *entire* patch surface is injecting them into 5 of our painted biomes. The cleanest single decision in the whole audit |
| `vanillaexpanded.vplantsesucculents` | 12 succulent defs, whose only patch surface is 24 `wildPlants` adds on our three desert biomes — thematically the most defensible desert flora in the stack |
| `spino.megafauna` | 92 defs, 231 desert `wildBiomes` entries |
| `mlie.beastsoftherim` | 45 defs |
| `veterano.mythicages.megafaunabestiary` | 343 defs |
| `erin.ffanimals` | 16 defs |
| `tyrannidae.littlecritters` | 5 defs |
| `dizzyeevee.bettercrossbreeding` + `dizzyeevee.rheng` | crossbreeding mechanic + 3 defs |
| `vanillaexpanded.vaewaste` | 55 defs, 12 pollution-spawn adds |

### Wave 3 — widened-scope knob mods entangled with open work *(6 mods)*

🟢 **RULED (owner, 2026-09-11, four cards).** Research trio → retire + re-validate
the (already-closed) recost via `RESEARCH_TRIO_RETIRE_1`; vsrexamined +
survivaltools → retire TOGETHER with the 4-placed-tools save cleanup
(`STAT_NORM_WAVE3_RETIRE_1`); complexjobs → **KEEP, declared resident**
(recorded in `mod_config_rulings.md`); caravanadventures → strip stats, keep
quests (counter-patch, same Wave-3 item).

Real conflicts, but each collides with an item or doctrine already in flight;
sequence with the owner, not standalone.

- `petetimessix.researchreinvented.steppingstones` (656 research operations) and
  `als.gravtech` / `als.gravtech.bc` (research `baseCost`) — collide with
  `RESEARCH_*` work and `design/Jawa/research_normalization_principles.md`.
- `gravenwitch.vsrexamined` and `jellypowered.survivaltools` — both rewrite
  work-speed; retiring one without the other leaves a half-normalized economy.
- `frozensnowfox.complexjobs` — 1,028 work-assignment operations. Zero save
  presence, but every pawn's work tab in the campaign is shaped by it.
- `iforgotmysocks.caravanadventures` — armour/bodySize/combatPower edits ride a
  whole quest layer with 3 live world objects.

### Wave 4 — 🔴 needs an explicit owner call; several are NOT retirable *(the rest)*

🟢 **RULED (owner, 2026-09-11, three cards) — every Wave-4 call made.** All
recommended keeps CONFIRMED as ruled permanent residents (Alpha Biomes; the
ideoligion trio; ReGrowth + GrimTerra ground cover; keep-and-suppress for More
Vanilla Biomes / Alpha Animals). ⚠️ **Biomes-team EXCEPTION (owner, same-day
conflict ruled at the 2026-09-11 card sitting):** the earlier 00:03 specific
correction STANDS over this sweeping confirm — `biomesteam.biomescaverns` /
`biomescore` / `biomespollutedlands` are **port-then-RETIRE** (retire once
`BMT_FAUNA_ABSORPTION_1`'s three escalation gates clear and the RSW_ port is
proven live), not keep-and-suppress. MVB and Alpha Animals are unaffected. Big and Small: **the scaling
experiment STANDS** — reconfirmed against the widened ruling, no silent
override. More Vanilla Textures: keep the retextures, **counter-patch its 15
drawSize replaces to neutral** (rides `STAT_NORM_WAVE3_RETIRE_1`'s
counter-patch bucket) so bodySize-from-visual owns drawSize. With this, all
four waves are ruled; the audit item closes and execution lives in the wave
items.

- ⛔ **`sarg.alphabiomes`** — 23,819 placed instances, 10 of our 23 painted
  biomes. **Recommend: keep, permanently.** Its `wildBiomes` injections are
  suppressed by the eviction file we already ship; that is the correct answer
  here, not retirement.
- ⛔ **`sarg.alphamemes`, `vanillaexpanded.vmemese`, `oskarpotocki.vfe.tribals`** —
  622 / 234 / 312 placed instances; the campaign ideoligion is built on them.
  Not retirable without re-authoring the religion.
- ⛔ **`regrowth.botr.core`, `grimterra.biomesmod`** — 563 and 782 placed plants;
  they are the map's ground cover. Retirement means re-authoring the flora.
- ⚠️ **`redmattis.*` (Big and Small)** — `mod_config_rulings.md` §3 already
  records this as a *deliberate scaling experiment*. Per
  `STARWARS_DONOR_SUNSET_1`'s lightsaber precedent, **a sweeping instruction does
  not silently overrule a specific prior ruling** — this needs reconfirmation,
  not a silent override.
- ⚠️ **`zylle.morevanillabiomes`, `sarg.alphaanimals`, `biomesteam.*`** — each
  owns painted biomes or large reference residue; keep-and-suppress is the likely
  answer, but the owner should say so rather than have it inferred.
- ⛔ **`mlie.starwarsanimalcollection`** — out of scope here; `MLIE_FAUNA_ABSORPTION_1`
  owns it.
- 🎨 **The 23 cosmetic-bucket mods** — lower priority by ruling; no numeric
  argument for or against, except `tidal.morevanilla.textures`, which is NOT
  cosmetic (15 `drawSize` replaces) and should be judged as a Wave 1 knob-turner.

---

## 5. Open questions for the owner

1. **Wave 1 — go?** 13 mods, zero content lost, zero save presence, and it
   removes a global 0.5×–10× HP multiplier plus a whole predator-behaviour
   overhaul before any tuning starts.
2. **Big and Small**: `mod_config_rulings.md` calls it a deliberate scaling
   experiment. Does "we're owning our whole loadout" end that experiment, or does
   the ruling stand?
3. **Wave 2 is a fauna/flora keep-or-cut sitting**, not a retirement list — nine
   mods, each losing real creatures or plants. Worth the review-sheet treatment
   (`skills/review-sheets`) rather than a yes/no per mod?
4. **`tidal.morevanilla.textures`** replaces 15 vanilla-animal `drawSize` values,
   which is the field `CreatureResize_Ashkarr.xml` owns. Cut it, or fold its
   sizes into our own resize file?
