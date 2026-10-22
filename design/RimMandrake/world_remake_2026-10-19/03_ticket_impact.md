# World remake proposal: impact on the open queue (2026-10-19)

FOUNDRY, offline, read-only on the ledger. **Proposal judged:** remake the world and savegame fresh now
(placeholder art allowed; biome shapes, mutators and defNames kept; retired donor mods gone; lost functionality
added back later) instead of finishing donor retirement piecemeal against the 2026-09-12 canonical save.

**Instrument:** `model.replay(model.read())` (the same projection `rimflow next` uses), as-of the last ledger event
2026-10-19T17:08Z. Open = every state except done/dropped/superseded: **874 items** (proposed 301, built 289,
validated 149, doing 119, ready 16; 94 carry the blocked flag). Classes were assigned by hand for every non-B item
(78) from the title, the blocked reason and, for the deciding items, the item prose; the 801 B rows were read by
title and given a family reason by rule (`classify.py` logic, reason column says which family). A B row's reason is a
family label, not a per-item proof.

| class | meaning | count |
|---|---|---:|
| A | obsolete, or shrinks to a stand-in, if the world is remade | 21 |
| B | unchanged (def/map/tooling level; carries over) | 801 |
| C | must come BEFORE a remake | 31 |
| D | becomes possible or easier after | 13 |
| E | needs the owner's word | 8 |

**Reading of the numbers.** 92% of the queue does not care which world it runs on. The proposal removes ~21 items of
save-repair and donor-art tax, but it does **not** remove the def work: everything a roster casts must already be ours
when the new world is cut (C), and renames must land before the new save or they reproduce the 2026-10-18
lost-biome incident (1,903 tiles fell back to TemperateForest because three BiomeDefs were renamed under a save,
`WORLDMAP_REPAIR_LOST_BIOMES_ROCKY_TEXTURES`).

## The two owner rulings the proposal collides with (E)

- `WORLD_REMAKE_FINAL_STEP_1` (owner 2026-09-20): the remake is *"the very last item to do before the official first
  play session"*, after every biome mod AND donor retirement; *"nothing may be blocked on it"*. The proposal moves it
  earlier. Carried across: worldmap, gravship layout, founders; everything else regenerates.
- `BIOME_PAINT_ONCE_AT_THE_END_1` (owner 2026-09-20): *"Once we have all the biomes in mods we will do the painting
  once and for all."* Remaking now means either painting now with unfinished biomes, or a remake now and a second
  paint later. He must say which.
- Also open: is this remake the shipped freeze? CLAUDE.md: *"A faction, ideoligion or setting absent when it freezes is
  absent from every player's game forever."* If yes, factions (`HORRORS_RAIDING_FACTION_1`, the RM scavenger faction
  in `CRACKEDLANDS_SALVAGE_CLAIM_CREW_1`) and xenotype cuts (`NONSW_XENOTYPES_SCOPE_1`) become prerequisites.

## Blocking structure (ledger `blocked_on` + blocked reasons)

- Heaviest live blockers, none on the remake path: `SUNSHADE_MIGRATE_MOVE_NOT_CHANGE` (6 Direct Sun / tree-shade
  items), `CATHEDRAL_REGARD_BLACKBOARD_1` (5 Cathedral arc items), `BAZAAR_WINDOW_GRID_1` (5, chain through
  `BAZAAR_PRICE_ENGINE_1` and `BAZAAR_HAGGLE_DUEL_1`), `BRIDGE_TPS_REVIEW2_FIXES_1` (4 metrics items),
  `SALVATION_RITES_UNIFICATION_1` (4 rites, owner-tabled), `COLD_LOAD_RUN_SHEET_4` (3), `CANON_CREATURE_REGEN_1` ->
  `FAUNA_LORE_DIVERSIFICATION_1` -> `FAUNA_TOLERANCE_NORMALIZATION_1`.
- **Stale blocks** (blocked_on names an item already done): `BIOME_DEFNAME_MIGRATION_WAVE_1` <- LANTERNDEEPS_TIER_COLLISION_1,
  `DESIGN_MATERIALS_REVIEW_1` <- BAROQUE_BEDAZZLE_PROGRAM_1, `FALL_LINE_FERAL_SURVIVOR_PAWNKIND_1` <-
  FALL_LINE_ARRIVAL_MECHANISM_1, `HOSTILE_MOBILE_PLANTS_1` <- REACTION_MECHANISM_GENERALISE_1,
  `SALVATION_RITES_UNIFICATION_1` <- BIOME_MOD_UNIFICATION_1. Each may still be blocked for its prose reason; the
  edge itself is dead.
- On the remake path, the blocks that matter are owner gates: `DONOR_DEFS_PORT_TO_OURS_1` (*"needs owner-sat plan/ordering
  first"*), `DESERT_FAMILY_PORT_EXECUTION_1` (review sheet), `CRACKEDLANDS_FULL_RENAME_1` (blocked because the old
  save names RM_FloodedCanyon on 44 tiles: the remake dissolves the reason but the rename must precede it).

## Critical path to a donor-free playable world

1. **Owner word** on `WORLD_REMAKE_FINAL_STEP_1` + `BIOME_PAINT_ONCE_AT_THE_END_1` (and whether this is the shipped freeze).
2. **Defs decoupled from donors:** `DONOR_DEFS_PORT_TO_OURS_1` (owner plan) -> `DESERT_FAMILY_PORT_EXECUTION_1`,
   `ALPHA_BIOMES_MIGRATE_PLANTS_TO_RM_TWINS` + `ALPHA_BIOMES_MIGRATE_DISEASES_AND_CODE` (both ready) ->
   `ALPHA_BIOMES_RETIRE_THE_LAST_PLANT_DONOR`, `ALPHA_BIOMES_CENSUS_THE_REST_OF_IT`, `REGEN_GAPS_DECIDE_STRAYS_AND_FLYERS`
   (16 roster rows still cast donor defs), `DONOR_ROSTER_GUARDS_FIX_WRONG_PACKAGE_ID`, `ALPHA_ANIMAL_PORTS_REHOME_1`;
   close `ABYSS_SHEET_DONOR_PORT_1`, `CONTAGION_RULED_CONTENT_1`, `CRACKEDLANDS_RULED_CONTENT_1`, `WARSCAR_SHEET_DONOR_PORT_1`.
3. **Names frozen:** `BIOME_DEFNAME_MIGRATION_WAVE_1`, `CRACKEDLANDS_FULL_RENAME_1`, `BIOME_TIER_CLEANUP_1`,
   `PLANT_TIERS_RECONCILE_MOST_ARE_BAROQUE` (every defName change after the new save is a new residue).
4. **The creation list:** `WAVE1_FIXES_DEPLOY_BEFORE_THE_CUT` -> `WAVE1_MODLIST_RETIRE_37_IN_ONE_LOAD` (list half only)
   -> `CHERRY_PICKER_RESTORE_FROM_SHIP_PROFILE`; `VRE_XENO_MODS_RETIRE_DEFOF_HOLDOUTS`, `MINES_SWAP_RETIRE_SHAFT_ALREADY_DUG`,
   `GENERATOR_MODS_PROVE_INERT_AFTER_CREATION`, `LANDFORMS_PROBE_REPLACE_OR_KEEP_EXPERIMENT` (E).
5. **Proof the list makes a game:** `DONOR_FOUR_RETIRE_JUST_GET_IT_DONE` / `DONOR_OFF_LOAD_PROVE_AFTER_BENCH` /
   `DONOR_PHASE0_FINISH_AWAITING_HIS_RULINGS` (donor-off load), `QUICKTEST_POLICY_NRE_FULLLIST_1` and
   `MATERIAL_MERGE_LOAD_CRASH_1` (both UNMEASURED since filing: re-check before trusting either way).
6. **Paint inputs:** ported mutators (`DONOR_MUTATORS_MIGRATE_TWENTY_TWO_CAME_HOME`, built; map
   `design/RimMandrake/retired_mutators_port_map.json`, 4 mutators not reproduced), `BIOME_WORLDTEX_BUILD_EVERY_BIOME_A_FACE`,
   factions (`HORRORS_RAIDING_FACTION_1`).
7. **Remake**, then the D items fold in at or after the paint (`UNUSED_MUTATORS_WORLD_ASSIGNMENT_1`,
   `FALL_LINE_MUTATOR_PLACEMENT_1`, `BIOME_LANDMARK_REFINEMENT_1`, world sites, `WORLDMAP_BIOME_APPEARANCE_1`, loadscreens).

Not measured here: whether test-site saves (`RM_TestSite_*`) are in the remake's scope (they carry the same donor and
Class= residue, `design/RimMandrake/donor_save_residue_2026-10-19.md`); whether landmark names and worldTags ride the
carried worldmap (`LANDMARK_NAMING_PASS_1`, `WORLDMAP_LIQUID_TAGS_1`).

## Table (E, C, A, D first; then B)

