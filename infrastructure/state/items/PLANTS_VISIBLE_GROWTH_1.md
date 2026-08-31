# PLANTS_VISIBLE_GROWTH_1 — plants that visibly grow as you watch

Owner's ask, 2026-08-31: "Plants that visibly grow as you watch." Spec by
BENCH, mechanism MEASURED from 1.6 source.

## spec
The engine already scales plant draw size by growth
(`plant.visualSizeRange.LerpThroughRange(growthInt)` in `Plant.Print`) and
swaps whole sprites across stages (`immatureGraphic`/`leaflessGraphic`) —
BUT the redraw is **quantized to 10% growth buckets and fires only for
CULTIVATED plants** (`CurrentlyCultivated()` gates the `MapMeshDirty` call);
a wild plant never re-dirties from growth at all.

Two-tier design:
1. **Pure-def tier (crops, free):** showcase fast growers — the Depths'
   pressure-fruit and lightkelp, a surface "dune bloom" crop — with small
   `growDays` (full cycle ~1 in-game hour), a WIDE `visualSizeRange`
   (~0.2→1.4) and an `immatureGraphic` swap. In a growing zone the plant
   visibly steps up in size ~every 10% — ten visible jumps in an hour reads
   as "growing while you watch."
2. **C# garnish (one tiny patch, makes it WILD too):** a Harmony postfix on
   `Plant.TickLong` dropping the `CurrentlyCultivated()` gate for defs
   carrying our `RM_VisibleGrowth` DefModExtension — wild showcase plants
   (vent gardens, post-rain desert bloom) get the same behavior. Perf guard:
   the extension whitelists, so only our handful of defs re-dirty often
   (the source read flagged mesh-dirty cost at scale as unmeasured — the
   whitelist is the mitigation, and a 200-plant quicktest is the proof).

Pairs naturally with DESERT_PLANTS_SCRAGGLY_1 (the bloom cycle is the one
moment scraggly desert flora turns briefly beautiful — the contrast is the
art direction).

## verify
Quicktest: plant the showcase crop, unpause at speed 1, PROVE the sprite
steps through ≥8 visible size changes within one in-game hour; EXPECT the
immature→mature sprite swap at harvestable. Then 200 instances at speed 3
with no TPS collapse (measure, don't eyeball). LIES: a wide visualSizeRange
LOOKS like growth even when growth is stalled — verify growthInt actually
advanced, not just that the sprite is big.

## criteria
The owner watches one plant grow from seed to harvestable in about an hour
of game time and calls it alive; wild tier works on a vent-garden tile; TPS
proof recorded.
