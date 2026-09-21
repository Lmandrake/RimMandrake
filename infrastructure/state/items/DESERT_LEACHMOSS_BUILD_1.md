# DESERT_LEACHMOSS_BUILD_1 — author the leachmoss, the desert's nutrient racer

## what is wrong

desert.md §4b's second defending shade plant — "mossy growth leaching nutrients
as fast as it can — fast, shallow, opportunistic, racing everything else to
whatever the wind just delivered" — has no def. `DESERT_SHADE_PLANTS_DESIGN_1`
decided it is a pure spawn-roll competitor (tier b, no C#) and split it from
the venomvine so it never waits on that item's assembly. **Read the design
first — it is the authority and names every number:**
`design/Jawa/worldbuilding/desert_shade_plants_design.md` §2, §3, §5.

## why it matters

It is half of the reason the ultracactus "holds the open ground by tolerance"
(§4b): the moss owns the fertile patch ground, so the ultracactus is pushed to
the sand. Without it the partition the sheet describes does not exist.

## the work — pure XML, in `src/RimMandrake/EnvironmentalHazards` (`mandrake.rm.environmentalhazards`)

MEASURED 2026-09-20: 1.6 `PlantProperties` has no reproduction fields and no
plant affects a neighbour; all wild spread is `WildPlantSpawner` weighting. So
the levers are exactly these, and nothing else is available:

- `ThingDef RM_Leachmoss` — `PlantBase`; `fertilityMin 0.5` (Gravel 0.7 / Soil
  1.0 only — Sand is 0.10, so it can never take the ultracactus's ground);
  `fertilitySensitivity 1.0`; `growDays 1.5`; `lifespanDaysPerGrowDays 4`;
  `plantRespawningCommonalityFactor 2.0`; `wildClusterRadius 5`,
  `wildClusterWeight 10`; `wildOrder 1`; `maxMeshCount 9`; `visualSizeRange
  0.4~0.7`; `topWindExposure 0`; `Nutrition 0.3`; `MaxHitPoints 60`;
  `harvestWork 60`; no harvest product; `purpose Misc`; `Flammability 0.2`;
  `pathCost 0`. Colour dull olive-umber, darker and duller than the
  ultracactus, never bright (§6.8 no lush; §9 palette).
- `RUT_Desert.xml` `wildPlants`: `RM_Leachmoss` at **1.5** — the highest weight
  in the list — `MayRequire="mandrake.rm.environmentalhazards"`.
- Settings: a leachmoss on/off toggle in `RM_EnvironmentalHazardsSettings`
  (default on), using whatever pattern the kit already uses to drop a def from
  `wildPlants` when a feature is off.
- Art: search `infrastructure/artpipe/{done,_artsrc,registry.jsonl,
  art_status.json}` for moss AGAIN before filing (2026-09-20: `grimmoss_v1`,
  `rut_palemoss_v1`, `rot_palemoss_v2` exist and are other rosters' plants —
  not this one). Then one `fill_queue.py` job.

## Watch out

- `PLANT_GROWTH_SPEC.md`'s ×4 postfix applies on top of `growDays 1.5`; that is
  intended ("fast enough to watch").
- The commonality that makes the moss *visibly* own patch ground at
  `plantDensity 0.05` is UNMEASURED — tune it by LOOKING at a quicktest desert
  map, not by arithmetic, and record what you saw.
- Do not reach for `CompPlantDamager` (plant-only `Rotting`, `CompTick`-driven,
  never fires on a Long-ticking plant, would rot its own stand) or any
  terrain-swap to fake fertility depletion. The design rejected both.

## verify

Design §5 step 7 on a quicktest desert map with all five DLC: moss present on
Gravel/Soil pockets and absent from Sand; cut a moss cell and confirm the
regrowth is moss more often than not; the ultracactus is still on the sand.

## criteria

`RM_Leachmoss` grows wild in `RUT_Desert` on fertile ground only, re-takes
emptied fertile cells first, and reads as the patch ground's dominant cover —
behind a working settings toggle, with no C#.
