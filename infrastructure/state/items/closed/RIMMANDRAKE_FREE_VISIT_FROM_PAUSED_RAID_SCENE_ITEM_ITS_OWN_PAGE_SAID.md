# RIMMANDRAKE_FREE_VISIT_FROM_PAUSED_RAID_SCENE_ITEM_ITS_OWN_PAGE_SAID

## spec

FlowWorks visit 9's one open road-back item (RIMMANDRAKE_TRACE_FLOWWORKS_HELD_RAIDER_LEFT_DRAINED_MOAT) is cited only by
failed rows of sc_moat_raid, a paused raid scene. Read from the code: once its fixer run is spent, `_road_back` reads
`fixer_spent` and holds visit 10 for as long as raids are paused, against the raid-pause page ("no road back ... does not
pause its mod").

## verify

`python3 src/RimMandrake/rimflow/selftest_visit_wait_cited_items.py`: t_paused_scene_item_does_not_hold_the_visit and
t_paused_scene_item_holds_when_not_paused, both red before the fix.

## criteria

An item cited only by paused raid scenes gets its one fixer run and then holds no visit; any other citing row, or a lifted
pause, holds as before.
