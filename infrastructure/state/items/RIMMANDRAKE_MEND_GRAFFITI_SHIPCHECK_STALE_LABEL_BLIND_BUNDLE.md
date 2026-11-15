# RIMMANDRAKE_MEND_GRAFFITI_SHIPCHECK_STALE_LABEL_BLIND_BUNDLE

Found by the Stage 2 preflight of Graffiti 0.1.0 (steward run RIMMANDRAKE_STEWARD_GRAFFITI_PREFLIGHT_STAGE, 2026-11-15); table `design/concepts/Graffiti/version/test_table.json`, record `design/concepts/Graffiti/version/preflight.json`.

## spec
`src/RimMandrake/Graffiti/ship_check.py` refuses two clauses on a sound mod (neutral fixer: a broken criterion, not the mod). Art: it cannot resolve `UI/Designators/RemovePaint` (Designator_ScrubGraffiti.cs), vanilla Ideology art loaded from an AssetBundle, not a loose PNG. Settings: it expects 6 fields and the label "Sacred Marks"; the mod ships 8 fields and labels viewerReaction "Feelings while near a mark". Fix the checker to see bundle textures (see reading-rimworld-graphics) and to read the settings from the source, never loosening what it asks of the mod.

## verify
Acceptance test: `python3 src/RimMandrake/Graffiti/ship_check.py` prints no `FAIL art` and no `FAIL settings` line (watched failing 2026-11-15: rc 1, both lines FAIL); the review clause is the separate item RIMMANDRAKE_REVIEW_GRAFFITI_SOURCE_THIRTY_SEVEN_FILES_DIRTY. Expected: 0 FAIL lines for art and settings.
