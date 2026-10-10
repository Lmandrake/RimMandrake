# Mod audit: actions that need no owner decision

Generated 2026-10-11 from the merged registry (`MASTER_REGISTRY.jsonl`) and the four checker groups. Every action
here carries out a ruling that already exists or fixes a defect of our own. None needs an owner card. **No ticket has been
filed yet.** Each ticket name below passed `rimflow namecheck`. File them with `rimflow file <NAME>`.

Each row is ordered by what to do first. The "evidence" column names the primary source. The merge author
opened the sources marked ✔ again on 2026-10-11 (see `merge_inputs.json` `spotchecks`).

## A. List regressions (FULL.LATEST disagrees with a ruling)

| # | ticket (proposed) | what is wrong | exact next step | evidence |
|---|---|---|---|---|
| A1 | `FULL_LATEST_RETIRE_ZOMBIE_PAIR` | `gravenwitch.vsrexamined` and `jellypowered.survivaltools` were ruled retired **together** on 2026-09-11. Both are back in FULL.LATEST. | Remove both ids from `infrastructure/state/modlists/ModsConfig.FULL.LATEST.xml`. Grep `src/` for counter-patches that the retirement left (`STAT_NORM_WAVE3_RETIRE_1` names them) and confirm each is guarded. Close the two card questions as answered. | ✔ `infrastructure/state/items/STAT_NORM_WAVE3_RETIRE_1.md:1-3`; FULL.LATEST |
| A2 | `BEASTS_OF_RIM_RETIRE_LAST_UNTICK` | `mlie.beastsoftherim` was ruled out on 2026-09-05 and `RSW_Jerba` replaces it. Step 4 of 4, the untick, was never done; the mod sits at FULL.LATEST position 62. | Run a save census for `Jerbal` placements (A15). Then remove the id from FULL.LATEST and tick step 4 in the checklist. | `design/Jawa/worldbuilding/RETIREMENT_CHECKLIST.md:4-6,:91,:151-155` |
| A3 | `PYRINTH_MIGRATE_LIST_NEVER_SWAPPED` | `CRYSTAL_INGEST_EXECUTION_1` is done and `mandrake.rm.pyrinth` absorbs `det.epochspyrinth`. The donor is still on FULL.LATEST and the absorber is not. `mandrake.rm.biomes` still patches the donor. | Swap the ids in FULL.LATEST (put the absorber where the donor was). Repoint the biomes patches that name donor defs to the `Absorbed_EpochsPyrinth` defs. Run a save census for donor-def placements before the next full load. | ✔ FULL.LATEST; `src/RimMandrake/Pyrinth/About/About.xml` |
| A4 | `RAID_FEE_RETIRE_UNTICK_NOT_CHERRY` | `leo.raidprotectionfee` stays ELIMINATE (it duplicates `geojak.tributedemand`, and a Harmony prefix swallows `RaidEnemy`). It declares 0 defs, so Cherry Picker cannot cut it. | Untick it in FULL.LATEST. Drop the "via Cherry Picker" wording from the proposal. | `JawaBenchIncidentTools.cs:141-142`; `design/Jawa/proposals/plot_mechanisms_wave.md:307` |
| A5 | `MODLIST_RECONCILE_RULED_VS_LISTED` | A1-A4 show that nothing checks FULL.LATEST against retirement rulings. | Add a lint that reads every closed RETIRE/ABSORB item naming a packageId and refuses a FULL.LATEST that still lists it, or that lacks the absorber. Run it in `run_selftests.py`. | `checks/check_group_4.md` "Ruling conflicts" |

## B. Live settings that contradict a ruling

