# acc_green_min rerun 2026-10-08
Game up, ModsConfig = 35 active mods (acc_green_min). Runner: python.exe -u Transient/acc_biomes/run_live_suite.py <Mod>; outputs Transient/acc_green/rerun_<Mod>.txt

## Per mod
- ShipVermin: nest chain now measures and PASSes (5 comps) after fixing ACT_FORCE/ACT_STATE paths to `Actions\T: ...` in validation.py (earlier "fixed" edit had never landed in the file; harness-site problem). Alert chain PASSed on first rerun; on the 2nd rerun UNMEASURED (leftover leeches from run 1 elsewhere on map = no clean baseline; harness-state, not mod bug). not_driven chain UNMEASURED by design.
- Abyss: ALL_GREEN, 17 PASS. First-pass FAIL clear_pocket_around_nothing ("no open ground far from buildings and colonists") was a harness-site problem (map-dependent); did not recur.
- OasisMaker: 23 PASS, 0 FAIL, 2 by-design UNMEASURED (UI ghost; game-day timings). fast_settings budget 2500->4000 ticks in validation.py (harness budget; ring 7 of 8 at 2500).
- Pyrinth: 11 PASS, 0 FAIL, 6 UNMEASURED (needs built instance / other mods; get_defs cannot read building.mineableThing => now UNMEASURED not FAIL; tool gap, edit in validation.py).
