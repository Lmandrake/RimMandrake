# SHADE_WHALE_ECOLOGY_LIVEPROOF_1 — live-prove the shade whale's two ecology mechanics

## what is wrong

`DESERT_SHADE_WHALE_FILTERFEED_1` built both of `desert.md` §4c's megafauna
mechanics and closed on offline evidence: the assembly compiles 0/0, the defs
parse and `validate_patch.py` passes against the 618-mod load set, and every
engine call the new code makes is resolved by the compiler against
`Assembly-CSharp`. What offline evidence cannot reach is whether either
mechanism FIRES.

Both are new mechanism CLASSES, never once observed running:

- **Terrain filter-feeding** — `RM_JobGiver_FilterFeedTerrain` /
  `RM_JobDriver_FilterFeedTerrain`. No pawn in this campaign has ever fed from
  terrain; the whole point is that it bypasses `FoodTypeFlags`, so nothing
  about it resembles a route already seen working.
- **Shade-gated dung seeding** — `RM_CompDungSeeder`. The first consumer of
  `RM_MapComponent_ShadeGrid.ShadeAt` on a comp tick rather than a JobGiver or
  a HediffComp.

## the work

One quicktest map, minimal list plus the five expansions
(`ALL TEST MOD LISTS include ALL FIVE EXPANSIONS`) plus
`mandrake.rm.creaturebehaviors` + `mandrake.rsw.swbestiary`. Spawn several
whales, not one — a single pawn's result can be pure RNG.

**Filter-feeding.**

- *The call:* spawn 4–6 `RSW_ShadeWhale` on `Sand`, set each pawn's food need
  low (below 0.75 of full), advance time, then read back each pawn's current
  job and its food level.
- *The expected reading:* at least one whale's `CurJobDef` is
  `RM_FilterFeedTerrain` and its `needs.food` level RISES over the bout with no
  food Thing consumed and none on the map.
- *How a pass could be false:* the food need rising is not enough on its own —
  a tamed whale fed by a colonist, or a plant eaten off-screen, produces the
  same number. The positive observation is **the job running by name** while
  the pawn stands on sand. And a whale standing on a non-sand cell that still
  feeds means `MatchesFeedTerrain` is reading the wrong grid.

**Dung seeding.**

- *The call:* place a whale under roof or beside a shade-casting building so
  `ShadeAt` clears 0.35, record the growth of every plant within 6 cells and
  the cell's thing list, then advance past `intervalTicksRange` (15000–30000
  ticks) and read both back.
- *The expected reading:* `Filth_AnimalFilth` appears at the whale's cell, and
  at least one recorded plant's `Growth` is strictly higher than its recorded
  value, and/or a new `RSW_Ultracactus` at ~0.05 growth stands on a cell that
  held no plant before.
- *How a pass could be false:* plants grow on their own. The comparison must be
  against a CONTROL whale parked in full sun on the same map for the same
  interval — that one must produce filth and NO growth delta beyond ordinary
  growth, because the shade gate is the mechanic. A pass with no control is
  not a pass. Equally, filth appearing proves only that the comp ticked; the
  whale's own `FilthRate` of 24 drops animal filth anyway.

## verify

Both mechanisms observed firing by name on a live map, with the sun-parked
control whale showing the dung gate holding.

## criteria

A positive observation of each, not an absence of errors.
