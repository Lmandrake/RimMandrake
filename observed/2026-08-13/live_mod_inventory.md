# live_mod_inventory.md — ACTIVE and INACTIVE mods, read from the machine

_Regenerated **2026-08-10 (third pass)** from `Config/ModsConfig.xml` + every installed `About/About.xml`. **Single source of truth for mod identity** — existence, packageId, Workshop ID, author, supported versions. Overrides all such claims elsewhere in the corpus. Regenerate, don't hand-edit._

**RimWorld 1.6 · 562 ACTIVE · 1211 installed · 655 inactive.**

> Snapshot history: 464 active (08-09) → 548 (08-10 a.m.) → **562** (08-10 p.m.).

---

## 1. Newly ACCEPTED this pass

| Mod | WS | Role | Notes |
|---|---|---|---|
| **Effigys – Terror Spikes** | 3647930333 | ✅ **ACCEPTED — Hutt territory decor.** Wooden effigy crowned with five human heads; fear aura. | Requires **Ideology**. packageId is literally `YourName.Effigys.Mod` — an unedited template. Cosmetically harmless but a sign of a hobby build; treat as art, not mechanics. Serves `desert_world_design.md` §3F (turf markers on Hutt ground) alongside `GibbetCage`/`Skullspike`. |
| **Torment Master** | 3746663772 | ✅ **ACCEPTED — Hutt flavour + fodder for tile maps / settlements.** | Requires **Biotech**. 6 buildings: Brazen Bull, Oil-Pour Cage, Water Prison, Laser Flayer (yields a wearable skin suit that disguises the wearer as the donor), Live Target Range, Auto-Vending Machine (sells organs; factions send buyers → **goodwill**). Plus a Cranial Pin (surgical prisoner-compliance implant) and trinkets. Author states: compatible with HAR, Facial Animation, Toddlers, Prison Labor; **safe to add mid-save**; to remove cleanly, deconstruct everything and reverse the pin surgeries first. |
| **Dynamic AI Sculptures** | 3753149685 | ✅ ACCEPTED — see §2. | `codex.dynamicaisculptures`, Artas48. Hard deps: Harmony + Powerful AI Integration. |
| **Powerful AI Integration** | 3744421283 | ⚠️ ACCEPTED **as a dependency only** — see §2. | `codex.dynamicrolesstoryteller`, Artas48. Note the packageId: this mod's real identity is a **dynamic-roles storyteller**, not an art library. |

## 2. ⚠️ Powerful AI Integration — read before configuring

Dynamic AI Sculptures is a genuinely good fit: craftable sculptures in 1×1 / 2×2 / 3×3 / 4×4 whose
artwork is AI-generated, imported, or pulled from a public community library, with **textures applied
live in-game** — no restart, no save reload. There is a reveal-cloth animation when the art lands, and
approved community results can be downloaded so it works before you configure any image provider.
For a scrapper clan that venerates salvaged objects, procedurally-unique sculptures are close to ideal.

**But its dependency is not a graphics library.** `Powerful AI Integration`'s own description (Russian)
translates to: *"adds a shared AI layer for the story and life of the colony: an **event director**,
**dynamic roles**, player prayers, live pawn dialogue, conversation memory, relationships and
storylines. It accounts for characters, factions, canon, colony state and real game events, works with
local models, bridges and OpenAI-compatible APIs, and falls back to safe local rules when needed."*
Its packageId is `codex.dynamicrolesstoryteller`.

**That is a fourth LLM director**, on top of RimTalk (30 mods), RimAI Core, and our own external
RimBridge/Imperial-Heat GM layer. Its warning is also explicit: *"do not remove the mod from a started
save without a backup."*

**Ruling: install it, use the sculpture path, leave the director OFF.**
- Turn off / do not configure: the event director, dynamic roles, prayers, pawn dialogue, memory.
- Reason: an LLM firing events competes directly with the **Imperial Heat gauge**, the sanctioned
  pacing mechanism — same objection that parked `RimTalk Expand: AI Storyteller`.
- Its pawn-dialogue layer is a **fifth** owner of speech bubbles. Leave it off.
- It can share the Ollama endpoint (`http://localhost:11434/v1`) for image/text calls once that is up.
- Because it is save-embedded, decide *before* the campaign save, not after.

## 3. Standing conflicts / open items

| Item | State |
|---|---|
| **Speech-bubble owners** | SpeakUp + RimTalk + Interaction Bubbles all active — and Powerful AI adds a fourth if its dialogue layer is enabled. Scope to one. |
| **Big and Small ×6 + Large Pawns** | Deliberate scaling experiment. |
| **AUR trio** | Correct — Hit Point *requires* All Deconstructible. |
| **Lightsabers** | Resolved — only The Force – Lightsaber (KotOR hard-dep). |
| **RimTalk Expand: AI Storyteller** | Recommend OFF (competes with Imperial Heat). |
| **RimTalk – Expand Actions** | Disable `recruit` and `surrender`. |
| **RimAI Core** | Voice-only; actuator tools off. |

---

## 4. ACTIVE — full load order

_Order is significant; this is the exact `<activeMods>` sequence._


### Core / DLC (6)

| # | Mod | packageId | Workshop | Versions |
|---:|---|---|---|---|
| 4 | (CORE/DLC/LOCAL) | `ludeon.rimworld` | — | — |
| 5 | (CORE/DLC/LOCAL) | `ludeon.rimworld.royalty` | — | — |
| 6 | (CORE/DLC/LOCAL) | `ludeon.rimworld.ideology` | — | — |
| 7 | (CORE/DLC/LOCAL) | `ludeon.rimworld.biotech` | — | — |
| 8 | (CORE/DLC/LOCAL) | `ludeon.rimworld.anomaly` | — | — |
| 9 | (CORE/DLC/LOCAL) | `ludeon.rimworld.odyssey` | — | — |

### Frameworks & libraries (33)

| # | Mod | packageId | Workshop | Versions |
|---:|---|---|---|---|
| 1 | Prepatcher | `zetrith.prepatcher` | 2934420800 | 1.4,1.5,1.6 |
| 2 | Harmony | `brrainz.harmony` | 2009463077 | 1.2,1.3,1.4,1.5,1.6 |
| 3 | Better Stacktraces | `aleksey.betterstacktraces` | 3541579129 | 1.6 |
| 12 | Adaptive Storage Framework | `adaptive.storage.framework` | 3033901359 | 1.4,1.5,1.6 |
| 13 | Fortified Features Framework | `aoba.framework` | 3498575851 | 1.5,1.6 |
| 15 | XML Extensions | `imranfish.xmlextensions` | 2574315206 | 1.2,1.3,1.4,1.5,1.6 |
| 16 | Custom Ritual Framework | `thesepeople.ritualattachableoutcomes` | 2561617361 | 1.3,1.4,1.5,1.6 |
| 17 | Big and Small - Framework | `redmattis.betterprerequisites` | 2925432336 | 1.4,1.5,1.6 |
| 18 | Vehicle Framework | `smashphil.vehicleframework` | 3014915404 | 1.4,1.5,1.6 |
| 19 | HugsLib | `unlimitedhugs.hugslib` | 818773962 | 1.0,1.1,1.2,1.3,1.4,1.5,1.6 |
| 20 | Vanilla Expanded Framework | `oskarpotocki.vanillafactionsexpanded.core` | 2023507013 | 1.0,1.1,1.2,1.3,1.4,1.5,1.6 |
| 21 | EBSG Framework | `ebsg.framework` | 3112549163 | 1.4,1.5,1.6 |
| 59 | Asimov | `neronix17.asimov` | 3096481956 | 1.4,1.5,1.6 |
| 81 | Biomes! Framework | `biomesteam.coreframework` | 3709492514 | 1.6 |
| 82 | BiomesKit (Continued) | `zal.biomeskit` | 3333951497 | 1.5,1.6 |
| 105 | Custom Quest Framework | `hailuan.customquestframework` | 2978572782 | 1.4,1.5,1.6 |
| 140 | Face Addon Framework | `eoralmilk.faceaddonframework` | 3217914520 | 1.4,1.5,1.6 |
| 183 | JecsTools Unofficial 1.6 BETA | `jecrell.jecstools` | 3524247750 | 1.0,1.1,1.2,1.3,1.4,1.5,1.6 |
| 201 | Map Mode Framework | `nozome.mapmodeframework` | 3296654393 | 1.6,1.5 |
| 224 | ModularWeapons 2 | `kaitorisenkou.modularweapons2` | 3497834944 | 1.6 |
| 275 | Resource Dictionary | `scorpio.resourcedictionary` | 2817607528 | 1.3,1.4,1.5,1.6 |
| 280 | RimAI Framework | `kilokio.rimai.framework` | 3529263357 | 1.5,1.6 |
| 390 | VehicleRaid Framework | `gabrieel1482.raidvehicleframework` | 3667863988 | 1.6 |
| 416 | ChezhouLib | `chezhou.chezhoulib.lib` | 3595247479 | 1.6 |
| 418 | Custom Quest Framework-Level AI | `hailuan.customquestframeworkai` | 3534228105 | 1.6 |
| 422 | Genetic Heads Framework for [NL] Facial Animation | `sd.fa.geneticheadsframework` | 3498759997 | 1.5,1.6 |
| 437 | Minerals Framework | `zacharyfoster.mineralsframework` | 3562390384 | 1.6 |
| 457 | Tabula Rasa | `neronix17.toolbox` | 1660622094 | 1.3,1.4,1.5,1.6 |
| 472 | ABF: Artificial Beings Framework | `killathon.artificialbeings` | 3284097810 | 1.5,1.6 |
| 480 | Custom Quest Framework-Rimtalk addon | `hailuan.customquestframework.rimtalk` | 3684497117 | 1.6 |
| 520 | ABF: Synstructs Core | `killathon.artificialbeings.syncore` | 3288463094 | 1.5,1.6 |
| 544 | Performance Optimizer | `taranchuk.performanceoptimizer` | 2664723367 | 1.2,1.3,1.4,1.5,1.6 |
| 559 | Star Wars KotOR Resources and Materials | `guy762.mm.kotorcore` | 3254370945 | 1.5,1.6 |

### Industry / factory / progression (18)

| # | Mod | packageId | Workshop | Versions |
|---:|---|---|---|---|
| 57 | Ancient mining industry | `xmb.ancientminingindustry.mo` | 3141472661 | 1.4,1.5,1.6 |
| 100 | Configurable Techprints | `com.makeitso.configurabletechprints` | 2876747024 | 1.3,1.4,1.5,1.6 |
| 103 | Cremation smelts apparels | `thumb.bettercremation` | 3212165730 | 1.5,1.6 |
| 123 | Disassemble Mechanoid | `futurplanet.disassemblemechanoid` | 3191640281 | 1.4,1.5,1.6 |
| 207 | Mechanoid slag to Plasteel | `xelnigma.mechanoidslagtoplasteel` | 3552644190 | 1.6 |
| 264 | Quarry | `ogliss.thewhitecrayon.quarry` | 2007576583 | 1.0,1.1,1.2,1.3,1.4,1.5,1.6 |
| 271 | Recycle This (Continued) | `mlie.recyclethis` | 3253550009 | 1.3,1.4,1.5,1.6 |
| 274 | Research Reinvented | `petetimessix.researchreinvented` | 2868392160 | 1.3,1.4,1.5,1.6 |
| 282 | Rimefeller | `dubwise.rimefeller` | 1321849735 | 1.0,1.1,1.2,1.3,1.4,1.5,1.6 |
| 294 | Salvage Rubble | `moja.salvagerubble` | 3529058623 | 1.6 |
| 305 | Show Known Techprints | `spacemoth.showknowntechprints` | 2920370783 | 1.4,1.5,1.6 |
| 312 | Smelt More Stuff | `hol.smeltpatch` | 2347285971 | 1.1,1.2,1.3,1.4,1.5,1.6 |
| 331 | Tinkering Bench and Biohacking Station | `propickelz.tinkerbench` | 3522976063 | 1.5,1.6 |
| 361 | Vanilla Chemfuel Expanded | `vanillaexpanded.vchemfuele` | 2792917473 | 1.6,1.4,1.5 |
| 368 | Vanilla Furniture Expanded - Factory | `vanillaexpanded.vfefactory` | 3686924415 | 1.6 |
| 412 | Belt Extractors - VFE Factory Patch | `groovytaco.beltextractors` | 3694555789 | 1.6 |
| 448 | Research Reinvented Retextured | `aw.researchreinvented.retextured` | 3279243445 | 1.3,1.4,1.5,1.6 |
| 449 | Research Reinvented: Stepping Stones | `petetimessix.researchreinvented.steppingstones` | 2868389782 | 1.3,1.4,1.5,1.6 |

### Gravship / ship (16)

| # | Mod | packageId | Workshop | Versions |
|---:|---|---|---|---|
| 37 | [sbz] Gravship Storage | `sbz.gravshipstorage` | 3537905298 | 1.5,1.6 |
| 51 | Almost There! Fork | `duz.almosttherefork` | 3515165298 | 1.5,1.6 |
| 78 | Bigger Gravships (and other Odyssey spaceship related settings) | `redmattis.biggergravship` | 3522759531 | 1.6 |
| 114 | Deep Orbit | `broms.deeporbit` | 3533793836 | 1.6 |
| 135 | Engines Unlimited | `nep.enginesunlimited` | 3528446690 | 1.6 |
| 157 | Gravship Crashes | `arcjc007.gravshipcrashes` | 3578515873 | 1.6 |
| 158 | Gravship Exporter | `arcjc007.gravshipexporter` | 3576790938 | 1.6 |
| 159 | Gravship Range On Map | `imagitama.rimworldgravshiprangeonmap` | 3545884382 | 1.6 |
| 186 | Just F*King Landing | `mf.jfklanding` | 3525655208 | 1.6 |
| 245 | Non-Destructive Gravlaunch | `planetace.nondestructivegravlaunch` | 3522708183 | 1.6 |
| 292 | Roofed Scanning 1.6 | `kupie.isjustdoingitlive.plzdonthateme.roofedscanning` | 3524551636 | 1.3,1.4,1.5,1.6 |
| 341 | Transparent Substructure | `aelanna.transparentsubstructure` | 3522762741 | 1.6 |
| 372 | Vanilla Gravship Expanded - Chapter 1 | `vanillaexpanded.gravship` | 3609835606 | 1.6 |
| 407 | [BTD] Gravship Blueprints | `btd.remix.gravshipblueprints` | 3575162262 | 1.6 |
| 409 | [kyzy] Ship Wall Enhanced | `kyzy.shipwallenhanced` | 3537799933 | 1.6 |
| 425 | Gravship Raids | `sk.gravshipraids` | 3767338163 | 1.6 |

### World / biomes / terrain (34)

| # | Mod | packageId | Workshop | Versions |
|---:|---|---|---|---|
| 46 | Advanced Biomes (Continued) | `mlie.advancedbiomes` | 3541022508 | 1.6 |
| 52 | Alpha Biomes | `sarg.alphabiomes` | 1841354677 | 1.6,1.5 |
| 75 | Better Trees | `chaoticenrico.bettertrees` | 3539609975 | 1.6 |
| 79 | Biome Compatibility Project | `kopp.biomecompatibilityproject` | 3535674283 | 1.6 |
| 80 | Biomes! Fossils | `biomesteam.biomesfossils` | 3100958580 | 1.4,1.5,1.6 |
| 95 | Choose Biome Commonality | `mlie.choosebiomecommonality` | 2582875043 | 1.3,1.4,1.5,1.6 |
| 113 | Decorative Cliffs (Continued) | `mlie.decorativecliffs` | 2453099145 | 1.1,1.2,1.3,1.4,1.5,1.6 |
| 200 | Map Designer | `zylle.mapdesigner` | 2111424996 | 1.1,1.2,1.3,1.4,1.5,1.6 |
| 202 | Map Preview | `m00nl1ght.mappreview` | 2800857642 | 1.3,1.4,1.5,1.6 |
| 223 | Modify Tiles at Game Start | `hali.modifylandingtile` | 3667490447 | 1.6 |
| 231 | More Vanilla Biomes | `zylle.morevanillabiomes` | 1931453053 | 1.0,1.1,1.2,1.3,1.4,1.5,1.6 |
| 237 | Natural Paths | `radzerp.naturalpaths` | 2008833499 | 1.0,1.1,1.2,1.3,1.4,1.5,1.6 |
| 258 | Prepare Landing (Continued) | `m00nl1ght.unofficialupdates.preparelanding` | 3221125358 | 1.5,1.6 |
| 259 | Primordial Geysers | `ironscruff.primordialgeysers` | 2896731795 | 1.4,1.6 |
| 290 | Rimworld Exploration Mode | `thelastbulletbender.rwexploration` | 2941608795 | 1.4,1.5,1.6 |
| 375 | Vanilla Landmarks Expanded | `vanillaexpanded.vexploratione` | 3656316229 | 1.6 |
| 403 | WorldEdit 2.0 | `funkyshit.mods.worldedit.alpha` | 3590928058 | 1.2,1.3,1.4,1.5,1.6 |
| 413 | Better Trees: More Djeeshka Like Textures | `maal.bettertreesmod` | 3543705507 | 1.6 |
| 414 | Biomes! Core | `biomesteam.biomescore` | 2038000893 | 1.1,1.2,1.3,1.4,1.5,1.6 |
| 417 | Comigo - A Better Trees Mod | `qux.comigo.bettertreesmod` | 3559784361 | 1.6 |
| 446 | Realistic Planets 1.6 | `koth.realisticplanets1.6` | 3533147031 | 1.6 |
| 447 | ReGrowth 2 | `regrowth.botr.core` | 2260097569 | 1.4,1.5,1.6 |
| 478 | Biomes! Polluted Lands | `biomesteam.biomespollutedlands` | 3390196656 | 1.5,1.6 |
| 479 | Comigo's Greater Swamps (Continued) | `zal.comigogreaterswamps` | 3620545124 | 1.6 |
| 484 | Geological Landforms | `m00nl1ght.geologicallandforms` | 2773943594 | 1.3,1.4,1.5,1.6 |
| 486 | Minerals Frozen | `zacharyfoster.mineralsfrozen` | 3562390973 | 1.6 |
| 487 | Minerals Rock | `zacharyfoster.mineralsrock` | 3562391080 | 1.6 |
| 488 | Minerals Sparkle | `zacharyfoster.mineralssparkle` | 3562390730 | 1.6 |
| 493 | ReGrowth 2 World Map Beautification for Advanced Biomes (Continued) | `noxilie.regrow.wmb.advancedbiomes` | 3564679844 | 1.6 |
| 494 | ReGrowth 2 World Map Beautification for Alpha Biomes | `noxilie.regrow.wmb.alphabiomes` | 3564679302 | 1.6 |
| 495 | ReGrowth 2 World Map Beautification for Realistic Planets 1.6 | `noxilie.regrow.wmb.realisticplanets` | 3564680092 | 1.6 |
| 496 | ReGrowth: Boiling | `regrowth.botr.boilingforest` | 3565675704 | 1.4,1.5,1.6 |
| 523 | Biome Transitions | `m00nl1ght.geologicallandforms.biometransitions` | 2814391846 | 1.3,1.4,1.5,1.6 |
| 524 | Biomes! Caverns | `biomesteam.biomescaverns` | 2969748433 | 1.4,1.5,1.6 |

### Quests / structures / events (21)

| # | Mod | packageId | Workshop | Versions |
|---:|---|---|---|---|
| 56 | Ancient Dangers on Campsites and Encounter maps | `vita.campdangers` | 3521383341 | 1.4,1.5,1.6 |
| 88 | Call For Intel | `8z.callforintel` | 2557139479 | 1.4,1.5,1.6 |
| 111 | Darkest Dungeon Incident Sounds | `darkestdungeon.incidentsounds` | 3438213596 | 1.4,1.5,1.6 |
| 155 | Go Explore! | `albion.goexplore` | 1814100216 | 1.0,1.1,1.2,1.3,1.4,1.5,1.6 |
| 161 | Guaranteed Ancient Dangers | `arti.shrinez` | 3566938404 | 1.6 |
| 169 | I will be back | `hailuan.iwbb` | 3400259397 | 1.5,1.6 |
| 174 | Incident Disabler (Continued) | `mlie.incidentdisabler` | 3574116665 | 1.2,1.3,1.4,1.5,1.6 |
| 222 | Mo'Events (Continued) | `mlie.moevents` | 2035143365 | 1.1,1.2,1.3,1.4,1.5,1.6 |
| 243 | Nomad Friendly Quests | `jaeger972.nomadfreindlyquests` | 3616175831 | 1.6 |
| 286 | RimQuest (Continued) | `mlie.rimquest` | 2263331727 | 1.0,1.1,1.2,1.3,1.4,1.5,1.6 |
| 363 | Vanilla Events Expanded | `vanillaexpanded.vee` | 1938420742 | 1.4,1.5,1.6 |
| 378 | Vanilla Quests Expanded - Ancients | `vanillaquestsexpanded.ancients` | 3618306875 | 1.6 |
| 379 | Vanilla Quests Expanded - Cryptoforge | `vanillaquestsexpanded.cryptoforge` | 3461526070 | 1.5,1.6 |
| 380 | Vanilla Quests Expanded - The Generator | `vanillaquestsexpanded.generator` | 3411401573 | 1.5,1.6 |
| 393 | Wandering Caravans | `ogliss.g223.wanderingcaravans` | 2295813916 | 1.0,1.1,1.2,1.3,1.4,1.5,1.6 |
| 419 | Dungeon Pack (Continued) | `mlie.dungeonpack` | 3765496911 | 1.6 |
| 423 | Gerrymon's Misc Props: Dungeon | `gmmp.dungeon` | 3772571876 | 1.6 |
| 504 | RimTalk - Quests | `rimtalk.quests` | 3642675329 | 1.6 |
| 522 | Ancient urban ruins | `xmb.ancienturbanruins.mo` | 3316062206 | 1.5,1.6 |
| 538 | Ancient Ruins All Deconstructible | `meteores.ancienturbanruinsalldeconstructible.aurad` | 3361061429 | 1.5,1.6 |
| 546 | Ancient Urban Ruins Hit Point | `meteores.ancienturbanruinsvanillaloot.aurvl` | 3446989523 | 1.5,1.6 |

