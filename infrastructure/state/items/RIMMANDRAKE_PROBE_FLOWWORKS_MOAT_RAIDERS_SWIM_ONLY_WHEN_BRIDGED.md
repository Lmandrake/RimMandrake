# RIMMANDRAKE_PROBE_FLOWWORKS_MOAT_RAIDERS_SWIM_ONLY_WHEN_BRIDGED

Caused by RIMMANDRAKE_DRIVE_FLOWWORKS_IN_GAME_VISIT_TWO (FlowWorks 0.1.0, in-game visit 2, game a, flowworks tier).

## spec

sc_moat_raid FAILed (design/concepts/FlowWorks/version/in_game/visit_2/evidence/sc_moat_raid_20261119T214016.json): MOAT_raiders_swim swimmers [] over 25 polls (last positions x 64-89, z 53-81), MOAT_two_held_and_captured UNMEASURED (none held), MOAT_control_bridge_down_no_swim FAIL (2 swam with the bridge down: Human24618, Human24640). MOAT_drains_fast, MOAT_chemfuel_pumped, MOAT_moat_burns PASS. Not diagnosed in the sitting (bound): whether the raiders in the main run ever reached the moat (site geometry, HARNESS) or the swim path is chosen only when a bridge is also in play (MOD). First experiment: log the raiders' path targets and distance to the moat ring each poll.

## verify

python.exe src/RimMandrake/FlowWorks/northstar/concept_scenes.py --scene scene_moat_raid --out <json>: every row PASS

## criteria

Acceptance test: none offline, the cause is not known; live: the sc_moat_raid row.
