# belt selftests 20261005
Full run_selftests.py: 180/181 pass. Earlier-reported art_checks, render, rimflow, label_collision, mandrakepatches, starwarspatches all PASS now (art_checks re-run alone: all checks passed).
Only failure: src/RimUtinni/UtinniPatches/selftest_utinnipatches_dump.py. JOE_Landopus label is 'thraia' in XML (renamed at 3386d6d44, 2026-10-04 23:19 PDT) but the def dump
(DefDump/captures/2026-10-04T17-39-06Z, earlier) still says 'landopus'. Stale instrument, correct checker: clears on next dump capture (needs live game; not touched). Test not weakened.
