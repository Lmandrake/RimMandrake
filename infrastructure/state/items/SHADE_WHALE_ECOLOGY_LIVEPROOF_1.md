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

## CLOSED — both mechanisms observed firing by name, with a three-level shade control, 2026-09-21

Run by FOUNDRY on the bridge, `modset_builder.py --tier desertplants` (19 mods, all five
DLC — the tier already carries `mandrake.rm.creaturebehaviors` and
`mandrake.rsw.swbestiary`). Deployment confirmed in sync for SWBestiary, UtinniPatches,
CreatureBehaviors and EnvironmentalHazards before launch; `RSW_ShadeWhale` resolved and
spawned with `bodySize 16.0`, so the `SHADEWHALE_EXTENSIONS_UNBUILT_1` stale-DLL block is
gone. Map: tile 83745 set to `RUT_Desert`, 250×250, generated through
`jawa/world_tile_map_generate` (deterministic — three generations, 8,823 things each).

---

### FILTER-FEEDING — PASSES, and the job is proven BY NAME

*The call.* Six `RSW_ShadeWhale` spawned faction-less on Sand at (60,140) (140,140)
(200,140) (60,160) (100,160) (140,160); each one's Food need written to 0.30 with
`jawa/pawn_need` (well under `beginBelowFoodPercent 0.75`); time stepped.

*What was read.*

```
t=4101   all six  food 4.800 (0.300)   on Sand, on their spawn cell
t=4501   4.791 / 4.787                 hunger drain only
t=4901   4.778
t=5301   4.765                          <- bout started at ~4101, boutDurationTicks 1200
t=5701   6.347 / 6.338 (0.397 / 0.396)  <- payout
```

**Net +1.582 against a predicted gross of `Need_Food.MaxLevel` 16.0 × `foodPercentPerBout`
0.10 = 1.600**, the difference being the hunger drain inside the reading window. The
payout landed exactly one `boutDurationTicks` after the job began. Not one whale moved a
cell in the whole run — the JobGiver's "standing on it already" branch, which is what
stops a megafauna shuffling across a sand sheet.

*The job, by name.* `rimworld/save_game` then parsing the `.rws`:

```
RSW_ShadeWhale60972  curJob.def = RM_FilterFeedTerrain  targetA (60, 0, 140)
RSW_ShadeWhale60973  curJob.def = RM_FilterFeedTerrain  targetA (140, 0, 140)
RSW_ShadeWhale60974  curJob.def = RM_FilterFeedTerrain  targetA (200, 0, 140)
RSW_ShadeWhale60975  curJob.def = RM_FilterFeedTerrain  targetA (60, 0, 160)
RSW_ShadeWhale60976  curJob.def = RM_FilterFeedTerrain  targetA (100, 0, 160)
RSW_ShadeWhale60977  curJob.def = RM_FilterFeedTerrain  targetA (140, 0, 160)
```

**Exactly 6 occurrences of that string in the whole 14.6 MB save** — no other pawn on
either map was running it. Every `targetA` is the whale's own cell and every one of those
cells read `Sand` from `jawa/get_terrain_batch`, so `MatchesFeedTerrain` is reading the
terrain grid the item said it must.

*The item's own false-pass checks, answered.* `group=Corpse` = 0 and
`group=FoodSourceNotPlantOrTree` = 1 across the whole 62,500-cell map, none of it at any
whale's cell; no whale was tamed and no colonist was within 100 cells; no whale moved, so
nothing was walked to and eaten; and the gain is exactly the driver's
`MaxLevel * foodPercentPerBout`, which no plant's nutrition would reproduce.

---

### DUNG SEEDING — PASSES, with a three-level shade dose-response

The item asked for a sun-parked CONTROL whale. It got four, plus a second shaded arm at a
different `ShadeAt` value, so a null result could be told apart from a broken gate.

*Staging.* Twelve all-Sand 15×15 sites on a 20-cell lattice, each cleared of plants and
then planted with **8 `RSW_Ultracactus` at growth 0.30** at fixed offsets ±2/±4 (within
`seedRadius` 5.9, leaving the rest of the radius empty for seedlings). One whale per site,
food need 1.0, then downed so its cell at fire time is known. `rimworld/get_cells_info`
confirmed per site that the only solids inside the 5×5 window `ShadeSearchRadius 2` can
see are the planted cactus (`visualSizeRange.max` 0.65, well under the 1.5
`ShadeCastingPlantVisualSize`) — and, at arm B, the three rocks.

| arm | how shade was made | `RM_MapComponent_ShadeGrid.ShadeAt` |
|---|---|---|
| **A_roof** | 13×13 `RoofRockThick` via `jawa/set_roof_batch` | **1.00** — `ComputeShadeAt` returns 1f for any roofed cell |
| **B_rock** | three `Sandstone` at (+1,−1..+1), unroofed | **0.667** — `1 − 1/(ShadeSearchRadius+1)` at distance 1 from a `fillPercent` 1.0 Building |
| **C_sun** | nothing within 2 cells, unroofed | **0.00** |

*Result, t=6,901 → 46,500 (~40,000 ticks, `intervalTicksRange` 15000~30000):*

