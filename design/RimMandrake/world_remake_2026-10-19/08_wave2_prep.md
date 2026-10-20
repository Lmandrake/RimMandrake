# World remake 08: Retirement Wave 2, prepared offline (2026-10-19)

FOUNDRY helper, offline. No game, no bridge, and the live `ModsConfig.xml` / Cherry Picker file were only READ.
**`FULL.LATEST` is NOT changed.** Owner orders: *"retire all the mods we don't need so we can repaint the world, then build
slowly back"* (2026-10-19); Minerals Framework: *"NRE test passes, retire that mod"* (card, 2026-10-19); PAINT profile:
*"the fundamental mods that define Utinni without any additional fluff... Even our own mods are left out unless they are
NEEDED (Baroque Biomes obviously is needed)."* (card, 2026-10-19).

## 0. Counts

| list | mods | file (`infrastructure/state/modlists/`) |
|---|---:|---|
| base (= live ModsConfig, same order, parsed) | 498 | `ModsConfig.FULL.LATEST.xml` |
| Wave 2 asked for | 124 | 112 SAFE (05 §3) + 6 DROP-DEEPER (07 §4a) + 4 Minerals (owner card; Rock and Frozen were already in the 112, Framework and Sparkle added) |
| **HOLD** | **2** | §1 |
| **Wave 2 drops** | **118** | `wave2_removed_118.txt` (packageId, name, why) |
| **new FULL** | **380** | `ModsConfig.FULL.WAVE2_380_2026-10-19.xml` (ET.parse count 380, 0 dupes, 0 drops left) |
| DEV | 118 | `ModsConfig.DEV.WAVE2_2026-10-19.xml` |
| TEST | 206 | `ModsConfig.TEST.WAVE2_2026-10-19.xml` |
| AUTHORING | 226 | `ModsConfig.AUTHORING.WAVE2_2026-10-19.xml` |
| SHIP | 330 | `ModsConfig.SHIP.WAVE2_2026-10-19.xml` |
| **PAINT** | **81** | `ModsConfig.PAINT.WAVE2_2026-10-19.xml` (§4) |
| Cherry Picker SHIP keys | 2,329 → **1,747** | `infrastructure/state/cherrypicker/CherryPicker.SHIP.WAVE2_CANDIDATE.xml`; the 582 trimmed keys: `cp_wave2_keys_582.txt` |

Every list carries Core + all five DLC (6 `ludeon.*`). Every list's members resolve to a real About.xml (the 498 capture's
mod roots). Closure on every list: **0 missing** (About.xml `modDependencies` incl. `v1.6`, plus 10-10 `class_ref`/`hard_dep`
edges from `mod_facts.jsonl`; edges to mods already absent from the clean-loading 498 are stale 10-10 rows and not counted).

## 1. HOLD (2) — kept on the list

| mod | why held | releases when |
|---|---|---|
| Vanilla Backstories Expanded `vanillaexpanded.vanillabackstoriesexpanded` | **player characters**: 3 founders' backstories (`founder_YekuFirst...xml:424` VBE_GiftedBurnout, `founder_NekkoCaptainVok...xml:420` VBE_ClonedHeir, `founder_TobbKeeperNkik...xml:422` VBE_Standardbearer). Runbook S11 imports these fragments into the new world | the 3 backstories are ported as `RUT_` defs (PawnFlavor) and the fragments rewritten |
| Vanilla Quests Expanded - The Generator `vanillaquestsexpanded.generator` | founder Nekko's adulthood `VQE_PowerArchitect02` (`...Nekko...xml:421`); also `DeepDesertTribes.xml:354` (MayRequire) | same port |

Nothing else failed: **0 retained mods hard-depend on a drop** (fresh About.xml read of all 498, `closure_118.json`); 59
`loadAfter` edges only (order, not a stop). No 10-10 `class_ref` from a retained mod to a drop.

## 2. Our src: what references the drops, and what changed

