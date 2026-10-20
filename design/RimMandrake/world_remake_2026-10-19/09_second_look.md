# 09 Second look: what is KEPT (DEV and TEST) and the 12 HOLDs

Method (all counts MEASURED by script over `07_profile_assignment.tsv` joined to `design/RimMandrake/mod_audit/facts/mod_facts.jsonl`, 2026-10-19):
205 DEV/DEV-INSTR/TEST rows; less 6 Ludeon and 62-odd of ours = **138 third-party mods** audited. For each: (a) `dependants_detail` kinds from OUR mods
(`hard_dep`, `class_ref`, `def_ref`, `mayrequire`, `patch_xpath`, `findmod`, `load_after`), (b) retained third-party dependants, (c) `src/` literal hits excluding
`northstar/` result JSON (those only list the loaded mod set, e.g. 18 hits for every mod, so they prove nothing), (d) our About.xml `modDependencies`
(parsed from `src/**/About/About.xml`). Cites are `mod_facts.jsonl:<line>`. Soft-only means `load_after`/`patch_xpath`/`findmod` and nothing else: a guarded patch that matches
nothing when the mod is absent, so the mod is not needed to LOAD or TEST our content.

## 1. Headline

- **54 mods (888 MB estimated decoded textures, 2214 defs; facts fields `texture_decoded_mb_est`, `def_total`) have no hard, class or def tie from us and no retained
  hard dependant.** None is a hard `modDependency` of any of our About.xml files (parsed). They are 54 of the 88 TEST-only rows. 4 of them (GravTide, 3 RimTek) have
  zero tie of any kind and are DROP candidates; 50 are MOVE-TO-SHIP (out of DEV/TEST/AUTHORING loads; still in SHIP).
- **The DEV profile is tighter than TEST**: of 49 third-party DEV rows only 2 can be demoted on evidence (section 3); the C1 label "our content hard-depends on it" is
  **unsupported for 6 of them** (section 3 table).
- **Load cost / log errors among kept mods** (facts `log_error_occurrences`; `tps_cost` is UNMEASURED for every mod): only 3 of 134 DEV/TEST third-party mods log errors:
  Dubs Bad Hygiene Lite 3 (facts:122, DEV), Rimfridge 2 (facts:262, DEV), Rim of Madness Bones 1 (facts:258, TEST). Heaviest by decoded textures:
  Outland Genetics 1499 MB (facts:484), Big and Small Core 1058 (facts:479), Alpha Memes 1029 (facts:53), Outer Rim Core 704 (facts:483), Genetics Expanded 477 (facts:467);
  whole DEV+TEST third-party set 10297 MB estimated. 07 lists further crash PROBLEMs (Research Reinvented HIGH, Vehicle Framework HIGH, Genetics Expanded startup crash).

## 2. TEST candidates (54): out of DEV/TEST/AUTHORING, keep in SHIP

Rules applied (script, then excluded): world-borne (Go Explore, Trader ships, Caravan Adventures, Faction Territories, Outposts x2, VFE Pirates, Ancient Mining, GTG Trader Core)
and scenario-identity (Ideology Scavenger Role, Xenotype Spawn Control, Dubs Thirst, Bigger Gravships) rows stay. Any mod with `def_ref`/`class_ref`/`mayrequire`/`hard_dep` from ours also stays.
Chains: a library moves only if all its retained dependants move (CQF with Dungeon Pack; Minerals Framework with Sparkle; VAE Accessories with More Utility Packs; Custom Ritual Framework with Rituals module; RimTek Core with DigiPal/DocMate).

