# walks2_log -- water_scenes_walk.py: shelf off + "pristine = nothing dug" (FOUNDRY offline helper, 2026-10-18)
Scratch clone /home/mandrake/rm/scratch/FOUNDRY/walks2 (base 6902efb9a). No bridge, no game.
- [x] deepBedsEnabled pinned off from staging to end of each scene run (do_scene wraps _do_scene in try/finally; previous value restored, also on BaseException); SHIPPED (restore verb) now carries deepBedsEnabled True. P11_FLOOR_ON_PAINTED_PONDS stays the owner's; scenes are independent of it.
- [x] The walk had no zero-bodies precondition; prep now prints "pristine" = excavatedCellCount==0 and superdeepCellCount==0, bodies printed not required 0.
- [x] S5 a/b/c/h/i vs level_solution with shelf off: unchanged and consistent. Ponds are WaterDeep painted = 4 levels (-2.0 m), canals -0.5 m (F canal -2.0 m); TOT_A 36 / TOT_B 4 levels are the unshelved stocks. With the shelf ON the pond stocks would be smaller, which is what the pin avoids. Not re-run live (no bridge).
- [x] selftest_water_walks (3 new pin checks) and selftest_fw_walks green under run_selftests.py.
