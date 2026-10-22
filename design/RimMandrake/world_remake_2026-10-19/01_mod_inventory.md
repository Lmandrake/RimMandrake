# World remake 01: what every mod in the live list is to us (2026-10-19)

FOUNDRY, offline. No game, no bridge. **Nothing here is a ruling.** Every class below is either an owner ruling
already on record (cited by card number from `design/RimMandrake/mod_audit/OWNER_RULINGS.md`) or this pass's
recommendation, and each row says which.

## 0. Answer

The live list (`ModsConfig.xml`, parsed as `activeMods`, file time 2026-10-19 06:03 PDT) has **536 mods**:
6 Ludeon (Core + 5 DLC), 62 ours (`mandrake.*`), **468 third-party**. It is identical, in order, to
`infrastructure/state/modlists/ModsConfig.FULL.DONOR_FREE_536_weathersuite_2026-10-19.xml`.

| class | mods | what it means |
|---|---:|---|
| A. retired already | 22 | owner-ruled, off the live list (`infrastructure/state/facts/retired_mods.json`); 0 of 22 are active |
| B. retire now | **39** | owner-ruled 2026-10-10 as Retirement Wave 1; gates met offline; **not executed** (§2) |
| C1. likely retire, replicate first | 28 | an owner direction to rebuild it, or our content still hard-depends on it |
| C2. likely retire, simply drop | 124 | registry PHASE-OUT or ELIMINATE, no ruling yet; nothing of ours hard-depends on it |
| D. dev and authoring only | 21 | keep while we build; strip from the player list at release (C04 and dev tooling) |
| E. evaluation-hostile | 32 (overlap) | exclude from dev test tiers; ship decision separate (§7) |
| F1. keep, framework we hard-depend on | 24 | |
| F2. keep, content or QoL | 232 | nothing of ours hard-depends on them; registry KEEP |

A + B + C1 + C2 + D + F1 + F2 = 22 retired + 468 live. E overlaps the others.

🔑 **Three findings the owner has not been told yet:**

1. **Retirement Wave 1 never ran.** 39 of its 40 packageIds are still on the live list (only `mlie.beastsoftherim`
   is gone, plus the Torment Master list entry). Its items are filed and nothing else
   (`WAVE1_MODLIST_RETIRE_37_IN_ONE_LOAD`, `CHERRY_PICKER_RESTORE_FROM_SHIP_PROFILE`: ledger shows only `file`
   events). Its candidate list `ModsConfig.WAVE1_CANDIDATE.xml` (514) predates the 2026-10-18 donor retirement, so it
   still names the seven donors retired since and lacks `mandrake.rut.weathersuite`. It must be rebuilt as
   *live list minus the 39* before use. The world remake is the natural moment to run it.
2. **`ModsConfig.FULL.LATEST.xml` (542) is stale**: it still lists the seven donors retired 2026-10-18
   (`grimterra.biomesmod`, `lingluo.cockroach`, `mlie.horrors`, `oskarpotocki.vfe.insectoid2`, `regrowth.botr.core`,
   `sarg.alphagenes`, `who.vfee.isopodageneline`) and lacks `mandrake.rut.weathersuite`. A `--restore` to
   FULL.LATEST would put them back.
3. **Texture dependence on third-party mods is ~0.** `donor_retire_census.py srctex`: of 3,402 texPaths our src XML
   names, 3,152 resolve in our src, 92 to another mandrake mod, 146 vanilla, 10 vanilla retextures, 1 DONOR
   (`aoba.fortress.industrial`, `Things/Building/Linked/Wall`, a known false positive: a Core appearance folder),
   1 MISSING. **Our dependence on third-party mods is defNames, classes and modDependencies, not art.**

## 1. Method and instruments

All counts are from one census run 2026-10-19 (session scratchpad `inv/inv.py`, not committed; the per-mod output
was folded into the tables below).

- **Active list:** `ET.parse(ModsConfig.xml).find("activeMods")`. 536 rows.
- **Who owns each defName:** the def dump database `DefDump/defs.sqlite` (`measure/dumpdb.py`, capture
  2026-10-19T11:23:54Z, 542 mods, 77,754 defs). Its mod set differs from the live list by exactly the seven
  2026-10-18 retirees (in the dump, not live) and `mandrake.rut.weathersuite` (live, not in the dump); every one of
  the 468 live third-party mods is in it. ⚠️ The dump attributes a vanilla def that a mod re-declares to that mod
  (Stronger Quality Scaling "owns" `AccuracyLong`; Survival Tools owns `ResearchSpeed`). Those are removed by
  excluding the 11,611 `<defName>`s found in the game's own `Data/` XML (grep, 2026-10-19), and all-lowercase
  tokens (`chassis`, `cold`).
- **How our content names them:** every XML under `src/` (not `obj/`, `bin/`, `Transient/`) parsed as elements
  (comments never count): element text, element tags, attribute values, defNames inside `xpath`. A file under
  `/Defs/` is a def reference; under `/Patches/` a patch reference. Each def reference is then checked for a
  `MayRequire`/`MayRequireAnyOf` on itself or an ancestor: **unguarded** means it breaks or dangles when the mod
  leaves.
- **Other edges:** `MayRequire` attributes naming the packageId; `PatchOperationFindMod` `<mods>` naming the mod's
  About name; our `About.xml` `modDependencies`/`loadAfter`/`forceLoadAfter`; `.csproj` `HintPath`/`Reference` to the
  mod's DLLs; `ParentName` values not defined in our src (181) resolved against the game's `Data/` (179) and then
  the mods (`AdaptiveStorageBase` -> Adaptive Storage Framework, `SpecialResearchOpportunityBase` -> Research
  Reinvented); `Class=` namespaces (the mod-audit 2026-10-10 `class_ref` edge, `mod_audit/facts/mod_facts.jsonl`, is
  quoted as "(10-10)" because it reads the DLLs' TypeDef tables, which this pass did not repeat).
- **Dependants:** active third-party mods whose `modDependencies` list the mod (from `mod_facts.jsonl`, 2026-10-10).
- **Decisions:** `design/RimMandrake/mod_audit/MASTER_REGISTRY.jsonl` `final_decision` (all 468 live third-party
  mods have a row: KEEP 267, PHASE-OUT 158, ELIMINATE 43) and `OWNER_RULINGS.md`.
- **Sanity probes:** `RSW_Gizka` is found in 14 src files; 1,064 `MayRequire` file-edges; 77,754 defs in the
  database; the guard walk finds Outland Genetics' 334 unguarded gene names in `StarWarsRaces`, the known hard case.
- **Classes in the "our dependence" column:** **HARD** = a `modDependencies` entry of ours, a C# project reference,
  a `ParentName` into it, a class it defines (10-10), or an unguarded defName. **soft** = only guarded rows, patches,
  `FindMod`, `MayRequire`. **order only** = only `loadAfter`. **none** = no edge at all.
- **Evidence column** counts files (`f`). "defs N names (U unguarded in Ff)" = N of its defNames named in our Defs
  files, U occurrences without a guard, in F files.
- **UNMEASURED:** string defName references inside C# (only `.cs` string literals were matched, and they are
  folded into nothing here); defs reached by `text()=` xpaths; whether each guarded row would leave a hole in a
  roster when its mod goes (that is per-biome review work, not a load question).

## 2. A. Retired already (22, all off the live list)

