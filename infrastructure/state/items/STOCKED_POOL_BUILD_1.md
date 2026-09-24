# STOCKED_POOL_BUILD_1 — build the Stocked Pool kit (Weeping Stones)

Build per the RULED spec
`design/Jawa/worldbuilding/biomes/weeping_stones_stocked_pool_2026-09-24.md`
(all rulings in its ⚖️ header; owner quotes verbatim there). Ships in the
`RM_WeepingStones` kit, feature-gated per the biome-kit Mod Settings law.

## scope

1. **Bestiary defs** — 8 rows (5 fish incl. the unchanged RM_Murrin baseline,
   3 doubt-beasts). Two-def law where a row is catchable: fishTypes item def +
   floor/pen presence. Wild table (the ruled gentle six, 2026-09-18) is
   UNTOUCHED — nastiness is stocked-line only.
2. **Husbandry loop** — STOCK/FEED/READ/HARVEST/OVERDRAW/CULL/RECAPTURE; pen
   zones over contiguous pool cells; murrin rings + silence telemetry
   (`RM_MapComponent_SilenceCue`); population via `RM_CompVerminBreeder` +
   `RM_MapComponent_VerminPopulation`; the M-risk is per-pool-body bookkeeping
   (`RM_MapComponent_PoolStock` — steal RM_LiquidBody's region logic).
3. **Cuisine hooks** — 6 recipes/ingredients per the spec; doubt-meat mood
   economy is RULED REAL: per-beast `Ate X` thoughts, no new C#; ideo
   bless/ban hook deferred to ideo passes.
4. Handler injuries real-but-minor (BENCH-settled). Vhorrin is the
   pool-turned-nasty state row as drafted.

Art: 8 sprite commissions ride the art queue AFTER a `_artsrc`/done sweep per
the standing check-first rule.