### Factions / antagonists (27)

| # | Mod | packageId | Workshop | Versions |
|---:|---|---|---|---|
| 11 | Faction Control (1.4-1.6) | `thereallemon.factioncontrol` | 2882785581 | 1.4,1.5,1.6 |
| 23 | [1.6] CAI 5000 - Advanced AI + Fog Of War (continued) | `krkr.rule56` | 3673768803 | 1.6 |
| 38 | [SR]Factional War (fork) | `sr.modrimworld.factionalwarcontinued` | 3423264477 | 1.2,1.3,1.4,1.5,1.6 |
| 141 | Faction Customizer | `azravos.factioncustomizer` | 3336572602 | 1.3,1.4,1.5,1.6 |
| 142 | Faction Raid Cooldown (Continued) | `mlie.factionraidcooldown` | 3547098393 | 1.2,1.3,1.4,1.5,1.6 |
| 191 | Large Faction Bases (Continued) | `mlie.largefactionbases` | 3257781909 | 1.0,1.1,1.2,1.3,1.4,1.5,1.6 |
| 208 | Mechs and Animals for NPC Factions | `samael.npcmechsandanimals` | 3407831843 | 1.4,1.5,1.6 |
| 218 | MiningCo. Alert speaker (Continued) | `mlie.miningcoalertspeaker` | 3276121703 | 1.1,1.2,1.3,1.4,1.5,1.6 |
| 219 | MiningCo. DrillTurret (Continued) | `mlie.miningcodrillturret` | 3258344832 | 1.1,1.2,1.3,1.4,1.5,1.6 |
| 220 | MiningCo. MMS (Continued) | `mlie.miningcomms` | 3257136373 | 1.1,1.2,1.3,1.4,1.5,1.6 |
| 221 | MiningCo. Spaceship (Continued) | `mlie.miningcospaceship` | 2912642991 | 1.1,1.2,1.3,1.4,1.5,1.6 |
| 228 | More Faction Interaction (Continued) | `mlie.morefactioninteraction` | 2379076640 | 1.0,1.2,1.3,1.4,1.5,1.6 |
| 256 | Powerful AI Integration | `codex.dynamicrolesstoryteller` | 3744421283 | 1.6 |
| 301 | Sensible Factions | `boots.sensiblefactions` | 3531306011 | 1.6 |
| 323 | Storyteller Enhanced (Continued) | `mlie.storytellerenhanced` | 2604427827 | 1.0,1.1,1.2,1.3,1.4,1.5,1.6 |
| 364 | Vanilla Factions Expanded - Insectoids 2 | `oskarpotocki.vfe.insectoid2` | 3309003431 | 1.5,1.6 |
| 365 | Vanilla Factions Expanded - Tribals | `oskarpotocki.vfe.tribals` | 3079786283 | 1.4,1.5,1.6 |
| 404 | Xenotype Spawn Control | `bs.xenotypespawncontrol` | 2891975564 | 1.4,1.5,1.6 |
| 408 | [JDS] StarWars - The Separatist Droid Army | `m3.continued.jangodsoul.starwars.tsda` | 3276499495 | 1.5,1.6 |
| 421 | Faction Territories and Vassalage | `jaeger972.factionterritories` | 3626725895 | 1.6 |
| 451 | Rimsential - Total Control: Continued | `co.uk.epicguru.factionloadout` | 3063465133 | 1.4,1.5,1.6 |
| 489 | Outer Rim - Core | `neronix17.outerrim.core` | 2919227155 | 1.4,1.5,1.6 |
| 497 | Rimesis | `font.rimesis` | 3767949538 | 1.6 |
| 527 | Outer Rim - Droid Depot | `neronix17.outerrim.droiddepot` | 3096501398 | 1.4,1.5,1.6 |
| 528 | Outer Rim - Furniture & Decor | `neronix17.outerrim.furnitureanddecor` | 2919553599 | 1.4,1.5,1.6 |
| 529 | Outer Rim - Galactic Diversity | `neronix17.outerrim.galacticdiversity` | 2980427615 | 1.4,1.5,1.6 |
| 545 | RimTalk Expand: AI Storyteller | `cyberchronicle.rimtalkstoryteller` | 3715752189 | 1.6 |

### Creatures / threats (55)

| # | Mod | packageId | Workshop | Versions |
|---:|---|---|---|---|
| 31 | [MUS]太空基地家具Space Base Furniture | `mingtuwuxiang.spacebasedecorative` | 3523916780 | 1.5,1.6 |
| 41 | AA FancyRats | `armoredampharos.fancyrats` | 2113851330 | 1.1,1.2,1.3,1.4,1.5,1.6 |
| 47 | Ali's Grow All Odyssey Plants | `ali.growodysseyplants` | 3526247608 | 1.6 |
| 49 | Allow Dead Animals | `andrewraphaellukasik.allowdeadanimals` | 2403873031 | 1.6,1.5,1.4,1.3,1.2 |
| 53 | Alpha Mechs | `sarg.alphamechs` | 2973169158 | 1.6,1.5 |
| 58 | Aqued Dredge Aberrations | `aqued.dredgeaberrations` | 3606495707 | 1.6 |
| 64 | Beasts of the Rim (Continued) | `mlie.beastsoftherim` | 2194018641 | 1.0,1.1,1.2,1.3,1.4,1.5,1.6 |
| 72 | Better Kibble | `coldcrow.betterkibble` | 3009060901 | 1.1,1.2,1.3,1.4,1.5,1.6 |
| 91 | Cephaloids | `joe.cephaloids` | 3753477123 | 1.6 |
| 94 | Children Learn on Caravan | `heatherathebyne.childrenlearnoncaravan` | 3497730368 | 1.5,1.6 |
| 97 | Choose Wild Animal Spawns | `mlie.choosewildanimalspawns` | 2564042934 | 1.3,1.4,1.5,1.6 |
| 102 | Crafting Spot Slave Gear | `heatherathebyne.craftingspotslavegear` | 3502196889 | 1.6 |
| 109 | Dark Ages : Beasts and Monsters | `van.beasts` | 3472275628 | 1.5,1.6 |
| 112 | Death Rattle Continued [1.2+] | `troopersmith1.deathrattle` | 2896207870 | 1.3,1.4,1.5,1.6 |
| 122 | Deteriorable Filter | `cometopapa.deteriorated` | 3018050013 | 1.4,1.5,1.6 |
| 138 | Erin's Final Fantasy Animals | `erin.ffanimals` | 2877589761 | 1.4,1.5,1.6 |
| 144 | FancyRats+ | `tyrannidae.fancyratsplus` | 3265419811 | 1.1,1.2,1.3,1.4,1.5,1.6 |
| 152 | Giant Snake (Continued) | `zal.giantsnake` | 3278855253 | 1.5,1.6 |
| 160 | Grimstone : Beasts | `abrolo.grimstone.beasts` | 3535302121 | 1.5,1.6 |
| 166 | Horrors (Continued) | `mlie.horrors` | 3535224844 | 1.6 |
| 178 | Integrated Genes | `turnovus.biotech.integratedgenes` | 2884115974 | 1.4,1.5,1.6 |
| 185 | Jurassic Rimworld - Dinosaurs Only (Continued) | `mlie.jurassicrimworlddinosaursonly` | 3541510004 | 1.6 |
| 190 | Knick Knacks - Let your colonists decorate! | `vaguelysexual.modpackageid.goeshere` | 3595196942 | 1.6 |
| 198 | Little Critters | `tyrannidae.littlecritters` | 3331281387 | 1.4,1.5,1.6 |
| 203 | Martens - Nature's Most Adorable Assassins | `razim.zgfmartens` | 1966193572 | 1.0,1.1,1.2,1.3,1.4,1.5,1.6 |
| 211 | Megafauna | `spino.megafauna` | 1055485938 | 1.3,1.4,1.5,1.6 |
| 235 | Mythic Ages: Megafauna Bestiary | `veterano.mythicages.megafaunabestiary` | 3537788184 | 1.6 |
| 236 | Mythological Creatures! | `wiggler310.mythologicalcreatures` | 3520377015 | 1.6 |
| 250 | Performance - Slower Pawn Tick Rate | `arkymn.slowerpawntickrate` | 3524116050 | 1.6 |
| 272 | Relevant Stats In Description | `mlie.relevantstatsindescription` | 2692669482 | 1.2,1.3,1.4,1.5,1.6 |
| 277 | Rim cockroach | `lingluo.cockroach` | 3196253802 | 1.5,1.6 |
| 302 | Sentience Catalyst Filth Rate Reducer | `flyingsloth.scfilthreducer` | 3525790312 | 1.6 |
| 308 | Skunks | `guppyfacesarecute.skunks` | 3775906812 | 1.6 |
| 315 | Space Worms (Continued) | `mlie.spaceworms` | 2105322804 | 1.0,1.1,1.2,1.3,1.4,1.5,1.6 |
| 319 | Star Wars Animal Collection (Continued) | `mlie.starwarsanimalcollection` | 3497316713 | 1.6 |
| 327 | Tabletop Decorations | `ucp.tabletopdecorations` | 2535771403 | 1.2,1.3,1.4,1.5,1.6 |
| 329 | They! (Giant Ants) | `sapiently.theyatomicmonsters` | 3620253282 | 1.6 |
| 332 | Titans | `titans.fl` | 3572242808 | 1.4,1.5,1.6 |
| 347 | Turrets Shoot Hunting Predators | `archie.turrettargetpatch` | 3221646589 | 1.4,1.5,1.6 |
| 355 | Vanilla Animals Expanded | `vanillaexpanded.vanillaanimalsexpanded` | 2871933948 | 1.4,1.5,1.6 |
| 356 | Vanilla Animals Expanded — Waste Animals | `vanillaexpanded.vaewaste` | 2962126499 | 1.4,1.5,1.6 |
| 377 | Vanilla Plants Expanded - Succulents | `vanillaexpanded.vplantsesucculents` | 2198652536 | 1.4,1.5,1.6 |
| 411 | Alpha Animals | `sarg.alphaanimals` | 1541721856 | 1.5,1.6 |
| 424 | Giant Toads (Continued) | `zal.gianttoads` | 3365223736 | 1.5,1.6 |
| 428 | Insectoids 2 - Isopoda geneline | `who.vfee.isopodageneline` | 3357632382 | 1.5,1.6 |
| 445 | R-Hen-G: Chaos Chickens | `dizzyeevee.rheng` | 3521663802 | 1.6 |
| 464 | VSIE - Rational Trait Development | `stagz.vsierationaltraitdevelopment` | 2916405546 | 1.4,1.5,1.6 |
| 473 | Alpha Animals Patch for Outposts Mines | `daria40k.alphaanimalspatchoutposts` | 2704392053 | 1.3,1.4,1.5,1.6 |
| 474 | Alpha Animals Retextured | `ks.aaretextured` | 3536598972 | 1.0,1.1,1.2,1.3,1.4,1.5,1.6,1.7,1.8,1.9 |
| 485 | LEVIATHANS:SANDWORM | `chezhou.creature.sandworm` | 3713982815 | 1.6 |
| 500 | RimTalk - Expand Literature | `cj.rimtalk.literature` | 3633249209 | 1.6 |
| 510 | RimTalk Mood Reactions | `drati.rimtalkmoodreactions` | 3755539006 | 1.5,1.6 |
| 516 | Shield Generators | `neronix17.shieldgenerators` | 2540563802 | 1.3,1.4,1.5,1.6 |
| 518 | Vanilla Genetics Expanded | `vanillaexpanded.vgeneticse` | 2801160906 | 1.4,1.5,1.6 |
| 549 | Big and Small - Sapient Animals | `redmattis.sapientanimals` | 3505241400 | 1.6 |

### Star Wars content (8)

| # | Mod | packageId | Workshop | Versions |
|---:|---|---|---|---|
| 28 | [JDS] StarWars - Armory | `m3.continued.jangodsoul.starwars.bti` | 3511954303 | 1.5,1.6 |
| 320 | Star Wars Themed Sounds | `starwars.themedsounds` | 3249480517 | 1.0,1.1,1.2,1.3,1.4,1.5,1.6 |
| 553 | Star Wars Xenotypes | `guy762.starwarsxenotypes` | 2915192253 | 1.5,1.6 |
| 557 | Star Wars : The Force - Lightsaber | `lee.theforce.lightsaber` | 3466124712 | 1.5,1.6 |
| 558 | [BTD] Xenotype REMIX: Star Wars | `btd.xenotyperemix.starwars` | 3458153185 | 1.6 |
| 560 | Star Wars KotOR Weapons and Armor | `guy762.kotorweapons` | 2938932438 | 1.5,1.6 |
| 561 | Star Wars KotOR Droids | `guy762.kotordroids` | 3047371944 | 1.5,1.6 |
| 562 | [BTD] Ship Pack: KotOR Ships VGE | `btd.gbp.shippack.kotor.vge` | 3614012898 | 1.6 |

### Hazard / environment (8)

| # | Mod | packageId | Workshop | Versions |
|---:|---|---|---|---|
| 69 | Better Explosions | `nephlite.advexplosions` | 2572683272 | 1.3,1.4,1.5,1.6 |
| 104 | Custom Gas Types | `greg.customgastypes` | 3756399441 | 1.6 |
| 126 | Dubs Bad Hygiene - Thirst | `dubwise.dubsbadhygiene.thirst` | 2582878800 | 1.3,1.4,1.5,1.6 |
| 127 | Dubs Bad Hygiene Lite | `dubwise.dubsbadhygiene.lite` | 2570319432 | 1.3,1.4,1.5,1.6 |
| 139 | Extra Explosion Effects | `keshash.extraexplosioneffects` | 3066208882 | 1.4,1.5,1.6 |
| 164 | High Tech Helmets Give Tox Gas Resistance | `ael.tua.helmetsaddtoxresistance` | 3503847744 | 1.5,1.6 |
| 261 | Psilocap Cultivation | `laureeeeeeeeeeeeeeen.shrooms` | 3523760036 | 1.6 |
| 444 | Psyshrooms | `lambda.psykshroom` | 3280268952 | 1.5,1.6 |

### Storage / hauling / QoL / UI (55)

| # | Mod | packageId | Workshop | Versions |
|---:|---|---|---|---|
| 27 | [HMC]Wall Furniture | `hmc.wall.furniture` | 3533512691 | 1.6 |
| 30 | [LC] Selectable Sculpture Graphic | `lc.tammybee.selectablesculpturegraphic` | 3239359525 | 1.0,1.1,1.2,1.3,1.4,1.5,1.6 |
| 36 | [sbz] Fridge | `sbz.neatstoragefridge` | 3486264784 | 1.5,1.6 |
| 42 | Achtung! | `brrainz.achtung` | 730936602 | 1.0,1.1,1.2,1.3,1.4,1.5,1.6 |
| 43 | Adaptive Ideology Storage | `adaptive.ideology.storage` | 3301337278 | 1.4,1.5,1.6 |
| 44 | Adaptive Primitive Storage | `adaptive.primitivestorage` | 3400037215 | 1.5,1.6 |
| 45 | Adaptive Simple Storage | `adaptive.simplestorage` | 3297307747 | 1.4,1.5,1.6 |
| 50 | Allow Tool | `unlimitedhugs.allowtool` | 761421485 | 1.0,1.1,1.2,1.3,1.4,1.5,1.6 |
| 62 | Auto links | `automatic.autolinks` | 2059389912 | 1.1,1.2,1.3,1.4,1.5,1.6 |
| 63 | Auto Strip on Haul | `fuu.autostriponhaul` | 2560725133 | 1.3,1.4,1.5,1.6 |
| 73 | Better ModMismatch Window | `madeline.modmismatchformatter` | 1872244972 | 1.0,1.1,1.2,1.3,1.4,1.5,1.6 |
| 76 | Better Workbench Management | `falconne.bwm` | 935982361 | 1.0,1.1,1.2,1.3,1.4,1.5,1.6 |
| 77 | Betures | `businburg.businfeatures` | 3530082693 | 1.6 |
| 87 | Build From Inventory - Continued | `memegoddess.buildfrominventory` | 3534185281 | 1.1,1.2,1.3,1.4,1.5,1.6 |
| 89 | Camera+ | `brrainz.cameraplus` | 867467808 | 1.0,1.1,1.2,1.3,1.4,1.5,1.6 |
| 116 | Designator Shapes | `merthsoft.designatorshapes` | 1235181370 | 1.1,1.2,1.3,1.4,1.5,1.6 |
| 118 | Destroy Item | `garwel.destroyitem` | 2423311270 | 1.2,1.3,1.4,1.5,1.6 |
| 129 | Dubs Mint Menus | `dubwise.dubsmintmenus` | 1446523594 | 1.0,1.1,1.2,1.3,1.4,1.5,1.6 |
| 130 | Dubs Mint Minimap | `dubwise.dubsmintminimap` | 1662119905 | 1.0,1.1,1.2,1.3,1.4,1.5,1.6 |
| 147 | Float Sub-Menus | `kathanon.floatsubmenu` | 2864015430 | 1.6,1.5,1.4,1.3 |
| 179 | Interaction Bubbles | `jaxe.bubbles` | 1516158345 | 1.3,1.4,1.5,1.6 |
| 181 | Invisible Conduit Continued | `glitchgoblin.invisibleconduitcont` | 3506645273 | 1.0,1.1,1.2,1.3,1.4,1.6 |
| 188 | Just Put It Over There | `mlie.justputitoverthere` | 2856471776 | 1.3,1.4,1.5,1.6 |
| 194 | LED Lights Strip | `noneobsidiaexpansion.ledlightsstrip` | 3476135064 | 1.5,1.6 |
| 195 | LightsOut | `juanlopez2008.lightsout` | 2584269293 | 1.3,1.4,1.5,1.6 |
| 246 | Numbers | `mehni.numbers` | 1414302321 | 1.0,1.1,1.2,1.3,1.4,1.5,1.6 |
| 252 | Perspective: Buildings (Continued) | `mlie.perspectivebuildings` | 3346955193 | 1.3,1.4,1.5,1.6 |
| 253 | Pick Up And Haul | `mehni.pickupandhaul` | 1279012058 | 1.0,1.1,1.2,1.3,1.4,1.5,1.6 |
| 262 | Quality Affects HP | `fluxilis.germanquality` | 2898409109 | 1.6,1.5,1.4 |
| 263 | Quality Colors (Continued) | `dawnsglow.qualcolor` | 3513846773 | 1.2,1.3,1.4,1.5,1.6 |
| 273 | Replace Stuff - Continued | `memegoddess.replacestuff` | 3526354009 | 1.1,1.2,1.3,1.4,1.5,1.6 |
| 283 | RimFridge: Now with Shelves! | `rimfridge.kv.rw` | 2898411376 | 1.6,1.5,1.4 |
| 284 | RimHUD | `jaxe.rimhud` | 1508850027 | 1.1,1.2,1.3,1.4,1.5,1.6 |
| 285 | RIMMSqol | `malteschulze.rimmsqol` | 1084452457 | 1.0,1.1,1.2,1.3,1.4,1.5,1.6 |
| 296 | Search and Destroy (Continued) | `memegoddess.searchanddestroy` | 3232242247 | 1.0,1.1,1.2,1.3,1.4,1.5,1.6 |
| 297 | Search Option | `hellrevenger.searchoption` | 3508618083 | 1.5,1.6 |
| 313 | Snap Out! | `weilbyte.snapout` | 1319782555 | 1.1,1.0,1.2,1.3,1.4,1.5,1.6 |
| 317 | Stackable Chunks | `elshender.stackablechunks` | 3222674854 | 1.0,1.1,1.2,1.3,1.4,1.5,1.6 |
| 322 | Storage Memory | `karshou.storagememory` | 3543261305 | 1.6 |
| 324 | Stronger Quality Scaling (1.6) | `kas.strongerscaling` | 1206001612 | 1.6,1.5,1.4,1.3,1.2,1.1,1.0 |
| 325 | Stuff on Tables Forked | `moistestwhale.stuffontablesforked` | 3289533061 | 1.3,1.4,1.5,1.6 |
| 344 | Triumphant Research | `ferny.triumphantresearch` | 3647618250 | 1.6 |
| 349 | Undraft After Tucking Forked | `amagicallime.undraftaftertucking` | 3526748256 | 1.1,1.2,1.3,1.4,1.5,1.6 |
| 352 | Utility Columns | `nephlite.orbitaltradecolumn` | 2013476665 | 1.5,1.6 |
| 398 | What's Missing? | `revolus.whatsmissing` | 3231090162 | 1.4,1.5,1.6 |
| 399 | What's That Mod | `co.uk.epicguru.whatsthatmod` | 2258431182 | 1.1,1.2,1.3,1.4,1.5,1.6 |
| 402 | Work Tab | `fluffy.worktab` | 3453549086 | 1.5,1.6 |
| 429 | Invisible Display Case Continued | `icepickgma.invisibledisplaycase` | 3546566196 | 1.5,1.6 |
| 431 | Keyz' Allow Utilities | `keyz182.keyzallowutilities` | 3524716849 | 1.6 |
| 434 | LWM's Deep Storage | `lwm.deepstorage` | 3532608331 | 1.0,1.1,1.2,1.3,1.4,1.5,1.6 |
| 439 | Nice Research Tab | `andromeda.niceresearchtab` | 3773496046 | 1.6 |
| 440 | Pick Up And Haul - Shared Storage Access | `sugarcube.puahsharedstorage` | 3774922633 | 1.6 |
| 454 | Searchable Menus | `kathanon.searchablemenus` | 2928608119 | 1.4,1.5,1.6 |
| 465 | WallStuff | `arcjc007.wallstuff` | 1994340640 | 1.1,1.2,1.3,1.4,1.5,1.6 |
| 517 | Simple sidearms | `petetimessix.simplesidearms` | 927155256 | 1.0,1.1,1.2,1.3,1.4,1.5,1.6 |

