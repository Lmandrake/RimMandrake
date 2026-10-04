# FOUNDRY_REBOOT_HANDOFF_202610040002 — READ FIRST on wake

Follows `FOUNDRY_REBOOT_HANDOFF_202610031504`. Everything below is committed and pushed unless a
line says otherwise. **Game and bridge state is the last section — read it
before touching the game.**

## The one thing to carry forward

<!-- The single most important thing learned. Not a list — the thing that would cost the next seat hours if it had to rediscover it. If nothing qualifies, write 'nothing this wave' and mean it. -->
The live harness, not the mods, was the main cause of RED for hours: fixes are all committed (bland map on ZBiome_Grasslands, roofs/gas cleared per chain, Food pct, budgeted waits, ambient-hediff ignore list, timeoutSeconds 25, RunInBackground True via static_call, no search_debug_actions). Trust a suite RED only from a run made after commit 973e49fdb.

## What the owner should see

<!-- Findings that need HIS eye or HIS decision: a number nobody ruled on, a mod that vanished from his list, a change he can veto. Say what you shipped deliberately with a flag raised. Empty is a legitimate answer. -->
WEEPINGSTONES_NET_TARGET_FLEES_1 (BENCH decision) is filed. Cauldron suush was a REAL defect, fixed: any damage detonated it (Pawn HitPoints ~0) so requiredDamageTypeToExplode=Bullet was added; BlueDesert vhaulk/krissek (also CompExplosive pawns) likely share it, unverified. Bacta Base_Outlander_Standard stock rows are overwritten by another mod: no fix chosen.

## What is half-done, and where it stops

<!-- Anything left mid-flight, one bullet each: `- ITEM_ID -- state; NEXT: <one imperative action>`. A pointer without a ledger item id does not survive a seat change, and a pointer without a NEXT: measured ~0% pickup. An item in `doing` with no line here is a trap for the next seat. -->
- `rerun15` — situational_rerun --bland-world (Bacta,BrainWorms,LeaningScrub,BlueDesert,WeepingStones,TheForge,Cauldron) was running in the background on load 10, at BlueDesert warm chain when a Dialog_NamePlayerFactionAndSettlement stalled the clock (closed by hand); NEXT: run `python3 src/RimMandrake/Utils/belt_watchdog.py`, read Transient/belt_rerun15_20261003.txt, then record with `python3 src/RimMandrake/Utils/modcheck/live_queue/record_summaries.py <Mod>...` (python.exe recording fails with PermissionError).
- `BACTA_BASE_OUTLANDER_STOCK_1` (not filed) — RSW_Bacta_TraderStock.xml rows for Base_Outlander_Standard absent live (64 rows, ours missing); NEXT: find the later patch that rewrites stockGenerators (Merchant/Patch_Traders in workshop 1541721856/2007061826) and add loadAfter or a late PatchOperationAdd.
- `CAULDRON_STEEL_YIELD_1` (not filed) — martyr tree harvest read 351 steel vs 6 expected, but list_things shows ~12 loot stacks appearing on the map, so unproven; NEXT: poke a harvest on an empty pad and diff steel stacks by id.
- `BLUEDESERT_EXPLOSIVE_PAWNS_1` (not filed) — vhaulk/krissek detonation chains FAIL; NEXT: check CompExplosive on those pawns for the same HitPoints-0 trap and add requiredDamageTypeToExplode.
- `LEANINGSCRUB_FLORA_1` — flora_spawns/dead_venomvine_fuels_fire/guardians_roost still red or untested after warden fix; NEXT: read rerun15 LeaningScrub results.
- `UtinniStatues` — new mod never deployed or tested (builder mid-edit at launch); NEXT: deploy --mod UtinniStatues and run its first script.
- Unrun: AcousticScanner, AssailantSalvage, FallLineArrivals, Webwork, TheRot, FeverWood, TheSump, RustCathedral first scripts; NEXT: situational_rerun --bland-world --mods for them.

## Traps learned