| mod | packageId | evidence | risk | recommend |
|---|---|---|---|---|
| Better Beggars (Continued) | `mlie.betterbeggars` | mod_facts.jsonl:66; ours: none | low | MOVE-TO-SHIP |
| Breeding Ritual | `gulmadred.breedingritual` | mod_facts.jsonl:81; ours: rut.pawnflavor:load_after+patch_xpath+findmod | low | MOVE-TO-SHIP |
| Crafting Spot Slave Gear | `heatherathebyne.craftingspotslavegear` | mod_facts.jsonl:94; ours: none | low | MOVE-TO-SHIP |
| Custom Quest Framework | `hailuan.customquestframework` | mod_facts.jsonl:97; ours: none | follows mlie.dungeonpack (only retained dependant, facts:97) | MOVE-TO-SHIP |
| Custom Ritual Framework | `thesepeople.ritualattachableoutcomes` | mod_facts.jsonl:16; ours: none | library, follows ritualsmodule | MOVE-TO-SHIP |
| Death Rattle Continued [1.2+] | `troopersmith1.deathrattle` | mod_facts.jsonl:104; ours: none | low | MOVE-TO-SHIP |
| Dungeon Pack (Continued) | `mlie.dungeonpack` | mod_facts.jsonl:390; ours: rsw.armoury:load_after+patch_xpath+findmod; rut.researchretag:load_after+patch_xpath | site/quest content (dungeons) may be world-borne: check before moving | MOVE-TO-SHIP |
| Fortifications - Neolithic | `aoba.fortress.neolithic` | mod_facts.jsonl:141; ours: none | low | MOVE-TO-SHIP |
| Giddy-Up 2 - Continued | `memegoddess.giddyup` | mod_facts.jsonl:143; ours: none | low | MOVE-TO-SHIP |
| Glowing eyes genes | `lts.geg` | mod_facts.jsonl:144; ours: none | low | MOVE-TO-SHIP |
| GravTide | `gravtide.mod` | mod_facts.jsonl:163; ours: none | C1 "kept until replicated" but zero ours refs; 753 defs; NRE; north-star runs listed it as loaded, so test baselines shift | DROP (C1 zero refs; owner confirms) |
| High Tech Helmets Give Tox Gas Resistance | `ael.tua.helmetsaddtoxresistance` | mod_facts.jsonl:152; ours: none | low | MOVE-TO-SHIP |
| Hunting Traps | `hazn.huntingtraps` | mod_facts.jsonl:155; ours: rut.researchretag:load_after+patch_xpath | low | MOVE-TO-SHIP |
| Intimacy - Socio Butterfly | `lovelydovey.recreation.witheuterpe` | mod_facts.jsonl:492; ours: none | low | MOVE-TO-SHIP |
| Just Leave Already | `timuttie.justleavealready.fork.mitasamodel` | mod_facts.jsonl:184; ours: none | low | MOVE-TO-SHIP |
| Mercer's Backpacks (Continued) | `mlie.mercerbackpacks` | mod_facts.jsonl:204; ours: none | low | MOVE-TO-SHIP |
| Minerals Framework | `zacharyfoster.mineralsframework` | mod_facts.jsonl:403; ours: none | low | MOVE-TO-SHIP |
| Minerals Sparkle | `zacharyfoster.mineralssparkle` | mod_facts.jsonl:445; ours: none | low | MOVE-TO-SHIP |
| Mines 2.0 | `cain.mineshaft` | mod_facts.jsonl:209; ours: rut.researchretag:load_after+patch_xpath | low | MOVE-TO-SHIP |
| More Slavery Stuff | `garryflowers.moreslaverystuff` | mod_facts.jsonl:220; ours: rut.pawnflavor:load_after+patch_xpath+findmod | low | MOVE-TO-SHIP |
| More Utility Packs (Continued) | `zal.moreutilitypacks` | mod_facts.jsonl:406; ours: rut.researchretag:load_after+patch_xpath | low | MOVE-TO-SHIP |
| Orc Clan + Xenotype | `karew.orcclan` | mod_facts.jsonl:234; ours: rut.patches:load_after+patch_xpath+findmod | OrcClan_GamorreanRename.xml renames its content; if Gamorrean xenotype is world-borne keep | MOVE-TO-SHIP |
| Precepts and Memes - Rituals module (Continued) | `mlie.preceptsandmemesritualsmodule` | mod_facts.jsonl:410; ours: none | ideology precepts: if the Salvation ideo (.rid) names its defs, keep | MOVE-TO-SHIP |
| Prison Labor | `avius.prisonlabor` | mod_facts.jsonl:447; ours: rut.pawnflavor:load_after+patch_xpath+findmod | low | MOVE-TO-SHIP |
| Prisoner Realism | `legator.prisonerrealism` | mod_facts.jsonl:462; ours: rut.pawnflavor:load_after+patch_xpath+findmod | low | MOVE-TO-SHIP |
| Prisoners Should Fear Turrets | `mlie.prisonersshouldfearturrets` | mod_facts.jsonl:243; ours: none | low | MOVE-TO-SHIP |
| Psyshrooms | `lambda.psykshroom` | mod_facts.jsonl:411; ours: none | low | MOVE-TO-SHIP |
| Raider Swarm Compression | `ingendum.raiderswarmcompression` | mod_facts.jsonl:247; ours: none | raid behaviour, not world content | MOVE-TO-SHIP |
| RimTek Core | `deon.rimtek.core` | mod_facts.jsonl:264; ours: none | low | DROP (C1 zero refs; owner confirms) |
| RimTek DigiPal | `deon.rimtek.digipal` | mod_facts.jsonl:419; ours: none | low | DROP (C1 zero refs; owner confirms) |
| RimTek DocMate | `deon.rimtek.docmate` | mod_facts.jsonl:420; ours: none | low | DROP (C1 zero refs; owner confirms) |
| RimTraits - General Traits | `sierra.rt.generaltraits` | mod_facts.jsonl:265; ours: none | low | MOVE-TO-SHIP |
| Romance & Intimacy On The Rim | `mianreplicate.romanceandintimacyontherim` | mod_facts.jsonl:267; ours: none | low | MOVE-TO-SHIP |
| Romance On The Rim | `telardo.romanceontherim` | mod_facts.jsonl:421; ours: rut.pawnflavor:load_after+patch_xpath+findmod | low | MOVE-TO-SHIP |
| Roofed Scanning 1.6 | `kupie.isjustdoingitlive.plzdonthateme.roofedscanning` | mod_facts.jsonl:268; ours: none | low | MOVE-TO-SHIP |
| RunAndGun - Continued | `memegoddess.runandgun` | mod_facts.jsonl:270; ours: none | low | MOVE-TO-SHIP |
| Simple Slavery Collars | `tribeagle.simpleslaverycollars` | mod_facts.jsonl:465; ours: rut.pawnflavor:load_after+patch_xpath+findmod | low | MOVE-TO-SHIP |
| Simple sidearms | `petetimessix.simplesidearms` | mod_facts.jsonl:464; ours: none | low | MOVE-TO-SHIP |
| SimpleStairs (Fork) | `rw.mod.simplestairs` | mod_facts.jsonl:544; ours: none | low | MOVE-TO-SHIP |
| Slave Outfits [1.6] | `usgiyi.slaveoutfits` | mod_facts.jsonl:283; ours: none | low | MOVE-TO-SHIP |
| Stonecutting Extended | `scherub.stonecuttingextended` | mod_facts.jsonl:424; ours: none | low | MOVE-TO-SHIP |
| Tech Level Enforcement | `summersausages2ttv.techlevelenforcement` | mod_facts.jsonl:304; ours: none | low | MOVE-TO-SHIP |
| Toddlers | `cyanobot.toddlers` | mod_facts.jsonl:425; ours: none | changes pawn lifestages: affects pawn gen in the start save, compare census | MOVE-TO-SHIP |
| Tunneler Expanded | `error277.tunneler.expanded` | mod_facts.jsonl:317; ours: rut.researchretag:load_after+patch_xpath | low | MOVE-TO-SHIP |
| Universal Pregnancy | `universalpregnancy.1trickpwnyta` | mod_facts.jsonl:320; ours: none | pawn hediffs; census before save | MOVE-TO-SHIP |
| Vanilla Apparel Expanded — Accessories | `vanillaexpanded.vaeaccessories` | mod_facts.jsonl:323; ours: rm.patches:load_after | low | MOVE-TO-SHIP |
| Vanilla Ideology Expanded - Relics and Artifacts | `vanillaexpanded.ideo.relicsandartifacts` | mod_facts.jsonl:344; ours: none | low | MOVE-TO-SHIP |
| Weapon Racks | `aelanna.weaponracks` | mod_facts.jsonl:365; ours: none | low | MOVE-TO-SHIP |
| Wing's Meaningful Parties | `winggar.meaningfulparties` | mod_facts.jsonl:369; ours: rm.biomes:patch_xpath; rm.luminouspigment:patch_xpath; rsw.jawavoice:patch_xpath; rsw.patches:patch_xpath; rut.patches:patch_xpath; rut.pawnflavor:patch_xpath | six of our mods PATCH it (patch_xpath, no findmod): patches silently match nothing when it is absent, harmless | MOVE-TO-SHIP |
| [1.1]TO[1.6]MultipleTraders | `04.23.2020` | mod_facts.jsonl:24; ours: none | low | MOVE-TO-SHIP |
| [AP] Hunting Meme | `ap.huntingmeme` | mod_facts.jsonl:25; ours: none | low | MOVE-TO-SHIP |
| [RF] Rumor Has It.... (Continued) | `mlie.rfrumorhasit` | mod_facts.jsonl:33; ours: rut.patches:load_after+patch_xpath | low | MOVE-TO-SHIP |
| [sbz] Fridge | `sbz.neatstoragefridge` | mod_facts.jsonl:36; ours: none | low | MOVE-TO-SHIP |
| [sbz] Gravship Storage | `sbz.gravshipstorage` | mod_facts.jsonl:37; ours: none | low | MOVE-TO-SHIP |
**Not moved on purpose (stay TEST, flagged):** `aoba.fortress.industrial` (facts:393) + `vanillaexpanded.vfearchitect` (facts:331, 109 MB, HOLD) + `aoba.framework`: only soft ties from
`rsw.armoury`, but `rut.researchretag` has a `def_ref` to it; if ResearchRetag is told to guard it, the whole chain (358 MB) moves too -> **MOVE-TO-SHIP after one guard check**.
`sihv.rombonesport` (facts:258): `def_ref` from `rsw.swbestiary` (mayrequire), `rut.doctrine`, `rut.greentideraidant` -> KEEP.
`llunak.moreprecepts` (218 defs): `JawaTribes.xml:161` says its NomadPatch relabels a meme we use -> KEEP until that line is settled.