### Trade / economy (16)

| # | Mod | packageId | Workshop | Versions |
|---:|---|---|---|---|
| 22 | [1.1]TO[1.6]MultipleTraders | `04.23.2020` | 2070709529 | 1.1,1.2,1.3,1.4,1.5,1.6 |
| 29 | [KV] Call Trade Ships (Continued) | `zal.calltradeships` | 3722921543 | 1.6 |
| 74 | Better Traders | `jm.bettertraders` | 2012774042 | 1.2,1.3,1.4,1.5,1.6 |
| 184 | Jewelry | `kikohi.jewelry` | 3203280763 | 1.4,1.5,1.6 |
| 265 | Raid Protection Fee | `leo.raidprotectionfee` | 3650927927 | 1.5,1.6 |
| 303 | Settlements buy more | `victor.buymore` | 2886202254 | 1.4,1.5,1.6 |
| 314 | Social Experience from Trade | `krelinos.socialexpfromtrade` | 3400608063 | 1.6,1.5,1.4,1.3 |
| 335 | Trade Ships Drop Spot | `smashphil.dropspot` | 1969732297 | 1.0,1.1,1.2,1.3,1.4,1.5,1.6 |
| 336 | Trade UI Revised | `hobtook.tradeui` | 2683622537 | 1.3,1.4,1.5,1.6 |
| 337 | Tradeable Trinkets (Continued) | `mlie.tradeabletrinkets` | 2966786575 | 1.2,1.3,1.4,1.5,1.6 |
| 338 | Trader ships | `automatic.traderships` | 2046222331 | 1.1,1.2,1.3,1.4,1.5,1.6 |
| 339 | TraderGen | `joseasoler.tradergen` | 3525848981 | 1.3,1.4,1.5,1.6 |
| 343 | Tribute Demand | `geojak.tributedemand` | 3711373966 | 1.6 |
| 426 | GTG Trader Core | `teiwaz.gtgtradercore` | 3682209120 | 1.6 |
| 470 | [GTG]Traders Accept All Junk Gear | `teiwaz.taajg` | 3729570505 | 1.6 |
| 471 | [GTG]Traders Accept Chunks & Corpses | `teiwaz.tacac` | 3756658373 | 1.6 |

### Vehicles / caravans / settlements (14)

| # | Mod | packageId | Workshop | Versions |
|---:|---|---|---|---|
| 90 | Caravan Adventures | `iforgotmysocks.caravanadventures` | 2558957509 | 1.2,1.3,1.4,1.5,1.6 |
| 153 | Giddy-Up 2 - Continued | `memegoddess.giddyup` | 3674332861 | 1.4,1.5,1.6 |
| 177 | Instant Caravan | `ferny.easycaravanformation` | 3165744287 | 1.4,1.5,1.6 |
| 192 | Large Outpost (Continued) | `zal.largeoutpost` | 3337099675 | 1.5,1.6 |
| 376 | Vanilla Outposts Expanded | `vanillaexpanded.outposts` | 2688941031 | 1.6,1.4,1.5 |
| 391 | Visit Settlements | `ninagoblin.visitsettlements` | 3535955435 | 1.6 |
| 392 | Walk the World | `addvans.walktheworld` | 3546716725 | 1.6 |
| 394 | WASDed Pawn | `addvans.wasdedpawn` | 3471835151 | 1.5,1.6 |
| 405 | Yayo's Caravan (Continued) | `mlie.yayoscaravan` | 2886919774 | 1.3,1.4,1.5,1.6 |
| 460 | Vanilla Mining Outpost Patch | `kuhlyus.modpatch.vanillaoutpost` | 2968491314 | 1.4,1.5,1.6 |
| 461 | Vanilla Outposts Expanded: Additional Outposts | `mrhydralisk.voeadditionaloutposts` | 2873841790 | 1.3,1.4,1.5,1.6 |
| 463 | Vanilla Vehicles Expanded | `oskarpotocki.vanillavehiclesexpanded` | 3014906877 | 1.4,1.5,1.6 |
| 477 | Alpha Vehicles - Neolithic | `sarg.alphavehiclesneolithic` | 3028675048 | 1.6,1.5 |
| 535 | VVE - Deconstructable Vehicles Junk | `farxmai2.vanilladeconstructablevehicles` | 3108171008 | 1.4,1.5,1.6 |

### Social / romance / slavery / prisoners (36)

| # | Mod | packageId | Workshop | Versions |
|---:|---|---|---|---|
| 33 | [RF] Rumor Has It.... (Continued) | `mlie.rfrumorhasit` | 2013940581 | 1.0,1.1,1.2,1.3,1.4,1.5,1.6 |
| 34 | [RH2] CPERS: Arrest Here! | `rh2.cpers.arrest.here` | 2563157350 | 1.5,1.4,1.3,1.2,1.6 |
| 39 | [SYR] More Slaves (Continued) | `mlie.syrmoreslaves` | 3361231919 | 1.0,1.1,1.2,1.3,1.4,1.5,1.6 |
| 67 | Better Beggars (Continued) | `mlie.betterbeggars` | 3006899215 | 1.3,1.4,1.5,1.6 |
| 68 | Better Crossbreeding | `dizzyeevee.bettercrossbreeding` | 3520675842 | 1.6 |
| 70 | Better Growth Moments | `arkymn.bettergrowthmoments` | 3642805464 | 1.6 |
| 86 | Breeding Ritual | `gulmadred.breedingritual` | 3772996961 | 1.6 |
| 173 | Imprisonment On The Go! (Continued) | `agentblac.makepawnsprisoners` | 3358620558 | 1.3,1.4,1.5,1.6 |
| 189 | Keep Converting | `linnun.keepconverting` | 3461478214 | 1.5,1.6 |
| 230 | More Slavery Stuff | `garryflowers.moreslaverystuff` | 2896845138 | 1.4,1.5,1.6 |
| 254 | Polyamory Beds (Vanilla Edition) | `meltup.polyamorybeds.vanilla` | 3276496684 | 1.1,1.2,1.3,1.4,1.5,1.6 |
| 260 | Prisoners Should Fear Turrets | `mlie.prisonersshouldfearturrets` | 2602436826 | 1.1,1.2,1.3,1.4,1.5,1.6 |
| 267 | RandomGrowthChoices (Continued) | `zal.randomgrowthchoices` | 3413983862 | 1.5,1.6 |
| 287 | RimSteal | `stealmod.author` | 3722523355 | 1.6 |
| 288 | RimTraits - General Traits | `sierra.rt.generaltraits` | 2206957172 | 1.1,1.2,1.3,1.4,1.5,1.6 |
| 291 | Romance & Intimacy On The Rim | `mianreplicate.romanceandintimacyontherim` | 3612563959 | 1.6 |
| 300 | Sensible Bed Ownership | `sensiblebedownership.1trickpwnyta` | 3328702448 | 1.5,1.6 |
| 309 | Slave Outfits [1.6] | `usgiyi.slaveoutfits` | 1522429439 | 1.1,1.2,1.3,1.4,1.5,1.6 |
| 310 | Slave Rebellions Improved (Continued) | `mlie.slaverebellionsimproved` | 3259932217 | 1.3,1.4,1.5,1.6 |
| 321 | Stealing Mod | `amoruch.rimworldstealingmod` | 3775811814 | 1.6 |
| 326 | Stylized Slave Collars and Headgears | `gerrymon.stylizedslavecollar` | 3040600773 | 1.4,1.5,1.6 |
| 330 | Tickle Your Pawn | `tickleyourpawn.core` | 3721622218 | 1.6 |
| 333 | Torment Master | `vlvop.tormentmaster.expansion` | 3746663772 | 1.6 |
| 334 | Torture Pod | `tsa.torturepod` | 3572173918 | 1.6 |
| 350 | Universal Pregnancy | `universalpregnancy.1trickpwnyta` | 3303758779 | 1.5,1.6 |
| 351 | UnlimitedNuzzles | `doomdrvk.unlimitednuzzles` | 3508337433 | 1.5,1.6 |
| 385 | Vanilla Social Interactions Expanded | `vanillaexpanded.vanillasocialinteractionsexpanded` | 2439736083 | 1.4,1.5,1.6 |
| 387 | Vanilla Traits Expanded | `vanillaexpanded.vanillatraitsexpanded` | 2296404655 | 1.4,1.5,1.6 |
| 443 | Prison Labor | `avius.prisonlabor` | 1899474310 | 1.0,1.1,1.2,1.3,1.4,1.5,1.6 |
| 453 | Romance On The Rim | `telardo.romanceontherim` | 2654432921 | 1.3,1.4,1.5,1.6 |
| 455 | Simple Slavery Collars | `tribeagle.simpleslaverycollars` | 2557274194 | 1.3,1.4,1.5,1.6 |
| 466 | Way Better Romance | `divinederivative.romance` | 2877731755 | 1.4,1.5,1.6 |
| 491 | Prisoner Realism | `legator.prisonerrealism` | 3760196312 | 1.6 |
| 525 | Intimacy - Friends n' Lovers | `lovelydovey.sex.witheuterpe` | 3498422643 | 1.6 |
| 542 | Intimacy - Gender Works | `lovelydovey.sex.withrosaline` | 3534254491 | 1.6 |
| 543 | Intimacy - Socio Butterfly | `lovelydovey.recreation.witheuterpe` | 3630896210 | 1.6 |

### Ideology / ritual / religion (24)

| # | Mod | packageId | Workshop | Versions |
|---:|---|---|---|---|
| 24 | [AP] Hunting Meme | `ap.huntingmeme` | 3535691822 | 1.3,1.4,1.5,1.6 |
| 26 | [Dizzy] Candles and Hidden Meditation | `dizzy.candlesandmeditation` | 2569910895 | 1.1,1.2,1.3,1.4,1.5,1.6 |
| 54 | Alpha Memes | `sarg.alphamemes` | 2661356814 | 1.5,1.6 |
| 107 | Cybranian - Ideology Virtues | `dimonsever000.ideologyvirtues` | 3459205505 | 1.5,1.6 |
| 108 | Dance Party Custom Music | `east.dancepartycustommusic` | 3752711168 | 1.6 |
| 133 | Effigys - Terror Spikes | `yourname.effigys.mod` | 3647930333 | 1.5,1.6 |
| 136 | Epochs - Incense | `det.epochsincense` | 3072579620 | 1.4,1.5,1.6 |
| 137 | Epochs - Pyrinth | `det.epochspyrinth` | 3336544632 | 1.5,1.6 |
| 170 | Ideology Scavenger Role | `amegakull.scvrole` | 3565039115 | 1.5,1.6 |
| 171 | Ideology symbols as Ideograms | `kxp.ideosymbolsasideograms` | 3199358915 | 1.4,1.5,1.6 |
| 172 | Ideology: More Precepts | `llunak.moreprecepts` | 2559533848 | 1.3,1.4,1.5,1.6 |
| 242 | No Random Apparel on Ideology Edit | `edern.norandomapparelonideoedit` | 2669243201 | 1.3,1.4,1.5,1.6 |
| 249 | Party Expansion | `sysmy.partyexpansion` | 3645797292 | 1.6 |
| 251 | Persistent Precepts | `alleykat.persistentprecepts` | 2944765939 | 1.4,1.5,1.6 |
| 257 | Precepts and Memes (Continued) | `mlie.preceptsandmemes` | 2894625496 | 1.3,1.4,1.5,1.6 |
| 373 | Vanilla Ideology Expanded - Hats and Rags | `vanillaexpanded.viehar` | 2567387768 | 1.4,1.5,1.6 |
| 374 | Vanilla Ideology Expanded - Relics and Artifacts | `vanillaexpanded.ideo.relicsandartifacts` | 2564895018 | 1.4,1.5,1.6 |
| 400 | Wing's Meaningful Parties | `winggar.meaningfulparties` | 3504909699 | 1.5,1.6 |
| 433 | Linkin Park Party Music (Party Expansion) | `sysmy.pelinkinpark` | 3647834609 | 1.6 |
| 438 | More Ritual Rewards | `sinnamon.moreritualrewards` | 2582489076 | 1.3,1.5,1.6 |
| 442 | Precepts and Memes - Rituals module (Continued) | `mlie.preceptsandmemesritualsmodule` | 2894628849 | 1.3,1.4,1.5,1.6 |
| 509 | RimTalk Ideology Patch | `leyley.rimtalkideologypatch` | 3724752618 | 1.5,1.6 |
| 519 | Vanilla Ideology Expanded - Memes and Structures | `vanillaexpanded.vmemese` | 2636329500 | 1.4,1.5,1.6 |
| 526 | More Ritual Seats | `toastyman.moreritualseats` | 3411913071 | 1.6,1.5 |

### Apparel / faces / furniture / decoration (46)

| # | Mod | packageId | Workshop | Versions |
|---:|---|---|---|---|
| 14 | Vanilla Backgrounds Expanded | `vanillaexpanded.backgrounds` | 2775017012 | 1.4,1.5,1.6 |
| 32 | [NL] Facial Animation - WIP | `nals.facialanimation` | 1635901197 | 1.0,1.1,1.2,1.3,1.4,1.5,1.6 |
| 35 | [RH2] Uncle Boris' - Used Furniture | `cp.uncle.boris.used.furniture` | 2563508405 | 1.3,1.4,1.5,1.6 |
| 60 | Astronomy Style Pack | `asp.halituisamaricanous` | 3522312454 | 1.3,1.4,1.5,1.6,1.7,1.8,1.9,2.0 |
| 65 | BestApparel | `io.github.relvl.rimworld.bestapparel` | 2946961833 | 1.4,1.5,1.6 |
| 83 | Biotech Mechanoid Retexture | `el.biotechmechrt` | 3164022710 | 1.4,1.5,1.6 |
| 101 | Cozy Fires | `cozyfire.velcroboy333` | 2390924647 | 1.1,1.2,1.3,1.4,1.5,1.6 |
| 125 | Dub's Paint Shop | `dubwise.dubspaintshop` | 1579516669 | 1.0,1.1,1.2,1.3,1.4,1.5,1.6 |
| 149 | Fortifications - Industrial | `aoba.fortress.industrial` | 2561619583 | 1.3,1.4,1.5,1.6 |
| 150 | Fortifications - Neolithic | `aoba.fortress.neolithic` | 2385960678 | 1.2,1.3,1.4,1.5,1.6 |
| 156 | Graffiti Mod (Continued) | `mlie.graffitimod` | 2986996933 | 1.3,1.4,1.5,1.6 |
| 193 | Layered Apparel | `costel.layeredapparel` | 3632480044 | 1.6 |
| 209 | Medieval Melee Sounds | `bonible.medievalmeleesounds` | 2962064646 | 1.4,1.5,1.6 |
| 210 | Medieval Signs | `mewn.medievalsigns` | 3488857567 | 1.5,1.6 |
| 229 | More Sculpture | `bichang.moresculpture` | 1612316880 | 1.0,1.1,1.2,1.3,1.4,1.5,1.6 |
| 232 | More Vanilla Textures | `tidal.morevanilla.textures` | 2707120862 | 1.3,1.4,1.5,1.6 |
| 304 | Shavius's Medieval Flavour Pack | `shavius.medieval.flavour` | 2767940226 | 1.2,1.3,1.4,1.5,1.6 |
| 306 | Signs and Comments | `dark.signs` | 3281950776 | 1.6,1.5,1.4,1.3,1.2 |
| 307 | Simple Cape and Hood Retexture | `stokes.simplehoodcape` | 3543386604 | 1.6 |
| 318 | Standalone Hot Spring | `balistafreak.standalonehotspring` | 2205980094 | 1.1,1.2,1.3,1.4,1.5,1.6 |
| 342 | Tribal Furniture | `xercaine.tribal.furniture` | 3671245310 | 1.6 |
| 353 | Van's Retexture : Melee Weapons | `sirvan.mwretextured` | 2922441211 | 1.4,1.5,1.6 |
| 354 | Van's Retexture : Steel | `sirvan.steelretexture` | 2955560866 | 1.4,1.5,1.6 |
| 357 | Vanilla Apparel Expanded | `vanillaexpanded.vappe` | 1814987817 | 1.4,1.5,1.6 |
| 358 | Vanilla Apparel Expanded — Accessories | `vanillaexpanded.vaeaccessories` | 2521176396 | 1.4,1.5,1.6 |
| 366 | Vanilla Furniture Expanded | `vanillaexpanded.vfecore` | 1718190143 | 1.4,1.5,1.6 |
| 367 | Vanilla Furniture Expanded - Art | `vanillaexpanded.vfeart` | 1968134023 | 1.4,1.5,1.6 |
| 369 | Vanilla Furniture Expanded - Medical Module | `vanillaexpanded.vfemedical` | 1718191613 | 1.6,1.4,1.5 |
| 370 | Vanilla Furniture Expanded - Production | `vanillaexpanded.vfeproduction` | 1880253632 | 1.4,1.5,1.6 |
| 371 | Vanilla Furniture Expanded - Props and Decor | `vanillaexpanded.vfepropsanddecor` | 2102143149 | 1.4,1.5,1.6 |
| 396 | Weapon Racks | `aelanna.weaponracks` | 2788630748 | 1.3,1.4,1.5,1.6 |
| 401 | Wirehead Style | `tleno.wireheadstyle` | 3311183008 | 1.4,1.5,1.6 |
| 410 | [NL] Facial Animation - Experimentals | `nals.facialanimationexperimentals` | 2581693737 | 1.3,1.4,1.5,1.6 |
| 415 | Character Editor Retextured | `neronix17.retexture.charactereditor` | 2855844396 | 1.3,1.4,1.5,1.6 |
| 420 | Dynamic AI Sculptures | `codex.dynamicaisculptures` | 3753149685 | 1.6 |
| 427 | Head Set For [NL]Facial Animation | `ab.hoffa` | 2975760383 | 1.4,1.5,1.6 |
| 483 | Genetic Biotech for Facial Animation | `sd.fa.geneticheadsbiotech` | 3501317537 | 1.6,1.5 |
| 492 | Reel's Facial Animation Textures | `reel.facialanims` | 3118315633 | 1.4,1.5,1.6 |
| 511 | RimTalk StyleExpand | `rimtalk.styleexpand` | 3694936738 | 1.5,1.6 |
| 521 | Adjustments for Reel's Facial Animation Textures | `sd.fa.reelsadjustments` | 3429452043 | 1.6,1.5,1.4,1.3,1.2,1.1,1.0 |
| 534 | Vanilla Textures Expanded - [NL] Facial Animation | `vanillaexpanded.vtexe.facialanims` | 2816938779 | 1.7,1.6,1.5,1.4,1.3,1.2,1.1,1.0 |
| 537 | Adjustments for Vanilla Textures Expanded - [NL] Facial Animation | `sd.fa.vteadjustments` | 3532050275 | 1.6,1.5 |
| 539 | Beard Adjustment | `kem.beardadjustment` | 2880669781 | 1.6,1.5,1.4 |
| 552 | Rustic Meal Retexture | `jelheb.rusticmealretexture` | 3453364177 | 1.4,1.5,1.6 |
| 554 | Facial Animation Compatability Project | `danzinagri.facialanimationcompatabilityproject` | 3585705988 | 1.6 |
| 555 | Genetic Mods for Facial Animation | `sd.fa.geneticheadsmods` | 3501317734 | 1.6,1.5 |

### Audio / music (7)

