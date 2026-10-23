# SCENARIO_REELS_FIX_STILL_FACING_WEST

FlowWorks stagers build every hose reel West (`RM_HoseReel:x,z,3`: `northstar/liquid_checks.py:77`,
`northstar/water_scenes_walk.py:739`, 0ab8470911) although reels turn since 73b8805755. On the walkthrough save 10 hoses
(41679, 41683-85, 41687, 41688, 42273, 42433, map R 382378/382379) leave the west nozzle and U-turn to a target behind the reel.
Evidence: `Transient/pile_2026-10-22/hose_audit.md` §3 D10.

## criteria
- Each staged reel is built facing its free end/port; a rebuilt walkthrough shows no 180-degree loop out of any reel (capture per reel).
