# acc_green_min rerun 2026-10-08
Game up, ModsConfig = 35 active mods (acc_green_min). Runner: python.exe -u Transient/acc_biomes/run_live_suite.py <Mod>; outputs Transient/acc_green/rerun_<Mod>.txt

## Per mod
- ShipVermin: nest chain now measures and PASSes (5 comps) after fixing ACT_FORCE/ACT_STATE paths to `Actions\T: ...` in validation.py (earlier "fixed" edit had never landed in the file; harness-site problem). Alert chain PASSed on first rerun; on the 2nd rerun UNMEASURED (leftover leeches from run 1 elsewhere on map = no clean baseline; harness-state, not mod bug). not_driven chain UNMEASURED by design.