| ID | state | what it is (item's own title) | class | reason |
|---|---|---|---|---|
| BIOME_PAINT_ONCE_AT_THE_END_1 | proposed | Owner ruling 2026-09-20: the worldmap is painted ONCE, after every biome is its own RimMandrake mod - no pe... | E | "paint once, after every biome is a mod": remaking now means painting with unfinished biomes |
| CRACKEDLANDS_SALVAGE_CLAIM_CREW_1 | proposed | Floodline salvage claim stakes + rival crew visitor lord (scatter already built); owner: RM scavenger facti... | E | asks for an RM scavenger FACTION: exists at creation or never |
| LANDFORMS_PROBE_REPLACE_OR_KEEP_EXPERIMENT | proposed | Experiment: can we replicate Geological Landforms ourselves, or must it stay? Landforms looks like a big li... | E | keep or replace Geological Landforms decides the creation list |
| LANDMARK_NAMING_PASS_1 | doing/blocked | Review B2: 32 landmark names reused (worst 'Dead Sarlacc' x7) — hand-name the ~15 that matter in faction/re... | E | whether landmark names ride the carried worldmap is UNMEASURED |
| NONSW_XENOTYPES_SCOPE_1 | built | Owner: the cut-the-twelve ruling says only Star Wars xenotypes belong, but the load has 32 more non-SW Xeno... | E | 32 non-SW xenotypes: cut before factions are generated? |
| PLAYER_START_SITE_1 | proposed | The formal player start site: Hutt junkyard of ruined ships + old megastructures — lore fixed by Scenario_U... | E | formal start site: part of the remake or later? |
| WORLDMAP_LIQUID_TAGS_1 | built | worldTag authoring pass on the frozen map (builds on LIQUID_BIOMES_MAP_1) + landing GenStep repaints shores... | E | worldTag authoring on the frozen map: carried or redone? UNMEASURED |
| WORLD_REMAKE_FINAL_STEP_1 | proposed | Remake the world from scratch as the LAST act before the official first play session - expected, not a fail... | E | his 2026-09-20 text says LAST, after biomes AND donor retirement; the proposal moves it earlier |
| ABYSS_SHEET_DONOR_PORT_1 | validated | Abyss sheet 2026-10-05: port 17 donor rows to owned RM_ defs under new names, wire the ruled art | C | 17 donor rows to owned RM_ defs (validated; close it) |
| ALPHA_ANIMAL_PORTS_REHOME_1 | doing | Five Alpha Animals creatures have RSW_-prefixed ports (Wildpawn=RSW_Durrok, Wildpod=RSW_Mullgoth, Cactipine... | C | AA ports must be homed before rosters freeze into the new world |
| ALPHA_BIOMES_CENSUS_THE_REST_OF_IT | proposed | Decide the ~130 other AB_ names (terrains, weather, thoughts, biomes, tile mutators) the kickoff's 16 omit | C | ~130 AB_ terrains/weathers/biomes undecided; a fresh world needs the answer |
| ALPHA_BIOMES_MIGRATE_DISEASES_AND_CODE | ready | Replace the 3 AB_Disease incidents in Miasma; remove sarg.alphabiomes strings from C# (WarmGround, Pollinat... | C | AB_Disease incidents + C# strings (ready) |
| ALPHA_BIOMES_MIGRATE_PLANTS_TO_RM_TWINS | ready | Port the 14 AB_ plant defs to RM_ twins, repoint rosters and patches (XML only) | C | 14 AB_ plants to RM_ twins + roster repoint (ready, XML only) |
| ALPHA_BIOMES_RETIRE_THE_LAST_PLANT_DONOR | ready | Retire Alpha Biomes as a donor (umbrella): plan in design/RimMandrake/alpha_biomes_retirement_2026-10-16.md | C | umbrella for the last plant donor; a fresh world must not need AB |
| BIOME_DEFNAME_MIGRATION_WAVE_1 | proposed/blocked | Three biomes renamed 2026-09-26 carry defNames that no longer match their labels: RM_SleepingIce/RM_Poison... | C | rename BEFORE the new save; its live-tile blocker vanishes (blocked_on is done: stale) |
| BIOME_TIER_CLEANUP_1 | proposed | Biome tier cleanup: move twin-only features to RM_, scrub Star Wars IP, move RUT_ defs out of free mods | C | tier moves change defNames; post-remake they re-break the save |
| BIOME_WORLDTEX_BUILD_EVERY_BIOME_A_FACE | proposed | Placeholder world-map textures for ALL our biomes: read each description, make each distinct in colour and ... | C | placeholder world textures so the painted world is readable |
| CHERRY_PICKER_RESTORE_FROM_SHIP_PROFILE | proposed | Wave 1 W2: make CherryPicker.SHIP.WAVE1_CANDIDATE.xml the SHIP profile and swap it live with the game down ... | C | the SHIP profile defines what the new world loads with |
| CONTAGION_RULED_CONTENT_1 | built | Build the Contagion grotesque cast: 35 RM_ defs replacing the donor roster outright (no patches), 8 new spe... | C | 35 RM_ defs replacing a donor roster (built, unproven live) |
| CRACKEDLANDS_FULL_RENAME_1 | built/blocked | Full rename FloodedCanyon -> CrackedLands everywhere: defs, code, file names, docs (owner-typed 2026-09-28)... | C | blocked only because the old save names RM_FloodedCanyon; remake frees it, rename must precede |
| CRACKEDLANDS_RULED_CONTENT_1 | doing/blocked | Build the Cracked Lands ruled content: roster surgery (vanilla zoo out, RM_ migration, eopie to merchants),... | C | roster surgery / RM_ migration (doing, live verify owed) |
| DESERT_FAMILY_PORT_EXECUTION_1 | proposed/blocked | Port all 109 desert-family species to our own defs and our own art - owner ruled every row REPLACE 2026-09-... | C | 109 desert species to own defs; blocked on its review sheet |
| DONOR_DEFS_PORT_TO_OURS_1 | ready/blocked | Port EVERY donor def we use to our own thing defs - owner ruling 2026-09-20; two mods (starwarsanimalcollec... | C | umbrella: every donor def a roster casts must be ours first; BLOCKED on an owner-sat plan |
| DONOR_FOUR_RETIRE_JUST_GET_IT_DONE | validated | Retire SWAC, Alpha Animals, AA Outposts patch and Alpha Biomes: code done offline, donor-off load owed | C | SWAC/AA/AA-Outposts/AB retirement: code done, donor-off load owed |
| DONOR_MUTATORS_MIGRATE_TWENTY_TWO_CAME_HOME | built | Our own defs replace the retired donors' world-tile mutators and landmarks (20 new mutators, 3 landmarks, 4... | C | ported mutators/landmarks (built) are what the paint uses |
| DONOR_OFF_LOAD_PROVE_AFTER_BENCH | proposed | W4 live gate for retiring the Star Wars Animal Collection: deploy SWBestiary/Shokk/UtinniPatches, load with... | C | W4 donor-off live gate: the load that proves the new world can be made |
| DONOR_PHASE0_FINISH_AWAITING_HIS_RULINGS | proposed | Finish Phase 0 donor retirement: install batch 5/6 art on his rulings, deploy SWBestiary, run donor-off L1 ... | C | deploy SWBestiary + donor-off L1 (art-install half shrinks to A) |
| DONOR_ROSTER_GUARDS_FIX_WRONG_PACKAGE_ID | proposed | Bileworm and Zrrik roster guards are wrong, fix at his sitting | C | wrong roster guards: rosters must be right at creation |
| GENERATOR_MODS_PROVE_INERT_AFTER_CREATION | proposed | Prove Alien Worlds, Tidally Locked, My Little Planet, Sensible Factions and Faction Territories do nothing ... | C | decides which generator mods the creation list needs |
| HORRORS_RAIDING_FACTION_1 | doing/blocked | Horrors become a RAIDING faction (no settlements, nightside-gated encounters) + nests/sinkholes/crysalises ... | C | a faction absent at world creation is absent forever (CLAUDE.md) |
| MATERIAL_MERGE_LOAD_CRASH_1 | proposed | Full-list cold load CRASHES on origin/main as of 02:49 2026-10-10: MinifyEverything GenerateImpliedDefsPost... | C | full-list cold-load crash, if still live (UNMEASURED since 2026-10-10) |
| MINES_SWAP_RETIRE_SHAFT_ALREADY_DUG | proposed | With the game down: deploy mandrake.rm.mineshaft (+ Armoury policy), swap cain.mineshaft and leutiankane.mi... | C | mod swap: lands before the new save, else save residue again |
| PLANT_TIERS_RECONCILE_MOST_ARE_BAROQUE | doing | Census every plant def in RUT/RSW mods: generic -> move into Baroque Biomes; genuine SW canon -> reskin of ... | C | plant def moves/renames: settle before defNames freeze |
| QUICKTEST_POLICY_NRE_FULLLIST_1 | proposed | quicktest map will not start on the 613-mod list: NRE in ReadingPolicyDatabase.GenerateStartingPolicies (fi... | C | a new game must start on the full list (current status UNMEASURED) |
| REGEN_GAPS_DECIDE_STRAYS_AND_FLYERS | proposed | Donor art the regen queue cannot reach: 16 roster rows cast donor defs with no def of ours (Visceral, LavaS... | C | 16 roster rows cast donor defs with no def of ours |
| VRE_XENO_MODS_RETIRE_DEFOF_HOLDOUTS | proposed | Retire VRE Archon, VRE Fungoid and VRE Phytokin: their 5 xenotypes are ruled cut but named in their own ass... | C | mod retirement: should leave before the world is cut |
| WARSCAR_SHEET_DONOR_PORT_1 | validated | Warscar donor rows: ruled art picks wait for owned defs | C | donor rows awaiting owned defs |
| WAVE1_FIXES_DEPLOY_BEFORE_THE_CUT | proposed | Wave 1 W0-W1: back up, then deploy Armoury (durasteel 67153b072), StarWarsPatches, ResearchRetag, UtinniPat... | C | W0-W1 deploys precede the list the new world is made on |
| WAVE1_MODLIST_RETIRE_37_IN_ONE_LOAD | proposed | Wave 1 W3-W6: edited save copy, promote WAVE1_CANDIDATE to FULL.LATEST, one cold load, load the edited save... | C | list half is a prerequisite; its edited-save-copy half becomes obsolete |
| ALPHA_BIOMES_INSTALL_UNINSTALLED_RENDERS | proposed | Install the finished renders the 14 plants owe (TinkleGrass has no texture of ours; rotvar variants wait on... | A | art half of the AB retirement; placeholder allowed |
| BIOME_WORLD_SWITCH_WAVE_1 | doing | World-switch every donor/vanilla-painted tile to its owned RUT_ successor: MEASURED 2026-09-12 live export,... | A | in-place tile repaint of the OLD save; a fresh world is painted from the paint list instead |
| CRYPTOFORGE_HARVEST_RETIRE_1 | doing/blocked | Harvest then retire VQE Cryptoforge: (1) reproduce the 18 SALVAGE_PALETTE-cited props as owned RUT_/RSW_ Th... | A | per its block note only the canonical-save piece remains; a fresh save removes it |
| DEF_ALIAS_CHAIN_HASH_1 | validated | EnvironmentalHazards: Def aliases: chain resolution, typed keys, real historical terrain hashes | A | historical terrain hashes exist for old saves; shrinks to current aliases only |
| DESICCATED_LOOKALIKE_FAMILIES_1 | proposed/blocked | Dried-out corpse art shared by look-alike family (~450 jobs; 308 races draw no desiccated corpse today). Bl... | A | corpse art: placeholder allowed |
| DESSICATED_CORPSES_INSTALL_AFTER_PICKS | proposed | Sheet, owner picks and art.py install for the dessic_* renders; needs the renders landed | A | follows the redraw; off path |
| DESSICATED_CORPSES_REDRAW_ONE_BY_ONE | proposed | Draw the 63 donor-byte dessicated corpse pictures per species (artpipe jobs dessic_*); supersedes the look-... | A | donor-byte corpse art: placeholder allowed |
| DONOR_COATS_REDRAW_SIX_HUNDRED_TO_GO | proposed | Regenerate every def still wearing donor/stand-in/placeholder/vanilla art: 627 bound rows (765 job files) f... | A | placeholder art allowed: off the remake path (still owed for ship) |
| DONOR_PACK_TEX_REPAIR_SEVEN_LEFT_BEHIND | proposed | With Star Wars Animal Collection absent (SWBestiary dropped the donor, 3898fe6212; ratchet_pilot now forbid... | A | shrinks to a stand-in texture per missing path |
| DONOR_SAVE_ICONS_RENAME_IKEE_STILL_SULKING | proposed | P6 save rewrite: 6 ideo icons renamed in second donor-free copy; ikee rows held | A | P6 rewrite of the donor-free save copy; no old save to rewrite |
| DONOR_SUCCULENT_ART_DECIDE_A_STAND_IN | proposed | 13 plants and the lunger fry need art or a stand-in he picks | A | stand-in allowed: shrinks to one placeholder pick |
| EXCAVATION_LEGACY_MIGRATION_FLAG_1 | built | FlowWorks: Legacy rehydration: schema flag and a restoration policy for cells with no original terrain | A | rehydration policy for legacy-save cells; a fresh save has none |
| FUNGAL_SOIL_RESCUE_RETIRED_MOD_ART | proposed | RUT_FungalSoil needs owned art or a terrain stand-in | A | shrinks to a terrain stand-in |
| MOOKEE_TRADE_ANIMAL_IDENTIFY_1 | proposed | Identify the Rot trader animal named 'Mookee' (donor SW art) and own a realistic render | A | donor-art replacement; placeholder allowed |
| REGEN_RENDERS_INSTALL_AS_THEY_LAND | proposed | Install finished donor-regen renders accept-for-now; NEXT: run python3 src/RimMandrake/Utils/art/art_accept... | A | donor-regen installs: off the remake path |
| SAVE_RELIC_PRECEPTS_REPAIR_VWE_NULLS | built | Owner choice before wave 1 W3: replacement relics for the 5 VWE relic precepts (Hexlink, Loccorpus, Animal ... | A | null-repair in the old save goes; the relic CHOICE survives for the new ideoligion |
| STANDINS_RETIRE_AS_OUR_COATS_ARRIVE | proposed | Replace StandIn/ copies as renders land (175 StandIn PNGs); NEXT: after each install pass, list remaining X... | A | stand-ins are acceptable in the remade world; off path |
| SUCCULENT_PLANTS_REDRAW_BORROWED_WARDROBE | proposed | Redraw succulent plant stand-ins whose donor paths are gone | A | placeholder allowed: off the remake path |
| TEXREGEN_GAPS_REDRAW_EIGHTEEN_QUEUED | proposed | 18 biome art gaps with no render of ours in the artpipe state: jobs queued, collect and review | A | art gaps: placeholder allowed |
| WORLDMAP_AUDIT_LIVE_CHECKS_1 | doing | Four worldmap audit checks needing the live game — batch into next game-up window | A | audits of the current world; re-asked of the remade one |
| WORLDMAP_REPAIR_LOST_BIOMES_ROCKY_TEXTURES | doing | Repoint three lost biomes on the world; flatten rocky world-map textures | A | lost-biome repoint is save repair (1,903 tiles); rocky-texture half survives as world-texture work |
| ART_SIZES_AUDIT_AFTER_DONORS_LEAVE | proposed | Deep scan of art sizes (drawSize / visualSizeRange / bodySize vs sprite and fiction) for all flora and faun... | D | runs after donors leave |
| BIOME_ENRICHMENT_DESERT_WASTELAND_1 | doing | Enrichment wave (review B1): Desert (53% zero-mutator) + Wasteland (63%) — the two largest land biomes read... | D | zero-mutator share is a paint-time choice |
| BIOME_LANDMARK_REFINEMENT_1 | doing | First-pass landmark density on 8 dense biomes (Greentide/Contagion/Webwork/Weeping Stones/Slime/Scarlands/P... | D | landmark density authored at the paint, not patched live |
| DROIDWORKS_PRIMITIVE_TIER_1 | built/blocked | Primitive family: Jawa-fabricable frames/parts/modules at grossly inferior stats, the G2 repair droid (new ... | D | card 2026-10-09: deferred until after the world remake |
| FALL_LINE_MUTATOR_PLACEMENT_1 | proposed | Place the RUT_FallLine tile mutator on the 308 Fall Line + The Breaks tiles of the frozen world (bridge wor... | D | folds into the paint step (308 tiles) |
| PAINTER_REGIONS_RETHINK_GHOSTS_MAY_HAUNT | proposed | AFTER the one-time repaint: revisit the 5 painter-only regions (Ashteeth, Ember Sink, Fall Line Barrens, Sc... | D | explicitly AFTER the one-time repaint |
| PLANETARY_LOADSCREEN_RENDERS_2 | proposed/blocked | Photo-realistic loadscreen planet renders seeded from OUR post-repaint worldmap beauty shots (ring, real te... | D | needs post-repaint beauty shots |
| ROT_NAVIGATOR_CAMPAIGN_TILES_1 | proposed | Swallowed Navigator campaign tiles: name the carrier's Rot tile and the log's salvage-site tiles, then patch | D | named campaign tiles placed at creation |
| TWILIGHT_BOTTOM_CAST_1 | doing | The Deepwater bottom cast: 6-8 named residents of the lit bottom-houses (per-tile world objects), roles fro... | D | per-tile world objects placed at creation |
| UNUSED_MUTATORS_WORLD_ASSIGNMENT_1 | ready/blocked | Put the unused tile mutators and Geological Landforms landforms on the frozen world — 88 of ~380 in use, ze... | D | folds into the paint step; no live world_* edits |
| WARSCAR_PILGRIM_CAMP_SITES_1 | proposed | Pilgrim camps as world SitePartDefs at authored locations on the fixed planet (WARSCAR_PILGRIM_CAMPS_1 spec... | D | authored world sites placed once at creation |
| WORLDMAP_BIOME_APPEARANCE_1 | proposed/blocked | Regenerate our biomes' worldmap tile appearance AFTER the terminal repaint - measured 2026-09-27: only 2 of... | D | blocked on the paint; remake is the paint |
| WORLDMAP_DOCS_PASS_1 | ready | Worldmap canonical-docs pass with the owner: reconcile every doc to the authored world, rulings verbatim | D | docs reconcile to the authored world once it settles |
| ABYSS_CRAGS_ART_ON_PORTED_DEFS_1 | proposed/blocked | Wire the 12 done crags_* art sets (+ the dusk rat redo when commissioned) onto the Abyss's ported defs as D... | B | art wiring onto ported defs; follows DONOR_DEFS_PORT_TO_OURS_1 |
| ABYSS_DARK_MUFFLE_ALL_SOUNDS_1 | built | Abyss: the Dark muffles every map sound (Harmony on sample creation) | B | biome/mod content at def or map level; carries into a remade world |
| ABYSS_FIRST_SCRIPT_1 | validated | First north-star script: Abyss | B | mod validation script/trial; world-independent |
| ABYSS_HIDDEN_SHIP_PROBES_1 | built | The Abyss: hidden-ship cover; probe droids still come and must be avoided | B | biome/mod content at def or map level; carries into a remade world |
| ABYSS_LIGHTFALL_BROOD_WRECK_1 | validated | Lightfall's bottom: the dragons' brood and the wreck that repairs your ship | B | biome/mod content at def or map level; carries into a remade world |
| ACC_BIOMES_FIXES_LIVE_RERUN_1 | proposed | Live re-run of the four acc_biomes marks/settings fixes from 220d7a754 (GelatinousSlime, LeaningScrub, Rust... | B | tooling / harness / process; world-independent |
| ALLOWLIST_DIAGNOSE_BARE_MIXED_PATCHES | proposed | Wild-plant allowlist empties mixed-biome patches' candidate lists without supplying native grass | B | biome/mod content at def or map level; carries into a remade world |
| ALT_GRAPHICS_FIX_SIX_SECOND_FACES | proposed | Alternate pictures (alternateGraphics) never ruled on for Eopie, Falumpaset, KowakianMonkeyLizard, Hssiss, ... | B | code fix at map/def level; carries over unchanged |
| AMBROSYX_SOURCE_BUILD_DISH_BEFORE_SHROOM | built | No plant in the live def dump gives RM_AmbrosyxShroom; the Rot needs an ambrosyx source before RM_Render_Am... | B | biome/mod content at def or map level; carries into a remade world |
| ANCIENT_WAR_LAB_1 | doing | The war lab beneath the propane lake over the Impact Site — submerged dungeon, lab fauna + mechanoid guardi... | B | biome/mod content at def or map level; carries into a remade world |
| ANT_HIVE_REAL_GEOMETRY_1 | proposed | FeverWood: Ant hive genstep builds real enclosed rooms | B | biome/mod content at def or map level; carries into a remade world |
| AQUATIC_WATER_BREATHING_GENE_1 | doing | Design and build a real water-breathing mechanism (gene or hediff) for the 4 aquatic xenotypes currently mi... | B | biome/mod content at def or map level; carries into a remade world |
| ARMOURY_JUMPPACK_INVALID_IL_1 | validated | Armoury JumppackForMeleeAI transpiler on JobGiver_AIFightEnemy.TryGiveJob throws InvalidProgramException at... | B | biome/mod content at def or map level; carries into a remade world |
| ARMOURY_PROJECTILE_DAMAGE_TOOL_1 | validated | Bridge tool reading projectile damageAmountBase (private) so Armoury's ranged ladder can be asserted live | B | tooling / harness / process; world-independent |
| ARTIST_BIOME_INSPIRATION_MOD_1 | proposed | New mod idea (owner, 2026-09-29): artists above ~10 skill get an inspirational biome that boosts art made t... | B | art for our own defs; unaffected by the remake |
| ARTPIPE_FACING_COHERENCE_1 | ready | Facing sets are three independent side-profiles: no view direction in north/south prompts, no cross-facing ... | B | tooling / harness / process; world-independent |
| ART_OVERRIDE_FAMILY_SCRIPT_1 | doing | One parametrized north-star script for the 48 *ArtOverride mods | B | art for our own defs; unaffected by the remake |
| ART_PAINTERLY_RESTORATION_1 | ready | MAJOR RULING 2026-09-14: painterly style restored (Ronto exemplar), cartoonish pipeline stood down, legibil... | B | art for our own defs; unaffected by the remake |
| ART_SHEETS_SCALE_CELLS_WIDEN_TOO_LATE | proposed | Art sheets and briefs carry cell footprint and scale | B | tooling / harness / process; world-independent |
| ART_SHEETS_TAIL_1 | proposed | Ruled biome sheets tail: rerun refresh_ruled_sheets.sh as Greentide (177) and LongShade (68) renders land; ... | B | tooling / harness / process; world-independent |
| ART_SHEET_REDESIGN_FRESH_OR_REFUSE | proposed | Art review sheets must guarantee freshness by construction (hashes/hooks/design): never serve an image that... | B | tooling / harness / process; world-independent |
| ART_SUBJECT_RESOLVER_1 | proposed | One shared art/canon resolver (subject.py) for every sheet, census and tool; jobs bind their target; backfi... | B | tooling / harness / process; world-independent |
| ART_TEXTURE_GAPS_FOLLOWUP_1 | doing | Install owed art: RM_Braskeen, RM_Ismerrow, KOTOR small crystals, AA_Swarmling (texture_audit dead paths) | B | art for our own defs; unaffected by the remake |
| ART_VERSION_WRANGLING_1 | proposed | Art wrangling: find every art variant per creature (artpipe, review sheets, deployed, git history, donor), ... | B | tooling / harness / process; world-independent |
| ASHKARR_WEATHER_INSTALL_THE_SLEEPING_STORMS | proposed | Add mandrake.rut.weathersuite (Ashkarr Weather Suite) to the active list after mandrake.rm.weathersuite so ... | B | biome/mod content at def or map level; carries into a remade world |
| ASH_FIELD_FIX_FORGETS_THE_WATER | built | Ash field live state stale: wateredUntil unsaved, black-rain 0 keeps expiry, overlay not dirtied, static la... | B | code fix at map/def level; carries over unchanged |
| ASH_TERRAIN_FIX_NO_MEDIUM_GROUND | built | Deep ash + scorchable ground lack Medium affordance: Medium-support buildings/floors cannot be placed on ~8... | B | code fix at map/def level; carries over unchanged |
| ASSAILANT_DUNGEON_BUILD_1 | doing/blocked | Build the Assailant flesh dungeon: frozen first-impact complex, thaw-gated, deep Umbra | B | biome/mod content at def or map level; carries into a remade world |
| ASSAILANT_SALVAGE_FIRST_SCRIPT_1 | built | First north-star script: AssailantSalvage | B | mod validation script/trial; world-independent |
| ASSAILANT_WARLAB_BUILD_MERGE | proposed | Assailant complex IS the war lab: fold ASSAILANT_DUNGEON_BUILD_1 and ANCIENT_WAR_LAB_1 into one build, reco... | B | biome/mod content at def or map level; carries into a remade world |
| ASTEROID_DESERT_ORES_1 | built | Doonium asteroid ore smelted aboard with glower crust; rare desert phrikite smelted aboard into phrik | B | biome/mod content at def or map level; carries into a remade world |
| ATMOSPHERIC_BASE_BUILD_PROGRAM_1 | doing | AtmosphericBase (mandrake.rm.atmosphericbase): the ambient framework the gods speak through — light AND sou... | B | biome/mod content at def or map level; carries into a remade world |
| AWARENESS_GENPAWN_TAME_ARM_BEFORE_USE | built | GeneratePawn awareness hook installs lazily (on arm, from the main thread) unless awareness_settings.json s... | B | tooling / harness / process; world-independent |
| AWAY_DASHBOARD_BUILD_1 | proposed | Build the beautiful floating 'what is happening / while you were away' dashboard widget with red (OOM, stop... | B | tooling / harness / process; world-independent |
| AXIS_SURGE_CLAMP_DRIFT_1 | built | EnvironmentalHazards: Gradient surge recede over-corrects saturated cells | B | biome/mod content at def or map level; carries into a remade world |
| BACTA_FIRST_SCRIPT_1 | built | First north-star script: Bacta | B | mod validation script/trial; world-independent |
| BACTA_REVIVAL_MECHANIC_1 | built/blocked | Bacta revival of the recently dead (owner ruling: works on dead bodies IF retrieved within a few hours): co... | B | biome/mod content at def or map level; carries into a remade world |
| BACTA_TANK_ART_1 | doing | Bacta tank art from the ESB canon image (tall 2:1 cylinder, translucent pale-blue backlit fluid, bubbles, w... | B | art for our own defs; unaffected by the remake |
| BACTA_TANK_CORE_1 | validated | Bacta Tank core: RSW mod skeleton, tank building, trade-scarce fluid on the LiquidDef registry, CompBactaIm... | B | biome/mod content at def or map level; carries into a remade world |
| BAZAAR_BANTER_LINES_1 | doing/blocked | The Bazaar slice 5: authored banter pools (day one) + dormant claude -p Oracle consumer gated on ORACLE_EXP... | B | biome/mod content at def or map level; carries into a remade world |
| BAZAAR_BROKER_TAB_1 | doing/blocked | The Bazaar slice 4: bulk-liquid Broker tab — renders Liquid Logistics' tank API both directions at worldTag... | B | biome/mod content at def or map level; carries into a remade world |
| BAZAAR_DISPLACEMENT_PASS_1 | proposed/blocked | Retire Trade UI Revised + Utility Columns + VTE from the campaign list after Bazaar slices 1-2 prove live; ... | B | UI-mod retirement; no world/save coupling |
| BAZAAR_HAGGLE_DUEL_1 | doing/blocked | The Bazaar slice 3: WHOLE-DEAL patience-meter haggle duel (owner: per-item rejected as monotonous) — crits ... | B | biome/mod content at def or map level; carries into a remade world |
| BAZAAR_PRICE_ENGINE_1 | validated/blocked | The Bazaar slice 2: read-side RM_BazaarEconomy (worldTag-seeded buckets, history ring, drift+clamp) + intel... | B | biome/mod content at def or map level; carries into a remade world |
| BAZAAR_STOLEN_GOODS_PROPERTY_1 | proposed | Stolen goods as a trade mechanic: RimProperty integration, the scanner registry, and the transponder reader | B | biome/mod content at def or map level; carries into a remade world |
| BAZAAR_WINDOW_GRID_1 | doing | The Bazaar slice 1: Dialog_Trade replacement via WindowStack.Add intercept + virtualized grid, presets, wis... | B | biome/mod content at def or map level; carries into a remade world |
| BEACH_RING_RETIRE_DRAINED_MEANS_DRY | validated | Natural-water default: no 0.5 m shore shelf (owner 2026-10-18: drained means dry); lakeShoreShelfMetres def... | B | framework mechanic (map level); carries over unchanged |
| BEDAZZLE_TOP_SHAPE_PROGRAM_1 | proposed | Bedazzle top-shape program: re-score 12, finish seas, build backlog, rites over the 11 | B | biome/mod content at def or map level; carries into a remade world |
| BELT_WATER_HARNESS_1 | built | Bland-map water cell helper: Miasma return proof and Greentide vurrak need water; paint via set_terrain_bat... | B | biome/mod content at def or map level; carries into a remade world |
| BESKAR_ARMORER_QUEST_1 | proposed | Blackstar quest to a rare Mandalorian armorer, the only way to reforge beskar (quest design needs the owner) | B | content/design at map or def level; survives the remake |
| BIG_CREATURES_DESIGN_WALLS_AND_SLOTS | built | Design pass + GPT review: big creatures vs narrow slots, thin walls, roofs, squeezing | B | content/design at map or def level; survives the remake |
| BILEWORM_CORPSE_ROT_1 | built | Bileworm: corpses near it rot fast into corpse bile it drinks; colonists nearby feel the stench (descriptio... | B | biome/mod content at def or map level; carries into a remade world |
| BIOME_ARRIVAL_LETTERS_ALL_1 | validated | X-6/FV-5: arrival letter per biome that has had its sitting, starting with Fever Wood; names heat kind and ... | B | biome/mod content at def or map level; carries into a remade world |
| BIOME_FLORAFAUNA_ART_REVIEW_1 | proposed | Biome FloraFauna Art Review: one sheet per biome covering every flora+fauna row, >=1 art version each, cano... | B | art for our own defs; unaffected by the remake |
| BIOME_GROUP_SIZE_WALK_1 | proposed | Per biome, on its review sheet, walk every custom creature with the owner and set the typical group size it... | B | biome/mod content at def or map level; carries into a remade world |
| BIOME_MAP_GENERATORS_DESIGN_1 | proposed | BIOME_MAP_GENERATORS_DESIGN_1 | B | content/design at map or def level; survives the remake |
| BIOME_NUISANCE_NORMALIZATION_1 | proposed | Nuisance/solvent normalization pass over ALL biomes, run at the end of the last biome detailing (owner tick... | B | biome/mod content at def or map level; carries into a remade world |
| BIOME_SHIP_CONTRIBUTIONS_1 | proposed | Every-biome pass: how does each biome uniquely improve the SHIP - what players take aboard (owner 2026-09-2... | B | biome/mod content at def or map level; carries into a remade world |
| BIOME_SPRINT_PROVE_SCRUB_SETS_PACE | proposed | Next sprint: Cauldron, Contagion and LeaningScrub fully to done (art + mechanics + 0-fail/0-unmeasured suit... | B | biome/mod content at def or map level; carries into a remade world |
| BIOME_TRANSITIONS_JUDGE_VS_BAROQUE | proposed | Judge Biome Transitions against our Baroque Biomes: with baroque biomes it may no longer make sense and nee... | B | biome/mod content at def or map level; carries into a remade world |
| BIOME_VISUAL_BEDAZZLE_PASS_1 | proposed | Visual bedazzle pass on every biome (ground, colour, density), AFTER all biomes are green-code, art-complet... | B | biome/mod content at def or map level; carries into a remade world |
| BLOWER_ROOM_COOLER_1 | validated | Dry-air blower becomes a special room cooler: never heats a room, cools the room behind it; power and stren... | B | biome/mod content at def or map level; carries into a remade world |
| BLUEDESERT_FLORA_PLANT_REFUSAL_1 | proposed | BlueDesert flora_spawns still refuses 8 plants at tile temp -5 (retile read back): read set_plants message,... | B | biome/mod content at def or map level; carries into a remade world |
| BLUEDESERT_GPT_ENRICHMENT_1 | doing | Blue Desert enrichment (GPT consult 2026-09-30, owner-picked by card): blue-ice heat sink, the line gives b... | B | biome/mod content at def or map level; carries into a remade world |
| BLUEDESERT_MECHANICS_BUILD_1 | doing/blocked | Build the Blue Desert mechanics: vhaulk trigger-gated detonation (EMP-on-hit trap), Warnings study ladder +... | B | biome/mod content at def or map level; carries into a remade world |
| BLUE_DESERT_FIRST_SCRIPT_1 | built | First north-star script: BlueDesert | B | mod validation script/trial; world-independent |
| BONES_LEAN_PORT_BUILD_TREELESS_WORLD | proposed | Owner card: lean port of Bones to our own tier (bone as building stuff, our art and numbers, no fuel/plaste... | B | biome/mod content at def or map level; carries into a remade world |
| BRAIN_WORMS_FIRST_SCRIPT_1 | built | First north-star script: BrainWorms | B | mod validation script/trial; world-independent |
| BRIDGE_CALL_EVIDENCE_WIRE_LOST_REPLY_UNKNOWN | built | rimbridge_client writes bounded per-call evidence for every caller; a mutating call with a lost reply is IN... | B | tooling / harness / process; world-independent |
| BRIDGE_LOCK_CROSS_CLONE_RACE_1 | built | rimflow bridge take can't see the other clone's unpushed take: BENCH and FOUNDRY both held the bridge 2026-... | B | tooling / harness / process; world-independent |
| BRIDGE_LOCK_HARDEN_ALIVE_MEANS_A_PID | built | exclusive driver lock keyed on process identity with O_EXCL acquisition, heartbeat/PID liveness, loud failu... | B | tooling / harness / process; world-independent |
| BRIDGE_STALL_DIAGNOSTIC_1 | proposed | When a bridge call blocks past ~60 s, record what the game's main thread is doing (managed stack dump / cur... | B | tooling / harness / process; world-independent |
| BRIDGE_TARGETS_HARDEN_STALE_AFTER_RELOAD | built | Game/map epoch guards: reserved call arguments expectGameEpoch / expectMapId / expectCurrentMapId refused a... | B | tooling / harness / process; world-independent |
| BRIDGE_TPS_CAPTURE_FIXES_1 | validated | TPS record fixes from the Opus+GPT reviews: auto-start at load, keep stalls, correct window maths, dependab... | B | tooling / harness / process; world-independent |
| BRIDGE_TPS_REGULAR_REPORT_1 | built | Bridge regularly samples and reports game TPS during use: continuous gathering, a rolling record on disk, a... | B | tooling / harness / process; world-independent |
| BRIDGE_TPS_REVIEW2_FIXES_1 | built | Repair TPS record build 2 per second GPT review: 17 MUST fixes (profiler skip-safety, measurement boundarie... | B | tooling / harness / process; world-independent |
| BRONZIUM_DROP_1 | built | Drop bronzium from the game (split out of MATERIAL_MERGES_CLEANUP_1) | B | biome/mod content at def or map level; carries into a remade world |
| BURN_HISTORY_FIX_ANCHOR_NEVER_AGES | built | Burn history pruned only on new samples: fireless map keeps an arbitrarily old herd anchor | B | code fix at map/def level; carries over unchanged |
| CAGE_CROP_SNAPSHOT_FIDELITY_1 | built | TerminalBiomes: Cage crop transport keeps only def+growth and world-space offsets | B | biome/mod content at def or map level; carries into a remade world |
| CANAL_LAKE_COLOUR_UNIFY_TWO_BLUES | proposed | Water in a dug canal and the lake it joins are drawn in different colours (seen in the 2026-10-17 water-sce... | B | framework mechanic (map level); carries over unchanged |
| CANAL_OBJECTS_SHEET_BUILD_POSES_AND_STYLES | proposed | Labelled sheet of every ladder pose, weirs, fords and the four material styles of tank, reel and weir | B | art for our own defs; unaffected by the remake |
| CANON_CREATURE_REGEN_1 | doing | Regenerate every SW-canon creature from library guidance (library CANON_REFERENCE_LIBRARY_1 is done; + pilot sheet ... | B | biome/mod content at def or map level; carries into a remade world |
| CANON_DRAIN_1 | proposed | Total canon drain: reconcile every lore doc to ONE level of truth, grinding out all superseded/obsoleted st... | B | biome/mod content at def or map level; carries into a remade world |
| CANON_FAUNA_FLORA_GPT_REVIEW_1 | proposed | GPT review of the Star Wars fauna/flora canon library: criticism, corrections, enrichment (text only, no im... | B | biome/mod content at def or map level; carries into a remade world |
| CANON_HERD_LORE_ARBITRATION_1 | proposed | Arbitrate 45 canon creatures whose herd/pack status canon leaves UNCLEAR - Transient/canon_herd_lore_2026-1... | B | biome/mod content at def or map level; carries into a remade world |
| CANON_MATERIALS_BUILD_1 | proposed | Build the decided canon materials design: RSW_Durasteel with donor conversion, plasteel salvage/trade only,... | B | biome/mod content at def or map level; carries into a remade world |
| CANOPY_LAYER_BUILD_ROOF_OF_THE_WORLD | proposed | Zoom-gated canopy layer: Titanic (opt. Giant) trees draw trunk always, canopy fades in only when zoomed out... | B | framework mechanic (map level); carries over unchanged |
| CANOPY_SHADE_DESIGN_BIG_DARK_PATCHES | proposed | Jungle-adjacent heavily vegetated biomes (Webwork, Greentide, LongShade...): tree canopy casts BIG shade pa... | B | content/design at map or def level; survives the remake |
| CARGO_FLOAT_LAUNCH_PUSH_1 | built | TerminalBiomes: "Load and launch" does not launch and loads only its own cell | B | biome/mod content at def or map level; carries into a remade world |
| CATHEDRAL_DESCENT_REVEAL_SITE_1 | doing/blocked | The A7 real under-plate descent site + reveal beat + A1 Utinni-receiver lore propagation | B | biome/mod content at def or map level; carries into a remade world |
| CATHEDRAL_EXPOSURE_COMPLETION_1 | built | The A6 pyrrhic discovery ending: witnessed fall, warzone flip, priced Hutt extraction, ship mourns | B | biome/mod content at def or map level; carries into a remade world |
| CATHEDRAL_MECHANOID_PASS_VERBS_1 | validated/blocked | GRANT/REVOKE mechanoid-pass instrument, scoped Harmony hostility exception (C#, row-3) | B | biome/mod content at def or map level; carries into a remade world |
| CATHEDRAL_MISSION_BOON_OFFERS_1 | doing/blocked | Deniably-sourced Assailant missions + Heat-gated gravtech boons | B | biome/mod content at def or map level; carries into a remade world |
| CATHEDRAL_REGARD_BLACKBOARD_1 | built | Cathedral Regard counter + stage machine + exposure pressure on the GM blackboard, shadow-mode first | B | biome/mod content at def or map level; carries into a remade world |
| CATHEDRAL_STAGE_COMMENTARY_POOLS_1 | built | Stage-keyed RUT_HumCommentary pools + the bans-2/6 linter gate every arc item runs | B | biome/mod content at def or map level; carries into a remade world |
| CATHEDRAL_STAGE_HUM_BRIDGE_1 | built | Stage-to-hum-baseline bridge lane into RM_BiomeAttitudeDef (C#, row-3) | B | biome/mod content at def or map level; carries into a remade world |
| CATHEDRAL_SURVEY_MISDIRECTION_QUEST_1 | doing/blocked | The A4 Imperial-survey misdirection quest, three branches, K2 anti-laundering | B | content/design at map or def level; survives the remake |
| CAULDRON_ENRICHMENT_LIVE_PROOF_1 | validated | Quicktest-prove the offline-built Cauldron enrichment: assay grade line, vexxiss poisoned-water letter, net... | B | biome/mod content at def or map level; carries into a remade world |
| CAULDRON_ENRICHMENT_VISUALS_1 | validated | Cauldron enrichment visuals: dewfall chemical beads, dewfall plant saturation, assay flecks on old trees, v... | B | biome/mod content at def or map level; carries into a remade world |
| CAULDRON_FLECKS_FILL_SEVEN_STILL_BLANK | proposed | Cauldron: draw the 7 missing overlay textures (2 assay flecks, 5 dew variants); O-TEX fails on them | B | biome/mod content at def or map level; carries into a remade world |
| CAULDRON_HUSH_FIX_COUNT_FORGETS_ON_LOAD | built | Cauldron: hushedThisFalter not scribed (RM_CauldronVents.cs ~274) | B | code fix at map/def level; carries over unchanged |
| CAULDRON_MECHANICS_BUILD_1 | built/blocked | Build the Cauldron mechanics: engine-underfoot soundscape + falter tell, four ratified weathers, flammable ... | B | biome/mod content at def or map level; carries into a remade world |
| CAULDRON_ROAST_FIX_RAW_FOOD_MOOD_STAYS | built | Cauldron: roasted tsevrix still gives ate-raw-food mood (RM_CauldronFloraItems.xml:53) | B | code fix at map/def level; carries over unchanged |
| CAULDRON_SUITE_WIDEN_RUINS_STILL_UNREAD | proposed | Cauldron suite: add rows for Filter-Works converting, ruins at mapgen, Oomo shrine, gas drift (ruled scope,... | B | biome/mod content at def or map level; carries into a remade world |
| CAULDRON_TOGGLE_FIX_JOBS_FINISH_ANYWAY | built | Cauldron: vent-drink/attack jobs ignore setting turned off mid-job (RM_CauldronVents.cs ~160, RM_CompVexxis... | B | code fix at map/def level; carries over unchanged |
| CAULDRON_VENT_ENRICHMENT_HOOKS_1 | validated | Cauldron enrichment pieces that hang on vents: weather vent multipliers + vent-local exposure + falter, vex... | B | biome/mod content at def or map level; carries into a remade world |
| CAULDRON_YIELD_LIVE_RERUN_1 | proposed | Live re-run of modcheck Cauldron yield/yield_factor_scales + yield_toggle_off after harness fix 09d32ba8f (... | B | biome/mod content at def or map level; carries into a remade world |
| CHANNEL_CURRENT_CADENCE_FIDELITY_1 | built | TerminalBiomes: Channel current runs slower than its kernel says and can be crossed unseen | B | biome/mod content at def or map level; carries into a remade world |
| CHILL_AIR_PUMP_1 | validated | DI-2: air pump building oxygenates a sealed Chill room (per-provider counts); power cost; research-gated; s... | B | biome/mod content at def or map level; carries into a remade world |
| CHILL_AURORA_UNATTENDED_SOURCE_1 | built | DivingInteraction: Drowned aurora on a floor map whose surface map is not loaded | B | biome/mod content at def or map level; carries into a remade world |
| CHILL_DIVE_DENSITY_SAMPLER_1 | built | Chill dive spawns obey density (not one-of-each); number set on a live walk with the owner, leaning 2-4 (Q6) | B | biome/mod content at def or map level; carries into a remade world |
| CHILL_SUIT_SHELTER_RULE_1 | built | DivingInteraction: Heated suit drain/recharge uses roof and straight-line distance | B | biome/mod content at def or map level; carries into a remade world |
| CHILL_SURFACE_SITTING_1 | proposed | The Chill surface: its own full biome pass sitting (Burner guardian place, shore ecology) | B | biome/mod content at def or map level; carries into a remade world |
| CHOTRIX_HUNT_TARGET_REVALIDATE_1 | built | Scarlands: Chotrix hunt does not re-check "lone prey" after choosing | B | biome/mod content at def or map level; carries into a remade world |
| COLD_LOAD_RUN_SHEET_4 | doing | Run sheet for the next full-list load: three readings owed from the 2026-09-06 offline wave | B | art for our own defs; unaffected by the remake |
| COMMISSION_LEDGER_CLEANUP_1 | doing | 85 genuinely-owed new-art/def commissions from the 118-row ledger | B | tooling / harness / process; world-independent |
| COMPANION_PROFILE_ENFORCE_SAFE_BY_DEFAULT | validated | Runtime safe profile for the JawaBench companion: every jawa tool not on a reviewed read-only allow-list re... | B | tooling / harness / process; world-independent |
| CONTACT_VENOM_NONLETHAL_ORDER_1 | built | EnvironmentalHazards: Nonlethal venom option clamps after the pawn is already dead | B | biome/mod content at def or map level; carries into a remade world |
| CONTAGION_ARMS_UNTANGLE_SITE_ALREADY_SICK | built | Contagion northstar: split the test arms so the suite runs on a saved Contagion site (northstar_site.py ref... | B | tooling / harness / process; world-independent |
| CONTAGION_CLAWS_FIX_ABSTRACT_VERB | built | Contagion: Unfinished claw/spike/fang name abstract Verb_MeleeAttack (RM_UnfinishedHediffs.xml:47,68,89) | B | code fix at map/def level; carries over unchanged |
| CONTAGION_DIVE_FIX_FOUR_WALLED_CELLS | built | Contagion: UV-shy dive always tries same nearest 4 shelter cells (RM_SkyKernel.cs:242, ContagionBurn.cs:88) | B | code fix at map/def level; carries over unchanged |
| CONTAGION_DIVE_HARDEN_WANDERERS_WELCOME | doing | Contagion native_dives_for_roof: add a no-Burn wander control (a native wandering onto the 8x8 patch passes... | B | biome/mod content at def or map level; carries into a remade world |
| CONTAGION_FIRST_SCRIPT_1 | built | First north-star script: Contagion | B | mod validation script/trial; world-independent |
| CONTAGION_INJECT_FIX_CANCEL_STILL_STABS | built | Contagion: interrupted inject job still starts gestation and eats sample (JobDriver_RM_InjectGenomeSample.c... | B | code fix at map/def level; carries over unchanged |
| CONTAGION_INJECT_FIX_HOST_WANDERS_OFF | built | Contagion: inject delay toil has no reach check (JobDriver_RM_InjectGenomeSample.cs:44-47) | B | code fix at map/def level; carries over unchanged |
| CONTAGION_MECHANICS_BUILD_1 | validated/blocked | Build the Contagion mechanics: Burn/Bloom weather + tells, the Coalescence (one growing organism), Cloud Re... | B | biome/mod content at def or map level; carries into a remade world |
| CONTAGION_SINKERS_FIX_RESET_AFTER_LOAD | built | Contagion: sink animation restarts after load mid-tell (RM_MapComponent_ContagionSky.cs:107) | B | code fix at map/def level; carries over unchanged |
| CONTAGION_SITE_BUILD_SKY_STAYS_CALM | proposed | Saved RM_Contagion test site (on-Contagion arm), no Burn at save/load | B | test-site save, not the canonical one (test sites carry donor residue too: UNMEASURED scope) |
| CONTAGION_WOMBPOD_FIX_SAC_NEVER_HATCHES | built | Contagion: RM_WombpodSac inherits tickerType Never so CompHatcher never ticks (RM_WombpodSac.xml:32) | B | code fix at map/def level; carries over unchanged |
| CORD_GRAPH_TOPOLOGY_REVISION_1 | built | GimmeSomeSlack: Cord graph rebuilds the whole map for every section reprint; motion rescans all pieces per ... | B | framework mechanic (map level); carries over unchanged |
| CORPSE_SITE_SAFETY_1 | built | Titan corpse-site conversion and harvest safety from the full GPT review (B3.1 deferred conversion, B3.3 sp... | B | biome/mod content at def or map level; carries into a remade world |
| CRACKEDLANDS_ENRICHMENT_QUICKTEST_1 | built | Quicktest-prove the Cracked Lands enrichment tranche by state reads: five beats, peakstorm odds, recede fea... | B | biome/mod content at def or map level; carries into a remade world |
| CRACKEDLANDS_FIVE_BEATS_AUDIO_1 | built | Bespoke audio for the five beats (6 SoundDefs on vanilla-clip placeholders) + the tarruq's call; owner: aud... | B | biome/mod content at def or map level; carries into a remade world |
| CRACKEDLANDS_MECHANICS_BUILD_1 | doing/blocked | Build the Cracked Lands mechanics: the Swale (FlowWorks-normal, Utinni-locked biome discovery), survey+cist... | B | biome/mod content at def or map level; carries into a remade world |
| CRACKEDLANDS_SWALE_CAMPAIGN_LOCK_1 | ready/blocked | Utinni lock for RM_Swale: locked in the campaign until discovered in the Cracked Lands (first completed sur... | B | biome/mod content at def or map level; carries into a remade world |
| CRACKEDLANDS_THREE_HEIGHT_FLORA_1 | proposed | Qirra mats + talus clasps (names swept clean): art to review sheet before defs; owner: what 'pry cracks wid... | B | biome/mod content at def or map level; carries into a remade world |
| CRADLE_STRIKE_RECONCILE_WITH_LAB_DIVE | proposed | Cradle strike on the war lab vs the player's own lab dive: reconcile (owner card 11, 2026-10-10) | B | biome/mod content at def or map level; carries into a remade world |
| CREATURE_ALARM_ORIGIN_SHARE_1 | built | CB-1: disturbed creature reserves its own alarm share before propagation | B | biome/mod content at def or map level; carries into a remade world |
| CREATURE_BEHAVIORS_FIRST_SCRIPT_1 | validated | First north-star script: CreatureBehaviors | B | mod validation script/trial; world-independent |
| CREATURE_BEHAVIORS_SETTINGS_SCREEN_1 | built | CB-5: CreatureBehaviors settings screen usable: group ~106 controls by mechanic, search, reset per group, w... | B | biome/mod content at def or map level; carries into a remade world |
| CREATURE_BEHAVIOR_LAST_OUTCOME_1 | validated | CB-7: Ambushers, lures and alarms record last outcome | B | biome/mod content at def or map level; carries into a remade world |
| CREATURE_JOB_INTERRUPTION_POLICY_1 | built | CreatureBehaviors: One shared targeting and interruption policy for the forced-job creature comps | B | biome/mod content at def or map level; carries into a remade world |
| CREEP_WEB_HARVEST_LIVE_1 | proposed | Live-check the creep-web colonist harvest (SHOKKWEAVE_SOLE_SOURCE_1 route 4, 6c1f40e9d): deploy Webwork DLL... | B | biome/mod content at def or map level; carries into a remade world |
| CUT_FALLOUT_GENERATED_DATA_1 | built | Load C fallout from the Caverns + Polluted Lands cuts (MEASURED 2026-09-19, Transient/harvest_loadC_triage_... | B | biome/mod content at def or map level; carries into a remade world |
| DANGER_CLOCK_ALERTS_1 | built | DI-4: alerts for heated-suit low/empty and brine-encased smother clock | B | biome/mod content at def or map level; carries into a remade world |
| DEAD_OR_INERT_SETTINGS_1 | built | Settings the def lints found unwired: wire or delete per mod (Scarlands, EmpirePursuit done; TerminalBiomes... | B | framework mechanic (map level); carries over unchanged |
| DECOY_SHADE_TARP_1 | validated | CB-8: decoy shade tarp read as shade by heat-driven predators, no cooling; mirrak-hide variant; research-ga... | B | biome/mod content at def or map level; carries into a remade world |
| DEEPFIRE_FAMILY_SETTINGS_SAVE_LOAD_1 | proposed | Live Scribe round-trip of keyed family settings incl. legacy-list migration (65798d581) | B | framework mechanic (map level); carries over unchanged |
| DEEPFIRE_HEALTH_CHECK_1 | built | LP-9: Deepfire health check: debug action listing orphan light proxies, pawn lights on the wrong map and cl... | B | framework mechanic (map level); carries over unchanged |
| DEEPFIRE_SETTINGS_LIGHT_REFRESH_1 | built | LuminousPigment: Settings changes should refresh every existing deepfire light | B | framework mechanic (map level); carries over unchanged |
| DEEPFIRE_WORLD_LIGHT_1 | built | X-9 (card ruled): glow-seekers drawn to deepfire, deepfire raises night visibility, glowing pawn cannot use... | B | framework mechanic (map level); carries over unchanged |
| DEEPS_FAUNA_MECHANICS_1 | built | Deeps creature mechanics from the fauna verdicts: Grabber hold-and-crush, Soulchime psychic stun + tamed so... | B | biome/mod content at def or map level; carries into a remade world |
| DEEPS_FAUNA_MECHANICS_2 | built | Deeps fauna mechanics, second pass on DEEPS_FAUNA_MECHANICS_1: grabber-side crush comp + rescue roll, soulc... | B | biome/mod content at def or map level; carries into a remade world |
| DEEP_DIG_BUILD_DROIDS_TAKE_THE_SHOVEL | proposed | Digging deeper than 4: a digging machine, a self-digging digger droid, and droids that can operate the mach... | B | framework mechanic (map level); carries over unchanged |
| DEEP_DRILL_HOME_BIOME_1 | doing | Deep drilling: iron everywhere, every other deep deposit only in its home biome - Harmony postfix on CompDe... | B | biome/mod content at def or map level; carries into a remade world |
| DEEP_LAYER_BELT_HARNESS_1 | proposed | LanternDeeps Deep-layer proofs say comp only on a Deep: harness needs a Deep map; Nightside shivven needs a... | B | biome/mod content at def or map level; carries into a remade world |
| DERELICT_LABS_DESIGN_ONE_MORE_MUTATOR | proposed | Derelict gene lab as a normal world mutator (replaces AB_DerelictBioLab); design from the derelict study, v... | B | replaces an unported AB mutator: add after, paint it in later or leave |
| DESERT_WRAPS_ART_COMMISSION_1 | doing | Original desert-wrap apparel art (full body-type matrix) + devolved Tusken head shape, inspired-not-copied;... | B | art for our own defs; unaffected by the remake |
| DESIGN_MATERIALS_REVIEW_1 | proposed/blocked | DesignMaterials: first-ever whole-game materials balance review - normalize Star Wars + RimWorld exotic all... | B | content/design at map or def level; survives the remake |
| DESTROY_BATCH_NEVER_KILLS_PAWNS_1 | doing | jawa/destroy_batch never destroys pawns: Cauldron kill_pawns() and northstar despawn_pawns_in() rely on it ... | B | tooling / harness / process; world-independent |
| DEV_SCRATCH_DIRS_MIGRATE_OFF_LODESTARS_LAWN | proposed | Move the live D:\Luke\dev\_* runtime dirs (artpipe, artstore, rmscratch, rmbuild, obs, rmdashboard) under o... | B | tooling / harness / process; world-independent |
| DEWBACK_ART_RECONCILE_ONE_LIZARD_MANY_CARDS | doing | Dewback art is split across several texPaths/sheet cards (RimStarWars/SWBestiary/Dewback, swanimals/Dewback... | B | art for our own defs; unaffected by the remake |
| DIG_ROCK_TUNE_STONE_FIGHTS_BACK | doing | Canal digging: through rock yields rock chunks at the vanilla rock-wall mining rate and takes much more wor... | B | framework mechanic (map level); carries over unchanged |
| DIRECT_SUN_LIVE_VERIFY_ANGLE_NOT_BIOME | proposed/blocked | Direct Sun live rows: L1 state reads on three maps (same angle, same numbers), air-heat on thermometer; L2 ... | B | framework mechanic (map level); carries over unchanged |
| DIRECT_SUN_SELFTEST_BUILD_EVERY_BIOME_EQUAL | proposed/blocked | Direct Sun offline selftest: same elevation gives same offset and shade in every biome; lint no per-biome h... | B | framework mechanic (map level); carries over unchanged |
| DIRECT_SUN_SETTINGS_WIRE_FEWER_KNOBS | proposed/blocked | Direct Sun Mod Settings rows: master, strength, zenith C (55), weather dims sun, day/night-world mode; dele... | B | framework mechanic (map level); carries over unchanged |
| DIRECT_SUN_UNIFY_GEOMETRY_ALONE_DECIDES | proposed/blocked | Direct Sun in code: one geometry model (55 C x sin E), no per-biome heat kind/number, parasols+roofs only, ... | B | framework mechanic (map level); carries over unchanged |
| DIRTY_CODE_REVIEW_STANDING_LOOP_1 | doing | Standing FOUNDRY code-review loop in progress per owner (keep going, bit by bit) - 12 waves in, ~230 ledger... | B | tooling / harness / process; world-independent |
| DIVING_INTERACTION_FIRST_SCRIPT_1 | built | First north-star script: DivingInteraction | B | mod validation script/trial; world-independent |
| DIVING_SETTINGS_CONTRACT_1 | validated | DivingInteraction: Define what each DivingInteraction toggle actually turns off | B | biome/mod content at def or map level; carries into a remade world |
| DONOR_CODE_REPLACE_CAST_1 | proposed | Replace 3 cut donor-code creatures with NEW cast in same biome: CrescendoAnole (TheForge), LuciferBug (Caul... | B | lost donor-code creatures: new cast can follow the remake |
| DONOR_CODE_SHAPE_REBUILD_1 | proposed | Rebuild twitching/scaled-limb render behaviour in our own code: ColossalAerofleet, Mantrap, OcularJelly | B | lost donor render behaviour: restore after |
| DRAGONSNAKE_PAIR_BUILD_ONE_PALE_ONE_PROPER | doing | Commission both official dragonsnakes in SWBestiary: canon RSW_Dragonsnake to the Jedi: Fallen Order spec, ... | B | biome/mod content at def or map level; carries into a remade world |
| DRAWN_EXTENT_UNIFY_ONE_RULER_TWO_MODS | proposed | Move Huge Things drawn-quad kernel to _Shared/DrawnExtent, source-linked into Huge Things and Sun & Shade; ... | B | framework mechanic (map level); carries over unchanged |
| DROIDWORKS_FACE_RENDER_DEFAULT_HUMAN_1 | built | Droidworks races (G2 included) show a default human face despite RSW_DW_HeadType_Blank — AlienRace head-ren... | B | biome/mod content at def or map level; carries into a remade world |
| DROIDWORKS_WIPE_SEVERITY_1 | validated | Memory wipe: 7-day severe relearning debuff, service-record reset, permanent accreting hardware quirks | B | biome/mod content at def or map level; carries into a remade world |
| DUNE_MOVED_EVENT_1 | validated | SS-5: MovingDunes announces "this sand actually moved"; singing dunes and the quake warning listen to it in... | B | biome/mod content at def or map level; carries into a remade world |
| DUNE_TRACK_ERASE_ACCUMULATE_1 | built | Stillsand: Dune track erasure misses gradual sand movement | B | biome/mod content at def or map level; carries into a remade world |
| DUNGEON_SETPIECE_TEXT_1 | doing | Dungeon set-piece prose held for the owner: Assailant reveal letters + 6 Forsaken vault hand-finish text pe... | B | biome/mod content at def or map level; carries into a remade world |
| DUNG_HATCH_WILDLIFE_CAP_1 | built | CB-4: dung-hatched young respect the map wildlife limit | B | biome/mod content at def or map level; carries into a remade world |
| DUST_DEVIL_ITEM_LOSS_FIX_1 | built | SS-4: dust devil finds landing spot before lifting an item | B | code fix at map/def level; carries over unchanged |
| DUST_SETTLED_LETTER_1 | built | SS-3: horizon-warning group that never arrives gets a 'the dust settled' letter; plume lasts until real arr... | B | biome/mod content at def or map level; carries into a remade world |
| ECONOMY_TRADE_SWEEP_1 | proposed/blocked | Full economic sweep of what is sold where and when, scheduled at the END of the world sweeps; includes Deep... | B | biome/mod content at def or map level; carries into a remade world |
| ECOSYSTEM_PYRAMID_LAW_1 | proposed | Food-pyramid law: small critters outnumber large in every biome roster | B | biome/mod content at def or map level; carries into a remade world |
| EFFECTIVE_DEF_LINT_WIDEN_PAST_DURASTEEL | built | effective_def_lint.py: costlist_resolve_check generalised to a cached patched-tree lint (cost/recipe/stuff ... | B | tooling / harness / process; world-independent |
| EGROWTH_BURST_FIX_NEVERDOWNS_AVERAGES | proposed | ExplosiveGrowth: never-downs guard checks only summary health (RM_TopResolver.cs:170) | B | code fix at map/def level; carries over unchanged |
| EGROWTH_DISABLE_FIX_BLOATED_PLANTS_STAY | proposed | ExplosiveGrowth: disabling engine never dirties meshes (ExplosiveGrowthMod.cs:355) | B | code fix at map/def level; carries over unchanged |
| EGROWTH_MASTER_FIX_SPARES_THE_BANDS | proposed | ExplosiveGrowth: BandsOn ignores enabled master switch (ExplosiveGrowthMod.cs:45) | B | code fix at map/def level; carries over unchanged |
| EGROWTH_RELOAD_FIX_FREE_CHARGE_PASS | built | ExplosiveGrowth: nextPassTick/lastPassTick not saved, each load adds a pass (MapComponent:70, Kernel:74) | B | code fix at map/def level; carries over unchanged |
| EGROWTH_SAVELOAD_PROVE_DICT_SCRIBE_SHARE | proposed | ExplosiveGrowth: unproven Scribe working-list sharing across dictionaries (MapComponent:360); add save roun... | B | biome/mod content at def or map level; carries into a remade world |
| EGROWTH_SCOPE_FIX_FROZEN_CHARGES_GAMBLE | proposed | ExplosiveGrowth: out-of-scope charges frozen, last-swing still fires (MapComponent:230, Patches:218) | B | code fix at map/def level; carries over unchanged |
| EGROWTH_SUPPRESS_FIX_OFF_STILL_SUPPRESSES | proposed | ExplosiveGrowth: existing suppression honoured with toggle off (MapComponent:141, Kernel:168) | B | code fix at map/def level; carries over unchanged |
| EGROWTH_TELL_FIX_STAGE_RATCHET_STUCK | proposed | ExplosiveGrowth: tell stage only rises (Kernel:297-303) | B | code fix at map/def level; carries over unchanged |
| ELDER_DISCHARGE_STUN_LIVING_1 | built | DivingInteraction: Verify the Elder's EMP discharge stuns living pawns | B | biome/mod content at def or map level; carries into a remade world |
| ELDER_TRADE_TRANSACTIONAL_PAYOUT_1 | built | DivingInteraction: Make the Brine Elder trade commit only after the payout lands | B | biome/mod content at def or map level; carries into a remade world |
| EMPIRE_ESCALATION_LADDER_1 | validated | Empire escalation ladder: evadable probes first, new raid kinds per rung, until you move | B | biome/mod content at def or map level; carries into a remade world |
| ENVHAZARDS_HAZARD_CLOCK_READOUTS_1 | built | EH-4: EnvironmentalHazards: show the hazard clocks (venomvine contact and next scratch, wet-bulb ramp, warm... | B | biome/mod content at def or map level; carries into a remade world |
| ENVHAZARDS_SETTINGS_SCREEN_1 | built | EH-3: EnvironmentalHazards settings screen: sections, search, per-section reset, "applies now / new maps on... | B | biome/mod content at def or map level; carries into a remade world |
| ENVIRONMENTAL_HAZARDS_FIRST_SCRIPT_1 | built | First north-star script: EnvironmentalHazards | B | mod validation script/trial; world-independent |
| ENV_WEATHER_GATE_SCOPE_1 | built | EnvironmentalHazards: Environmental weather mechanic gate leaves ambient effects live | B | biome/mod content at def or map level; carries into a remade world |
| EVENT_TRACE_PROPS_LIBRARY_1 | doing | Design a props library of event traces: blaster marks, burn/scorch marks, floor scrapings, drag trails, imp... | B | biome/mod content at def or map level; carries into a remade world |
| EXCAVATION_WALL_ART_1 | validated | Wall-face art for all four depths, spikes and ladder (Quarry perspective) | B | art for our own defs; unaffected by the remake |
| EXPERIMENT_MANIFEST_BUILD_FREEZE_SIX_CELLS | built | experiment_manifest.py: record/verify frozen inputs per C0-C5 cell; refuse complete on changed inputs or an... | B | tooling / harness / process; world-independent |
| EXPLOSIVE_GROWTH_FIRST_SCRIPT_1 | built | First north-star script: ExplosiveGrowth | B | mod validation script/trial; world-independent |
| EXPLOSIVE_GROWTH_MERGE_COMES_HOME | built | Fold ExplosiveGrowth into Baroque Biomes (mandrake.rm.biomes) as a composed member; native soak only for Ba... | B | biome/mod content at def or map level; carries into a remade world |
| EXPLOSIVE_GROWTH_RETHINK_SERIOUS_CONCERNS | doing | ExplosiveGrowth deep dive: what it is configured to do now, the original design, and where to take it (owne... | B | biome/mod content at def or map level; carries into a remade world |
| EXPLOSIVE_PLANT_GROWTH_1 | ready | World mechanic: water-soaked plants grow VISIBLY on screen; design the terminal moment (what happens at the... | B | biome/mod content at def or map level; carries into a remade world |
| EXPLOSIVE_SCOPE_ROW_PROVE_NEEDS_QUIET_LIST | proposed | ExplosiveGrowth scope_native_only is UNMEASURED on biomes_sprint (campaign layer loaded); prove it on explo... | B | biome/mod content at def or map level; carries into a remade world |
| EXTRA_ART_PER_BIOME_COMMISSION_1 | proposed/blocked | Once a biome's group sizes and herd/pack/domestic lore are settled, commission its gender art (every herd a... | B | art for our own defs; unaffected by the remake |
| FACINGS_REDRAW_NORTHS_ABOUT_FACE | proposed | Regenerate the wrong north/east facings (Dragonsnake A-D + swim, Varactyl_m, Strill, OpeeSeaKiller, Yobshri... | B | art for our own defs; unaffected by the remake |
| FALLEN_WIRE_SHOCK_1 | validated | GS-2+X-7 (card ruled): live fallen wire knocks out and throws back a little, lethal only with weak-heart/he... | B | biome/mod content at def or map level; carries into a remade world |
| FALLZONE_LOST_CARGO_QUESTS_1 | proposed | Injected wreckage in the fall zone leads to quests about lost cargo of interest | B | content/design at map or def level; survives the remake |
| FALL_DAMAGE_BUILD_DEEP_DROPS_KILL | validated | Deep falls can kill (owner V3 card 2026-10-18): a death chance by metres fallen on top of the metre-scaled ... | B | framework mechanic (map level); carries over unchanged |
| FALL_GUARDRAILS_BUILD_REAL_OBJECT | validated | Deep falls can kill (V3 lethal); guardrail building as a real object, existing fences act as rails | B | framework mechanic (map level); carries over unchanged |
| FALL_LINE_FERAL_SURVIVOR_PAWNKIND_1 | validated/blocked | Feral-race crash-survivor pawnkind + permanent mental-scar hediff + capture-to-slave wiring | B | framework mechanic (map level); carries over unchanged |
| FASCINATING_WORLD_JUNK_1 | doing | Reskin and re-text every map-scatter wreck (tanks, trucks, cars, ancient junk) into Star Wars scavenger wre... | B | biome/mod content at def or map level; carries into a remade world |
| FAUNA_LORE_DIVERSIFICATION_1 | proposed/blocked | Per-beast damage diversification round AFTER size scaling: judge each beast by its art + description (scary... | B | biome/mod content at def or map level; carries into a remade world |
| FAUNA_TOLERANCE_NORMALIZATION_1 | doing/blocked | Return to canonical-graph fauna normalization, now biome-aware: wide temperature tolerances covering each a... | B | biome/mod content at def or map level; carries into a remade world |
| FEVERWOOD_ANT_HIVE_DUNGEON_1 | doing | Ant hives are reactive procedural dungeons | B | biome/mod content at def or map level; carries into a remade world |
| FEVERWOOD_BOUGH_SOIL_TERRAIN_1 | validated | The crown cannot grow anything: boughway is fertility 0, so bough-soil is owed | B | biome/mod content at def or map level; carries into a remade world |
| FEVERWOOD_BROOD_RANSOM_1 | validated | Fever Wood giant story: ransom of its young (world tally, release gift, young cask trade, Sporefall tank) | B | biome/mod content at def or map level; carries into a remade world |
| FEVERWOOD_HIVE_GUARD_CHAMBER_1 | proposed | Ant hive kept guard at the chokepoints: invent the guard creature, station it where corridors narrow (build... | B | biome/mod content at def or map level; carries into a remade world |
| FEVERWOOD_LIMB_LINGER_CAP_1 | validated | FV-1: tentacle limbs sink back after a linger time and a per-map cap; settings for both | B | biome/mod content at def or map level; carries into a remade world |
| FEVERWOOD_RM_CAST_COMPLETION_1 | validated | Fever Wood: build the seven ratified creatures; the skreth brood as the free second front of the lure | B | biome/mod content at def or map level; carries into a remade world |
| FEVERWOOD_TWO_FRONT_LURE_TUNING_1 | doing | Two-front lure numbers, prey-quality gate, and a free-tier second raider | B | biome/mod content at def or map level; carries into a remade world |
| FEVERWOOD_WATER_TOPOLOGY_SERVICE_1 | built | FeverWood: One registered-water topology (clusters, reachable shore) for FeverWood consumers | B | biome/mod content at def or map level; carries into a remade world |
| FEVER_WOOD_FIRST_SCRIPT_1 | built | First north-star script: FeverWood | B | mod validation script/trial; world-independent |
| FINDMOD_ROT_SPORE_KIT_GUARD_1 | proposed | RotDecayHarvest_LivingProduce.xml guards on FindMod 'RimUtinni: Rot Spore Kit', which matches no mod (inert... | B | biome/mod content at def or map level; carries into a remade world |
| FIREFOAM_DIAGNOSE_CANNOT_AIM_AT_FIRE | proposed | Firefoam sprayer Verb_Shoot has no targetParams: can a drafted colonist aim at a free fire or open ground? | B | biome/mod content at def or map level; carries into a remade world |
| FIRE_CLOCK_FIX_RAIDS_IGNORE_THE_SWITCH | built | fireClockEnabled tooltip says fire raid/flame harvest/rite never fire when off; only the fire front reads it | B | code fix at map/def level; carries over unchanged |
| FIRE_RITE_FIX_DEFENDERS_MISS_THE_WAR | built | LordJob_RUT_FireRite: hostility/arrival transitions skip the Travel subgraph's defend toil, missed signal n... | B | code fix at map/def level; carries over unchanged |
| FIRE_SCAN_DIAGNOSE_BIG_BURN_COST | proposed | Big-burn perf: per-fire fruit-spot closure+9 probes each interval, burrowers scan all fires every tick | B | biome/mod content at def or map level; carries into a remade world |
| FISH_BESTIARY_BUILD_1 | doing/blocked | Build the fish bestiary: 32 RUT_ species across 8 registers on 7 waters, per-biome mod homes, all 8 §6 ques... | B | biome/mod content at def or map level; carries into a remade world |
| FISH_ROLL_MEND_PONDS_BORN_BARREN | built | Plan P13: the vanilla water-body traps (engine doc §2.3): re-roll fish when a body grows past 75/100/200 sq... | B | biome/mod content at def or map level; carries into a remade world |
| FLAME_STATUES_MOD_BUILD_1 | built | Statue spec steps 4-7: mandrake.rm.flamestatues (three Chemfuel flame statues, RM_CompFlamePoints, art wave... | B | biome/mod content at def or map level; carries into a remade world |
| FLOOD_SOAK_MARKERS_BUILD_AIMED_AT_CANALS | doing | Dev map controls (Baroque Biomes): flood trigger aimed at a canal (fixes FW review station 11) and soak zon... | B | biome/mod content at def or map level; carries into a remade world |
| FLOOD_STATION_REWIRE_DRY_CANAL_STAYS_DRY | proposed | FW review station 11: forced canyon flood is torn down next tick on a non-canyon map (Active false: feature... | B | biome/mod content at def or map level; carries into a remade world |
| FLOOD_WITNESS_EVENT_1 | doing/blocked | Plot event: the player witnesses a Cracked Lands flood (chimes, wall of water, explosive growth) at least o... | B | biome/mod content at def or map level; carries into a remade world |
| FLORA_LEGIBILITY_BAR_1 | doing/blocked | Flora legibility bar: own grading pass + model (no keyline law), sizeBin-scaled canvases, no stroke — carri... | B | biome/mod content at def or map level; carries into a remade world |
| FLOWWORKS_BARS_JUDGE_FIVE_IN_ONE_SITTING | proposed | Owner re-validates the FlowWorks north-star section in one sitting: the new bar still_water_one_surface_hei... | B | framework mechanic (map level); carries over unchanged |
| FLOWWORKS_CHECKOUT_SCOPE_1 | built | FlowWorks: ordinary features only in the on-request extension proof; walk lines lack coverage arrows | B | framework mechanic (map level); carries over unchanged |
| FLOWWORKS_CONTAINER_MATERIALS_1 | validated | Bottles and barrels are made from a material the player picks (stuffable + per-material recipes at matching... | B | framework mechanic (map level); carries over unchanged |
| FLOWWORKS_CONVERTER_FIX_BLOCKED_STARVES_REST | built | FlowWorks: first blocked recipe truncates shared budget (CompLiquidConverter.cs:~265) | B | code fix at map/def level; carries over unchanged |
| FLOWWORKS_DEPTH_REBUILD_ONE_BIG_DIG | proposed | One big FlowWorks depth rebuild: exactly-level water (decilitres, one surface per body), metres/litres rewi... | B | framework mechanic (map level); carries over unchanged |
| FLOWWORKS_LADDER_RAISE_LOWER_1 | validated | Pit ladder has two player-toggled states (raised/lowered); entering a pit from the top descends a lowered l... | B | framework mechanic (map level); carries over unchanged |
| FLOWWORKS_NORTHSTAR_GREEN_FULL_1 | built | FlowWorks north star GREEN on the full mod list | B | mod validation script/trial; world-independent |
| FLOWWORKS_NORTHSTAR_GREEN_MINIMAL_1 | proposed | FlowWorks north star GREEN on the minimal tier | B | mod validation script/trial; world-independent |
| FLOWWORKS_NORTHSTAR_SHIP_1 | proposed | FlowWorks SHIPPED: settings superb, art complete, code review CLEAN, deployed | B | mod validation script/trial; world-independent |
| FLOWWORKS_NORTHSTAR_TRIAL_1 | built | FlowWorks north-star trial: VALIDATED -> WIRED -> GREEN-minimal -> GREEN-full -> SHIPPED | B | mod validation script/trial; world-independent |
| FLOWWORKS_PITCOVER_FIX_BURNS_PAWN_UNHARMED | proposed | FlowWorks: destroyed pit cover gives occupants no fall (Building_PitCover.cs:161) | B | code fix at map/def level; carries over unchanged |
| FLOWWORKS_PITFALL_FIX_HISTORY_NOT_SAVED | proposed | FlowWorks: lastCell not scribed, last-tick fall lost across save (RM_SuperdeepTrap.cs:512,606) | B | code fix at map/def level; carries over unchanged |
| FLOWWORKS_PLAYTEST_CAMPAIGN_1 | proposed | FlowWorks bugs via new test methods + rich-screenshot art pre-review; method-per-bug-class data | B | framework mechanic (map level); carries over unchanged |
| FLOWWORKS_QUARRY_DIGGING_1 | validated | Design pass: extend FlowWorks with the quarry concept - digging a canal can uncover local materials (local ... | B | framework mechanic (map level); carries over unchanged |
| FLOWWORKS_REACTOR_FIX_STUCK_ENDS_SHIFT | built | FlowWorks: return where continue intended, later reactions never run (RM_LiquidReaction.cs:187-191) | B | code fix at map/def level; carries over unchanged |
| FLOWWORKS_REVIEW_LOOKS_ROUND_1 | proposed | FlowWorks review-map round 2026-10-06: scorch marks, stone/dirt tar dark grey opaque, depth-only water labe... | B | framework mechanic (map level); carries over unchanged |
| FLOWWORKS_RIVERCOLOR_FIX_DICT_SELF_ENUM | built | FlowWorks: path compression writes parent[] while enumerating parent.Keys (RM_RiverColors.cs:160) | B | code fix at map/def level; carries over unchanged |
| FLOWWORKS_V2_DIAGNOSE_THREE_NEW_REDS | proposed | validation_v2 regressed 61/0/0 -> 58/3/0 on ccf36a9af7 (S3 W4, P3f, P4f) | B | framework mechanic (map level); carries over unchanged |
| FLOWWORKS_VISUAL_PRINCIPLES_1 | validated | FlowWorks look: owner's five visual rules (deep cuts as walls, dirt/stone faces, moving water, tar as liqui... | B | framework mechanic (map level); carries over unchanged |
| FLOW_CONTROLS_BUILD_EIGHT_QUIET_PEBBLES | doing | Dev map controls (FlowWorks): flow meter, level holder, timer switch, map-edge setter, current painter, liq... | B | framework mechanic (map level); carries over unchanged |
| FLOW_ORDER_EXTERNAL_INPUT_1 | built | FlowWorks: Flow order for sourceless (pump/drill/rain-fed) channels and >6000-cell networks | B | framework mechanic (map level); carries over unchanged |
| FLOW_SOURCE_SINK_BUILD_TAPS_FOR_MAPMAKERS | doing | FlowWorks dev-placed Source and Sink objects (any liquid, set rate; minimal look; not buildable) for map ma... | B | framework mechanic (map level); carries over unchanged |
| FLUID_PALETTE_EXHAUSTION_MEND_KEY_ZERO | validated | FlowWorks P7 (GPT G3.6): an exhausted fluid palette returns key 0, so a cell's fluid identity silently chan... | B | code fix at map/def level; carries over unchanged |
| FLYER_STABLE_BODY_GATE_1 | proposed | Flyer-ready static gate + stable-body flip-book regeneration for every flyer | B | biome/mod content at def or map level; carries into a remade world |
| FLYER_VARIANTS_INSTALL_MORE_FACES_PLEASE | proposed | Install the owner's variant picks as alternate graphics: Fleet Flier B/C/D (alien sheet; his note 'Use B, C... | B | biome/mod content at def or map level; carries into a remade world |
| FOCUS_HEAL_TAME_HANDS_OFF_HIS_WINDOWS | built | focus_heal/game_focus never steal or minimise the foreground unless an explicit opt-in flag is set; Run-in-... | B | tooling / harness / process; world-independent |
| FOOTPRINT_TRACK_GRID_1 | validated | One footprint grid for the planet: capped TrackGrid + section layer + cell-entry postfix in CreatureBehavio... | B | biome/mod content at def or map level; carries into a remade world |
| FORCE_DISTURBANCE_REFLAVOR_1 | validated | Reflavor vanilla psychic assault/drone storm events as disturbances in the Force at the RimStarWars tier | B | biome/mod content at def or map level; carries into a remade world |
| FORGE_CYCLE_MECHANICS_1 | doing/blocked | Build the Forge fire-and-water grand cycle: gas-wash ignition, boiling rain + FlowWorks flooding, steam plu... | B | biome/mod content at def or map level; carries into a remade world |
| FORGE_DHOKKUR_WAYS_1 | validated | Dhokkur ways: outcrop disguise clues, rain-wake groan, path memory on glass-polished tracks, walls shoved n... | B | biome/mod content at def or map level; carries into a remade world |
| FORGE_DHUVVOX_SWARM_REMAINDER_1 | doing | Dhuvvox clock remainder: nodules as Things vs sealed pawns, swarm aggregation, slowing sound | B | biome/mod content at def or map level; carries into a remade world |
| FORGE_ENRICHMENT_QUICKTEST_1 | validated | Quicktest-prove the Forge enrichment tranche on a Forge map: keel brace fuel saving, spunstone reveal, phas... | B | biome/mod content at def or map level; carries into a remade world |
| FORGE_KEELWORK_REMAINDER_1 | built | Floatstone keelwork remainder: glassy ring at launch, brace art, and whether payload means substructure sup... | B | biome/mod content at def or map level; carries into a remade world |
| FORGE_MECHANICS_1 | built | Forge C# kit: boiling-rain weather (scald, flash cycle, flash-interval growth), beldon herds + tibanna harv... | B | biome/mod content at def or map level; carries into a remade world |
| FORGE_SKY_PASTURES_1 | doing | Sky pastures: render the vapour-column grid, ash spirals, column-aware hunting and jossur stoops, flier-sel... | B | biome/mod content at def or map level; carries into a remade world |
| FORGE_SPUNSTONE_SOURCES_1 | validated | Spunstone bonding remainder: foundry salvage as a study source, and what the high-speed doors and advanced ... | B | biome/mod content at def or map level; carries into a remade world |
| FORGE_WHITE_PLUME_FRONTS_1 | validated | White plume fronts: moving quench-steam fronts that obscure shooters, soak ground, raise vanilla heatstroke... | B | biome/mod content at def or map level; carries into a remade world |
| FOUL_POOL_SUPPRESSION_SCOPE_1 | built | FeverWood: Decide what radioactive fouling actually suppresses | B | biome/mod content at def or map level; carries into a remade world |
| FULL_LIST_MEMORY_AUDIT_THIRTY_GB_PRIVATE | proposed | 550-list game holds 30.6 GB private / 18.3 GB working set with only ~5 GB managed heap: attribute the ~25 G... | B | tooling / harness / process; world-independent |
| FULL_LOAD_RESIDUE_TRIAGE_1 | built | Full-list load residue beyond the FlowWorks water fix: RSW patch failures, RSW_*Juv config errors, TYR Scri... | B | tooling / harness / process; world-independent |
| FUNGAL_SOIL_TRADE_FIRST_SCRIPT_1 | built | First north-star script: FungalSoilTrade | B | mod validation script/trial; world-independent |
| FURNACE_HERD_DIAGNOSE_ARRIVES_NEVER_LEAVES | proposed | World furnace herd delivered onto a persistent map never rejoins the circuit: herds dwindle over a long game? | B | biome/mod content at def or map level; carries into a remade world |
| GAMECOMP_STALL_HUNT_SEVEN_SECONDS | proposed | Name the GameComponent behind one-off stalls on the 550 list (Rot save): gameComp 6.76 s at tg 7501 and 2.8... | B | tooling / harness / process; world-independent |
| GAME_OBSERVER_BUILD_OUTSIDE_LOOKING_IN | doing | Persistent Windows-side health observer (python.exe, stdlib/ctypes): process identity pid+creation, process... | B | tooling / harness / process; world-independent |
| GARDEN_ESCALATION_PROGRESS_FIX_1 | built | DivingInteraction: Garden defense: tier-1 resets tier-2 progress; Tarnn wake repeats | B | code fix at map/def level; carries over unchanged |
| GC_EARLYLOAD_DUMPS_PROBE_SHOW_VALUE_FIRST | proposed/blocked | Conditional spikes, each kept unbuilt-by-default until it shows useful evidence on a known case: GC timing ... | B | tooling / harness / process; world-independent |
| GELATINOUSSLIME_JOINING_WATER_RITE_1 | proposed | The Joining Water rite: join hands holding slime, one person's permanent hediffs spread weak over several (... | B | content/design at map or def level; survives the remake |
| GELATINOUSSLIME_KIT_ART_1 | doing | Slime: real art for the whole free kit, replacing the vanilla tortoise/grass/bush/dandelion stand-ins | B | art for our own defs; unaffected by the remake |
| GELATINOUSSLIME_PIT_SOLVENT_1 | built/blocked | Slime pit as a solvent: renders toxic or indigestible food safe (Rot's finest in the campaign) | B | biome/mod content at def or map level; carries into a remade world |
| GELATINOUSSLIME_TITAN_CHUNK_BOMB_1 | validated | Slime giant: a chunk of the titanoslime is a terrible thrown bioweapon | B | biome/mod content at def or map level; carries into a remade world |
| GELATINOUSSLIME_VAULT_SEAL_BREACH_1 | built | A titanoslime chunk opens a Forsaken vault blocked by an Assailant seal (seal does not exist yet; owner to ... | B | biome/mod content at def or map level; carries into a remade world |
| GELATINOUS_SLIME_FIRST_SCRIPT_1 | built | First north-star script: GelatinousSlime | B | mod validation script/trial; world-independent |
| GIANT_MUSHROOM_DRAW_FIX_SOUTH_GOES_FRONT | doing | Tall plants (giant mushrooms on the FW review map) overlap wrongly: a more-southern plant must draw in fron... | B | code fix at map/def level; carries over unchanged |
| GIT_WORKFLOW_MIGRATION_1 | ready | Git workflow migration: guard D:\ writes, per-seat ext4 clones, generated views out of git, ledger union+de... | B | tooling / harness / process; world-independent |
| GIZKA_STOWAWAY_FIRST_SCRIPT_1 | validated | First north-star script: GizkaStowaway | B | mod validation script/trial; world-independent |
| GIZKA_STOWAWAY_UNMEASURED_ROWS_1 | proposed | GizkaStowaway RED from 10 UNMEASURED rows | B | biome/mod content at def or map level; carries into a remade world |
| GLASS_TO_TRANSPARISTEEL_1 | built | Transparisteel replaces glass: sifted Stillsand fine sand -> RSW_Transparisteel; sun/lens glass fold in; bo... | B | biome/mod content at def or map level; carries into a remade world |
| GLOOMCAST_FOLLOW_RECHECK_1 | proposed | Gloomcast followers: two live sittings disagree (3 of 3 FollowClose vs 1 of 3); settle on one map with Proo... | B | biome/mod content at def or map level; carries into a remade world |
| GLOW_TANK_LIQUID_FEED_1 | validated | LP-2: glow tank drinks salt or boiling water from a FlowWorks pipe network; settings toggle 'tank needs water' | B | biome/mod content at def or map level; carries into a remade world |
| GLOW_TANK_SEED_LIVE_SOW_1 | validated | Live sow check: glow tank consumes seed culture once established (57536f0db) | B | biome/mod content at def or map level; carries into a remade world |
| GM_BLACKBOARD_SHADOW_M4_1 | built | Build M4: Imperial Heat + orbital-detection timer + dark-tile pause as a Python shadow-mode state machine | B | biome/mod content at def or map level; carries into a remade world |
| GRAFFITI_DESIGNATOR_MARK_CHOICE_1 | built | Graffiti F6: designator chooses the mark (float menu + per-cell order), not a random pool pick | B | content/design at map or def level; survives the remake |
| GRAFFITI_IMPERIAL_FIRST_SCRIPT_1 | built | First north-star script: GraffitiImperial | B | mod validation script/trial; world-independent |
| GRAFFITI_NORTHSTAR_BRIDGE_TOOLS_1 | validated | JawaBench tools the Graffiti trial cannot fake: thing_graphic, spawn_variant, running_mods, glow_at, site_s... | B | mod validation script/trial; world-independent |
| GRAFFITI_NORTHSTAR_GREEN_FULL_1 | proposed | Graffiti: GREEN on the owner's FULL list (fresh launch, full-list driver mode) | B | mod validation script/trial; world-independent |
| GRAFFITI_NORTHSTAR_GREEN_MINIMAL_1 | built | Graffiti: GREEN on MINIMAL+graffiti via fast driver, owner sheet review | B | mod validation script/trial; world-independent |
| GRAFFITI_NORTHSTAR_SHIP_1 | proposed | Graffiti: SHIPPED - art complete, settings superb, CLEAN, stamped, deployed | B | mod validation script/trial; world-independent |
| GRAFFITI_NORTHSTAR_TRIAL_1 | built | Graffiti north-star trial: pipeline pilot to first GREEN (parent of WIRED/GREEN_MINIMAL/GREEN_FULL/SHIP) | B | mod validation script/trial; world-independent |
| GRAFFITI_PUNK_ART_REVIEW_1 | proposed | Graffiti: owner looks at the rendered punk set + 27 meme glyphs + sigil frame in game (keeper save), criter... | B | art for our own defs; unaffected by the remake |
| GRAFFITI_SIGIL_FRAMES_ART_1 | built | Graffiti: render the two missing tier-A sigil frames (stencil-box, drip-frame) and give each an IdeoSigil v... | B | art for our own defs; unaffected by the remake |
| GRAFFITI_V1_LIVE_PROOF_1 | proposed | Graffiti v1 live proof: tier-A sigil renders, raid exit tags, going-over, hostile-maker reaction, scrub, de... | B | biome/mod content at def or map level; carries into a remade world |
| GRAVSHIP_ACOUSTIC_SCANNER_1 | validated | Gravship acoustic scanner (owner, 2026-09-30, from the Cracked Lands Belly Sounder): grounded ship fires a ... | B | biome/mod content at def or map level; carries into a remade world |
| GRAVSHIP_LANDING_FIRST_SCRIPT_1 | built | First north-star script: GravshipLanding | B | mod validation script/trial; world-independent |
| GRAVSHIP_PEACEFUL_SETTLEMENT_LANDING_1 | proposed | Prove a gravship can land in a non-hostile settlement (Hutt test site first) without it being treated as an... | B | biome/mod content at def or map level; carries into a remade world |
| GRAVSHIP_WIRES_SURVIVE_LAUNCH_1 | validated | GS-1: overhead wires with both ends aboard stay strung through gravship launch (treat WillReplace as in-tra... | B | biome/mod content at def or map level; carries into a remade world |
| GREATBOLE_ATMOSPHERE_AND_CROSSOVERS_1 | validated | The greatbole's song, thermal sanctuary, pilgrims, and the two opt-in crossovers | B | biome/mod content at def or map level; carries into a remade world |
| GREENTIDE_BASE_PORT_BUILD_1 | validated | Greentide free tier gets Roil, Breaklight, wet-bulb, dry-air blower, root causeways and living greatbole (R... | B | biome/mod content at def or map level; carries into a remade world |
| GREENTIDE_CEDED_ROOM_RITE_1 | proposed | The Ceded Room, for Ozzik: cede a room built outside the ship to the jungle; scales with room quality | B | content/design at map or def level; survives the remake |
| GREENTIDE_HUMMING_GROVE_1 | built | A grove that hums at differing pitches as you walk through it | B | biome/mod content at def or map level; carries into a remade world |
| GREENTIDE_MECHANICS_2 | built | The Greentide C# kit build: wet-bulb condition+gear, dry-air blower, steam devils (Scald damage already shi... | B | biome/mod content at def or map level; carries into a remade world |
| GREENTIDE_RAID_ANT_FIRST_SCRIPT_1 | built | First north-star script: GreentideRaidAnt | B | mod validation script/trial; world-independent |
| GREENTIDE_STELLOCK_LACE_BUILD_1 | validated | Stellock lace: study a self-sealing branch, craft a cartridge that stops all bleeding on a pawn anywhere | B | biome/mod content at def or map level; carries into a remade world |
| GREENTIDE_THURROCK_HERD_BUILD_1 | validated | The thurrock: tree-felling giant herd on the built Shatterer aura (no moult) | B | biome/mod content at def or map level; carries into a remade world |
| GREYSEA_FLOOR_FLORA_ZERO_1 | built | Grey Sea floor grows ZERO flora: plants above the lowest wildOrder need lower-order neighbours and the lowe... | B | biome/mod content at def or map level; carries into a remade world |
| GREYSEA_FLOOR_PASS_1 | doing | Whole individual pass for the Grey Sea floor biome: terrain+features, dive experience, ruled cast wired wit... | B | biome/mod content at def or map level; carries into a remade world |
| GREYSEA_USELESS_ARTIFACT_PLOT_1 | proposed | The Elders' sixth treasure - 'a beautifully useless artifact whose significance only becomes apparent much ... | B | art for our own defs; unaffected by the remake |
| GREY_LAMP_ANSWER_RETRY_1 | built | TerminalBiomes: Grey lamp giant response latches on dispatch, not on completion | B | biome/mod content at def or map level; carries into a remade world |
| GREY_TWILIGHT_SEABED_BIOME_GATE_1 | validated | TerminalBiomes sea gates key on the surface sea biome and never fire on a RM_SeabedLayer floor map | B | biome/mod content at def or map level; carries into a remade world |
| GSS_CORD_SILENCE_PHANTOM_SPARK | doing | GSS draws a second, dangling sparking cord at a pump fed by an adjacent conduit (vanilla adjacency): only t... | B | framework mechanic (map level); carries over unchanged |
| GSS_HOOKUP_CABLE_PROBE_HIDDEN_CONDUIT | proposed | GSS render checks: hookup to HiddenConduit/excluded conduit may print a visible cable (B13); shader-sway st... | B | framework mechanic (map level); carries over unchanged |
| GSS_STYLE_RUN_PROVE_MIXED_LOOKS_SUSPECTED | proposed | GSS one-run-one-style: suspected mixed looks after a default change on legacy members (D1), batched links j... | B | framework mechanic (map level); carries over unchanged |
| GSS_TOGGLES_FIX_OFF_MEANS_OFF | proposed | GSS: settings that do not switch their patches off (run queueing, anchor looks, power scope, tap debit) — m... | B | code fix at map/def level; carries over unchanged |
| GUARDRAIL_ART_RESKIN_BORROWED_FENCE | proposed | RM_PitGuardrail ships with vanilla fence art; a bespoke guardrail look needs the owner's permission (cosmet... | B | art for our own defs; unaffected by the remake |
| HAZARD_CLOCK_INSPECT_LINES_1 | validated | TB-4: Inspect lines for Grey lamp burn time, twilight well phase, grav engine crust count | B | biome/mod content at def or map level; carries into a remade world |
| HAZARD_TAR_TERRAIN_FROM_LIQUIDS_1 | built | EH-5: hazard code reads tar terrains from FlowWorks liquid defs, not literals | B | biome/mod content at def or map level; carries into a remade world |
| HEALTH_BANDS_WIRE_QUEUED_BEHIND_OVERHEAD | proposed/blocked | Minimal in-game health extension to the TPS record: frame-interval histogram from existing Root.Update time... | B | tooling / harness / process; world-independent |
| HEALTH_CHECK_MONITOR_MEMORY_TPS_OVER_TIME | proposed | C24 standing health check: memory (private, managed, native/GPU) and TPS as a function of time beside load-... | B | tooling / harness / process; world-independent |
| HEALTH_METRICS_JUDGE_EARN_THEIR_KEEP | proposed | Post-hoc review: evaluate each game-health metric's worth and measured cost from the metrics ledger in game... | B | tooling / harness / process; world-independent |
| HEALTH_METRICS_PROVE_EIGHT_WRITTEN_UNTESTED | proposed | Deploy and measure the eight written-not-deployed health metrics (b59c43446) after the TPS overhead test (B... | B | tooling / harness / process; world-independent |
| HEAT_BUDGET_PREFIX_MEND_LATE_CELLS_STARVE | validated | FlowWorks P9a (GPT G3.8): the liquid heat budget is spent from the start of the list every interval, starvi... | B | code fix at map/def level; carries over unchanged |
| HEAVY_TEXTURES_MEASURE_REAL_VRAM | proposed | Measure real memory of Planet Atmosphere, EGI Holograms, Minerals Rock shapes and Glowing Bush in a live se... | B | tooling / harness / process; world-independent |
| HEDIFF_GLOW_MOVING_PROXY_1 | built | LuminousPigment: Cuisine hediff lights should ride the worn moving-proxy machinery | B | framework mechanic (map level); carries over unchanged |
| HEDIFF_GLOW_TARGETING_PULSE_1 | built | LuminousPigment: Wire or remove inert hediff glow targeting/pulse fields | B | framework mechanic (map level); carries over unchanged |
| HELIX_TELLUROX_BUILD_1 | doing/blocked | Build Tellurox, Ascendant Helix labour-line livestock | B | biome/mod content at def or map level; carries into a remade world |
| HORIZON_CARAVAN_VANILLA_REFUSES_1 | proposed | Stillsand horizon_warns_then_arrives: vanilla TraderCaravanArrival also refused on the L2 site. Repro: rege... | B | biome/mod content at def or map level; carries into a remade world |
| HORIZON_WARNING_DROP_RAIDS_1 | built | Stillsand: Horizon warning turns centre/drop raids into edge drops | B | biome/mod content at def or map level; carries into a remade world |
| HOSE_JOINTS_REDESIGN_PUMP_TOO_PUNY | doing | Liquid connection visuals: pump heftier than the hose, hose diameter a bit thinner, visible connectors wher... | B | content/design at map or def level; survives the remake |
| HOSE_LAY_POLISH_CENTRE_VS_MOUTH | proposed | FlowWorks: hose lay edge cases (centre vs mouth range, refused feeder, bend radius) | B | framework mechanic (map level); carries over unchanged |
| HOSE_PATHING_REPAIR_SCENIC_ROUTE_PLEASE | proposed | Hose routing should prefer bare ground around a hose reel over passing through it (water-scene S3: pond los... | B | framework mechanic (map level); carries over unchanged |
| HOSE_PIPE_WALK_JUDGE_GIRTH_IN_GAME | proposed | Live walk: hoses vs solid pipes side by side at pumps, tanks, taps, sprinklers — are the diameters sensible... | B | framework mechanic (map level); carries over unchanged |
| HOSE_REALFLOW_DIAGNOSE_SHORT_POUR_DRY_TANK | built | proof_hose realflow: pump cycle moves 0.86-0.89 level, tank->hose moves 0 (live 2026-10-19) | B | framework mechanic (map level); carries over unchanged |
| HOSE_RULINGS_BUILD_THREE_REVERSALS_ONE_CARD | validated | FlowWorks: enact the 2026-10-11 hose-port reversals - rigid universal pipe with wire-style art picker (#1, ... | B | framework mechanic (map level); carries over unchanged |
| HOSTILE_FLORA_FIRST_SCRIPT_1 | built | First north-star script: HostileFlora | B | mod validation script/trial; world-independent |
| HOSTILE_MOBILE_PLANTS_1 | doing/blocked | Hostile mobile plants as animals - a new creature class | B | biome/mod content at def or map level; carries into a remade world |
| HUGETHINGS_SETTINGS_HARDENING_1 | built | Huge Things settings: validate every numeric on load, honest labels, translation keys (B3.19/C3.6/D3.3, A2.... | B | framework mechanic (map level); carries over unchanged |
| HUGETHINGS_TRUNK_ZERO_BLOCKERS_1 | proposed | HugeThings trunk.full_grown_giant_gets_its_measured_footprint FAIL live 2026-10-08 (Transient/modcheck/Huge... | B | framework mechanic (map level); carries over unchanged |
| HUTT_SLAVE_PIT_TEST_SITE_1 | built | Hutt slave pit at a small stand-alone test site: sell slaves, prisoners and downed beasts for silver; seale... | B | biome/mod content at def or map level; carries into a remade world |
| ICON_OUTLINE_REPAINT_1 | proposed | Repaint remaining ~141 outlined item icons painted/no-outline; review the 24 queued renders; install on own... | B | art for our own defs; unaffected by the remake |
| INDIGENOUS_TECH_REVISIT_1 | proposed | Indigenous-tech revisit per biome, GATED to after the last biome detailing (owner 2026-09-24): which specif... | B | biome/mod content at def or map level; carries into a remade world |
| INHABITED_AUGMENTATION_BUILD_1 | doing | Build the tile-augmentation content: rimplace templates + Inhabited wiring for the biome/faction/latitude a... | B | biome/mod content at def or map level; carries into a remade world |
| INSITU_ART_JUDGE_SAVES_KEPT_WARM | proposed | Joint in-game walk on staged keeper saves: sprinkler heads (4 looks), thin-water pond, joined weirs (4 look... | B | art for our own defs; unaffected by the remake |
| JAWABENCH_DESTROY_PAWNS_1 | proposed | jawa/destroy_batch never removes pawns even with categories=Pawn ('1 pawn(s) left alone'), so Greentide _cl... | B | tooling / harness / process; world-independent |
| JAWA_SWIM_HOOD_KEEP_1 | validated | URGENT (owner, chat 2026-09-25: Jawa must never be seen without a hood): swimming Jawa lose their hood beca... | B | biome/mod content at def or map level; carries into a remade world |
| JOSSUR_FLIGHT_FRAMES_1 | doing/blocked | Flight flip-book frames for RM_Jossur (optional; flight stat already set) | B | art for our own defs; unaffected by the remake |
| KEEPER_SAVES_HARDEN_WRONG_SLOT_WRITES | built | save-guard wrapper: hash-backup Saves keepers before any save-capable run, refuse current-slot overwrite, p... | B | tooling / harness / process; world-independent |
| KHORRAK_STEEL_DIET_TIER_1 | built | RSW_Khorrak kept uncast as sole carrier of C# CompMetalEater after the Khorrak RM tier move: port the steel... | B | lost mechanic carrier: restore after |
| KINETIC_BLAST_WEAPONS_1 | validated | Design + commission a range of projectile kinetic-blast weapons; thump cannons throw farther | B | biome/mod content at def or map level; carries into a remade world |
| KURRETH_LOSS_FINALIZE_1 | built | FeverWood: Kurreth column: explicit recovery/loss state per victim | B | biome/mod content at def or map level; carries into a remade world |
| KURRETH_THEFT_PER_COLUMN_1 | built | FeverWood: Theft letters/quests grouped by column, not time window | B | biome/mod content at def or map level; carries into a remade world |
| KYBER_TRADE_PLOT_1 | doing/blocked | Selling kyber: Empire heat rises per sale, Hutt interest rises, alleged Jedi from the Moisture Farmers, the... | B | content/design at map or def level; survives the remake |
| KYBER_TRADE_PLOT_FIRST_SCRIPT_1 | built | First north-star script: KyberTradePlot | B | mod validation script/trial; world-independent |
| LACQUER_PRESS_REWIRE_BILL_PLUS_RIGHT_CLICK | doing | Lacquer worn items via a press bill plus right-click the press, no pawn gizmo | B | biome/mod content at def or map level; carries into a remade world |
| LAKE_FLOORS_BUILD_MOUNTAINS_RUN_DEEP | built | Plan P11: every limited natural lake gets its floor recorded when the map is made (books only, nothing on s... | B | framework mechanic (map level); carries over unchanged |
| LANTERNDEEPS_ANSWERING_RITE_BUILD_1 | validated/blocked | Lantern Deeps: The Answering, Ohm's found settlement rite (campaign) | B | content/design at map or def level; survives the remake |
| LANTERNDEEPS_SHEET_ART_REDO_1 | built | Lantern Deeps art sheet 2026-10-05: eye repaints, blinker redo, plant variants to install on return | B | art for our own defs; unaffected by the remake |
| LARGEPAWNS_BRIDGE_HARDENING_1 | built | Large Pawns bridge: turn its PathClearingUtility wall-break off as ruled, and make reconcile atomic (B3.15,... | B | biome/mod content at def or map level; carries into a remade world |
| LASSO_CHERRYPICKER_REMOVAL_1 | validated | Remove lassos: Cherry Picker cut AM_LassoCloth + Melee Animation lasso spawning off | B | biome/mod content at def or map level; carries into a remade world |
| LASSO_CONFIG_UNSET_1 | proposed | Melee Animation config Mod_2944488802_Core.xml has no LassoSpawnChance element on the live profile; set 0 a... | B | biome/mod content at def or map level; carries into a remade world |
| LAUNCHER_READY_HARDEN_OLD_LOG_LINES_LIE | built | launch_and_wait.sh succeeds only on a current-process readiness receipt (PID+start time, fresh token line a... | B | tooling / harness / process; world-independent |
| LAUNCH_HELD_COLONIST_WARNING_1 | validated | Gravship launch confirmation names any colonist held inside something (brine jacket, Hwelgrue, Titanoslime)... | B | tooling / harness / process; world-independent |
| LAVA_LIQUID_BUILD_PROMISED_BY_CARD | validated | FlowWorks: add the lava liquid the owner promoted by card 2026-09-24 (missing from the liquid registry); se... | B | biome/mod content at def or map level; carries into a remade world |
| LEANINGSCRUB_CROWN_MOB_LIVE_1 | proposed | LeaningScrub crown mob: dustflutters ranged 23-70 cells with mob ON or OFF; CrownMob claims only idle mobbe... | B | biome/mod content at def or map level; carries into a remade world |
| LEANINGSCRUB_ENRICHMENT_QUICKTEST_1 | validated | Quicktest-prove dripping regrow, crown mob, runway bloom, named sweetline trees by state read | B | biome/mod content at def or map level; carries into a remade world |
| LEANINGSCRUB_MECHANICS_BUILD_1 | built/blocked | Build the Leaning Scrub mechanics: Stall+Gale wind calendar, the Lean scent/fire axis, vaporator + V-blight... | B | biome/mod content at def or map level; carries into a remade world |
| LEANINGSCRUB_SHEET_ART_REDO_1 | doing | Leaning Scrub sheet: wiring, variants and design asks | B | art for our own defs; unaffected by the remake |
| LEANINGSCRUB_STALL_SHARED_MOVE_1 | proposed | LeaningScrub stall: both animals (0.4 Thornhold + 0.7 Shirrel control) made the same +12,+12 move in the fi... | B | biome/mod content at def or map level; carries into a remade world |
| LEANINGSCRUB_SWEETLINE_SHED_LIVE_1 | proposed | LeaningScrub sweetline: mature tree shed 0 felt after +5.5 d. Repro: sweetline pad (anchor+45,+45), set_pla... | B | biome/mod content at def or map level; carries into a remade world |
| LEANINGSCRUB_SWEETLINE_VISITORS_1 | validated | Sweetline travellers camp and pilgrims leave tokens: who, mapgen or incident, token def | B | biome/mod content at def or map level; carries into a remade world |
| LEANINGSCRUB_VENOMVINE_SITTING_1 | proposed | Settle all 11 Leaning Scrub venomvine forms (art + patch-growth mechanic) in one in-game BENCH sitting with... | B | biome/mod content at def or map level; carries into a remade world |
| LEANINGSCRUB_VISSLER_ARM_SCAVENGERS_1 | validated | Shed vissler arms draw real scavengers: which species, food or lure job | B | biome/mod content at def or map level; carries into a remade world |
| LEANING_SCRUB_FIRST_SCRIPT_1 | built | First north-star script: LeaningScrub | B | mod validation script/trial; world-independent |
| LEANING_SCRUB_SITE_BUILD_LEANS_ONE_WAY | proposed | LeaningScrub saved site + the Lean rows (heading lock, upwind flee, downwind fire) | B | biome/mod content at def or map level; carries into a remade world |
| LIGHT_LEDGER_ONE_1 | validated | X-3/TB-5: one light ledger; every GlowRadius writer registers a modifier (10 files, 6 mods); fixes SUN_SPHE... | B | framework mechanic (map level); carries over unchanged |
| LIQUID_BOTTLE_LOOP_1 | built/blocked | Bottles as real items: fill/use/dirty/wash loop (dirty behind a toggle, default ON), revert-on-bottle for b... | B | framework mechanic (map level); carries over unchanged |
| LIQUID_CONTAINERS_REDRAW_NO_MANA_POTIONS | doing | Bottles, buckets, barrels: four tech styles each (Junker oddly shaped, Industrial generic water bottle, Mod... | B | art for our own defs; unaffected by the remake |
| LIQUID_INDUSTRY_SETPIECES_1 | validated | Found industrial liquid works via the shared scatterer: desal, detox, tar refinery, pumping station — wreck... | B | framework mechanic (map level); carries over unchanged |
| LIQUID_LEDGER_BUILD_NO_UNIT_LOST | validated | FlowWorks liquid networks L1-L3 (design/RimMandrake/liquid_network_semantics_design_2026-10-11.md §6): one ... | B | framework mechanic (map level); carries over unchanged |
| LIQUID_LOOK_MATERIAL_OWNERSHIP_1 | built | FlowWorks: Liquid looks own their materials | B | framework mechanic (map level); carries over unchanged |
| LIQUID_THIRST_CHAIN_1 | built/blocked | Water cleaning chain crude/household/industrial wired to DBH thirst (DBHThirst MEASURED in frozen dump); gr... | B | framework mechanic (map level); carries over unchanged |
| LIVE_ROUND2_FIXES_PROOF_1 | validated | Prove the three live-round-2 fixes in game (beam, soorrak loop log, rimplace stuff) | B | code fix at map/def level; carries over unchanged |
| LIVINGBOLT_CORPSE_ART_1 | proposed | RM_LivingBolt corpse render (none exists; body graphic stands in) | B | art for our own defs; unaffected by the remake |
| LOAD_RED_BASELINE_DRIFT_1 | proposed | 2026-10-08 19:30 full-list load vs baseline: patch ops failed 6 vs 5 (new: UtinniPatches ops on BMT_GreyLad... | B | tooling / harness / process; world-independent |
| LONGSHADE_BEDAZZLE_CONTENT_1 | built/blocked | Long Shade bedazzle content: wire the finished-but-unwired art (7 magenta creatures + vorrel family), five ... | B | biome/mod content at def or map level; carries into a remade world |
| LONGSHADE_BEDAZZLE_MECHANICS_1 | built/blocked | Long Shade bedazzle mechanics: golden-hour perpetual sunset + pinned sun angle, mirrak false-shadow ambushe... | B | biome/mod content at def or map level; carries into a remade world |
| LONGSHADE_ENRICHMENT_QUICKTEST_1 | built | Quicktest the Long Shade enrichment: gloomcast moving shade, camera heat soundscape, Shipfall Commons, grov... | B | biome/mod content at def or map level; carries into a remade world |
| LONGSHADE_JAWATOW_RECHECK_1 | proposed | Re-check after fix: LONGSHADE_JAWATOW_RECHECK_1 | B | code fix at map/def level; carries over unchanged |
| LONGSHADE_MIDDENS_SPENT_BUILD_1 | validated | Long Shade middens: spent-once heaps, mapgen seeding at rock lee ends, clean-patch tell | B | biome/mod content at def or map level; carries into a remade world |
| LONGSHADE_SCENE_LIVECHECK_1 | proposed | Live check: tollok ticks, lure awning, harrok on one RM_LongShade scene | B | biome/mod content at def or map level; carries into a remade world |
| LONGSHADE_STAMPEDE_LIVECHECK_1 | proposed | Live check: stampede for your roof incident | B | biome/mod content at def or map level; carries into a remade world |
| LONG_SHADE_FIRST_SCRIPT_1 | built | First north-star script: LongShade | B | mod validation script/trial; world-independent |
| LORE_STAGES_FIRST_SCRIPT_1 | built | First north-star script: LoreStages | B | mod validation script/trial; world-independent |
| MACRO_GENERATOR_V0_1 | built/blocked | Macro generator v0: ONE idea per map — chooser + plan + terrain grid, graded on a comparator sheet by the o... | B | biome/mod content at def or map level; carries into a remade world |
| MAP_AWARENESS_PROVE_ON_A_QUIET_MAP | proposed | Deploy the map-awareness companion build (game down) and run the live acceptance tests of GPT review s7 pha... | B | tooling / harness / process; world-independent |
| MAP_LANDFORM_MUTATORS_DESIGN_1 | proposed | MAP_LANDFORM_MUTATORS_DESIGN_1 | B | content/design at map or def level; survives the remake |
| MAP_SILENCE_SINGLE_OWNER_1 | built | FV-3: one owner for the map ambient-sound hush | B | biome/mod content at def or map level; carries into a remade world |
| MASS_VALIDATION_LADDER_1 | doing | Batched validation ladder: get_defs deep-serialize, manifest runner, hot-reload trial, first review environ... | B | tooling / harness / process; world-independent |
| MAT_DISCOVERY_SIGHT_RULE_1 | built | LuminousPigment: Mat discovery: decide who must see it and add a harvest trigger | B | biome/mod content at def or map level; carries into a remade world |
| MESSYCONDUIT_CABLE_PILE_LOOK_1 | built | Cable and hose pile look: power strips always have cables plugged in, cables read as one flowing run except... | B | framework mechanic (map level); carries over unchanged |
| MESSYCONDUIT_REVIEW_ROUND1_1 | built | MessyConduit human review round 1: 10 findings from the owner at the review map (Star Wars style art, stati... | B | framework mechanic (map level); carries over unchanged |
| MESSY_CONDUIT_MOD_1 | built | Messy Conduit (mandrake.rm.messyconduit): conduit sprawls over the floor like real wiring; concept talk wit... | B | framework mechanic (map level); carries over unchanged |
| MIASMA_FIRST_SCRIPT_1 | built | First north-star script: Miasma | B | mod validation script/trial; world-independent |
| MIASMA_MECHANICS_1 | built | Miasma C# kit: surge/salt-line system (fresh-brine map axis, storm-driven movement, stranding pools), fever... | B | biome/mod content at def or map level; carries into a remade world |
| MIASMA_RECALL_WRITTEN_OFF_RITE_1 | proposed | The Recall of the Written-Off rite (Rekko): a struck-out disposal order calls a salvage operation on you | B | content/design at map or def level; survives the remake |
| MIASMA_WARDEN_MOTHER_ART_1 | doing | Warden mother art, with an aged variant for her last season | B | art for our own defs; unaffected by the remake |
| MINDSTONE_MATRIX_KINDLED_BUILD_1 | validated | Mindstone matrix + the Kindled's first making: RUT_Mindstone + head casing at the reassembly harness -> RUT... | B | biome/mod content at def or map level; carries into a remade world |
| MINERALS_WHERE_THEY_BELONG_1 | doing | Design (later): minerals where they belong — per-biome allocation of every mineral, gem and mineable materi... | B | biome/mod content at def or map level; carries into a remade world |
| MIRROR_BEAM_SUN_POLICY_1 | built | Stillsand: Pawn mirror beams ignore cast shade; turret beams don't | B | biome/mod content at def or map level; carries into a remade world |
| MISSION_TANK_GOAL_REWIRE_TO_DEST | built | FlowWorks P14 (GPT G6.5): the machinery player mission's goal accepts ANY filled tank (northstar/player_mis... | B | framework mechanic (map level); carries over unchanged |
| MODCHECK_DONOR_ENVIRONMENTS_1 | doing/blocked | MODCHECK_DONOR_ENVIRONMENTS_1 Armoury and WreckedMachines modcheck environments: compose their donor mods (... | B | tooling / harness / process; world-independent |
| MODCHECK_SETUP_UNMEASURED_FIX_READS_AS_FAIL | proposed | modcheck runner.py ~529-538 records any chain-SETUP ExpectationFailed as FAIL + finding, ignoring an 'UNMEA... | B | tooling / harness / process; world-independent |
| MODCHECK_SUITE_CORRECTIONS_1 | doing | MODCHECK_SUITE_CORRECTIONS_1 first-live-run corrections for the 12 RED + 2 aborted mature-mod suites (evide... | B | tooling / harness / process; world-independent |
| MODCHECK_ULTRAFAST_CLOCK_STALL_1 | proposed | modcheck Ultrafast wait never advances TicksGame (0 successes in 47 result JSONs; LeaningScrub smother + bl... | B | tooling / harness / process; world-independent |
| MOD_HUMAN_EXPLORATION_PASS_1 | proposed/blocked | Human-executable exploration pass: per mod, a scripted in-game walkthrough the owner runs to confirm it loo... | B | biome/mod content at def or map level; carries into a remade world |
| MOD_MANIFEST_BUILD_THREE_LISTS_ONE_TRUTH | built | modmanifest.py check/diff: ordered intended manifest vs next-load ModsConfig vs loaded mods; flags Core-onl... | B | tooling / harness / process; world-independent |
| MOD_VALIDATION_RETROFIT_1 | doing/blocked | modcheck full retrofit wave: every shipped mod gets a validation.steps.yaml and a green run (owner ruling 2... | B | biome/mod content at def or map level; carries into a remade world |
| MOVINGDUNES_WATER_BANKS_SAND_1 | built | MovingDunes: sand hopping onto water banks on the shore (owner card: water banks the sand) | B | biome/mod content at def or map level; carries into a remade world |
| MOVING_DUNES_BUILD_1 | validated/blocked | Build the dunes engine per MOVING_DUNES_DESIGN.md v2 (model=opus, ~1.1-1.4k lines): Werner transport on Ody... | B | biome/mod content at def or map level; carries into a remade world |
| MOVING_DUNES_FIRST_SCRIPT_1 | built | First north-star script: MovingDunes | B | mod validation script/trial; world-independent |
| MYCOID_COLOSSUS_LIVE_LOOK_1 | built | MYCOID_COLOSSUS_LIVE_LOOK_1 | B | biome/mod content at def or map level; carries into a remade world |
| MYNOCK_FLIPBOOK_FRAMES_1 | proposed | RSW_Mynock flies with no wing-beat: its 8-frame flight flip-book is owed art | B | art for our own defs; unaffected by the remake |
| NATURAL_HEAT_CACHE_PROVE_STALE_DAYS | validated | FlowWorks P9b (GPT G3.9, hook unverified): the natural-heat cache trusts terrain for 15,000 ticks after it ... | B | framework mechanic (map level); carries over unchanged |
| NIGHTSIDEICE_SHEET_ART_REDO_1 | built | Nightside Ice sheet: redo art and Tauntaun canon wiring | B | art for our own defs; unaffected by the remake |
| NIGHTSIDE_ICE_NEW_LIFE_1 | proposed | Nightside Ice strange life: sheet sitting on the roster draft, then defs/C# | B | biome/mod content at def or map level; carries into a remade world |
| NINEFOLD_FAVOUR_ODDS_BUILD_1 | validated | Build Nine Faults (fresh-find rite, Rekko to Zizzik), the Left Behind transfer (Ohm to Ta'Baa), the god-fav... | B | biome/mod content at def or map level; carries into a remade world |
| NINEFOLD_LOUDNESS_FRONT_1 | built | Ninefold owes LOUDNESS and THE FRONT, which canon rules exist and no code computes — MEASURED 2026-09-16: G... | B | biome/mod content at def or map level; carries into a remade world |
| NORTHSTAR_ADVERSARIAL_REVIEW_1 | proposed | Standing: periodic adversarial and GPT review of north-star scripts | B | mod validation script/trial; world-independent |
| NORTHSTAR_COMPANION_GAPS_1 | validated | Companion tools: pawn census (mental state+job), incident-queue peek/selective remove, damage-event ring bu... | B | mod validation script/trial; world-independent |
| NORTHSTAR_EVERYWHERE_PROGRAM_1 | proposed | North-star scripts for every mod; new-content pause until done | B | mod validation script/trial; world-independent |
| NORTHSTAR_FAST_DRIVER_1 | proposed | Ultra-fast Python bridge driver for north-star validation (core built, live proof owed) | B | mod validation script/trial; world-independent |
| NORTHSTAR_ISHKO_PILOT_1 | validated | Northstar pilot on IshkoDarkLandmarks: walk arrows, ishko tier, mock clean, record status, first live_sessi... | B | mod validation script/trial; world-independent |
| NORTHSTAR_PARTIAL_GAPS_FILL_1 | proposed | Fill the coverage gaps of the 67 PARTIAL north-star scripts, a mod at a time beside its own build or live r... | B | mod validation script/trial; world-independent |
| NORTHSTAR_PROCESS_RETRO_1 | proposed/blocked | Northstar process retro after GimmeSomeSlack goes Green: what worked, update skills, build Python helpers | B | mod validation script/trial; world-independent |
| NORTHSTAR_SITUATIONAL_ROLLOUT_1 | proposed | Flip modcheck --situational to default after an abort-only pass over every suite | B | mod validation script/trial; world-independent |
| NORTHSTAR_VALIDATION_SKILL_1 | proposed | Carve a northstar-validation skill out of rimworld-debug-testing: bland saved world, situational envelope, ... | B | mod validation script/trial; world-independent |
| NORTH_STAR_ATMOSPHERIC_TBD_1 | proposed | TBD by owner ruling 2026-09-17: how the ship-lighting north star bars get automated waits on live play. Ver... | B | mod validation script/trial; world-independent |
| NORTH_STAR_WALK_AUTHORING_1 | ready | Author must-show sections across the 77 validation walks: agent drafts candidate lines from each walk's mus... | B | mod validation script/trial; world-independent |
| OASIS_MAKER_FIRST_SCRIPT_1 | built | First north-star script: OasisMaker | B | mod validation script/trial; world-independent |
| OLD_ART_SHEETS_REBUILD_WITH_SCALE_PANELS | proposed | Rebuild sheet_conflicts_review_2026-10-09 and sluice_panning_warden_sheet_20261010 with art_sheet.py --subj... | B | tooling / harness / process; world-independent |
| OLLOPOM_BEAUTY_VERIFY_DEPLOYED_NOT_SEEN | proposed | Ollopom perceived-beauty DLL is deployed; run its validation.py perceived_beauty check on the next live ses... | B | biome/mod content at def or map level; carries into a remade world |
| OPTIMISATION_TOOLS_BUILD_BY_NAME_NOT_BLAME | proposed/blocked | Named optimisation tools: own-code counters for our mods' hot paths and an on-demand, expiring profiler ove... | B | tooling / harness / process; world-independent |
| ORDNANCE_TRIGGER_REAL_SHOT_1 | built | Scarlands: "Set off from range" should be a real shot, or be renamed | B | biome/mod content at def or map level; carries into a remade world |
| OWN_PRESET_WIDEN_PYRELANDS_JOINS_IN | proposed | Companion redeploy owed (53595b2d45, built not deployed): health_profile preset own adds GSS (ticks+Updates... | B | biome/mod content at def or map level; carries into a remade world |
| PACK_ANIMALS_RESTORE_EMPTY_SADDLES | proposed | 56 of our 62 BiomeDefs have an empty allowedPackAnimals, so by PawnGroupKindWorker_Trader no land trade car... | B | biome/mod content at def or map level; carries into a remade world |
| PACK_OVERLAYS_BUILD_SHARED_SADDLEBAGS | proposed | Draw 3-4 shared loaded-pack overlays (quadruped, biped, six-legged, larva) for the 54 packAnimal races | B | biome/mod content at def or map level; carries into a remade world |
| PALETREE_UNTANGLE_CASE_TWINS_ONE_SLOT | proposed | TheRot PaleTree: _B.png and _b.png collide on Windows; one variant never deploys (_B duplicates _e, _A dupl... | B | biome/mod content at def or map level; carries into a remade world |
| PAWN_ORIGIN_BUILD_SAY_ORIGIN_UNKNOWN | validated | Map awareness phase 3 (companion C#): pawn origin recorder - context chain (bridge action -> incident -> ge... | B | tooling / harness / process; world-independent |
| PEN_ANIMALS_UNSTICK_STATUES_LEARN_TO_WALK | built | Review-save pen animals: companion tools to end/re-apply their 60000-tick Wait pin (jawa/pen_release, jawa/... | B | tooling / harness / process; world-independent |
| PIGMENT_JOB_PAYMENT_ALLOCATION_1 | built | LuminousPigment: Deepfire jobs: allocate pigment across queued jobs and validate payment | B | biome/mod content at def or map level; carries into a remade world |
| PIPE_ENDS_BUILD_MEET_IN_THE_MIDDLE | built | Draw pipes and hoses as if they run into the CENTRE of every pipe-receiving building, continuing beneath it... | B | framework mechanic (map level); carries over unchanged |
| PIT_ACCESS_BUILD_LADDERS_CLIMBING_JUMPS | validated | Rescue access: wall ladder, carryable ladder, climbing gear, wall scaling, jump/teleport | B | framework mechanic (map level); carries over unchanged |
| PIT_ALERT_BUILD_RED_MEANS_HELP | validated | Standard red alert when one of our colonists is held in a pit and cannot reach food or a bed (owner Q12 car... | B | framework mechanic (map level); carries over unchanged |
| PIT_CLIMB_PROVE_RAIDERS_VS_SHEER_TRENCH | proposed | Plan P2: owed live proofs of the built climb work (pocket grid, cliff masks, ramp, ladder: PIT_POCKET_GRID_... | B | framework mechanic (map level); carries over unchanged |
| PIT_COVER_DIAGNOSE_GIVES_WAY_TOO_SOON | built | Pit cover decks (120/220 kg) give way under one ~60 kg colonist (live 2026-10-19) | B | framework mechanic (map level); carries over unchanged |
| PIT_LADDER_REDRAW_HUNG_ON_THE_WALL | doing | Pit ladder mounts on a pit wall like a door (placed on the edge, faces into the pit), with a slid-up state ... | B | art for our own defs; unaffected by the remake |
| PIT_LIP_FIX_BOAR_HANGS_OUT | built | Pit near-lip occlusion: a pawn lying (asleep/downed) in a pit's southern cell draws over the south lip inst... | B | code fix at map/def level; carries over unchanged |
| PIT_LIP_OCCLUDES_OUTSIDE_1 | built | Pit-lip occlusion quad paints ground over a pawn standing OUTSIDE the pit (Muffalo south of pit, owner-spot... | B | framework mechanic (map level); carries over unchanged |
| PIT_POCKET_GRID_BUILD_SLOPES_NEVER_TRAP | superseded | Relative climbing core: climb-limit bands, StepAllowed math + selftests, cached per-band pocket grid replac... | B | framework mechanic (map level); carries over unchanged |
| PIT_ROOM_TUNE_TALL_FOLK_DIG_DEEPER | validated | Pit room depth = 3.0 m for a person, scaled by body height (owner card 2026-10-18; replaces 'superdeep only... | B | framework mechanic (map level); carries over unchanged |
| PIT_SPIKES_SHRINK_HALF_A_MAN | doing | RM_Spikes art fills the whole pit cell vertically; redraw: spikes about half a man tall, mostly pointing up... | B | framework mechanic (map level); carries over unchanged |
| PIT_SUPERDEEP_COLLAPSE_1 | doing | Collapse the pit onto the D/F primitive: a superdeep cell you cannot climb out of, a room for prisoner stor... | B | framework mechanic (map level); carries over unchanged |
| PIT_TEMPERATURE_SOFTENING_1 | validated | Pit temperature couples hard to ambient and wears down resistance; Exposed Prisoner thought | B | framework mechanic (map level); carries over unchanged |
| PLANET_ATMOSPHERE_CLOUD_COST_1 | proposed | Measure Planet Atmosphere 8K cloud cost: load-time and VRAM A/B with and without the mod (owner Q2 = measur... | B | tooling / harness / process; world-independent |
| PLANET_GEOMETRY_WIDEN_SUN_STANDS_STILL | proposed | Add fixedSun to PlanetGeometryDef (WeatherSuite), true in Ash'karr def; Sun & Shade reads E and bearing fro... | B | code fix at map/def level; carries over unchanged |
| PLANT_ECONOMY_TUNE_EVERY_NUMBER_AT_ONCE | proposed | Renormalize plant growth and yields planet-wide under the water rule (x0.1 dry, x10 wet+lit, wet natives x4... | B | framework mechanic (map level); carries over unchanged |
| PLANT_FOOTPRINT_HARDENING_1 | built | Huge Things plant adapter hardening from the full GPT review (A2.3, A3.3, A3.8, A3.11, A3.12, C3.2, C4.9, T... | B | framework mechanic (map level); carries over unchanged |
| PLANT_GROWTH_MERGE_NEVER_MEANT_APART | doing | Fuse Jawa Plant Growth (mandrake.rut.plantgrowth) into Baroque Biomes (mandrake.rm.biomes) as one mod with ... | B | art for our own defs; unaffected by the remake |
| PLANT_INTERACTION_GUARDS_1 | built | Huge Things plant interaction guards from the full GPT review (A3.4 interaction cells, A3.6 quest items, A3... | B | framework mechanic (map level); carries over unchanged |
| PLOT_MECHANISM_MODS_WAVE_1 | doing/blocked | Build wave: LLM raid-redesigner + post-battle/event hostility creation + plot-gap mods (from plot_mechanism... | B | content/design at map or def level; survives the remake |
| POND_DEPTH_BUILD_SHALLOWS_BEFORE_MUD | validated | Natural water cells (ponds, marsh, vanilla water terrain) get partial depth like dug cells: a drying pond s... | B | framework mechanic (map level); carries over unchanged |
| POWER_THEFT_BUILD_SLOW_GOODWILL_LEAK | done | GimmeSomeSlack power theft (GS-3 hook): when caught, a steady goodwill drain with the victim faction, like ... | B | biome/mod content at def or map level; carries into a remade world |
| PRECIOUS_CAVE_DEN_OCCUPANT_1 | built | Stillsand: Den quest can target any wild animal of the kind on the map | B | biome/mod content at def or map level; carries into a remade world |
| PREFLIGHT_BUILD_85_ROWS_OF_HINDSIGHT | validated | preflight.py: ordered fail-fast pre-flight (offline before launch + --live first five minutes), PASS/FAIL/U... | B | tooling / harness / process; world-independent |
| PRESS_GATE_BUILDABLE_RESEARCH_1 | built | LuminousPigment: "Buildable" press gate must not finish the research project | B | biome/mod content at def or map level; carries into a remade world |
| PROMISED_GIFT_NEVER_LOST_1 | built | FV-2: owed deep-gifts not dequeued before ransom setting / placement checks | B | biome/mod content at def or map level; carries into a remade world |
| PROPANELAKE_FLOOR_PASS_1 | proposed | Whole individual pass for the Propane Lake floor biome: terrain+features, dive experience, ruled cast wired... | B | biome/mod content at def or map level; carries into a remade world |
| PROPANE_CANAL_WIRE_STILL_NO_FLUID | proposed | Propane has no canal FluidDef, so a propane tank cannot fill a cut | B | biome/mod content at def or map level; carries into a remade world |
| PROPANE_LAKE_MECHANICS_FIRST_SCRIPT_1 | built | First north-star script: PropaneLakeMechanics | B | mod validation script/trial; world-independent |
| PUMP_ART_RESKIN_LESS_GARDEN_HOSE | built | Regenerate the pump: a squarish device with clear join points for hoses and solid pipes, from any side, bot... | B | art for our own defs; unaffected by the remake |
| PYRELANDS_GREEN_FULL_1 | built | Pyrelands north star GREEN on the full list (fresh full-list mapgen on a scratch save, never quicktest) | B | biome/mod content at def or map level; carries into a remade world |
| PYRELANDS_GREEN_MINIMAL_1 | built | Pyrelands north star GREEN on the pyrelands tier (pre-flight gates, 2-ring scratch sites, K-pooled census) | B | biome/mod content at def or map level; carries into a remade world |
| PYRELANDS_NORTHSTAR_TRIAL_1 | proposed | Pyrelands north-star trial: carry the biome template to SHIPPED (parent; depends on BIOME_MOD_UNIFICATION_1) | B | mod validation script/trial; world-independent |
| PYRELANDS_SHIP_READINESS_1 | doing | Pyrelands SHIPPED rung: Ashwallow/Emberscythe art, code review CLEAN, settings gate mechanics, composed deploy | B | biome/mod content at def or map level; carries into a remade world |
| PYRELANDS_STRUCK_GLASS_RITE_BUILD_1 | proposed | Pyrelands: The Struck Glass rite for Zizzik (stamped lightning-glass ring, random powerful strike) | B | content/design at map or def level; survives the remake |
| PYRINTH_FIRST_SCRIPT_1 | validated | First north-star script: Pyrinth | B | mod validation script/trial; world-independent |
| QUARANTINE_PURGE_WEEK_1 | proposed | On/after 2026-10-15 delete /home/mandrake/rm/_quarantine/2026-10-08/ (~117 GB: stale clones + wt/gitlab, al... | B | tooling / harness / process; world-independent |
| RAIDERS_TRENCH_BUILD_BREACH_AND_JUMP | built | Raiders path around or breach a trench; jump-pack raiders cross; ladders pre-built for shallow pits; sieges... | B | biome/mod content at def or map level; carries into a remade world |
| RAIL_WALK_PROVE_NOBODY_WALKS_OFF_ANYWAY | proposed | Guardrail A3: the walked-step door (RefusesWalkedStep / detector put-back) has no live control; an unrailed... | B | framework mechanic (map level); carries over unchanged |
| RAKATAN_ARCHOTECH_MACHINES_1 | validated | Design session with the owner: extend Wrecked Machines into the core Rakatan tech trait - robust, survives,... | B | biome/mod content at def or map level; carries into a remade world |
| REBOOT_BREAKGLASS_VERIFY_1 | proposed/blocked | Verify the break-glass path survives a Windows reboot: WSL Keepalive must bring tailscaled back before logi... | B | tooling / harness / process; world-independent |
| RECLAMATION_TRIGGER_REWIRE_WOKEN_COUNT | built | Reclamation trigger: rewire the built 45-day chain delay to a woken-ancients count (owner card 13, 2026-10-10) | B | biome/mod content at def or map level; carries into a remade world |
| RECORDER_OVERHEAD_MEASURE_SIX_CONFIGS_DEEP | proposed/blocked | Full-list overhead protocol C0-C5 (off; external collector only; sampler without attribution; full recorder... | B | tooling / harness / process; world-independent |
| REGROWTH_RECOLOR_MINEABLES_NRE_1 | doing/blocked | Every full-list save load logs 'Exception from long event: NullReferenceException at ReGrowthCore.Map_Final... | B | biome/mod content at def or map level; carries into a remade world |
| RELOAD_POCKETS_DIAGNOSE_KEPT_NO_RECEIPTS | proposed | B7 reload: pocket_covers differs after save+load (twice); harness now keeps the strings | B | biome/mod content at def or map level; carries into a remade world |
| REPO_RENAME_SYMLINK_RETIRE_1 | doing | Retire the Rimworld -> RimMandrake symlink: repoint every old-path reference, then remove the link | B | tooling / harness / process; world-independent |
| RITE_HARVEST_FIX_PICKS_PAST_FULL | built | Fire-rite harvesters cut pods past the carry limit, search radius centred on pawn not rite origin, route-th... | B | code fix at map/def level; carries over unchanged |
| RIVER_SCENES_BUILD_WALKTHROUGH_WITH_CAPTIONS | proposed | River scenes the owner can watch: current, ford, weir, wash-off-map, with caption panels like the water scenes | B | framework mechanic (map level); carries over unchanged |
| RIVER_STEAM_ANIMATION_1 | built/blocked | Animated steam rising from the rivers (Pyrelands weather visual) | B | framework mechanic (map level); carries over unchanged |
| RIVER_TOGGLE_PROOFS_BUILD_ELEVEN_UNCLAIMED | built | FlowWorks rivers: prove the 11 river settings toggles owed in validation.py, and the 10 untested river-walk... | B | framework mechanic (map level); carries over unchanged |
| RIVER_WEIR_ART_JUDGE_CODEX_SQUINTS | proposed | Zoom in on river-works art (weir, stakes, silt trap, ferry, fords) and hose connections (tank, pump, reel s... | B | art for our own defs; unaffected by the remake |
| ROSTER_FACINGS_SHRINK_FRONT_VIEWS_STAND_TALL | proposed | Facing-scale lint: triage and fix the Baroque Biomes + SWBestiary creatures whose S/N facings are drawn lar... | B | code fix at map/def level; carries over unchanged |
| ROT_BIOME_PROVE_FIRST_IN_LINE | proposed | The Rot is the first biome of the sprint after BIOME_SPRINT_PROVE_SCRUB_SETS_PACE (after Phase 0 removes it... | B | biome/mod content at def or map level; carries into a remade world |
| ROT_CARTOON_VARIANT_REPAINT_1 | proposed | Rot plants: painted replacements for retired cartoon Graphic_Random variants | B | art for our own defs; unaffected by the remake |
| ROT_FAUNA_KIN_WIRING_1 | proposed/blocked | Wire the ruled Rot fauna kin/alarm table onto the 16 race defs (UtinniPatches, FindMod-gated) — AFTER BMT_F... | B | biome/mod content at def or map level; carries into a remade world |
| ROT_MOSS_VERIFY_UNDER_THE_MUSHROOMS | proposed | Look at the hessuk moss (AB_Bryolux, now FloorEmplacement, 1e6363c46) on a Rot map at play zoom; ask owner ... | B | already ported off AB; a look check |
| ROT_REGEN_SHEET_FINISH_SIX_OPTIONS_SERVED | proposed | Rot sheet regen options (Redsong, Angel moth; 6 new candidates, 639507729): enact his picks with art.py ena... | B | art for our own defs; unaffected by the remake |
| ROT_UNJOINING_RITE_1 | proposed/blocked | The Unjoining, for Ta'Baa: a symbiont-joined colonist purged until it dies, just before the clan leaves | B | content/design at map or def level; survives the remake |
| RSW_FACES_VERIFY_IN_GAME_BEFORE_SHIM | proposed | In game: does Facial Animation draw human faces on RSW_ xenotypes? Spawn 2 Jawa + one of each RSW_ humanlik... | B | biome/mod content at def or map level; carries into a remade world |
| RUSTCATHEDRAL_BASE_FINISH_BUILD_1 | validated | Rust Cathedral: line-cycle, hum reading, living coolant eels, overhead-sun heat, cooked strays, mynocks | B | biome/mod content at def or map level; carries into a remade world |
| RUSTCATHEDRAL_BOREHULK_GIANT_BUILD_1 | validated | Rust Cathedral giant: the borehulk, a colossal peaceful mining droid with a worn-out drill (three drill sta... | B | biome/mod content at def or map level; carries into a remade world |
| RUSTCATHEDRAL_GOODWILL_FLOOR_1 | validated | Rust Cathedral hum reads a permanent-enemy faction's goodwill: calm bands may be unreachable | B | biome/mod content at def or map level; carries into a remade world |
| RUSTCATHEDRAL_HULL_BOLTS_BUILD_1 | validated | Hull bolts: living bolts ride the ship for good as hull pets and the Cathedral's ears; reveal and dilemma | B | biome/mod content at def or map level; carries into a remade world |
| RUSTCATHEDRAL_LIVINGBOLT_WALL_FLIT_1 | proposed | LivingBolt flits on walls and surfaces: no mechanism exists, design owed | B | biome/mod content at def or map level; carries into a remade world |
| RUSTCATHEDRAL_MENDING_WELD_RITE_1 | proposed | The Mending Weld, for Rekko: rebuild a broken stretch of old structure into a whole room (Rust Cathedral rite) | B | content/design at map or def level; survives the remake |
| RUSTCATHEDRAL_SHEET_ART_REDO_1 | built | Rust Cathedral sheet: LivingBolt redo art, roach size, installs | B | art for our own defs; unaffected by the remake |
| RUSTCATHEDRAL_STRANGERS_OVERHAUL_RITE_1 | proposed | The Stranger's Overhaul, for Ohm: repair a free droid, capture it mid-repair or release it (Rust Cathedral ... | B | content/design at map or def level; survives the remake |
| RUSTCATHEDRAL_WORN_BIT_ARC_1 | proposed | The Worn Bit: unbolt the borehulk's drill, Junkers refurbish it, restore the giant; keep it to mine or free it | B | biome/mod content at def or map level; carries into a remade world |
| RUST_CATHEDRAL_MECHANICS_1 | validated | Rust Cathedral C# kit: hum-mood system (attitude value, layered tones, bolt-dance display, droid commentary... | B | biome/mod content at def or map level; carries into a remade world |
| RUST_CATHEDRAL_ROACHES_FIRST_SCRIPT_1 | built | First north-star script: RustCathedralRoaches | B | mod validation script/trial; world-independent |
| SALT_BOTTLE_DIAGNOSE_DRUNK_FOR_NOTHING | built | Regression at FlowWorks ea44bf7957: thirst_live T5 salt bottle consumed with no hydration and no poisoning ... | B | framework mechanic (map level); carries over unchanged |
| SALT_TRAVELS_WITH_DOOR_1 | built | TB-2: door salt stored on the door, survives flight/minify | B | framework mechanic (map level); carries over unchanged |
| SALVAGE_MINIFY_DESIGN_HAULER_OR_SCRAP | proposed | After Minify Everything goes: which buildings the Salvage action may lift (minify and reinstall vs scrap fo... | B | content/design at map or def level; survives the remake |
| SALVAGE_WRECKAGE_EVERYWHERE_1 | validated | Salvage wreckage across the planet: wreck families (hulls, tanks, frames, speeders...) scattered in every b... | B | biome/mod content at def or map level; carries into a remade world |
| SALVAGE_YIELD_UNIFY_THREE_RULES_TODAY | proposed | One salvage-yield rule for smelter tiers, crematorium and scavenging (Better Cremation retires in wave 1); ... | B | biome/mod content at def or map level; carries into a remade world |
| SALVATION_RITES_RENORMALIZE_PASS_1 | proposed | Renormalize gods, appeasement kinds and outcomes across all rites | B | content/design at map or def level; survives the remake |
| SALVATION_RITES_UNIFICATION_1 | proposed/blocked | Salvation rites unified in mandrake.rut.rites; biomes teach rites (four Abyss rites, four gods) | B | content/design at map or def level; survives the remake |
| SAND_SHOVEL_DIAGNOSE_DIGS_UNDER_WALLS | proposed | Shovel designation predating a wall stays eligible; dig swaps terrain under the wall? | B | biome/mod content at def or map level; carries into a remade world |
| SANGUOPHAGE_KEPT_UNREACHABLE_1 | built | Owner card: Sanguophage cannot be deleted (XenotypeDefOf binding) - keep the def but make it unreachable (s... | B | biome/mod content at def or map level; carries into a remade world |
| SARLACC_FIRST_SCRIPT_1 | built | First north-star script: Sarlacc | B | mod validation script/trial; world-independent |
| SARLACC_HABITAT_BUILD_1 | doing/blocked | Build the accepted sarlacc design (sarlacc_native_habitat_draft.md, ACCEPTED + all forks RULED 2026-09-12):... | B | biome/mod content at def or map level; carries into a remade world |
| SARLACC_PIT_WIDEN_THE_BIG_ONES | proposed | Sarlacc pit art accepted as the MODERATE pit (9x6); add much bigger pit sizes (variants) in the def/genstep | B | biome/mod content at def or map level; carries into a remade world |
| SARLACC_SEEKER_ROOTING_1 | doing | Sarlacc seeker (RSW_GreatDevourer) quests for food then water, then roots: wire CompSarlaccSwimmer + kill t... | B | biome/mod content at def or map level; carries into a remade world |
| SCALD_ART_UPGRADE_WAVE_1 | proposed | Scald art wave 2: high-res lush restyle of the Scald set, 2-3 stack variants per item; shulla catch as a sm... | B | art for our own defs; unaffected by the remake |
| SCALD_BATHING_RITE_1 | doing | Scald rite: water pilgrims bathe at the cool margins (design; register entry; waits on the margin cove) | B | content/design at map or def level; survives the remake |
| SCALD_GALLERY_SCHEMATIC_UNLOCK_1 | proposed/blocked | Return Gallery: what the immersion-engineering schematic unlocks (RM_ImmersionSchematic is an inert item to... | B | biome/mod content at def or map level; carries into a remade world |
| SCALD_MECHANICS_1 | doing | Scald C# kit: steam-catch industry, margin fishing + bath recreation, bubble-sailor and bottom-walker set-p... | B | biome/mod content at def or map level; carries into a remade world |
| SCALD_SHEET_REDOS_1 | proposed | The Scald sheet 2026-10-05: collect and install the redo renders (shimmer eel, doss, crowncarpet x3, irides... | B | art for our own defs; unaffected by the remake |
| SCALD_STEAM_WEATHER_DESIGN_1 | proposed | Design: Scald steam weather beautiful + interesting + deadly without protective gear; the boiling water's d... | B | content/design at map or def level; survives the remake |
| SCALD_WALKING_PASTURE_1 | built | Scald bottom-walkers: a grazing herd creature first, then the Walking Pasture (crew follows the herd, harve... | B | biome/mod content at def or map level; carries into a remade world |
| SCALD_WATER_AGITATION_FLECKS_1 | validated | Scald wreck shadowData fix + ambient water-agitation ripple mechanism (margin calm / shallow light / deep h... | B | code fix at map/def level; carries over unchanged |
| SCARLANDS_CHATRAK_LIVE_RERUN_1 | proposed | Live re-run of modcheck Scarlands chatrak_snap/snap_stage_0_2 after harness fix e0732bd98 (py_compile only) | B | biome/mod content at def or map level; carries into a remade world |
| SCARLANDS_FIRST_SCRIPT_1 | validated | First north-star script: Scarlands | B | mod validation script/trial; world-independent |
| SCARLANDS_LADDER_FIRST_SCRIPT_1 | validated | First north-star script: ScarlandsLadder | B | mod validation script/trial; world-independent |
| SCARLANDS_MECHANICS_2 | validated | The Scarlands C# kit build: Scarlands mark hediff+severity floor, plated-grazer scaria onset, Forgotten Sen... | B | biome/mod content at def or map level; carries into a remade world |
| SCARLANDS_RELOAD_MIDSTATE_1 | built | SC-5: Scarlands: save-and-reload checks for half-finished states (settling sweep mid-way, ring repair parts... | B | biome/mod content at def or map level; carries into a remade world |
| SCAVENGER_EVENTS_FIRST_SCRIPT_1 | built | First north-star script: ScavengerEvents | B | mod validation script/trial; world-independent |
| SCRAPNEST_BIRD_BASE_THEFT_1 | built | owner card: should scrap-nest birds steal from player bases? | B | biome/mod content at def or map level; carries into a remade world |
| SCREEN_STOPS_SPORES_1 | validated | X-11: particulate/aerosol screen also stops spore clouds (Gas_Damaging asks IsPositionScreened) | B | biome/mod content at def or map level; carries into a remade world |
| SCRUB_BLOOM_FIX_ERUPTOR_FLEES_GROUNDED | built | LeaningScrub: fleeing eruptor never gets TryLaunch (RM_RunwayBloom.cs:206) | B | code fix at map/def level; carries over unchanged |
| SCRUB_BLOOM_FIX_MANHUNTER_GETS_SHY | built | LeaningScrub: bloom orders override animals in mental state (RM_RunwayBloom.cs:150) | B | code fix at map/def level; carries over unchanged |
| SCRUB_CROWNMOB_FIX_CAP_THIRTY_IS_SIXTY | built | LeaningScrub: in-flight mobbers uncounted so maxMobbers cap doubles (RM_VenomvineRooms.cs:129) | B | code fix at map/def level; carries over unchanged |
| SCRUB_GALE_FIX_LATCH_SLEEPS_THROUGH_STORM | built | LeaningScrub: wasGale frozen by master-switch early return (RM_VenomvineForms.cs:576) | B | code fix at map/def level; carries over unchanged |
| SCRUB_GENSTEP_FIX_TIDIES_THEN_QUITS | built | LeaningScrub: SweetlineTrees Plant destroys items then aborts on pawn cell (RM_GenStep_SweetlineTrees.cs:127) | B | code fix at map/def level; carries over unchanged |
| SCRUB_PROOF_FIX_TIDIES_EVERYONES_STEEL | proposed | LeaningScrub: proof hooks destroy bystander fires/plants/steel (RM_FireStamp.cs:363, RM_VenomvineForms.cs:994) | B | code fix at map/def level; carries over unchanged |
| SCRUB_PYRE_FIX_FIVE_FIRES_FIVE_ISLANDS | built | LeaningScrub: too-little-caught warning counts fires not cluster (RM_CallingPyre.cs:130) | B | code fix at map/def level; carries over unchanged |
| SCRUB_SETTINGS_WIRE_MASTER_CANNOT_GREY | built | Leaning Scrub: declare SettingDependencies so the master switch greys its dependents | B | biome/mod content at def or map level; carries into a remade world |
| SCRUB_SMOTHER_FIX_BLANKET_IGNORES_OFF | built | LeaningScrub: in-progress smother job ignores Off setting (RM_SmotherCraft.cs:160) | B | code fix at map/def level; carries over unchanged |
| SCRUB_THORN_FIX_COOLDOWN_PAID_FOR_NOTHING | built | LeaningScrub: scratch cooldown committed before venom-off check (RM_VenomvineForms.cs:627) | B | code fix at map/def level; carries over unchanged |
| SCRUB_WARDEN_FIX_RELEASE_PRUNED_FIRST | built | LeaningScrub: ReleaseAll prunes before wake, MapHeld null after Destroy (RM_SweetlineGuardians.cs:480) | B | code fix at map/def level; carries over unchanged |
| SCRUB_WARDEN_FIX_TAMED_BOSS_STILL_REIGNS | built | LeaningScrub: IsLead ignores faction (RM_SweetlineGuardians.cs:322) | B | code fix at map/def level; carries over unchanged |
| SEABED_DESCENT_ASCENT_1 | proposed | Gravship flies from a sea tile down to its RM_SeabedLayer floor and back up (seabed Phase 2) | B | biome/mod content at def or map level; carries into a remade world |
| SEABED_FAUNA_SINGLE_SEEDER_1 | built | DivingInteraction: Chill floor seeds animals twice | B | biome/mod content at def or map level; carries into a remade world |
| SEABED_PER_SEA_FLOORS_1 | doing/blocked | Sea-floor planet layer Phases 3+4: guard the FinalizeInit plant crash, then a real floor biome per sea (rep... | B | biome/mod content at def or map level; carries into a remade world |
| SEAT_MEMORY_CLONES_DRIVES_1 | doing | Stop seats dying from memory: tmpfs residue, test fan-out, clones, drives (design a98c434cb) | B | tooling / harness / process; world-independent |
| SEAT_MEMORY_STANDARD_FALLBACK_1 | proposed | If the home-made seat-memory pieces misbehave (hook, seat sub-cgroup, harness admission), switch to the sta... | B | tooling / harness / process; world-independent |
| SEA_DIVE_FLOOR_TERRAIN_1 | built/blocked | Gravship dive floors ignore the seas' terrain bands: GenStep_SeaFloorTerrain paints one constant terrain (R... | B | biome/mod content at def or map level; carries into a remade world |
| SEA_DIVE_HATCH_REMOVE_1 | ready/blocked | Delete RM_SeaDiveHatch, RM_SeaDiveExit and their genstep/anchors once descent and layer generators land | B | biome/mod content at def or map level; carries into a remade world |
| SEA_FISHABLES_ALIVE_IN_DEPTHS_1 | validated | Every fishable in EVERY sea owes a living creature swimming the floor map, not just a catch item - owner ru... | B | biome/mod content at def or map level; carries into a remade world |
| SEA_FLOOR_AND_CATCH_PASS_1 | doing | Every sea describes BOTH its floor (animals you meet by diving) and its catch (fish from the shore): the fl... | B | biome/mod content at def or map level; carries into a remade world |
| SEKKULAATH_RISING_DESIGN_CRATER_EVENT | proposed | Sekkulaath rises in the crater event: Wildsteam site damage, closed world sites (owner card 19, 2026-10-10) | B | content/design at map or def level; survives the remake |
| SETTINGS_KIT_BUILD_GREY_SWITCHES_AT_LAST | built | Settings kit: master-switch greying of dependents + Reset-all-to-defaults (confirmed); wire GSS + Pyrelands... | B | framework mechanic (map level); carries over unchanged |
| SETTINGS_SCREEN_KIT_1 | built | X-12: Shared settings-screen kit: collapsible sections, search box, per-section reset, and a "now / new map... | B | framework mechanic (map level); carries over unchanged |
| SETTLEMENT_VERBS_WAVE_1 | doing | v1 interaction verbs: crime suite, salvage-law gray zone, walkable commerce, social fabric | B | biome/mod content at def or map level; carries into a remade world |
| SHADECRAFT_LESSONS_DESIGN_1 | proposed | Shade gear learned by study: lesson-to-piece mapping, and Long-Shade-only lessons vs the cross-biome gear r... | B | content/design at map or def level; survives the remake |
| SHEET_NOTES_FINISH_SEVENTEEN_DEF_HALVES | proposed | Biome art sheets: owner notes on ruled sheets whose DEF half was never done (17 rows: rewritten description... | B | art for our own defs; unaffected by the remake |
| SHIELD_MODS_LEVERAGE_1 | validated | Find existing shield mods, study and make compatible; tuned-plasma-field model per shd rulings | B | biome/mod content at def or map level; carries into a remade world |
| SHIPPING_NAME_CANDIDATES_1 | proposed | Draft 3 invented exotic names each for the 5 wasteland + 2 greentide working names (plus bezoar), put them ... | B | biome/mod content at def or map level; carries into a remade world |
| SHIPVERMIN_FREE_TIER_BEASTS_1 | validated | ShipVermin free tier gets its own beasts; Star Wars bestiary patches canon in when active | B | biome/mod content at def or map level; carries into a remade world |
| SHIP_ALLOY_FORGE_1 | validated | Alloy forge aboard with progressive unlocks: durasteel early (steel + zersium, route TO CONFIRM), plasteel ... | B | biome/mod content at def or map level; carries into a remade world |
| SHIP_TOW_LINE_1 | validated | X-13/CB-9: generalise tether pull Pawn->Thing so a ship tow line drags wrecks/carcasses home | B | biome/mod content at def or map level; carries into a remade world |
| SHIP_VERMIN_FIRST_SCRIPT_1 | validated | First north-star script: ShipVermin | B | mod validation script/trial; world-independent |
| SHOKKWEAVE_ECONOMY_FIRST_SCRIPT_1 | validated | First north-star script: ShokkweaveEconomy | B | mod validation script/trial; world-independent |
| SHOKK_FIRST_SCRIPT_1 | built | First north-star script: Shokk | B | mod validation script/trial; world-independent |
| SLIME_CROSSING_BUILD_SLIPPERY_SLOPE | doing | FlowWorks slime: nearly uncrossable and slow to climb out of (owner: 'so slippery it is nearly uncrossable'... | B | biome/mod content at def or map level; carries into a remade world |
| SLUICE_GATE_REWIRE_TURNS_LIKE_A_DOOR | doing | Sluice gate and every canal water-blocking structure auto-rotate after placement like vanilla doors (orient... | B | framework mechanic (map level); carries over unchanged |
| SOLAR_MIRRORS_BUILD_1 | validated | Solar Mirrors to deploy-ready: ancient Long Shade mirror field, dust, concentration heat, greenhouse, helio... | B | biome/mod content at def or map level; carries into a remade world |
| SOORRAK_INSTANT_JOB_LOOP_1 | doing | Wild soorrak sits in Wait_MaintainPosture forever: its next job succeeds instantly every cycle | B | biome/mod content at def or map level; carries into a remade world |
| SPECIES_TRAITS_OVER_APTITUDES_1 | proposed | Species character is being expressed as plus-or-minus skill aptitudes, which cannot carry nuance - the owne... | B | biome/mod content at def or map level; carries into a remade world |
| SPECIMEN_CABINET_DISPLAY_1 | built | DI-7: specimen cabinet displaying novel finds (Elder NoveltyKey), beauty + museum mood; research-gated, toggle | B | biome/mod content at def or map level; carries into a remade world |
| SPIRE_DUNGEONS_MERGE_DARK_TOWER | proposed | Spire IS the Scald dark tower: reconcile the two built dungeons (SCALD_DARK_TOWER_1, ASHFALL_RESEARCH_BASE_... | B | biome/mod content at def or map level; carries into a remade world |
| SPRINKLER_HEADS_BUILD_PUMP_REQUIRED | doing | Build sprinklers per design/RimMandrake/sprinklers_design_2026-10-16.md (ruled): native pipe head + VFE ada... | B | framework mechanic (map level); carries over unchanged |
| SPRINT_KIT_ART_SKETCH_BEFORE_THE_VETO | proposed | Biome-sprint kit art: 15 guessed designs commissioned (21 artpipe jobs); owner vetoes per line in design/Ri... | B | art for our own defs; unaffected by the remake |
| SPRINT_SITES_DIAGNOSE_VENOMVINE_SCRATCHES | doing | Sprint round test-env hazards: LeaningScrub site colonists scratched by RM_DrippingVenomvine within 50-120 ... | B | biome/mod content at def or map level; carries into a remade world |
| STARWARS_JUNK_RESKIN_1 | doing | Reskin vanilla ancient junk (cars, tanks, walkers, dropships) as Star-Wars-adjacent wrecks: Graphic_Random ... | B | art for our own defs; unaffected by the remake |
| STATION_REACH_CENTRE_RETHINK_FOOTPRINT | validated | FlowWorks P11 (GPT G1.22, note): a pumping station's reach is measured from its position, not its footprint... | B | code fix at map/def level; carries over unchanged |
| STATUE_ART_EXPANSION_1 | proposed | Statue expansion: assess the statue-choice mod (patch vs own), RM statues with flame emergence points, Utin... | B | art for our own defs; unaffected by the remake |
| STILLSAND_CAVE_AS_PLACE_1 | validated | Stillsand cave: preservation, drip, biosilica walls, tribal mark | B | biome/mod content at def or map level; carries into a remade world |
| STILLSAND_CONTENT_LIVE_PROOF_1 | proposed | Prove the built Stillsand cast live (atlas, zuurrik on blood) and swap four placeholder renders | B | biome/mod content at def or map level; carries into a remade world |
| STILLSAND_DUNE_GALE_LIVE_1 | proposed | Stillsand dune gale: live proof (mass delta, sun off, one emergence, carry letters, dust devil) + water ski... | B | biome/mod content at def or map level; carries into a remade world |
| STILLSAND_EVENT_CREATURES_LIVE_1 | built | Live-prove the krayt attack and muurrok on a Stillsand quicktest, and live-fire the Long Hunger | B | biome/mod content at def or map level; carries into a remade world |
| STILLSAND_FIRST_SCRIPT_1 | built | First north-star script: Stillsand | B | mod validation script/trial; world-independent |
| STILLSAND_GEOPHONE_1 | validated | Stillsand biosilica geophone: rumble markers from the sand-swim query | B | biome/mod content at def or map level; carries into a remade world |
| STILLSAND_GLASS_CHAIN_REMAINDER_1 | doing | Stillsand glass chain remainder: krayt lens, goggles recipe, fulgurite art, art wire-in, live proof | B | biome/mod content at def or map level; carries into a remade world |
| STILLSAND_LOOMMA_SUNSTRUCK_SHADE_1 | proposed | modcheck Stillsand loomma/loomma_sunstruck_open_vs_roofed FAILS live on acc_biomes-15: sunstruck no worse i... | B | biome/mod content at def or map level; carries into a remade world |
| STILLSAND_MUURROK_EMERGENCE_1 | proposed | Stillsand RM_MuurrokEmergence fires but no RM_Muurrok appears | B | biome/mod content at def or map level; carries into a remade world |
| STILLSAND_PRECIOUS_CAVES_LIVE_1 | validated | Precious caves: ten live Stillsand quicktest maps | B | biome/mod content at def or map level; carries into a remade world |
| STILLSAND_RETURN_REMAINDER_1 | proposed | Stillsand Return remainder: live proof, the visible Return line, cave debt stones, more water sources, stal... | B | biome/mod content at def or map level; carries into a remade world |
| STILLSAND_ROOF_COVER_EXPOSURE_1 | proposed | Stillsand roof at 60 deg reads exposure 1.00 under a verified roof | B | biome/mod content at def or map level; carries into a remade world |
| STILLSAND_SANDSWIM_GRAVEL_SUBMERGE_1 | proposed | modcheck Stillsand sandswim/vekka_submerges_on_sand FAILS live on acc_biomes-15: a vekka on Gravel is RM_Sa... | B | biome/mod content at def or map level; carries into a remade world |
| STILLSAND_SAND_SIEVE_CHORE_1 | validated | Stillsand sand sieve as a pawn chore: glass sand to fine sand with a carried sieve (feasible, no building) | B | biome/mod content at def or map level; carries into a remade world |
| STILLSAND_SAND_SWIM_REMAINDER_1 | doing | Sand-swim kit remainder: thumper, sand fishing, the Listening, wake track records, drift depth, Drazzik/Sar... | B | biome/mod content at def or map level; carries into a remade world |
| STILLSAND_SKELETONS_REMAINDER_1 | validated | Stillsand skeletons remainder: tracks on the footprint grid + dune eraser, dune burial, skeleton/skull art ... | B | biome/mod content at def or map level; carries into a remade world |
| STILLSAND_SOLAR_STILL_1 | built | Stillsand solar still and wringing still: sun-gated lens condenser distilling brine, wet organics and the dead | B | biome/mod content at def or map level; carries into a remade world |
| STILLSAND_SUN_LANCE_1 | validated | Stillsand sun lance: heliostat mirror turret that heats and never ignites | B | biome/mod content at def or map level; carries into a remade world |
| STILLSAND_SUN_LIVE_VERIFY_1 | built | Live-verify Stillsand sun from latitude on quicktest maps at two latitudes: no night, shadow length by lati... | B | biome/mod content at def or map level; carries into a remade world |
| SUBSTRUCTURE_PROPS_LAYER_OOB_1 | doing/blocked | Live 2026-09-30b: 'Could not regenerate layer RimWorld.SectionLayer_SubstructureProps: IndexOutOfRangeExcep... | B | biome/mod content at def or map level; carries into a remade world |
| SUMP_EFFIGY_RITE_BUILD_1 | proposed | Sump Rite B, Mob'Unloo's Price: good thing + hated effigy; Empire held off 5x on this map, faction's next g... | B | content/design at map or def level; survives the remake |
| SUMP_GASLIGHT_1 | doing/blocked | Sump gaslight: tar+acid reaction makes green gas (Helixien integration OK), warbling lamp light, flame stat... | B | biome/mod content at def or map level; carries into a remade world |
| SUMP_GLASSWALK_SPEED_RATIO_1 | proposed | Glasswalk measured 0.65 of granite speed (3 repeats, 9.8 ticks/cell pawn, glass 15) vs spec ~0.80 for pathC... | B | biome/mod content at def or map level; carries into a remade world |
| SUMP_INHABITED_NOTES_1 | proposed | Sump Inhabited injection notes (owner, 2026-09-24, for later): junkers/Jawa/deep tribes/Black Star more pre... | B | biome/mod content at def or map level; carries into a remade world |
| SUMP_MECHANICS_1 | doing | Sump C# kit: poured tar moat + command ignition (smoke wall), dig-lottery tables with era booby traps weigh... | B | biome/mod content at def or map level; carries into a remade world |
| SUMP_NOOTHELM_B_PLANT_1 | built | New Sump plant from the noothelm B render, cuisine implications | B | biome/mod content at def or map level; carries into a remade world |
| SUMP_SINKING_RITE_BUILD_1 | ready/blocked | Sump Rite A, the Sinking: one valuable into the tar; Heat down, fewer raids, claims wiped; beast-sleeps and... | B | content/design at map or def level; survives the remake |
| SUMP_TAR_FIRE_NETWORK_1 | doing | Network fire with gate firebreaks; wire belch to glass-cooling | B | biome/mod content at def or map level; carries into a remade world |
| SUMP_TAR_LIVING_SYSTEMS_1 | built | Living-map responders; tar rain mod-vs-scenario split | B | biome/mod content at def or map level; carries into a remade world |
| SUMP_TAR_NASTINESS_1 | validated | Sump nastiness mechanics: sticky tar overlay on any terrain, tarred-pawn hediffs, weak solvent craftable in... | B | biome/mod content at def or map level; carries into a remade world |
| SUMP_WALKWAYS_1 | built | Sump walkways, two tiers: duckboards (cheap, foul with tar, burn) and glasswalk (never fouls, never full sp... | B | biome/mod content at def or map level; carries into a remade world |
| SUNSHADE_DEPLOY_RIDES_THE_SAME_TRUCK | proposed | Ship the SunAndShade member in the same composed mandrake.rm.biomes redeploy Phase 0 already waits on; neve... | B | framework mechanic (map level); carries over unchanged |
| SUNSHADE_EXTRACT_DECIDE_WHEN_CLOCK_TICKS | proposed | PARKED: revisit standalone mod (alt A) when the day/night clock mode exists or a non-Baroque mod needs the ... | B | framework mechanic (map level); carries over unchanged |
| SUNSHADE_MIGRATE_MOVE_NOT_CHANGE | proposed | Create SunAndShade compose member (own csproj, DLL, settings page); move Sun & Shade files/defs from CB and... | B | blocks 6 Direct-Sun/tree-shade items; class moves after a remake only drop SKIPPED components |
| SUNSHADE_PROVE_EVERY_TYPE_ONE_HOME | proposed | Offline lint: every XML Class=, reflected type string and saved MapComponent class resolves to exactly one ... | B | framework mechanic (map level); carries over unchanged |
| SURFACE_HOME_MAP_HELPER_1 | built | X-1: one helper returns a surface home map (skips RM_SeabedLayer); swap the five Find.AnyPlayerHomeMap call... | B | biome/mod content at def or map level; carries into a remade world |
| SURFACE_RIVER_WEIRS_1 | validated | Port the weir / bank-works / breach system to ordinary surface river tiles (owner-typed 2026-09-26): weir, ... | B | biome/mod content at def or map level; carries into a remade world |
| SUSPENSION_ART_RESKIN_HE_SEES_FIRST | built | Suspension bridge textures in four styles: deck, grate, railing, anchor, tower, debris, jetty; review sheet... | B | art for our own defs; unaffected by the remake |
| SUSPENSION_BASE_REWIRE_COVERS_STEP_OUT | validated | Lift Building_PitCover into a span base class; DeckedAt replaces IsCovered at seven call sites; no behaviou... | B | framework mechanic (map level); carries over unchanged |
| SUSPENSION_BRIDGE_BUILD_POSTS_AT_BOTH_ENDS | built | Suspension bridge at the surface over dug ground: drag anchor to anchor, length per type + towers, load sho... | B | framework mechanic (map level); carries over unchanged |
| SUSPENSION_GRATE_BUILD_LET_THE_FIRE_UP | built | Grated suspension deck: fire reaches people above, burns, spilled liquid drains below, liquid shows through | B | framework mechanic (map level); carries over unchanged |
| SUSPENSION_JETTY_BUILD_WALK_THE_PLANK | built | Suspension bridge jetty: 1-2 square cantilever from an anchor, one person's weight, fails at the root | B | framework mechanic (map level); carries over unchanged |
| SUSPENSION_LIVE_DIAGNOSE_FIRST_REAL_RUN | built | Suspension bridges first live proof: 12 PASS / 13 FAIL (looks unstyled, rails-off never drops, shot through... | B | framework mechanic (map level); carries over unchanged |
| SUSPENSION_UNDERPASS_BUILD_MIND_YOUR_HEAD | built | Walk under suspension bridges (2 m clearance, floor band), sunken bridges via ledge/ramp/ladder, roof-colla... | B | framework mechanic (map level); carries over unchanged |
| SUSPENSION_WATERS_BUILD_MAY_BACKTRACK | built | Suspension bridges over rivers, large lakes and ocean: towers in water, floods, current exemption; backtrac... | B | framework mechanic (map level); carries over unchanged |
| SWALE_CANAL_ART_REFERENCE_1 | doing/blocked | Swale art from live reference: build a real FlowWorks canal in game, screenshot it, spec the RM_Swale art f... | B | art for our own defs; unaffected by the remake |
| TAKEN_BY_LAND_SERVICE_1 | validated | X-10: one 'taken by the land, comes back later' service for gale carry + swept-away, with ground trace | B | biome/mod content at def or map level; carries into a remade world |
| TANK_LOOKS_WIRE_FOUR_STYLE_SWITCH | doing | FlowWorks tanks (liquid tank, universal cargo tank, etc.) get the four-look style switch like hose reels an... | B | framework mechanic (map level); carries over unchanged |
| TANK_TALL_BUILD_TWICE_THE_DRINK | done | Tall variants of RM_LiquidTank and RM_UniversalCargoTank: same footprint, double the storage (160 / 320 uni... | B | framework mechanic (map level); carries over unchanged |
| TAOZIN_BRINE_TANK_BUILD_GRUB_GOES_PALE | doing | Taozin grub brine tank (C#): grub kept in brine makes RSW_TaozinBrine from RM_Brine; long-brined grub switc... | B | biome/mod content at def or map level; carries into a remade world |
| TAOZIN_SPLIT_BUILD_ONE_WORM_BECOMES_TWO | proposed | Taozin split: adult RSW_Taozin + RSW_TaozinGrub, nest, brine, art | B | biome/mod content at def or map level; carries into a remade world |
| TAR_BEAST_SETTINGS_CONSISTENCY_1 | built | EnvironmentalHazards: Tar-beast settings: pace, building limit, solvent hunt, sink rule | B | framework mechanic (map level); carries over unchanged |
| TAR_COOLING_GLASS_MEND_ENGINE_CELLS | validated | FlowWorks P6b (GPT G3.5): tar cooling writes glass onto cells the depth engine owns (Flood_FlowWorks.cs ~37... | B | code fix at map/def level; carries over unchanged |
| TAR_LOOK_TUNE_THICK_AND_SLOW | doing | Tar surface: water ripple plus a thick, slow, glossy look, tuned live with the owner; needs a live look-tun... | B | framework mechanic (map level); carries over unchanged |
| TECHPRINT_FACTION_GATING_1 | built | Code the four research access classes: common / faction-held techprints / jawa-special / ship-only | B | biome/mod content at def or map level; carries into a remade world |
| TELEMETRY_BUILD_EVERY_TICK_ACCOUNTED | validated | Build the hybrid telemetry stack (VictoriaMetrics + SQLite + Grafana + RimPulse alerts) on E:, 1 s test tie... | B | tooling / harness / process; world-independent |
| TELEMETRY_COLONY_VITALS_BUILD_SPEC_SAID_SO | validated | Colony vitals as telemetry: per map, # colonists alive, # in distress (downed / mental break / bleeding out... | B | tooling / harness / process; world-independent |
| TELEMETRY_DUPLICATES_RETIRE_AFTER_QUIET_WEEK | proposed | Design 08 P5, due after telemetry has run a week (from 2026-10-11): fold obs_events' transport/timeout/outc... | B | tooling / harness / process; world-independent |
| TELEMETRY_STACK_BUILD_AFTER_THE_MOVE | proposed | Build telemetry: VictoriaMetrics + SQLite + Grafana + RimPulse alerts on E:, 1 s windows + flight recorder ... | B | tooling / harness / process; world-independent |
| TEMPLE_RUINS_DESIGN_SEVERAL_FAITHS | proposed | Ruined temples in several Star Wars-esque faith themes as world mutators, plus Inhabited temples with livin... | B | content/design at map or def level; survives the remake |
| TERMINALBIOMES_REVIEW_FIXES_1 | built | TerminalBiomes 29-file review fix wave: 2 dead tickerType mechanisms (vaulisk lure never springs, mobile gl... | B | code fix at map/def level; carries over unchanged |
| TERMINAL_BIOMES_FIRST_SCRIPT_1 | built | First north-star script: TerminalBiomes | B | mod validation script/trial; world-independent |
| TERMINAL_SETTINGS_CONSUMERS_WIRE_1 | built | TerminalBiomes: TerminalBiomes settings that do nothing or say the wrong thing | B | biome/mod content at def or map level; carries into a remade world |
| TESTENV_FLOODS_HARDEN_SEASON_CRASHES_PARTY | built | 'Seasonal flooding' ThreatSmall letter on the FlowWorks river site map during extension_proof (04:29Z): sto... | B | tooling / harness / process; world-independent |
| TESTENV_HIVES_HARDEN_RIVER_MAP_SQUATTERS | built | FlowWorks river_site map carried a dormant insect Hive + GlowPod (vitals threat_structure, 04:28Z) during e... | B | tooling / harness / process; world-independent |
| TESTENV_MEGAPEDE_HARDEN_GATECRASHER | built | Test environment: a VFEI2_Megapede + 3 Spelopede (Insect) arrived on the FlowWorks golden site mid liquid_h... | B | tooling / harness / process; world-independent |
| TESTENV_QUICKTEST_DIAGNOSE_SPIKES_UNINVITED | proposed | Test env threats on fresh dev quicktest maps (ratchet_pilot, all DLC, 695812d5ec): map A had 3 Megaspiders ... | B | tooling / harness / process; world-independent |
| TESTENV_TOXIC_DIAGNOSE_RIVER_SITE_SNIFFLES | proposed | Test env threat: on river_site map 5 (tile 15061, TemperateForest, 695812d5ec) a colonist gains ToxicBuildu... | B | tooling / harness / process; world-independent |
| TESTENV_TRIALSITE_DIAGNOSE_NOBODY_HOME | built | Test environment: NS_FlowWorks_TrialSite_v1 on ratchet_pilot+patches loads with NO living colonist on the c... | B | tooling / harness / process; world-independent |
| TETHER_PRODUCTION_REEL_PROOF_1 | built | CreatureBehaviors: Tether proof should run the real production tick | B | biome/mod content at def or map level; carries into a remade world |
| TEXREGEN_UNPROVEN_ASK_THE_SHEETS | proposed | Live art with no pipeline record in the art ledger: adjudicate (owner-picked, hand-made or stand-in) | B | art for our own defs; unaffected by the remake |
| THE_BAZAAR_FIRST_SCRIPT_1 | built | First north-star script: TheBazaar | B | mod validation script/trial; world-independent |
| THE_FORGE_FIRST_SCRIPT_1 | built | First north-star script: TheForge | B | mod validation script/trial; world-independent |
| THE_ROT_FIRST_SCRIPT_1 | built | First north-star script: TheRot | B | mod validation script/trial; world-independent |
| THE_SUMP_FIRST_SCRIPT_1 | validated | First north-star script: TheSump | B | mod validation script/trial; world-independent |
| THING_LOOKUP_BUILD_OWNER_IS_NOT_PAINTER | built | Map awareness phase 2 (companion C#): jawa/thing_explain (one selector, never silent pick; def/kind/race/mo... | B | tooling / harness / process; world-independent |
| THIRST_BUILD_OWN_BOTTLES_DUBS_FRIENDLY | doing | FlowWorks gets its own drinking bottles and its own thirst need (design first); when Dubs Bad Hygiene Lite ... | B | framework mechanic (map level); carries over unchanged |
| THIRST_DESIGN_SLIME_IS_THE_LAST_RESORT | proposed | 3x3 deep design pass: thirst, every fluid type, gathering/storage/access, health, jobs, crop watering, mach... | B | content/design at map or def level; survives the remake |
| THIRST_RULES_BUILD_SALT_OFF_THE_MENU | doing | Build the ruled thirst/fluid rules: first fix today's two rule breaks (auto-fill gathers any liquid; thirst... | B | framework mechanic (map level); carries over unchanged |
| THORNBUG_FEAR_SCOPE_1 | built | EnvironmentalHazards: Map-wide StoryDanger.High bypasses the ruled 40-cell fear radius | B | biome/mod content at def or map level; carries into a remade world |
| THROAT_CASK_ITEM_1 | built | RUT_ThroatCask: heavy stack-1 hauled item, constant radiation, bursts on carrier hurt/burn | B | biome/mod content at def or map level; carries into a remade world |
| TICKER_NEVER_FIRES_FIX_1 | validated | 5 comps the new ticker lint says never tick: RUT_DyingCreep (CompTick on a Long plant), RM_Skylight Warblin... | B | code fix at map/def level; carries over unchanged |
| TILE_STRUCTURE_DESIGNS_1 | built | Make and improve the promise/whisper structure designs per the roster (22+22): rimplace templates + GenStep... | B | content/design at map or def level; survives the remake |
| TILE_TEMP_CACHE_RESET_TOOL_1 | built | JawaBench: world_tile_set (or a new jawa/tile_cache_reset) nulls Tile.cachedMinTemp/cachedMaxTemp/hilliness... | B | tooling / harness / process; world-independent |
| TITANIC_BODYSIZE_TEST_RACE_1 | proposed | Titanic not_driven rows need a bodySize 8/20 test race or override tool | B | framework mechanic (map level); carries over unchanged |
| TITANIC_CREATURES_FIRST_SCRIPT_1 | validated | First north-star script: TitanicCreatures | B | mod validation script/trial; world-independent |
| TITANOSLIME_SLIME_BIOME_1 | ready | Owner ask: a Titanoslime for RUT_Slime, devour-whole + grows-as-it-eats | B | framework mechanic (map level); carries over unchanged |
| TITAN_BREAKTHROUGH_CLEARING_1 | built | Titans smash THROUGH built obstacles and eligible giant plants instead of detouring, as card #1 rules (B3.4... | B | framework mechanic (map level); carries over unchanged |
| TITAN_CAMPS_SCAVENGERS_EVENTS_1 | proposed | Huge Things titans: corpse camps, scavenger draw, footfall-warned titan events. Ruled by cards #4/#5 2026-0... | B | framework mechanic (map level); carries over unchanged |
| TITAN_ROOF_AVOIDANCE_1 | built | Titans never path under thick roof, footprint-wide, as card #1 rules (B3.5/D3.1/D1.4; fix B2.6 comment) | B | framework mechanic (map level); carries over unchanged |
| TITAN_TRENCHES_WIRE_MIND_THE_GAP | built | Titans step over trenches narrower than B/4 (card 3): wire WallsSlots.StepsOverTrench into FlowWorks' cliff... | B | framework mechanic (map level); carries over unchanged |
| TITAN_WAKE_FIXES_1 | built | Titan wake step fixes from the full GPT review (B3.6 per-step dedup, B3.7 real-move only, B3.8 flying, B2.4... | B | code fix at map/def level; carries over unchanged |
| TPS_HOOKS_HARDEN_REENTRY_AND_LATE_GUARDS | built | Fix the TPS-code hazards in GPT review 2.3: global state in TmuPrefix/Postfix, LePrefix/LeFinalizer and _ti... | B | tooling / harness / process; world-independent |
| TPS_VERDICT_FIX_SIX_SECONDS_NOT_THIRTY | proposed | JawaBench sampler + tps_record reader: the sustained low/high TPS verdict counts 6 windows, which is 30 s a... | B | tooling / harness / process; world-independent |
| TREE_BURST_BUILD_LITRES_BUY_YEARS | doing | ExplosiveGrowth tree burst, as ruled 2026-10-17: trees = visual 3.0+ (fungi never, Greatbole excluded); 40 ... | B | framework mechanic (map level); carries over unchanged |
| TREE_BURST_DESIGN_SWEETLINE_TAKES_ITS_TIME | proposed | Explosive growth for tree-sized plants: water advances a tree a bit along a long life; a full burst yields ... | B | content/design at map or def level; survives the remake |
| TREE_CROWN_MEASURE_FROM_THE_ART | proposed | Extend measure_huge_plant_masks.py to emit crown radius and height for the six day-side giants, replacing t... | B | art for our own defs; unaffected by the remake |
| TREE_GRAPHICS_OWNERSHIP_1 | built/blocked | Own tree art at our scales: generate custom tree graphics (sweetline trees first — huge, ancient); remove t... | B | framework mechanic (map level); carries over unchanged |
| TREE_SHADE_BUILD_CROWNS_ON_STILTS | proposed/blocked | Tree crowns cast Direct Sun shade by sun geometry (projected crown disc + trunk strip, growth-aware, overla... | B | framework mechanic (map level); carries over unchanged |
| TREE_SHADE_SELFTEST_PROVE_FOREST_IS_SHADE | proposed/blocked | Offline selftest for the tree crown shade model (T1-T6 of the adopt-or-fall-back test) plus per-biome canop... | B | framework mechanic (map level); carries over unchanged |
| TRENCH_COVER_BUILD_SANDBAGS_MADE_OF_DIRT | validated | Dug holes give cover (wet or dry) read like sandbags; raiders use it with cage check; no blast cover; fix o... | B | framework mechanic (map level); carries over unchanged |
| TRENCH_CROSSING_FIX_DOWN_ACROSS_AND_UP | built | Bank-to-bank across a laddered trench is one reachability hop (down, floor, up) for any pawn the ladders al... | B | code fix at map/def level; carries over unchanged |
| TWILIGHTSEA_FLOOR_PASS_1 | proposed | Whole individual pass for the Twilight Sea floor biome: terrain+features, dive experience, ruled cast wired... | B | biome/mod content at def or map level; carries into a remade world |
| TWILIGHTSEA_FLORA_PASS_1 | built | Twilight Sea underwater flora pass: own strange-flora roster in the light-economy register (decision taken ... | B | biome/mod content at def or map level; carries into a remade world |
| TWILIGHT_SEABED_WELLS_MISSING_1 | built | Twilight skylight wells run only on the old pocket-map floor; the RM_SeabedLayer floor gets none, so well-d... | B | biome/mod content at def or map level; carries into a remade world |
| TWILIGHT_SEA_FIX_IT_RAINS_UNDERWATER | built | RM_TwilightSea BiomeDef has <Rain>4</Rain> (TerminalBiomes/Defs/BiomeDefs/RM_TwilightSea.xml:110); it is a ... | B | code fix at map/def level; carries over unchanged |
| TWILIGHT_WELL_AVOIDS_CURRENT_1 | built | TB-3: twilight wells avoid the current lane map | B | biome/mod content at def or map level; carries into a remade world |
| TWILIGHT_WELL_LIGHT_STATE_1 | built | TerminalBiomes: Twilight wells: dimming not composed or saved, last waning step unreachable, frozen not frozen | B | biome/mod content at def or map level; carries into a remade world |
| TWO_FRONT_BAIT_TARGETING_1 | built | FeverWood: Two-front lure: real opposite fronts and a bait objective | B | biome/mod content at def or map level; carries into a remade world |
| UNDERPASS_REACH_VERIFY_WALK_UNDER_FOR_REAL | proposed | Live row for a01c76fe25: CanReach and A* agree in game for a colonist in a trench walking under a surface s... | B | biome/mod content at def or map level; carries into a remade world |
| UNFINISHED_LINE_SITE_BEATS_1 | built | Beats 3-5 run at the chosen site (A/C/D): caravan tithe, defence-site First Light variant | B | biome/mod content at def or map level; carries into a remade world |
| UNFINISHED_LINE_SITE_CHOICE_1 | built/blocked | Unfinished Line site choice (where the line stands, A-D) offered at the end of beat 2 and carried to beats ... | B | biome/mod content at def or map level; carries into a remade world |
| UNFINISHED_LINE_TITHE_BEAT_1 | built | Unfinished Line beat 4 The Tithe and the Hands: scaled material tithe to the site + lend a Crafting 8 colon... | B | biome/mod content at def or map level; carries into a remade world |
| UNFINISHED_LINE_WORLD_FOUNDRY_1 | validated | Unfinished Line runs in the world (Q1=A): Enclave regrowth, Foundry-grade frames/parts in Enclave stock, vo... | B | biome/mod content at def or map level; carries into a remade world |
| UNPROVEN_LIVE_LEGS_TRIAGE_1 | proposed | Triage unproven Cauldron, FeverWood, RustCathedral, Forge live legs | B | tooling / harness / process; world-independent |
| UTINNI_DISCOVERY_ACHIEVEMENTS_1 | built | Utinni discovery achievements mod: surfaces every discoverable and unique mod capability so players know to... | B | biome/mod content at def or map level; carries into a remade world |
| UTINNI_WORLDMAP_FLIGHT_ICON_1 | validated | Replace the gravship's world-map flight icon with a Utinni-specific sprite: vanilla WorldObjectDef Gravship... | B | art for our own defs; unaffected by the remake |
| VALIDATION_SETTINGS_SNAPSHOT_1 | built | TerminalBiomes: TerminalBiomes live validation resets the owner's settings and never tests Scribe | B | tooling / harness / process; world-independent |
| VALIDATION_V2_IDENTITY_WIRE_READS_ZERO | proposed | validation_v2.py and proof_all write no deploy fingerprint/run_identity, so the report counts 0 proven; rec... | B | tooling / harness / process; world-independent |
| VALIDATION_V2_RECONCILE_AFTER_THE_BIG_DIG | proposed | Sort validation_v2's 24 failures into test-site causes (P11 shore shelf on painted ponds) and real regressi... | B | tooling / harness / process; world-independent |
| VANILLA_BEAST_EXCISION_1 | doing | No vanilla beasts in the Utinni scenario: cut every vanilla/DLC animal at the scenario layer, biome by biom... | B | scenario-layer cut of vanilla beasts; not a donor, not world-bound |
| VAULISK_LURE_REVEAL_TRIGGER_1 | built | TerminalBiomes: Vaulisk lure reveal can miss a passing pawn entirely | B | biome/mod content at def or map level; carries into a remade world |
| VAULT_DUNGEON_BUILD_1 | built | Build the six Forsaken vaults: concentric grammar templates, LARGE maps, quicktest-proven | B | biome/mod content at def or map level; carries into a remade world |
| VAULT_THAW_QUEST_FAMILY_1 | validated | Six Forsaken vault layouts exist but nothing makes them play - no QuestScriptDef family for thaw/reversal/s... | B | content/design at map or def level; survives the remake |
| VENOMVINE_BUILD_SCRUB_GROWS_TEETH | doing | Venomvine: LeaningScrub's integral plant - grows abundantly, tall and dangerous; design pass over its many ... | B | biome/mod content at def or map level; carries into a remade world |
| VERMIN_EAT_BREEDING_FOOD_1 | validated | CB-3: breeding vermin consume food per litter; unreachable food does not count | B | biome/mod content at def or map level; carries into a remade world |
| VEXXITH_USES_1 | proposed | Vexxith uses: acid-proof material for FlowWorks, hulls and suits | B | biome/mod content at def or map level; carries into a remade world |
| VISITOR_DETECTORS_MEND_NAME_THE_STRANGER | validated | Map awareness phase 1 (Python harness): per-test bounded expectation contract; detectors name exact pawn id... | B | tooling / harness / process; world-independent |
| VITALS_OVERHEAD_MEASURE_FULL_LIST_TOLL | proposed | Measure the vitals monitor's overhead armed vs off on the 23-mod tier and the full list (GPT §5): busy pawn... | B | tooling / harness / process; world-independent |
| WALL_SCALING_BUILD_ROPE_OVER_RAMPARTS | built | Climbing gear scales built walls (unroofed both sides): ask whether 'walls' meant building walls | B | art for our own defs; unaffected by the remake |
| WARBLING_GLOW_BASELINE_1 | built | EnvironmentalHazards: Warbling gaslight overwrites player colour and leaves its last frame when disabled | B | biome/mod content at def or map level; carries into a remade world |
| WARCASKET_FIRST_SCRIPT_1 | validated | First north-star script: Warcasket | B | mod validation script/trial; world-independent |
| WARCASKET_JUNKER_KINDS_BUILD_1 | built | Warcasket Junker: passive scavenger + elite hostile pawnkinds, sealed-corpse scatter, both in trade caravans | B | biome/mod content at def or map level; carries into a remade world |
| WARCASKET_WASTE_RUN_REMAINDER_1 | validated/blocked | Cask-bay follow-ons: five waste-run destinations, Stenchlands cask item, Junker pawnkind wearing the warcas... | B | biome/mod content at def or map level; carries into a remade world |
| WARDEN_MOTHER_LAND_RECOVERY_1 | built | EnvironmentalHazards: Water-locked pawn on land has no route back to water | B | biome/mod content at def or map level; carries into a remade world |
| WARLAB_CRATER_ACCIDENTAL_TRIGGER_1 | proposed/blocked | RUT_WarLabReactorCore's CompIgniteCraterOnDestroy fires the planet-wide Chill crater swap on ANY destructio... | B | biome/mod content at def or map level; carries into a remade world |
| WARLAB_GARRISON_DESIGN_EARLY_BLAST | proposed | Early lake blast: Empire heat rise + Imperial garrison outside the revealed war lab (owner card 8, 2026-10-10) | B | content/design at map or def level; survives the remake |
| WARLAB_SPECIMENS_DESIGN_BREAKOUT_CHOICE | proposed | War lab specimens: design the player's containment choice, the breakout, the recover-or-fail beat (owner ca... | B | content/design at map or def level; survives the remake |
| WARSCAR_AEROSOL_SCREEN_1 | validated/blocked | Warscar projectors and aerosol screen: lift ShipShields particulate core to RM, broad polluted-biome screen... | B | biome/mod content at def or map level; carries into a remade world |
| WARSCAR_CHOTRIX_SIGNS_1 | validated/blocked | Chotrix readable signs: track-grid prints and dragged-kill marks (needs FOOTPRINT_TRACK_GRID_1), tetchik si... | B | biome/mod content at def or map level; carries into a remade world |
| WARSCAR_HOSPICE_DESERTERS_1 | doing | Warscar hospice: kneeling chassis rings, deserter histories, five-stage cradle revival into an overseer-fre... | B | biome/mod content at def or map level; carries into a remade world |
| WARSCAR_OLD_TONGUE_1 | built | Warscar old tongue: inscribed panel sets read by Intellectual 8 unlock hospice protocols, projector calibra... | B | biome/mod content at def or map level; carries into a remade world |
| WARSCAR_OPEN_BOAST_RITE_1 | proposed | The Open Boast, for Ozzik, found in the Warscar: a public boast, a warned challenge raid, once per colony | B | content/design at map or def level; survives the remake |
| WARSCAR_PILGRIM_JOURNAL_ANTIQUITY_1 | built | Pilgrim journals as Antiquities artifacts: catalogue at the Reading Station also advances the Scarlands lad... | B | biome/mod content at def or map level; carries into a remade world |
| WARSCAR_RAINBOW_POOLS_1 | validated/blocked | Warscar rainbow pools: reaction-liquor registry row, phase cycle with colour-blind icons, tap and four reag... | B | biome/mod content at def or map level; carries into a remade world |
| WARSCAR_TOTCHAK_WAKES_1 | validated | Warscar totchak: dormant in the Last Line, demolition wake, eats ruin walls then player walls, lies down again | B | biome/mod content at def or map level; carries into a remade world |
| WARSCAR_TURRETS_TRACK_1 | validated | Warscar turrets still track: verbless aim comp on broken turrets, refit into a working old-line turret | B | biome/mod content at def or map level; carries into a remade world |
| WARSCAR_VALIDATION_FIDELITY_1 | built | Scarlands: Warscar validation proves less than it claims | B | biome/mod content at def or map level; carries into a remade world |
| WAR_LAB_CRATER_HOOK_1 | built/blocked | Ignition->crater world-tile mutation C# hook for the war lab, blocked on LIQUID_BIOMES_MAP_1's frozen footp... | B | biome/mod content at def or map level; carries into a remade world |
| WASTELAND_CONTAGION_PROBE_FIVE_LOOSE_ENDS | proposed | Reproduce live the unresolved acc_biomes findings: Wasteland tipping + middenshell toggles, Contagion place... | B | biome/mod content at def or map level; carries into a remade world |
| WASTELAND_FIRST_SCRIPT_1 | built | First north-star script: Wasteland | B | mod validation script/trial; world-independent |
| WASTELAND_GPT_ENRICHMENT_1 | validated | Wasteland enrichment (GPT consult 2026-09-30, owner-picked by card): named storms (Deadlight Halo, Cinderwi... | B | biome/mod content at def or map level; carries into a remade world |
| WASTELAND_LIVE_SUITE_FAILS_ACC_BIOMES_1 | proposed | modcheck Wasteland live on acc_biomes-15: 8 FAIL: sloghog/sootgrazer on polluted ground read 'off feed grou... | B | biome/mod content at def or map level; carries into a remade world |
| WASTELAND_MECHANICS_BUILD_1 | validated/blocked | Build the Wasteland mechanics: 20-cell Middenshell on TitanicCreatures, processor gatherable comps, ambient... | B | biome/mod content at def or map level; carries into a remade world |
| WASTE_RUN_SIGNAL_DEBUG_HOOK_1 | validated | Bridge hook to press a Command_Action / send a quest signal so the waste run can be state-read | B | tooling / harness / process; world-independent |
| WASTE_RUN_STUBS_1 | proposed | Waste run stubs: propane war-lab breach (needs ANCIENT_WAR_LAB_1), Slime world effects, flight-to-destinati... | B | biome/mod content at def or map level; carries into a remade world |
| WATER_DEPTH_RESKIN_HE_LOOKS_FIRST | proposed | New art per ruled depth spec §4: wall-edge depth band overlay on wet canals (gap between water and lip) and... | B | art for our own defs; unaffected by the remake |
| WATER_LEDGER_DOUBLE_CHARGE_1 | built | Stillsand: Still water is booked to the ledger twice | B | framework mechanic (map level); carries over unchanged |
| WATER_LEVEL_BUILD_DECILITRES_NOT_NOTCHES | built | Plan P3: level-surface solver (flowworks_level_surface_2026-10-17.md Option 1): each connected body holds e... | B | framework mechanic (map level); carries over unchanged |
| WATER_SCENES_S5_JUDGE_THIRD_DRAFT | proposed | Owner: approve scene S5 redrawn a third time with exactly-level numbers (plan P10; one surface per body, li... | B | framework mechanic (map level); carries over unchanged |
| WEATHERSUITE_DEPLOY_MAST_LEAVES_THE_BUILDING | proposed | At next game-down window: deploy WeatherSuite (mast def deleted, rebuilt DLL c89d78695) via deploy_custom_m... | B | biome/mod content at def or map level; carries into a remade world |
| WEBWORK_DEAD_GIANT_BUILD_1 | built | Webwork giant: wrapped urraveth skeleton, read bone by bone, loaded bones creak and collapse | B | biome/mod content at def or map level; carries into a remade world |
| WEBWORK_EGG_BROKER_CHANNEL_1 | doing/blocked | Add the egg black-market broker channel as a Bazaar tab, once Bazaar has tabs | B | biome/mod content at def or map level; carries into a remade world |
| WEBWORK_EGG_WEAPON_VERSION_1 | proposed | Future: free-form egg-planting sabotage weapon (mechanism A hatcher-variant, must re-answer the farm ban) -... | B | biome/mod content at def or map level; carries into a remade world |
| WEBWORK_FELLED_NOON_RITE_1 | proposed | Rite: The Felled Noon for Sh'kaar (found in Webwork; fell tallest tree at noon, owners gather at shade line) | B | content/design at map or def level; survives the remake |
| WEBWORK_FIRST_SCRIPT_1 | validated | First north-star script: Webwork | B | mod validation script/trial; world-independent |
| WEBWORK_TERRAIN_WEATHER_PASS_1 | proposed | Design sitting: the Webwork's signature terrain (silk-carpet floor, gutters) and weather (hard sun for the ... | B | biome/mod content at def or map level; carries into a remade world |
| WEBWORK_TRACTION_LANCE_BUILD_1 | validated | Traction lance: capstan sibling on one shared pull, learnable at Webwork or Sump, fabric tether | B | biome/mod content at def or map level; carries into a remade world |
| WEEPINGSTONES_CONDENSER_QUESTS_1 | built | Walking condenser quests: Hutt capture for the Arena, or Moisture Farmers keep it free vs Blackstar fame hu... | B | content/design at map or def level; survives the remake |
| WEEPINGSTONES_HANDLER_VANISHES_1 | proposed | WeepingStones L2: every chain-spawned pawn (handler + target) left AllPawnsSpawned during forced jobs (13->... | B | biome/mod content at def or map level; carries into a remade world |
| WEEPINGSTONES_NET_FLEEING_FLIER_1 | proposed | NET job cannot catch a wild skarrin: it flies off-map before the handler arrives | B | biome/mod content at def or map level; carries into a remade world |
| WEEPINGSTONES_NET_TARGET_FLEES_1 | proposed | Weeping Stones NET: wild skarrin outruns the handler and leaves the map before the 200-tick net finishes - ... | B | biome/mod content at def or map level; carries into a remade world |
| WEEPINGSTONES_REFUSED_TOLL_RITE_1 | ready/blocked | The Refused Toll, for Mob'Unloo: draw at an Imperial metering station and walk away unpaid | B | content/design at map or def level; survives the remake |
| WEEPINGSTONES_SETTLED_FOLLOWUPS_1 | proposed | Weeping Stones: Vellak description after art, 5 catches waiting on their creature, huldu fur question | B | biome/mod content at def or map level; carries into a remade world |
| WEEPINGSTONES_STOCK_JOB_LOOP_1 | built | WeepingStones: bland colonists restart RM_StockPoolPen up to 10x per tick (JobGiver_Work) and the stock/net... | B | biome/mod content at def or map level; carries into a remade world |
| WEEPING_STONES_FIRST_SCRIPT_1 | built | First north-star script: WeepingStones | B | mod validation script/trial; world-independent |
| WETBULB_FOLD_INTO_HEAT_1 | validated | EH-1 (card ruled FOLD): wet-bulb feeds vanilla heatstroke; retire RM_WetBulbOverwhelm/RM_WetBulbProtection;... | B | biome/mod content at def or map level; carries into a remade world |
| WET_FOXHOLE_BUILD_COLD_FEET_SHAKY_AIM | proposed | Standing in water costs: -15% aim chest-deep, wet pawns colder, swimmers cannot fire, downed-drowning warni... | B | biome/mod content at def or map level; carries into a remade world |
| WILDSTEAM_EGG_BOUNTY_FIRST_SCRIPT_1 | built | First north-star script: WildsteamEggBounty | B | mod validation script/trial; world-independent |
| WORN_DARKNESS_PROXY_POSITION_1 | built | LuminousPigment: Darkness test should subtract our light at the proxy's real cell | B | biome/mod content at def or map level; carries into a remade world |
| WOUNDLINK_INJURY_IDENTITY_1 | built | CreatureBehaviors: Wound link should mirror the injury this hit made, onto the matching body part | B | biome/mod content at def or map level; carries into a remade world |
| WRECKED_DISTILLATION_MODULE_1 | validated | WreckedMachines ship Distillation module: clean water from distillable rows (not oil), rate per repair tier | B | biome/mod content at def or map level; carries into a remade world |
| WYYYSCHOKK_FANG_PENDANT_1 | validated | Wyyyschokk fang pendant: hunt trophy apparel, bravery social thoughts with Wildsteam/Blackstar/Deep Tribe (... | B | biome/mod content at def or map level; carries into a remade world |
| XENOTYPE_CANON_CORRECTION_1 | doing | Nine patterns of xenotype defs disagreeing with canon, found by the species library - wrong-species namers,... | B | biome/mod content at def or map level; carries into a remade world |
| ZERSIUM_FORGE_BIOME_1 | built | Zersium mineral lives in the Forge biome: RSW_Zersium def, mineable deposit in TheForge (src/RimMandrake/Th... | B | biome/mod content at def or map level; carries into a remade world |
| ZRRIK_VAMPIRIC_STAB_REBUILD_OWN_BLOODLUST | proposed | RM_Zrrik's vampiric stab heals the attacker again, in our own C# (AA DamageWorker_Vampiric retired 2026-10-18) | B | lost AA mechanic: restore after |
| ZUURRIK_GROWTH_BY_FEEDING_1 | built | Stillsand: Zuurrik fatness grows from blood seen at wake, not what it ate | B | biome/mod content at def or map level; carries into a remade world |
