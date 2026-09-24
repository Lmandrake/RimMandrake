using System.Collections.Generic;
using RimWorld;
using Verse;

namespace RimMandrake.EnvironmentalHazards
{
    // SUMP_TAR_NASTINESS_1 (item spec §1, "sticky tar onto any terrain
    // surface — an overlay/coating a source can apply to arbitrary terrain
    // (belch events, beast surfacing, tracking)").
    //
    // Deliberately NOT a TerrainDef-swap and NOT a new liquid-spread system:
    // SUMP_WALKWAYS_1 already established the real vanilla mechanism this
    // item's own header points at — TerrainDef.generatedFilth +
    // Pawn_FilthTracker for TRACKING (a pawn wading in an RM_Tar liquid
    // picks up RM_Filth_Tar on its own). What that mechanism does NOT cover
    // is a SOURCE splashing tar onto ground nobody has walked through yet —
    // a belch, a surfacing beast, a burst pipe. The generic building block
    // for that is the SAME filth system, entered from the other side:
    // FilthMaker.TryMakeFilth (RimWorld/FilthMaker.cs, read in full this
    // pass) is the real, already-vanilla-used API for "drop this FilthDef
    // on this cell," gated by the terrain's own filthAcceptanceMask
    // (RimWorld/FilthMaker.TerrainAcceptsFilth) exactly like every other
    // filth in the game — the same gate RUT_TarShallow_FilthAcceptance.xml
    // already opens for RM_TarShallow. No new spread simulation, no new
    // TerrainGrid write: a coating IS thick filth, on whatever terrain the
    // source is standing over, and ordinary cleaning (JobDriver_Clean) is
    // still the only way off — same "no separate bookkeeping" posture
    // RM_MapComponent_LivingRegrowth's own sealant check already uses.
    //
    // Kept as a static utility (not baked into one comp) so a belch event's
    // own GenStep/IncidentWorker and a beast's own emergence comp can both
    // call the same, already-proven cell-coating logic without each
    // reinventing the FilthMaker loop.
    public static class RM_TarCoatingUtility
    {
        // Splashes filthDef onto every cell in cells, thickened
        // thicknessPerCell times each (Filth.ThickenFilth is the real
        // vanilla accumulation call FilthMaker.TryMakeFilth already makes
        // internally when a cell already carries that filth def — calling
        // TryMakeFilth N times on the same cell is the correct, already-
        // vanilla way to lay down N thickness, not a new counter).
        // Respects the terrain's own filthAcceptanceMask by construction
        // (TryMakeFilth refuses a cell that does not accept it) — a coating
        // source placed over e.g. bare rock with a restrictive
        // filthAcceptanceMask simply does not stain that cell, same as any
        // other filth in the game.
        //
        // Returns the count of cells that accepted at least one layer.
        public static int CoatCells(
            Map map,
            IEnumerable<IntVec3> cells,
            ThingDef filthDef,
            int thicknessPerCell = 1,
            FilthSourceFlags additionalFlags = FilthSourceFlags.None)
        {
            if (map == null || cells == null || filthDef == null || filthDef.filth == null)
            {
                return 0;
            }

            int coated = 0;
            foreach (IntVec3 cell in cells)
            {
                if (!cell.InBounds(map))
                {
                    continue;
                }

                bool any = false;
                for (int i = 0; i < thicknessPerCell; i++)
                {
                    if (FilthMaker.TryMakeFilth(cell, map, filthDef, 1, additionalFlags, shouldPropagate: false))
                    {
                        any = true;
                    }
                }

                if (any)
                {
                    coated++;
                }
            }

            return coated;
        }

        // Convenience wrapper for a radius splash around a point (a belch's
        // epicenter, a surfacing beast's cell). useCenter true: the source's
        // own cell is coated too — a belch or a surfacing beast is standing
        // in what it just spat.
        public static int CoatRadius(
            Map map,
            IntVec3 center,
            float radius,
            ThingDef filthDef,
            int thicknessPerCell = 1,
            bool useCenter = true,
            FilthSourceFlags additionalFlags = FilthSourceFlags.None)
        {
            if (map == null || radius <= 0f)
            {
                return 0;
            }

            return CoatCells(map, GenRadial.RadialCellsAround(center, radius, useCenter), filthDef, thicknessPerCell, additionalFlags);
        }
    }
}
