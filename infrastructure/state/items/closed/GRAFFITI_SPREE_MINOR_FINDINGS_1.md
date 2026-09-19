# GRAFFITI_SPREE_MINOR_FINDINGS_1

Opus code review (2026-09-02) of the Graffiti mod's spree mechanic. The
critical/important findings (undeployed assembly+defs, paint-on-any-
interruption, per-tick job churn, always-repaints-one-cell, silent
ClanOnly mis-wire) were fixed same-session. These 3 are lower priority.

## spec

1. `MentalStateDefs_Graffiti.xml`'s port of the donor mod's
   `Graffiti_Spree` dropped `<workerClass>GraffitiMod.
   MentalStateWorker_GraffitiPaintingSpree</workerClass>` (the donor's
   original had one; the port has none, falling back to the default
   `MentalStateWorker`). Consequence: the break can fire for a pawn with
   nothing paintable in reach, then just falls through to
   `JobGiver_WanderColony`. Decide deliberately: port an equivalent
   worker that checks paintability, or accept the fallback as fine.
2. `ThinkTreeDefs_Graffiti.xml` puts the spree's paint behavior BEFORE
   `JobGiver_GetFood`/`JobGiver_GetRest` in the priority sorter, unlike
   vanilla's own `MentalStateNonCritical` subtree which puts food/rest
   first. A spree pawn will paint instead of eating or sleeping for the
   whole 25000-45000 tick duration. Byte-identical to the donor's tree
   (pre-existing, not introduced by today's work) — still worth fixing to
   match vanilla's own ordering.
3. `ThingDefs_Graffiti.xml`'s `RM_Graffiti_Vandal` keeps
   `<tickerType>Normal</tickerType>`, inherited from the donor's custom
   `GraffitiMod.Filth_Graffiti` thingClass — the port's actual thingClass
   is plain vanilla `Filth`. Unverified whether plain `Filth` needs a
   Normal ticker; if not, this is a free per-tick virtual call per mark
   with nothing behind it. Check vanilla Filth_* defs' own tickerType
   before changing.

## verify

1 and 2 are XML-only, offline-verifiable. 3 needs a quick check of
vanilla's own Filth defs (e.g. `Filth_Trash`) for their tickerType
convention before deciding whether to change it.

## criteria

All 3 resolved (fixed or explicitly decided-to-keep with the reasoning
recorded).

## Closed 2026-09-02 (FOUNDRY)

1. **Checked, kept as-is.** `JobGiver_GraffitiPaintingSpree.TryGiveJob`
   already returns `null` cleanly when `TryFindWallMarkCell` finds nothing
   paintable, so the ThinkTree falls through to `JobGiver_WanderColony` —
   a graceful degrade, not a crash or a stuck pawn. Porting a dedicated
   `MentalStateWorker` subclass would be new C# surface for a case already
   handled one layer down; not worth the added risk for this pass.
2. Fixed: `ThinkTreeDefs_Graffiti.xml` now puts the food/rest
   `ThinkNode_PrioritySorter` before `JobGiver_GraffitiPaintingSpree`,
   matching vanilla's own `MentalStateNonCritical` ordering.
3. Fixed: removed `RM_BaseGraffiti`'s `<tickerType>Normal</tickerType>` —
   confirmed against vanilla's `BaseFilth` (Filth_Various.xml), which sets
   none for plain `Filth` thingClass.

XML well-formedness confirmed (no build step for raw defs). Deployed
directly.
