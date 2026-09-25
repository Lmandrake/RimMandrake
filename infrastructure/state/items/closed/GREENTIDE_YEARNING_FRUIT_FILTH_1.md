# GREENTIDE_YEARNING_FRUIT_FILTH_1 — the fruit's filth/seed-dispersal mechanic

## what

Split out of `GREENTIDE_YEARNING_FRUIT_1` (`COMMISSION_LEDGER_CLEANUP_1`,
the_greentide sheet). `RUT_YearningFruit`/`RUT_DigestiveAccelerant` (built)
ship the "digests fast, hunger returns, brief waddle" half of
the_greentide.md §4's mechanic with plain vanilla stats. The half genuinely
missing is the payoff line: "hunger returns fast, filth follows... The
ground is carpeted in filth and sprouts, which is the strategy *working*."

## why deferred

No vanilla mechanism spawns filth or a seedling on a timer after a hediff
is applied. The nearest live precedent in this codebase is
`RM_HediffComp_ShadeStagger` (`RimMandrake.CreatureBehaviors`,
`DESERT_STAGGERSEED_BUILD_1`) — a HediffComp that, once a severity
threshold is crossed, steers the pawn toward a target condition and then
germinates a plant nearby. This slug wants the same SHAPE (a comp that
fires once the digestive-accelerant hediff has run its course) but a
different PAYLOAD: drop filth at the pawn's current position and/or spawn a
`RUT_YearningFruit` seedling nearby, rather than steer-then-germinate.

## scope

A new HediffComp (or comp properties class) that, on the
`RUT_DigestiveAccelerant` hediff's natural end (severity reaching 0), does
one or both of:

1. Spawns a filth thing (e.g. vanilla `Filth_Vomit`-shaped, or a new
   `RUT_`-named filth def if the flavor wants something more "seed-rich
   droppings" specific) at the pawn's position.
2. Rolls a chance to spawn a `RUT_YearningFruit` seedling nearby (mirroring
   `RM_HediffComp_ShadeStagger`'s own `germinateThingDef`/`germinateChance`/
   `germinateRadius` fields).

Should work on ANY eater (wild animals grazing the bush count as much as
colonists), matching the sheet's own "the ground is carpeted" framing — a
pure colonist-only effect would miss the point.

## needs

offline