Instrument: `wave2_prep.py` (this folder). Dropped defNames = defs in the 498 capture (`2026-10-19T22-45-42Z`, its mod set =
the list) whose every defining package is a drop, plus `<defName>`s in the drops' own XML (catches Cherry-Picker-cut defs),
minus every name that Core/DLC or a retained mod also declares (grep of their XML): **5,955 names**. Every leaf in an ACTIVE
src mod's XML naming one was checked for a guard (FindMod naming a drop, a Conditional on that def, MayRequire).
**1,632 references; 0 unguarded** after the two fixes below (8 false hits: the word "Awkward" in a description).
Sanity: before the fixes the same scan reported the JawaWorld rows unguarded.

| change | file | why |
|---|---|---|
| prerequisite guard (generator + output) | `design/Jawa/research_review/build_retag_patches.py` (`prereq_guard`), `src/RimUtinni/ResearchRetag/Patches/RUT_ResearchRetag.xml` | Core's `MoisturePump` was rewired to require `VFE_Res_FarmingTechniques` (VFE Farming, a drop): an unresolved cross-reference. A prerequisites rewrite now applies only when every non-Core/DLC prerequisite exists; otherwise the def keeps its own (vanilla). 46 of 80 prereq blocks wrapped; behaviour unchanged while the prereqs load. The generator's pinned capture `2026-09-04T02-23-44Z` no longer exists, so the output was transformed with the generator's own `prereq_guard` (non-Core attribution from the current capture) instead of a regen. Selftest: same verdict as before (only the pre-existing techprint-gate row FAIL) |
| `MayRequire="zal.comigogreaterswamps"` on 3 rows | `src/RimUtinni/UtinniPatches/Patches/JawaWorld_BiomeMix.xml:91,92,123` | biomeBlacklist / biomeConfigs named the Comigo swamp biomes unguarded inside a Conditional on TidallyLocked (retained) |
| `loadAfter` lines to drops removed (30 lines) | About.xml of Doctrine (4), UtinniPatches (9), MenuShell (1), PawnFlavor (2: Fossils, Torture Pod), SWBestiary (1), Armoury (5, incl. Ancient urban ruins), StarWarsPatches (2, incl. Ancient urban ruins), MandrakePatches (5), Aftermath (1) | owner: remove offending material. Load-safe either way (the engine orders by ModsConfig). `about_load_order_lint.py`: 0 cycles |
| **kept** | `src/RimUtinni/ResearchRetag/About/About.xml` forceLoadAfter (16 drops) | its selftest bar `force_load_after_names_every_donor_owner` reads the live dump, where the drops are still owners; removing them now turns a passing check red. Remove after the post-deploy dump |
| **no C# change** | `src/RimMandrake/Pyrelands/Source/RM_PyrelandsDensityEnforcer.cs`, `src/RimMandrake/DivingInteraction/Source/RM_SeabedFloorLife.cs:67` | both are idempotent re-asserts (write only when the value differs). With Map Designer absent they find nothing to fix and stay silent; the Pyrelands enforcer still carries the live regrow-override setting, so it stays. No rebuild, no DLL |

Guarded references left in place (load-safe, they match nothing once the mod is gone): FindMod blocks in Armoury, Doctrine,
StarWarsPatches, MandrakePatches, PawnFlavor (Fossils museum thought, Torture Pod), ResearchRetag tab/techprint rows, the
Ancient urban ruins rows of `AncientsAreRakata.xml` / `ApparelTags_DeadTagRepair.xml`. Deleting them is cleanup, not a fix.

**Soft losses the owner should know** (guarded, so no error, but content disappears):
- `rut.menushell`: every main-menu background is a `VBE.BackgroundImageDef MayRequire="vanillaexpanded.backgrounds"`; with VBE dropped the menu shell shows no backgrounds.
- **Gravship** `Gravship_v2_ring_2026-09-12.xml` names drops: `UCScaffoldTile` ×229 (Utility Columns, top terrain on Substructure), 9 `OuterRim_AurebeshWord*` signs (Outer Rim Furniture & Decor), `AM_DamagedEmptyShelves` ×1 + 2 storage filters (Ancient urban ruins), `VFE_LargeAdvancedBattery` ×1 (VFE Power). Runbook S10b already remaps a copy (AG_RustedTile 892 cells); add these.
- **Founders**: face-addon defs from the dropped Facial Animation texture packs (`nals.facialanimationexperimentals`, `vanillaexpanded.vtexe.facialanims`, `reel.facialanims`) — cosmetic, and FA itself is SHIP-only.
- Lantern Deeps keeps its pyrinth scatter via `mandrake.rm.pyrinth` (retained); Better Infestations' silencing patch becomes moot.

