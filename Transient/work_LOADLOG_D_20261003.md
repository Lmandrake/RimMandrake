# LOADLOG D 2026-10-03
Task: butcherProducts misplaced under race.
Sweep of all src ThingDef race blocks: only RM_Titanoslime had butcherProducts under race (41 other defs correct at ThingDef level, vanilla shorthand <Def>count</Def>). Moved to ThingDef level. Glurro.xml has no butcherProducts (comment only). validate_patch OK, selftest_slime_suite rc 0.
