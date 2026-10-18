## spec
Plan P11 of `FLOWWORKS_DEPTH_REBUILD_ONE_BIG_DIG` (`design/RimMandrake/flowworks_one_rebuild_plan_2026-10-17.md`).
Owner rulings R10 and R11 on `WATER_NATURAL_DECIDE_ONE_SURFACE` (2026-10-17). Analysis:
`design/RimMandrake/flowworks_natural_water_engine_2026-10-17.md` (B2 step 1) and
`design/RimMandrake/flowworks_natural_water_play_2026-10-17.md` (§1.1, the old slope's numbers).

His words (R11): *"Vary it. Some lakes will be shallow and silted up. Others will be deep and chasm-like. Depends on
the biome. The more mountainous, the deeper in general. The more plains-like, the smoother/shallower. They should also
have some variation down there, not just a radial crater."*

1. **Formation at map creation** (and once on first load of an old save): every LIMITED natural body is walked, its
   `bedRecord` written and it joins the P3 solver as a body. Oceans and edge rivers are classified limitless at the
   same moment and get a floor for the picture/readout only. **No terrain changes** on a natural lake (R10).
2. **Floor generator, per lake:** depth scale from the map tile's roughness (hilliness: flat → shallow and smooth;
   mountainous → deep, steep-sided, chasm-like), a per-lake random draw so two lakes in one biome differ (some silted
   shallow, some deep), and irregular variation across the floor (shelves, holes, ridges: seeded noise, not a radial
   cone). Shore squares keep a walkable first step (shallow-water shore 1 m, deep-water shore 2 m, as today) unless
   the beach default below is vetoed. Deterministic from the map seed (a reload never re-rolls a floor).
3. **Numbers:** the 0.5 m-per-4-squares slope and the 20 m default / 50 m large-lake caps are no longer fixed rules
   (replaced by R11). The settable ceiling stays (up to 125 m). **50 m is an upper bound reachable only by
   mountainous/deep biomes**, not a default for large lakes. Propose the per-roughness ranges (a table) and show them
   to him with the floor-variety look below; they are tuning, his to approve.
4. No shore ring (owner card 2026-10-18, BEACH_RING_RETIRE_DRAINED_MEANS_DRY: drained means dry); the shelf is a Mod
   Setting, default off.

Replaces the lake-floor criterion carried into `LIQUID_DEPTH_REWIRE_FIVE_IS_DEAD` from the absorbed
`LAKE_FLOOR_TUNE_TEN_TO_FIFTY_METRES`. ESTIMATE 2 to 3.5 agent-days. Needs P3 (bodies) and P4 (bed code, settings in
metres).

## verify
- L1: every limited natural body on a freshly made map has a recorded floor before the first tick; no natural lake
  square's terrain changed (diff of the terrain grid before/after formation = 0).
- L1: floors differ by roughness: over N seeded lakes per roughness class, mean and max floor depth rise from flat to
  mountainous; no floor exceeds the ceiling setting; 50 m reached only in mountainous/deep classes.
- L1: floors are irregular: a lake's floor is not a function of distance-to-shore alone (fraction of squares whose depth
  differs from the radial-slope prediction by ≥ 1 m is above a stated floor); same seed → same floor.
- L1: an old save forms its lakes once on load; a lake already formed lazily keeps its recorded floor.
- L2 (owner's look, live or staged savegame): lake floor variety: one flat-biome and one mountainous-biome map, lakes
  drawn down so their floors show; he judges "shallow and silted" vs "deep and chasm-like".