| # | ticket | what is wrong | exact next step | evidence |
|---|---|---|---|---|
| B1 | `LANDONANYTHING_ENFORCE_RULING_NEVER_TOOK` | The owner ruled on 2026-09-06 that `allowedToSqishRoofs` and `allowedToLandOnAnyTerrain` are forced **OFF**. Both read `True` in the live config (mtime 2026-09-12), and no code of ours overrides them. The item is closed as done. | Pick the durable route: a tiny Harmony-free settings override in `mandrake.rm.*` (or a `ModSettings` write at startup) that forces the two fields false. A Config hand-edit is undone by any settings-window save. Re-read the Config after the next load. Reopen or annotate `GRAVSHIP_LANDING_CRUSH_1`. | ✔ `C:\Users\Mandrake\AppData\LocalLow\Ludeon Studios\RimWorld by Ludeon Studios\Config\Mod_3545384484_LandOnAnythingMod.xml`; `infrastructure/state/items/closed/GRAVSHIP_LANDING_CRUSH_1.md:3-11` |
| B2 | `BIGGER_GRAVSHIP_RECONCILE_TWELVE_NOT_FOUR` | `ship_designs.py` (2026-08-13) records four numbers, 34/30/12/85. The live config (2026-08-15) stores **twelve**: 4500/100/5000/12/100/100, chemfuel tanks 1140.6/8805.5, 20 small thrusters, shield radius 29.9, health 2522.6 and 20.2 generators. | Correct `ship_designs.py` to the twelve live values. Own the eight structural values in an RM patch now. The fuel-tank and shield values touch the fuel-scarcity pillar, so they wait for **card C12** and are not frozen yet. | ✔ `Config\Mod_3522759531_GravshipSizeSettings.xml` |
| B3 | `RIMEFELLER_ENFORCE_FOUND_ONLY_OIL` | Rimefeller was adopted **only** as non-buildable, found oil (owner, 2026-08-04). Nothing in `src/` removes buildability. `mandrake.rut.researchretag` has 87 refs that retag its research instead. | Write a `UtinniPatches` patch that strips `designationCategory` (or adds a `ResearchPrerequisites` of an impossible project) from the derrick, oil well and cracker ThingDefs, and places them through world/map authoring only. Verify offline with `validate_patch.py --defs`. | `design/Jawa/mods/required_mods.md:565-575` |

## C. Defects in our own mods

