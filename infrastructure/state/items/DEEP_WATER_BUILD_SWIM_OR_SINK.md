## spec
Plan P12 of `FLOWWORKS_DEPTH_REBUILD_ONE_BIG_DIG` (`design/RimMandrake/flowworks_one_rebuild_plan_2026-10-17.md`).
Owner ruling R12 on `WATER_NATURAL_DECIDE_ONE_SURFACE` (card, 2026-10-17): **pawns may swim in water 2 m or deeper**,
in lakes, canals and pits alike. Vanilla 1.6 treats `WaterDeep` as impassable (engine doc §1.1); Odyssey's swimming joy
only reaches standable water. Also answers play Q2 (water over the head) of `DEPTH_QUESTIONS_ASK_RAIDERS_FIRST`.

Build:
1. **Passable deep band.** The 2 m+ rung of the one-water ladder (`POND_DEPTH_BUILD_SHALLOWS_BEFORE_MUD`, P14) is
   enterable. Keep vanilla `WaterDeep`'s identity where vanilla compares by identity (roads, `RoadDefGenStep_Place`;
   engine doc §1.1) or patch passability at the path-grid level; pick one and record why.
2. **Swim speed** in deep water (slower than wading at 1.5 m), from a stat-like factor (Swimming skill or Moving
   capacity, race `waterCellCost`, genes such as the aquatic ones, `AQUATIC_WATER_BREATHING_GENE_1`).
3. **Exhaustion and drowning:** swimmers tire; a swimmer who cannot reach a climbable exit before exhaustion drowns,
   and gets a readable warning first (no-vanishing rule, 2026-09-29/30). Ties to `PIT_RULES_REWIRE_RELATIVE_NOT_ABSOLUTE`
   V2 (drowning when water covers the head): one drowning rule for lakes and pits. Downed/lying pawns in deep water drown.
4. **Apparel and weight:** heavy armour and carried mass slow swimming and shorten endurance; a stated table.
5. **Animals:** swimmers by race (aquatic/waterSeeker/`waterCellCost`) cross freely; others path around unless forced;
   wild and tame pathing avoids deep water unless no other route exists.
6. **AI pathing:** non-swimmers and the downed are never routed through deep water; raiders may swim a moat (ruling 26:
   *"a water moat alone stops nobody"*) at the swim cost.
7. **Non-water fluids keep the no-swim refusal** (`RM_Patch_NoRecreationalSandSwim.cs`; propane, boiling water, tar,
   slime, brine per the liquid matrix).
8. **Risk owed (flag):** trenches, moats and prisoner pits that relied on deep water as a barrier
   (`PIT_SUPERDEEP_COLLAPSE_1`, `PIT_CLIMB_PROVE_RAIDERS_VS_SHEER_TRENCH`, `HUTT_SLAVE_PIT_TEST_SITE_1`,
   `PIT_TEMPERATURE_SOFTENING_1`) are re-checked: a flooded pit is now swimmable to its lip, so only the climb rule
   (sheer wall above the surface) holds a prisoner. List each site and its verdict in this item.

ESTIMATE 3 to 5 agent-days plus about 0.5 live. Lands with or after P7 (shares drowning) and P14 (the deep band).

## verify
- L1: path grid: a swimmer can path across a 2 m+ water body; a non-swimmer/downed pawn is never routed through it.
- L1: swim speed, endurance and drowning numbers as a table with selftests (armour and carried mass lower both).
- L1: a pawn in non-water fluid of any depth is refused swim joy and is not routed through it as a swimmer.
- L1: each barrier site in spec step 8 has a recorded verdict (still holds / no longer holds / needs a ruling).
- L2 (live, minimal list, no flyers): a colonist swims across a 3 m lake and climbs out; a heavily armoured colonist
  tires and is warned before drowning; an animal that cannot swim walks around; a prisoner in a flooded sheer pit
  swims to the lip and cannot climb out.
