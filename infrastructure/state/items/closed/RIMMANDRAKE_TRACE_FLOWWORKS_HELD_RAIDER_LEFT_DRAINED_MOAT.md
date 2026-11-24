# RIMMANDRAKE_TRACE_FLOWWORKS_HELD_RAIDER_LEFT_DRAINED_MOAT

## spec

sc_moat_raid run T161018 (2026-11-23 16:10 PST, ArchSmall, flowworks tier, FlowWorks f4971d58fa), row MOAT_rim_wardens_not_stabbed FAIL: raider Human21212 (Yttakin Mercenary_Slasher) cut a warden at tick 2599. Read from `design/concepts/FlowWorks/version/in_game/visit_9/evidence/sc_moat_raid_20261123T161018.json` (call numbers in brackets):
- [572] he read `VERDICT Allowed held=True` at 67,62, 4 polls after the sluice opened (water 2.98 m); a raider with climbing gear does not read held, so he wore none [guess ~80%].
- [683] 67,60, water 0.96 m; [689] 67,62, water 0.96 m; [694, 695] he and Human21222 both on 67,63; [699] 67,64, a plot square (undug), tick 2224. The moat is dug 4 m: over 3 m of wall stood above the water.
- [708 on] he stayed on 67,64; he is not in the ring, so neither the drive-off nor the held list read him, and the warden spawned beside him.
- Human21204 went 63,64 then 63,66 in the ring in the same polls: the others moved too and stayed held.
- The raiders outside were vanished at the first held read; no free raider was left to fetch him, the colonist was vanished, no ladder was built by the scene, the leaf stayed raised.
Ruled out so far: none by its own run. Theories: a path already committed when the cell's climb depth fell; a pawn pushed off an occupied square (67,63 held two pawns); a held read that turned false for a while (the drain stage reads held only until the first held poll).
The traced runs after (`moatDrainTrace`, b150bbd9ce) read 1 PASS, and 1 void (host load): not reproduced in 1 of 1 traced opportunities.

## verify

1. `python.exe src\RimMandrake\FlowWorks\northstar\concept_scenes.py --scene scene_moat_raid --out <json>`: the row and the new `moatDrainTrace` (every raider's square and job each 60 ticks of the drain). A run where a raider stands on a plot square (64..71, 64..71) after a held read names his job and the poll before it.
2. Then a C# or live check that is red for that cause.

Acceptance test: none runnable before the cause is known (the fault was seen in 1 of 3 valid runs of the scene this visit); the deciding row is MOAT_rim_wardens_not_stabbed, red on T161018.

## criteria

A raider a moat or pit holds stays in it until a ladder, climbing gear, a carrier or the player takes him out.
