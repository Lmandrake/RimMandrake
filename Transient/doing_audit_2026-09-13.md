# Doing-items audit — 2026-09-13 (~09:45Z)

Owner asked: "What about examining the stuck queue items marked doing?"
Method: ledger projection (file-order; an earlier ts-sorted projection double-counted
41 items because same-second start+close pairs sort alphabetically — corrected here),
then three read-only classification passes (legacy seats / stale FOUNDRY / BENCH+OWNER),
verdicts spot-checked against `rimflow show` and real commit shas.

## Headline

- Naive projection said **102** items in doing; the truth is **61**, and of those only
  **21 were genuinely stuck** (dead-session starts, no activity since 2026-09-06..10).
- All 20 legacy-seat (DECIDE/CHECK/BUILD) "stuck" items were already closed or
  superseded — false positives of the sort the ledger's same-second events invite.
- The five DIRTY_CODE_REVIEW_LOOP_RESTART_3..8 entries are handoff markers, each
  superseded by its successor; the standing loop itself is live.

## Actions taken (BENCH, this session)

- ASSIGNMENT_SHEETS_VERDICT_SITTING_1, WORLDMAP_FINAL_REVIEW_1,
  CAMPAIGN_STORY_SITTING_1 → `needs owner` (were stale offline/unset).
- GIZKA_TRIBBLE_ADAPTATION_1, ART_PIPELINE_DAEMON_1, EXPLOSIVE_PLANT_GROWTH_1 →
  audit notes naming their real holds (dependency items, not owner).
- TECHPRINT_FACTION_GATING_1 (OWNER seat, 277h, ruled 2026-09-04 then abandoned) →
  reassigned to FOUNDRY, ready.
- 21 zombie FOUNDRY starts → filed DOING_SEDIMENT_RECLAIM_1 for FOUNDRY (BENCH may
  not reclaim another seat's items; the owner-said route correctly refused a question
  as authorization).

## Per-item verdicts

### Genuinely stuck (21, FOUNDRY) — reclaim list, see DOING_SEDIMENT_RECLAIM_1
| item | last touch | note |
|---|---|---|
| MASS_VALIDATION_LADDER_1 | 2026-09-01 71c5e2110 | offline half only |
| DROID_TILES_SOURED_TERRAIN_1 | 2026-09-08 | blocked on Droidworks Phase 3 prereq |
| INHABITED_STOCK_ONTO_MAP_AND_FATE_1 | 2026-09-09 b9520e45a | fate live-check owed |
| PLOT_MECHANISM_MODS_WAVE_1 | 2026-09-10 39da0b74f | |
| MACRO_GENERATOR_V0_1 | 2026-09-10 | really awaiting owner grade → needs owner |
| MAPGEN_PAINTER_V1_1 / MAPGEN_GL_SHEET_1 / MAPGEN_CONVERGENCE_LOOP_1 | 2026-09-09 805d59838 | the mapgen trio stalled together |
| UNUSED_MUTATORS_WORLD_ASSIGNMENT_1 | 2026-09-06 83d0cfe02 | |
| ANCIENT_WAR_LAB_1 | 2026-09-09 7dfa465e5 | |
| DROID_REPAIR_FOR_PROFIT_EVENTS_1 | 2026-09-09 5edacb132 | |
| ORACLE_CLIENT_CLAUDE_CODE_REWRITE_1 | 2026-09-10 | live-verify owed |
| PITCELL_PRISONER_BED_BRIDGE_GAP_1 | 2026-09-09 | game crashed mid live-proof |
| DROIDWORKS_FORMAT_TIERS_1 | 2026-09-09 63d09a030 | |
| CHRONICLE_NINEFOLD_DECOUPLE_1 | 2026-09-09 | |
| MANYWATERS_COLOR_SUPPORT_1 | 2026-09-09 | mod-activation blocker recorded |
| MOVING_DUNES_BUILD_1 | 2026-09-09 2847f418a | |
| LANDMARK_NAMING_PASS_1 | 2026-09-10 | rename tool bug found |
| OASIS_LANDMARK_PLACEMENT_1 | 2026-09-10 | |
| FISH_BESTIARY_COMMISSION_1 | 2026-09-10 | |
| CRYPTOFORGE_HARVEST_RETIRE_1 | 2026-09-10 | steps 2-3/5 done |

