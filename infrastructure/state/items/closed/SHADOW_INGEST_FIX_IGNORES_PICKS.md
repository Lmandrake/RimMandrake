# SHADOW_INGEST_FIX_IGNORES_PICKS

## Defect
`src/RimMandrake/Utils/art_eval/shadow.py ingest` (209-264) reads only `q.pipeline_check`. On owner_escalations
sheets he picks columns and never clicks the shadow buttons, so ingest logs 0 rows and
`infrastructure/state/art_eval/shadow_log.jsonl` does not exist at all: `shadow.py status` (the turn-off streak)
has never seen a verdict. Both leaningscrub sheets (2026-10-24) were fed back by hand as CL-012..CL-025.

## Fix wanted
Ingest derives KEEP/OVERRIDE from his picks when q is empty: picked letter == pipeline ACCEPT => KEEP, a picked or
kept picture the pipeline REGENed => OVERRIDE (rejected good), a purged picture the pipeline ACCEPTed => OVERRIDE
(passed bad); qPrefill never counts. Selftest on the leaningscrub_1 decisions file.
Evidence: enact dry runs /home/mandrake/.seat-tmp/FOUNDRY/ls1_enact_dry.txt, ls1_enact_apply.txt; verdict dump ls1_verdicts.txt; sheet Transient/biome_ffar/owner_escalations_leaningscrub_1_sheet_2026-10-24.decisions.json; run infrastructure/state/art_eval/runs/owner_escalations_leaningscrub1_20261024/.
