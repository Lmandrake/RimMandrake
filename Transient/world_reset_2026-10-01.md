# Saved bland world + world_reset (2026-10-01)

Owner: stop re-cleaning a dirty world and stop the naming dialogs. Build a bland world ONCE, name it, save it, LOAD it between suites.

- New bridge tool `jawa/name_colony` (`src/RimMandrake/bridgetools/JawaBench.BridgeTools/JawaBenchColonyNameTool.cs`): sets `Faction.OfPlayer.Name`, `Settlement.Name` and `namedByPlayer` (what the dialogs' OK does), so `Faction.FactionTick` (TicksGame % 1000 == 200) never raises them. Built with `build.py --gm`, NOT deployed (game was up). Deploy needs the game closed.
- `src/RimMandrake/Utils/modcheck/saved_base.py`: `induce_and_finish_naming`, `save_base` (backs up Saves, proves a NEW file and no changed existing save), `world_reset` (load `BLAND_NORTHSTAR_BASE`, then assert_bland; fallback `cleanup`), `cleanup`.
- `live_queue/j6_bland_base.py` (J6): the one-time live creation script = J3 recipe + naming + assert_bland + save. Ready, NOT run live.
- Selftest: `python3 src/RimMandrake/Utils/modcheck/live_queue/selftest_live_queue.py` 33/33; rimdrive selftest 21/21.

UNVERIFIED live: tool `jawa/name_colony` (needs deploy + game restart); `rimworld/load_game_ready` as a mid-session reset; `destroy_batch categories=Corpse,Filth` in the fallback; fallback cannot remove extra colonists (no verified tool, reported as a problem).
