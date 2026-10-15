# Review: modset_builder.py + selftest_modset_restore.py (full-file)

Reviewer: BENCH independent review, 2026-10-15. Subject: c4cbb5c66c (MODSET_MARKER_REPAIR_RESTORES_YESTERDAY), self-marked CLEAN.
Scope: every line of both files, focused on whether --restore / --restore-full / --tier --apply can write anything but the owner's list, or destroy the before-copy.

## Verdict
DEFECT FOUND, fixed, re-reviewed: CLEAN.

## Findings
1. **DEFECT: `restore_before` never checked the live file.** c4cbb5c66c taught `take_before_copy` to refuse when a stale
   marker meets a live list that is neither the tier list nor the before-copy, but `--restore` itself still copied
   the before-copy blindly. Repro: swap (OWNER_V1 -> TIER_A), owner restores a NEWER list by hand (OWNER_V2) and the marker
   stays behind, `--restore` -> OWNER_V1 written over OWNER_V2, "verified", marker consumed. That is "restores yesterday",
   still reachable through --restore. Confirmed against the HEAD code in a scratch copy.
   Fix: write only when live == marker `tier_md5`; live == before-copy clears the stale marker and writes nothing;
   anything else (including an old marker with no `tier_md5`) refuses with the manual path named.
2. Minor, fixed with it: a non-dict marker (`[1]`) raised an uncaught TypeError in restore_before (no write); now refused.
3. Checked, no defect: --restore-full is explicit by design and clears the marker; --tier --apply mid-swap keeps the
   original before-copy, garbled/missing/changed before-copy refuses, crash between write_config and record_tier_written
   leaves a marker without tier_md5 (now refused by both paths, manual copy named); a fresh swap overwrites
   before-tier-<tier>.xml only when no swap is active; game_running and bridge gate precede every write.

## Selftest
`src/RimMandrake/Utils/selftest_modset_restore.py`: OK after fix (temp dirs only); the 3 new cases fail on HEAD code.
