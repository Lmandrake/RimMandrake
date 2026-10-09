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
