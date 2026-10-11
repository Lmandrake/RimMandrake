# FOUNDRY art-queue fill, 2026-10-11

Result: QUEUED NOTHING. No genuinely owed, approved art lacks a job. Padding refused.

## Method
Python sweep (sanity probe: RM_Ashwallow_east present in done/, registry hit) of all 1847 prepared job rows
in Transient/**/*.json (rows with prompt+canvas_w) against ids in D:\Luke\dev\_artpipe done/active/failed/pending/_withdrawn
and registry.jsonl. facings in these files are often a comma STRING, split before matching (first pass
mis-reported 28 unmatched for that reason).

## Unmatched rows
Only 5: Transient/sketto_pilot_2026-10-08/stage2_plates_wings_v2.json (RSW_Sketto wing plates, superseded pilot
iteration, not an owed commission). Not queued.

## Texture-gap allowlist (src/RimMandrake/Utils/art/texture_gap_allowlist.json), 11 MISSING entries
Already generated, awaiting install/pick, not queue work: CrawlSmear (gap_RM_CrawlSmear), RM_Dakkra_rest,
AssayFlecks Light/Heavy, 5 Dewfall *_dew (gap_RM_Dewfall_*), KOTOR_SmallCrystal (gap_KOTOR_SmallCrystal_a),
Swarmling (rot_swarmling_v2, miasma_swarmling_green_v2/v3), Ismerrow (miasma_ismerrow_a: needs his confirm),
Braskeen (v2 renders await his pick after REDO ruling). Ashwallow/Emberscythe (PYRELANDS_SHIP_READINESS_1): done and wired.

## Failed jobs
requeue_quota_failures --dry-run: 0 of 391; requeue_flakes --dry-run: 0 (2 master_still_failed, by design).

## Owed but NOT fill_queue work
DESERT_WRAPS_ART_COMMISSION_1: 17 cells (13 Draped wrap + 4 desert_nomad head north/east), owner-approved, but
produced by its own magenta-key + process_matrix pipeline under src/RimStarWars/Armoury/_artsrc/desert_wraps_candidates_2026-09-09/work/
(gen_matrix_parallel.py). Not routed through the art ledger; filing it as plain jobs would skip the conform step.
COMMISSION_LEDGER_CLEANUP_1 (85 slugs): owner-graded in, but no defs/concept briefs yet; art is not yet owed.