<!-- Instruments that lied, silent failures, commands that ate their own input. ONE line each, ending with where it now lives -- file it with `lessons.py add` the moment it is learned, then cite `(filed: lessons)` or `(see: <item/doc>)`. Never re-explain a trap that is already recorded somewhere durable. -->
jawa/damage skips player pawns unless allowColonists=true (filed: lessons). rimworld/search_debug_actions hangs the main thread (see: design/RimMandrake/live_test_hang_runbook.md row 8). bland_world on the full list wedges via mlie.nwnrealfogofwar, which is now removed from ModsConfig (filed: lessons). Prefs.RunInBackground is in-memory: re-run set_RunInBackground after every launch (filed: lessons). python.exe processes are named python3.13, not python (see: this handoff).

## Closed since the last handoff (152)

- `MODCHECK_COMPOSED_BIOMES_LIST_1` — c9d07f4c4
- `JAWA_NAMEMAKER_NEVER_FIRES_1` — 685b0d6ab
- `FLAWED_MASTERWORK_ENGINE_CHECK_1` — 4b3d663bf
- `ABYSS_INVENTED_CREATURES_TO_RM_1` — f75f996c6
- `LANTERNDEEPS_LANTERN_LIGHT_BUILD_1` — f54cd3d8e
- `SUMP_HUNGRY_GOD_TEXT_1` — HEAD
- `ROT_TIER_LEAKS_FIX_1` — 6ab632b63
- `CRACKEDLANDS_PLANT_LIST_OWNED_1` — 7e3a11674
- `WEEPINGSTONES_HEAT_WINDHOUR_TEXT_1` — bb10600cf
- `FEVERWOOD_CROWN_SOUND_HEAT_1` — 8d477f2e8
- `LANTERNDEEPS_FAUNA_TIER_PORT_BUILD_1` — aeaa3caf0442409c6bcad03cd79653bda7adcd39
- `SHIPVERMIN_MYNOCK_KIND_NAME_1` — ab8053cbc79ee09211925ca8047d5f1ea98f83ee
- `SILTTRAP_TERRAINS_UNBUILT_1` — 86b7f41154a89b969bd092cde2a3bd3830c4e8bf
- `MINERAL_BIOME_LEAKS_1` — 45346bd11394811159a24da015e4a22917f858c3
- `PYRELANDS_FAUNA_TIER_PORT_BUILD_1` — c0f2e9842212ecf06df8d326f38d9e7ea1056a80
- `PYRELANDS_HEAT_KIND_BUILD_1` — 23f664e468dac7bd817ef19fc79b2ed527d2ba05
- `ROT_RM_CAST_MIGRATION_1` — 941b4805eaeab5a594cf1f9b23e1e33a2f3ff6c4
- `WEBWORK_HEAT_SHADE_BUILD_1` — 28601a9e6254ddd3a651ae1e194ce6296eaba214
- `PYRELANDS_FURNACE_WARMTH_AMBIENT_1` — 5a87d93178f36ee16d51ca9714a055786ee1afd6
- `BLUEDESERT_FLORA_EXPANSION_BUILD_1` — 5da96df3e8c764704386900827144446ac12bb34
- `GREENTIDE_FREE_ROSTER_OWNED_1` — af179341a
- `CAULDRON_FLORA_EXPANSION_BUILD_1` — d48186901e38
- `ROT_MOD_SETTINGS_WIRING_1` — 9046342e1c22
- `ROT_SPORE_ALLERGY_PORT_1` — 891c1d14a069
- `ROT_WOUND_SHARING_WIRING_1` — 8d2f36142f29
- `CRACKEDLANDS_FLORA_EXPANSION_BUILD_1` — 5c14d3d5986d3a88181d2a7901e2dfe9c3a010e0
- `WEBWORK_BASE_PORT_BUILD_1` — 95229531669f487f8528a9519bff353ce3a82e24
- `SUMP_KETHREL_BUILD_1` — b09fcd2d9
- `FEVERWOOD_TIER_LEAKS_FIX_1` — 16765aa02
- `WEEPINGSTONES_MURRIN_CATCH_WIRING_1` — 9aa2aa9f3
- `WEEPINGSTONES_OASIS_MUTATOR_FLORA_1` — 7cfdfd2f8
- `ABYSS_ETCHCAP_BUILD_1` — e44b4d2e6
- `MIASMA_SWARM_COMPOSTER_PORT_1` — 9c2d28f08
- `GELATINOUSSLIME_GENE_TEXT_TIER_1` — 444a7aaa4
- `SUMP_TAR_BEAST_BUILD_1` — 0e0d94f34afd
- `STILLSAND_CAVE_TIER_ROWS_1` — 8986b740f
- `CHILL_FREE_TIER_CATCH_1` — a8a4998ec
- `RUSTCATHEDRAL_FREE_NAMES_TIDY_1` — 84d2b3626ea5
- `SCALD_CROWNCARPET_NO_HABITAT_1` — ca774b8b9
- `TWILIGHT_TENANCY_PAPER_REMOVAL_1` — 3e6a74b87
- `TWILIGHT_REVIEW_FIXES_1` — 3e6a74b87
- `OFFBIOME_SHEET_RERENDERS_1` — cc28f2f0b
- `MIASMA_SHIPPING_NAMES_1` — 8f59422c7
- `SUMP_SOLVENT_WAKE_BUILD_1` — 8ebbd2448742
- `PROPERTY_CLAIM_ERASE_API_1` — 628220afd0af
- `SHRUBLAND_TREE_GUARDIAN_1` — fd8b0b8d2a9e
- `FALL_LINE_ARRIVAL_MECHANISM_1` — 0fecc4432549
- `LADDER_PRISON_DOOR_1` — cf789dc80207
- `PIT_COVER_FALL_REWIRE_1` — 9d6cefabd3c9
- `SWEETLINE_SCRATCHING_TREE_BUILD_1` — 7f3b13094597
- `FALL_LINE_FERAL_SURVIVORS_BUILD_1` — da199b9d2f54
- `SWEETLINE_TREE_MAP_STEP_1` — fc4fa853025f
- `SWEETLINE_FELT_COMFORT_BUILD_1` — 103d2793db88
- `LEANINGSCRUB_SWEETLINE_GUARDIAN_1` — 103d2793db88
- `REACTION_MECHANISM_GENERALISE_1` — 18668e795963
- `FEVERWOOD_HIVE_SEALED_PASSAGES_1` — e7051fcece5e
- `FEVERWOOD_HIVE_PARASITE_CHAMBER_1` — 1041b2b077f1
- `GREENTIDE_VURRAK_BUILD_1` — 353c7efebffe
- `UTINNI_STATUES_SKELETON_BUILD_1` — fc40549e5b85
- `SHKAAR_FLAME_IDOL_BUILD_1` — 4a7fcdbeda76
- `UNFINISHED_LINE_SPINE_COUNT_1` — 63d5ed55728d
- `DROID_MASS_PRODUCTION_QUEST_CHAIN_1` — 63d5ed55728d
- `CANAL_BOTTOM_SPIKES_1` — 05b688a8149d
- `TOLLUK_CAP_ART_REGEN_1` — ea39b4ad6edf
- `UNFINISHED_LINE_ENVOY_BEAT_1` — a1b5b72616aa
- `UNFINISHED_LINE_CORES_BEAT_1` — ff0375f15617
- `ROT_HWELGRUE_GIANT_BUILD_1` — 5e633e159eef
- `ROT_STILL_ALIVE_SWALLOW_1` — 83f5b76f4346
- `ROT_SWALLOWED_NAVIGATOR_1` — 480a0abec753
- `ROT_GUT_MOTHER_VAT_1` — 3a36b9d9b114
- `ROT_NAVIGATOR_LOG_SITES_1` — 1e940911ea6a
- `UTINNI_STATUES_ART_WIRING_1` — 5ba6d743fc9e
- `ROT_UNJOINING_DRAUGHT_1` — c63f3d2c3d54
- `WEEPINGSTONES_TRUCE_HUNT_SUPPRESSION_1` — ce6509b93
- `WEEPINGSTONES_SETTINGS_SLIDERS_1` — 6da4923a3
- `WEEPINGSTONES_WALKING_CONDENSER_1` — 14e6dd024
- `WEEPINGSTONES_DEWSILK_COCOON_1` — af0f944fe
- `GELATINOUSSLIME_SETTINGS_SWITCHES_1` — d534b23a6
- `CHILL_NATIVE_COLD_TOLERANCE_1` — d1a92626a
- `CHILL_FLOOR_CAST_TRIM_1` — ab0ebfce1
- `SCALD_IMMERSION_BERTH_1` — 846f4ad52
- `SCALD_FLOOR_VENT_FIELDS_1` — ad5afe347
- `SCALD_RETURN_GALLERY_1` — a8a4998ec
- `GELATINOUSSLIME_FUBBUM_HUNTER_1` — 89cc24542
- `GELATINOUSSLIME_DWOMMO_FLIER_1` — 719927a73
- `MIASMA_FREE_SALT_CRUST_1` — 17396b66e
- `MIASMA_FREE_NURSERY_YOUNG_1` — 0ea605ef1
- `GELATINOUSSLIME_GLURRO_SALVE_1` — d1cdebec5
- `MIASMA_AMBUSH_FROG_REMAKE_1` — c9647d2b1
- `MIASMA_ATTAR_STILL_1` — 3542d0da2
- `MIASMA_FLOTSAM_YARD_1` — 3542d0da2
- `MIASMA_YOUNG_CALL_1` — 3f2311a84
- `SCALD_SAAL_ONE_NAME_1` — 2aee84e61
- `NABOO_FISH_TO_TWILIGHT_1` — f9390dd0a
- `CHILL_WAX_PROCESSION_GIANT_1` — afb94bc21
- `CHILL_ZHIIL_FLOOR_BODY_1` — 34af3ef3e
- `CHILL_RETURN_COMB_LANDMARK_1` — 5185f5a2c
- `MIASMA_ROUND2_IMPORTS_1` — fccf0f1b3
- `GELATINOUSSLIME_ARCHIVE_RESURRECTION_1` — d81982d27
- `WARSCAR_FREE_TIER_BODY_1` — ee8fbc21f
- `WARSCAR_CHOTRIX_BUILD_1` — 72368fbb3
- `GELATINOUSSLIME_RAIN_STRIP_1` — d4da652d9
- `STILLSAND_EVENT_CREATURES_REMAINDER_1` — 6a62a8616
- `GELATINOUSSLIME_GAPPO_FAMILY_1` — ae89151e2
- `WARSCAR_SETTLING_WEATHER_1` — 8cef95e5e
- `WARSCAR_GEIGER_CHOIR_1` — c2d354db7
- `GELATINOUSSLIME_FARM_RUINS_1` — 636105df2
- `MIASMA_SETTINGS_SWITCHES_1` — 2bb0abac4
- `ABYSS_DURRGAK_BUILD_1` — 41f41d1fe6ac
- `ABYSS_GHARREK_BUILD_1` — 32beda5b9
- `ABYSS_KRIZZAK_BUILD_1` — 150889e19
- `LANTERNDEEPS_WORKING_DEAD_BUILD_1` — 92d87b1f0c0f
- `ABYSS_DONOR_BEASTS_FREED_1` — 0c3fb6948ea4
- `ABYSS_DARK_BUILD_1` — 41bc6751f
- `CONTAGION_GROWN_LIMBS_BUILD_1` — e713b8036
- `GREYSEA_HULL_CRUST_BUILD_1` — 213f28292652
- `GREYSEA_LAMP_RESPONSE_BUILD_1` — a45dfc46f7f3
- `GREYSEA_RULED_CONTENT_1` — a45dfc46f7f3
- `LANTERNDEEPS_ORUN_GHAL_BUILD_1` — a963cd096564
- `LANTERNDEEPS_MINDSTONE_GALLERY_BUILD_1` — 9d90e3b58ed9
- `LANTERNDEEPS_HYDROCARBON_WAVE1_BUILD_1` — 97ecd0d1e6da
- `LANTERNDEEPS_CREEP_CLEAVERS_BUILD_1` — f8a1206555e9
- `LANTERNDEEPS_AURORA_COLLAPSE_BUILD_1` — f8a1206555e9
- `LANTERNDEEPS_HYDROCARBON_WAVE2_BUILD_1` — b689995546fb
- `UNFINISHED_LINE_FIRSTLIGHT_BEAT_1` — e5dfe8cf04ef
- `ABYSS_ETCHFALL_BUILD_1` — 41bc6751f
- `ABYSS_LAMP_CROPS_BUILD_1` — d75bc400ffc5
- `ABYSS_FOLD_LAMP_BUILD_1` — d75bc400ffc5
- `ABYSS_SOUNDSCAPE_BUILD_1` — d75bc400ffc5
- `LANTERNDEEPS_HYDROCARBON_WAVE3_BUILD_1` — b37617e677cf
- `LANTERNDEEPS_HYDROCARBON_FAUNA_BUILD_1` — b37617e677cf
- `FLOWWORKS_DOOR_FAMILY_1` — 6359e69b569b
- `WARSCAR_MARK_TRADE_BUILD_1` — 4ba64518db21
- `WARSCAR_PILGRIM_CAMPS_1` — 68676a8465d4
- `STILLSAND_SKELETON_ART_TRACKS_WIRING_1` — 2655f315f369
- `NIGHTSIDEICE_EVICTION_HOUSEKEEPING_1` — b0d8a9f74c5a
- `WARSCAR_CHATRAK_SNAP_BUILD_1` — b55a79ac1
- `NIGHTSIDEICE_HEAT_DIAL_1` — 65d1d3f12
- `NIGHTSIDEICE_HEAT_DIAL_BUILD_1` — 65d1d3f12
- `SEA_DIVE_DOCS_CORRECTION_1` — 88df5c923
- `SEA_DIVE_HATCH_RETIRE_1` — 88df5c923
- `NORTHSTAR_PHASE_LADDER_1` — 0c17ccfe9
- `SEABED_FLOOR_GENERATORS_1` — cbc8adc7c
- `NIGHTSIDEICE_SHIVVEN_BUILD_1` — 5cb0b0e4a
- `NIGHTSIDEICE_BREACH_CRACKS_1` — 9a75e1046
- `LEANINGSCRUB_RUNWAY_BLOOM_VISUALS_1` — 52b9e2800
- `ABYSS_FREE_CRYPTID_1` — a8866a648
- `SEABED_FLOOR_AMBIENT_CARRYOVER_1` — 04bbf881f
- `HOIST_SHIP_PART_BUILD_1` — 231c05821
- `HOIST_FIXED_SITE_FRAMES_1` — d56cccf14
- `PYRELANDS_ULLAI_GIANT_BUILD_1` — 1be79afda
- `MIASMA_DECAY_CELLS_1` — 4b0614b9f

