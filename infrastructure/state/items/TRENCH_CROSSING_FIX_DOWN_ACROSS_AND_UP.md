# TRENCH_CROSSING_FIX_DOWN_ACROSS_AND_UP

Caused by RAIDERS_TRENCH_BUILD_BREACH_AND_JUMP (3f540054fa, DLL f56dafaf3f).

## finding

`RM_PocketGridMath.ReachVetoed` (called by `RM_SuperdeepTrap.RelativeVeto`, the postfix on
`Reachability.CanReach`) vetoes any two DIFFERENT surface components outright: "two surface components (no
pocket at either end) stay apart". The ladders were only ever counted as a way in/out of the pocket at one
END of the query. So bank A to bank B across a trench with a usable ladder on each wall was never one
reachability hop, although the cliff masks (structural lowered-ladder edges) let A* walk it. Consequences:
`RM_RaiderTrench.LadderJob` had to send raiders INTO the trench first ("Every ladder stands: step into the
trench"); a colonist ordered across by two ladders was refused; `CanReachMapEdge` refused a laddered island.

## spec

A trench with a usable ladder on the near wall and one on the far wall is crossable as an ordinary route
(down, floor, up) for any pawn those ladders allow: reachability (CanReach + CanReachMapEdge), the pathfinder
(masks + closed-ladder grid) and the step floor agree. Usable = `LadderIsAWay` (pawn query: LadderLetsOut —
prison-door rule, own-faction scaling ladders; pawnless: any lowered ladder). Raised ladders, other hostiles'
ladders and sealed pockets stay barriers.

## verify

Offline: `CliffMaskChecks` / `RaiderTrenchChecks` cases — colonist two-ladder crossing, raider with own-faction
ladders, hostile refused (prison door), raised ladder blocks, one ladder only is not a crossing.
Live row owed (FOUNDRY): a colonist ordered bank-to-bank walks down, across and up without a stall; a raid's
scaling ladders carry it straight across.
