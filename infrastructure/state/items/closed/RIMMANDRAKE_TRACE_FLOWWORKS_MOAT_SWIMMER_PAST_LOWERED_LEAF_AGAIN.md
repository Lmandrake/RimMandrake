# RIMMANDRAKE_TRACE_FLOWWORKS_MOAT_SWIMMER_PAST_LOWERED_LEAF_AGAIN

Road-back item for FlowWorks 0.1.0 after in-game visit 8 (`design/concepts/FlowWorks/version/in_game/visit_8/SUMMARY.md`,
`rows.jsonl`), filed by the steward run RIMMANDRAKE_ROUTE_FLOWWORKS_VISIT_EIGHT_FAILURES_BACK. Design Version FlowWorks
0.1.0 (current; a Problem against the locked bar `moat_raid_sequence`). Lowest stage that shows the fault: Stage 6 only
(game-only): the cause is unknown until a live read.

## spec

Steward class: MOD (the driver's class), cause unknown (mod path choice, or scene geometry).

Visit 8 run 1, 2026-11-23 03:45-03:48 PST, ArchBig, flowworks tier, deployed build 6b52871479
(`design/concepts/FlowWorks/version/in_game/visit_8/evidence/sc_moat_raid_20261123T034521.json`):
`MOAT_control_bridge_down_no_swim` FAIL: `{'swimmers': ['Human24626'], 'crossedToThePlot': ['Human24620', 'Human24634'],
'reachedTheRing': ['Human24613', 'Human24620', 'Human24626', 'Human24634'], 'polls': 2, 'leafDown': True}`.
One of the four raiders that reached the ring swam with the leaf down; two crossed by the bridge. The next 8 counted runs on
the same build read this row PASS.

History: visit 2 saw 2 swimmers with the bridge down; RIMMANDRAKE_TRACE_FLOWWORKS_MOAT_SWIMMERS_ONLY_IN_THE_CONTROL closed
it at eb15c22de9cd as HARNESS (the control watched 3,000 ticks and the raiders wrecked the leaf; the control now ends at the
crossing). This reading has `leafDown: True` and only 2 polls, so the leaf-wreck cause does not explain it [guess ~70%].

The visit-8 row cites RIMMANDRAKE_HOLD_FLOWWORKS_PIT_PRISONERS_THREE_CAPTURE_FAULTS as `filed`, but that item's three
faults are capture faults and do not name this one; this item carries it.

First experiment: in the control run, log each raider's path (`pather.curPath` nodes or destination) and its cell every
poll, and the leaf's deck cells' passability, so the one swim reads as either "the mod gave a swim path a lower cost than
the bridge" (MOD), or "his target or spawn made the swim shorter than the bridge by a margin the game's cost allows"
(SITE: the scene stages the raiders so the bridge is not the obvious route).

## verify

Stage 6 check: `sc_moat_raid`, `python.exe -u src\RimMandrake\FlowWorks\northstar\concept_scenes.py --scene scene_moat_raid --out <json>`
(bridge held, flowworks tier). Acceptance test: none offline, the cause is known only from a live experiment (no fake models
the raid's path choice); the live row is the test.

## criteria

- The swim is explained by a live read (MOD, SITE or HARNESS, with the evidence).
- If MOD: the fix, and `MOAT_control_bridge_down_no_swim` PASS on 5 control runs in a row on the fixed build.
- If SITE or HARNESS: the scene or check repaired, seen red on a planted case and green on the build.
- No locked 0.1.0 bar is loosened or edited by this work.

## refs

file: src/RimMandrake/FlowWorks/northstar/concept_scenes.py
item: RIMMANDRAKE_TRACE_FLOWWORKS_MOAT_SWIMMERS_ONLY_IN_THE_CONTROL
item: RIMMANDRAKE_HOLD_FLOWWORKS_PIT_PRISONERS_THREE_CAPTURE_FAULTS