### In progress, leave alone (19+, FOUNDRY) — touched 2026-09-11/12 or <24h
DIRTY_CODE_REVIEW_STANDING_LOOP_1, TILEGEN_SILENT_REUSE_1,
NINEFOLD_DEBUG_GAME_READY_CRASH_1, COLD_LOAD_RUN_SHEET_4, IKEE_MYNOCK_ART_REGEN_1,
BAREHANDED_MELEE_FALLBACK_1 (15/18), GREENTIDE_FISH_ITEMS_FIX_1 (needs bridge proof),
NURSERY_JUVENILES_CRASH_1, WORLDMAP_AUDIT_LIVE_CHECKS_1, MLIE_FAUNA_ABSORPTION_1
(74 left), TILE_STRUCTURE_DESIGNS_1, SETTLEMENT_VERBS_WAVE_1, VAULT_THAW_QUEST_FAMILY_1,
INHABITED_AUGMENTATION_BUILD_1 (14/14 wired), RUST_CATHEDRAL_MECHANICS_1 (6/6 offline),
VAULT_DUNGEON_BUILD_1, SETTLEMENT_VISIT_LOOP_1, DROIDWORKS_WIPE_SEVERITY_1,
SHIELD_MODS_LEVERAGE_1 (needs bridge) — plus everything started 2026-09-12/13 by the
live FOUNDRY window.

### Waiting on the owner by design (BENCH)
WORLDMAP_FINAL_REVIEW_1 (report delivered, wants his read), DUNGEON_SETPIECE_TEXT_1
(second redraft delivered, wants his strike sitting), CAMPAIGN_STORY_SITTING_1
(phase A gathered, phase B is a live sitting), ASSIGNMENT_SHEETS_VERDICT_SITTING_1
(contested-group verdicts want his eyes).

### Already terminal, projection artifacts (no action needed)
All 20 legacy DECIDE/CHECK/BUILD items (each verified closed/superseded with a real
sha — e.g. BRIDGE_TOOLS_MEDIUM_BLOCK_1 d4cad32d, TEMPLATE_FOOTPRINT_IGNORES_SIZE_1
d188a7ea); WEAPONS_ABSORPTION_WAVE_1, GRAFFITI_MOD_EXPANSION_1, WEATHER_SUITE_SLICE_1,
JAWABENCH_COMPANION_NOT_LOADING_1 (db99bf514 "false alarm"),
CODE_REVIEW_STATUS_HASH_REWRITE_1 (9ed835fb), DROID_DONOR_REFGREP_1 (a7dd7782),
COLD_LOAD_RUN_SHEET_1→2, ORACLE_OHM_PROMPT_STILL_SHIP_1 (fc27cbf5),
CRYSTAL_MODS_INGEST_1→CRYSTAL_INGEST_EXECUTION_1, FISH_BY_BIOME_1→
FISH_TYPES_PATCH_BUILD_1, MECHANOID_BIOME_PRESENCE_REVIEW_1→MECH_PRESENCE_ENFORCEMENT_1,
the RESTART_3..8 markers, LIVESTOCK_STARTER_TRIO_1 and FLUID_CANAL_MECHANIC_1 (open
FOUNDRY queue entries, not doing).

### Premise-stale but READY (claim with care)
ANTIQUITIES_TREE_BUILD_1, UI_SHELL_SLICE_BUILD_1 — last real work 2026-09-04/05;
verify the premise before spending a claim (queue-items-decay).

Shelf life ~14 days. Re-derive from the ledger, not from this file.
