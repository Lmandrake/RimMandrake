# RIMMANDRAKE_PROVE_FLOWWORKS_BOTTLE_JOBS_MOVE_EXACT_LITRES

Filed by the detached helper on RIMMANDRAKE_CLEAR_FLOWWORKS_PAPERWORK_TO_GAME_ONLY_ROAD (FlowWorks 0.1.0, the game-only road). Bar `inv_bottles_thirst`; source event `THIRST_GAME_SIDE_NOT_KERNEL`. One ticket per source event.

## spec
Lane 1 of blind cycle 4 left `THIRST_GAME_SIDE_NOT_KERNEL` UNSETTLED (`design/concepts/FlowWorks/version/blind_challenge/cycle_4/lane2/lane1_rows_after_fix.jsonl`): the thirst kernel and `RM_DrinkReserve` pass offline, but no offline test can show that the bottle fill, empty and wash jobs (`JobDriver_FillBottle` and its siblings) move exactly a bottle's litres: a filled bottle takes exactly its litres from the source and gives them back on emptying. `sc_garden` stages only the faucet drink (its header says so).

The scene that decides it: `src/RimMandrake/FlowWorks/northstar/thirst_live.py`, with one row added if it has none: fill a bottle from a tank of known stock, read the tank's stock before and after, empty the bottle into a second tank, read again; both deltas equal the bottle's litres. Run it with the existing bottle rows (T4, T11, T23). The open mod ticket `FLOWWORKS_BOTTLE_FIX_JOBS_VANISH_EMPTY` (a bottle lost when Near placement fails) is on the same jobs: a FAIL there is that ticket's, not this one's.

Acceptance test: none offline, live-game behaviour (the cycle-4 judge recorded that no offline test can show it). The live command is under verify; record it UNRUN with `maturation.py unrun` if the visit does not reach it.

## verify
python.exe src\RimMandrake\FlowWorks\northstar\thirst_live.py (bottle rows) on the minimal flowworks tier, results to D:\ClaudeWork\rimmandrake\evidence\flowworks_visit2\thirst_bottles.json

## criteria
The fill and empty deltas each equal the bottle's litres (row PASS), and T4/T11/T23 PASS or are classed with a cause; the lane-1 row is then settled by that evidence.

## refs
file: src/RimMandrake/FlowWorks/northstar/thirst_live.py
file: src/RimMandrake/FlowWorks/Source/LiquidTypes/JobDriver_FillBottle.cs
file: src/RimMandrake/FlowWorks/Source/LiquidTypes/JobDriver_FillBottleFromTank.cs
file: src/RimMandrake/FlowWorks/Source/LiquidTypes/JobDriver_EmptyBottleIntoTank.cs
tier: flowworks