| # | ticket | what is wrong | exact next step | evidence |
|---|---|---|---|---|
| C1 | `RESEARCHRETAG_FIX_NEGATIVE_COORDS` | `RR_LateralThinking` and `RR_Organization` declare `researchViewX -2.00`, which the 1.6 engine rejects. The tab-collision "Config error ... same research view coords" lines charged to Roots of Rimworld and Dubs Bad Hygiene Lite come from **our** `RUT_ResearchTabAssign.xml`. | Give both projects non-negative X on `RUT_Tree_Scavenging` (shift the tree right). Deconflict the coordinates in `RUT_ResearchTabAssign.xml`. Re-attribute those log lines to `mandrake.rut.researchretag` in the record. | ✔ `src/RimUtinni/ResearchRetag/Defs/ResearchProjectDefs/RUT_Ported_ResearchTrio.xml:92,107`; RimSage `ResearchProjectDef.cs:401` |
| C2 | `NORTHFIX_ART_MERGE_ORPHANED_NORTHS` | `mandrake.rsw.msedroidfix` holds the only `MSE_north.png` (Droidworks ships east/south only). `mandrake.rsw.kotorbandoliernorthfix` holds 20 north PNGs for bandoliers that Armoury absorbed. Their dependencies are absent, so this art loads nowhere today. | Move `MSE_north.png` into `src/RimStarWars/Droidworks/Textures/OuterRim/Droid/`. Move the 20 north PNGs into the matching `src/RimStarWars/Armoury/Textures/SWApparel/Accessories/...` texPaths. Confirm each texPath binds (texture binds by texPath, not defName). Then delete both fix mods and deploy. | ✔ `src/RimStarWars/MSEDroidFix/Textures/OuterRim/Droid/MSE_north.png`; ✔ `src/RimStarWars/KotORBandolierNorthFix/` |
| C3 | `DEPLOY_PRUNE_NORTHSTAR_STOWAWAYS` | `deploy_custom_mods.py` `EXCLUDE_DIRS` has no `northstar`, so 76 MB of GimmeSomeSlack test JSON is in the game's Mods folder. Other mods are likely affected too. | Add `northstar` (and any other test-data dir names found by a sweep of `src/*/*/`) to `EXCLUDE_DIRS` (line 148). Re-run the deploy as a dry run and check that the plan shows the `-` deletions. Then `--apply`. | ✔ `C:\Program Files (x86)\Steam\steamapps\common\RimWorld\Mods\GimmeSomeSlack\northstar`; `src/RimMandrake/Utils/deploy_custom_mods.py:148` |
| C4 | `RESTRAINING_BOLTS_REWIRE_DEAD_HEDIFF` | `GoodwillSituationWorker_RestrainingBolts.cs` (~line 36) looks up `OuterRim_RestraintBolt` from the absent Droid Depot through `GetNamedSilentFail`, so the goodwill cap silently never applies. Droidworks ships `RSW_DW_RestrainingBolt` instead. | Repoint the lookup to `RSW_DW_RestrainingBolt` (and decide whether `RSW_DW_BoltResentment` counts). Rebuild with `winbuild.py`. Note that the mod is OURS_ABSENT_INSTALLED, so shipping it is a separate decision. | `src/RimUtinni/RestrainingBolts/...GoodwillSituationWorker_RestrainingBolts.cs`; `HediffDefs_Droidworks.xml:96,:162` |
| C5 | `SALVATION_GODS_EXCISE_FROM_RM_TIER` | The owner ruled on 2026-09-08 for an RM engine plus a RUT Salvation pack. `God.cs` and `RM_GodFavourTilts.xml` still name the Nine inside `mandrake.rm.ninefold`. SacredGraffiti's nine mark-styles also still sit in RM. | Split the god roster and tilts into a RUT pack, and extract the nine mark-styles to RUT, following the map in `MOD_NAMING_CONSOLIDATION_AUDIT_1`. | `design/NAMING_SCHEME_PLAN.md` §7.1 and :54 |
| C6 | `PROPERTY_MIGRATE_RSW_PATCHES_LEAKED` | `mandrake.rm.property` carries 5 FindMod-gated theft-hauler ops that name `RSW_DW_Race_*` (a tier breach). Its About.xml also has a self-referential "Absorbed mandrake.rm.property" line. | Move `Patches/TheftHauler/*` into an RSW mod (Droidworks). Delete the stale About line. | `checks/check_group_4.jsonl` mandrake.rm.property |
| C7 | `GREENTIDE_ANT_RENAME_STILL_EARTHLY` | `mandrake.rut.greentideraidant` still labels its race "giant ant", and `Textures/Things` is empty. `THEY_MOD_REPLICATION_1` steps 3-4 require a coined name and new art. | Coin the name per `NONCANON_BEAST_RENAME_1`. Queue art only after `artpipe_state.py find` comes back empty. | `THEY_MOD_REPLICATION_1` (closed) |
| C8 | `NORTHSTAR_STATE_CORRECT_CLAUDE_MD_STALE` | CLAUDE.md says FlowWorks is VALIDATED. `modcheck status` today reads FlowWorks DRAFT, WreckedMachines RED/DRAFT, and Graffiti not listed. | Correct the CLAUDE.md north-star bullet to the measured state, and say which command measured it. | `checks/check_group_4.md` item 4 |

## D. Keep-as-is notes (these stop a wrong removal; nothing to do except not untick)

- `aoba.framework`: **KEEP**. `aoba.fortress.industrial` hard-requires it for v1.6, and Armoury depends on Fortifications.
  Unticking it would silently drop Fortifications at load.
