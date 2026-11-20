# RIMMANDRAKE_FIX_FLOWWORKS_ISLAND_RESTORE_NEEDS_BRIDGE_FIRST

Caused by RIMMANDRAKE_DRIVE_FLOWWORKS_IN_GAME_VISIT_TWO (FlowWorks 0.1.0, in-game visit 2, game a, flowworks tier).

## spec

sc_hung_bridge FAILed on SB_islands_restore_reach (design/concepts/FlowWorks/version/in_game/visit_2/evidence/sc_hung_bridge_20261119T215759.json): outcome needs_bridge_first, 'a colonist on the bank cannot touch the mid-channel square (canReach=False)', hasJobOnCell True, RM_FillInCanalJob. The claim: 'a colonist reaches a mid-channel dug square and Restore grounds it'. Not diagnosed in the sitting (bound): MOD (Restore should be reachable from the bank or give a reachable job) or a row that asks for an impossible reach. Visit 1's run of the same script read 9 rows, none FAIL; this row is new since. Other rows UNMEASURED (owed by the script itself).

## verify

python.exe src/RimMandrake/FlowWorks/northstar/suspension_bridge_proof.py <json>: SB_islands_restore_reach PASS

## criteria

Acceptance test: none offline, the cause is not known; live: the sc_hung_bridge row.