## 3. DEV candidates

| mod | packageId | evidence | risk | recommend |
|---|---|---|---|---|
| Vanilla Factions Expanded - Tribals | `oskarpotocki.vfe.tribals` | facts:329: ours only `rsw.patches` + `rut.pawnflavor` load_after/patch/findmod and `rut.researchretag` def_ref; no class_ref/hard_dep. 07 calls it "C1 hard-depends" | low-med: ResearchRetag def_ref (a TEST-level mod) | DEMOTE DEV -> TEST |
| Research Reinvented | `petetimessix.researchreinvented` | facts:254: `rm.wreckedmachines` mayrequire def_ref, `rut.researchretag` patch_xpath, no hard_dep/class_ref; 07 records a HIGH crash (Stepping Stones) | med: Wrecked Machines (DEV) research gate falls back; every DEV test sees the default tech tree | DEMOTE DEV -> TEST, owner ruling (it is the research UI everything is tuned against) |
| Alpha Memes | `sarg.alphamemes` | facts:53: `JawaTribes.xml:141`, `JawaJunkers.xml:140`, `JawaHuttCartel.xml:138`, `RUT_Cauldron.xml:131` all MayRequire | Faction meme lists = world-borne ideology; 1029 MB, 2216 defs | KEEP (world-borne); biggest cost item, note for owner |
| Bubbles | `jaxe.bubbles` | `src/RimStarWars/JawaVoice/README.md:114`: removing it silently stops Jawaese speech display | UI only, but README ties it | KEEP |
| Deep Orbit | `broms.deeporbit` | facts:457; 05 §2 (fixtures need Orbit2 layer) | fixtures fail to load | KEEP until fixtures retire |
| LWM Deep Storage / Rimfridge | `lwm.deepstorage`, `rimfridge.kv.rw` | facts:401 `neronix17.outerrim.core` class_ref (no About dep); rimfridge is its library, errors 2 (facts:262) | soft class ref could NRE without it | KEEP while Outer Rim Core stays |
| Cherry Picker | `owlchemist.cherrypicker` | facts:13; 07 reason (cuts shape the def set) | removing it un-cuts defs | KEEP |
| Archon / Genie / Saurid, Det's Keshig, Outer Rim Empire+Rebels, Landmarks, VFE Security, Kikohi Jewelry, Dubs Lite | see `dependants_detail` | `def_ref` from `rsw.starwarsraces`, `rm.inhabited`, `rm.biomes`, `rut.injections`, `rsw.trophycraft` (all DEV) | real | KEEP (claims hold) |
| VFE Core, Harmony, Vehicle Framework (VVE chain), Humanoid Alien Races, GenesExpandedEyes, Integrated Genes, Outland Genetics, Big and Small x2, XML Extensions, ADS, EBSG, Rimthemes, SpeakUp, Doors Expanded, JecsTools, Lightsaber, VFE Factory, Lovely Dovey Rosaline/Euterpe, Tabula Rasa | parsed About.xml | `hard_dep`/`class_ref` from `rsw.*`/`rut.menushell`/`rm.wreckedmachines` (section header query) | real | KEEP |

