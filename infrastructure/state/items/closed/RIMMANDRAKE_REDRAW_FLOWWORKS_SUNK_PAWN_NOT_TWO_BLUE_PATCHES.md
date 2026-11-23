# RIMMANDRAKE_REDRAW_FLOWWORKS_SUNK_PAWN_NOT_TWO_BLUE_PATCHES

From his FlowWorks walk of 2026-11-20: `design/RimMandrake/validation_holding/flowworks_walk_20261120.md` row #13 (his words, the picture, the station).

## spec

A colonist lying in 2 m of pit water (station 33) draws whole with two flat blue patches on it. `RM_SubmergeDraw.CoverPawn` (`src/RimMandrake/FlowWorks/Source/Superdeep/RM_SubmergeDraw.cs:559-617`) covers the drowned part with the body silhouette only (`r.SilhouetteGraphic`: not head, hair or clothes) in the water colour at 1 - Seen; the whole-picture cover (`:608`) runs only for a lying, wholly drowned pawn with a cached atlas frame [measured]. Which path drew his pawn [guess ~65% the silhouette band]. Related: RIMMANDRAKE_JUDGE_FLOWWORKS_DROWNED_BODY_COVER_BY_EYE (his verdict there: fail).

## verify

Zoomed captures of a standing, a lying and a dead pawn in 0.5, 1 and 2 m of clear water.

## criteria

Acceptance test: none, a look (his eye or a judge that did not make it).
