# LANTERNDEEPS_HYDROCARBON_FAUNA_BUILD_1

Spec: `design/Jawa/worldbuilding/biomes/lanterndeeps_bedazzle_review_2026-10-01.md` §3 (ruled table) and `design/Jawa/worldbuilding/biomes/rosters/lantern_deeps_repopulation_proposals.md` (one section per animal, mechanics and feasibility).

Owner, typed: *"Both yes, both must be made hydrocarbons to survive, and yolk is now called galuush"* · *"Love these. Also hydrocarbon."* · *"Yes all 7 and ensure hydrocarbon"*.

All twelve, `RM_` tier, inline in `RM_LanternDeeps`, one home each: galuush (`RM_Galuush`, the giant, bs 6), hush, knocker, candler, sipper, drifter, tapper, pooler, blinker, chiller, slick, shoal. Every one a HYDROCARBON organism: yellow oil/wax/gas fluids, no iron blood, products fuel-class and warm-reactive (proposals premises 1-4, now ruled). Each mechanic reuses the `CreatureBehaviors` comp the proposals doc names. May be split into waves (XML-only first: drifter, candler, galuush, chiller, shoal); file each split as its own item.

Depends on `LANTERNDEEPS_FAUNA_TIER_PORT_BUILD_1` (shared `RM_` roster).

## verify
- All twelve load and spawn in a Deep; each mechanic fires once in a quicktest; none has meat or blood.