Unsupported-label note: for `lovelydovey.sex.withrosaline` the tie is `def_ref` (facts:491) not hard_dep; `mlie.advancedbiomes`, `zylle.morevanillabiomes`, `ironscruff.primordialgeysers` are mayrequire/def_ref only (guarded) yet `rm.biomes`/`rut.patches`/`RUT_TheForge.xml:174` use their content, so they are biome-cast content: KEEP.

## 4. The 12 HOLDs re-checked (05_drop_closure.md section 2)

| mod | packageId | finding | verdict |
|---|---|---|---|
| Alien Worlds Framework | `7f.alienworlds` | already profile AUTHORING (07 tsv), so it costs no test load; our only ties are `rsw/rut.patches` load_after (facts:47) | KEEP in AUTHORING; droppable the day the repaint is finished and no one re-generates |
| Alien Worlds Tidally Locked | `7f.alienworlds.tidallylocked` | AUTHORING; ties load_after and one patch_xpath (facts:381) | same |
| Sensible Factions | `boots.sensiblefactions` | AUTHORING; `dependants_detail` EMPTY (facts:278) | **DROP-eligible after the paint**; no one names it |
| My Little Planet | `oblitus.mylittleplanet` | AUTHORING; only `PlanetPresetPrime` load_after (facts:223) | KEEP until the planet size is baked |
| Deep Orbit | `broms.deeporbit` | DEV; no dependants at all (facts:457); needed by fixtures only | KEEP until fixtures retire, then DROP |
| Biomes! Framework | `biomesteam.coreframework` | 05 is STALE: `biomesteam.biomesfossils` is now DROP-DEEPER (07 tsv), so the only retained dependant is `zylle.morevanillabiomes` class_ref (facts:78) | follows More Vanilla Biomes (below) |
| More Vanilla Biomes (not a HOLD, but gates the one above) | `zylle.morevanillabiomes` | record `world/ASHKARR_WORLDMAP_tiles.csv` (a RECORD; parsed with csv) has 222 of 21872 tiles on `ZBiome_Grasslands`; ours are all MayRequire-guarded (`OasisMutator_DesertOasis.xml:61`) | KEEP until the repaint; then DROP both |
| Custom Quest Framework | `hailuan.customquestframework` | only retained dependant `mlie.dungeonpack` (hard_dep+class_ref+def_ref, facts:97); Dungeon Pack itself has soft ties only (facts:390) | **DROPPABLE WITH Dungeon Pack** (both MOVE-TO-SHIP/DROP on an owner word on dungeons) |
| Vanilla Apparel Expanded - Accessories | `vanillaexpanded.vaeaccessories` | retained dependant only `zal.moreutilitypacks` (hard_dep), which has soft ties only (facts:323, 406) | **DROPPABLE WITH More Utility Packs** |
| Minerals Framework | `zacharyfoster.mineralsframework` | only retained dependant Minerals Sparkle, zero ties from us (facts:403, 445) | **DROPPABLE WITH Minerals Sparkle** |
| Vanilla Furniture Expanded - Architect | `vanillaexpanded.vfearchitect` | retained dependant `aoba.fortress.industrial` class/def_ref (facts:331); that mod's only blocker is ResearchRetag def_ref | droppable with the Fortifications chain after the guard check (section 2) |
| VFE Props and Decor | `vanillaexpanded.vfepropsanddecor` | profile is SHIP not DEV/TEST (07 tsv); dependant `gmmp.dungeon` is SHIP (facts:338) | stays SHIP; no test cost; drops only with Gerrymon's Dungeon |
| BiomesKit | `zal.biomeskit` | dependant `ironscruff.primordialgeysers` class_ref (facts:79); Geysers' plants are MayRequire-guarded in `RUT_TheForge.xml:174-183` | KEEP with Geysers (Forge biome cast) |