| arm | ShadeAt | new plants seeded | sites that seeded |
|---|---|---|---|
| A_roof | 1.00 | **17** | 4 / 4 |
| B_rock | 0.667 | **10** | 4 / 4 |
| **C_sun** | **0.00** | **0** | **0 / 4** |

Every seeded plant is `RSW_Ultracactus` reading **"5% grown"** — `seedPlantGrowth 0.05`
exactly — and every one is within 3.6 cells of its whale, inside `seedRadius 5.9`.
**The four sun-parked whales seeded nothing at all**, across a window in which each of
them was past its own `intervalTicksRange` at least once. `minShadeToSeed 0.35` holds,
and it holds as a gradient rather than an on/off accident.

*The fertilise half, with exact arithmetic.* The eight plants put down at 30 % now read:

```
C_sun                 34%   = 30 + 4 natural growth over 40,000 ticks
A_roof, one event     55%   = 30 + growthBoost 25
A_roof, two events    80%   = 30 + 25 + 25
B_rock, one event     59%   = 30 + 25 + 4 natural
```

⭐ The A_roof arm is the cleanest reading in the run: under `RoofRockThick` the plants
report **"Growth rate: 0% (resting, needs light level 51%)"**, so natural growth there is
literally zero and the +25 can only be `RM_CompDungSeeder.FertiliseNearbyPlants`.
The two A_roof sites that fired twice also show three seedlings sitting at **30 %** —
`seedPlantGrowth` 0.05 plus one later `growthBoost` 0.25, the comp caught fertilising its
own earlier seedling.

*The creature half — supporting, not conclusive.* Two young animals appeared inside
A_roof radii during the run (`RSW_Sketto` near (40,80), `RSW_Gorg` near (100,100)), both
under `maxWildlifeBodySize` 0.6, both `ageBiologicalYears` 0 (`seededWildlifeAgeYears` 0.4
truncates in that field). ⚠️ A live map also spawns its own wildlife, so this is not a
clean positive on its own — but no extra pawn ever appeared at any B or C site, and both
of these appeared *inside* a whale's radius rather than walking in from a map edge.
Recorded as consistent with `SeedYoungCreature` firing at roughly its 0.15 chance
(2 of ~10 shaded dung events), not as proof.

*One anomaly, measured and not explained.* At B_rock (120,100) a single dung event
boosted **6 of the 8** plants in radius; two stayed at 34 %. `maxPlantsBoosted` is 12 and
only 8 plants were in radius at boost time, so the cap does not account for it. Recorded
so the next reader does not have to rediscover it.

---

### 🔴 DEFECT — `Filth_AnimalFilth` is a permanent no-op on natural ground

Filed as `FILTH_ON_NATURAL_TERRAIN_NOOP_1`. Both mechanisms in this item drop filth and
**neither one can**, anywhere outdoors in this biome.

MEASURED: six completed filter-feed bouts with `leavingsFilthDef Filth_AnimalFilth`
count 1 produced **0** `Filth_AnimalFilth` on the map. Eight shaded dung events with
`dungFilthCount 4` produced 0 at every site but one; that one (A_roof 120,20) accumulated
5 → 18 over the run, a cadence far faster than a 15,000–30,000-tick dung interval — that
is the whale's own `FilthRate 24` through `Pawn_FilthTracker`, which passes
`FilthSourceFlags.Pawn` and therefore takes `FilthMaker.CanMakeFilth`'s roofed-cell
exemption that the comps do not.

ENGINE SOURCE, read from the decompiled 1.6 tree:

- `Filth_AnimalFilth.filth.placementMask` is `[Terrain]` — Core
  `Defs/Core/ThingDefs_Misc/Filth_Various.xml`.
- Every terrain inheriting `NaturalTerrainBase` — Sand, SoftSand, Soil, Gravel, the lot —
  declares `filthAcceptanceMask` `[Unnatural]`, Core `Defs/Core/TerrainDefs/Terrain_Natural.xml`.
- `FilthMaker.TerrainAcceptsFilth` requires `(acceptance & placement) == placement`;
  `Unnatural & Terrain` is 0, so it is false.
- `CanMakeFilth`'s roof/indoor escape hatch requires `placementMask.HasFlag(Pawn)`, which
  `Filth_AnimalFilth` does not have, and the `TryMakeFilth(cell, map, def, count)`
  overload both comps call never adds it.

⇒ **Filth is not a usable "the comp ticked" indicator for either mechanism**, and the
"massive dung at shade patches" flavour never appears in the desert. The verify above
therefore rests on the seeding and the growth boost, not on filth.

---

### verify / criteria

Both mechanisms observed firing by name on a live map — filter-feeding as
`curJob.def = RM_FilterFeedTerrain` on six whales with the exact `MaxLevel × 0.10` payout,
dung seeding as 27 `seedPlantGrowth`-0.05 seedlings and an exact +0.25 growth boost across
eight shaded whales — with **four sun-parked control whales producing zero of either**.
A positive observation of each, not an absence of errors. **Item CLOSED**, with one
defect filed.
