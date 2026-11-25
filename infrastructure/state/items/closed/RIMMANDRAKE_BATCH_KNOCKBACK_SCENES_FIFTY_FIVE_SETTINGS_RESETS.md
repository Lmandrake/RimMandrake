## spec
Explosive Knockback (Design Version 0.1.0). Rank 9 of the costly-acts study (`design/specs/2026-11-23-costly-test-acts/analysis.md` sections 6 and 9; item RIMMANDRAKE_CENSUS_COSTLY_TEST_ACTS_REPEATED_HE_SAW_SHIP_FLY). Test-harness change only: no mod bar moves.

**Measured:** the small-list rerun after visit 5 ran 55 scene processes, 11.8 s start to start, 9.0 s each (median). Each process snapshots every setting, resets, and restores them: 96 `mod_settings_field` calls a process, 187 s in all; process gaps about 150 s. About 5 min saved: [guess ~60%]. One load, one map, 55 scenes is a good shape already; only the process start and the settings set repeat. The runner takes a comma list: `src/RimMandrake/ExplosiveKnockback/knockback_runner.py --scenes a,b,c` (it prints one verdict per scene). The table `design/concepts/ExplosiveKnockback/version/test_table.json` has 55 stage-6 checks that each name one runner command (80 scenes in all; sc_walk_blasts is another script). The driver `design/concepts/ExplosiveKnockback/version/in_game/visit_5/scripts/batch.py` runs one command per check and reads one `VERDICT`; to share a process it must read each scene's own verdict line, and a crash of a group must not lose the other groups (the study: "one crash loses the group; each scene still prints its own verdict").
Groups: scenes with the same --ticks, --real-seconds and list note, at most 10 per process (our own rule, the study's "8 to 10"): 13 keys, 17 processes.

**Recommendation: Polish list** (about 5 min per visit, guess; Knockback is also switched OFF in the pipeline). The Conductor decides.

## verify
Acceptance test: `bash infrastructure/state/items/RIMMANDRAKE_BATCH_KNOCKBACK_SCENES_FIFTY_FIVE_SETTINGS_RESETS.acceptance.sh`
- Counts distinct runner commands among stage-6 checks against the group-of-10 limit, and checks all 80 baseline scenes (read from the table on 2026-11-24) are still in some command. WATCHED FAIL today (2026-11-24): `stage-6 runner checks read 55; distinct processes 55 (limit 17, our own rule: groups of 10); baseline scenes 80, missing 0`, exit 1. `--selftest` prints SELFTEST OK (4 cases: 12 separate -> red; 10 batched -> green; a scene dropped from the batch -> red; empty table -> could not look). Watched green.
- Expected on a correct result: exit 0 with `distinct processes <= 17`. It does not prove each scene still prints its own verdict through batch.py: UNRUN live (a rerun on ArchSmall must give 55 rows from <= 17 processes with the verdicts of the last full rerun, 54 checks).

## criteria
- The acceptance script exits 0 and batch.py yields one row per check from a shared process.