Net on the HOLDs: **4 become droppable with their lone dependant (CQF, VAE Accessories, Minerals Framework, VFE Architect)**; 05's Biomes! Framework reason is out of date; the 4 world-generation mods are not in any test profile, so holding them changes nothing.

## 5. Unmeasured

Save-borne residue of any candidate in `_AREAFIX2` fixtures (run `save_def_census.py` before promoting); `tps_cost` and runtime memory per mod (facts say UNMEASURED); whether `.rid`/`.xtp` ideology files name any candidate (excluded from the src grep: `src/Jawa/ideoligion/The Salvation.rid:404` and `MandrakeJawa.xtp` name ALL 50 MOVE candidates, measured by literal grep, but as the active-mod stamp the editor writes into an ideo file, not as defs used; moving them makes the ideo files load with a missing-mod notice, harmless but re-save the ideo under the new profile); C# string references inside third-party DLLs.

## 6. Our own mods vs the owner's paint rule (2026-10-19: paint profile = only what is NEEDED to represent world, gravship, player characters)

Scope: the 59 `OURS` rows of `07_profile_assignment.tsv` (the remaining of the 62 are not in the DEV/TEST/DEV-INSTR set). Edges are from `mod_facts.jsonl` `dependants_detail`
(cite `facts:<line>`) and our `modDependencies`. "Needed" = defines or is hard/def-referenced by something that defines biomes, factions, settlements/landmarks, species/pawnkinds/backstories, or the sun geometry.
Gravship: all gravship defs are third-party (Vanilla Gravship Expanded, GravTide); of ours only `rm.gravshiplanding` touches it and it is a fog-reveal behaviour, not representation.

