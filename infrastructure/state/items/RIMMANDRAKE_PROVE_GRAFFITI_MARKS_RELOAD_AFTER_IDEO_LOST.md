# RIMMANDRAKE_PROVE_GRAFFITI_MARKS_RELOAD_AFTER_IDEO_LOST

Found by the Stage 2 preflight of Graffiti 0.1.0 (steward run RIMMANDRAKE_STEWARD_GRAFFITI_PREFLIGHT_STAGE, 2026-11-15); table `design/concepts/Graffiti/version/test_table.json`, record `design/concepts/Graffiti/version/preflight.json`.

## spec
Test H1_IDEO_RELOAD in the table, specified at Stage 2, built at Stage 3 (red first). Observes: after the colony's ideoligion is removed, a save reloads with 0 Graffiti reference errors (held walk defect #1: rmMarkMakerIdeo, Filth_Mark.cs:297)
File: `src/RimMandrake/Graffiti/validation.py`. Reads: src/RimMandrake/Graffiti/Source/Filth_Mark.cs

## verify
Acceptance test: none offline, a live test (the game decides it: Scribe reference resolution on save and load is engine behaviour over a live world's ideoligion list; no offline model of Scribe_References exists to decide it). Command when built: `bridge: validation.py scene_ideo_removed_save_reload`; recorded UNRUN until run.
