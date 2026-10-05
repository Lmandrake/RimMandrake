# Hose carry S5 report (settings + review stations)

## Status
- started
- 23:5x CR7 + devmode probe verb written
- 00:0x stations 43-47 + REGION2 widened to z118 (strip 118-139) + hooks; --plan layout ok
- 00:1x HoseSettings rows + HoseJobTuning -> properties; building
- built OK, selftests 646/646 + review 28/28; run_selftests running (bg)

## Result (S5)
- run_selftests 177/179: northstar_matrix/selftest.py (known Transient-PNG failure) and UtinniPatches selftest_utinnipatches_dump.py (not touched by S5).
- Files: HoseSettings.cs (handlingTime 0.25-3x, windCellsPerSecond 1-8, autoResumeDroppedHose; reset + Scribe), JobDriver_CarryHoseEnd.cs (HoseJobTuning now reads settings), HoseProbe.cs (+devmode verb for CR7), validation_hose.py (CR7), human_review.py (stations 43-47, REGION2 widened to z118; carry hooks), selftest_human_review.py (28/28).
## Owed
- "Show the route and length while choosing where to deploy" setting NOT added (nothing draws a route preview yet; a dead toggle would lie).
- Live: --carry CR7 and review map stations 43-47 unrun; deploy needed.