| # | Mod | packageId | Workshop | Versions |
|---:|---|---|---|---|
| 55 | Ambient Rim | `swablu.ambience` | 3158997430 | 1.4,1.5,1.6 |
| 61 | AuthenticTantrumNoises | `kshtantrumsounds.mod` | 2839608123 | 1.3,1.4,1.5,1.6 |
| 197 | LiquidSFX | `dorbo.watersfx` | 3758773902 | 1.6 |
| 213 | Metal Pipe | `flangopink.metalpipe` | 2960013295 | 1.4,1.5,1.6 |
| 214 | Metal Pipe Horseshoe Replacement | `flangopink.metalpipehorseshoe` | 2961064957 | 1.4,1.5,1.6 |
| 269 | Realistic Human Sounds (Continued) | `mlie.realistichumansounds` | 3497264525 | 1.6 |
| 289 | RimTunes | `depscian.rimtunes` | 3399705740 | 1.5,1.6 |

### Weapons / combat (17)

| # | Mod | packageId | Workshop | Versions |
|---:|---|---|---|---|
| 117 | Destiny Exotic Weapons | `milkwater.destinymod` | 3496200631 | 1.5,1.6 |
| 134 | Enable Oversized Weapons | `carnysenpai.enableoversizedweapons` | 2543371889 | 1.2,1.3,1.4,1.5,1.6 |
| 146 | Fists Aren't Made of Steel | `aelanna.fistnerf` | 2845980214 | 1.3,1.4,1.5,1.6 |
| 162 | Gunplay | `automatic.gunplay` | 2034896549 | 1.1,1.2,1.3,1.4,1.5,1.6 |
| 168 | Hunting Traps | `hazn.huntingtraps` | 3219487356 | 1.4,1.5,1.6 |
| 176 | Injured Carry | `haecriver.injuredcarry` | 2413690575 | 1.2,1.3,1.4,1.5,1.6 |
| 182 | Ion Weaponry (Continued) | `zal.ionweaponry` | 3532877485 | 1.6 |
| 248 | Out of Combat ReBoost | `coolzie.oocreboost` | 3527970878 | 1.6 |
| 266 | Raider Swarm Compression | `ingendum.raiderswarmcompression` | 3515541126 | 1.6 |
| 348 | Ugh You Got Me | `marvinkosh.ughyougotme` | 1542424705 | 1.0,1.1,1.2,1.3,1.4,1.5,1.6 |
| 388 | Vanilla Weapons Expanded | `vanillaexpanded.vwe` | 1814383360 | 1.4,1.5,1.6 |
| 389 | Vanilla Weapons Expanded - Makeshift | `vanillaexpanded.vwems` | 2419690698 | 1.4,1.5,1.6 |
| 397 | WeaponStats | `bodlosh.weaponstats` | 974066449 | 1.0,1.1,1.2,1.3,1.4,1.5,1.6 |
| 435 | Makeshift: Re-Examined | `smxrez.makeshiftreexamined` | 3455187943 | 1.5,1.6 |
| 468 | Yayo's Combat 3 (Continued) | `mlie.yayoscombat3` | 2854006492 | 1.1,1.2,1.3,1.4,1.5,1.6 |
| 550 | Big and Small - Weapons | `redmattis.bigweapons` | 3105907309 | 1.4,1.5,1.6 |
| 551 | Melee Animation | `co.uk.epicguru.meleeanimation` | 2944488802 | 1.4,1.5,1.6 |

### Xenotypes / genes (16)

| # | Mod | packageId | Workshop | Versions |
|---:|---|---|---|---|
| 119 | Det's Xenotypes - Boglegs | `det.boglegs` | 3146564944 | 1.4,1.5,1.6 |
| 120 | Det's Xenotypes - Brawnum | `det.brawnum` | 3429572581 | 1.5,1.6 |
| 121 | Det's Xenotypes - Keshig | `det.keshig` | 3376864722 | 1.5,1.6 |
| 151 | Genetic Drift 1.6 | `masstell.geneticdrift16` | 3522332727 | 1.4,1.5,1.6 |
| 154 | Glowing eyes genes | `lts.geg` | 3023336989 | 1.4,1.5,1.6 |
| 165 | Highborn Xenotype | `elsov.highborn` | 3380776687 | 1.5,1.6 |
| 167 | Humanoid Alien Races | `erdelf.humanoidalienraces` | 839005762 | 0.19,1.0,1.1,1.2,1.3,1.4,1.5,1.6 |
| 241 | No Missing Gene Icons | `mlie.nomissinggeneicons` | 2890795292 | 1.4,1.5,1.6 |
| 255 | Posthuman Drift Core Mod | `xylthixlm.races.core` | 3521814323 | 1.6 |
| 381 | Vanilla Races Expanded - Genie | `vanillaracesexpanded.genie` | 2901424072 | 1.4,1.5,1.6 |
| 382 | Vanilla Races Expanded - Saurid | `vanillaracesexpanded.saurid` | 2880990495 | 1.4,1.5,1.6 |
| 383 | Vanilla Races Expanded - Starjack | `vanillaracesexpanded.starjack` | 3531912428 | 1.6 |
| 441 | Posthuman Drift Titan Xenotype | `xylthixlm.races.titan` | 3540820354 | 1.6 |
| 475 | Alpha Genes | `sarg.alphagenes` | 2891845502 | 1.6,1.5 |
| 490 | Outland - Genetics | `neronix17.outland.genetics` | 2910172297 | 1.4,1.5,1.6 |
| 540 | Big and Small - Genes & More | `redmattis.bigsmall.core` | 2920751126 | 1.4,1.5,1.6 |

### LLM / agent / authoring tools (28)

| # | Mod | packageId | Workshop | Versions |
|---:|---|---|---|---|
| 10 | Cherry Picker | `owlchemist.cherrypicker` | 3521312241 | 1.3,1.4,1.5,1.6 |
| 93 | Character Editor | `void.charactereditor` | 1874644848 | 1.0,1.1,1.2,1.3,1.4,1.5,1.6 |
| 131 | Dubs Performance Analyzer | `dubwise.dubsperformanceanalyzer.steam` | 2038874626 | 1.2,1.3,1.4,1.5,1.6 |
| 199 | Log After Def Error (Continued) | `mlie.logafterdeferror` | 3550944748 | 1.5,1.6 |
| 279 | RimAI Core (BETA) | `kilokio.rimai.core` | 3560404184 | 1.6 |
| 281 | RimBridgeServer | `brrainz.rimbridgeserver` | 3727949765 | 1.6 |
| 295 | Scenario Amender [1.5 - 1.6] | `katana.scenarioamender` | 3236547440 | 1.5,1.6 |
| 316 | SpeakUp | `jpt.speakup` | 2502518544 | 1.2,1.3,1.4,1.5,1.6 |
| 452 | RimTalk | `cj.rimtalk` | 3551203752 | 1.5,1.6 |
| 481 | Custom Room Names - RimTalk Addon | `costel.customroomnames.rimtalkaddon` | 3626983869 | 1.6 |
| 498 | RimTalk - Expand Actions Core | `zruic.expand.action` | 3661055729 | 1.6 |
| 499 | RimTalk - Expand Dialogue | `zruic.expand.dialogue` | 3662962455 | 1.6 |
| 501 | RimTalk - Expand Memory | `cj.rimtalk.expandmemory` | 3608181242 | 1.5,1.6 |
| 502 | RimTalk - Expand Thoughts | `zruic.expand.thoughts` | 3661175034 | 1.6 |
| 503 | RimTalk - Expand Toddlers | `cj.rimtalk.toddlers` | 3659064387 | 1.6 |
| 505 | RimTalk Context Upgrade | `wuren.rimtalkcontextupgrade` | 3641774579 | 1.6 |
| 506 | RimTalk Dialogue Patch | `neachi.rimtalkdialoguepatch` | 3631632728 | 1.6 |
| 507 | RimTalk DynamicColors 边缘世谭-言出多彩 | `maiya.rimtalkdynamiccolors` | 3628773219 | 1.6 |
| 508 | RimTalk Event+ | `saltgin.rimtalkeventmemory` | 3612632140 | 1.5,1.6 |
| 512 | RimTalk-MemoryDigest | `oceantest7.rimtalk.memory` | 3726488698 | 1.6 |
| 513 | RimTalk-PromptCleaner | `oceantest6.rimtalk.promptcleaner` | 3630607068 | 1.6 |
| 514 | RimTalk.DisplayOptimization | `oceantest5.rimtalk.enhance` | 3629456304 | 1.6 |
| 515 | RimTalk: Persona Director | `rp.rimtalk.personadirector` | 3619548407 | 1.6 |
| 530 | RimTalk - Expand Actions | `sanguo.rimtalk.expandactions` | 3628755033 | 1.4,1.5,1.6 |
| 531 | RimTalk - Expand Relation | `zruic.expand.relation` | 3661493651 | 1.6 |
| 532 | RImtalk Expand : News, Expert and Colony Chronicle | `cyberchronicle.rimtalkexperts` | 3714540653 | 1.6 |
| 533 | RimTalk-Message Filter | `assssssqwww.feelingfilter` | 3697500330 | 1.6 |
| 556 | Rim Control | `lordfelix.rimcontrol` | 3774299554 | 1.6 |

### Other / uncategorised (77)

