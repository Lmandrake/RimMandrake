# WEEPINGSTONES_WALKING_CONDENSER_1 — the giant's story: the walking condenser (the oldest gorrask carries a running ancient water machine; a pool and its truce form wherever it settles)

Caused by `WEEPINGSTONES_SCORING_SITTING_1` (turn 1). **Free tier**, `mandrake.rm.weepingstones` (invented creature,
invented machine, no canon names). The two quest branches the owner added are
`WEEPINGSTONES_CONDENSER_QUESTS_1`. Design: `design/Jawa/worldbuilding/biomes/weepingstones_bedazzle_review_2026-10-02.md` §3, §4 row 1, §7 Q2, §8.

Ruling: build the giant's story in the first batch (decision taken by question card 2026-10-02 12:53 PDT). Story:
the owner typed, 2026-10-02: *"I love (1). Optional quest from Hutts to capture it for the Arena (sad), or work with
Moisture Farmers to keep it free by foiling fellow hunters (Blackstar hunting it for fame)."* Option (1) is the
card's **walking condenser**: *the oldest crab grew an ancient water machine into its shell and it still runs:
wherever the crab settles for a season, a pool forms round it, truce and all… The clan can guide it onto its own
land for a season, sell where it will settle next to the highest bidder, or cut the machine out, ending the moving
oasis but getting the last working ancient condenser as a water plant for your ship.*

## What exists

- `RM_Gorrask` (`RM_Gorrask.xml`, bs 15, `wildAnimals` 0.02): a single-tile legendary-rare creature with **no
  comps**. The ruled follow-on *"true multi-tile landform occupation"* (BiomeDef header) has no item; this item lands
  it only as far as the story needs.
- `RM_CompOasisMaker` + `RM_OasisPlacementScorer` (`src/RimMandrake/OasisMaker/`): ring growth of a water site.
- `RM_MapComponent_WaterTruce` / `RM_WaterTruceExtension` (truce at water); `RM_MapComponent_PoolStock` (pool health).
- Art: gorrask pawn art exists (artpipe `done/weepingstones2_gorrask_*`); `RM_CorrodedCondenserStack` art exists
  and may serve as reference only. New art: `weepingstones_turn1_2026-10-02.csv`.

## spec

1. **The oldest gorrask** `RM_GorraskCondenser` (name collision-checked; GPT's *Korrav* fails the stem rule): a
   unique variant, one per world, a static overlay of the machine grown into its shell (multi-tile footprint or
   blocking cells as far as the build needs; not a general landform system).
2. **It moves by seasons.** It settles on a map site for a season; while settled, a pool forms round it
   (`RM_CompOasisMaker` ring growth reused) and the truce holds there (the pool carries `RM_WaterTruceExtension`
   semantics, reusing `IsTruceWater`). When it moves on, the pool dries back over days, never instantly, with a
   letter (no thing vanishes without a readable sign).
3. **Three player choices**, each a readable action with a letter:
   - **Guide it onto your land** for one season (an escort/lure action; the pool and truce come to you).
   - **Sell where it will settle next** to the highest bidder among factions (a world-map signal and a payout;
     the buyer's settlement gains a season pool).
   - **Cut the machine out**: kills or frees the crab (the moving oasis ends for good, world letter) and yields
     `RM_AncientCondenserPlant`, a minifiable, ship-installable water-producing building (the last working one).
4. Mod Setting: enable/disable the walking condenser; tuning for season length.
5. No new heat or weather; vanilla seasons only.

Depends on: `WEEPINGSTONES_TRUCE_HUNT_SUPPRESSION_1` (the moving pool carries both truce halves). Feeds:
`WEEPINGSTONES_CONDENSER_QUESTS_1`.

## criteria

- `jawa/get_defs` for `RM_GorraskCondenser` and `RM_AncientCondenserPlant`: `foundCount` 1 each.
- Live (debug-spawned on a quicktest map): a pool cell set forms round it over the configured days; `IsTruceWater`
  is true at that pool; forcing a move dries the pool with a letter.
- Each of the three choices fires end to end on a quicktest; cutting yields the plant, which installs on a gravship
  and produces water.
