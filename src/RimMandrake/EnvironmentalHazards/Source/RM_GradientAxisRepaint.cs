using RimWorld;
using Verse;

namespace RimMandrake.EnvironmentalHazards
{
    // MIASMA_MECHANICS_1 M2 build. The kit spec's own flagged hard part
    // (miasma_kit_spec.md M2: "the repaint/reflow correctness... is the
    // kit's hard part") and its own open question: "verify the under-floor
    // natural terrain layer — TerrainGrid holds an under-grid; confirm the
    // API and that reflow on floor removal reads the new band."
    //
    // Resolved against the live 1.6 decompile (Source/Verse/TerrainGrid.cs,
    // read directly this pass). TerrainGrid stores THREE parallel per-cell
    // arrays — topGrid (what renders and what a pawn walks on), underGrid
    // (the natural ground a player-placed LAYERABLE terrain displaced — only
    // ever populated by TerrainGrid.SetTerrain's own layerable branch when a
    // floor/bridge is built over existing ground), and foundationGrid
    // (constructed hull terrain, e.g. gravship floors).
    //
    // TerrainGrid.SetTerrain(c, newTerr) for a non-layerable newTerr — every
    // terrain M1/M2 ever paint (brine/brackish/salt-crust are all natural
    // ground, never floors) — unconditionally overwrites topGrid AND clears
    // underGrid to null (that method's own `else { underGrid[num] = null; }`
    // branch, the non-layerable path). Calling it blind on a cell that
    // currently holds a player floor would therefore silently DESTROY that
    // floor — replace it outright with raw surge terrain — and simultaneously
    // erase the record of what natural ground used to sit under it. This is
    // exactly the "repaint silently overwrites a player's bridge" bug class
    // this item's own assignment called out.
    //
    // TerrainGrid.RemoveTopLayer confirms the read side of the fix: removing
    // a floor promotes underGrid -> topGrid. So writing the surge's terrain
    // into underGrid (via TerrainGrid.SetUnderTerrain, which never touches
    // topGrid at all) is exactly what makes a LATER floor removal reveal the
    // surge-shifted ground — closing the spec's own "confirm reflow-on-floor-
    // removal reads the new band" with a real mechanism, not an assumption.
    //
    // Foundation cells (FoundationAt != null, underGrid empty) are skipped
    // outright rather than guessed at: TerrainAt() only falls back to
    // foundationGrid when underGrid is empty, meaning a bare foundation
    // (e.g. a gravship hull tile with nothing built on it) IS the effective
    // surface there, and SetTerrain's own branches don't have a "write under
    // a foundation" case to use safely.
    //
    // Band-pick logic below is a deliberate, small, standalone duplicate of
    // RM_GenStep_GradientAxis's own private RepaintCell/PickWaterBand/
    // IsShallowWater (that file is M1's, already built; this item's own
    // assignment is explicit — "Do NOT touch M1" — so this is a fresh helper
    // rather than an extract-and-share refactor of that file).
    public static class RM_GradientAxisRepaint
    {
        public static void RepaintCell(Map map, IntVec3 c, float salinity, RM_GradientAxisExtension ext)
        {
            if (ext == null)
            {
                return;
            }

            TerrainGrid grid = map.terrainGrid;

            // The banding DECISION is made against the natural ground, not
            // whatever a player has built on top of it. BaseTerrainAt
            // returns underGrid when a floor/bridge sits over this cell,
            // else the same value TerrainAt would (Source/Verse/
            // TerrainGrid.cs, read this pass). Using TerrainAt here instead
            // would silently skip every water cell a player has bridged —
            // the bridge itself is never IsWater and never appears in
            // landRepaintSource — leaving its hidden underGrid stale, so a
            // later bridge removal would reveal PRE-surge terrain: exactly
            // the "confirm reflow on floor removal reads the new band"
            // defect this item's own assignment named.
            TerrainDef current = grid.BaseTerrainAt(c);
            if (current == null)
            {
                return;
            }

            TerrainDef target = null;
            bool isLandRepaint = false;
            if (current.IsWater)
            {
                RM_GradientAxisWaterBand band = PickWaterBand(ext, salinity);
                if (band != null)
                {
                    target = IsShallowWater(current) ? band.terrainShallow : band.terrainDeep;
                }
            }
            else if (ext.landTerrain != null && salinity >= ext.landRepaintMinSalinity
                && !ext.landRepaintSource.NullOrEmpty() && ext.landRepaintSource.Contains(current))
            {
                target = ext.landTerrain;
                isLandRepaint = true;
            }

            if (target == null || target == current)
            {
                return;
            }

            SetTerrainFloorSafe(grid, c, target);

            if (isLandRepaint)
            {
                KillAndReplacePlant(map, c, ext);
            }
        }

