# FEVERWOOD_OIL_BOIL_WEATHER_1 — the oil boil: on the hottest still days the swamp oil boils into a rainbow haze that doubles the harvest and burns on one spark

Caused by `FEVERWOOD_SCORING_SITTING_1` (turn 1). Free tier, `mandrake.rm.feverwood`. Design:
`feverwood_bedazzle_review_2026-10-02.md` §4 row 3 (*The Seep Boil*), §8. Ruling: new marks = **the oil boil
(weather) only** (decision taken by question card 2026-10-02 11:12 PDT), card text: *"on the hottest still days
the swamp oil boils up into a low rainbow haze; oil gathering doubles, but one spark (a gunshot, a torch, dry
lightning) flashes fire along the haze and a burning pool edge wakes the deep."* NOT CHOSEN: the mooring, the
pressure wedge, "all three". Sheet ban 5 binds: **no rain, no flowing water**.

## spec

1. **The weather.** `WeatherDef` `RM_FeverWood_OilBoil` (no rain, no wind; a low iridescent ground haze
   overlay, C# overlay on the `RM_WeatherOverlay_GreentideRoil` precedent) and a `GameConditionDef`
   `RM_OilBoilCondition` that carries the mechanics while it lasts. Added to `RM_FeverWood`'s
   `baseWeatherCommonalities` with a small weight, **and gated**: it may only start when the map's outdoor
   temperature is at or above a threshold (`// INVENTED`, Mod Settings; reads the same vanilla temperature the
   ambient heat kind of `FEVERWOOD_CROWN_SOUND_HEAT_1` uses). Letter on start: the oil is boiling; no sparks.
2. **The harvest doubles.** While the condition is active, `RM_Seepril` harvests yield twice their `RM_SeepOil`
   (a harvest-yield hook or a `StatPart` on the plant's yield; no new item).
3. **The haze is fuel.** The haze lies on ground-level cells only (not boughway, bough-soil, stilt platforms
   or trunk tops: the crown is above it). Any of these at or into a hazed cell ignites it: a projectile weapon
   firing from or landing in a hazed cell; a torch/lit-fire source (vanilla `Fire`, a burning pawn, an
   incendiary); a dry-lightning strike (`DryThunderstorm`'s strike). Ignition **flashes** fire along connected
   hazed cells within a radius (`// INVENTED`), using vanilla `Fire`, then ends the condition (the haze burns
   off). Melee does not ignite. Readable: a letter names what sparked it.
4. **A burning pool edge wakes the deep.** If the flash reaches a cell adjacent to a registered pool, the
   `RM_MapComponent_TentacleWatch` forces an ordinary emergence at that pool (a new public method on the
   existing component, beside `OnPorterAttacked`) and adds encounter pressure. Never the plot-reserved full
   emergence.
5. **Mod Settings:** `oilBoilEnabled`, temperature threshold, commonality weight, yield multiplier (default
   2), flash radius, `oilBoilWakesDeep`. Every field read by the code it claims to gate.

Depends on: `FEVERWOOD_CROWN_SOUND_HEAT_1` (soft: same heat reading). Art: the haze overlay texture is on
`infrastructure/artpipe/art_lists/feverwood_turn1_2026-10-02.csv`.

## criteria

- `jawa/get_defs` (`success`/`foundCount`): `WeatherDef/RM_FeverWood_OilBoil` = 1,
  `GameConditionDef/RM_OilBoilCondition` = 1; loaded `RM_FeverWood.baseWeatherCommonalities` includes
  `RM_FeverWood_OilBoil` and still has `Rain` = 0.
- Gate: forcing the weather by the weather decider at an outdoor temperature below the threshold is refused (a
  `[Tool]` read of the gate's `CanOccur`-style answer is false); above it, true.
- Yield: with the condition active, harvesting one mature `RM_Seepril` produces exactly 2× the `RM_SeepOil`
  count of the same harvest with it inactive (same plant growth, read the dropped stack count).
- Spark: with the condition active and no fire on the map, a debug shot fired from a hazed ground cell → fire
  count on the map > 0 within 60 ticks and the condition ends; the same shot fired from a boughway cell → no
  fire. A melee attack in a hazed cell → no fire.
- Wake: a flash that reaches a pool-adjacent cell → that pool's TentacleWatch shows a limb spawned within
  250 ticks (count of `RM_Sekkulaath_*` things within the pool's cluster rises by ≥ 1); with
  `oilBoilWakesDeep` off, it does not.
