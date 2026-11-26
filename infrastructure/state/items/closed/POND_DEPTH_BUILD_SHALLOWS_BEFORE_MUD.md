## spec
**Re-scoped 2026-10-17 as Plan P14 of `FLOWWORKS_DEPTH_REBUILD_ONE_BIG_DIG`: the one-water terrain ladder**
(`design/RimMandrake/flowworks_one_rebuild_plan_2026-10-17.md`). Owner ruling R10 on `WATER_NATURAL_DECIDE_ONE_SURFACE`
(card, 2026-10-17): ONE kind of water (engine doc Option B2,
`design/RimMandrake/flowworks_natural_water_engine_2026-10-17.md` §3 and §5).

What was built here (BENCH, `0b60f7a80` + `118a5ae89`, offline): pond stages that write the **base** terrain by water
depth (original → `WaterDeep` → `RM_WaterChestDeepStill` → `WaterShallow` → `RM_WaterThin` → Mud → `RM_Lakebed_*`),
with an integer head rule. That stage ladder is the seed of P14. Its integer head rule and "s levels below the brim"
are replaced by the exactly-level solver (`WATER_LEVEL_BUILD_DECILITRES_NOT_NOTCHES`).

P14 scope:
1. **One ladder** of vanilla-water-family terrains chosen by water depth, the same for a lake, a pond, a canal and a
   pit: under 25 cm (new look, R2) → 0.5 m `RM_WaterThin` → 1 m `WaterShallow` → 1.5 m `RM_WaterChestDeepStill` (takes
   vanilla `WaterChestDeepBase`'s affordances, not `ShallowWater`: GPT finding #2) → 2 m and deeper (the deep band,
   enterable per R12 / `DEEP_WATER_BUILD_SWIM_OR_SINK`) → darker tints past 5 m (art, his look). Freshwater for water;
   each other fluid keeps its own ladder and water-body type.
2. **Wet dug squares write the base layer**, not the temp layer (`SetTempTerrain` sites in
   `RM_MapComponent_Excavation.cs` fill staging). Dry dug squares show `RM_Channel_*` from `depthGrid`; dry lake squares
   `RM_Lakebed_*` from `bedRecord`. The temp layer is left to vanilla (ice, floods). This is what gives dug water
   fishing and ice (engine §2.2: flags alone do not).
3. **Natural lakes:** a full natural lake square keeps its vanilla terrain (R10: nothing on screen changes); only
   drawn-down squares move along the ladder.
4. **Things on squares that change band** (bridges, conduits, blueprints, frames, items, pawns) follow vanilla
   terrain-change rules; one rule for a building whose affordance the new band lacks.
5. **Save migration:** every wet dug square's temp fill becomes a base write, once, on load. Back up Saves first.
6. Rivers and oceans are not touched (R10).

Still owed from the original item: thin-water art is judged in game only (owner, 2026-10-17: *"Same with the thin
water. Must see it in situ"*); `RM_WaterThin` may already be the under-25 cm look of
`VERY_SHALLOW_WATER_RESKIN_HE_SEES_FIRST`. ESTIMATE 2.5 to 3.5 agent-days, of which about 1 overlaps P3/P4 (same
staging code). Right after P3.

## verify
- L1: one ladder table in code, used by both lake drawdown and dug-water staging; a selftest maps metres → def for each rung.
- L1: no `SetTempTerrain` call stages liquid in FlowWorks (grep); a wet dug square's base terrain has a water-body type.
- L1: a full natural lake's terrain grid is unchanged by formation or by joining a canal.
- L1: save migration converts temp fills to base writes with litres unchanged (logged before/after).
- L2 (live, minimal list): ice on dug water: a canal at −10 °C freezes and thaws with its water picture intact; a
  seasonal or torrential flood over a wet canal leaves the canal's water and floor correct; fishing on a dug
  reservoir (with `FISH_ROLL_MEND_PONDS_BORN_BARREN`); the thin-water look seen in situ by the owner.
