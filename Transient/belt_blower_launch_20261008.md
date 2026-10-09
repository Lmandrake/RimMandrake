# BELT: blower room cooler + launch held-colonist warning (2026-10-08)

## Item 1: BLOWER_ROOM_COOLER_1
(pending)

## Item 2: LAUNCH_HELD_COLONIST_WARNING_1
(pending)

## Result
- BLOWER_ROOM_COOLER_1: CompHeatPusher removed; RM_CompBlowerRoomCooler + vanilla CompTempControl; cools back-cell room, never heats; settings strength 14 / 250 W PROVISIONAL. Wording fixed in spec M2, the_greentide.md, WETBULB item, TICKER item A4, faction_tech_alignment.
- LAUNCH_HELD_COLONIST_WARNING_1: postfix on GravshipUtility.PreLaunchConfirmation appends named held colonists; GimmeSomeSlack not on this hook. Setting default on.
- Build OK; envhazards fuzz PASS (cooler, held families); validate_patch 0 errors; run_selftests 279 pass, 0 fail, 1 crash = selftest_memwatch (pre-existing memwatch.py TypeError, untouched).
