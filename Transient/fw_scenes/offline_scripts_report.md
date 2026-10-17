# Offline scripts report (FOUNDRY helper, 2026-10-17)

All four files are in `D:\Luke\dev\...` terms under `\\wsl.localhost\Ubuntu\home\mandrake\rm\foundry\src\RimMandrake\FlowWorks\northstar\`. None has touched a game; each runs end to end only on the offline fake (`--mock`).

- [x] fw_walk_common.py: rotation read-back (jawa/list_things), PIL labels (64 px titles), index.html writer (looks right / looks wrong / note per group, localStorage + copy-as-JSON), traceback keeper, bank/ford cell finders, FakeGame.
- [x] objects_sheet.py: groups ladders_lowered, ladders_raised (ProofLadder raise), ladders_autoturn, styles_<tank|tall tank|hose reel|universal pipe> (default + Futuristic/Industrial/Modern/Scrapper), river_weirs (5 styles), river_fords. Output `Transient/fw_scenes/live/objects/`. Runbook line at top of file.
- [x] river_scenes_walk.py: R1 current, R2 ford, R3 wash-off-map, R4 bank weir, R5 sluice box; caption panels; `--prep` runs river_site.py. Output `Transient/fw_scenes/live/rivers/`. Runbook line at top.
- [x] selftest_fw_walks.py: green under run_selftests.py (2.9 s).

## Things the first live run will tell us (guesses made offline)
- jawa/list_things rotation key and position key names are guessed tolerantly (rotation/rot/rotInt/facing; x,z or pos); an unreadable one prints UNMEASURED with the field names seen.
- Fords are laid with set_terrain_batch and read back; if the bridge writes the wrong layer the row says so.
- Weir and sluice box are placed by god-mode build_batch (no PlaceWorker), cells chosen by a Python bank search; the real placement rule is the mod's proofs, shown beside.
- Pawn positions come from the HoseProbe `colonists` list (`pos`); if live gives other keys R1/R2/R3 read UNMEASURED.
- R3 does not read the two letters (the river suite's swept chain does).