| # | Mod | packageId | Workshop | Versions |
|---:|---|---|---|---|
| 25 | [AV] Mechanoid Skins | `veltaris.mechanoidskins` | 3667667489 | 1.6 |
| 40 | [ZAV] Glowstone | `zav.glowstoneforked` | 3231900626 | 1.4,1.5,1.6 |
| 48 | All Specialists Can Work | `opa.allspecialistscanwork` | 2833543540 | 1.3,1.4,1.5,1.6 |
| 66 | Better Ambushes Continued | `ionfrigate12345.coolandgoodambush` | 3422946483 | 1.2,1.3,1.5,1.6 |
| 71 | Better Infestations (Continued) | `zal.betterinfestations` | 3285516766 | 1.5,1.6 |
| 84 | Blood Animations | `fuu.bloodanimations` | 3228047321 | 1.4,1.5,1.6 |
| 85 | Bradson's Main Button Icons (Forked + Expanded) | `bs.mbifvte` | 3532359201 | 1.2,1.3,1.4,1.5,1.6 |
| 92 | Change map edge limit | `kapitanoczywisty.changemapedge` | 1546494565 | 1.0,1.1,1.2,1.3,1.4,1.5,1.6 |
| 96 | Choose Where To Land | `kearril.choosewheretoland` | 3537970831 | 1.6 |
| 98 | Colored deep resources | `kikohi.coloreddeepresources` | 3203269467 | 1.3,1.4,1.5,1.6 |
| 99 | Compact Hediffs | `petetimessix.compacthediffs` | 2031734067 | 1.1,1.2,1.3,1.4,1.5,1.6 |
| 106 | Custom Room Names | `costel.customroomnames` | 3626983473 | 1.6 |
| 110 | Dark Ages : Crypts and Tombs | `van.dacrypts` | 2963826335 | 1.4,1.5,1.6 |
| 115 | Defensive Positions - Forked | `gondragon.defensivepositions` | 3550360467 | 1.6 |
| 124 | Disease Immunity Progress Tracker | `lornath.diseaseimmunityprogresstracker` | 3659005144 | 1.6 |
| 128 | Dubs Break Mod | `dubwise.dubsbreakmod` | 1722398508 | 1.0,1.1,1.2,1.3,1.4,1.5,1.6 |
| 132 | Dynamic Effects Forge | `blues.forge` | 3735443951 | 1.6 |
| 143 | Fahrenheit and Celsius | `kosaro.fahrenheitandcelsius` | 937759575 | 1.0,1.1,1.2,1.3,1.4,1.5,1.6 |
| 145 | Firefoam poppers aren't ugly! | `realify.firefoam` | 3749974270 | 1.6,1.5,1.4,1.3,1.2 |
| 148 | Floor Lights 2 | `temeez.floorlights2` | 2882927601 | 1.4,1.5,1.6 |
| 163 | Harvest When Butchering | `mlie.harvestwhenbutchering` | 2898826891 | 1.3,1.4,1.5,1.6 |
| 175 | Infestations Spawn in Darkness 1.6 | `koth.isid` | 3551839891 | 1.6 |
| 180 | Interaction-Area Settings | `mlie.interactionareasettings` | 3647833135 | 1.5,1.6 |
| 187 | Just Leave Already | `timuttie.justleavealready.fork.mitasamodel` | 3530313037 | 1.4,1.5,1.6 |
| 196 | Linkable Settings | `mlie.linkablesettings` | 2739581441 | 1.2,1.3,1.4,1.5,1.6 |
| 204 | Mass Lovin' | `udon.masslovein` | 2612846082 | 1.3,1.4,1.5,1.6 |
| 205 | Meaningful Encounters | `sirdarkelf.meaningfulencounters` | 3778244635 | 1.6 |
| 206 | Meat on a Stick | `badoaks.meatonastick` | 3435027361 | 1.5,1.6 |
| 212 | Mercer's Backpacks (Continued) | `mlie.mercerbackpacks` | 2014572849 | 1.0,1.1,1.2,1.3,1.4,1.5,1.6 |
| 215 | Milky Way | `andromeda.milkyway` | 3773448562 | 1.6 |
| 216 | Mine Sight | `rabiosus.minesight` | 3769804600 | 1.6 |
| 217 | MinifyEverything | `erdelf.minifyeverything` | 872762753 | 1.0,1.1,1.2,1.3,1.4,1.5,1.6 |
| 225 | Mood Alerts | `deadmano.moodalerts` | 3128351120 | 1.4,1.5,1.6 |
| 226 | Mood Chain Reaction | `acutus.moodchainreaction` | 3721381956 | 1.6 |
| 227 | More Dangerous Game | `zylle.moredangerousgame` | 2364245786 | 1.1,1.2,1.3,1.4,1.5,1.6 |
| 233 | Morphs Assorted Biotech Retex | `morphsassorted.biotechretex` | 2950383797 | 1.4,1.5,1.6 |
| 234 | MutatorWorldIcons | `snobi.mutatorworldicons` | 3551904193 | 1.6 |
| 238 | Night Lights | `zylle.nightlights` | 2149276108 | 1.1,1.2,1.3,1.4,1.5,1.6 |
| 239 | Nightmare Core | `nightmare.core` | 3047049650 | 1.3,1.4,1.5,1.6 |
| 240 | No Forced Slowdown | `dingo.noforcedslowdown` | 1419593453 | 1.0,1.1,1.2,1.3,1.4,1.5,1.6 |
| 244 | Non uno Pinata (don't drop items) | `avilmask.nonunopinata` | 1778821244 | 1.0,1.1,1.2,1.3,1.4,1.5,1.6 |
| 247 | Onimods - Electric Torches and Braziers | `onimods.electrictorches` | 3301583634 | 1.5,1.6 |
| 268 | Realistic Darkness (Light) | `wemd.realisticdarknesslight` | 1555355332 | 1.6,1.5,1.4,1.3,1.2,1.1 |
| 270 | Rebalanced Ancient Junk | `mosi.rebalancedancientjunk` | 3336109612 | 1.5,1.6 |
| 276 | Right Click to Toss Carried Pawn | `alma.tossem` | 3779630220 | 1.6 |
| 278 | Rim of Madness - Bones Unofficial Fix | `sihv.rombonesport` | 3252977437 | 1.0,1.1,1.2,1.3,1.4,1.5,1.6 |
| 293 | Roots of Rimworld | `ghost.rootsofrimworld` | 2977818583 | 1.4,1.5,1.6 |
| 298 | Security Doors Expanded | `jarocks.securitydoorsexpanded` | 3777106218 | 1.6 |
| 299 | Self Dyeing | `avilmask.selfdyeing` | 2562859859 | 1.3,1.4,1.5,1.6 |
| 311 | Sleeping Buddies | `astryl.sleepingbuddies` | 3774741768 | 1.6 |
| 328 | Tech Level Enforcement | `summersausages2ttv.techlevelenforcement` | 3430230860 | 1.5,1.6 |
| 340 | Trading Options Continue | `kearril.tradingoptionscontinue` | 3524414310 | 1.6 |
| 345 | Trystan Traveller's Shuttle Schematics | `trouperton.trystantravellersshuttleschematics` | 3655212016 | 1.6 |
| 346 | Tunneler Expanded | `error277.tunneler.expanded` | 2599616050 | 1.3,1.4,1.5,1.6 |
| 359 | Vanilla Backstories Expanded | `vanillaexpanded.vanillabackstoriesexpanded` | 2861806869 | 1.6,1.4,1.5 |
| 360 | Vanilla Brewing Expanded | `vanillaexpanded.vbrewe` | 2186560858 | 1.4,1.5,1.6 |
| 362 | Vanilla Cooking Expanded | `vanillaexpanded.vcooke` | 2134308519 | 1.4,1.5,1.6 |
| 384 | Vanilla Skills Rexamined | `gravenwitch.vsrexamined` | 3235834179 | 1.5,1.6 |
| 386 | Vanilla Trading Expanded | `vanillaexpanded.vanillatradingexpanded` | 2785616901 | 1.4,1.5,1.6 |
| 395 | We Are United | `sl4vp0wer.weareunited` | 3030804445 | 1.3,1.4,1.5,1.6 |
| 406 | Yayo's Meteor (Continued) | `mlie.yayosmeteor` | 2892867866 | 1.3,1.4,1.5,1.6 |
| 430 | ISEKAI RPG LEVELING | `jellycreative.isekaileveling` | 3657580708 | 1.6 |
| 432 | Large Pawns | `neku.largepawns` | 3777700657 | 1.6 |
| 436 | Meat on a Stick - Expansion | `badoaks.meatonastick.expansion` | 3577333297 | 1.6 |
| 450 | Rimsential - Spaceports (Continued) | `zal.spaceports` | 3225120958 | 1.5,1.6 |
| 456 | Stonecutting Extended | `scherub.stonecuttingextended` | 2571676542 | 1.3,1.4,1.5,1.6 |
| 458 | Toddlers | `cyanobot.toddlers` | 2903359152 | 1.4,1.5,1.6 |
| 459 | Vanilla Cooking Expanded - Stews | `vanillaexpanded.vcookestews` | 2134312965 | 1.4,1.5,1.6 |
| 462 | Vanilla Skills Expanded | `vanillaexpanded.skills` | 3400246558 | 1.4,1.5,1.6 |
| 467 | Yayo's Animation (Continued) | `com.yayo.yayoani.continued` | 2877292196 | 1.3,1.4,1.5,1.6 |
| 469 | [42G]Glowing Bushes | Fork by [ETF] | `fourtoo.glowingbush` | 3425062214 | 1.0,1.1,1.2,1.3,1.4,1.5,1.6 |
| 476 | Alpha Skills | `sarg.alphaskills` | 3448953006 | 1.5,1.6 |
| 482 | Functional Vanilla Expanded Props (Continued) | `mlie.functionalvanillaexpandedprops` | 2574097280 | 1.1,1.2,1.3,1.4,1.5,1.6 |
| 536 | [FSF] Complex Jobs | `frozensnowfox.complexjobs` | 2069684319 | 1.0,1.1,1.2,1.3,1.4,1.5,1.6 |
| 541 | Common Sense | `avilmask.commonsense` | 1561769193 | 1.0,1.1,1.2,1.3,1.4,1.5,1.6 |
| 547 | Big and Small - Enable All Optional Content | `redmattis.optional` | 3532649666 | 1.6,1.7,1.8,1.9,1.10,1.11,1.12,1.13,1.14,1.15 |
| 548 | Big and Small - Races | `redmattis.bigsmall` | 2894397737 | 1.4,1.5,1.6 |

---

## 5. INACTIVE — installed but switched off

_655 mods. The 'already owned, one click away' pool._


### Frameworks & libraries — inactive (6)

| Mod | packageId | Workshop | Versions |
|---|---|---|---|
| [SYR] Processor Framework | `syrchalis.processor.framework` | 3210544395 | 1.3,1.4,1.5,1.6 |
| ATH's Styleable Framework | `anthitei.athsstyleableframework.style` | 3016405872 | 1.3,1.4,1.5,1.6 |
| Bunny Framework | `romyashi.bunnyframework` | 3015333853 | 1.4,1.5,1.6 |
| KEP:Toolbox Bionics (Continued) | `zal.keptb` | 2803222245 | 1.3,1.4,1.5,1.6 |
| Log Publisher from HugsLib | `m00nl1ght.unofficialupdates.hugslogpublisher` | 2873415404 | 1.4,1.5,1.6 |
| Prepatcher | `jikulopo.prepatcher` | 3563469557 | 1.4,1.5,1.6 |

### Industry / factory / progression — inactive (2)

| Mod | packageId | Workshop | Versions |
|---|---|---|---|
| Retextured! - Recycle This | `soulretextured.recyclethis` | 2978527594 | 1.3,1.4,1.5,1.6 |
| Vanilla Chemfuel Expanded - Odyssey Patch | `bulldog.vanillachemfuelexpandedodysseypatch` | 3530583255 | 1.6 |

### Gravship / ship — inactive (8)

| Mod | packageId | Workshop | Versions |
|---|---|---|---|
| [DHM]Hybrid-Powered Gravships | `drilledhead.hybridpoweredgravships` | 3524491355 | 1.6 |
| [Odyssey] Necrotic Gravship Retextured | `okagrim.necrotexgrav` | 3567591339 | 1.6 |
| Anomaly for Gravship | `als.anomalygravship` | 3558784993 | 1.6 |
| Archean Tree in Gravship | `sielfyr.archeangravship` | 3530307917 | 1.6 |
| Get Off My Gravship! | `nep.getoffmygravship` | 3548548674 | 1.6 |
| Gravship Biofuel Refinery Retexture | `superpox.gravshipbiofuelrefineryretexture` | 3553790634 | 1.0,1.1,1.2,1.3,1.4,1.5,1.6 |
| Gravship Substructure Anywhere | `qwertaii.substructureanywhere` | 3528440892 | 1.6 |
| Mini Gravships | `memer.minigravships` | 3527312835 | 1.6 |

### World / biomes / terrain — inactive (9)

| Mod | packageId | Workshop | Versions |
|---|---|---|---|
| [TW1.6]幻彩林地 Rainbow forest | `tw.tangsbiome.rainbowforest` | 3532501549 | 1.6 |
| Dusk Wood Biome | `okagrim.duskwood` | 3560499511 | 1.6 |
| Greenworld - ReGrowth | `son1c.greenworldregrowth` | 2882040405 | 1.2,1.3,1.4,1.5,1.6 |
| Gulden Biome (Continued) | `pphhyy.guldennew` | 3607066070 | 1.5,1.6 |
| ReGrowth 2 World Map Beautification for More Vanilla Biomes | `noxilie.regrow.wmb.morevanillabiomes` | 3564679624 | 1.6 |
| ReGrowth 2: Aspen | `regrowth.botr.aspenforest` | 2545774148 | 1.4,1.5,1.6 |
| ReGrowth ReTextures Patches | `zaire82.rgretexpatches` | 3410715318 | 1.6 |
| ReGrowth: Core Animal Texture Patch | `shira.rgrwthpatch` | 2985646173 | 1.6,1.5 |
| Smooth Terrain | `chaoticenrico.smoothterrain` | 3502765685 | 1.6 |

### Quests / structures / events — inactive (12)

| Mod | packageId | Workshop | Versions |
|---|---|---|---|
| Better Quest Rewards | `steve.betterquestrewards` | 2671237934 | 1.3,1.4,1.5,1.6 |
| Dungeon Core | `hailuan.dungeon` | 3064597982 | 1.4,1.5,1.6 |
| Limit Quest Pawns | `kathanon.limitquestpawns` | 2898408684 | 1.4,1.5,1.6 |
| Medieval Fantasy Themed Quest Rewards | `botchjob.medievalfantasyquestrewards` | 2955864975 | 1.4,1.5,1.6 |
| Medieval Fantasy Themed Relic Quests | `botchjob.medievalfantasythemedrelicquests` | 3035624471 | 1.4,1.5,1.6 |
| No Disabled Factions In Quests | `kathanon.nodisabledfactions` | 2892125637 | 1.4,1.5,1.6 |
| Quest Expiration Critical Alert | `reiquard.questexpirationcriticalalert` | 2405632805 | 1.2,1.3,1.4,1.5,1.6 |
| Questing Gives Goodwill (1.6) | `sirrolin.questsgivesgoodwill` | 3074941619 | 1.4,1.5,1.6 |
| Questing Meme | `sirmashedpotato.questingmeme` | 2826539854 | 1.3,1.4,1.5,1.6 |
| Real Ruins | `woolstrand.realruins` | 1552146295 | 1.0,1.1,1.2,1.3,1.4,1.5,1.6 |
| Vanilla Quests Expanded - Deadlife | `vanillaquestsexpanded.deadlife` | 3497226454 | 1.5,1.6 |
| Wood's Muzzle Flash for Ancient urban ruins | `charlie.muzzle.flash.for.ancientruins` | 3442021825 | 1.5,1.6,1.7,1.8,1.9 |

### Factions / antagonists — inactive (21)

| Mod | packageId | Workshop | Versions |
|---|---|---|---|
| [RH2] Faction: Utilitarian | `rh2.faction.utilitarian` | 2942350062 | 1.4,1.5,1.6 |
| [RH2] Faction: V.O.I.D. | `rh2.faction.void` | 2883208829 | 1.4,1.5,1.6 |
| [RH2] V.O.I.D. Storyteller | `rh2.void.storyteller` | 2130957394 | 1.1,1.2,1.3,1.4,1.5,1.6 |
| Friendly Hostile Factions (Continued) | `zal.fhf` | 2812503053 | 1.3,1.4,1.5,1.6 |
| Moon Factions | `ocarina.hazzor.moon.factions` | 3561739080 | 1.6 |
| Real Faction Guest (Continued) | `mlie.realfactionguest` | 2886929245 | 1.2,1.3,1.4,1.5,1.6 |
| Reel's Insector Faction | `reel.insectorfaction` | 3309022698 | 1.5,1.6 |
| Rimsenal Faction Pack - Federation | `rimsenal.federation` | 736172213 | 1.0,1.1,1.2,1.3,1.4,1.5,1.6 |
| Rimsenal Faction Pack - Spacer | `rimsenal.spacer` | 3086137468 | 1.4,1.5,1.6 |
| Ultimate Storyteller - Basilicus Patch [1.4-1.6] | `gold.usbasilicuspatch` | 2928443788 | 1.4,1.5,1.6 |
| Ultimate Storyteller [1.4-1.6] | `gold.ultimatestoryteller` | 2887952810 | 1.4,1.5,1.6 |
| USCM - Colonial Marines Corps Faction | `hiztaar.optionnal.uscmfcm` | 759866027 | 1.0,1.1,1.2,1.3,1.4,1.5,1.6 |
| USCM - Xenomorphs Faction | `hiztaar.optionnal.uscmxenomorphs` | 974867140 | 1.5,1.6 |
| Vanilla Factions Expanded - Classical | `oskarpotocki.vfe.classical` | 2787850474 | 1.4,1.5,1.6 |
| Vanilla Factions Expanded - Deserters | `oskarpotocki.vfe.deserters` | 3025493377 | 1.4,1.5,1.6 |
| Vanilla Factions Expanded - Empire | `oskarpotocki.vfe.empire` | 2938820380 | 1.4,1.5,1.6 |
| Vanilla Factions Expanded - Medieval 2 | `oskarpotocki.vfe.medieval2` | 3444347874 | 1.5,1.6 |
| Vanilla Factions Expanded - Pirates | `oskarpotocki.vfe.pirates` | 2723801948 | 1.4,1.5,1.6 |
| Vanilla Factions Expanded - Settlers | `oskarpotocki.vanillafactionsexpanded.settlersmodule` | 2052918119 | 1.4,1.5,1.6 |
| Vanilla Storytellers Expanded - Perry Persistent | `vse.perrypersistent` | 2149702069 | 1.4,1.5,1.6 |
| Vanilla Storytellers Expanded - Winston Waves | `vanillastorytellersexpanded.winstonwave` | 3215569151 | 1.6,1.4,1.5 |

### Creatures / threats — inactive (48)

| Mod | packageId | Workshop | Versions |
|---|---|---|---|
| [FSF] Better Exploration Loot | `frozensnowfox.betterexplorationloot` | 3526957922 | 1.6 |
| [MUS]哥特式吸血鬼家具 Gothicstyle Vampire Furniture | `mingtuwuxiang.gothicdecorative` | 3102678787 | 1.6,1.5,1.4,1.3,1.2 |
| [WYD] Worthless Plants | `wyr3d.worthlessplants` | 3555545972 | 1.6 |
| ANDH - Animals Nuzzling Detects Horrors | `latta.petknowstrueyou` | 3230195082 | 1.5,1.6 |
| Anima Animals Combined (Continued) | `vr.animaanimalscombined` | 3190798512 | 1.2,1.3,1.4,1.5,1.6 |
| Animal Apparel: Basic Armor | `ingendum.animalarmorbasic` | 3513849448 | 1.6 |
| Animal Apparel: Universal Basic Armor | `ingendum.animalarmoruniversal` | 3524467381 | 1.6 |
| Animal Biosculpter | `bodilpwnz.animalbiosculpter` | 2883571601 | 1.4,1.5,1.6 |
| Animal Variety Coats | `cucumpear.azrael.varietycoats` | 1511926373 | 1.0,1.1,1.2,1.3,1.4,1.5,1.6 |
| AnimalHarvestingSpot (Continued) | `mlie.animalharvestingspot` | 1542765654 | 1.0,1.1,1.2,1.3,1.4,1.5,1.6 |
| Animals are fun! (Continued) | `colossalfossil.animalsarefuncontinued` | 3245454244 | 1.1,1.2,1.3,1.4,1.5,1.6 |
| Anomaly - Chimera Variants | `hekmo.chimeravariants` | 3482158348 | 1.5,1.6 |
| Better Orbital Traders | `coldcrow.betterorbitaltraders` | 3009866854 | 1.4,1.5,1.6 |
| Better Tradable Items | `coldcrow.bettertradableitems` | 3009963773 | 1.4,1.5,1.6 |
| Bonded Animals RNG | `scurvyez.bondedanimalsrng` | 3370236256 | 1.5,1.6 |
| Cut plants before building (Continued) | `mlie.cutplantsbeforebuilding` | 3286376165 | 1.0,1.1,1.2,1.3,1.4,1.5,1.6 |
| Decorations and dishes at Gorgeous banquet | `mo.decorationsluxury` | 3027639868 | 1.2,1.3,1.4,1.5,1.6 |
| Defiler Generator | `fleshforge.defilergenerator` | 3530838203 | 1.6 |
| Devilstrand Hydroponics | `steelchicken.devilstrandhydroponics` | 2008034916 | 1.3,1.4,1.5,1.6 |
| Dlc collaboration - Void universe | `hailuan.voiduniverse` | 3587277884 | 1.6 |
| Draftable Animals - Releashed | `wolfcub05.draftableanimals` | 3534629428 | 1.6 |
| Dust Bunnies | `crows.dustbunny` | 3480725900 | 1.5,1.6 |
| Erin's Decorations | `erin.decorations` | 2463358089 | 1.2,1.3,1.4,1.5,1.6 |
| Farhan's Warcasket Tweaks (Vacuum and Temperature) | `farhanfair.warcaskettweakspatch` | 3533261706 | 1.6 |
| Hardworking animals 1.6 | `daniledman.hardworkinganimals` | 933324235 | 1.0,1.1,1.2,1.3,1.4,1.5,1.6 |
| Human Pregnancy Duration Settings | `daysleep.humanpregnancyduration` | 2880967245 | 1.4,1.5,1.6 |
| Integrated Creep Joiners | `grillmaster.integratedcreepjoiners` | 3233429182 | 1.5,1.6 |
| Integrated Implants | `lts.i` | 3223443793 | 1.5,1.6 |
| Mad Skills | `ratys.madskills` | 731111514 | 1.0,1.1,1.2,1.3,1.4,1.5,1.6 |
| More Archotech Implants | `legendaryminuteman.mai` | 2646064233 | 1.0,1.1,1.2,1.3,1.4,1.5,1.6 |
| More Milkable and Shearable Animals | `koberiddle.milkandwoolpatches` | 3453878341 | 1.5,1.6 |
| More Predators | `zylle.morepredators` | 2347596617 | 1.1,1.2,1.3,1.4,1.5,1.6 |
| Never Generate Relations | `doll.nevergeneraterelations` | 2891797130 | 1.4,1.5,1.6 |
| RimKeeper - Wild Animal Procreation | `keepercraft.rimkeeperanimals` | 3259367736 | 1.5,1.6 |
| Thrumbo Husbandry | `hoboofserenity.thrumbohusbandry` | 2208985736 | 1.6,1.5,1.4,1.3,1.2 |
| Ultratech Shades (Continued) | `mlie.ultratechshades` | 2937778775 | 1.3,1.4,1.5,1.6 |
| UNAGI Decorative Furniture | `unagi.funiture.build.window` | 3379047800 | 1.5,1.6 |
| Vanilla Animals Expanded — Endangered | `vanillaexpanded.vaeendandext` | 2366589898 | 1.6,1.4,1.5 |
| Vanilla Animals Expanded — Royal Animals | `vanillaexpanded.vaeroy` | 2858079457 | 1.4,1.5,1.6 |
| Vanilla Base Generation Expanded | `vanillaexpanded.basegeneration` | 3209927822 | 1.4,1.5,1.6 |
| Vanilla Genetics Expanded - Genome Extracting Table ALL Genomes | `victor.genometable` | 2883081878 | 1.4,1.5,1.6 |
| Vanilla Plants Expanded | `vanillaexpanded.vplantse` | 2134308522 | 1.4,1.5,1.6 |
| Vanilla Plants Expanded - More Plants | `vanillaexpanded.vplantsemore` | 2748889667 | 1.4,1.5,1.6 |
| Vanilla Plants Expanded - Mushrooms | `vanillaexpanded.vplantsemushrooms` | 3006389281 | 1.4,1.5,1.6 |
| Vanilla Psycast Expanded - Biotech Integration | `danzen.vpe.biotechintegration` | 3110971925 | 1.4,1.5,1.6 |
| VFE Pirates - Hardworking Warcaskets | `dmp.vfepirates.warcasketwork` | 3535194807 | 1.6 |
| VGP Xtra Trees and Flowers | `dismarzero.vgp.xtratreesandflowers` | 2007064094 | 1.0,1.1,1.2,1.3,1.4,1.5,1.6 |
| XenomorphInsectoids | `joe.xenomorphinsectoids` | 2873545234 | 1.6,1.5,1.4,1.3 |

### Star Wars content — inactive (3)

| Mod | packageId | Workshop | Versions |
|---|---|---|---|
| [JDS] AQW Armor Set | `m3.jangodsoul.aqw.armorset` | 3541935426 | 1.6 |
| [JDS] Dead Frontier - V.O.I.D | `m3.jangodsoul.df.void` | 3543946353 | 1.6 |
| Star Wars Dub's Hygiene Stuff | `ucp.starwarsdubshygienestuff` | 3371695380 | 1.5,1.6 |

### Hazard / environment — inactive (5)

| Mod | packageId | Workshop | Versions |
|---|---|---|---|
| (NWN) Real Fog of War (Continued) | `mlie.nwnrealfogofwar` | 3391128917 | 1.2,1.3,1.4,1.5,1.6 |
| [CF] Dubs Bad Hygiene Upscaled | `dbh.upscaled` | 3163175368 | 1.4,1.5,1.6 |
| Dubs Bad Hygiene | `dubwise.dubsbadhygiene` | 836308268 | 1.0,1.1,1.2,1.3,1.4,1.5,1.6 |
| Dubs Bad Hygiene - Spring Water Patch | `azrazalea.dbh.springwater.patch` | 3531641684 | 1.6 |
| VE Medical drips - Dubs Bad Hygiene patch | `scorpio.vemedicaldripsdubsbadhygiene` | 2940894029 | 1.2,1.3,1.4,1.5,1.6 |

### Storage / hauling / QoL / UI — inactive (28)

| Mod | packageId | Workshop | Versions |
|---|---|---|---|
| [CF] Anomaly Upscaled | `cf.anomalyupscaled` | 3239664028 | 1.5,1.6 |
| [FSF] No Default Shelf Storage | `frozensnowfox.nodefaultshelfstorage` | 945085502 | 1.0,1.1,1.2,1.3,1.4,1.5,1.6 |
| [sbz] Neat Storage | `sbz.neatstorage` | 3416243474 | 1.5,1.6 |
| Anomaly Research Asteroid | `zoarak.anomalyplat` | 3527726648 | 1.6 |
| Compact Work Tab (Continued) | `mlie.compactworktab` | 3250322299 | 1.4,1.5,1.6 |
| Controlled Rituals - Anomaly | `nuanki.controlledrituals` | 3328826971 | 1.5,1.6 |
| Crafting Quality Rebalanced | `phomor.craftingqualityrebalanced` | 1542004942 | 1.0,1.1,1.2,1.3,1.4,1.5,1.6 |
| Durable Clothes (Continued) | `mlie.durableclothes` | 2015395963 | 1.0,1.1,1.2,1.3,1.4,1.5,1.6 |
| EnchantQualityPlus | `statistno1.enchantqualityplusunofficial` | 3531518926 | 1.3,1.4,1.5,1.6 |
| Epochs - Tallow | `det.epochstallow` | 3502180016 | 1.5,1.6 |
| Epochs Tallow - Butchery Patch | `tinda.patches.epochstallow` | 3508507223 | 1.5,1.6 |
| Fix Styled Blueprints | `kathanon.fixstyledblueprints` | 2957953663 | 1.4,1.5,1.6 |
| Gerrymon's Upscaled Vanilla Textures | `gerrymon.uvt` | 3276562906 | 1.5,1.6 |
| Haul to Stack | `jkluch.haultostack` | 949498803 | 1.0,1.1,1.2,1.3,1.4,1.5,1.6 |
| Keyz Misc Resources | `keyz182.keyzmiscresources` | 3355560776 | 1.5,1.6 |
| Letter stack cleaner | `seohyeon.letterstackcleaner` | 2669779266 | 1.3,1.4,1.5,1.6 |
| LWM's Adaptive Deep Storage | `asf.deepstorage` | 3373064575 | 1.4,1.5,1.6 |
| Ollie's Invisible Walls | `ucp.invisiblewalls` | 2857888739 | 1.3,1.4,1.5,1.6 |
| Phaneron's Basic Storage | `phaneron.basic.storage` | 3201536200 | 1.4,1.5,1.6 |
| Premade Xenotype Floatmenu to Dialog | `lee.xenotypefloattodialogue` | 3350991041 | 1.5,1.6 |
| Progression: Storage | `ferny.progressionstorage` | 3292746186 | 1.5,1.6 |
| QualityBuilder Unofficial 1.6 | `hatti.qualitybuilder` | 3512466087 | 1.1,1.2,1.3,1.4,1.5,1.6 |
| Reel's Expanded Storage | `reel.expanded.storage` | 3237638097 | 1.5,1.6 |
| Simple Utilities: Fridge | `owlchemist.fridgeutilities` | 3219883811 | 1.5,1.6 |
| SimpleCameraSetting | `ray1203.simplecamerasetting` | 3232415388 | 1.5,1.6 |
| Stack gap | `andromeda.stackgap` | 3071298014 | 1.4,1.5,1.6 |
| Upgrade Quality | `rakros.upgradequality` | 3176082972 | 1.4,1.5,1.6 |
| Vanilla Fix: Haul After Slaughter | `puremj.mjrimmods.vanillafixhaulafterslaughter` | 2801452324 | 1.3,1.4,1.5,1.6 |

### Trade / economy — inactive (6)

| Mod | packageId | Workshop | Versions |
|---|---|---|---|
| [GTG]Odyssey Orbital Trader | `teiwaz.oot` | 3522859265 | 1.6 |
| Gene Trader | `tac.genetrader` | 2886375137 | 1.4,1.5,1.6 |
| Livestock Traders | `samael.livestocktraders` | 2960610215 | 1.4,1.5,1.6 |
| Medieval Trader Airships (Legacy) | `joeownage.automatic.traderships` | 3448488157 | 1.5,1.6 |
| TradeHelper | `timmyliang.tradehelper` | 2113372560 | 1.1,1.2,1.3,1.4,1.5,1.6 |
| We Had a Trader? (Continued) | `mlie.wehadatrader` | 1541408076 | 1.0,1.1,1.2,1.3,1.4,1.5,1.6 |

### Vehicles / caravans / settlements — inactive (8)

| Mod | packageId | Workshop | Versions |
|---|---|---|---|
| Caravan Mood Buff | `syrus.caravanmoodbuff` | 2680751877 | 1.3,1.4,1.5,1.6 |
| Small Vehicle Add-ons | `inoshishi3.smallvehicleaddons` | 3420948947 | 1.4,1.5,1.6 |
| Technical map Vehicles | `mo.technicalmapvehicles` | 3438366909 | 1.5,1.6 |
| Vanilla Outposts Expanded: Delivery Logistics | `mrhydralisk.voedeliverylogistics` | 3006726393 | 1.3,1.4,1.5,1.6 |
| Vanilla Outposts Expanded: Power Grid | `mrhydralisk.voepowergrid` | 2915686437 | 1.3,1.4,1.5,1.6 |
| Vanilla Outposts Expanded: Prisoner Patch | `mrhydralisk.voeprisonerpatch` | 3002936071 | 1.3,1.4,1.5,1.6 |
| Vanilla Vehicles Expanded - Upgrades | `oskarpotocki.vanillavehiclesexpandedupgrades` | 3302208420 | 1.5,1.6 |
| Vehicles - Pelican(Helldivers 2) | `hd2.pelican` | 3370607942 | 1.5,1.6 |

### Social / romance / slavery / prisoners — inactive (6)

| Mod | packageId | Workshop | Versions |
|---|---|---|---|
| [NL] Custom Portraits | `nals.customportraits` | 1569605867 | 1.0,1.1,1.2,1.3,1.4,1.5,1.6 |
| More Persona Traits | `arquebus.morepersonatraits` | 2863308112 | 1.3,1.4,1.5,1.6 |
| RimTek StealthBelt | `deon.rimtek.stealthbelt` | 3501257149 | 1.5,1.6 |
| Stealth Shuttle | `mrwireman.stealthshuttle` | 3534488918 | 1.6 |
| The Sims Traits | `goji.thesimstraits` | 3604588393 | 1.5,1.6 |
| Trait and Backstory Icons | `superniquito.traiticons` | 2873494547 | 1.3,1.4,1.5,1.6 |

### Ideology / ritual / religion — inactive (20)

| Mod | packageId | Workshop | Versions |
|---|---|---|---|
| Dark Psychic Rituals: The Following | `dprtf.darkpsychicrituals.sentinel` | 3596468709 | 1.6 |
| Ducks' No Limits - Ideology (Continued) | `mlie.ducksnolimitsideology` | 2916566114 | 1.3,1.4,1.5,1.6 |
| Empiricism and Faith - Mort's Ideologies: Memes and Precepts | `mortstrudel.mortideologyscifai` | 2948947009 | 1.4,1.5,1.6 |
| Gauranlen Supremacy doesn't need Tree Connection! | `kitty.treememepatch` | 3556875187 | 1.6 |
| Gorlath's Flowery Ideology Addon | `gorlath.ideonature` | 3362432392 | 1.5,1.6 |
| Ideology Warframe Icons | `rince.ideo.warframesymbols` | 2937728695 | 1.4,1.5,1.6 |
| Meals On Wheels - Continued | `memegoddess.mealsonwheels` | 3538082807 | 1.1,1.2,1.3,1.4,1.5,1.6 |
| Millitarism Meme | `seti.millitarism` | 3482463633 | 1.5,1.6 |
| No Random Ideologies | `mlie.norandomideologies` | 3337263133 | 1.4,1.5,1.6 |
| Obsidia Expansion - Ideology Icons | `obsidiaexpansion.ideology.icons` | 2990607010 | 1.3,1.4,1.5,1.6 |
| Pesky's Arcanist Ideology Style Pack | `pesky.arcanist.style` | 3370539088 | 1.5,1.6 |
| Ritual Size Attenuation | `delmaintweaks.ritualsizeattenuation` | 3262033797 | 1.4,1.5,1.6 |
| Slaughtering Meme | `slaughteringmeme.rince` | 3151598704 | 1.4,1.5,1.6 |
| Stellaris Ideology Icons | `hol.stellarisicons` | 3540888076 | 1.4,1.5,1.6 |
| Thick Armor - Continued | `memegoddess.thickarmor` | 3531630021 | 1.1,1.2,1.3,1.4,1.5,1.6 |
| Tribal Ideology Icons | `ghost.tribalicons` | 3083595998 | 1.3,1.4,1.5,1.6 |
| Vanilla Ideology Expanded - Anima Theme | `vanillaexpanded.vieat` | 2666998627 | 1.4,1.5,1.6 |
| Vanilla Ideology Expanded - Dryads | `vanillaexpanded.ideo.dryads` | 2720631512 | 1.4,1.5,1.6 |
| Vanilla Ideology Expanded - Icons and Symbols | `vanillaexpanded.ideo.iconsandsymbols` | 2552609458 | 1.4,1.5,1.6 |
| Vanilla Ideology Expanded - Sophian Style | `vanillaexpanded.ideo.sophianstyle` | 3194606539 | 1.4,1.5,1.6 |

### Apparel / faces / furniture / decoration — inactive (88)

| Mod | packageId | Workshop | Versions |
|---|---|---|---|
| [RH2] Uncle Boris' - Brainwash Chair | `cp.uncle.boris.brainwash.chair` | 2885223720 | 1.4,1.5,1.6 |
| [TW1.6]堂丸贴图重置~UI Tang's~Retexture~UI | `tw.tangs.retexture.ui` | 3141849282 | 1.2,1.3,1.4,1.5,1.6 |
| [TW1.6]堂丸贴图重置~制成品 Tang's_Retexture_Manufactured | `tw.tangs.retexture.manufactured` | 3058943402 | 1.2,1.3,1.4,1.5,1.6 |
| [TW1.6]堂丸贴图重置~原材料 Tang's~Retexture~Resource | `tw.tangs.retexture.resource` | 3050448166 | 1.2,1.3,1.4,1.5,1.6 |
| [TW1.6]堂丸贴图重置~服饰 Tang's~Retexture~Apparel | `tw.tangs.retexture.apparel` | 3255510656 | 1.4,1.5,1.6 |
| [TW1.6]堂丸贴图重置~武器 Tang's~Retexture~Weapons | `tw.tangs.retexture.weapons` | 3048306872 | 1.2,1.3,1.4,1.5,1.6 |
| [TW1.6]堂丸贴图重置~结构 Tang's~Retexture~Structure | `tw.tangs.retexture.structure` | 3168625192 | 1.2,1.3,1.4,1.5,1.6 |
| [TW1.6]堂丸贴图重置~食物 Tang's~Retexture~Foods | `tw.tangs.retexture.foods` | 3050762215 | 1.2,1.3,1.4,1.5,1.6 |
| Apparello 2 | `shinzy.apparello` | 728381322 | 1.4,1.5,1.6 |
| ATH's style Gothic and Bloody Gothic | `anthitei.athsstylegothic.style` | 3136210612 | 1.3,1.4,1.5,1.6 |
| ATH's styles Norse | `anthitei.athsstylenorse.style` | 3292048218 | 1.3,1.4,1.5,1.6 |
| Barbarian Style Pack | `unclejackhughes.barbarianstylepack` | 3551819421 | 1.6 |
| Better Hot Springs | `elindis.betterhotsprings` | 3532108439 | 1.6 |
| Big and Small Furniture | `redmattis.bsfurniture` | 3024478368 | 1.4,1.5,1.6 |
| Blue Archive Furniture | `mlmlmlm.bluearchivefurniture` | 3491176484 | 1.5,1.6 |
| Change Style Anytime | `cedaro.csa` | 3072859227 | 1.4,1.5,1.6 |
| Clean Textures | `ih.clean.textures` | 2865361569 | 1.3,1.4,1.5,1.6 |
| Dark Ages : Medieval Tools | `van.datools` | 3028566550 | 1.4,1.5,1.6 |
| Delmain Tweaks - Role Apparel | `delmaintweaks.roleapparel` | 2980235255 | 1.4,1.5,1.6 |
| Dubs Apparel Tweaks | `dubwise.dubsappareltweaks` | 2296697286 | 1.2,1.3,1.4,1.6 |
| Erin's Baldur's Gate 3 Hairs | `erin.bg3.hair` | 3069933015 | 1.4,1.5,1.6 |
| Erin's Body Retexture | `erin.body.texture` | 2662457442 | 1.3,1.4,1.5,1.6 |
| Erin's Hairstyles - Redux | `erin.hairredux` | 2361911135 | 1.2,1.3,1.4,1.5,1.6 |
| Erin's Hairstyles 2 | `erin.hair2` | 2849477421 | 1.3,1.4,1.5,1.6 |
| Erin's KPop Demon Hunters Hairs | `erin.kpdh.hair` | 3595945875 | 1.6 |
| Food Texture Variety - Vanilla Expanded Coffee and Tea | `goat.food.texture.variety.vecoffetea` | 3409546023 | 1.5,1.6 |
| Food Texture Variety - Vanilla Expanded Cooking | `goat.food.texture.variety.vecooking` | 3388883044 | 1.5,1.6 |
| Food Texture Variety Core | `goat.food.texture.variety.core` | 3354455179 | 1.5,1.6 |
| Fortification Industrial -Nuclear Dawn | `aoba.fortress.industrial.nucleardawn` | 2733185331 | 1.3,1.4,1.5,1.6 |
| Fortifications - Medieval | `aoba.fortress.medieval` | 2501486827 | 1.2,1.3,1.4,1.5,1.6 |
| Gerrymon's Cannibal Style | `gm.cannibal.style` | 3432956417 | 1.5,1.6 |
| Gerrymon's Erotic Style | `gm.erotic.style` | 3273776545 | 1.5,1.6 |
| Gerrymon's Medieval DBH Retexture | `gerrymon.medievaldbh` | 3510803927 | 1.5,1.6 |
| Gerrymon's Nautian Style | `gm.nautian.style` | 3147664706 | 1.4,1.5,1.6 |
| Gradient Hair | `automatic.gradienthair` | 1687053679 | 1.0,1.1,1.2,1.3,1.4,1.5,1.6 |
| Hard Times: Hair and Beards | `botchjob.hthair` | 3092175321 | 1.4,1.5,1.6 |
| Khayrea Pass Stylepack | `resurrectionem.khayrea` | 3372728277 | 1.4,1.5,1.6 |
| Lock apparel | `lecht.lockapparel` | 3507498385 | 1.5,1.6 |
| Mechanoid Cluster Retexture | `happycam.conditioncauserretexture` | 3523231836 | 1.1,1.2,1.3,1.4,1.5,1.6 |
| Medieval Backstories No HAR | `assassinsbro.medievalbackstoriesnohar` | 3128454510 | 1.4,1.5,1.6 |
| Medieval Backstories Patch | `grasstypefire.medieval.backstoriespatch` | 3170653412 | 1.4,1.5,1.6 |
| Medieval Coastal Outfits | `gerrymon.mco` | 3483685923 | 1.5,1.6 |
| Medieval Era RimTheme | `thale.medievalerarimtheme` | 3551233435 | 1.5,1.6 |
| Medieval Fantasy Psycaster Raids | `waffle.fantasypatches` | 3413747772 | 1.5,1.6 |
| Medieval Fantasy Themed Rare Resources | `botchjob.medievalfantasyrareresources` | 2942661554 | 1.4,1.5,1.6 |
| Medieval Persona Weapons | `arquebus.medievalpersonaweapons` | 2869057049 | 1.3,1.4,1.5,1.6 |
| Medieval Repair | `sm.medievalrepair` | 2955709750 | 1.4,1.5,1.6 |
| Medieval Tailor Continued | `tinda.medieval.tailor.continued` | 3512201406 | 1.5,1.6 |
| Medieval Tool Cabinet (Continued) | `gaon.lowtoolcabinet` | 3326055369 | 1.4,1.5,1.6 |
| Medieval Undead Hordes | `redmattis.undead.medieval` | 2994387009 | 1.4,1.5,1.6 |
| Misc. Training Medieval Retexture | `serek.misctrainingmedievalretexture` | 3271602770 | 1.4,1.5,1.6 |
| MorrowRim - Dunmer Styles | `escp.morrowrim.dunmerstyles` | 3244646489 | 1.5,1.6 |
| MorrowRim - Passive Birthsigns | `escp.morrowrim.birthsignspassive` | 3244646911 | 1.5,1.6 |
| Projectile Bullet Retexture | `nd.rtpj` | 2962208832 | 1.4,1.5,1.6 |
| Reel's Frieren Hairs | `reel.hair2` | 3119772468 | 1.4,1.5,1.6 |
| Reel's Galactic Hairs | `reel.hair` | 2278578765 | 1.0,1.1,1.2,1.3,1.4,1.5,1.6 |
| Rimsenal Style Pack - Techist | `rimsenal.techist` | 2661828028 | 1.3,1.4,1.5,1.6 |
| Rimsenal Style Pack - Urbworld | `rimsenal.urb` | 2908039338 | 1.4,1.5,1.6 |
| RimTek Style | `deon.rimtek.style` | 3502852790 | 1.5,1.6 |
| Romascita Style pack | `resurrectionem.romascita` | 3277109336 | 1.4,1.5,1.6 |
| Roo's HD Hairstyles (continued) | `rooboid.hdhair.continued` | 3559870636 | 1.6 |
| RowMart Stylepack | `resurrectionem.rowmart` | 3503142907 | 1.4,1.5,1.6 |
| RPG Style Inventory | `sandy.rpgstyleinventory` | 1561221991 | 1.0,1.1,1.2,1.3,1.4,1.5,1.6 |
| RPG Style Level Up Mod | `flashpoint55.rpgstylelevelupmod` | 1995668415 | 1.0,1.1,1.2,1.3,1.4,1.5,1.6 |
| ScrubDaddy's Hairstyles | `scrubdaddy.hairstyles` | 3536769145 | 1.6 |
| Simple Apparel Recycling | `arvkus.simplerecycling` | 3239309389 | 1.5,1.6 |
| Simple Learning Retexture | `phaneron.simplelearningretexture` | 3026005966 | 1.4,1.5,1.6 |
| Small Bedroom Furniture | `xale86.smallbedroomfurniture` | 3570779724 | 1.6 |
| Stoneborn - Dwarven Style Pack | `det.dwarvenstyle` | 3172496453 | 1.4,1.5,1.6 |
| Swift Tools Stylepack | `resurrectionem.swifttools` | 3378901481 | 1.4,1.5,1.6 |
| Tribal Backstories - Medieval Patch | `grasstypefire.tribalbackstories.medievalpatch` | 3170651153 | 1.4,1.5,1.6 |
| Tribal Signal Fire (Continued) | `mlie.tribalsignalfire` | 2026582975 | 1.0,1.1,1.2,1.3,1.4,1.5,1.6 |
| UI Retexture | `katsudon.uiretexture` | 2978831421 | 1.4,1.5,1.6 |
| Unique Apparel & Armor | `amro.uniqueapparel` | 3545666494 | 1.6 |
| Van's Retexture : Mechanitor | `sirvan.mechanitorretexture` | 2943977908 | 1.4,1.5,1.6 |
| Van's Retexture : Misc. Training | `sirvan.misctrainingretexture` | 2848956469 | 1.3,1.4,1.5,1.6 |
| Vanilla Beards Retextured | `neronix17.retexture.vanillabeards` | 2777098392 | 1.3,1.4,1.5,1.6 |
| Vanilla Expanded: Hero Backgrounds | `ferny.vanillaexpandedherobackgrounds` | 3313700572 | 1.4,1.5,1.6 |
| Vanilla Furniture Expanded - Architect | `vanillaexpanded.vfearchitect` | 2608762624 | 1.4,1.5,1.6 |
| Vanilla Furniture Expanded - Farming | `vanillaexpanded.vfefarming` | 1957158779 | 1.4,1.5,1.6 |
| Vanilla Furniture Expanded - Spacer Module | `vanillaexpanded.vfespacer` | 2028381079 | 1.4,1.5,1.6 |
| Vanilla Hair Expanded | `vanillaexpanded.vhe` | 1888705256 | 1.4,1.5,1.6 |
| Vanilla Hair Retextured | `neronix17.retexture.vanillahair` | 2748834409 | 1.3,1.4,1.5,1.6 |
| Vanilla Pawns Retextured | `neronix17.hd.pawns` | 2275310562 | 1.3,1.4,1.5,1.6 |
| Vanilla Textures Expanded | `vanillaexpanded.vtexe` | 2016436324 | 1.4,1.5,1.6 |
| Vanilla Textures Expanded - Variations | `vanillaexpanded.vtexvariations` | 2493234474 | 1.4,1.5,1.6 |
| Wartalker Stylepack | `resurrectionem.wartalker` | 3569670754 | 1.4,1.5,1.6 |
| Water retextured | `manulinkraft.waterretextured` | 2782707284 | 1.6,1.5,1.4,1.3 |

### Audio / music — inactive (2)

| Mod | packageId | Workshop | Versions |
|---|---|---|---|
| Modded Weapon Sound Replacement | `bonible.modded.gun.sound.pack` | 2999509683 | 1.4,1.5,1.6 |
| Rimworld: Soundscape Enhanced | `tro.soundscape.enhanced` | 3276642170 | 1.4,1.5,1.6 |

### Weapons / combat — inactive (17)

| Mod | packageId | Workshop | Versions |
|---|---|---|---|
| Combat Readiness Check (Continued) | `mlie.combatreadinesscheck` | 2314304057 | 1.0,1.1,1.2,1.3,1.4,1.5,1.6 |
| Customize Weapon | `vortex.customizeweapon` | 3550585103 | 1.6 |
| Cybranian - Weapon Proficiency | `dimonsever000.weaponproficiency` | 3523531768 | 1.6 |
| Dynamic Weapon Cooldown | `pixelbirb.dwc` | 3038525914 | 1.6 |
| Extra Mini-Turrets | `extts.fl` | 3199145674 | 1.4,1.5,1.6 |
| Full Armor - Hands and Feet [1.6] | `stevezero.fullarmorhandsfeet` | 3530977354 | 1.6 |
| Possessed Weapons | `botchjob.possessedweapons` | 2982391372 | 1.4,1.5,1.6 |
| Rah's Vanilla Turrets Expansion | `rah.rvte` | 2583529720 | 1.3,1.4,1.5,1.6 |
| Reel's Turret Pipeline | `reel.turretpipeline` | 3424132769 | 1.5,1.6 |
| Sellable Odyssey Unique Weapons | `teiwaz.uws` | 3522909912 | 1.6,1.7,1.8,1.9,2.0 |
| TC Tribalized Armor | `tc.tribalizedarmor` | 3338236184 | 1.1,1.2,1.3,1.4,1.5,1.6 |
| Throwing Weapon Belt | `misstall.throwingweaponbeltz` | 3238126692 | 1.5,1.6 |
| UnLimitedArmor | `paragon.hanul.unlimitedarmor` | 1695493009 | 1.0,1.1,1.2,1.3,1.4,1.5,1.6 |
| Vanilla Persona Weapons Expanded | `vanillaexpanded.vpersonaweaponse` | 2826922787 | 1.4,1.5,1.6 |
| Vanilla Weapons Expanded - Laser | `vanillaexpanded.vwel` | 1989352844 | 1.4,1.5,1.6 |
| Vanilla Weapons Expanded - Non-Lethal | `vanillaexpanded.vwenl` | 2454918354 | 1.4,1.5,1.6 |
| Wall Mounted Turrets Version 2 | `honeybadger.wallmountedturretsversiontwo` | 3525168205 | 1.5,1.6 |

### Xenotypes / genes — inactive (31)

| Mod | packageId | Workshop | Versions |
|---|---|---|---|
| [AB] Xenotype: Yautja | `biotechrace.yautja.alleyballey` | 3536839586 | 1.6 |
| [FM] Gene Banks Expanded | `farxmai2.genebanksexapnded` | 3138968978 | 1.4,1.5,1.6 |
| Archotech Genetics | `neronix17.archotech.genetics` | 2995858859 | 1.4,1.5,1.6 |
| AutoExtractGenes | `nibato.autoextractgenes` | 2882834449 | 1.4,1.5,1.6 |
| Beliar Xenotype | `elsov.beliar` | 3237072670 | 1.5,1.6 |
| Big and Small - More Xenotypes | `redmattis.morexenos` | 3218636337 | 1.4,1.5,1.6 |
| Compact Gene Banks/Processors | `redtrainer.compactgenebuildings` | 3466062158 | 1.5,1.6 |
| Det's Xenotypes - Buzzers | `det.buzzers` | 3545293786 | 1.6 |
| Det's Xenotypes - Half-foot | `det.halffoot` | 3530817307 | 1.6 |
| Det's Xenotypes - Stoneborn | `det.stoneborn` | 2888722722 | 1.4,1.5,1.6 |
| Det's Xenotypes - Venators | `det.venators` | 3140248688 | 1.4,1.5,1.6 |
| Faster Gene Recovery | `fastergene.recovery` | 2882689772 | 1.4,1.5,1.6 |
| Gene Extractor Tiers | `redmattis.geneextractor` | 3016454783 | 1.4,1.5,1.6 |
| Gene Nodes - Genes for Sale | `redmattis.genenodes` | 3264344552 | 1.5,1.6 |
| Gene Ripper | `defi.generipper` | 3524806362 | 1.4,1.5,1.6 |
| Gene Tools - Forked | `prkr.genetools` | 3047454700 | 1.4,1.5,1.6 |
| Goblins of the Rim | `bean.customxenotypes.goblinsoftherim` | 3237397753 | 1.5,1.6 |
| Hemogen Extractor | `uveren.hemogenextractor` | 3267565839 | 1.5,1.6 |
| Oops All Gene Banks | `redundant.oopsallgenepacks` | 2883683444 | 1.4,1.5,1.6 |
| Orc Clan + Xenotype | `karew.orcclan` | 3232348025 | 1.5,1.6 |
| Random's Gene Assistant | `rimworld.randomcoughdrop.geneassistant` | 2882497271 | 1.4,1.5,1.6 |
| Rimwars:Pureblood Xenotype | `sov.sith` | 3485069256 | 1.5,1.6 |
| Vanilla Genes Rebalanced | `redmattis.vanillagenesrebalanced` | 2905707100 | 1.4,1.5,1.6 |
| Vanilla Races Expanded - Archon | `vanillaracesexpanded.archon` | 3067715093 | 1.4,1.5,1.6 |
| Vanilla Races Expanded - Custom Icons | `vanillaracesexpanded.customicons` | 2917311689 | 1.4,1.5,1.6 |
| Vanilla Races Expanded - Fungoid | `vanillaracesexpanded.fungoid` | 3042690053 | 1.4,1.5,1.6 |
| Vanilla Races Expanded - Highmate | `vanillaracesexpanded.highmate` | 2995385834 | 1.4,1.5,1.6 |
| Vanilla Races Expanded - Hussar | `vanillaracesexpanded.hussar` | 2893586390 | 1.4,1.5,1.6 |
| Vanilla Races Expanded - Insector | `vanillaracesexpanded.insector` | 3260509684 | 1.5,1.6 |
| Vanilla Races Expanded - Phytokin | `vanillaracesexpanded.phytokin` | 2927323805 | 1.4,1.5,1.6 |
| Wingless Flight Gene | `winglessflight.gene` | 3002447909 | 1.4,1.5,1.6 |

### Other / uncategorised — inactive (335)

| Mod | packageId | Workshop | Versions |
|---|---|---|---|
| [CF] Bionic Icons HD | `bionicicons.hd` | 3239007545 | 1.4,1.5,1.6 |
| [FSF] Better Ancient Complex Loot | `frozensnowfox.betterancientcomplexloot` | 2559244124 | 1.3,1.4,1.5,1.6 |
| [FSF] Better Anomaly Loot | `frozensnowfox.betteranomalyloot` | 3229997523 | 1.5,1.6 |
| [FSF] Filth Vanishes With Rain And Time | `frozensnowfox.filthvanisheswithrainandtime` | 1508341791 | 1.0,1.1,1.2,1.3,1.4,1.5,1.6 |
| [FSF] FrozenSnowFox Tweaks | `frozensnowfox.frozensnowfoxtweaks` | 2893432492 | 1.4,1.5,1.6 |
| [FSF] Indoor Tree Farms | `frozensnowfox.indoortreefarms` | 1515299608 | 1.0,1.1,1.2,1.3,1.4,1.5,1.6 |
| [JF] Geometric Floors | `jf.geometricfloors` | 2863525144 | 1.3,1.4,1.5,1.6 |
| [JF] Royal Carpets | `jf.royalcarpets` | 2977701969 | 1.4,1.5,1.6 |
| [JWL] Atmospheric Water Processor (Continued) | `mlie.jwlatmosphericwaterprocessor` | 3007838663 | 1.3,1.4,1.5,1.6 |
| [Kit] Graze up | `kittahkhan.grazeup` | 2302739121 | 1.2,1.3,1.4,1.5,1.6 |
| [Og] Immersive Filter | `og.immersive.filter` | 3735827910 | 1.6 |
| [Og] Repair Your Gear | `og.repair.your.gear` | 3513376486 | 1.5,1.6 |
| [WYD] Better Campsites | `wyr3d.bettercampsites` | 3546818262 | 1.6 |
| [WYD] Bone | `wyr3d.simpleboneblocks` | 3195547844 | 1.4,1.5,1.6 |
| [WZRD] Carry Capacity (Continued) | `mlie.wzrdcarrycapacity` | 2237017954 | 1.0,1.1,1.2,1.3,1.4,1.5,1.6 |
| [ZAV] Fantasy Metals | `zav.fantasymetalsforked` | 2936850549 | 1.3,1.4,1.5,1.6 |
| Alien | Rimworld | `niz.xenomorphtype` | 3596077324 | 1.6 |
| Aliens: Xenocide (MKI) | `xslayer300.ax.aliens.parta` | 2866528992 | 1.3,1.4,1.5,1.6 |
| Alpha Books | `sarg.alphabooks` | 3403180654 | 1.5,1.6 |
| Alpha Crafts | `sarg.alphacrafts` | 3382446150 | 1.5,1.6 |
| Alpha Props - Parks and Gardens | `sarg.alphapropsparks` | 3146268928 | 1.6,1.5 |
| Ancient hydroponic farm facilities | `xmb.ancienthydroponicfarmfacilities.mo` | 3075384838 | 1.4,1.5,1.6 |
| Anomalies Expected | `mrhydralisk.anomaliesexpected` | 3240752689 | 1.5,1.6 |
| Anomalies Expected Addon | `fallen.anomaliesexpectedaddon` | 3251944598 | 1.5,1.6 |
| Anomaly Anywhere | `souper.anomalyanywhere` | 3534053654 | 1.6 |
| Anomaly Events Extended | `goat.anomaly.events` | 3307094049 | 1.5,1.6 |
| Anomaly Power Improved | `anomaly.power.improved` | 3263594825 | 1.5,1.6 |
| Anomaly Skill Trainer | `ru.anomalyskilltrainer` | 3602237032 | 1.6 |
| Archean Tree Sunlamps | `goat.archean.sunlamps` | 3536650291 | 1.6 |
| Architect Icons | `com.bymarcin.architecticons` | 1195427067 | 1.0,1.1,1.2,1.3,1.4,1.5,1.6 |
| Ars Mythica - Lightseeker | `myf.lightseeker` | 3068154233 | 1.5,1.6 |
| Artificial Water Place | `sc.waterplace` | 2382789361 | 1.1,1.2,1.3,1.4,1.5,1.6 |
| Asteroid Grounds | `rashomcree.odyssey.asteroidgrounds` | 3527371016 | 1.6 |
| Asteroid Mineral Scanner | `broms.asteroidmineralscanner` | 3536585361 | 1.6 |
| Auto-Cast Specialist Commands | `linnun.autocastspecialistcommands` | 3459647882 | 1.5,1.6 |
| Auto-Cut Blight - 1.6 | `defi.autocutblight` | 3520167264 | 1.0,1.1,1.2,1.3,1.4,1.5,1.6 |
| Autocleaner | `automatic.autocleaner` | 2051042827 | 1.1,1.2,1.3,1.4,1.5,1.6 |
| Automatic Parking | `rabiosus.vfautoparking` | 3365473553 | 1.5,1.6 |
| Basic Double Doors | `gt.sam.basicdoubledoors` | 3223646936 | 1.5,1.6 |
| Basic RimThemes Recolours | `mrsamuelstreamer.rimthemesrecolours` | 2916014613 | 1.4,1.5,1.6 |
| Beautiful Outdoors | `meltup.beautifuloutdoors` | 2011794898 | 1.1,1.2,1.3,1.4,1.5,1.6 |
| Beautiful Water (Fork) | `nathanielcwm.beautifulwater` | 2039480177 | 1.0,1.1,1.2,1.3,1.4,1.5,1.6 |
| Better autocasting for Vanilla Psycasts Expanded | `dev.tobot.vpe.betterautocast` | 3199585285 | 1.4,1.5,1.6 |
| Better Distress Call | `nalzurin.betterdistresscall` | 3305489753 | 1.5,1.6 |
| Better Pawn Control | `voult.betterpawncontrol` | 1541460369 | 1.2,1.3,1.4,1.5,1.6 |
| Better Roads | `wastelandr.betterroads` | 1489564822 | 0.17,0.18,0.19,1.0,1.1,1.2,1.3,1.4,1.5,1.6 |
| BetterSliders | `sirrandoo.bettersliders` | 2218078784 | 1.1,1.2,1.3,1.4,1.5,1.6 |
| Big and Small - Heaven and Hell | `redmattis.heaven` | 3170117364 | 1.4,1.5,1.6 |
| Big and Small - Vampires and the Undead | `redmattis.undead` | 2926556467 | 1.4,1.5,1.6 |
| Big Little Mod Patch | `daria40k.biglittlemodpatch` | 2710382569 | 1.3,1.4,1.5,1.6 |
| Bioform Matrix | `bart.bioformmatrix` | 3535848372 | 1.6 |
| Bionic icons | `automatic.bionicicons` | 1677616980 | 1.0,1.1,1.2,1.3,1.4,1.5,1.6 |
| Biosculpter Pod and Neural Supercharger Resize | `syrus.bpansresize` | 2710513531 | 1.3,1.4,1.5,1.6 |
| BioSculptingPlus (Continued) | `mlie.biosculptingplus` | 3272451634 | 1.3,1.4,1.5,1.6 |
| Biotech Expansion - Core | `biotexpans.core` | 2884018485 | 1.4,1.5,1.6 |
| Biotech Expansion - Mythic | `biotexpans.mythic` | 2883216840 | 1.4,1.5,1.6 |
| Block Unwanted Minutiae (Continued) | `mlie.blockunwantedminutiae` | 3278213153 | 1.1,1.2,1.3,1.4,1.5,1.6 |
| Blueprints Forked - 1.6 | `defi.blueprints.fork` | 3525001145 | 1.4,1.5,1.6 |
| Boots and Stuff | `techmago.bootsnstuff` | 1488970545 | 1.2,1.3,1.4,1.5,1.6 |
| Build From Chunk | `cyanobot.buildfromchunk` | 3218639401 | 1.4,1.5,1.6 |
| Bunk Beds | `darknote.bunkbeds` | 2961752749 | 1.4,1.5,1.6 |
| Camping Tent | `aoba.tent` | 2407128339 | 1.1,1.2,1.3,1.4,1.5,1.6 |
| Cash Register (Continued) | `orion.cashregister` | 3509487668 | 1.5,1.6 |
| Castle Walls Expanded | `chaoticenrico.castlewallsexpanded` | 3024167916 | 1.2,1.3,1.4,1.5,1.6 |
| Castle Walls Reborn | `gideon.castlewalls` | 3256542892 | 1.5,1.6 |
| Change Stuff Properties | `mlie.changestuffproperties` | 2788278669 | 1.3,1.4,1.5,1.6 |
| Charge Stunners | `desmond.chargestunners.7742` | 2994740520 | 1.4,1.5,1.6 |
| Cheaper Primitive Floors | `harryrobinson.primitivefloorscheap` | 2833159444 | 1.0,1.1,1.2,1.3,1.4,1.5,1.6 |
| Choose Your Recipe (Continued) | `zal.chooseyourrecipe` | 3263007587 | 1.5,1.6 |
| Cleaning Priority (Continued) | `mlie.cleaningpriority` | 2018316486 | 1.0,1.1,1.2,1.3,1.4,1.5,1.6 |
| Close Settlements | `jelly.bar0th.closesettlements` | 2600837512 | 1.3,1.4,1.5,1.6 |
| Colourful Sterile Tiles | `mlie.colourfulsteriletiles` | 1619656080 | 1.0,1.1,1.2,1.3,1.4,1.5,1.6 |
| Config Applied Check | `taggerung.configappliedcheck` | 3103608609 | 1.4,1.5,1.6 |
| Craft with Color | `kathanon.craftwithcolor` | 2795998250 | 1.3,1.4,1.5,1.6 |
| Custom Fonts - Forked | `zcubekr.customfonts` | 3231727915 | 1.4,1.5,1.6 |
| CustomUIScales | `taggerung.customuiscales` | 2882372932 | 1.5,1.6 |
| Cybranian - Anima Obelisk | `dimonsever000.animaobelisk.specific` | 2614248835 | 1.3,1.4,1.5,1.6 |
| Cybranian - Events | `dimonsever000.events.specific` | 2599784515 | 1.3,1.4,1.5,1.6 |
| Damage Indicators [1.6] | `caesarv6.damageindicators` | 2016331497 | 1.1,1.2,1.3,1.4,1.5,1.6 |
| Deathpallcalypse | `phaserrave.deathpallcalypse` | 3253910772 | 1.5,1.6 |
| Development Mode Hotkey | `nightmare.devmodehotkey` | 3009274839 | 1.3,1.4,1.5,1.6 |
| Disable Raid Needs | `konstantynopolitaneczka.disableraidneeds` | 3568265578 | 1.5,1.6 |
| Disco! | `co.uk.epicguru.disco` | 2436747646 | 1.2,1.3,1.4,1.5,1.6 |
| Dismantle Ancient Junk | `proxyer.dismantleancientjunk` | 2871064871 | 1.3,1.4,1.5,1.6 |
| Divine Order | `botchjob.divineorder` | 3017163907 | 1.4,1.5,1.6 |
| Doormats | `alias.doormats` | 3239838811 | 1.5,1.6 |
| Dragons Descent | `onyxae.dragonsdescent` | 2026992161 | 1.1,1.2,1.3,1.4,1.5,1.6 |
| DragSelect | `telardo.dragselect` | 2599942235 | 1.3,1.4,1.5,1.6 |
| Drop Pod Raid Jammer | `kongkim.droppodjammer` | 3527131849 | 1.6 |
| Dubs Skylights | `dubwise.dubsskylights` | 833899765 | 1.0,1.1,1.2,1.3,1.4,1.5,1.6 |
| Dubs Skylights Addon | `bjr1984.dubsskylights.addon` | 2016959026 | 1.0,1.1,1.2,1.3,1.4,1.5,1.6 |
| Dubs Skylights Glass+Lights Patch | `maaxar.dubsskylights.glasslights.patch` | 1610803364 | 1.0,1.1,1.2,1.3,1.4,1.5,1.6 |
| Dynamic Diplomacy - Continued | `nilchei.dynamicdiplomacycontinued` | 3220299022 | 1.0,1.1,1.2,1.3,1.4,1.5,1.6 |
| Echoes of the Rim | `ghastly.echoesoftherim` | 3573196843 | 1.6 |
| ED-Embrasures (Continued) | `ganja.ed.embrasures` | 3277482616 | 1.0,1.1,1.2,1.3,1.4,1.5,1.6 |
| Epochs - Pottery | `det.epochspottery` | 3092351095 | 1.4,1.5,1.6 |
| Equipment Manager | `lordkuper.equipmentmanager` | 2790435986 | 1.3,1.4,1.5,1.6 |
| ESCP - Race Tools | `escp.racetools` | 3244642507 | 1.3,1.4,1.5,1.6 |
| ESCP - Skyshards | `sirmashedpotato.escp.skyshards` | 2814453057 | 1.3,1.4,1.5,1.6 |
| EvolvedOrgansRedux | `statistno1.evolvedorgansredux` | 3648390934 | 1.1,1.2,1.3,1.4,1.6 |
| Expanded Incidents (Continued) | `mlie.expandedincidents` | 2039064466 | 1.0,1.1,1.2,1.3,1.4,1.5,1.6 |
| Extract Any Plant | `romyashi.extractanyplant` | 2833838214 | 1.3,1.4,1.5,1.6 |
| F3: Spacer Jumpsuits and More | `hg.originals.f3` | 2776936670 | 1.3,1.4,1.5,1.6 |
| Fast regen 1.6 | `daniledman.fastregen` | 943925765 | 1.0,1.1,1.2,1.3,1.4,1.5,1.6 |
| Fast Spreading Grass | `shakeyourbunny.fastspreadinggrass` | 3541038010 | 1.6 |
| Faster Biosculpter Pod | `inglix.fasterbiosculptingpod` | 2576257954 | 1.3,1.4,1.5,1.6 |
| Faster Settlement Restock | `smeir.fastersettlementrestock` | 3363826406 | 1.5,1.6 |
| FeedinFishies | `jetharius.feedinfishies` | 3573713081 | 1.6 |
| Fertile Fields 1.6 | `jamaicancastle.rf.fertilefields` | 3225843229 | 1.1,1.2,1.3,1.4,1.5,1.6 |
| Field Administer | `jackdeg.fieldadminister` | 2472006801 | 1.4,1.5,1.6 |
| FIP - RobCo | `fip.robco` | 3563825876 | 1.6 |
| Fishing Is Fun | `jalapenolabs.rimworld.fishingisfun` | 3538562620 | 1.6 |
| Follow Target | `chaoticenrico.followtarget` | 3555423377 | 1.6 |
| Forced Xenogerm Implantation | `unknown.forcedxenogermimplantation` | 3586850201 | 1.6 |
| Full Gun Sell Price | `bdew.fullgunsellprice` | 1575464750 | 1.0,1.1,1.2,1.3,1.4,1.5,1.6 |
| Fungoids aren't that ugly! | `tookatee.fungoidnovomit` | 3433197206 | 1.5,1.6 |
| Gardens | `tk421storm.gardens` | 2869260174 | 1.3,1.4,1.5,1.6 |
| Gastronomy (Continued) | `orion.gastronomy` | 3509488152 | 1.6 |
| Glass+Lights | `nanoce.glasslights` | 826153738 | 1.0,1.1,1.2,1.3,1.4,1.5,1.6 |
| Graphics Settings+ | `telefonmast.graphicssettings` | 1678847247 | 1.1,1.2,1.3,1.4,1.5,1.6 |
| Grav-Shuttle | `turbopickle.gravshuttle` | 3528998097 | 1.6 |
| GravTech | `als.gravtech` | 3545374124 | 1.6 |
| Grazing Lands | `avilmask.grazinglands` | 1770268130 | 1.0,1.1,1.2,1.3,1.4,1.5,1.6 |
| Grouped Pawns Lists | `name.krypt.rimworld.pawntablegrouped` | 2340773428 | 1.1,1.2,1.3,1.4,1.5,1.6 |
| GrowingZoneIcons | `msws.growingzoneicons` | 3531165541 | 1.6 |
| Harvest Organs Post Mortem Continued | `smuffle.harvestorganspostmortem` | 1204502413 | 1.0,1.1,1.2,1.3,1.4,1.5,1.6 |
| Help me build | `andromeda.helpmebuild` | 3534699220 | 1.6 |
| HLRW - The Combine | `cgf1.hlrw.thecombines` | 3536753286 | 1.6 |
| Hospital | `adamas.hospital` | 2992224079 | 1.4,1.5,1.6 |
| Hospitality (Continued) | `orion.hospitality` | 3509486825 | 1.5,1.6 |
| Hospitality: Casino | `adamas.hospitalitycasino` | 2939292644 | 1.4,1.5,1.6 |
| Hospitality: Spa | `adamas.hospitalityspa` | 2971831654 | 1.4,1.5,1.6 |
| Hospitality: Storefront | `adamas.storefront` | 2952321484 | 1.4,1.5,1.6 |
| Hospitality: Vending machines | `adamas.vendingmachines` | 3014885065 | 1.4,1.5,1.6 |
| I Aint Building That | `taggerung.iaintbuildingthat` | 3118060751 | 1.4,1.5,1.6 |
| I Clearly Have Enough! (Continued) | `mlie.iclearlyhaveenough` | 2023661266 | 1.0,1.1,1.2,1.3,1.4,1.5,1.6 |
| Ignorance Is Bliss | `dame.ignorance` | 2554423472 | 1.4,1.5,1.6 |
| IV Drug Infuser | `akaster.ivdruginfuser` | 3484624947 | 1.5,1.6 |
| Joe's Tweaks | `joe.mo.tweaks` | 3458506170 | 1.5,1.6 |
| Just Ignore Me Passing (Continued) | `mlie.justignoremepassing` | 3503627342 | 1.0,1.1,1.2,1.3,1.4,1.5,1.6 |
| Keep On Linking | `marek15.keeponlinking` | 2717482472 | 1.3,1.4,1.5,1.6 |
| Kidnapped Pawns Die Less | `conit.kpdl` | 3308076464 | 1.5,1.6 |
| Kitchen Sink Fix for Vanilla Cooking Expanded | `linnun.kitchensinkfix` | 3288756218 | 1.3,1.4,1.5,1.6 |
| Lagless Lamps - C# | `jsin.laglesslamps` | 3467878826 | 1.5,1.6 |
| Lambda's Nuclear-Powered Stove | `lambda.nuclearstove` | 3347342950 | 1.5,1.6 |
| Landing On Asteroid 着陆小行星 | `runningbugs.landingonasteroid` | 3532991747 | 1.6 |
| Layered Wall Destruction | `keshash.layeredwalldestruction` | 3024527775 | 1.4,1.5,1.6 |
| Letter Permanent Injury | `buggy.rimworld.letterpermanentinjury` | 2592535960 | 1.3,1.4,1.5,1.6 |
| Level This! (Continued) | `dingzhen.levelthis` | 3443626025 | 1.5,1.6 |
| Level Up! | `krafs.levelup` | 1701592470 | 1.3,1.4,1.5,1.6 |
| Lightless Empyrean Reborn | `pphhyy.lightlessempyrean` | 3517488959 | 1.6 |
| Live With The Pain | `mlie.livewiththepain` | 2659985388 | 1.1,1.2,1.3,1.4,1.5,1.6 |
| Luci heals more! | `svcbot.lhm` | 965087548 | 1.2,1.3,1.4,1.5,1.6 |
| Luciferium Mood Boost | `p90forretail.nanomachines` | 2810755290 | 1.3,1.4,1.5,1.6 |
| Mashed's Bloodmoon | `sirmashedpotato.bloodmoon` | 3523186663 | 1.6 |
| Mech energy setting | `none1637.mechenergysetting` | 3238097300 | 1.5,1.6 |
| Mechanitor Orbital Platform | `zoarak.mechplat` | 3523146525 | 1.6 |
| MedPod | `sumghai.medpod` | 2153065191 | 1.4,1.5,1.6 |
| Miniaturization (Minify) | `cyber.miniaturization` | 2885885154 | 1.0,1.1,1.2,1.3,1.4,1.5,1.6 |
| Misc. Training | `haplo.miscellaneous.training` | 717575199 | 1.0,1.1,1.2,1.3,1.4,1.5,1.6 |
| Mod Options Sort | `superniquito.modoptionssort` | 2910865748 | 1.4,1.5,1.6 |
| Mooloh's Dnd Menagerie | `mooloh.dndmenagerie` | 2751849453 | 1.3,1.4,1.5,1.6 |
| Moonlight | `owlchemist.moonlight` | 3261311563 | 1.3,1.4,1.5,1.6 |
| More Creepjoiners | `metalocif.morecreeps` | 3434682604 | 1.5,1.6 |
| More Linkables | `4loris4.morelinkables` | 1103809207 | 1.0,1.1,1.2,1.3,1.4,1.5,1.6 |
| More Pause Events | `sirrandoo.mpe` | 1874708724 | 1.0,1.1,1.2,1.3,1.4,1.5,1.6 |
| More Prop Categories | `ferny.propscore` | 3167021055 | 1.4,1.5,1.6 |
| More Psycasts (Continued) | `mlie.morepsycasts` | 2036349987 | 1.1,1.2,1.3,1.4,1.5,1.6 |
| More Vanilla Fences | `jiopaba.fences` | 2546954423 | 1.3,1.4,1.5,1.6 |
| MoreAgingMultiplier | `vingy.moreagingmulitplier` | 2879214881 | 1.4,1.5,1.6 |
| MSS Tweaks and Fun | `mss.flavourpack` | 3379574408 | 1.5,1.6 |
| Museums | `nightmare.museums` | 3204176859 | 1.4,1.5,1.6 |
| Muzzle Flash | `issaczhuang.muzzleflash` | 2917732219 | 1.4,1.5,1.6 |
| My Little Planet | `oblitus.mylittleplanet` | 1117406550 | 0.19,1.0,1.1,1.2,1.3,1.4,1.5,1.6 |
| Myf's Vanilla Psycast Expanded Tweaks | `myf.vpe.tweaks` | 3328399391 | 1.5,1.6 |
| NANAME Floors | `oels.nanamefloors` | 3293767181 | 1.4,1.5,1.6 |
| New Anomaly Threats | `gogatio.newanomalythreats` | 3274840013 | 1.5,1.6 |
| New Limbs Needs Training | `mlie.newlimbsneedstraining` | 2439159828 | 1.1,1.2,1.3,1.4,1.5,1.6 |
| New Zone Tools (Continued) | `mlie.newzonetools` | 2377860105 | 1.1,1.2,1.3,1.4,1.5,1.6 |
| Nice Health Tab | `andromeda.nicehealthtab` | 3328729902 | 1.5,1.6 |
| No Burn Metal | `unon.noburnmetal` | 1923990111 | 1.0,1.1,1.2,1.3,1.4,1.5,1.6 |
| No Forced Slowdown | `thegoosebehindtheslaughter.noforcedslowdown` | 3223768532 | 1.5,1.6 |
| No Job Authors | `doug.nojobauthors` | 2009825774 | 1.1,1.2,1.3,1.4,1.5,1.6 |
| No More Lethal Damage Threshold | `jdalt.nmldt` | 2657551690 | 1.3,1.4,1.5,1.6 |
| No Summon Mech Threat Gizmo | `canon.nomechsummonergizmo` | 2889317343 | 1.4,1.5,1.6 |
| Not My Fault | `vesper.notmyfault` | 2870045856 | 1.3,1.4,1.5,1.6 |
| Nuclear revolution | `oddbase.nuclearrevolution` | 3536364597 | 1.6 |
| Nutrient Paste Love | `espio.pastelove` | 3386437690 | 1.5,1.6 |
| Odysseus Vacsuit Set | `kilo.odysseusvacset` | 3530182181 | 1.6 |
| Oktober's Scrap-Tek | `ok.scraptek` | 3122686960 | 1.4,1.5,1.6 |
| Optimization: Leathers - C# Edition | `scorpio.optimizationleathers` | 2591816333 | 1.3,1.4,1.5,1.6 |
| Optimization: Meats - C# Edition | `seohyeon.optimizationmeats` | 2542931556 | 1.4,1.5,1.6 |
| Optional Icons for Architect Icons | `proxyer.optionalicons4ai` | 1966995052 | 1.1,1.2,1.3,1.4,1.5,1.6 |
| Oracle's Miscellania | `oracle.miscellania` | 3279582979 | 1.6,1.5,1.4,1.3,1.2,1.1,1.0 |
| Orbital Platforms | `rashomcree.odyssey.orbitalplatforms` | 3525980713 | 1.6 |
| Outfit Builder Redux^2 | `annoprofi.outfitbuilderredux2` | 3589354596 | 1.6 |
| Outfit Stands Plus | `khamenman.outfitstandsplus` | 3545172389 | 1.6 |
| Outfitted 1.6 | `mitasamodel.outfitted` | 3546414006 | 1.6 |
| OverflowingFlowers | `sumika.overflowingflowers` | 3005103112 | 1.4,1.5,1.6 |
| Passion On Level Up Plus | `ayas.passiononlevelupplus` | 3526025445 | 1.5,1.6 |
| Pawn Education (Continued) | `mlie.pawneducation` | 2296533470 | 1.0,1.1,1.2,1.3,1.4,1.5,1.6 |
| Pawn Name Variety (Continued) | `mlie.pawnnamevariety` | 3548290568 | 1.1,1.2,1.3,1.4,1.5,1.6 |
| Pawn Target Fix | `fed1splay.pawntargetfix` | 2014789938 | 1.1,1.2,1.3,1.4,1.5,1.6 |
| Peer Pressure (Continued) | `densevoid.peerpressure` | 3605155621 | 1.4,1.5,1.6 |
| Perishable | `wtfomgjohnny.perishable` | 2294597530 | 1.6,1.5,1.4,1.3,1.2,1.1,1.0 |
| Pigs are smart | `gonezzle.pig` | 2837154037 | 1.3,1.4,1.5,1.6 |
| Planning Extended | `scherub.planningextended` | 2877392159 | 1.4,1.5,1.6 |
| PlantTreeIndoor | `planttreeindoor.serval.patch` | 3569744872 | 1.6 |
| Pocket Sand | `usagirei.pocketsand` | 2226330302 | 1.2,1.3,1.4,1.5,1.6 |
| Post-apocalyptic Shelters | `aoba.tentshelters` | 2444147091 | 1.1,1.2,1.3,1.4,1.5,1.6 |
| Power mill (1.4-1.6) | `thereallemon.powermill` | 2884054310 | 1.4,1.5,1.6 |
| pphhyy's Demigryphs Continued | `pphhyy.demigryphsmod` | 3540496928 | 1.6 |
| Practical Powercells | `mrwireman.powercell.01` | 3524003581 | 1.6 |
| Primitive Floors (Continued) | `zal.primitivefloors` | 2801265143 | 1.3,1.4,1.5,1.6 |
| Priority Treatment Ressurected | `tk421storm.prioritytreatmentressurected` | 3009738919 | 1.4,1.5,1.6 |
| Proselytizing Never | `yoann.proselytizingnever` | 3053650876 | 1.6,1.5,1.4 |
| Prosthetic No Missing Body Parts (Continued) | `mlie.prostheticnomissingbodyparts` | 2739055353 | 1.1,1.2,1.3,1.4,1.5,1.6 |
| Psychic Sensitivity Affects More (VPE) | `mute.vpesensitivity` | 2881380497 | 1.6 |
| RBSE | `rah.rbse` | 850429707 | 1.3,1.4,1.5,1.6 |
| Reasonable Components | `twistedpacifist.reasonablecomponents` | 1542915888 | 1.0,1.1,1.2,1.3,1.4,1.5,1.6 |
| ReBuild: Doors and Corners | `rebuild.cotr.doorsandcorners` | 3262718980 | 1.5,1.6 |
| Recipe icons (Continued) | `mlie.recipeicons` | 2904906618 | 1.0,1.1,1.2,1.3,1.4,1.5,1.6 |
| Recon And Discovery (Continued) | `mlie.reconanddiscovery` | 2035131107 | 1.1,1.2,1.3,1.4,1.5,1.6 |
| Recubes Your Cube | `mss.recube` | 3220139435 | 1.5,1.6,1.7 |
| Recycle 1.5 | `sneaks.recycle` | 1534883539 | 1.0,1.1,1.2,1.3,1.4,1.4,1.5,1.6 |
| Repair Station | `gunseeker.repairstation` | 3534893110 | 1.6 |
| ReplaceLib | `ferny.replacelib` | 3417393194 | 1.5,1.6 |
| Replimat | `sumghai.replimat` | 1715402900 | 1.4,1.5,1.6 |
| Replimat Meals | `sumghai.replimatmeals` | 3274344708 | 1.5,1.6 |
| Resurrect Enemy Mechanoids | `nikidigi.resurrectenemymechanoids` | 2882468335 | 1.4,1.5,1.6 |
| Reunion | `kyrun.reunion` | 1985186461 | 1.0,1.1,1.2,1.3,1.4,1.5,1.6 |
| Rim-Effect Renegade: Asari and Reapers | `rimeffectrenegade.asarireapers` | 3473370728 | 1.5,1.6 |
| Rim-Effect Renegade: Core | `rimeffectrenegade.core` | 3473370247 | 1.5,1.6 |
| Rim-Effect Renegade: Drell | `rimeffectrenegade.drell` | 3473371103 | 1.5,1.6 |
| Rim-Effect Renegade: Extended Cut | `rimeffectrenegade.extendedcut` | 3473382290 | 1.5,1.6 |
| Rim-Effect Renegade: N7 | `rimeffectrenegade.n7` | 3473371554 | 1.5,1.6 |
| Rimano: Architect Icons | `deadmano.rimanoarchitecticons` | 3212495112 | 1.3,1.4,1.5,1.6 |
| RimSaves | `arandomkiwi.rimsaves` | 1713367505 | 1.0,1.1,1.2,1.3,1.4,1.5,1.6 |
| RimScent | `reo.rimscent` | 3645569466 | 1.6 |
| RimTek Core | `deon.rimtek.core` | 3500429104 | 1.5,1.6 |
| RimTek DigiPal | `deon.rimtek.digipal` | 3500443258 | 1.5,1.6 |
| RimTek DocMate | `deon.rimtek.docmate` | 3500863752 | 1.5,1.6 |
| RimThemes | `arandomkiwi.rimthemes` | 1668983184 | 1.0,1.1,1.2,1.3,1.4,1.5,1.6 |
| Rottable Filter | `tests.rottable` | 2845056427 | 1.3,1.4,1.5,1.6 |
| RPG Adventure Flavour Pack - Fork | `joe.rpgadventureflavour.fork` | 3342554570 | 1.5,1.6 |
| RPG Dialog | `esvn.rpgdialog` | 3547971440 | 1.5,1.6 |
| RuntimeGC [1.6] fork2 | `louize.runtimegc.fork` | 3528496623 | 1.5,1.6 |
| RWLayout | `name.krypt.rimworld.rwlayout.alpha2` | 2209393954 | 1.1,1.2,1.3,1.4,1.5,1.6 |
| Scavenging | `romyashi.scavenging` | 3108829323 | 1.4,1.5,1.6 |
| Seed Fish Tool | `dhl.seedfish` | 3549336894 | 1.6 |
| SeedsPlease: Lite Redux | `evyatar108.seedspleaseliteredux` | 3523459853 | 1.4,1.5,1.6 |
| Setosa's Power Tools | `setosa.power.tools` | 3526160222 | 1.6 |
| SF Comfy Meditation (Continued) | `mlie.sfcomfymeditation` | 3432727841 | 1.3,1.4,1.5,1.6 |
| Simple FX: Smoke | `owlchemist.simplefx.smoke2` | 3261314247 | 1.3,1.4,1.5,1.6 |
| Simple Learning (Continued) | `fox.simplelearning` | 3580464748 | 1.3,1.4,1.5,1.6 |
| Simple Make Reinforced Barrel 1.6 | `bbbbilly.simplemakereinforcedbarrel` | 3540205861 | 1.5,1.4,1.6 |
| Skill Bionics | `drwalz.contentmodnumberthreeskillbionics` | 3228526665 | 1.5,1.6 |
| Sleep Meditation | `sl4vp0wer.sleepmeditation.1.5` | 3238976509 | 1.5,1.6 |
| Slightly Faster Mech Gestator | `shepirotgamer.slightlyfastermechgestator` | 3546705271 | 1.4,1.5,1.6 |
| Smaller radius for Anima Trees, Shrines and Animus Stones | `longman.smallerradiusforanimatreesandshrines` | 2812513517 | 1.3,1.4,1.5,1.6 |
| Smart Farming | `owlchemist.smartfarming` | 3220129183 | 1.3,1.4,1.5,1.6 |
| Smart Meditation | `puremj.mjrimmods.smartmeditation` | 2800676538 | 1.3,1.4,1.5,1.6 |
| Smart Odyssey | `sarg.smartodyssey` | 3522762411 | 1.6 |
| Smart Speed | `sarg.smartspeed` | 1504723424 | 1.6,1.5 |
| Smarter Construction | `dhultgren.smarterconstruction` | 2202185773 | 1.1,1.2,1.3,1.4,1.5,1.6 |
| Smarter Deconstruction and Mining (Continued) | `mlie.smarterdeconstructionandmining` | 3261302741 | 1.2,1.3,1.4,1.5,1.6 |
| Sometimes Raids Go Wrong | `marvinkosh.sometimesraidsgowrong` | 1551336515 | 1.0,1.1,1.2,1.3,1.4,1.5,1.6 |
| Spacer Arsenal | `det.spacerarsenal` | 3247891820 | 1.5,1.6 |
| Spacer Shields 1.6 | `lts.ps` | 3536995307 | 1.5,1.6 |
| Spread The Word (Continued) | `mlie.spreadtheword` | 3287847068 | 1.3,1.4,1.5,1.6 |
| Start Date | `pershonkey.startdate` | 2991015129 | 1.4,1.5,1.6 |
| Steve's Walls Continued [1.6] | `randallboggs.steveswalls` | 3525402809 | 1.6 |
| Stop, Drop, And Roll! [BAL] | `balistafreak.stopdropandroll` | 2362707956 | 1.2,1.3,1.4,1.5,1.6 |
| Stranger In Black Techlevel | `zal.sibtl` | 3428237149 | 1.5,1.6 |
| Stronger Wings | `mbee.strongerwings` | 3185383404 | 1.4,1.5,1.6 |
| Stuff List (Continued) | `mlie.stufflist` | 2798767227 | 1.1,1.2,1.3,1.4,1.5,1.6 |
| Sun Lamp Power | `sun.reducer` | 738063560 | 1.0,1.1,1.2,1.3,1.4,1.5,1.6 |
| SZ_Atmospheric Events | `void.szatmosphericevents` | 1874676885 | 0.19,1.0,1.1,1.2,1.3,1.4,1.5,1.6 |
| T's Conversion Staff | `trickity.conversion.staff` | 2890481507 | 1.4,1.5,1.6 |
| Tab-sorting | `mlie.tabsorting` | 2138635288 | 1.1,1.2,1.3,1.4,1.5,1.6 |
| Taste of Vanilla - The Brotherhood Compendium | `icc.tov.tbc` | 3008804056 | 1.0,1.1,1.2,1.3,1.4,1.5,1.6 |
| Tastier Vanilla Clothes | `al9000.tvc` | 2808554143 | 1.3,1.4,1.5,1.6 |
| The Brotherhood Compendium 1.6 | `altushka.boscompendium` | 3571412768 | 1.1,1.2,1.3,1.4,1.5,1.6 |
| The Profaned | `botchjob.profaned` | 3202008037 | 1.4,1.5,1.6 |
| Thermal Well Excavation | `tolgrim.thermalwellexcavation` | 3656836896 | 1.5,1.6 |
| Time Kills | `silencer59.timekills` | 2374079539 | 1.2,1.3,1.4,1.5,1.6 |
| Toggleable Overlays | `owlchemist.toggleableoverlays` | 3261316725 | 1.3,1.4,1.5,1.6 |
| Toggleable Readouts | `owlchemist.toggleablereadouts` | 3261317086 | 1.3,1.4,1.5,1.6 |
| Toggleable Shields | `owlchemist.toggleableshields` | 3261317430 | 1.3,1.4,1.5,1.6 |
| Trading Control | `tradingcontrol.tad.rimworld.core` | 2007107588 | 1.1,1.2,1.3,1.4,1.5,1.6 |
| Tribal Backstories | `shenanigans.tribalbackstories1.4` | 2879649038 | 1.4,1.5,1.6 |
| Tribal Essentials Reborn | `zal.tribalessentials` | 2597790751 | 1.3,1.4,1.5,1.6 |
| Un-Limited Reborn | `nuanki.unlimitedreborn` | 3295368629 | 1.5,1.6 |
| Uniform Growing Zone Tool | `asmallrabbit.uniformgrowzone` | 1898969926 | 1.3,1.4,1.5,1.6 |
| Unlimited Mechanitor Command Range | `swwu.mechanitorcommandrange` | 2878895195 | 1.4,1.5,1.6 |
| USCM - Core | `hiztaar.essential.uscmcore` | 726855894 | 1.0,1.1,1.2,1.3,1.4,1.5,1.6 |
| Ushankas Necroa Archovirus | `ushanka.necroaarchovirus` | 3531035748 | 1.6 |
| Vanilla Arsenal | `det.vanillaarsenal` | 3273371966 | 1.5,1.6 |
| Vanilla Books Expanded | `vanillaexpanded.vbookse` | 2193152410 | 1.4,1.5,1.6 |
| Vanilla Brewing Expanded - Coffees and Teas | `vanillaexpanded.vbrewecandt` | 2275449762 | 1.4,1.5,1.6 |
| Vanilla Fishing Expanded | `vanillaexpanded.vcef` | 1914064942 | 1.6,1.4,1.5 |
| Vanilla Fishing Expanded - Fishing Treasures AddOn | `vanillaexpanded.vcefaddon` | 2468543398 | 1.6,1.4,1.5 |
| Vanilla Food Variety Expanded | `vanillaexpanded.vanillafoodvarietyexpanded` | 3334272487 | 1.5,1.6 |
| Vanilla Nutrient Paste Expanded | `vanillaexpanded.vnutriente` | 2920385763 | 1.4,1.5,1.6 |
| Vanilla Nutrient Paste Expanded: Reimagined Progression | `mrhydralisk.vnpereimaginedprogression` | 3530651481 | 1.5,1.6 |
| Vanilla Psycasts Expanded | `vanillaexpanded.vpsycastse` | 2842502659 | 1.4,1.5,1.6 |
| Vanilla Psycasts Expanded - Hemosage | `vanillaexpanded.vpe.hemosage` | 2990596478 | 1.4,1.5,1.6 |
| Vanilla Psycasts Expanded - Puppeteer | `vanillaexpanded.vpe.puppeteer` | 3033779606 | 1.4,1.5,1.6 |
| Vanilla Recycling Expanded | `vanillaexpanded.recycling` | 3155781848 | 1.4,1.5,1.6 |
| Vanillafy Floors | `nakomaru.vanillafyfloors` | 3219321678 | 1.4,1.5,1.6 |
| VGP Vegetable Garden | `dismarzero.vgp.vgpvegetablegarden` | 2007061826 | 1.0,1.1,1.2,1.3,1.4,1.5,1.6 |
| Visible Cybernetics | `ghastly.visualcybernetics` | 3262173908 | 1.5,1.6 |
| Visible Raid Points | `visibleraidpoints.1trickpwnyta` | 2562730174 | 1.3,1.4,1.5,1.6 |
| VPE - Anima | `vpe.anima.sentinel` | 3462136587 | 1.5,1.6 |
| VPE - Horaxian | `vpe.horaxian.sentinel` | 3456508582 | 1.5,1.6 |
| VPE - Luminis | `vpe.luminis.sentinel` | 3559834496 | 1.6 |
| VPE - Ranger | `aranmaho.rangerclass` | 2927626324 | 1.5,1.6 |
| VPE - Voidweaver | `vpe.voidweaver.sentinel` | 3467913565 | 1.5,1.6 |
| VPE Self-Cast This! Plus Temp 1.6 | `ctrlaltfunk.vpeselfcastpluspatch` | 3519928832 | 1.4,1.5,1.6 |
| VPE: Revert Some Nerfs (Continued) | `steve.vpe.revertsomenerf` | 3484509389 | 1.4,1.5,1.6 |
| Wall light Relic | `wall.light.relic` | 3220394219 | 1.5,1.6 |
| Wall mounted solar panels | `xale86.wallsolarpanels` | 3545934731 | 1.6 |
| Wall Sun Lamp | `xercaine.wallsunlamp` | 3234498246 | 1.5,1.6 |
| Walls are solid | `victor.wallsaresolid` | 2896548513 | 1.4,1.5,1.6 |
| Who shot my leg off? | `tixiv.whoshotmylegoff` | 3491552121 | 1.5,1.6 |
| Wildheart Psycast | `aranmaho.ravenouseye.wildhunter.psycast` | 3043229067 | 1.4,1.5,1.6 |
| Wololoo - Better Conversion and Recruitment | `redmattis.betterconversion` | 3108763487 | 1.4,1.5,1.6 |
| World Pawn Cleaner | `cedaro.worldpawncleaner` | 3181327333 | 1.4,1.5,1.6 |
| Worldbuilder | `ferny.worldbuilder` | 3522102833 | 1.6 |
| WVC - Ultra Expansion II | `wvc.sergkart.ultraexpansion` | 3107443670 | 1.4,1.5,1.6 |
| WVC - Work Modes | `wvc.sergkart.biotech.moremechanoidsworkmodes` | 2888380373 | 1.4,1.5,1.6 |
| Yet another prosthetic expansion mod - Core | `mrkociak.yetanotherprostheticexpansionmodcore` | 2808872704 | 1.3,1.4,1.5,1.6 |
| You Are So Beautiful | `cn.youaresobeautiful` | 3576178532 | 1.6 |
| You Drive, I Sleep | `spacemoth.youdriveisleep` | 3324430833 | 1.5,1.6 |
| 剧本扩展:小行星空岛生存 | `hdz.asteroidsurvival` | 3527737313 | 1.6 |
