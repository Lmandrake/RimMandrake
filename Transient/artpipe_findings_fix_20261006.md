# artpipe findings fix 2026-10-06 (wave14 follow-up, Transient/review_loop_wave14_20261006.md)

Uncommitted. Selftest: `python3 src/RimMandrake/Utils/artpipe/selftest_artpipe.py` — 3 new tests,
6 checks FAILED before the fix, all checks passed after (rc=0).

## (1) art_class/drawsize classification — FIXED
Intent (comment at artpiped.py LEGIBILITY_BACKFILL, commit 247f7d481 "Daemon routes by class via the
backfill", ART_QUEUE_DRAWSIZE_BACKFILL_1 / FLORA_LEGIBILITY_BAR_1): class comes from the job's
art_class else the backfill's per-stem `class`; drawsize from the job else the backfill. The
`art_class or drawsize` gate conflated the two fields — not an ambiguous design choice, so fixed:
each field now resolves independently in `artpiped._job_art_info` and
`build_flora_legibility_sheet.job_art_info` (ds_source stays "job-field" when the job carries drawsize).
Effect when the daemon is next restarted: fill_queue jobs whose stem the backfill marks flora become
flora-exempt from the creature gate/stroke. Live daemon untouched (old code stays loaded until restart).
Test: test_job_art_info_unset_art_class_does_not_fall_through_to_drawsize.

## (2) requeue_flakes bad manifest aborts pass — FIXED
Unparseable manifest (or derive_from job json) is skipped, counted under skipped["unreadable"], named
on stdout, left in failed/. Test: test_requeue_flakes_skips_and_reports_a_bad_manifest.

## (3) requeue_flakes require() pending/ — FIXED
After require(), refuses (SystemExit) unless failed/ and pending/ both exist. Before the fix the pass
had already parked the manifest when the job rename died — a half-move. Fixed in requeue_flakes.py
only; state_dir.require() unchanged (shared by every reader).
Test: test_requeue_flakes_refuses_without_pending_dir.