**Pre-existing selftest reds (not caused here, verified by restoring HEAD About.xml):** `selftest_mandrakepatches.py` (3),
`selftest_xenotype_cut_spawnsets.py` (dump cannot see xenotypeSets), ResearchRetag techprint-gate row (RG_/VFEI2_ rows).

## 3. Profiles (from `07_profile_assignment.tsv`)

Built by `wave2_lists.py`: DEV = DEV+DEV-INSTR · TEST = DEV+TEST · AUTHORING = TEST+AUTHORING · SHIP = DEV+TEST+SHIP (no
instruments). Order = the 380 list's order. Changes from 07: Minerals Framework/Sparkle leave TEST; the 2 HOLDs sit in TEST
(founder identity: the start save is made on TEST); `mandrake.rm.pyrinth` is DEV (07 labelled only its donor, DROP-W1).
SHIP-PENDING (24) is in no profile. Closure pulled nothing in any profile (0 missing).

## 4. PAINT (81) — the smallest list that represents the world, the gravship and the player characters

Built by `paint_profile.py`: explicit seeds (reason each), then closure to a fixpoint over (1) About.xml dependencies,
(2) 10-10 `class_ref`/`hard_dep`, (3) **unguarded** def references in OUR members' Defs XML to defs only a non-member defines
(Core/DLC names excluded; third-party Defs not scanned: they use LoadFolders). Need evidence for characters and ship is
MEASURED: every defName in the six founder fragments (minus the retired Eyeling), the ship layout and `Scenario_Utinni.xml`,
attributed to mods through the 498 capture. Our-mod verdicts start from `09_second_look.md` §6.

