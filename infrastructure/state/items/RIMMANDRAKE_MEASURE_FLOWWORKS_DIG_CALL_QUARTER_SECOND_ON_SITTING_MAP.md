## spec
found-by: FlowWorks in-game visit 3, 2026-11-21 7:07-7:26 AM PST, game a, evening_20261113 list (23 mods), SITTING_20261114_PIT_FIXES (250 x 250).
big_pit_scene `stage` digs 8 copies of a 16 x 16 pit (8 notches) cell by cell with jawa/flowworks_excavation_drive. Bridge call log
(D:\ClaudeWork\rimmandrake\scratch\bridge_calls.jsonl, pid 23240, 15:15:16-15:15:18Z): about 4 dig calls a second, ~250 ms each, so
~2,000 digs did not finish in 530 s, twice. The resume step then dug the last 97 cells at ~43 ms a call, and on the 13-mod calm site
the same call takes ~41 ms (sc_hung_bridge: 393 calls, 16.1 s). Unexplained: what costs ~200 ms more per dig while the dug body grows.
If a colonist's dig completion pays the same main-thread cost, a player digging a large pit on a big map sees a hitch per cell.
Not measured: the cost inside the game per completed dig (the bridge time includes the main-thread wait).

## verify
- jawa/map_comp_timing (or a stopwatch read) around one dig completion on a 250 x 250 map with a 2,000-cell dug body, against a fresh map.

## criteria
- A1 L2: the per-dig cost on the grown body is measured and stated in ms, with the control.

Acceptance test: none, a measurement item (its result decides whether a perf ticket follows).

## refs
file: src/RimMandrake/FlowWorks/Source/RM_MapComponent_Excavation.cs
