# RELENTLESS_ENFORCE_BOXRUN_EXAM_DISPUTE

## spec

Flip the three shadow-mode gates to enforce once their own shadow data agrees: WP-07 boxrun (relentless_boxrun.json, mode=shadow), WP-03 exam (relentless_exam.json; 30-item shadow sample not yet collected, accrues from new first contracts once the books clone pulls d05b6069efcb) and WP-08 dispute (arbiter launch is WP-08's). Criteria are the sample counts in redesign_final.md: exam shadow on >=30 items with exam existing before first edit, boxrun/dispute reading with 0 disagreements against what the builder's own contract/arbiter did. Flip one at a time, each its own landing with a selftest run.

Done when: each of the three config files reads mode=enforce, each flip citing the shadow reading (count, 0 disagreements) in its commit, and the matching selftest plus run_selftests --only relentless green after the flip.

Source: /mnt/d/ClaudeWork/rimmandrake/conductor/redesign_2026-11-06/stage4_log.md WP-07/WP-03/WP-08 lines; /mnt/d/ClaudeWork/rimmandrake/conductor/redesign_2026-11-06/redesign_final.md rows 03, 07, 08