| packageId | name | retired | how |
|---|---|---|---|
| `veterano.mythicages.megafaunabestiary` | Mythic Ages: Megafauna Bestiary | 2026-09-05 | owner ruling 2026-09-05; zero dependents, nothing absorbed |
| `Spino.Megafauna` | Megafauna | 2026-09-05 | owner ruling 2026-09-05; every reference was conditional and is deleted |
| `Mlie.JurassicRimworldDinosaursOnly` | Jurassic Rimworld - Dinosaurs Only (Continued) | 2026-09-05 | owner ruling 2026-09-05; eight creatures absorbed into mandrake.rsw.swbestiary |
| `Mlie.BeastsoftheRim` | Beasts of the Rim (Continued) | 2026-09-05 | owner ruling 2026-09-05; content absorbed, hard dependency removed |
| `petetimessix.researchreinvented.steppingstones` | Research Reinvented: Stepping Stones | 2026-09-18 | RESEARCH_TRIO_RETIRE_1, owner ruling 2026-09-18 (port all 17, then cut); its 10 owned ResearchProjectDefs (RR_… |
| `als.gravtech` | GravTech | 2026-09-18 | RESEARCH_TRIO_RETIRE_1, owner ruling 2026-09-18 (port all 17, then cut); its 6 named ResearchProjectDefs (Grav… |
| `als.gravtech.bc` | GravTech - Big cannons | 2026-09-18 | RESEARCH_TRIO_RETIRE_1, owner ruling 2026-09-18 (port all 17, then cut); its 1 owned ResearchProjectDef (GTbc_… |
| `halituisamaricanous.gravtechbigcannons` | GravTech - Big cannons Retextured | 2026-09-18 | RESEARCH_TRIO_RETIRE_1 fallout: hard modDependencies on als.gravtech.bc (see that entry), cosmetic-only retext… |
| `biomesteam.biomescore` | Biomes! Core | 2026-09-27 | owner 2026-09-27: 'try to fix the savegame then retire the retirable'. No active mod or src/ file hard-depends… |
| `Sapiently.TheyAtomicMonsters` | They! (Giant Ants) | 2026-09-28 | owner 2026-09-24: queued for replacement and retirement. Its whole surface (race, 2 pawnkinds, hidden raid fac… |
| `mlie.moevents` | Mo'Events (Continued) | 2026-09-29 | owner-ruled scope: port 7 of 8 Mo'Events map-event mechanisms natively (8th, RescueTraitor, CUT 2026-09-11 -- … |
| `mlie.starwarsanimalcollection` | Star Wars Animal Collection (Continued) | 2026-10-18 | owner 2026-10-18: "Just put in placeholder art for now or donor copies and retire these mods!!! Just get it do… |
| `sarg.alphaanimals` | Alpha Animals | 2026-10-18 | owner 2026-10-18: "Just put in placeholder art for now or donor copies and retire these mods!!! Just get it do… |
| `daria40k.alphaanimalspatchoutposts` | Alpha Animals Patch for Outposts | 2026-10-18 | owner 2026-10-18: "Just put in placeholder art for now or donor copies and retire these mods!!! Just get it do… |
| `sarg.alphabiomes` | Alpha Biomes | 2026-10-18 | owner 2026-10-18: "Just put in placeholder art for now or donor copies and retire these mods!!! Just get it do… |
| `sarg.alphagenes` | Alpha Genes | 2026-10-18 | owner 2026-10-18: "Just put in placeholder art for now or donor copies and retire these mods!!! Just get it do… |
| `oskarpotocki.vfe.insectoid2` | Vanilla Factions Expanded - Insectoids 2 | 2026-10-18 | owner 2026-10-18: "Just put in placeholder art for now or donor copies and retire these mods!!! Just get it do… |
| `grimterra.biomesmod` | GrimTerra | 2026-10-18 | tail-mod retirement, design/RimMandrake/tail_mods_art_retirement_2026-10-18.md; FlowWorks ChunkStone still rea… |
| `who.vfee.isopodageneline` | Isopoda Geneline | 2026-10-18 | tail-mod retirement, design/RimMandrake/tail_mods_art_retirement_2026-10-18.md; FlowWorks ChunkStone still rea… |
| `regrowth.botr.core` | ReGrowth 2 (BOTR core) | 2026-10-18 | tail-mod retirement, design/RimMandrake/tail_mods_art_retirement_2026-10-18.md; FlowWorks ChunkStone still rea… |
| `mlie.horrors` | Horrors | 2026-10-18 | tail-mod retirement, design/RimMandrake/tail_mods_art_retirement_2026-10-18.md; FlowWorks ChunkStone still rea… |
| `lingluo.cockroach` | Cockroach | 2026-10-18 | tail-mod retirement, design/RimMandrake/tail_mods_art_retirement_2026-10-18.md; FlowWorks ChunkStone still rea… |

## 3. B. Retire now: Retirement Wave 1 (owner-ruled 2026-10-10; 39 still live)

Definition: `design/RimMandrake/mod_audit/RETIREMENT_WAVE_1.md`; run sheet `RETIREMENT_WAVE_1_RUN_SHEET.md`. Every
offline gate is met (per-mod table in its §3, 0 type references from our C#). The fresh census agrees: one row is
HARD, and it is the Pyrinth swap whose replacement (`mandrake.rm.pyrinth`) is built and deployed but **not on the
live list**. "Replicate vs drop" is in the last column.

| mod | packageId | our dependence | evidence (fresh census) | active 3rd-party mods that hard-depend on it | recommendation |
|---|---|---|---|---|---|
| [HMC]Wall Furniture | `hmc.wall.furniture` | none | none | 0 | **C10**: drop |
| [SYR] More Slaves (Continued) | `mlie.syrmoreslaves` | none | none | 0 | **C07**: drop now; study as above |
| AA FancyRats | `armoredampharos.fancyrats` | none | none | 1: tyrannidae.fancyratsplus | **C19**: drop |
| Alpha Mechs | `sarg.alphamechs` | soft | patches 4f; FindMod 1f; About 2f | 0 | **C15**: drop |
| Aqued Dredge Aberrations | `aqued.dredgeaberrations` | none | none | 0 | **C19**: drop (absorb is a design note only) |
| AuthenticTantrumNoises | `kshtantrumsounds.mod` | none | none | 0 | **C19**: drop |
| Cremation smelts apparels | `thumb.bettercremation` | none | none | 0 | **C13 card**: drop; one salvage rule replaces it |
| Dark Ages : Crypts and Tombs | `van.dacrypts` | none | none | 0 | **C19**: drop |
| Dedicated Turrets | `clown.dedicatedturrets` | none | none | 0 | **C10**: drop, add back if needed |
| Destiny Exotic Weapons | `milkwater.destinymod` | order only | About 1f | 0 | **C15**: drop |
| Epochs - Pyrinth | `det.epochspyrinth` | HARD | defs 12 names (29 unguarded in 4f); patches 3f; MayRequire 1f; FindMod 1f; About 1f | 0 | **Pyrinth swap**: already replicated: mandrake.rm.pyrinth redefines every DV_ def verbatim |
| FancyRats+ | `tyrannidae.fancyratsplus` | none | none | 0 | **C19**: drop |
| Large Faction Bases (Continued) | `mlie.largefactionbases` | none | none | 0 | **C09**: drop; owner: study to learn |
| LightsOut | `juanlopez2008.lightsout` | none | none | 0 | **C10**: drop, add back if needed |
| Medieval Melee Sounds | `bonible.medievalmeleesounds` | none | none | 0 | **C19**: drop |
| Metal Pipe | `flangopink.metalpipe` | none | none | 0 | **C19**: drop |
| Metal Pipe Horseshoe Replacement | `flangopink.metalpipehorseshoe` | none | none | 0 | **C19**: drop |
| MinifyEverything | `erdelf.minifyeverything` | none | none | 0 | **C10**: drop; minifiability becomes a Salvage-action question |
| Raid Protection Fee | `leo.raidprotectionfee` | none | none | 0 | **list regression**: drop |
| Reel's Turret Pipeline | `reel.turretpipeline` | none | none | 0 | **C10**: drop, then add back key function |
| Storyteller Enhanced (Continued) | `mlie.storytellerenhanced` | none | none | 0 | **C09**: drop |
| Survival Tools Reborn | `jellypowered.survivaltools` | none | none | 0 | **list regression**: drop |
| Vanilla Quests Expanded - Ancients | `vanillaquestsexpanded.ancients` | soft | defs 1 names (2 unguarded in 1f); patches 4f; FindMod 3f; About 2f; FALSE POSITIVE: VQE_Experiment is a backstory spawnCategory string in PawnFlavor (wave-1 doc: unreachable once the mod leaves) | 0 | **C15**: drop; save quest rows removed by W3 |
| Vanilla Skills Rexamined | `gravenwitch.vsrexamined` | none | none | 0 | **list regression**: drop |
| Vanilla Weapons Expanded | `vanillaexpanded.vwe` | soft | patches 4f; FindMod 1f; About 3f | 0 | **C15**: drop; save relics repaired by W3 |
| We Are United | `sl4vp0wer.weareunited` | none | none | 0 | **C07**: drop now; owner: study it to build our own crew-growth quests |
| Belt Extractors - VFE Factory Patch | `groovytaco.beltextractors` | none | none | 0 | **C10**: drop, then add back key function (convenience_replacements.md) |
| WallStuff | `arcjc007.wallstuff` | none | none | 0 | **C10**: drop |
| [kyzy] Ship Wall Enhanced | `kyzy.shipwallenhanced` | none | none | 0 | **C10**: drop |
| Ancient Ruins All Deconstructible | `meteores.ancienturbanruinsalldeconstructible.aurad` | none | none | 1: meteores.ancienturbanruinsvanillaloot.aurvl | **C22 shell (W4b)**: drop |
| Vanilla Skills Expanded | `vanillaexpanded.skills` | soft | defs 2 names (3 unguarded in 3f); FALSE POSITIVE: 'Butcher'/'Major' match an enum value and prose, not VSE defs | 2: gravenwitch.vsrexamined, sarg.alphaskills | **C08**: drop; as above |
| Alpha Skills | `sarg.alphaskills` | none | none | 0 | **C08**: drop; save passions mapped by wave1_save_preedit.py |
| Ancient Urban Ruins Hit Point | `meteores.ancienturbanruinsvanillaloot.aurvl` | none | none | 0 | **C22 shell (W4b)**: drop |
| ChezhouLib | `chezhou.chezhoulib.lib` | none | none | 1: chezhou.creature.sandworm | **C02**: drop with Sandworm |
| Rimesis | `font.rimesis` | none | none | 0 | **C09**: drop |
| WarCasket Expanded | `aoba.warcasket` | soft | patches 1f; FindMod 1f; About 1f | 0 | **C15**: drop |
| LEVIATHANS:SANDWORM | `chezhou.creature.sandworm` | none | none | 0 | **C02**: already replicated: our Long Hunger (mandrake.rut.longhunger) |
| Shield Generators | `neronix17.shieldgenerators` | none | none | 0 | **C10**: drop, add back if needed |
| Big and Small - Races | `redmattis.bigsmall` | soft | patches 1f; About 1f | 0 | **C22 shell (W4b)**: drop |

Not in the wave, held: `xmb.ancienturbanruins.mo` (not save-safe; see C1).

## 4. C1. Likely retire, replicate (or port) first (28)

Owner direction in the row where one exists; otherwise our content still hard-depends on the mod.

| mod | packageId | our dependence | evidence (fresh census) | active 3rd-party mods that hard-depend on it | recommendation |
|---|---|---|---|---|---|
| Advanced Biomes (Continued) | `mlie.advancedbiomes` | HARD | defs 8 names (4 unguarded in 2f); patches 15f; MayRequire 8f; FindMod 4f; About 3f; class_ref 106 (10-10) | 0 | port VolcanoSoil/WastelandAsphalt/Poison* terrain+plants used by RM_Wastes and RUT_ twins |
| Alpha Memes | `sarg.alphamemes` | HARD | defs 7 names (6 unguarded in 1f); patches 8f; MayRequire 7f; FindMod 1f; About 3f | 0 | C01 port everything; but the 10-18 donor pass kept it STAY: TuskAttackTool, dryads, AM_ memes in faction defs |
| Det's Xenotypes - Keshig | `det.keshig` | HARD | defs 1 names (1 unguarded in 1f); patches 4f; About 1f | 0 | UtinniPatches reskins DV_PirateKeshig; 1 unguarded weapon name |
| Geological Landforms | `m00nl1ght.geologicallandforms` | order only | About 1f | 1: m00nl1ght.geologicallandforms.biometransitions | C06: replicate if we can, else keep (LANDFORMS_REPLICATE_OR_KEEP_EXPERIMENT) |
| GravTide | `gravtide.mod` | none | none | 0 | C03: goes once our sea-floor layer works alone |
| More Vanilla Biomes | `zylle.morevanillabiomes` | HARD | defs 2 names (0 unguarded in 0f); patches 15f; MayRequire 2f; FindMod 2f; About 3f; class_ref 61 (10-10) | 0 | C01 port (biome content; patches + class refs on frozen RUT_ twins die at the paint) |
| Orc Clan + Xenotype | `karew.orcclan` | soft | patches 3f; FindMod 1f; About 1f | 0 | C20: stays until ported (Gamorreans) |
| Primordial Geysers | `ironscruff.primordialgeysers` | soft | defs 3 names (0 unguarded in 0f); patches 6f; MayRequire 2f; FindMod 2f; About 5f | 0 | port 3 grass/plant rows (guarded) into The Forge |
| Rim of Madness - Bones Unofficial Fix | `sihv.rombonesport` | soft | defs 1 names (0 unguarded in 0f); patches 6f; MayRequire 2f; FindMod 4f; About 2f | 0 | owner card: lean port of our own (bone as material), then retire |
| RimTek Core | `deon.rimtek.core` | none | none | 2: deon.rimtek.digipal, deon.rimtek.docmate | C21: retire with DigiPal and DocMate |
| Stronger Quality Scaling (1.6) | `kas.strongerscaling` | soft | patches 5f | 0 | rule with Yayo (deep dive §10) |
| Vanilla Factions Expanded - Tribals | `oskarpotocki.vfe.tribals` | HARD | defs 4 names (5 unguarded in 1f); patches 5f; FindMod 2f; About 3f | 0 | C01 port: 4 VFET_ research prereqs unguarded in ResearchRetag |
| Vanilla Furniture Expanded - Security | `vanillaexpanded.vfesecurity` | HARD | defs 2 names (2 unguarded in 1f); patches 6f; FindMod 3f; About 2f | 0 | replicate the unguarded names, then drop (registry KEEP-TEMPORA) |
| Vanilla Landmarks Expanded | `vanillaexpanded.vexploratione` | HARD | defs 1 names (1 unguarded in 1f); patches 3f; About 1f | 0 | replicate the unguarded names, then drop (registry KEEP-TEMPORA) |
| Vanilla Races Expanded - Archon | `vanillaracesexpanded.archon` | HARD | defs 1 names (1 unguarded in 1f); patches 4f; FindMod 2f; About 2f | 0 | C20: stays until ported (Mortis wanderers) |
| Vanilla Races Expanded - Genie | `vanillaracesexpanded.genie` | HARD | defs 1 names (1 unguarded in 1f) | 0 | replicate the unguarded names, then drop (registry KEEP-TEMPORA) |
| Vanilla Races Expanded - Saurid | `vanillaracesexpanded.saurid` | HARD | defs 1 names (11 unguarded in 1f); patches 3f; FindMod 1f; About 3f | 0 | replicate the unguarded names, then drop (registry KEEP-TEMPORA) |
| Yayo's Combat 3 (Continued) | `mlie.yayoscombat3` | order only | About 1f | 0 | deep dive: remove, port hand/foot coverage + skill-weighted accuracy, armour wear as a StatPart |
| Ancient urban ruins | `xmb.ancienturbanruins.mo` | soft | patches 5f; FindMod 4f; About 3f | 1: meteores.ancienturbanruinsvanillaloot.aurvl | held out of wave 1: not save-safe (placed shelf, live faction, precepts); its excision is a wave-2 item |
| Biome Transitions | `m00nl1ght.geologicallandforms.biometransitions` | none | none | 0 | C06: may simply go with baroque biomes (BIOME_TRANSITIONS_WITH_BAROQUE_JUDGE) |
| RimTek DigiPal | `deon.rimtek.digipal` | none | none | 0 | C21: our own bounty-hunter item replaces it, then retire |
| RimTek DocMate | `deon.rimtek.docmate` | none | none | 0 | C21: medical droid gets its capabilities (with bacta), then retire |
| Vanilla Ideology Expanded - Memes and Structures | `vanillaexpanded.vmemese` | soft | defs 12 names (0 unguarded in 0f); patches 4f; MayRequire 9f; FindMod 1f; About 2f | 0 | C01 port: VME_ memes named by our faction defs (guarded) |
| Vanilla Genetics Expanded | `vanillaexpanded.vgeneticse` | soft | defs 6 names (0 unguarded in 0f); patches 13f; MayRequire 3f; FindMod 3f; About 6f | 0 | C01-style port: GR_ hybrids in biome rows (guarded); pairs with Alpha Animals history |
| Alpha Vehicles - Neolithic | `sarg.alphavehiclesneolithic` | HARD | patches 6f; FindMod 4f; About 2f; modDependency of rsw.desertvehiclereskin | 0 | drop together with our DesertVehicleReskin (modDependency) or rebuild those carts on Vehicle Framework |
| Outer Rim - Core | `neronix17.outerrim.core` | HARD | defs 9 names (8 unguarded in 7f); patches 12f; MayRequire 1f; FindMod 7f; About 5f; modDependency of rsw.armoury, rsw.ionweapons | 4: leutiankane.mineablesor, leutiankane.mines2patchouterrim, neronix17.outerrim.galacticempire… | replicate: Armoury + IonWeapons declare it in modDependencies; beskar, hypertech component, blasters, faction |
| Outer Rim - Galactic Empire | `neronix17.outerrim.galacticempire` | HARD | defs 12 names (4 unguarded in 2f); patches 4f; MayRequire 2f; FindMod 3f; About 2f | 0 | replicate the 4 unguarded weapon/armour names in Inhabited cast rosters |
| Outer Rim - Rebel Alliance | `neronix17.outerrim.rebelalliance` | HARD | defs 1 names (1 unguarded in 1f); patches 4f; FindMod 1f; About 2f | 0 | replicate/rename OuterRim_A280Blaster in the Inhabited roster |

## 5. C2. Likely retire, simply drop (124)

Registry PHASE-OUT or ELIMINATE with no owner ruling, and **nothing of ours hard-depends** on any of them. "soft"
rows carry guarded patches or rows of ours: they stay load-safe if left, but delete them in the same change
("simply remove offending material"). C20's owner-ruled drops (Avaloi, Beliar, Posthuman Drift + Titan, VRE
Starjack) are here too.

| mod | packageId | our dependence | evidence (fresh census) | active 3rd-party mods that hard-depend on it | recommendation |
|---|---|---|---|---|---|
| Vanilla Backgrounds Expanded | `vanillaexpanded.backgrounds` | soft | MayRequire 2f; About 1f | 0 | registry PHASE-OUT; delete our guarded rows/patches with it. Why: Our own mandrake.rut.menushell ships 10 VBE.BackgroundImageDef rows (src/RimUtinni/MenuShell/Defs/BackgroundIm |
| [ZAV] Glowstone | `zav.glowstoneforked` | none | none | 0 | registry PHASE-OUT. Why: Harmless, but it is a donor content mod and the standing ruling is 'Everything should be moved to our own thin |
| Adaptive Ideology Storage | `adaptive.ideology.storage` | none | none | 0 | registry PHASE-OUT. Why: Pure cosmetic storage skins |
| Adaptive Primitive Storage | `adaptive.primitivestorage` | none | none | 0 | registry PHASE-OUT. Why: Same shape as its two siblings but the most on-genre for scavengers and tribal beginnings (cellars, baskets) |
| Adaptive Simple Storage | `adaptive.simplestorage` | none | none | 0 | registry PHASE-OUT. Why: A cosmetic storage-skin pack; the most generic of the three and the closest to an item a ship hold would use |
| Alien Worlds Framework | `7f.alienworlds` | order only | About 2f | 1: 7f.alienworlds.tidallylocked | registry PHASE-OUT. Why: It is a world-generation framework (brief section 4 test 5: dissonant; section 2: no worldgen), yet it is wire |
| Ambient Rim | `swablu.ambience` | none | none | 0 | registry PHASE-OUT. Why: Our own ambient layer is designed to replace it: design/RimMandrake/atmospheric_base_hook_ecosystem.md (line 4 |
| Ancient Dangers on Campsites and Encounter maps | `vita.campdangers` | none | none | 0 | registry PHASE-OUT. Why: Ancient Dangers are Ideology/Anomaly-style map events |
| Astronomy Style Pack | `asp.halituisamaricanous` | none | none | 0 | registry PHASE-OUT. Why: Pure cosmetic skin pack ('Inspired by midworld and argi-industrial art') |
| Beliar Xenotype | `elsov.beliar` | soft | patches 2f | 0 | owner-ruled drop: C20 (non-canon peoples go); delete our guarded rows first |
| Better Infestations (Continued) | `zal.betterinfestations` | soft | patches 3f; FindMod 2f; About 2f | 0 | registry PHASE-OUT C09; delete our guarded rows/patches with it. Why: Mismatch with a ruling: owner ruled the vanilla Infestation event banned planet-wide except the Dune Sea (RM_S |
| Better Trees | `chaoticenrico.bettertrees` | soft | FindMod 1f | 0 | registry PHASE-OUT; delete our guarded rows/patches with it. Why: Two of our mods patch its defs directly: src/RimUtinni/AshkarrFlora and src/RimMandrake/LeaningScrub ship Patc |
| Biome Compatibility Project | `kopp.biomecompatibilityproject` | none | none | 0 | registry ELIMINATE. Why: It directly contradicts the roster law: biome casts are hand-built per biome sitting and an animal belongs to  |
| Biomes! Framework | `biomesteam.coreframework` | none | none | 0 | registry ELIMINATE. Why: Nothing in the universe depends on it: dependants is empty, and the only Biomes! content pack in the list, bio |
| BiomesKit (Continued) | `zal.biomeskit` | none | none | 1: zal.comigogreaterswamps | registry PHASE-OUT. Why: Held by one dependant, zal.comigogreaterswamps (Comigo's Greater Swamps, a donor biome mod that REQUIRES Biome |
| Children Learn on Caravan [USE NEW FORK!] | `heatherathebyne.childrenlearnoncaravan` | none | none | 0 | registry PHASE-OUT. Why: The author's own description is "DEPRECATED .. |
| Custom Quest Framework | `hailuan.customquestframework` | none | none | 2: hailuan.customquestframeworkai, mlie.dungeonpack | registry PHASE-OUT. Why: A quest/map-authoring framework, not content |
| Cybranian - Ideology Virtues | `dimonsever000.ideologyvirtues` | none | none | 0 | registry PHASE-OUT. Why: Our ideoligion is authored and fixed (src/Jawa/ideoligion/MandrakeJawa.xtp lists the mod in its export mod lis |
| Dance Party Custom Music | `east.dancepartycustommusic` | none | none | 0 | registry PHASE-OUT. Why: design/RimMandrake/music_protocol.md (line 42) catalogues it: replaces only the lightball dance track and load |
| Dark Ages : Beasts and Monsters | `van.beasts` | soft | patches 8f; FindMod 2f; About 4f | 0 | registry PHASE-OUT; delete our guarded rows/patches with it. Why: Owner adopted it 2026-08-04 (user call), but that was before the recognizability rule and the 2026-09-20 "move |
| Det's Xenotypes - Avaloi | `det.avaloi` | soft | patches 1f | 0 | owner-ruled drop: C20; delete our guarded rows first |
| Det's Xenotypes - Boglegs | `det.boglegs` | soft | patches 1f | 0 | registry PHASE-OUT; delete our guarded rows/patches with it. Why: A merchant-people xenotype fits a Hutt-ledger, trade-driven setting (brief 1, the Bazaar), and nothing of ours |
| Det's Xenotypes - Brawnum | `det.brawnum` | soft | patches 1f | 0 | registry PHASE-OUT; delete our guarded rows/patches with it. Why: Labourer species is neutral for the setting; its caravan hauling bonus edges toward a stat advantage that the  |
| Det's Xenotypes - Buzzers | `det.buzzers` | soft | patches 3f; FindMod 1f; About 2f | 0 | registry PHASE-OUT; delete our guarded rows/patches with it. Why: Waste-eaters and scavenger-underclass bugs fit a junk-salvage frontier (brief 4 test 3) |
| Det's Xenotypes - Venators | `det.venators` | soft | patches 2f | 0 | registry PHASE-OUT; delete our guarded rows/patches with it. Why: Hunter people with a paralysis ability; neutral flavour |
| Engines Unlimited | `nep.enginesunlimited` | none | none | 0 | registry ELIMINATE. Why: Redundant and wrong-direction |
| Epochs - Incense | `det.epochsincense` | none | none | 0 | registry PHASE-OUT. Why: Decorative ritual item from a medieval-church-flavoured 'Epochs' mod set; nothing depends on it, and Ta'Baa's  |
| Face Addon Framework | `eoralmilk.faceaddonframework` | none | none | 0 | registry PHASE-OUT. Why: No universe mod lists it as a dependency (dependants empty), and a scan of XML and DLL text across the install |
| Faction Raid Cooldown (Continued) | `mlie.factionraidcooldown` | order only | About 1f | 0 | registry PHASE-OUT C09. Why: It softens raid cadence: more kills mean fewer raids |
| Guaranteed Ancient Dangers | `arti.shrinez` | none | none | 0 | registry ELIMINATE. Why: It forces an extra hazard-and-loot site onto every generated map |
| Highborn Xenotype | `elsov.highborn` | soft | patches 1f | 0 | registry PHASE-OUT; delete our guarded rows/patches with it. Why: Aristocrat xenotype with nothing of ours referencing it (src grep: 0 files, no patched_by edges) |
| I will be back | `hailuan.iwbb` | none | none | 0 | registry PHASE-OUT. Why: A random 'a former colonist returns' incident at baseChance 250 adds a population-gaining event the campaign d |
| Ideology symbols as Ideograms | `kxp.ideosymbolsasideograms` | none | none | 0 | registry PHASE-OUT. Why: Purely cosmetic (passes brief section 4 test 4) but its whole art source is vanilla/VE ideology icons, and the |
| Ion Weaponry (Continued) | `zal.ionweaponry` | soft | patches 1f | 0 | registry PHASE-OUT; delete our guarded rows/patches with it. Why: Our own work leans on it: mandrake.rsw.patches references its defs 21 times (patched_by) and src/RimMandrake/U |
| Large Outpost (Continued) | `zal.largeoutpost` | none | none | 0 | registry ELIMINATE. Why: A random faction-quest generator that hands out drop-pod loot worth thousands of silver |
| Laser Cannon | `arcjc007.lasercannon` | soft | patches 2f; FindMod 2f; About 1f | 0 | registry PHASE-OUT; delete our guarded rows/patches with it. Why: Genuinely on theme (a laser turret) and we already depend on it in the data: mandrake.rsw.armoury patches it t |
| LiquidSFX | `dorbo.watersfx` | none | none | 0 | registry PHASE-OUT. Why: Ambient water sound suits a planet with seas, rivers and a lava biome and passes brief section 4 test 4 |
| Medieval Signs | `mewn.medievalsigns` | none | none | 0 | registry ELIMINATE. Why: Medieval fantasy signage (inn, tavern, magic shop) is off-genre for the scenario (brief 4 test 3; donor_proper |
| MiningCo. Alert speaker (Continued) | `mlie.miningcoalertspeaker` | soft | patches 3f; About 1f | 0 | registry PHASE-OUT; delete our guarded rows/patches with it. Why: Adopted 2026-08-08 for 'strong thematic fit' (required_mods.md) and held in by our research retagging: mandrak |
| MiningCo. DrillTurret (Continued) | `mlie.miningcodrillturret` | soft | patches 4f; FindMod 1f; About 2f | 0 | registry PHASE-OUT; delete our guarded rows/patches with it. Why: Adopted (required_mods.md ADOPTED under the 'immobile production rule': a fixed resource generator you must le |
| MiningCo. MMS (Continued) | `mlie.miningcomms` | soft | patches 4f; FindMod 1f; About 1f | 0 | registry PHASE-OUT; delete our guarded rows/patches with it. Why: Adopted for the same reasons (required_mods.md) and held in by 18 of our patch references (researchretag 12, m |
| MiningCo. Spaceship (Continued) | `mlie.miningcospaceship` | soft | patches 2f; FindMod 2f; About 1f | 0 | registry PHASE-OUT; delete our guarded rows/patches with it. Why: Modern-corporate brand (brief 4 test 3 lists corporate brands as dissonant) and listed in donor_proper_noun_ba |
| More Faction Interaction (Continued) | `mlie.morefactioninteraction` | none | none | 0 | registry PHASE-OUT C09. Why: Not an ELIMINATE because no fit or duplication proof exists |
| My Little Planet | `oblitus.mylittleplanet` | order only | About 1f | 0 | registry PHASE-OUT. Why: It is a world-creation tool, which the scenario excludes as a player feature (brief section 2, test 5), but it |
| Natural Paths | `radzerp.naturalpaths` | none | none | 0 | registry PHASE-OUT. Why: A pure cosmetic terrain mod with no dependants and no edges from ours (patched_by empty) |
| Nightmare Core | `nightmare.core` | none | none | 1: icepickgma.invisibledisplaycase | registry PHASE-OUT. Why: Required by icepickgma.invisibledisplaycase (Invisible Display Case Continued, a cosmetic building to put item |
| Polyamory Beds (Vanilla Edition) | `meltup.polyamorybeds.vanilla` | none | none | 0 | registry PHASE-OUT. Why: required_mods.md lines 1206-1208 name Polyamory Beds as "optional QoL, not load-bearing" for the chosen polycu |
| Posthuman Drift Core Mod | `xylthixlm.races.core` | none | none | 1: xylthixlm.races.titan | owner-ruled drop: C20 (only Titan needs it) |
| Psilocap Cultivation | `laureeeeeeeeeeeeeeen.shrooms` | none | none | 0 | registry PHASE-OUT. Why: Cultivable psilocap is plant content, and plants are being ported into our own defs (brief 3, owner 2026-09-20 |
| Recycle This (Continued) | `mlie.recyclethis` | none | none | 0 | registry PHASE-OUT. Why: jawa_scavenge_system_design_2026-10-03.md (owner-ruled design, nothing built) lists Mlie.RecycleThis as a HARD |
| RimAI Framework | `kilokio.rimai.framework` | none | none | 1: kilokio.rimai.core | registry PHASE-OUT. Why: Held in by one dependant, kilokio.rimai.core (RimAI Core BETA: talk to an AI 'server/terminal' that sees your  |
| Roots of Rimworld | `ghost.rootsofrimworld` | soft | patches 2f; About 1f | 0 | registry PHASE-OUT; delete our guarded rows/patches with it. Why: Neolithic tribal decor from another game is off-genre for a Star Wars-style desert scavenger crew (brief secti |
| RW - Planet Atmosphere | `rwnodetree.rwplanetatmosphere` | none | none | 0 | registry PHASE-OUT. Why: Purely cosmetic and fits a planetary expedition feel, but it is the heaviest art footprint in this batch: 186  |
| Salvage Rubble | `moja.salvagerubble` | none | none | 0 | registry PHASE-OUT. Why: Salvage is the clan's identity and this mod gives rubble a salvage yield |
| Sensible Factions | `boots.sensiblefactions` | none | none | 0 | registry PHASE-OUT. Why: A world-generation faction placer: with no worldgen and a frozen savegame (brief 2, 4 test 5) it has no job af |
| Shavius's Medieval Flavour Pack | `shavius.medieval.flavour` | none | none | 0 | registry ELIMINATE. Why: Medieval identity is the textbook dissonant case (brief 4 test 3), and the campaign already carries its own fa |
| Smelt More Stuff | `hol.smeltpatch` | none | none | 0 | registry PHASE-OUT. Why: Smelting everything is a scavenger convenience, but the scavenge design lists Hol.SmeltPatch as a SOFT conflic |
| Standalone Hot Spring | `balistafreak.standalonehotspring` | none | none | 0 | registry PHASE-OUT. Why: The hot spring is one donor building with a donor-art texture set |
| Stylized Slave Collars and Headgears | `gerrymon.stylizedslavecollar` | none | none | 0 | registry PHASE-OUT. Why: Slavery is part of the clan doctrine (01_campaign.md; prior pass called collars on-theme), so collar styling f |
| Tabletop Decorations | `ucp.tabletopdecorations` | none | none | 0 | registry PHASE-OUT. Why: Trivial flavour (prior pass) |
| Torture Pod | `tsa.torturepod` | soft | patches 1f; FindMod 1f; About 1f | 0 | registry PHASE-OUT; delete our guarded rows/patches with it. Why: Prisoner-breaking fits a slaving scavenger clan but the pod art/behaviour is a generic donor mechanic; mandrak |
| Tradeable Trinkets (Continued) | `mlie.tradeabletrinkets` | none | none | 0 | registry PHASE-OUT. Why: Trinkets are a joy item and small trade good; loosely fits a barter setting, but it is donor content with dono |
| Transparent Substructure | `aelanna.transparentsubstructure` | none | none | 0 | registry PHASE-OUT. Why: Odyssey gravship substructure is central to the ship-centred game, so a see-through variant resonates, but thi |
| Trystan Traveller's Shuttle Schematics | `trouperton.trystantravellersshuttleschematics` | none | none | 0 | registry PHASE-OUT. Why: Shuttles compete with the gravship, the only scalable tree and the campaign centre (brief section 2; forbidden |
| Utility Columns | `nephlite.orbitaltradecolumn` | soft | patches 5f; FindMod 2f; About 2f | 0 | registry PHASE-OUT; delete our guarded rows/patches with it. Why: Columns that hold up roofs and light rooms are useful aboard, but our mods are wired to it: ResearchRetag reta |
| Vanilla Apparel Expanded | `vanillaexpanded.vappe` | soft | defs 33 names (0 unguarded in 0f); patches 3f; About 1f | 0 | registry PHASE-OUT; delete our guarded rows/patches with it. Why: Nothing of ours depends on it, but our mandrake.rut.researchretag rewrites 31 of its research edges (patched_b |
| Vanilla Apparel Expanded — Accessories | `vanillaexpanded.vaeaccessories` | order only | About 1f | 1: zal.moreutilitypacks | registry PHASE-OUT. Why: One third-party mod depends on it (zal.moreutilitypacks) and we ship an art fix that targets its textures (src |
| Vanilla Backstories Expanded | `vanillaexpanded.vanillabackstoriesexpanded` | none | none | 0 | registry PHASE-OUT. Why: Nothing depends on it and nothing of ours references it, but removing 174 backstories changes the generated-pa |
| Vanilla Furniture Expanded | `vanillaexpanded.vfecore` | soft | patches 3f; About 1f | 0 | registry PHASE-OUT; delete our guarded rows/patches with it. Why: No dependants and none of our source references it by packageId, but mandrake.rut.researchretag rewrites 43 of |
| Vanilla Furniture Expanded - Architect | `vanillaexpanded.vfearchitect` | none | none | 0 | registry PHASE-OUT. Why: Pure floor/fence variety |
| Vanilla Furniture Expanded - Art | `vanillaexpanded.vfeart` | soft | patches 3f; About 1f | 0 | registry PHASE-OUT; delete our guarded rows/patches with it. Why: Sculpture variety only |
| Vanilla Furniture Expanded - Farming | `vanillaexpanded.vfefarming` | soft | patches 4f; FindMod 1f; About 1f | 0 | registry PHASE-OUT; delete our guarded rows/patches with it. Why: The sprinkler is explicitly REJECTED in design (required_mods.md line 576: it boosts growth without water, whi |
| Vanilla Furniture Expanded - Medical Module | `vanillaexpanded.vfemedical` | none | none | 0 | registry PHASE-OUT. Why: Furniture-variety donor with donor art; nothing of ours depends on it and the brief says donor art is not kept |
| Vanilla Furniture Expanded - Power | `vanillaexpanded.vfepower` | soft | patches 3f; About 1f | 0 | registry PHASE-OUT; delete our guarded rows/patches with it. Why: Power tiers are a parallel ladder (brief section 2: anti-exponential; free fuel is out): advanced solar, wind  |
| Vanilla Furniture Expanded - Production | `vanillaexpanded.vfeproduction` | soft | patches 3f; About 1f | 0 | registry PHASE-OUT; delete our guarded rows/patches with it. Why: Workbench variants are a second production layer next to VFE-Factory, which the sole-industrial-tree rule (req |
| Vanilla Furniture Expanded - Props and Decor | `vanillaexpanded.vfepropsanddecor` | soft | patches 2f; FindMod 2f; About 1f | 2: gmmp.dungeon, mlie.functionalvanillaexpandedprops | registry PHASE-OUT; delete our guarded rows/patches with it. Why: It is the heaviest defs-by-count mod in the batch (3,638 of the universe's 55,988 def nodes, about 6.5%, INFER |
| Vanilla Furniture Expanded - Spacer Module | `vanillaexpanded.vfespacer` | soft | patches 3f; About 1f | 0 | registry PHASE-OUT; delete our guarded rows/patches with it. Why: Nothing depends on it |
| Vanilla Ideology Expanded - Hats and Rags | `vanillaexpanded.viehar` | none | none | 0 | registry PHASE-OUT. Why: Nothing depends on it, nothing of ours references it, and only oskarpotocki.vfe.tribals patches it (14 ops) |
| Vanilla Quests Expanded - The Generator | `vanillaquestsexpanded.generator` | soft | patches 1f; MayRequire 1f; About 1f | 0 | registry PHASE-OUT; delete our guarded rows/patches with it. Why: required_mods.md calls the VQE series OPTIONAL content, not load-bearing for progression |
| Vanilla Races Expanded - Fungoid | `vanillaracesexpanded.fungoid` | soft | patches 1f | 0 | registry ELIMINATE; delete our guarded rows/patches with it. Why: No reference in our src or design, no dependants, no patches from our mods (patched_by only third-party genese |
| Vanilla Races Expanded - Phytokin | `vanillaracesexpanded.phytokin` | soft | defs 1 names (0 unguarded in 0f); patches 3f; MayRequire 1f; FindMod 1f; About 3f | 0 | registry PHASE-OUT; delete our guarded rows/patches with it. Why: It is wired into the world: our BiomeCast_Ashkarr and RUT_Wastes reference it (the Polux bush row is MayReq |
| Vanilla Races Expanded - Starjack | `vanillaracesexpanded.starjack` | none | none | 0 | owner-ruled drop: C20 (VRE Starjack goes; registry still says KEEP) |
| Vanilla Weapons Expanded - Makeshift | `vanillaexpanded.vwems` | none | none | 1: smxrez.makeshiftreexamined | registry PHASE-OUT. Why: required_mods.md (updated 2026-08-15) says VWE-Makeshift was the scavenger-weapon answer on balance and 'lost  |
| VehicleRaid Framework | `gabrieel1482.raidvehicleframework` | none | none | 0 | registry PHASE-OUT. Why: The owner pre-committed (V2_DREAMS.md section 0b, 2026-08-12): "The point is to be able to have enemies use th |
| Walk the World | `addvans.walktheworld` | none | none | 0 | registry PHASE-OUT. Why: Conflicts with the intended travel model: the colony lives aboard the ship and the ship is the only way betwee |
| Wirehead Style | `tleno.wireheadstyle` | none | none | 0 | registry PHASE-OUT. Why: The look (exposed cables, piles of electronics, post-apocalyptic techie) is a very good match for Jawa junk-te |
| [BTD] Gravship Blueprints | `btd.remix.gravshipblueprints` | soft | patches 1f; FindMod 1f; About 1f | 1: btd.gbp.shippack.kotor.vge | registry PHASE-OUT; delete our guarded rows/patches with it. Why: The campaign's gravship is one fixed Rakatan ship delivered in the savegame; ship blueprints, extra downed gra |
| [NL] Facial Animation - Experimentals | `nals.facialanimationexperimentals` | soft | patches 1f | 0 | registry PHASE-OUT; delete our guarded rows/patches with it. Why: Animated faces are core to the look (owner rule: cosmetic changes can break animated faces, so ask first), and |
| Alien Worlds - Tidally Locked | `7f.alienworlds.tidallylocked` | soft | patches 1f; About 2f | 0 | registry PHASE-OUT; delete our guarded rows/patches with it. Why: Ash'karr is a tidally locked world, and our src/RimUtinni/UtinniPatches/Patches/JawaWorld_BiomeMix.xml patches |
| Custom Quest Framework-Level AI | `hailuan.customquestframeworkai` | none | none | 0 | registry PHASE-OUT. Why: required_mods.md lists it as the optional add-on to Custom Quest Framework (the quest-map backbone Ancient Urb |
| EGI Holograms and Projectors | `vesper.egihologramsandprojectors` | soft | patches 3f; About 1f | 0 | registry PHASE-OUT; delete our guarded rows/patches with it. Why: A high-tech display wall mod for "high-tech colonies" fits scavengers poorly (brief 4 test 3) and carries the  |
| Genetic Heads Framework for [NL] Facial Animatio | `sd.fa.geneticheadsframework` | none | none | 0 | registry PHASE-OUT. Why: It belongs to the Facial Animation stack that our UtinniPatches maintains (HeadSetForFA_Revive; batch 14 recor |
| Giant Toads (Continued) | `zal.gianttoads` | soft | patches 3f; FindMod 1f; About 2f | 0 | registry PHASE-OUT; delete our guarded rows/patches with it. Why: Recognisable Earth amphibian scaled up as a rideable fantasy-ish mount ('Absolutely not balanced for vanilla', |
| Invisible Display Case Continued | `icepickgma.invisibledisplaycase` | none | none | 0 | registry PHASE-OUT. Why: One cosmetic def that exists only because of a second framework: nightmare.core's only dependant in the univer |
| Makeshift: Re-Examined | `smxrez.makeshiftreexamined` | none | none | 0 | registry PHASE-OUT. Why: Makeshift weapons are junk-built scavenger gear (resonant), but this mod only rebalances VWE-Makeshift (vanill |
| Minerals Framework | `zacharyfoster.mineralsframework` | none | none | 3: zacharyfoster.mineralsfrozen, zacharyfoster.mineralsrock, zacharyfoster.mineralssparkle | registry PHASE-OUT. Why: Required by three universe packs (minerals rock, sparkle, frozen), whose own rows (batches 11 and 12) propose  |
| More Ritual Rewards | `sinnamon.moreritualrewards` | none | none | 0 | registry PHASE-OUT. Why: Rituals carry doctrine, so extra reward outcomes touch our own ritual design; four GameConditionDefs and a Wea |
| Posthuman Drift Titan Xenotype | `xylthixlm.races.titan` | soft | patches 1f | 0 | owner-ruled drop: C20; delete our guarded rows first |
| Quarry | `ogliss.thewhitecrayon.quarry` | none | none | 0 | registry PHASE-OUT. Why: Nothing depends on it and ours do not patch it (patched_by: only jellypowered.survivaltools, 2 ops) |
| RimAI Core (BETA) | `kilokio.rimai.core` | soft | patches 3f; About 1f | 0 | registry PHASE-OUT; delete our guarded rows/patches with it. Why: The owner adopted it 2026-08-07 as the "talking ship" (required_mods.md line 1127) |
| Vanilla Cooking Expanded - Stews | `vanillaexpanded.vcookestews` | soft | patches 2f; About 1f | 0 | registry PHASE-OUT; delete our guarded rows/patches with it. Why: It depends on vanillaexpanded.vcooke (KEEP) and nothing depends on it |
| Vanilla Mining Outpost Patch | `kuhlyus.modpatch.vanillaoutpost` | none | none | 0 | registry PHASE-OUT. Why: Only useful if Vanilla Outposts Expanded stays (list position 346; its verdict is in batch 7), and most of the |
| [42G]Glowing Bushes / Fork by [ETF] | `fourtoo.glowingbush` | none | none | 0 | registry PHASE-OUT. Why: A cosmetic highlight on foraged food plants |
| Comigo's Greater Swamps (Continued) | `zal.comigogreaterswamps` | soft | patches 4f; FindMod 2f; About 1f | 0 | registry PHASE-OUT; delete our guarded rows/patches with it. Why: Pure biome donor with no dependants |
| Functional Vanilla Expanded Props (Continued) | `mlie.functionalvanillaexpandedprops` | none | none | 0 | registry PHASE-OUT. Why: design/Jawa/worldbuilding/tile_augmentation_catalogue.md (row A5) relies on it to make a placed refinery or ta |
| Genetic Biotech for Facial Animation | `sd.fa.geneticheadsbiotech` | none | none | 0 | registry PHASE-OUT. Why: Companion to the Genetic Heads Framework (sd.fa.geneticheadsframework, list position 394) |
| Genetic Mods for Facial Animation | `sd.fa.geneticheadsmods` | none | none | 0 | registry PHASE-OUT. Why: The 1,057 MB figure is an upper bound: LoadFolders.xml (opened) loads each pack only if its host mod is active |
| Minerals Frozen | `zacharyfoster.mineralsfrozen` | none | none | 0 | registry PHASE-OUT. Why: A snow/ice mechanic for a world whose frozen biomes are a minority; the description labels it version 0.1 and  |
| Minerals Rock | `zacharyfoster.mineralsrock` | none | none | 0 | registry PHASE-OUT. Why: It rewrites the rock of every map and edits BiomeDefs, which overlaps the biome content we own in mandrake.rm. |
| Reel's Facial Animation Textures | `reel.facialanims` | none | none | 1: sd.fa.reelsadjustments | registry PHASE-OUT. Why: Stylistically a cartoon face source (its own description names Roblox faces), which sits poorly with the matte |
| Adjustments for Reel's Facial Animation Textures | `sd.fa.reelsadjustments` | none | none | 0 | registry PHASE-OUT. Why: Moves the placement of someone else's art (author says "I made none of the art"; will take it down if Reel ask |
| Deep Orbit | `broms.deeporbit` | none | none | 0 | registry PHASE-OUT. Why: Dissonant on two counts |
| Vanilla Textures Expanded - [NL] Facial Animatio | `vanillaexpanded.vtexe.facialanims` | none | none | 2: reel.facialanims, sd.fa.vteadjustments | registry PHASE-OUT. Why: Two mods depend on it (reel.facialanims, sd.fa.vteadjustments) and CLAUDE.md warns that cosmetic changes need  |
| VFE Pirates - Hardworking Warcaskets | `dmp.vfepirates.warcasketwork` | none | none | 0 | registry PHASE-OUT. Why: A leaf patch that exists only for oskarpotocki.vfe.pirates (list position 449), whose own verdict is in the fa |
| [GTG]Traders Accept All Junk Gear | `teiwaz.taajg` | none | none | 0 | registry PHASE-OUT. Why: Selling battlefield junk is a scavenger convenience, but our scavenge design lists Teiwaz.TAAJG as a SOFT conf |
| [GTG]Traders Accept Chunks & Corpses | `teiwaz.tacac` | none | none | 0 | registry PHASE-OUT. Why: Same family and author as TAAJG; chunks and corpses selling bypasses a disposal chore |
| Adjustments for Vanilla Textures Expanded - [NL] | `sd.fa.vteadjustments` | none | none | 0 | registry PHASE-OUT. Why: Placement tweak of someone else's art ("I made none of the art"); follows vanillaexpanded.vtexe.facialanims (l |
| Big and Small - Weapons | `redmattis.bigweapons` | soft | patches 1f | 0 | registry PHASE-OUT; delete our guarded rows/patches with it. Why: We already use it: mandrake.rsw.patches/WeaponTags_Renormalise.xml re-tags BS_GiantHammer, BS_GiantMedievalHam |
| LK Mineable Resources Outer Rim | `leutiankane.mineablesor` | soft | patches 3f; FindMod 2f | 0 | registry PHASE-OUT; delete our guarded rows/patches with it. Why: Owner ruling 2026-08-12 kept it ('something on the map to find and leave behind', per sw_ownership_survey) |
| LK Mines 2.0 Compatability[Outer Rim Core] | `leutiankane.mines2patchouterrim` | soft | FindMod 1f; About 1f | 0 | registry PHASE-OUT; delete our guarded rows/patches with it. Why: A glue patch between Outer Rim Core and Mines 2.0 |
| Outer Rim - Furniture & Decor | `neronix17.outerrim.furnitureanddecor` | none | none | 0 | registry PHASE-OUT C02. Why: Cosmetic furniture, nothing of ours depends on it (dependants_ours [], patched_by {}), and by brief s2/s4 test |
| Facial Animation Compatability Project | `danzinagri.facialanimationcompatabilityproject` | soft | FindMod 1f; About 3f | 0 | registry PHASE-OUT; delete our guarded rows/patches with it. Why: The author states the goal is an "anime aesthetic" for races like Ratkin, which fights the matte natural-histo |
| Sand Castles | `zylle.sandcastles` | none | none | 0 | registry PHASE-OUT. Why: A small joy activity that is mildly on-theme on a sand world, but it is donor content with donor art (22 textu |
| [BTD] Ship Pack: KotOR Ships VGE | `btd.gbp.shippack.kotor.vge` | none | none | 0 | registry ELIMINATE. Why: Fit is dissonant: the campaign is one fixed ship, the Utinni, 'getting it off the ground is the campaign'; rea |

## 6. D. Dev and authoring only: strip from the player list at release (21)

C04 (owner, 2026-10-10): *"Aim to remove it all."* No world, faction, map or pawn editing or scouting tool ships;
we keep them for authoring until shipping. Plus pure dev tooling.

| mod | packageId | our dependence | evidence (fresh census) | active 3rd-party mods that hard-depend on it | recommendation |
|---|---|---|---|---|---|
| Better Stacktraces | `aleksey.betterstacktraces` | none | none | 0 | **log aid**: keep for authoring/dev; strip from the player list at release |
| Cherry Picker | `owlchemist.cherrypicker` | none | none | 0 | **temporary bridge (owner 2026-10-10)**: keep for authoring/dev; strip from the player list at release |
| Better ModMismatch Window | `madeline.modmismatchformatter` | none | none | 0 | **load aid**: keep for authoring/dev; strip from the player list at release |
| Character Editor | `void.charactereditor` | none | none | 0 | **C04**: keep for authoring/dev; strip from the player list at release |
| Faction Customizer | `azravos.factioncustomizer` | none | none | 0 | **C04**: keep for authoring/dev; strip from the player list at release |
| Incident Disabler (Continued) | `mlie.incidentdisabler` | none | none | 0 | **evaluation AID (keep in every dev tier)**: keep for authoring/dev; strip from the player list at release |
| Log After Def Error (Continued) | `mlie.logafterdeferror` | none | none | 0 | **log aid**: keep for authoring/dev; strip from the player list at release |
| Map Designer | `zylle.mapdesigner` | none | none | 0 | **C06 (authoring-only)**: keep for authoring/dev; strip from the player list at release |
| Map Preview | `m00nl1ght.mappreview` | none | none | 0 | **C04**: keep for authoring/dev; strip from the player list at release |
| Modify Tiles at Game Start | `hali.modifylandingtile` | none | none | 0 | **C04**: keep for authoring/dev; strip from the player list at release |
| MutatorWorldIcons | `snobi.mutatorworldicons` | none | none | 0 | **C04**: keep for authoring/dev; strip from the player list at release |
| Persistent Precepts | `alleykat.persistentprecepts` | none | none | 0 | **C04**: keep for authoring/dev; strip from the player list at release |
| Prepare Landing (Continued) | `m00nl1ght.unofficialupdates.preparelanding` | none | none | 0 | **C04**: keep for authoring/dev; strip from the player list at release |
| RimBridgeServer | `brrainz.rimbridgeserver` | HARD | csproj 1 | 0 | **bridge (98 .cs files `using RimBridgeServer.Sdk`)**: keep for authoring/dev; strip from the player list at release |
| Scenario Amender [1.6 Fixed] | `plusblankplus.scenarioamenderfork` | none | none | 0 | **C04**: keep for authoring/dev; strip from the player list at release |
| What's That Mod | `co.uk.epicguru.whatsthatmod` | none | none | 0 | **dev aid**: keep for authoring/dev; strip from the player list at release |
| Worldbuilder | `ferny.worldbuilder` | none | none | 0 | **C04**: keep for authoring/dev; strip from the player list at release |
| WorldEdit 2.0 | `funkyshit.mods.worldedit.alpha` | none | none | 0 | **C04**: keep for authoring/dev; strip from the player list at release |
| Character Editor Retextured | `neronix17.retexture.charactereditor` | none | none | 0 | **C04**: keep for authoring/dev; strip from the player list at release |
| Rimsential - Total Control: Continued | `co.uk.epicguru.factionloadout` | none | none | 0 | **dev pawnkind tool**: keep for authoring/dev; strip from the player list at release |
| Rim Control | `lordfelix.rimcontrol` | none | none | 0 | **owner-adopted tuning tool**: keep for authoring/dev; strip from the player list at release |

## 7. E. Evaluation-hostile mods: exclude during dev, decide for ship separately

"Evaluation" = a live proof, a review sheet or screenshot, a balance measurement: anything that must give the
same answer twice. Each of these makes a run differ from the last for a reason that is not our mod. My judgment
of the cost: **HIGH** = it changes what a probe can SEE or the outcome of the thing under test; **MED** = it injects
events or state into a test map; **LOW** = cosmetic or narrow.

| mod | packageId | registry | cost | what it does to evaluation | recommendation |
|---|---|---|---|---|---|
| (NWN) Real Fog of War (Continued) | `mlie.nwnrealfogofwar` | KEEP | HIGH | hides things and terrain outside pawn sight on non-home maps (onlyOutsideColony=True live): pocket maps, the sea layer, quicktest sites that are not home; `unfogAll` wedged the game 4 min and the fog came back | exclude in dev tiers TOGETHER with CAI (CAI is what strips fog on player maps); re-add for ship (Route B ruling); DivingInteraction's compat patch is Prepare()-guarded |
| [1.6] CAI 5000 - Advanced AI + Fog Of War (c | `krkr.rule56` | KEEP | HIGH | rewrites enemy combat AI (cover, retreat, flanking): raid and fight outcomes vary run to run; also strips other mods' fog on player maps (FogOfWar_DisableOnPlayerMap=True) | exclude in dev tiers with Real FoW; ship decision stays Route B |
| Yayo's Combat 3 (Continued) | `mlie.yayoscombat3` | KEEP | HIGH | replaces shot resolution and injury code; random melee cooldown every swing; breaks other mods' hooks (mod_deepdive_yayo_full.md) | deep dive recommends remove + port ideas; until ruled, exclude from dev tiers |
| Stronger Quality Scaling (1.6) | `kas.strongerscaling` | KEEP-TEMPORA | MED | rescales quality on every armour/weapon stat: a quality roll swings numbers we are tuning | rule with Yayo (deep dive §10); exclude from tuning tiers |
| Vanilla Events Expanded | `vanillaexpanded.vee` | KEEP | MED | adds random events (psychic rain/bloom, droughts...) | exclude in dev; v1 keep is registry KEEP: re-judge under C09 'only what makes danger different' |
| Better Infestations (Continued) | `zal.betterinfestations` | KEEP-TEMPORA | MED | infestation events (2 already silenced by C09) | exclude in dev |
| Infestations Spawn in Darkness 1.6 | `koth.isid` | KEEP | LOW | moves infestations to darkness: changes where events land | exclude in dev |
| Space Worms (Continued) | `mlie.spaceworms` | KEEP | MED | random worm incident | exclude in dev |
| Gravship Raids | `sk.gravshipraids` | KEEP | MED | gravship raids arrive unbidden | exclude in dev |
| Gravship Crashes | `arcjc007.gravshipcrashes` | KEEP | LOW | random crash sites | exclude in dev |
| Better Ambushes Continued | `ionfrigate12345.coolandgoodambush` | KEEP | MED | ambush incidents | exclude in dev |
| Meaningful Encounters | `sirdarkelf.meaningfulencounters` | KEEP | MED | encounter incidents | exclude in dev |
| Wandering Caravans | `ogliss.g223.wanderingcaravans` | KEEP | MED | visitors walk onto test maps | exclude in dev (memory: visitors are recorded and removed) |
| [SR]Factional War (fork) | `sr.modrimworld.factionalwarcontinued` | KEEP | MED | factions fight each other off-screen: world state drifts | exclude in dev |
| Rimsential - Spaceports (Continued) | `zal.spaceports` | KEEP | LOW | shuttles arrive (`ShuttleIncoming`) | exclude in dev |
| I will be back | `hailuan.iwbb` | KEEP-TEMPORA | MED | random 'former colonist returns' incident, baseChance 250 | exclude in dev; registry PHASE-OUT |
| Ancient Dangers on Campsites and Encounter m | `vita.campdangers` | KEEP-TEMPORA | LOW | extra hazard sites on campsites | exclude in dev; registry PHASE-OUT |
| Yayo's Meteor (Continued) | `mlie.yayosmeteor` | KEEP | LOW | meteor incidents | exclude in dev |
| Tribute Demand | `geojak.tributedemand` | KEEP | LOW | tribute-demand incidents | exclude in dev |
| More Faction Interaction (Continued) | `mlie.morefactioninteraction` | KEEP-TEMPORA | MED | faction events (C09 study pending) | exclude in dev |
| RimQuest (Continued) | `mlie.rimquest` | KEEP | LOW | more quests offered | exclude in dev |
| Dubs Break Mod | `dubwise.dubsbreakmod` | KEEP | LOW | random breakdowns | exclude in dev |
| Mood Chain Reaction | `acutus.moodchainreaction` | KEEP | LOW | mood cascades make pawn state path-dependent | exclude from pawn/mood tests only |
| Slave Rebellions Improved (Continued) | `mlie.slaverebellionsimproved` | KEEP | LOW | rebellion incidents | exclude in dev |
| Stealing Mod | `amoruch.rimworldstealingmod` | KEEP | LOW | pawns steal: inventories change | exclude in dev |
| RimAI Core (BETA) | `kilokio.rimai.core` | KEEP-TEMPORA | MED | LLM-generated text: nondeterministic by construction | exclude in dev; C23 Oracle study owns the ship decision |
| RimAI Framework | `kilokio.rimai.framework` | KEEP-TEMPORA | MED | framework of the above | drop with RimAI Core in dev |
| Realistic Darkness (Light) | `wemd.realisticdarknesslight` | KEEP | MED | darker nights: screenshots and visual review read badly | exclude from art/visual-review tiers |
| Performance Optimizer | `taranchuk.performanceoptimizer` | KEEP | MED | changes caching/tick behaviour (a FasterGetComp-OFF config backup exists in deployed/config/) | exclude when a bug smells of stale state; keep for perf measurement |
| Melee Animation | `co.uk.epicguru.meleeanimation` | KEEP | LOW | melee animations alter timing; lasso spawn roll still live (LASSO_CHERRYPICKER_REMOVAL_1 A2 open) | exclude from combat-balance tiers |
| Interaction Bubbles | `jaxe.bubbles` | KEEP | LOW | speech bubbles clutter screenshots | exclude from screenshot/review tiers |
| [NL] Facial Animation - WIP | `nals.facialanimation` | KEEP | LOW | blinking/expressions: two captures of one pawn differ | keep (C16 keep); freeze or exclude only for pixel-diff tests |

Notes:
- 🔴 **Fog of war is a pair.** Owner ruled Route B (CAI 5000's combat AI + NWN Real Fog of War with CAI's own fog
  off; `design/Jawa/OPUS5_HANDOFF.md`). Live settings: CAI `FogOfWar_Enabled=False`,
  `FogOfWar_DisableOnPlayerMap=True` (CAI strips fog on player maps); Real FoW `onlyOutsideColony=True` (fog only
  on non-home maps). **Dropping CAI alone brings the fog back onto player maps**: exclude both or neither. Our
  code depends on Real FoW only softly (`DivingInteraction/Patch_RealFoWStaleHearing.cs`, `Prepare()` returns
  false without it); the Depths design rides NWN fog for its sight cap (design dependency, not code).
- Already removed by Wave 1 and so not listed: Large Faction Bases, Storyteller Enhanced, Rimesis, Raid Protection
  Fee (all event layers, C09).
- **Incident Disabler (`mlie.incidentdisabler`) is the opposite**: an evaluation aid. Keep it in every dev tier.
- Recommended mechanism: one `modset_builder.py` tier, *live list minus class E* (plus, at release, minus class D),
  instead of per-run settings toggles. Not built here.
- v2 candidates: Real FoW + CAI as the ruled ship feature; Yayo only if the owner keeps it after the deep dive;
  RimAI behind the C23 Oracle study; the event mods only through C09 ("only what makes danger different").

## 8. F1. Keep: frameworks our content hard-depends on (24)

| mod | packageId | our dependence | evidence (fresh census) | active 3rd-party mods that hard-depend on it | recommendation |
|---|---|---|---|---|---|
| Harmony | `brrainz.harmony` | HARD | About 50f; modDependency of rm.aftermath, rm.biomes, rm.explosiveknockback, rm.flowworks, rm.gimmesomeslack, rm.gravshiplanding, rm.hugethings, rm.inhabited, rm.kineticarms, rm.loadtracer, rm.luminouspigment, rm.ninefold, rm.planetpresetprime, rm.visibility, rsw.armoury, rsw.droidworks, rsw.gizkastowaway, rsw.jawarules, rsw.swbestiary, rut.empirepursuit | 257: 7f.alienworlds, 7f.alienworlds.tidallylocked, adaptive.primitivestorage… | keep: our content hard-depends on it |
| Adaptive Storage Framework | `adaptive.storage.framework` | HARD | About 1f; modDependency of rsw.armoury; ParentName AdaptiveStorageBase; class_ref 5 (10-10) | 5: adaptive.ideology.storage, adaptive.primitivestorage, adaptive.simplestorage… | keep: our content hard-depends on it |
| Big and Small - Framework | `redmattis.betterprerequisites` | HARD | defs 3 names (9 unguarded in 2f); patches 2f; MayRequire 7f; FindMod 1f; About 4f; modDependency of rsw.starwarsraces; class_ref 169 (10-10) | 2: redmattis.bigsmall.core, redmattis.optional | keep: our content hard-depends on it |
| Vehicle Framework | `smashphil.vehicleframework` | HARD | defs 1 names (1 unguarded in 1f); MayRequire 1f; About 2f; csproj 2; class_ref 3 (10-10) | 3: gabrieel1482.raidvehicleframework, oskarpotocki.vanillavehiclesexpanded, sarg.alphavehiclesneolithic | keep: our content hard-depends on it |
| XML Extensions | `imranfish.xmlextensions` | HARD | class_ref 14 (10-10) | 1: gravenwitch.vsrexamined | keep: our content hard-depends on it |
| Vanilla Expanded Framework | `oskarpotocki.vanillafactionsexpanded.core` | HARD | defs 6 names (15 unguarded in 6f); patches 2f; MayRequire 29f; About 4f; modDependency of rsw.armoury, rsw.starwarsraces, rut.injections; class_ref 193 (10-10) | 65: det.brawnum, det.epochsincense, det.keshig… | keep: our content hard-depends on it |
| EBSG Framework | `ebsg.framework` | HARD | defs 2 names (6 unguarded in 5f); patches 1f; MayRequire 4f; FindMod 1f; About 2f; modDependency of rsw.armoury; class_ref 110 (10-10) | 4: det.brawnum, det.buzzers, elsov.beliar… | keep: our content hard-depends on it |
| Doors Expanded | `jecrell.doorsexpanded` | HARD | patches 3f; About 2f; class_ref 14 (10-10) | 0 | keep: our content hard-depends on it |
| Dubs Bad Hygiene Lite | `dubwise.dubsbadhygiene.lite` | HARD | patches 3f; MayRequire 2f; FindMod 2f; About 6f; class_ref 41 (10-10) | 1: dubwise.dubsbadhygiene.thirst | keep: our content hard-depends on it |
| Integrated Genes | `turnovus.biotech.integratedgenes` | HARD | defs 25 names (71 unguarded in 2f); patches 3f; FindMod 2f; About 2f; modDependency of rsw.starwarsraces | 0 | keep: our content hard-depends on it |
| JecsTools Unofficial 1.6 BETA | `jecrell.jecstools` | HARD | About 1f; class_ref 76 (10-10) | 0 | keep: our content hard-depends on it |
| Jewelry | `kikohi.jewelry` | HARD | defs 1 names (1 unguarded in 1f); patches 3f; About 1f | 0 | keep: our content hard-depends on it |
| Research Reinvented | `petetimessix.researchreinvented` | HARD | defs 1 names (0 unguarded in 0f); MayRequire 1f; About 2f; ParentName SpecialResearchOpportunityBase | 0 | keep: our content hard-depends on it |
| SpeakUp | `jpt.speakup` | HARD | patches 8f; About 1f; modDependency of rsw.jawavoice | 0 | keep: our content hard-depends on it |
| Vanilla Furniture Expanded - Factory | `vanillaexpanded.vfefactory` | HARD | defs 13 names (36 unguarded in 1f); patches 7f; FindMod 3f; About 2f; modDependency of rm.wreckedmachines | 1: groovytaco.beltextractors | keep: our content hard-depends on it |
| Vanilla Gravship Expanded - Chapter 1 | `vanillaexpanded.gravship` | HARD | patches 7f; FindMod 3f; About 4f; class_ref 82 (10-10) | 0 | keep: our content hard-depends on it |
| [LFS] Genes Expanded - Eyes | `lazyfridaystudio.genesexpandedeyes` | HARD | defs 6 names (6 unguarded in 1f); patches 4f; FindMod 1f; About 3f; modDependency of rsw.starwarsraces | 0 | keep: our content hard-depends on it |
| Humanoid Alien Races | `erdelf.humanoidalienraces` | HARD | patches 1f; FindMod 1f; About 2f; modDependency of rsw.droidworks | 0 | keep: our content hard-depends on it |
| Tabula Rasa | `neronix17.toolbox` | HARD | patches 1f; MayRequire 2f; FindMod 1f; About 2f; class_ref 79 (10-10) | 4: neronix17.outerrim.core, neronix17.outerrim.furnitureanddecor, neronix17.outland.genetics… | keep: our content hard-depends on it |
| Big and Small - Genes & More | `redmattis.bigsmall.core` | HARD | defs 6 names (15 unguarded in 6f); patches 6f; MayRequire 3f; FindMod 2f; About 5f; modDependency of rsw.starwarsraces | 3: redmattis.bigsmall, redmattis.bigweapons, redmattis.optional | keep: our content hard-depends on it |
| Outland - Genetics | `neronix17.outland.genetics` | HARD | defs 104 names (334 unguarded in 2f); patches 3f; About 3f; modDependency of rsw.starwarsraces | 0 | keep: our content hard-depends on it |
| Intimacy - Gender Works | `lovelydovey.sex.withrosaline` | HARD | defs 2 names (2 unguarded in 1f); patches 1f; MayRequire 1f; About 1f | 0 | keep: our content hard-depends on it (C20: founder genes, save-critical until ported) |
| Star Wars : The Force - Lightsaber | `lee.theforce.lightsaber` | HARD | defs 20 names (4 unguarded in 4f); patches 4f; MayRequire 8f; FindMod 7f; About 3f; class_ref 148 (10-10) | 0 | keep: our content hard-depends on it |
| RimThemes | `arandomkiwi.rimthemes` | HARD | About 1f; modDependency of rut.menushell | 0 | keep: our content hard-depends on it |

## 9. Hard dependence: exactly what must be replicated before each retirement

Only mods in B, C1 or C2 matter here; F1 frameworks stay. From the guard walk (unguarded names and their files):

| mod | what of ours breaks if it leaves | what must be replicated |
|---|---|---|
| Outer Rim - Core `neronix17.outerrim.core` | `modDependencies` of `rsw.armoury` and `rsw.ionweapons` (load refuses without it); unguarded: `OuterRim_Beskar`, `OuterRim_PureBeskar`, `OuterRim_ComponentHypertech` (Armoury `RSW_MineShaftCanonPolicy.xml`, UtinniPatches `JawaFactionRoster.xml`), `OuterRim_Blaster` (Armoury `Absorbed_Eweb.xml`), `OuterRim_Shot_DLT19DBlasterBolt` (JawaIonWeapons), `OuterRim_BinaryStarRaiders` faction (Droidworks data spikes, StarWarsPatches Gamorrean pawnkinds), `OuterRim_CompositeHelmet`/`CyclerRifle`/`VibroBlade` (Inhabited cast rosters) | beskar + pure beskar materials, the hypertech component, 3 weapons + a projectile, 1 helmet, 1 faction; then drop the two About entries. 4 active third-party mods hard-depend on it (Galactic Empire, Rebel Alliance, the two LK patches): they go with it |
| Outer Rim - Galactic Empire `neronix17.outerrim.galacticempire` | Inhabited cast rosters: `OuterRim_DLT19HeavyBlasterRifle`, `OuterRim_DLT19XTargetingBlaster`, `OuterRim_StormtrooperHelmet` (4 unguarded, 2 files) | 2 rifles, 1 helmet (the Empire itself is reskinned vanilla, per memory) |
| Outer Rim - Rebel Alliance `neronix17.outerrim.rebelalliance` | Inhabited roster: `OuterRim_A280Blaster` | 1 rifle |
| Alpha Vehicles - Neolithic `sarg.alphavehiclesneolithic` | `modDependencies` of our `rsw.desertvehiclereskin` (a reskin of its carts) | nothing to port: retire our reskin with it, or rebuild the carts on Vehicle Framework (kept) |
| Advanced Biomes `mlie.advancedbiomes` | RM_Wastes (shipping): `VolcanoSoil`, `WastelandAsphalt` terrain; `Wasteland` named by `RM_WastesWreckField.xml` and a TileMutatorDef; frozen RUT_ twins (die at the paint): `Poison*` terrain/plants; 106 class refs in `rut.patches` (10-10) | 2 terrains for the shipping Wasteland; the rest dies with the twins |
| Alpha Memes `sarg.alphamemes` | `GU_RedWood` unguarded in `RM_Contagion_DonorPorts.xml`; guarded: `TuskAttackTool` (Abyss Ossumatha, SWBestiary bodies), 3 `AM_Dryad_*` in Cauldron, `AM_Gladiator`/`AM_Structure_Scavenger`/`AM_WaterPrimacy` in our faction defs | 1 wood, 1 tool capacity, the 3 dryads (or cut), 3 memes/structures for 4 factions. The 2026-10-18 pass kept it STAY; C01 says port |
| VFE Tribals `oskarpotocki.vfe.tribals` | `RUT_Ported_ResearchTrio.xml` names `VFET_Bow`, `VFET_Fire`, `VFET_Furniture`, `VFET_Tribalwear` as prerequisites, unguarded | 4 research nodes (or re-point the prereqs at ours) |
| VFE Security, Landmarks, VRE Genie, VRE Saurid, Det's Keshig | 1 to 11 unguarded names each (`VFES_Turret_ChargeRailgun`/`TeslaBlaster`; `VEE_Plant_DatePalm`; `VRE_Curiosity_Social`; `Saurid` x11 in one file; `DV_MeleeWeapon_SerratedScimitar`) | guard or re-point each name; tiny |
| Epochs - Pyrinth `det.epochspyrinth` | 29 unguarded `DV_*` names (Pyrinth, LanternDeeps) | **already replicated**: `mandrake.rm.pyrinth` defines every `DV_*` name; put it on the live list in the same change |
| Bones `sihv.rombonesport` | guarded only (`BoneAmount` stat in SWBestiary, GreentideRaidAnt) | owner: lean port (bone as material) first |
| RimTek Core/DocMate/DigiPal | none | owner C21: build the medical-droid capability and the bounty-hunter item first |

Not dependence of ours, but load-order coupling to remember: Vanilla Skills Expanded is depended on by VSR Examined
and Alpha Skills (all three are in Wave 1); Outer Rim Core by 4 mods (above); RimTek Core by DocMate and DigiPal.

## 10. F2. Keep: content and QoL (232)

Registry KEEP (or PHASE-OUT with an owner keep, such as the C16 face mods), no hard dependence of ours. One entry
per mod: packageId (name; our dependence; evidence when any).

- `zetrith.prepatcher` (Prepatcher; none)
- `krkr.rule56` ([1.6] CAI 5000 - Advanced AI + Fog; soft; patches 3f; About 1f)
- `mlie.nwnrealfogofwar` ((NWN) Real Fog of War (Continued); soft; patches 2f; About 1f)
- `aoba.framework` (Fortified Features Framework; none)
- `thesepeople.ritualattachableoutcomes` (Custom Ritual Framework; none)
- `unlimitedhugs.hugslib` (HugsLib; none)
- `04.23.2020` ([1.1]TO[1.6]MultipleTraders; none)
- `ap.huntingmeme` ([AP] Hunting Meme; none)
- `dizzy.candlesandmeditation` ([Dizzy] Candles and Hidden Meditat; none)
- `jm.disstynan` ([JM]Disable Pseudo Translate 禁用泰南语; none)
- `zal.calltradeships` ([KV] Call Trade Ships (Continued); none)
- `lc.tammybee.selectablesculpturegraphic` ([LC] Selectable Sculpture Graphic; none)
- `mingtuwuxiang.spacebasedecorative` ([MUS]太空基地家具Space Base Furniture; soft; patches 2f; About 1f)
- `nals.facialanimation` ([NL] Facial Animation - WIP; order only; About 3f)
- `mlie.rfrumorhasit` ([RF] Rumor Has It.... (Continued); soft; patches 1f; About 1f)
- `rh2.cpers.arrest.here` ([RH2] CPERS: Arrest Here!; none)
- `cp.uncle.boris.used.furniture` ([RH2] Uncle Boris' - Used Furnitur; none)
- `sbz.neatstoragefridge` ([sbz] Fridge; none)
- `sbz.gravshipstorage` ([sbz] Gravship Storage; none)
- `sr.modrimworld.factionalwarcontinued` ([SR]Factional War (fork); none)
- `ali.growodysseyplants` (Ali's Grow All Odyssey Plants; none)
- `andrewraphaellukasik.allowdeadanimals` (Allow Dead Animals; none)
- `unlimitedhugs.allowtool` (Allow Tool; none)
- `duz.almosttherefork` (Almost There! Fork; none)
- `xmb.ancientminingindustry.mo` (Ancient mining industry; soft; patches 4f; FindMod 1f; About 2f)
- `automatic.autolinks` (Auto links; none)
- `fuu.autostriponhaul` (Auto Strip on Haul; none)
- `io.github.relvl.rimworld.bestapparel` (BestApparel; none)
- `ionfrigate12345.coolandgoodambush` (Better Ambushes Continued; none)
- `mlie.betterbeggars` (Better Beggars (Continued); none)
- `nephlite.advexplosions` (Better Explosions; none)
- `arkymn.bettergrowthmoments` (Better Growth Moments; none)
- `mlie.betterprojectileorigin` (Better Projectile Origin; none)
- `jm.bettertraders` (Better Traders; soft; patches 4f)
- `falconne.bwm` (Better Workbench Management; none)
- `redmattis.biggergravship` (Bigger Gravships (and other Odysse; none)
- `biomesteam.biomesfossils` (Biomes! Fossils; soft; patches 3f; FindMod 1f; About 2f)
- `bs.mbifvte` (Bradson's Main Button Icons (Forke; none)
- `gulmadred.breedingritual` (Breeding Ritual; soft; patches 1f; FindMod 1f; About 1f)
- `memegoddess.buildfrominventory` (Build From Inventory - Continued; none)
- `8z.callforintel` (Call For Intel; none)
- `brrainz.cameraplus` (Camera+; none)
- `iforgotmysocks.caravanadventures` (Caravan Adventures; soft; patches 4f; FindMod 1f; About 2f)
- `kapitanoczywisty.changemapedge` (Change map edge limit; none)
- `kearril.choosewheretoland` (Choose Where To Land; none)
- `kikohi.coloreddeepresources` (Colored deep resources; none)
- `petetimessix.compacthediffs` (Compact Hediffs; none)
- `com.makeitso.configurabletechprints` (Configurable Techprints; soft; FindMod 1f)
- `cozyfire.velcroboy333` (Cozy Fires; none)
- `heatherathebyne.craftingspotslavegear` (Crafting Spot Slave Gear; none)
- `greg.customgastypes` (Custom Gas Types; soft; patches 4f; FindMod 1f; About 2f)
- `costel.customroomnames` (Custom Room Names; none)
- `darkestdungeon.incidentsounds` (Darkest Dungeon Incident Sounds; none)
- `troopersmith1.deathrattle` (Death Rattle Continued [1.2+]; none)
- `mlie.decorativecliffs` (Decorative Cliffs (Continued); none)
- `gondragon.defensivepositions` (Defensive Positions - Forked; none)
- `merthsoft.designatorshapes` (Designator Shapes; none)
- `garwel.destroyitem` (Destroy Item; none)
- `cometopapa.deteriorated` (Deteriorable Filter; none)
- `lornath.diseaseimmunityprogresstracker` (Disease Immunity Progress Tracker; none)
- `dubwise.dubspaintshop` (Dub's Paint Shop; none)
- `dubwise.dubsbadhygiene.thirst` (Dubs Bad Hygiene - Thirst; order only; About 1f)
- `dubwise.dubsmintmenus` (Dubs Mint Menus; none)
- `dubwise.dubsmintminimap` (Dubs Mint Minimap; none)
- `dubwise.dubsrimkit` (Dubs Rimkit; none)
- `blues.forge` (Dynamic Effects Forge; none)
- `yourname.effigys.mod` (Effigys - Terror Spikes; none)
- `carnysenpai.enableoversizedweapons` (Enable Oversized Weapons; none)
- `keshash.extraexplosioneffects` (Extra Explosion Effects; none)
- `kosaro.fahrenheitandcelsius` (Fahrenheit and Celsius; none)
- `realify.firefoam` (Firefoam poppers aren't ugly!; none)
- `kathanon.floatsubmenu` (Float Sub-Menus; none)
- `temeez.floorlights2` (Floor Lights 2; none)
- `aoba.fortress.neolithic` (Fortifications - Neolithic; none)
- `memegoddess.giddyup` (Giddy-Up 2 - Continued; none)
- `lts.geg` (Glowing eyes genes; none)
- `albion.goexplore` (Go Explore!; none)
- `arcjc007.gravshipcrashes` (Gravship Crashes; soft; defs 1 names (0 unguarded in 0f); patches 1f; MayRequire 2f; About 1f)
- `arcjc007.gravshipexporter` (Gravship Exporter; none)
- `sk.gravshipraids` (Gravship Raids; none)
- `imagitama.rimworldgravshiprangeonmap` (Gravship Range On Map; none)
- `ael.tua.helmetsaddtoxresistance` (High Tech Helmets Give Tox Gas Res; none)
- `hazn.huntingtraps` (Hunting Traps; soft; patches 2f; About 1f)
- `amegakull.scvrole` (Ideology Scavenger Role; none)
- `llunak.moreprecepts` (Ideology: More Precepts; none)
- `agentblac.makepawnsprisoners` (Imprisonment On The Go! (Continued; none)
- `koth.isid` (Infestations Spawn in Darkness 1.6; none)
- `haecriver.injuredcarry` (Injured Carry; none)
- `ferny.easycaravanformation` (Instant Caravan; none)
- `jaxe.bubbles` (Interaction Bubbles; none)
- `mlie.interactionareasettings` (Interaction-Area Settings; none)
- `nep.landonanything` (Land On Anything; none)
- `timuttie.justleavealready.fork.mitasamodel` (Just Leave Already; none)
- `mlie.justputitoverthere` (Just Put It Over There; none)
- `linnun.keepconverting` (Keep Converting; none)
- `vaguelysexual.modpackageid.goeshere` (Knick Knacks - Let your colonists ; none)
- `costel.layeredapparel` (Layered Apparel; none)
- `noneobsidiaexpansion.ledlightsstrip` (LED Lights Strip; none)
- `mlie.linkablesettings` (Linkable Settings; none)
- `nozome.mapmodeframework` (Map Mode Framework; none)
- `udon.masslovein` (Mass Lovin'; none)
- `sirdarkelf.meaningfulencounters` (Meaningful Encounters; none)
- `mlie.mercerbackpacks` (Mercer's Backpacks (Continued); none)
- `andromeda.milkyway` (Milky Way; none)
- `rabiosus.minesight` (Mine Sight; none)
- `cain.mineshaft` (Mines 2.0; soft; patches 3f; About 1f)
- `deadmano.moodalerts` (Mood Alerts; none)
- `acutus.moodchainreaction` (Mood Chain Reaction; none)
- `garryflowers.moreslaverystuff` (More Slavery Stuff; soft; patches 1f; FindMod 1f; About 1f)
- `zylle.nightlights` (Night Lights; none)
- `dingo.noforcedslowdown` (No Forced Slowdown; none)
- `mlie.nomissinggeneicons` (No Missing Gene Icons; none)
- `edern.norandomapparelonideoedit` (No Random Apparel on Ideology Edit; none)
- `jaeger972.nomadfreindlyquests` (Nomad Friendly Quests; none)
- `avilmask.nonunopinata` (Non uno Pinata (don't drop items); none)
- `planetace.nondestructivegravlaunch` (Non-Destructive Gravlaunch; none)
- `mehni.numbers` (Numbers; none)
- `coolzie.oocreboost` (Out of Combat ReBoost; none)
- `mlie.perspectivebuildings` (Perspective: Buildings (Continued); none)
- `mlie.preceptsandmemes` (Precepts and Memes (Continued); soft; patches 1f; MayRequire 1f; FindMod 1f; About 2f)
- `mlie.prisonersshouldfearturrets` (Prisoners Should Fear Turrets; none)
- `dawnsglow.qualcolor` (Quality Colors (Continued); none)
- `ingendum.raiderswarmcompression` (Raider Swarm Compression; none)
- `zal.randomgrowthchoices` (RandomGrowthChoices (Continued); none)
- `wemd.realisticdarknesslight` (Realistic Darkness (Light); none)
- `mlie.realistichumansounds` (Realistic Human Sounds (Continued); none)
- `mlie.relevantstatsindescription` (Relevant Stats In Description; none)
- `scorpio.resourcedictionary` (Resource Dictionary; none)
- `alma.tossem` (Right Click to Toss Carried Pawn; none)
- `dubwise.rimefeller` (Rimefeller; soft; patches 4f; FindMod 1f; About 2f)
- `rimfridge.kv.rw` (RimFridge: Now with Shelves!; none)
- `mlie.rimquest` (RimQuest (Continued); none)
- `sierra.rt.generaltraits` (RimTraits - General Traits; none)
- `depscian.rimtunes` (RimTunes; none)
- `mianreplicate.romanceandintimacyontherim` (Romance & Intimacy On The Rim; none)
- `kupie.isjustdoingitlive.plzdonthateme.roofedscanning` (Roofed Scanning 1.6; none)
- `memegoddess.runandgun` (RunAndGun - Continued; none)
- `hellrevenger.searchoption` (Search Option; none)
- `avilmask.selfdyeing` (Self Dyeing; none)
- `sensiblebedownership.1trickpwnyta` (Sensible Bed Ownership; none)
- `flyingsloth.scfilthreducer` (Sentience Catalyst Filth Rate Redu; none)
- `spacemoth.showknowntechprints` (Show Known Techprints; none)
- `dark.signs` (Signs and Comments; soft; patches 1f; FindMod 1f; About 3f)
- `usgiyi.slaveoutfits` (Slave Outfits [1.6]; none)
- `mlie.slaverebellionsimproved` (Slave Rebellions Improved (Continu; none)
- `astryl.sleepingbuddies` (Sleeping Buddies; none)
- `weilbyte.snapout` (Snap Out!; soft; patches 1f; FindMod 1f; About 1f)
- `krelinos.socialexpfromtrade` (Social Experience from Trade; none)
- `mlie.spaceworms` (Space Worms (Continued); soft; patches 4f; About 2f)
- `elshender.stackablechunks` (Stackable Chunks; none)
- `amoruch.rimworldstealingmod` (Stealing Mod; soft; patches 1f; FindMod 1f; About 1f)
- `karshou.storagememory` (Storage Memory; none)
- `moistestwhale.stuffontablesforked` (Stuff on Tables Forked; none)
- `mlie.tabsorting` (Tab-sorting; none)
- `summersausages2ttv.techlevelenforcement` (Tech Level Enforcement; none)
- `propickelz.tinkerbench` (Tinkering Bench and Biohacking Sta; soft; patches 3f; About 1f)
- `smashphil.dropspot` (Trade Ships Drop Spot; none)
- `automatic.traderships` (Trader ships; none)
- `kearril.tradingoptionscontinue` (Trading Options Continue; none)
- `xercaine.tribal.furniture` (Tribal Furniture; none)
- `geojak.tributedemand` (Tribute Demand; none)
- `ferny.triumphantresearch` (Triumphant Research; none)
- `error277.tunneler.expanded` (Tunneler Expanded; soft; patches 3f; About 1f)
- `marvinkosh.ughyougotme` (Ugh You Got Me; none)
- `madarauchiha.undraftaftertucking` (Undraft After Tucking; none)
- `universalpregnancy.1trickpwnyta` (Universal Pregnancy; none)
- `vanillaexpanded.vbrewe` (Vanilla Brewing Expanded; soft; defs 9 names (0 unguarded in 0f); patches 4f; FindMod 1f; About 2f)
- `vanillaexpanded.vcooke` (Vanilla Cooking Expanded; soft; patches 4f; FindMod 1f; About 2f)
- `vanillaexpanded.vee` (Vanilla Events Expanded; soft; patches 1f; FindMod 1f; About 1f)
- `vanillaexpanded.helixiengas` (Vanilla Helixien Gas Expanded; soft; patches 3f; FindMod 1f; About 1f)
- `vanillaexpanded.ideo.relicsandartifacts` (Vanilla Ideology Expanded - Relics; none)
- `vanillaexpanded.outposts` (Vanilla Outposts Expanded; none)
- `vanillaexpanded.vanillatraitsexpanded` (Vanilla Traits Expanded; soft; patches 2f; FindMod 2f; About 1f)
- `ninagoblin.visitsettlements` (Visit Settlements; none)
- `ogliss.g223.wanderingcaravans` (Wandering Caravans; none)
- `addvans.wasdedpawn` (WASDed Pawn; none)
- `aelanna.weaponracks` (Weapon Racks; none)
- `bodlosh.weaponstats` (WeaponStats; none)
- `revolus.whatsmissing` (What's Missing?; none)
- `winggar.meaningfulparties` (Wing's Meaningful Parties; soft; patches 1f)
- `fluffy.worktab` (Work Tab; none)
- `bs.xenotypespawncontrol` (Xenotype Spawn Control; none)
- `mlie.yayoscaravan` (Yayo's Caravan (Continued); none)
- `mlie.yayosmeteor` (Yayo's Meteor (Continued); none)
- `mlie.dungeonpack` (Dungeon Pack (Continued); soft; patches 4f; FindMod 1f; About 2f)
- `jaeger972.factionterritories` (Faction Territories and Vassalage; none)
- `aoba.fortress.industrial` (Fortifications - Industrial; soft; patches 4f; FindMod 1f; About 2f)
- `gmmp.dungeon` (Gerrymon's Misc Props: Dungeon; none)
- `neku.largepawns` (Large Pawns; order only; About 1f)
- `lwm.deepstorage` (LWM's Deep Storage; none)
- `zal.moreutilitypacks` (More Utility Packs (Continued); soft; patches 3f; About 1f)
- `andromeda.niceresearchtab` (Nice Research Tab; none)
- `mlie.preceptsandmemesritualsmodule` (Precepts and Memes - Rituals modul; none)
- `lambda.psykshroom` (Psyshrooms; none)
- `memegoddess.replacestuff` (Replace Stuff - Continued; none)
- `jaxe.rimhud` (RimHUD; none)
- `zal.spaceports` (Rimsential - Spaceports (Continued; soft; patches 1f)
- `telardo.romanceontherim` (Romance On The Rim; soft; patches 1f; FindMod 1f; About 1f)
- `kathanon.searchablemenus` (Searchable Menus; none)
- `mlie.showmeyourhands` (Show Me Your Hands; soft; FindMod 1f)
- `scherub.stonecuttingextended` (Stonecutting Extended; none)
- `cyanobot.toddlers` (Toddlers; none)
- `vanillaexpanded.vchemfuele` (Vanilla Chemfuel Expanded; soft; patches 1f; FindMod 1f)
- `mrhydralisk.voeadditionaloutposts` (Vanilla Outposts Expanded: Additio; none)
- `vanillaexpanded.vwel` (Vanilla Weapons Expanded - Laser; none)
- `zacharyfoster.mineralssparkle` (Minerals Sparkle; none)
- `mehni.pickupandhaul` (Pick Up And Haul; none)
- `avius.prisonlabor` (Prison Labor; soft; patches 1f; FindMod 1f; About 1f)
- `oskarpotocki.vfe.pirates` (Vanilla Factions Expanded - Pirate; soft; defs 3 names (0 unguarded in 0f); patches 12f; MayRequire 1f; FindMod 7f; About 4f)
- `opa.allspecialistscanwork` (All Specialists Can Work; none)
- `teiwaz.gtgtradercore` (GTG Trader Core; none)
- `keyz182.keyzallowutilities` (Keyz' Allow Utilities; none)
- `toastyman.moreritualseats` (More Ritual Seats; soft; defs 1 names (0 unguarded in 0f); MayRequire 19f)
- `sugarcube.puahsharedstorage` (Pick Up And Haul - Shared Storage ; none)
- `legator.prisonerrealism` (Prisoner Realism; soft; patches 1f; FindMod 1f; About 1f)
- `petetimessix.simplesidearms` (Simple sidearms; none)
- `tribeagle.simpleslaverycollars` (Simple Slavery Collars; soft; patches 1f; FindMod 1f; About 1f)
- `oskarpotocki.vanillavehiclesexpanded` (Vanilla Vehicles Expanded; soft; patches 9f; FindMod 1f; About 2f)
- `divinederivative.romance` (Way Better Romance; soft; patches 1f; FindMod 1f; About 1f)
- `brrainz.achtung` (Achtung!; none)
- `kem.beardadjustment` (Beard Adjustment; none)
- `lovelydovey.sex.witheuterpe` (Intimacy - Friends n' Lovers; none)
- `redmattis.optional` (Big and Small - Enable All Optiona; none)
- `avilmask.commonsense` (Common Sense; none)
- `lovelydovey.recreation.witheuterpe` (Intimacy - Socio Butterfly; none)
- `frozensnowfox.complexjobs` ([FSF] Complex Jobs; none)
- `dubwise.dubsbreakmod` (Dubs Break Mod; none)
- `taranchuk.performanceoptimizer` (Performance Optimizer; none)
- `co.uk.epicguru.meleeanimation` (Melee Animation; soft; FindMod 1f)
- `meathax.showmeyourtools` (Show Me Your Tools - Forked; none)
- `rw.mod.simplestairs` (SimpleStairs (Fork); none)
- `kutte.stairs` (Simple Visual Stairs; none)

## 11. Traps hit and false positives

- **The dump's ownership column credits re-declared vanilla defs to the last mod** (`kas.strongerscaling` "owned"
  16 vanilla StatDefs named in 432 of our files). Excluding the game's own `Data/` defNames removed this class;
  without it Stronger Quality Scaling and Survival Tools looked HARD.
- **Armoury's `CompExtraSounds.*`, `SecondaryMineableYield.*`, `guy762_Ionization.*`, `KoltoTank.*` and nine more
  namespaces are OUR code** (absorbed sources compiled into `JawaArmoury.dll`), not a third-party DLL. The 10-10
  `class_ref` edge credits `CompExtraSounds` to JecsTools, which ships a DLL of the same name; JecsTools stays F1
  regardless.
- References to inactive mods (`PathfindingFramework`, `NocturnalAnimals`, `AthenaFramework`, `ArtificialBeings`)
  are all `MayRequire`-guarded on the def or the `li`; they are not on the list and not counted.
- Two hits are not defs: `VQE_Experiment` (a backstory spawnCategory string) and VSE's `Butcher`/`Major` (an enum
  value and prose); both are marked in their rows.
