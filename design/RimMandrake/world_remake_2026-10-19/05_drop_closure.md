# World remake 05: dependency closure of the 124 "simply drop" mods (2026-10-19)

FOUNDRY, offline. No game, no bridge, no ModsConfig write. Owner chose option D by question card 2026-10-19 (*"Yes,
and also deploy the 39-mod retirement"*); the remake is a DEVELOPMENT world that may be repainted. This file answers
PLAN.md §5b: which of 01 §5's 124 can go without breaking a mod that stays.

## 0. Answer

- **SAFE to drop: 112.** No retained mod (ours or third-party) hard-depends on them or names their C# classes.
- **HOLD: 12.** 5 world-generation mods (held until the generator procedure is proven inert, 02 §2) and 7
  with a retained dependant. Holding them changes nothing on today's list.
- **Candidate profile:** `deployed/config/ModsConfig.CANDIDATE_2026-10-19.xml`, **367 mods** = the live 536 minus Wave 1 (39,
  `det.epochspyrinth` swapped in place for `mandrake.rm.pyrinth`) minus the 112 SAFE minus 25 class-E mods (6 of which
  are also SAFE drops). Every `modDependencies` entry of every mod in it resolves inside it (fresh About.xml read,
  0 unmet). **A file only: not activated, not deployed.**

## 1. Method

- Base list: `infrastructure/state/modlists/ModsConfig.FULL.DONOR_FREE_536_weathersuite_2026-10-19.xml` (536; identical to
  the live ModsConfig at 06:03, per 01 §0). Class lists parsed from 01's tables: B = 39, C2 = 124, E = 32 (counts match 01).
- Retained = live minus Wave 1 minus the 124. Each retained mod's About.xml was read FRESH from the Steam `Mods` folder or
  its workshop folder (all 536 found): `modDependencies` (+ v1.6 by-version) = hard; `loadAfter`/`forceLoadAfter` = order only.
- Class and def edges: `design/RimMandrake/mod_audit/facts/mod_facts.jsonl` `dependants_detail` (2026-10-10 DLL/XML scan):
  `class_ref` = HOLD; `def_ref` alone = SAFE-watch after a guard probe (does the dependant's XML name the dropped packageId,
  i.e. a `MayRequire`/LoadFolders guard?).
- Ours: every `src/` XML and `.cs` file naming the packageId (excluding `obj/`, `bin/`), and our `src/**/About.xml`
  `modDependencies`: **0 of ours hard-depend on any of the 124** (agrees with 01). Our references are `loadAfter`, guarded
  patches, `MayRequire` rows and `FindMod`: load-safe, but delete them in the same change (owner: remove offending material).
- Sanity probe: the known case `hailuan.customquestframework` ← `mlie.dungeonpack` is found by both instruments.
- **UNMEASURED:** (1) save-borne residue: whether the 112's classes/defs sit in the `_AREAFIX2` fixtures (run
  `save_class_census.py` / `save_def_census.py` on a fixture against the candidate before promotion); (2) `def_ref` edges whose
  guard is a `FindMod` by mod NAME (the probe only greps packageIds), listed as "watch" below; (3) C# string defName
  references in third-party DLLs beyond the 10-10 scan.

## 2. HOLD (12)

