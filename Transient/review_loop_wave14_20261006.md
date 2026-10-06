# Review loop wave 14 (2026-10-06), FOUNDRY, offline
Selftest: Utils/artpipe/selftest_artpipe.py passes after edits.
- artpipe/common.py: CLEAN, marked. Reachable: imported by artpiped/fill_queue/artreg.
- artpipe/requeue_quota_failures.py: CLEAN, marked. Reachable: docstring CLI. Minor: unparseable manifest skipped silently (counted in "examined").
- rimflow/priority.py: CLEAN, marked. Reachable: cli.py `from . import model, priority, probe`.
- artpipe/artreg.py: FIXED, left DIRTY. status/render/backfill on an absent state dir read as an empty registry ("targets: 0", "manifests_scanned 0 MEASURED"); now state_dir.require().
- artpipe/fill_queue.py: FIXED, left DIRTY. `sorted()` over row keys crashed with TypeError when a CSV row had more cells than header (DictReader keys surplus under None), killing the whole file; keys now str().
- artpipe/build_flora_legibility_sheet.py: FIXED, left DIRTY. Absent state dir printed "flora rows (MEASURED): 0" and wrote an empty sheet; now require(). Template without CONFIG/ITEMS script blocks silently shipped unfilled; now refuses.
- rimflow/live_proof_lint.py: FIXED, left DIRTY. Sweep treated an unreadable commit body (no sha / not in clone) as "no debt"; now prints the unreadable count (46 of 1850 closes right now).
- FINDING (unfixed, owner/daemon call): artpiped._job_art_info and the sheet builder classify by `job.get("art_class") or job.get("drawsize")`; fill_queue ALWAYS writes drawsize, so any fill_queue job without an explicit art_class is "creature" and never reaches the flora exemption or the backfill. Only art_class-bearing or pre-fill_queue jobs classify as flora.
- FINDING (unfixed): artpipe/requeue_flakes.py json.loads of a manifest/job is unguarded (one bad file aborts the pass), and `require()` checks done/ only so a missing pending/ fails at rename.
- No dead-file candidates among these.