## Filed and still open (22) — the next seat's queue

- `STARWARS_JUNK_RESKIN_1` — Reskin vanilla ancient junk (cars, tanks, walkers, dropships) as Star-Wars-adjacent wrecks: Graphic_Random folders of many variants, patch in mandrake
- `BIOME_VISUAL_BEDAZZLE_PASS_1` — Visual bedazzle pass on every biome (ground, colour, density), AFTER all biomes are green-code, art-complete, in the single biome mod, with basic Nort
- `WEEPINGSTONES_NET_FLEEING_FLIER_1` — NET job cannot catch a wild skarrin: it flies off-map before the handler arrives
- `FALL_LINE_MUTATOR_PLACEMENT_1` — Place the RUT_FallLine tile mutator on the 308 Fall Line + The Breaks tiles of the frozen world (bridge world_* + world_commit, back up the start save
- `FALL_LINE_WRECKAGE_CREATURES_PORT_1` — BMT_BunkerBug and BMT_Megapleura (Fall wreckage creatures) are absent: load Biomes! Polluted Lands or port them to our own defs; then add them to the 
- `FEVERWOOD_HIVE_GUARD_CHAMBER_1` — Ant hive kept guard at the chokepoints: invent the guard creature, station it where corridors narrow (build LAST, after a reacting hive is played)
- `GREENTIDE_ILLISK_BUILD_1` — Build the Illisk shoal (fast, nearly unkillable except explosives); open: one pawn or many, how 'nearly unkillable' is expressed, Odyssey water intera
- `FLAME_STATUES_MOD_BUILD_1` — Statue spec steps 4-7: mandrake.rm.flamestatues (three Chemfuel flame statues, RM_CompFlamePoints, art wave, Helixien link), replacing RM_FlameStatuar
- `UNFINISHED_LINE_TITHE_BEAT_1` — Unfinished Line beat 4 The Tithe and the Hands: scaled material tithe to the site + lend a Crafting 8 colonist 10 days
- `UNFINISHED_LINE_WORLD_FOUNDRY_1` — Unfinished Line runs in the world (Q1=A): Enclave regrowth, Foundry-grade frames/parts in Enclave stock, volunteer free droids, line heat -> Imperial 
- `WEEPINGSTONES_NET_TARGET_FLEES_1` — Weeping Stones NET: wild skarrin outruns the handler and leaves the map before the 200-tick net finishes - how should capture work?
- `SPIKE_DAMAGE_NUMBERS_RULING_1` — Pit spike damage numbers for the owner's word: built PROPOSED 3 Stab hits totalling 40 x BodySize (human ~13/hit = 40, muffalo ~96, thrumbo ~160), arm
- `UNFINISHED_LINE_SITE_CHOICE_1` — Unfinished Line site choice (where the line stands, A-D) offered at the end of beat 2 and carried to beats 3-5; BLOCKED on BENCH/owner: Q1=A ruled no 
- `ROT_NAVIGATOR_CAMPAIGN_TILES_1` — Swallowed Navigator campaign tiles: name the carrier's Rot tile and the log's salvage-site tiles, then patch
- `MINDSTONE_MATRIX_KINDLED_BUILD_1` — Mindstone matrix + the Kindled's first making: RUT_Mindstone + head casing at the reassembly harness -> RUT_MindstoneMatrix -> RSW_DW_Head_Mindstone; 
- `ABYSS_DARK_MUFFLE_ALL_SOUNDS_1` — Abyss: the Dark muffles every map sound (Harmony on sample creation)
- `WARSCAR_LOOSENED_PANEL_BUILD_1` — Warscar loosened panels in ruin walls with a sealed cache behind, worked loose only at deepening mark (WARSCAR_SNAP_MARK_1 spec 6)
- `WARSCAR_PILGRIM_CAMP_SITES_1` — Pilgrim camps as world SitePartDefs at authored locations on the fixed planet (WARSCAR_PILGRIM_CAMPS_1 spec 1 remainder; needs the authored tiles alon
- `WARSCAR_PILGRIM_JOURNAL_ANTIQUITY_1` — Pilgrim journals as Antiquities artifacts: catalogue at the Reading Station also advances the Scarlands ladder, one route not two (WARSCAR_PILGRIM_CAM
- `SEABED_DESCENT_ASCENT_1` — Gravship flies from a sea tile down to its RM_SeabedLayer floor and back up (seabed Phase 2)
- `SEA_DIVE_HATCH_REMOVE_1` — Delete RM_SeaDiveHatch, RM_SeaDiveExit and their genstep/anchors once descent and layer generators land
- `MIASMA_ROTTING_BED_CORPSES_1` — Rotting bed as corpse disposal: haul a corpse in, it rots down, out come its skull and bones

## Commits

```
89d34b60f ledger: split MIASMA_DECAY_CELLS_1 (part A 4b0614b9f), file MIASMA_ROTTING_BED_CORPSES_1
4b0614b9f MIASMA_DECAY_CELLS_1 part A: decay cells make power from rot and go over to a rotting bed
02a504d5d ledger: close PYRELANDS_ULLAI_GIANT_BUILD_1 (1be79afda)
1be79afda PYRELANDS_ULLAI_GIANT_BUILD_1: the ullai herd follows the burn; the furnace-beast grows into a giant
a20f00708 ledger: shadecraft lessons ruled
705fb75b1 ledger: close HOIST_FIXED_SITE_FRAMES_1 (d56cccf14)
d56cccf14 HOIST_FIXED_SITE_FRAMES_1: genstep-placed head-frames, sealed holder target, Foundry tower frame
4cab3f032 ledger: close HOIST_SHIP_PART_BUILD_1 (231c05821)
231c05821 HOIST_SHIP_PART_BUILD_1: mandrake.rm.keelhoist, the keel hoist as a gravship part
973e49fdb Bacta suite: natural healing is ~0.36/2500t so off-phase limit 0.5; unpowered baseline read after entering
9983323a4 ledger: note MINERALS_WHERE_THEY_BELONG_1 (a848691fa)
a848691fa MINERALS_WHERE_THEY_BELONG_1: registry design final (GPT consult applied, quarry via transpiler) + cards
2eb3d45b1 Older owner questions: 9 cards (23 questions), 5 holds, 2 answered
bca9cdbc8 ledger: three answered/not-owner-ready items moved from owner to offline
ed68a7a98 MINERALS_WHERE_THEY_BELONG_1: registry design draft (inventory, sweep, EPM unit, quarry) + draft CSV
91bc8c777 artpipe: requeue_quota_failures reads the state dir, not the pre-migration in-repo queue
c1c756cee ledger: close SEABED_FLOOR_AMBIENT_CARRYOVER_1 (04bbf881f)
04bbf881f SEABED_FLOOR_AMBIENT_CARRYOVER_1: layer floors get the hatch's temperature, flora and refilling cast
191a5da33 ledger: event traces ruled, to FOUNDRY
09239202c file FLOWWORKS_QUARRY_DIGGING_1; venomvine all six forms to FOUNDRY
... 279 more: git log --oneline dedb2a28d..HEAD
```

## Game / bridge / tree state at wrap

- running   : RUNNING   (RimWorldWin64 running, bridge answers)
- recorded  : LOADING  → corrected to UP, measured now
- Bridge: for     full belt: clean deploy, launch, situational_rerun

Uncommitted (replace the placeholder after each line below with whose it is —
yours, the other seat's, a subagent's):

```
M Transient/belt_bridge_log_20261003.md   this subagent (BRIDGE round 2)
 M Transient/modcheck/live_queue/situational_rerun/Cauldron_summary.json   this subagent or earlier belt runs (run artifacts, safe to commit or bin)
 M Transient/modcheck/live_queue/situational_rerun/LeaningScrub_summary.json   this subagent or earlier belt runs (run artifacts, safe to commit or bin)
 M Transient/modcheck/live_queue/situational_rerun/TheForge_summary.json   this subagent or earlier belt runs (run artifacts, safe to commit or bin)
 M Transient/modcheck/live_queue/situational_rerun/WeepingStones_summary.json   this subagent or earlier belt runs (run artifacts, safe to commit or bin)
 M Transient/modcheck/live_queue_results.jsonl   this subagent or earlier belt runs (run artifacts, safe to commit or bin)
 M infrastructure/state/modcheck_status.json   this subagent or earlier belt runs (run artifacts, safe to commit or bin)
?? deployed/config/ModsConfig.before-tier-builds_biomes.xml   this subagent or earlier belt runs (run artifacts, safe to commit or bin)
?? deployed/config/ModsConfig.before-tier-flowworks.kept-20261002.xml   this subagent or earlier belt runs (run artifacts, safe to commit or bin)
?? deployed/config/ModsConfig.before-tier-flowworks.xml   this subagent or earlier belt runs (run artifacts, safe to commit or bin)
?? deployed/config/ModsConfig.before-tier-messyconduit.xml   this subagent or earlier belt runs (run artifacts, safe to commit or bin)
?? deployed/config/ModsConfig.pre-ns-flowworks.20261002T070221.xml   this subagent or earlier belt runs (run artifacts, safe to commit or bin)
?? deployed/config/ns_flowworks_backup.20261002T070221.json   this subagent or earlier belt runs (run artifacts, safe to commit or bin)
```

