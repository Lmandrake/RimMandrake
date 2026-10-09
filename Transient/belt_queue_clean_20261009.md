# Queue clean 2026-10-09 (FOUNDRY helper)

Plan: oldest-first batches of ~15; classify built/dropped/dup/stale; close w/ cited evidence.

## Batches
Candidate shortlist (verify each against src/ + git log before close): SEA_DIVE_HATCH_REMOVE_1, BIOME_DEFNAME_MIGRATION_WAVE_1, WARLAB_CRATER_ACCIDENTAL_TRIGGER_1, FLOWWORKS_*_SHIP/GREEN, STILLSAND_*, plus proposed/offline items filed 2026-10-04..08.
Sanity probe: defName set from src xml = 12130 names; RM_Fessk present.

## Results (2026-10-09)
- Triage population: 311 distinct FOUNDRY items in proposed/ready/doing (217 proposed/ready, rest doing). 569 headings in the queue view duplicate across sections.
- Finding: the queue is overwhelmingly LIVE. 2026-10-07..09 items (~130) are fresh GPT-review/modcheck findings with 0 fixing commits; older ones are owner-gated, bridge-gated or partial builds.
- CLOSED SUN_SPHERE_GRAZE_PERSIST_1 at 2f40b54d9 (tb.graze Scribed subtraction in RM_MapComponent_GlowGraze.cs; live check owed under LIGHT_LEDGER_ONE_1 A2).
- SUPERSEDED SEADIVEHATCH_CACHES_FIRST_SEA_FLOOR_1 by SEA_DIVE_HATCH_REMOVE_1 (owner ruling in item: layer replaces pocket maps; SEABED_PLANET_LAYER_1 closed 0e1bba537).
- KEPT after check: SKETTO_FLIGHT_DRAWSIZE_FIX_1 (RSW_Sketto.xml:182 still 1.0), WARBLING_GLOW_BASELINE_1 (colour still overwritten, only radius moved to ledger), MYNOCK_FLIPBOOK_FRAMES_1 (no frames), TWILIGHT_WELL_LIGHT_STATE_1 (half done, open ruling), JAWABENCH_DESTROY_PAWNS_1 vs DESTROY_BATCH_NEVER_KILLS_PAWNS_1 (overlapping, not identical: tool vs callers; left).
- Observation: HUGE_THINGS_FOOTPRINT_1 prose says "Built 2026-10-07" but state is proposed (needs `implemented`).
- Sweeps: title-similarity duplicate scan (ratio>0.62) found 0 pairs; stale-block scan (blocker IDs already closed) flagged 5, only one actually dead (above).