| mod | why it is in PAINT |
|---|---|
| `brrainz.harmony` | closure: hard dependency / class_ref of owlchemist.cherrypicker |
| `ludeon.rimworld` | Core + DLC: every list carries all five expansions (owner 2026-09-19/25) |
| `ludeon.rimworld.royalty` | Core + DLC: every list carries all five expansions (owner 2026-09-19/25) |
| `ludeon.rimworld.ideology` | Core + DLC: every list carries all five expansions (owner 2026-09-19/25) |
| `ludeon.rimworld.biotech` | Core + DLC: every list carries all five expansions (owner 2026-09-19/25) |
| `ludeon.rimworld.anomaly` | Core + DLC: every list carries all five expansions (owner 2026-09-19/25) |
| `ludeon.rimworld.odyssey` | Core + DLC: every list carries all five expansions (owner 2026-09-19/25) |
| `owlchemist.cherrypicker` | TOOL: its cuts define the def set the world is made under |
| `adaptive.storage.framework` | closure: hard dependency / class_ref of mandrake.rsw.armoury |
| `redmattis.betterprerequisites` | closure: hard dependency / class_ref of mandrake.rsw.starwarsraces |
| `smashphil.vehicleframework` | closure: hard dependency / class_ref of mandrake.rsw.armoury |
| `imranfish.xmlextensions` | closure: hard dependency / class_ref of mandrake.rsw.armoury |
| `oskarpotocki.vanillafactionsexpanded.core` | closure: hard dependency / class_ref of mandrake.rut.injections |
| `ebsg.framework` | closure: hard dependency / class_ref of mandrake.rsw.armoury |
| `mlie.advancedbiomes` | closure: hard dependency / class_ref of mandrake.rut.patches |
| `7f.alienworlds` | TOOL: generator framework Ash'karr was made with (02 sec 2) |
| `sarg.alphamemes` | closure: mandrake.rm.biomes's Defs name GU_RedWood unguarded |
| `biomesteam.coreframework` | closure: hard dependency / class_ref of zylle.morevanillabiomes |
| `det.keshig` | closure: mandrake.rm.inhabited's Defs name DV_MeleeWeapon_SerratedScimitar unguarded |
| `jecrell.doorsexpanded` | closure: hard dependency / class_ref of mandrake.rsw.patches |
| `dubwise.dubsbadhygiene.lite` | closure: hard dependency / class_ref of mandrake.rm.biomes |
| `mandrake.rm.injections` | WORLD: TileMutatorDefs / structure GenSteps named by tiles (09 sec 6) |
| `mandrake.rsw.injections` | WORLD: SW TileMutatorDefs (09 sec 6) |
| `mandrake.rut.injections` | WORLD: Ash'karr TileMutatorDefs (09 sec 6) |
| `mandrake.rm.inhabited` | WORLD: settlements as world objects (09 sec 6) |
| `mandrake.rut.inhabited` | WORLD: the Ash'karr settlement manifests (09 sec 6) |
| `turnovus.biotech.integratedgenes` | closure: hard dependency / class_ref of mandrake.rsw.starwarsraces |
| `jecrell.jecstools` | closure: hard dependency / class_ref of mandrake.rsw.armoury |
| `zylle.morevanillabiomes` | closure: hard dependency / class_ref of mandrake.rut.patches |
| `oblitus.mylittleplanet` | TOOL: planet size until it is baked (09 sec 4) |
| `brrainz.rimbridgeserver` | TOOL: the bridge that stamps the CSV bundle (w9_run.py) and prints the ship |
| `rimfridge.kv.rw` | closure: hard dependency / class_ref of lwm.deepstorage |
| `vanillaexpanded.vanillabackstoriesexpanded` | CHARACTERS: 3 founder backstories (Wave 2 HOLD) |
| `oskarpotocki.vfe.tribals` | closure: mandrake.rut.researchretag's Defs name VFET_Tribalwear unguarded |
| `vanillaexpanded.vfefactory` | SHIP: 6 VFEFactory machines in Gravship_v2_ring |
| `vanillaexpanded.vfesecurity` | closure: mandrake.rut.injections's Defs name VFES_Turret_TeslaBlaster unguarded |
| `vanillaexpanded.gravship` | SHIP: VGE_AstrofuelPipe in Gravship_v2_ring |
| `vanillaexpanded.vexploratione` | closure: mandrake.rm.biomes's Defs name VEE_Plant_DatePalm unguarded |
| `vanillaquestsexpanded.generator` | CHARACTERS: founder Nekko's adulthood VQE_PowerArchitect02 (Wave 2 HOLD) |
| `vanillaracesexpanded.archon` | closure: mandrake.rsw.starwarsraces's Defs name VRE_ShortPregnancy unguarded |
| `vanillaracesexpanded.genie` | closure: mandrake.rsw.starwarsraces's Defs name VRE_Curiosity_Social unguarded |
| `vanillaracesexpanded.saurid` | closure: mandrake.rut.patches's Defs name Saurid unguarded |
| `vanillaexpanded.vanillatraitsexpanded` | CHARACTERS: 6 founder traits (VTE_Dunce, VTE_Ecologist, VTE_Insomniac...) |
| `lazyfridaystudio.genesexpandedeyes` | closure: hard dependency / class_ref of mandrake.rsw.starwarsraces |
| `7f.alienworlds.tidallylocked` | TOOL: tidal-lock generator (02 sec 2); our JawaWorld_BiomeMix patches it |
| `mandrake.rut.ashkarrlandmarkart` | WORLD: the landmark icons the map draws |
| `mandrake.rut.ishkolandmarks` | WORLD: LandmarkDefs on the world map |
| `lwm.deepstorage` | closure: hard dependency / class_ref of neronix17.outerrim.core |
| `mandrake.rm.planetpresetprime` | TOOL: world-creation page preset (09 sec 6: needed for the paint only) |
| `mandrake.rm.weathersuite` | WORLD: hard dep of rut.patches; terminator/sun geometry engine |
| `mandrake.rut.weathersuite` | WORLD: Ash'karr's PlanetGeometry (substellar point) on the frozen planet |
| `erdelf.humanoidalienraces` | closure: hard dependency / class_ref of mandrake.rsw.droidworks |
| `neronix17.toolbox` | closure: hard dependency / class_ref of mandrake.rsw.starwarsraces |
| `redmattis.bigsmall.core` | closure: hard dependency / class_ref of mandrake.rsw.starwarsraces |
| `lovelydovey.sex.witheuterpe` | closure: hard dependency / class_ref of lovelydovey.sex.withrosaline |
| `neronix17.outerrim.core` | closure: mandrake.rm.inhabited's Defs name OuterRim_CompositeHelmet unguarded |
| `neronix17.outland.genetics` | closure: hard dependency / class_ref of mandrake.rsw.starwarsraces |
| `lovelydovey.sex.withrosaline` | closure: mandrake.rsw.starwarsraces's Defs name SEX_AlwaysAphrodor unguarded |
| `neronix17.outerrim.galacticempire` | closure: mandrake.rm.inhabited's Defs name OuterRim_DLT19HeavyBlasterRifle unguarded |
| `neronix17.outerrim.rebelalliance` | closure: mandrake.rm.inhabited's Defs name OuterRim_A280Blaster unguarded |
| `lee.theforce.lightsaber` | closure: mandrake.rm.inhabited's Defs name Force_Lightsaber_Inquisitor unguarded |
| `mandrake.rsw.starwarsraces` | CHARACTERS: RSW_Jawa xenotype, genes, heads, eyes of all six founders; scenario's RSW_MandrakeJawa |
| `mandrake.rsw.armoury` | CHARACTERS+SHIP: the founders' Jawa robes/hood/poncho and the ship's guy762 floors + RSW_Durasteel |
| `mandrake.rm.proximityhatch` | closure: hard dependency / class_ref of mandrake.rm.biomes |
| `mandrake.rsw.shokk` | WORLD: a FactionDef present at the faction pass (09 sec 6) |
| `mandrake.rm.luminouspigment` | closure: hard dependency / class_ref of mandrake.rm.biomes |
| `mandrake.rsw.ionweapons` | closure: mandrake.rut.patches's Defs name RSW_JawaIon_Damage unguarded |
| `mandrake.rut.antiquities` | closure: mandrake.rut.injections's Defs name RUT_Antiq_Cartography unguarded |
| `mandrake.rut.researchretag` | closure: mandrake.rsw.droidworks's Defs name RUT_Tree_Unbolting unguarded |
| `mandrake.rm.patches` | WORLD: load fixes rut.patches loads after (09 sec 6) |
| `mandrake.rsw.patches` | WORLD: pawnkind/weather fixes rut.patches loads after (09 sec 6) |
| `mandrake.rut.patches` | WORLD: 28 RUT_ BiomeDefs, our factions, Scenario_Utinni, the founders' RUT_Jawa_Colonist kind |
| `mandrake.rut.pawnflavor` | CHARACTERS: faction backstories/traits (founder Wim's RUT_Jawa_ReapsTheFlames) |
| `mandrake.rsw.droidworks` | WORLD/CHARACTERS: droid pawnkinds used by our factions (09 sec 6) |
| `mandrake.rm.flowworks` | closure: hard dependency / class_ref of mandrake.rut.patches |
| `mandrake.rm.explosiveknockback` | closure: hard dependency / class_ref of mandrake.rm.kineticarms |
| `mandrake.rm.kineticarms` | closure: hard dependency / class_ref of mandrake.rut.patches |
| `mandrake.rm.hugethings` | closure: hard dependency / class_ref of mandrake.rm.biomes |
| `mandrake.rm.biomes` | WORLD: Baroque Biomes, every RM_ biome (owner: 'obviously needed') |
| `mandrake.rsw.swbestiary` | CHARACTERS: the founders' Dewback and the scenario's bonded RSW_Ikee |
| `mandrake.rm.shipvermin` | closure: hard dependency / class_ref of mandrake.rut.patches |

**Ours: 30 of 63 in PAINT, 33 NOT needed to paint:** `rm.loadtracer` `rm.rimdefdump` (instruments) `rm.pyrinth` `rm.ninefold`
`rm.aftermath` `rm.visibility` `rm.graffiti` `rm.sacredgraffiti` `rsw.jawarules` `rut.scavengerevents` `rut.empirepursuit`
`rm.strandedquest` `rsw.jawavoice` `rsw.cuisine` `rut.longhunger` `rsw.desertvehiclereskin` `rut.doctrine` `rsw.gizkastowaway`
`rut.shipmemory` `rut.rites` `rsw.bacta` `rut.droidrepairjobs` `rm.wreckedmachines` `rut.pyrelandsmechanics` `rm.gimmesomeslack`
`rm.oracle` `rm.property` `rut.birthhatchdemo` `rut.menushell` `rut.shokkweaveeconomy` `rut.rustcathedralroaches`
`rm.gravshiplanding` `rut.greentideraidant`. These of ours entered only by closure, not by a need of their own:
`rm.proximityhatch`, `rm.hugethings`, `rm.luminouspigment`, `rm.flowworks` (rm.biomes), `rm.kineticarms` + `rm.explosiveknockback`,
`rm.shipvermin` (rut.patches class refs), `rsw.ionweapons` (rut.patches names `RSW_JawaIon_Damage`), `rut.antiquities`
(rut.injections), `rut.researchretag` (droidworks names `RUT_Tree_Unbolting`).

**Calls for the owner (not decided here):**
- `rut.greentideraidant` (a FactionDef), `rsw.shokk` (in) and any third-party WORLD faction: a faction absent at the faction pass is absent from that world. PAINT carries only our factions in `rut.patches` + Shokk; the third-party world-borne mods (Go Explore, outposts, VFE Pirates, trader ships…) are TEST.
- `rut.shokkweaveeconomy`: 2 GenSteps for the Webwork biome; in only if Webwork must generate maps under PAINT.
- Tools: Worldbuilder (NRE every load), WorldEdit 2.0, Sensible Factions, Deep Orbit are OUT (Deep Orbit only for the `_AREAFIX2` fixtures). Add WorldEdit if hand-editing tiles in game.
- Founder data that drops silently under PAINT (needs/hediffs/thoughts of mods not in it): Dubs Bad Hygiene is IN (via rm.biomes); Romance/Intimacy, Prison Labor, Mood Chain Reaction, Melee Animation skills, VME memes, Caravan Adventures relation are OUT. Expect "could not load reference" lines at import; census per runbook G11.
- PAINT is not a test profile: it has not been loaded (load time, first exception: UNMEASURED).

## 5. Live deploy (exact steps; game DOWN, bridge held)

1. `rimflow bridge take --for "Wave 2 retirement deploy"`; `./game` must read down.
2. Back up: copy live `ModsConfig.xml` → `infrastructure/state/modlists/ModsConfig.LIVE_BACKUP_<date>_pre_wave2.xml`; Cherry Picker backs itself up in step 5.
3. Deploy the changed mods (plan, read, then `--apply`): `python3 src/RimMandrake/Utils/deploy_custom_mods.py --mod <M>` for
   UtinniPatches, ResearchRetag, Doctrine, MenuShell, PawnFlavor, SWBestiary, Armoury, StarWarsPatches, MandrakePatches, Aftermath.
4. Mod list: copy `ModsConfig.FULL.WAVE2_380_2026-10-19.xml` over the live `ModsConfig.xml`; parse it back: 380, sha equal to the file.
   Then `cp` it to `ModsConfig.FULL.LATEST.xml` (only now).
5. Cherry Picker: `cp CherryPicker.SHIP.WAVE2_CANDIDATE.xml CherryPicker.SHIP.xml`, then `python3 src/RimMandrake/Utils/cherrypicker_swap.py --ship --apply`; `--status` must read 1,747 keys.
6. Cold load (Steam). Read the FIRST exception in Player.log; compare with the 498 baseline (`Transient/live_testing_2026-10-19f/`):
   ConfigErrors/patch failures/xref must be ≤ baseline and none ours. Arm a def dump; on it run
   `python3 src/RimUtinni/ResearchRetag/selftest_researchretag.py` (then drop ResearchRetag's 16 forceLoadAfter drops) and the
   G11 censuses if a fixture is loaded (`_AREAFIX2` still needs Ancient urban ruins residue checked: `save_def_census.py`).
7. Release the bridge; commit the backup + FULL.LATEST + SHIP swap by explicit path; `./publish`.
Rollback: the backup from step 2 and the `CherryPicker.PRESWAP.*` the swap prints.

UNMEASURED: save-borne residue of the 118 in the `_AREAFIX2` fixtures (Ancient urban ruins was "not save-safe" for OLD saves,
07 §4a); C# string defName references inside third-party DLLs; load time of every new list.