| mod | packageId | why held | what releases it |
|---|---|---|---|
| Alien Worlds Framework | `7f.alienworlds` | world-generation framework; Ash'karr was generated with it (02 §2); our UtinniPatches/StarWarsPatches loadAfter it | generator procedure proven inert without it (02 §2; runbook gates), or the world/fixtures no longer need it |
| Alien Worlds - Tidally Locked | `7f.alienworlds.tidallylocked` | world-generation (tidal lock); our `JawaWorld_BiomeMix.xml` patches it (guarded) | generator procedure proven inert without it (02 §2; runbook gates), or the world/fixtures no longer need it |
| Biomes! Framework | `biomesteam.coreframework` | retained `biomesteam.biomesfossils` and `zylle.morevanillabiomes` (C1) name its C# classes (10-10 class_ref); no About dependency, so the load would not refuse, but the classes would fail to resolve | drop the dependant too (a ruling on it), or keep |
| Sensible Factions | `boots.sensiblefactions` | world-generation faction placer, active at the faction pass | generator procedure proven inert without it (02 §2; runbook gates), or the world/fixtures no longer need it |
| Deep Orbit | `broms.deeporbit` | world-generation AND save-borne: its `Orbit2` planet layer is required to LOAD the 09-12-family saves (lesson 20261016T155408Z), so the `_AREAFIX2` fixtures option D proves on need it | generator procedure proven inert without it (02 §2; runbook gates), or the world/fixtures no longer need it |
| Custom Quest Framework | `hailuan.customquestframework` | retained `mlie.dungeonpack` hard-depends on it (modDependencies, fresh About.xml) and uses its classes (10-10 class_ref) | drop the dependant too (a ruling on it), or keep |
| My Little Planet | `oblitus.mylittleplanet` | world-generation (planet size); our PlanetPresetPrime loadAfters it | generator procedure proven inert without it (02 §2; runbook gates), or the world/fixtures no longer need it |
| Vanilla Apparel Expanded — Accessories | `vanillaexpanded.vaeaccessories` | retained `zal.moreutilitypacks` hard-depends on it (modDependencies) | drop the dependant too (a ruling on it), or keep |
| Vanilla Furniture Expanded - Architect | `vanillaexpanded.vfearchitect` | retained `aoba.fortress.industrial` names its classes and defs (10-10 class_ref + def_ref) | drop the dependant too (a ruling on it), or keep |
| Vanilla Furniture Expanded - Props and Decor | `vanillaexpanded.vfepropsanddecor` | retained `gmmp.dungeon` (Gerrymon's Dungeon) hard-depends on it and uses its classes | drop the dependant too (a ruling on it), or keep |
| Minerals Framework | `zacharyfoster.mineralsframework` | retained `zacharyfoster.mineralssparkle` hard-depends on it and uses its classes | drop the dependant too (a ruling on it), or keep |
| BiomesKit (Continued) | `zal.biomeskit` | retained `ironscruff.primordialgeysers` (C1) names its C# classes (10-10 class_ref) | drop the dependant too (a ruling on it), or keep |

Dependants that go with their framework are NOT holds: `hailuan.customquestframeworkai` (depends on CQF; dropping the add-on while CQF
is held is fine), `zal.comigogreaterswamps` → BiomesKit, `icepickgma.invisibledisplaycase` → `nightmare.core`, `kilokio.rimai.core` →
framework, `xylthixlm.races.titan` → core, `smxrez.makeshiftreexamined` → `vanillaexpanded.vwems`, the Facial Animation texture
chain (`vanillaexpanded.vtexe.facialanims` → `reel.facialanims` → `sd.fa.reelsadjustments`, `sd.fa.vteadjustments`), the BTD
ship pack → blueprints: every member is in the 112.

## 3. SAFE to drop (112)

"ours" = `src/` files naming the packageId (cleanup owed in the same change; guarded or `loadAfter` only). "watch" = a
retained third-party `def_ref` edge (10-10) with no packageId guard found: worst case a cross-reference error at the
candidate load, not a refusal; read Player.log for these names at the proof load.

| mod | packageId | ours | watch | E? |
|---|---|---:|---|---|
| Vanilla Backgrounds Expanded | `vanillaexpanded.backgrounds` | 3 |  |  |
| [ZAV] Glowstone | `zav.glowstoneforked` |  |  |  |
| Adaptive Ideology Storage | `adaptive.ideology.storage` |  |  |  |
| Adaptive Primitive Storage | `adaptive.primitivestorage` |  |  |  |
| Adaptive Simple Storage | `adaptive.simplestorage` |  |  |  |
| Ambient Rim | `swablu.ambience` |  |  |  |
| Ancient Dangers on Campsites and Encounter maps | `vita.campdangers` |  |  | E |
| Astronomy Style Pack | `asp.halituisamaricanous` |  |  |  |
| Beliar Xenotype | `elsov.beliar` |  |  |  |
| Better Infestations (Continued) | `zal.betterinfestations` | 3 | `vanillaexpanded.vgeneticse` | E |
| Better Trees | `chaoticenrico.bettertrees` |  |  |  |
| Biome Compatibility Project | `kopp.biomecompatibilityproject` | 1 |  |  |
| Children Learn on Caravan [USE NEW FORK!] | `heatherathebyne.childrenlearnoncaravan` |  |  |  |
| Cybranian - Ideology Virtues | `dimonsever000.ideologyvirtues` |  |  |  |
| Dance Party Custom Music | `east.dancepartycustommusic` |  |  |  |
| Dark Ages : Beasts and Monsters | `van.beasts` | 4 |  |  |
| Det's Xenotypes - Avaloi | `det.avaloi` | 1 |  |  |
| Det's Xenotypes - Boglegs | `det.boglegs` |  |  |  |
| Det's Xenotypes - Brawnum | `det.brawnum` |  |  |  |
| Det's Xenotypes - Buzzers | `det.buzzers` | 2 |  |  |
| Det's Xenotypes - Venators | `det.venators` |  |  |  |
| Engines Unlimited | `nep.enginesunlimited` |  |  |  |
| Epochs - Incense | `det.epochsincense` |  |  |  |
| Face Addon Framework | `eoralmilk.faceaddonframework` |  |  |  |
| Faction Raid Cooldown (Continued) | `mlie.factionraidcooldown` | 2 |  |  |
| Guaranteed Ancient Dangers | `arti.shrinez` |  |  |  |
| Highborn Xenotype | `elsov.highborn` |  |  |  |
| I will be back | `hailuan.iwbb` |  |  | E |
| Ideology symbols as Ideograms | `kxp.ideosymbolsasideograms` |  |  |  |
| Ion Weaponry (Continued) | `zal.ionweaponry` |  |  |  |
| Large Outpost (Continued) | `zal.largeoutpost` |  |  |  |
| Laser Cannon | `arcjc007.lasercannon` | 1 |  |  |
| LiquidSFX | `dorbo.watersfx` |  |  |  |
| Medieval Signs | `mewn.medievalsigns` |  |  |  |
| MiningCo. Alert speaker (Continued) | `mlie.miningcoalertspeaker` | 1 |  |  |
| MiningCo. DrillTurret (Continued) | `mlie.miningcodrillturret` | 2 |  |  |
| MiningCo. MMS (Continued) | `mlie.miningcomms` | 1 |  |  |
| MiningCo. Spaceship (Continued) | `mlie.miningcospaceship` | 1 |  |  |
| More Faction Interaction (Continued) | `mlie.morefactioninteraction` |  |  | E |
| Natural Paths | `radzerp.naturalpaths` |  |  |  |
| Nightmare Core | `nightmare.core` |  |  |  |
| Polyamory Beds (Vanilla Edition) | `meltup.polyamorybeds.vanilla` |  |  |  |
| Posthuman Drift Core Mod | `xylthixlm.races.core` |  |  |  |
| Psilocap Cultivation | `laureeeeeeeeeeeeeeen.shrooms` |  |  |  |
| Recycle This (Continued) | `mlie.recyclethis` |  |  |  |
| RimAI Framework | `kilokio.rimai.framework` |  |  | E |
| Roots of Rimworld | `ghost.rootsofrimworld` | 1 |  |  |
| RW - Planet Atmosphere | `rwnodetree.rwplanetatmosphere` |  |  |  |
| Salvage Rubble | `moja.salvagerubble` |  |  |  |
| Shavius's Medieval Flavour Pack | `shavius.medieval.flavour` |  |  |  |
| Smelt More Stuff | `hol.smeltpatch` |  |  |  |
| Standalone Hot Spring | `balistafreak.standalonehotspring` |  |  |  |
| Stylized Slave Collars and Headgears | `gerrymon.stylizedslavecollar` |  |  |  |
| Tabletop Decorations | `ucp.tabletopdecorations` |  |  |  |
| Torture Pod | `tsa.torturepod` | 1 |  |  |
| Tradeable Trinkets (Continued) | `mlie.tradeabletrinkets` |  |  |  |
| Transparent Substructure | `aelanna.transparentsubstructure` |  |  |  |
| Trystan Traveller's Shuttle Schematics | `trouperton.trystantravellersshuttleschematics` |  |  |  |
| Utility Columns | `nephlite.orbitaltradecolumn` | 2 | `memegoddess.replacestuff` |  |
| Vanilla Apparel Expanded | `vanillaexpanded.vappe` | 1 | `andromeda.niceresearchtab`; ours: `mandrake.rut.researchretag` |  |
| Vanilla Backstories Expanded | `vanillaexpanded.vanillabackstoriesexpanded` |  |  |  |
| Vanilla Furniture Expanded | `vanillaexpanded.vfecore` | 1 | `andromeda.niceresearchtab`, `cozyfire.velcroboy333`, `cyanobot.toddlers`, `memegoddess.replacestuff`, `oskarpotocki.vfe.tribals`, `sarg.alphamemes`, `vanillaexpanded.vbrewe`, `vanillaexpanded.vmemese` |  |
| Vanilla Furniture Expanded - Art | `vanillaexpanded.vfeart` | 1 | `andromeda.niceresearchtab` |  |
| Vanilla Furniture Expanded - Farming | `vanillaexpanded.vfefarming` | 1 | `andromeda.niceresearchtab`; ours: `mandrake.rut.researchretag` |  |
| Vanilla Furniture Expanded - Medical Module | `vanillaexpanded.vfemedical` |  |  |  |
| Vanilla Furniture Expanded - Power | `vanillaexpanded.vfepower` | 1 | `andromeda.niceresearchtab`, `memegoddess.replacestuff`, `sarg.alphamemes`, `vanillaexpanded.helixiengas`, `vanillaexpanded.vgeneticse` |  |
| Vanilla Furniture Expanded - Production | `vanillaexpanded.vfeproduction` | 1 | `andromeda.niceresearchtab`, `meathax.showmeyourtools`, `memegoddess.replacestuff`, `vanillaexpanded.helixiengas` |  |
| Vanilla Furniture Expanded - Spacer Module | `vanillaexpanded.vfespacer` | 1 | `andromeda.niceresearchtab`, `memegoddess.replacestuff` |  |
| Vanilla Ideology Expanded - Hats and Rags | `vanillaexpanded.viehar` |  | `vanillaexpanded.vmemese` |  |
| Vanilla Quests Expanded - The Generator | `vanillaquestsexpanded.generator` | 2 | ours: `mandrake.rut.patches` |  |
| Vanilla Races Expanded - Fungoid | `vanillaracesexpanded.fungoid` |  | `redmattis.betterprerequisites`, `redmattis.bigsmall.core` |  |
| Vanilla Races Expanded - Phytokin | `vanillaracesexpanded.phytokin` | 4 | ours: `mandrake.rut.patches` |  |
| Vanilla Races Expanded - Starjack | `vanillaracesexpanded.starjack` |  |  |  |
| Vanilla Weapons Expanded - Makeshift | `vanillaexpanded.vwems` |  | `andromeda.niceresearchtab`, `mlie.showmeyourhands` |  |
| VehicleRaid Framework | `gabrieel1482.raidvehicleframework` |  |  |  |
| Walk the World | `addvans.walktheworld` |  |  |  |
| Wirehead Style | `tleno.wireheadstyle` |  |  |  |
| [BTD] Gravship Blueprints | `btd.remix.gravshipblueprints` | 3 |  |  |
| [NL] Facial Animation - Experimentals | `nals.facialanimationexperimentals` |  | `gravtide.mod`; ours: `mandrake.rm.flowworks`, `mandrake.rut.pawnflavor` |  |
| Custom Quest Framework-Level AI | `hailuan.customquestframeworkai` |  |  |  |
| EGI Holograms and Projectors | `vesper.egihologramsandprojectors` | 1 |  |  |
| Genetic Heads Framework for [NL] Facial Animatio | `sd.fa.geneticheadsframework` |  |  |  |
| Giant Toads (Continued) | `zal.gianttoads` | 2 |  |  |
| Invisible Display Case Continued | `icepickgma.invisibledisplaycase` |  |  |  |
| Makeshift: Re-Examined | `smxrez.makeshiftreexamined` |  |  |  |
| More Ritual Rewards | `sinnamon.moreritualrewards` |  |  |  |
| Posthuman Drift Titan Xenotype | `xylthixlm.races.titan` | 1 |  |  |
| Quarry | `ogliss.thewhitecrayon.quarry` |  |  |  |
| RimAI Core (BETA) | `kilokio.rimai.core` | 1 |  | E |
| Vanilla Cooking Expanded - Stews | `vanillaexpanded.vcookestews` | 1 | `andromeda.niceresearchtab` |  |
| Vanilla Mining Outpost Patch | `kuhlyus.modpatch.vanillaoutpost` |  |  |  |
| [42G]Glowing Bushes / Fork by [ETF] | `fourtoo.glowingbush` |  |  |  |
| Comigo's Greater Swamps (Continued) | `zal.comigogreaterswamps` | 2 | ours: `mandrake.rut.patches` |  |
| Functional Vanilla Expanded Props (Continued) | `mlie.functionalvanillaexpandedprops` |  |  |  |
| Genetic Biotech for Facial Animation | `sd.fa.geneticheadsbiotech` |  |  |  |
| Genetic Mods for Facial Animation | `sd.fa.geneticheadsmods` |  |  |  |
| Minerals Frozen | `zacharyfoster.mineralsfrozen` |  |  |  |
| Minerals Rock | `zacharyfoster.mineralsrock` |  | `zacharyfoster.mineralssparkle` |  |
| Reel's Facial Animation Textures | `reel.facialanims` |  | `redmattis.betterprerequisites`, `vanillaexpanded.vmemese` |  |
| Adjustments for Reel's Facial Animation Textures | `sd.fa.reelsadjustments` |  |  |  |
| Vanilla Textures Expanded - [NL] Facial Animatio | `vanillaexpanded.vtexe.facialanims` |  |  |  |
| VFE Pirates - Hardworking Warcaskets | `dmp.vfepirates.warcasketwork` | 1 |  |  |
| [GTG]Traders Accept All Junk Gear | `teiwaz.taajg` |  |  |  |
| [GTG]Traders Accept Chunks & Corpses | `teiwaz.tacac` |  |  |  |
| Adjustments for Vanilla Textures Expanded - [NL] | `sd.fa.vteadjustments` |  |  |  |
| Big and Small - Weapons | `redmattis.bigweapons` |  |  |  |
| LK Mineable Resources Outer Rim | `leutiankane.mineablesor` | 3 |  |  |
| LK Mines 2.0 Compatability[Outer Rim Core] | `leutiankane.mines2patchouterrim` | 2 |  |  |
| Outer Rim - Furniture & Decor | `neronix17.outerrim.furnitureanddecor` | 1 | `neronix17.outerrim.core` |  |
| Facial Animation Compatability Project | `danzinagri.facialanimationcompatabilityproject` | 4 |  |  |
| Sand Castles | `zylle.sandcastles` |  |  |  |
| [BTD] Ship Pack: KotOR Ships VGE | `btd.gbp.shippack.kotor.vge` | 1 |  |  |

## 4. The candidate profile

`deployed/config/ModsConfig.CANDIDATE_2026-10-19.xml` (367). Order = the live order with removals; `mandrake.rm.pyrinth` takes
`det.epochspyrinth`'s index (RETIREMENT_WAVE_1.md row 29).

**Class E excluded (25):** `mlie.nwnrealfogofwar`, `krkr.rule56`, `mlie.yayoscombat3`, `vanillaexpanded.vee`, `zal.betterinfestations`, `koth.isid`, `mlie.spaceworms`, `sk.gravshipraids`, `arcjc007.gravshipcrashes`, `ionfrigate12345.coolandgoodambush`, `sirdarkelf.meaningfulencounters`, `ogliss.g223.wanderingcaravans`, `sr.modrimworld.factionalwarcontinued`, `zal.spaceports`, `hailuan.iwbb`, `vita.campdangers`, `mlie.yayosmeteor`, `geojak.tributedemand`, `mlie.morefactioninteraction`, `mlie.rimquest`, `dubwise.dubsbreakmod`, `mlie.slaverebellionsimproved`, `amoruch.rimworldstealingmod`, `kilokio.rimai.core`, `kilokio.rimai.framework`.

- 🔴 **The fog pair goes together:** `mlie.nwnrealfogofwar` AND `krkr.rule56` are both out (CAI is what strips the fog on
  player maps; dropping CAI alone brings fog back). Re-add both for ship (Route B ruling).
- **Tier exceptions (01 §7), kept in this base dev profile and excluded only in their own tier (7):** `acutus.moodchainreaction`, `co.uk.epicguru.meleeanimation`, `jaxe.bubbles`, `kas.strongerscaling`, `nals.facialanimation`, `taranchuk.performanceoptimizer`, `wemd.realisticdarknesslight`.
  Stronger Quality Scaling leaves tuning tiers; Mood Chain Reaction pawn/mood tests; Realistic Darkness art/visual-review tiers;
  Performance Optimizer when a bug smells of stale state; Melee Animation combat balance; Interaction Bubbles screenshots;
  `nals.facialanimation` is a C16 KEEP and the Facial Animation stack depends on it (pixel-diff tests only).
- `mlie.incidentdisabler` (evaluation AID) stays. Class D authoring tools stay (they leave at release, not in dev).
- Not reconciled in this file: the Cherry Picker ship profile (`CHERRY_PICKER_RESTORE_FROM_SHIP_PROFILE`, a Wave 1 step) and
  the 12 HOLDs' `def_ref` dependants. **Promotion** = a donor-off load of this profile on a copy of an `_AREAFIX2` fixture and
  fresh scratch maps (option D step 1), then the three save censuses. Never activate by copying this file over ModsConfig.xml.
