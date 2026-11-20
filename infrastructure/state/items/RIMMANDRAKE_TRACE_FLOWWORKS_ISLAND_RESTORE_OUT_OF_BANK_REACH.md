# RIMMANDRAKE_TRACE_FLOWWORKS_ISLAND_RESTORE_OUT_OF_BANK_REACH

Road-back item for FlowWorks 0.1.0 after in-game visit 2 (design/concepts/FlowWorks/version/in_game/visit_2/SUMMARY.md, rows.jsonl), filed by the steward run RIMMANDRAKE_ROUTE_FLOWWORKS_VISIT_TWO_FAILURES_BACK. It takes over RIMMANDRAKE_FIX_FLOWWORKS_ISLAND_RESTORE_NEEDS_BRIDGE_FIRST (filed by the visit driver; superseded by this filing so the maturation tick, which launches fixers on items caused by the steward run, finds it). Its prose stays in items/closed/RIMMANDRAKE_FIX_FLOWWORKS_ISLAND_RESTORE_NEEDS_BRIDGE_FIRST.md. Lowest stage that shows the fault: Stage 6 only (game-only).

## spec

Steward class: REAL MISS, cause unknown (mod or criterion).

sc_hung_bridge FAILed on SB_islands_restore_reach (design/concepts/FlowWorks/version/in_game/visit_2/evidence/sc_hung_bridge_20261119T215759.json): outcome needs_bridge_first, 'a colonist on the bank cannot touch the mid-channel square (canReach=False)', hasJobOnCell True, RM_FillInCanalJob. The claim: 'a colonist reaches a mid-channel dug square and Restore grounds it'. Not decided: a mod fault (Restore should be reachable from the bank, or give a reachable job) or a row that asks for an impossible reach (then a CRITERION FLAW: refusal record and re-pin, or his card if the bar's words must change). Visit 1's run of the same script read 9 rows, none FAIL; this row is new since.

## verify

Stage 6 check: sc_hung_bridge, `python.exe src\RimMandrake\FlowWorks\northstar\suspension_bridge_proof.py <out>  (entry posts; bridge held, flowworks tier)`.
Acceptance test: none offline, the cause is known only from a live experiment (no fake models it); the live row above is the test.

## refs

file: src/RimMandrake/FlowWorks/northstar/suspension_bridge_proof.py

## criteria

- SB_islands_restore_reach reads PASS on the mod's behaviour, or the row is shown to demand an impossible reach and goes the criterion-flaw road.
