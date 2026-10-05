# DEF_DUMP_RECAPTURE_1 notes (2026-10-05)

- Selftest `src/RimUtinni/UtinniPatches/selftest_utinnipatches_dump.py` reads the capture at `GP.DEF_DUMP` (DefDump/captures/2026-10-04T17-39-06Z, 638 mods). It FAILS (4) on defs_vs_dump_static labels (Landopus->thraia relabel).
- refresh.py has NO capture mode: --offline/--patches/--fingerprint only; the dump is produced by a FULL GAME LOAD with DefDump/dump_request.txt armed (~15-25 min on the 638-mod list). --freeze is owner-only; not needed.
- Fingerprint now: live ModsConfig = 50 mods (minimal list), 0 missing. A full-list load means swapping ModsConfig.
- Bridge at 2026-10-05T21:2x: HELD by FOUNDRY "flowworks northstar" (idle 0 min); game NOT running. Taking it / swapping the list would clobber that run, so NOT taken.
- NEXT: when bridge is free, modset_builder full tier -> arm dump_request.txt -> launch -> harvest -> run_selftests.py 181/181 -> close with sha.
