# RIMMANDRAKE_REVIEW_GRAFFITI_SOURCE_THIRTY_SEVEN_FILES_DIRTY

Found by the Stage 2 preflight of Graffiti 0.1.0 (steward run RIMMANDRAKE_STEWARD_GRAFFITI_PREFLIGHT_STAGE, 2026-11-15); table `design/concepts/Graffiti/version/test_table.json`, record `design/concepts/Graffiti/version/preflight.json`.

## spec
ship_check's review clause reads 37 Graffiti files not CLEAN under `code_review_status.py` (e.g. Source/AutoCleanProtection.cs, Source/Designator_PaintGraffitiMark.cs). Full-file reviews, fixes, then `mark-clean`. Stage 3 (offline build) work.

## verify
Acceptance test: `python3 src/RimMandrake/Graffiti/ship_check.py` prints no `FAIL review` line (watched failing 2026-11-15: `FAIL review 37 files, not CLEAN`). Expected: the review row ok.
