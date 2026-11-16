# RIMMANDRAKE_BIND_CERTIFICATE_TO_OFFLINE_DECIDERS_NO_OP_PASSED

## spec

Found by the GimmeSomeSlack blind cycle 5 judge (2026-11-16), planting faults into the mod's `version/test_table.json`:
`maturation.py certificate GimmeSomeSlack` stayed OK when (a) bar `no_hose` (proves_at 4-5) had `decides: []` while
`offline_decides` still named T_NO_HOSE, and (b) T_NO_HOSE's command was replaced by `true` after its green stamped run.
`judge_certificate.certify` looped only over `offline_decides` (an offline bar naming none produced no rows and passed),
and `build_id` hashes files, not the command.

Fix (`src/RimMandrake/rimflow/judge_certificate.py`): clause `decided` refuses an offline bar (proves_at 2 or 4-5) with no
offline decider, and an offline decider missing from the bar's `decides`; `run_offline` records `runs_today.command`, and
`ran_on_this_build` refuses a recorded command that differs from the table's. Known limit: a stamp made before this fix
carries no command and is read as before until its next `maturation.py certificate <Mod> --run`; a no-op command that is
itself rerun and stamped still certifies (the build does not know what a test is meant to run).

## verify

Acceptance test: `python3 src/RimMandrake/rimflow/acceptance/guard_certificate_binds_offline_bars_accept.py` prints
`PASS 8/8` (rc 0). Watched fail on the base judge_certificate.py: `FAIL 2/8` (rc 1). Also green after the fix:
`guard_judge_certificate_accept.py` 18/18, `selftest_maturation.py` 0 FAIL; certificates of ExplosiveKnockback,
GimmeSomeSlack, Graffiti, Pyrelands unchanged (OK); FlowWorks refused before and after (stale build stamps, not this).