**PAINT-NEEDED (23)**

| mod | reason (cited) |
|---|---|
| `rm.biomes` | the biomes; 2661 defs (facts:547) |
| `rm.flowworks` | hard dependency of rm.biomes, 108 TerrainDefs (facts:547 needs; 530) |
| `rm.luminouspigment` | hard_dep of rm.biomes (facts:512) |
| `rut.patches` | 28 BiomeDefs, factions, scenario; hard needs rm.biomes + rm.weathersuite (facts:522) |
| `rm.weathersuite`, `rut.weathersuite` | sun/terminator geometry; hard_dep of rut.patches (facts:437, 588). UNMEASURED whether paint reads it; the Direct Sun ruling says geometry decides |
| `rsw.starwarsraces` | species, xenotypes, pawnkinds (527 defs; facts:507) |
| `rsw.swbestiary` | creature rosters; rm.biomes has def_ref to it (facts:548) |
| `rsw.droidworks` | droid pawnkinds used by rut.patches and rsw.injections (facts:526) |
| `rsw.armoury` | rm.biomes and rm.inhabited def_ref its weapons (facts:508) |
| `rsw.patches`, `rm.patches` | pawnkind/weather defs and load fixes that rut.patches loads after (facts:521, 519) |
| `rut.pawnflavor` | faction backstories/traits, i.e. the characters (facts:523) |
| `rm.inhabited`, `rut.inhabited` | settlements, 294 CharacterDefs, world objects (facts:172, 173) |
| `rm.injections`, `rsw.injections`, `rut.injections` | TileMutatorDefs and structure GenSteps; rm.inhabited references them (facts:164-166) |
| `rm.hugethings` | rm.biomes def_ref (facts:546) |
| `rut.ishkolandmarks`, `rut.ashkarrlandmarkart` | LandmarkDefs and landmark icons: world map content (facts:385, 384) |
| `rsw.shokk` | FactionDef; hard needs rm.biomes (facts:511) |
| `rm.planetpresetprime` | creates the world; belongs in AUTHORING not DEV/TEST by 07's own reading (facts:408); NEEDED for the paint only |

