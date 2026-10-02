# SUPERDEEP_SEAM_MEASURE_1 — Measure the engine seams the pit collapse needs (Desktop, RimSage)

Part of the pit collapse (`PIT_SUPERDEEP_COLLAPSE_1` carries the rulings; `design/RimMandrake/flowworks_pits_unified_model_2026-10-02.md` is the one model). A pit is a canal cell dug to SUPERDEEP (D=4) and nothing else.

## spec
Desktop only (RimSage). Read, do not build. Record each answer with the decompiled member cited, in a `## measured` section here.
1. `Verse.AI.PathFinder.FindPath` / `Pawn_PathFollower.TryEnterNextPathCell` / `CostToMoveIntoCell`: is the cell being LEFT available when a move is costed or taken? (Decides where the D=4 exit veto and the descent-into-cell event live.)
2. `Reachability.CanReach` + `ReachabilityCache`: does the cache key include the start cell, so a per-start veto ("standing on D=4, cannot reach D<4") is cacheable?
3. `RegionMaker` / `RegionAndRoomUpdater` / `District` / `Room`: do regions ever split on `TerrainDef`, or only on edifices/`Fillage`? (Decides whether an enclosed D=4 area can be a room without a Harmony patch on region building.)
4. `Building_Door.PawnCanOpen` and the prisoner-escape path: the shape to copy for "openable from outside, never from inside".
5. Unroofed-room temperature: how vanilla equalises an unroofed room with outdoor temperature, and where a stronger coupling multiplier would attach.
6. The beggar-rejection thought(s) and which traits/precepts null them — the structure "Exposed Prisoner" must copy.
7. `legator.prisonerrealism` (Prisoner Realism): how it judges adequate confinement.

## verify
Each of the 7 answers cites a type and member from the decompiled 1.6 source. "UNMEASURED" is an allowed answer only with the reason.

## criteria
The holder-retire, prison-room and temperature items can each name their patch point without guessing.

## depends
Nothing. First in line.

## northstar
None — this is measurement. Its answers become `## anti-guessing notes` lines in the FlowWorks walk.
