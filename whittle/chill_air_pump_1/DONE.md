# Done claim

- true: **O1 (L0):** DivingInteraction builds; oxygen ledger fuzz and RoomServed units pass; patch matches 1 OxygenPump in Odyssey | evidence: `whittle/chill_air_pump_1/evidence/O1_build.log` `whittle/chill_air_pump_1/evidence/O1_fuzz_oxygen_units.log` `whittle/chill_air_pump_1/evidence/O1_selftests.log` `whittle/chill_air_pump_1/evidence/O1_patch_match.log`
- unseen: **A1 (L1):** OxygenPump def carries RM_CompProperties_ChillAirSupply on the live load | evidence: none fresh; this lane may not load the game (the 2026-10-09 pass was at 8ceac720a and its Transient file is gone)
- unseen: **A2 (L2):** on a Chill floor map, a fuelled stove in a sealed roofed room with a powered pump lights; with the pump switched off it goes dark | evidence: none fresh (live)
- unseen: **A3 (L2):** two pumps in one room; switching one off keeps the room lit, switching both off ends it | evidence: none fresh (live)
- unseen: **A4 (L2):** a pump in an unroofed or edge-touching room oxygenates nothing and says so in its inspect line | evidence: none fresh (live)
- cannot tell: **H1 (L4):** the owner judges power cost and room capacity (PROVISIONAL until then) | evidence: the owner's card ruling of 2026-10-09 in `infrastructure/state/items/CHILL_AIR_PUMP_1.md` (keep 300 W / 60 cells, still PROVISIONAL); no new sitting

## What I'm least sure about
- The new `ReceiveCompSignal` / `PostDeSpawn` room-wide re-count and the load-end refresh compile and follow vanilla's signal
  names (read from source), but have never run in a game. The `PowerTurnedOff` signal fires inside the power net's
  tick; the refresh only edits our ledger and the pumps' PowerOutput, which I believe is safe there.
- The Harmony postfix on `CompLowPowerInSpace.CompInspectStringExtra` (lint_harmony_targets passes) is unseen live.

## What I did not test
Anything live: A1-A4 at the new sha, real power-net behaviour, a wall-hung pump placed by a pawn, save/reload,
settings changed mid-run. Room edits and settings changes still take up to one rare tick (~4 s) to apply.