**NOT-NEEDED to paint (36)** (stay in SHIP, and in DEV only if a test needs them; none is def-referenced by a needed mod in `dependants_detail`)

`rm.loadtracer`, `rm.rimdefdump` (instruments), `rm.ninefold`, `rm.aftermath`, `rm.visibility`, `rm.graffiti`, `rm.sacredgraffiti`, `rsw.jawarules`, `rut.scavengerevents`, `rm.strandedquest`,
`rsw.jawavoice`, `rsw.cuisine`, `rsw.desertvehiclereskin`, `rut.doctrine`, `rm.proximityhatch`, `rsw.gizkastowaway`, `rsw.ionweapons`, `rut.shipmemory`, `rut.antiquities`, `rut.rites`,
`rut.researchretag`, `rsw.bacta`, `rut.droidrepairjobs`, `rm.wreckedmachines`, `rut.pyrelandsmechanics`, `rm.explosiveknockback`, `rm.kineticarms`, `rm.gimmesomeslack`, `rm.oracle`, `rm.property`,
`rut.birthhatchdemo`, `rut.menushell`, `rm.shipvermin`, `rut.longhunger`, `rut.empirepursuit`, `rm.gravshiplanding`.

**Flagged, need an owner or measurement call (not counted above):** `rut.shokkweaveeconomy` (2 GenSteps for the Webwork biome, no dependants, facts:541: PAINT-NEEDED if the Webwork biome ships in the paint, else NOT), `rut.rustcathedralroaches` (rut.patches def_ref+mayrequire, facts:542: guarded, so NOT-NEEDED unless the roaches belong in the Rust Cathedral roster), `rut.greentideraidant` (a FactionDef and pawnkinds, no dependants, facts:551: NEEDED only if that faction exists at the faction pass), `rm.wreckedmachines` (rsw.armoury patch only; no world content).
Cross-link: Third-party mods that these needed mods hard/def-reference (Harmony, VEF, Humanoid Alien Races, Big and Small, Outer Rim, Genes, Keshig, Landmarks, Archon/Genie/Saurid, the Tribals/Alpha chain) therefore stay in the paint profile; section 3 stands.
