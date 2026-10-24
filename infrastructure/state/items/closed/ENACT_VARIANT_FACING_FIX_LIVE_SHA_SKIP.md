# ENACT_VARIANT_FACING_FIX_LIVE_SHA_SKIP

Found enacting owner_escalations_leaningscrub_1 (FOUNDRY, 2026-10-24).

## Defect
`src/RimMandrake/Utils/art/enact.py` ~1396-1401: a ticked variant's facing whose sha is already live anywhere is
skipped as "already live". RM_Fuzzrunner variant C (leaningscrub_fuzzrunner_v1) has an east identical to the live
RM_Fuzzrunner_east (2328eb361c), so the plan installs only RM_FuzzrunnerV_C_north/south and adds the
alternateGraphics entry: an incomplete Graphic_Multi (east falls back to another view in game).

## Fix wanted
A variant facing must be written to its own variant path even when the same picture is live elsewhere (copy), or the
whole variant must be refused by name. Never a partial set. Regression: Fuzzrunner C on this sheet.

## State
RM_Fuzzrunner was enacted with `--hold RM_Fuzzrunner` (its purge of B and the variant both wait). Re-run
`art.py enact <decisions> ` after the fix; enact.py is owned by its reviewer, not edited here.
Evidence: enact dry runs /home/mandrake/.seat-tmp/FOUNDRY/ls1_enact_dry.txt, ls1_enact_apply.txt; verdict dump ls1_verdicts.txt; sheet Transient/biome_ffar/owner_escalations_leaningscrub_1_sheet_2026-10-24.decisions.json; run infrastructure/state/art_eval/runs/owner_escalations_leaningscrub1_20261024/.
