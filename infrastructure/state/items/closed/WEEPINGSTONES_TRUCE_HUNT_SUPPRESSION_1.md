# WEEPINGSTONES_TRUCE_HUNT_SUPPRESSION_1 — finish the water truce: predators never start a hunt within the truce radius

Caused by `WEEPINGSTONES_SCORING_SITTING_1` (turn 1). **Free tier**, `mandrake.rm.environmentalhazards`. Design:
`design/Jawa/worldbuilding/biomes/weepingstones_bedazzle_review_2026-10-02.md` §1 (c) 2, §4 row 0, §8. Ruling: build first, land what was decided plus the giant's story (decision taken
by question card 2026-10-02 12:53 PDT). Underlying ruling: the 2026-09-24 roster sitting, *"predators never start
hunts near full water… accepted for v1"*; sheet §6 hard ban: **no ambush-at-water predator**.

## What exists

- `RM_MapComponent_WaterTruce` ships the **retribution** half only; its own header (l.14): *"The SUPPRESSION half
  (a stocked-pool predator never hunts near truce water…) is a separate owed build"*. No item carried it until now.
- `RM_MapComponent_WaterTruce.IsTruceWater` is public so this build reads the identical radius
  (`RM_WaterTruceExtension.radius`, default 10).
- The roster names the shape: the inverse of `RM_MapComponent_DreadField` + `RM_JobGiver_DreadAvoidWander`.
- `RM_EnvironmentalHazardsSettings.waterTruceRetributionEnabled` gates the retribution half.
- `RM_Vhakk`'s description promises *"It never hunts at water"*; nothing enforces it today.

## spec

1. A predator (any `race.predator`, wild or tame) never **starts** a hunt whose prey stands within the truce
   radius of truce water, and never targets prey from inside it. A hunt already running whose prey enters the
   radius is abandoned. Hook the narrowest point (prey selection for predator hunts, `FoodUtility.BestPawnToHuntForPredator`
   or its caller; confirm with RimSage, never assume). Pawns' player-ordered hunting is untouched.
2. The ruled side effect stands: the colony's tamed predators also will not hunt there.
3. New setting `waterTruceSuppressionEnabled` (default true) beside the retribution toggle; off = vanilla hunting.
4. Applies on any biome carrying `RM_WaterTruceExtension` (today `RM_WeepingStones`), never by biome defName.

Feeds: `WEEPINGSTONES_WALKING_CONDENSER_1` (the moving pool carries the truce), `WEEPINGSTONES_REFUSED_TOLL_RITE_1`
(the truce binds the clan at the metered water).

## criteria

- Live, Weeping Stones quicktest: spawn 10 hungry predators and 10 prey inside a pool's truce radius
  (spawn many: one pawn is RNG); over 30,000 ticks zero predator hunt jobs target prey within the radius;
  with the setting off, at least one does (the control).
- A predator hunt started outside the radius is abandoned when the prey crosses into it.
- Retribution half still fires on a guilty colonist strike (regression).