        // MIASMA_FLORA_ROSTER_1: the salt-line gauge. Fires once, the moment
        // this exact cell first repaints to landTerrain — the surviving
        // landRepaintDeadPlant is never itself landRepaintKillPlant, so this
        // is naturally self-terminating with no extra Scribed state, even
        // though RepaintCell re-visits every land cell on every throttled
        // pass for the whole duration of a shift.
        private static void KillAndReplacePlant(Map map, IntVec3 c, RM_GradientAxisExtension ext)
        {
            if (ext.landRepaintKillPlant == null)
            {
                return;
            }

            Plant plant = c.GetPlant(map);
            if (plant == null || plant.def != ext.landRepaintKillPlant)
            {
                return;
            }

            plant.Destroy();

            if (ext.landRepaintDeadPlant != null && GenPlace.TryPlaceThing(
                ThingMaker.MakeThing(ext.landRepaintDeadPlant), c, map, ThingPlaceMode.Direct, out Thing placed))
            {
                if (placed is Plant deadPlant)
                {
                    deadPlant.Growth = 1f;
                }
            }
        }

        // The floor-exclusion fix itself (see class header). Public so a
        // later, separate M3 build (stranding pools — the spec's own words,
        // "leaves pools behind" — also repaints via TerrainGrid) can reuse
        // this same safe write instead of re-deriving it.
        public static void SetTerrainFloorSafe(TerrainGrid grid, IntVec3 c, TerrainDef newTerrain)
        {
            TerrainDef under = grid.UnderTerrainAt(c);
            if (under != null)
            {
                // Avoid a redundant SetUnderTerrain (glow re-registration +
                // Notify_TerrainChanged) on every throttled pass while a
                // floored cell sits in the same salinity band — this gets
                // re-evaluated every ~250 ticks for the whole duration of a
                // multi-hour shift, so a same-value write here is not a
                // one-off cost.
                if (under != newTerrain)
                {
                    grid.SetUnderTerrain(c, newTerrain);
                }
                return;
            }

            if (grid.FoundationAt(c) != null)
            {
                return;
            }

            grid.SetTerrain(c, newTerrain);
        }

        private static RM_GradientAxisWaterBand PickWaterBand(RM_GradientAxisExtension ext, float salinity)
        {
            for (int i = 0; i < ext.waterBands.Count; i++)
            {
                if (salinity <= ext.waterBands[i].max)
                {
                    return ext.waterBands[i];
                }
            }

            return null;
        }

        // Same heuristic as RM_GenStep_GradientAxis.IsShallowWater
        // (duplicated, not shared — see class header): WaterShallowBase-
        // derived terrain carries the ShallowWater affordance;
        // WaterDeepBase-derived does not.
        private static bool IsShallowWater(TerrainDef terrain)
        {
            if (terrain.affordances == null)
            {
                return false;
            }

            for (int i = 0; i < terrain.affordances.Count; i++)
            {
                if (terrain.affordances[i].defName == "ShallowWater")
                {
                    return true;
                }
            }

            return false;
        }
    }
}
