using System.Collections.Generic;
using UnityEngine;
using Verse;

namespace RimMandrake.EnvironmentalHazards
{
    // MIASMA_MECHANICS_1 M1 spike (miasma_kit_spec.md). The fresh->brine
    // axis: a per-map scalar field, 0f fresh .. 1f brine, that M2's surge
    // shoves and M3/M4/M6 read.
    //
    // SPIKE SCOPE: this proves the storage + API shape only — SalinityAt,
    // SetSalinityAt, SaltLineCells, and ShiftAxis's entry point signature
    // (M2's GameCondition is the class that will actually drive a shift
    // tick-by-tick and repaint terrain; that's its own, larger, later
    // build/spike, explicitly not done here). Owed, not silently skipped:
    //   - a real GenStep deriving initial axis direction from the tile's
    //     river/coast data (both fields exist and are real — SurfaceTile.
    //     Rivers is a List<RiverLink> with a per-link angle,
    //     RimWorld.Planet/SurfaceTile.cs:24; World.CoastDirectionAt(tile)
    //     returns a Rot4, RimWorld.Planet/Tile.cs:98 IsCoastal — confirmed
    //     against the live 1.6 decompile, closing the spec's own ❓ on
    //     exact 1.6 field names);
    //   - the "coarse grid" downsample the spec mentions (perf tuning, not
    //     an engine fact, deferred to the full build);
    //   - Scribe save/load of the grid itself (TerrainGrid.
    //     ExposeTerrainGrid's per-cell ushort-array pattern is the model
    //     to crib — Verse/TerrainGrid.cs:671 — not reproduced here since
    //     no per-cell save format decision has been made yet).
    public class RM_MapComponent_GradientAxis : MapComponent
    {
        private float[] salinity;

        // M2's future shift-in-progress state. Scribed so a save mid-surge
        // doesn't silently forget it; ShiftAxis itself does not yet apply
        // per-tick movement (see SPIKE SCOPE above).
        private bool shiftInProgress;
        private float shiftDeltaRemaining;
        private int shiftTicksRemaining;

        public RM_MapComponent_GradientAxis(Map map)
            : base(map)
        {
        }

        private void EnsureGrid()
        {
            int n = map.cellIndices.NumGridCells;
            if (salinity == null || salinity.Length != n)
            {
                salinity = new float[n];
            }
        }

        public float SalinityAt(IntVec3 c)
        {
            EnsureGrid();
            if (!c.InBounds(map))
            {
                return 0f;
            }
            return salinity[map.cellIndices.CellToIndex(c)];
        }

        public void SetSalinityAt(IntVec3 c, float value)
        {
            EnsureGrid();
            if (!c.InBounds(map))
            {
                return;
            }
            salinity[map.cellIndices.CellToIndex(c)] = Mathf.Clamp01(value);
        }

        // M2's entry point (RM_GameCondition_GradientSurge calls this on
        // the surge's ramp-in/recede). Records the requested shift; actually
        // walking it cell-by-cell each tick is M2's own build, not this
        // spike's.
        public void ShiftAxis(float delta, int durationTicks)
        {
            shiftInProgress = true;
            shiftDeltaRemaining = delta;
            shiftTicksRemaining = durationTicks < 1 ? 1 : durationTicks;
        }

        public bool ShiftInProgress => shiftInProgress;

        public IEnumerable<IntVec3> SaltLineCells(float band = 0.05f)
        {
            EnsureGrid();
            foreach (IntVec3 c in map.AllCells)
            {
                float s = salinity[map.cellIndices.CellToIndex(c)];
                if (s > 0.5f - band && s < 0.5f + band)
                {
                    yield return c;
                }
            }
        }

        public override void ExposeData()
        {
            base.ExposeData();
            Scribe_Values.Look(ref shiftInProgress, "shiftInProgress", false);
            Scribe_Values.Look(ref shiftDeltaRemaining, "shiftDeltaRemaining", 0f);
            Scribe_Values.Look(ref shiftTicksRemaining, "shiftTicksRemaining", 0);
        }
    }
}
