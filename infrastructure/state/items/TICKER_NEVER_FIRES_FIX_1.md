# TICKER_NEVER_FIRES_FIX_1 — five comps that never ticked

## what was built
Published 40553e46e. `lint_ticker_compat.py` reports 0 ERROR (was 5).
- `RUT_DyingCreep` (PlantBase, Long): `RM_CompScriptedDieOff` moved from CompTick to CompTickLong, clock steps by `GenTicks.TickLongInterval`. Its only user is this plant.
- `RM_Skylight`, `RM_Webwork_Web`: tickerType Never -> Normal; their comps (WarblingGlow, AdhesiveSlick) self-throttle with IsHashIntervalTick.
- `RM_Webwork_NestWall`, `RM_DryAirBlower`: stay Normal (dormancy/spawner, power/fuel/cooler comps need it); `RM_CompEggClutchRelay` and `RM_CompDryFieldEmitter` now run from CompTick gated on `TickRareInterval`. Each is used only on that one building.

## criteria
- O1 L0: both assemblies build; ticker lint 0 ERROR; selftests (FeverWood settings check was already red from FV-1, unrelated)
- A1 L1: a spawned RUT_DyingCreep spreads and then dies into RUT_DeadCreep filth within its lifetime hours
- A2 L1: an RM_Skylight's glow radius/colour changes between two reads a few hundred ticks apart
- A3 L1: a pawn standing in an RM_Webwork_Web cell gains RM_Webwork_Slick
- A4 L1: a powered, fuelled RM_DryAirBlower suppresses plant growth and repels a wild animal in its doorway arc (RM_MapComponent_DryRooms was deleted by WETBULB_FOLD_INTO_HEAT_1)
- A5 L1: a nest wall with a living Ollathrix places an egg clutch after its relay interval

## verify

Run each criterion at its stated level and record it with `rimflow verify TICKER_NEVER_FIRES_FIX_1 --criterion <ID> --result pass|fail|partial --config <list> --evidence <path>`:
- L0: offline build, selftest/fuzz/lint (already run at implementation).
- L1: one minimal-list load, read Player.log for config/cross-reference errors and the specific line, or one spawn-and-read bridge probe.
Evidence is the Player.log line or bridge read the criterion names; a screenshot is not evidence of state.

### Exact checks 2026-10-09 (acceptance sitting)
- A1 CHECK: No chain or proof hook exists. Raw state read: `jawa/spawn_batch ops="RUT_DyingCreep:<x>,<z>"` on a clear soil cell (defs in `RimUtinni/UtinniPatches/Defs/ThingDefs_Plants/RUT_DyingCreep.xml`; the comp is `RM_CompScriptedDieOff`, lifetimeHours 8, spread over 4 h), advance with `rimworld/step_game_ticks` in chunks and verify with `jawa/time_clock` (ticksGame) that the clock really moved; the tool silently truncates under load, and `jawa/time_set_ticks` does NOT simulate; poll `jawa/list_things defName="RUT_DyingCreep"` and `defName="RUT_DeadCreep"` every ~2500 ticks up to 8 h (20000 ticks) plus margin. Needs the Utinni patch layer active. PASS: DyingCreep count rises above 1 during the first 4 h (it spread), then reaches 0 by ~8 h, and RUT_DeadCreep things (filth) exist where they stood. FAIL: count never rises (the comp never ticks, the original bug), or DyingCreep is still present well past 8 h, or no RUT_DeadCreep appears. A spawn that returns no thing is UNMEASURED.
- A4 CHECK: STALE criterion: `RM_MapComponent_DryRooms` no longer exists. A python sweep of `src/` (.cs and .xml) for `DryRoom` returns 0 hits (the sanity probe on the same walker found 31 hits for `RUT_DyingCreep|RUT_DeadCreep`), and BLOWER_ROOM_COOLER_1 states there is no dry-room state. Do not run it live; rewrite the criterion to the blower comp: `jawa/comp_read thing="RM_DryAirBlower" comp="BlowerRoomCooler"` on a powered, fuelled blower and read the comp's tick fields advancing between two reads 250 ticks apart. PASS: n/a until reworded; the reworded read passes when two comp_read results show a changed tick counter on a powered blower. FAIL: the old criterion cannot pass (no such type): `jawa/type_probe typeName="RimMandrake.EnvironmentalHazards.RM_MapComponent_DryRooms"` returns resolved=false.