- `deon.rimtek.core`: **KEEP-TEMPORARILY**. `deon.rimtek.docmate` (KEEP) hard-depends on it. Digipal is DISPUTED (card C21).
- `sd.fa.geneticheadsframework`: follows `sd.fa.geneticheadsbiotech`, which has 11 class refs.
- `leutiankane.mines2patchouterrim`, `mineablesor`, `jecrell.jecstools`, `lovelydovey.sex.withrosaline`, Gender Works,
  Doors Expanded, Show Me Your Hands, Better Trees: our own patches, xenotypes or absorbed defs use them (the founders carry
  `SEX_AlwaysAphrodor` and `SEX_Ovipositor` with no guard). Do not read `dependants_ours: []` as "unused" (checks 2 and 3).

## E. Tickets to measure (former owner questions that are measurements)

| ticket | question it answers | how |
|---|---|---|
| `AMBUSH_MULTIPLIER_MEASURE_DLL_DEFAULT` | Better Ambushes has no Config file, so what is its compiled default multiplier? If it is 1x, card C10 drops the mod. | Decompile or read the default from the DLL |
| `DEEP_STORAGE_VERIFY_CAP_SETTING` | Is the ruled low Deep Storage capacity actually set? | Read the Config file for `lwm.deepstorage` |
| `FOG_TOGGLES_VERIFY_ROUTE_B` | Is CAI 5000's fog off and NWN the single fog system (Route B)? | Config read at the next load |
| `DUBS_LITE_VERIFY_OPTIONS_OFF` | Are DBH Lite's toilets and hygiene off (`required_mods.md:581`)? | Read the DubsModOptions Config |
| `FACTIONAL_WAR_VERIFY_FREQUENCY_LOW` | Is the accepted Factional War set to LOW frequency? | Config read |
| `FACTION_TERRITORIES_VERIFY_SETTINGS` | Can faction expansion add settlements to the frozen world? | Config read plus a description read |
| `ALPHA_MEMES_MEASURE_STYLE_COST` | What do 1,253 ThingStyleDefs cost at load and in memory? | Load-time A/B on the minimal list |
| `HEAVY_TEXTURES_MEASURE_REAL_VRAM` | Are the header-proxy giants real: `vesper.egihologramsandprojectors` (1.5 GB proxy), `rwnodetree.rwplanetatmosphere` (about 1 GB), `vanillaexpanded.vtexe.facialanims`, `mandrake.rsw.droidworks` (378 MB)? | Process-memory A/B on a minimal list. Read after the facts regen (Source/ images excluded). |
| `SPACEPORTS_AUDIT_BAZAAR_OVERLAP` | Does `zal.spaceports` duplicate or fight Bazaar, GravshipLanding and the Trader-ships mod? | Design and code read |
| `OUTERRIM_CORE_HUNT_REAL_REPO` | The facts URL for `neronix17.outerrim.core` is the pardeike/Harmony false match. What is the real source? | gh search by author |
| `SWAC_EDGES_CENSUS_PORTED_VS_LIVE` | Why do 3,439 references to the Star Wars Animal Collection remain after its absorption closed? Split them into ported-twin wiring and live dependence. | Script over `rut.patches`, `doctrine` and `swbestiary` |
| `DOOMED_MODS_CENSUS_SAVE_PLACEMENTS` | Placed Things or pawns in the campaign save for every ELIMINATE and every retirement in A1-A4. This is UNMEASURED throughout the audit (one known hit: a pawn with `SH_MED_MedievalAlchemist`). | `rimworld-savegame` skill, `<def>NAME</def>` grep per def |
| `QUARRY_ERROR_REMEASURE_UNATTRIBUTED` | A Quarry sandstone duplicate-key error is in the deploy record but was not attributed by the log probe. 244 of 344 error blocks are unattributed overall. | Re-run `runtime.py` attribution on the next full-list log |
| `BIOME_DONOR_DEPENDENCY_UNTANGLE_HARD_LINK` | Can `mandrake.rm.biomes`' hard `<modDependency>` on `sarg.alphabiomes` become guarded ops, so the dependency ends biome by biome? (Answered process: Q12 of the donor retirement plan.) | Technical read of the 1,155 refs |
