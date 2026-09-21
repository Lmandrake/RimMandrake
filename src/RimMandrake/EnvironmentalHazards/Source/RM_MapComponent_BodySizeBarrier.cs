using System;
using System.Collections.Generic;
using Unity.Collections;
using Verse;

namespace RimMandrake.EnvironmentalHazards
{
    // VENOMVINE_FORTRESS_PASSABILITY_1, the map-side half. Owns every cell a
    // RM_CompBodySizeBarrier has registered and everything the pathfinder is
    // ever shown.
    //
    // 🔑 THE ENGINE CHANNEL, and why this is not a custom pathfinder.
    //
    // RimWorld 1.6 has no per-body-size passability of its own. MEASURED
    // against the decompiled engine, 2026-09-21, the complete list of
    // per-pawn passability channels is: three fixed PathGridDefs (Normal,
    // FenceBlocked, Flying — Pathing's ctor binds those three by DefOf and
    // PathFinderMapData builds a CostSource for those three and no others,
    // so a fourth PathGridDef would be constructed and then never consulted
    // by the pathfinder), the single fenceBlocked bool on TraverseParms,
    // TraverseMode, the allowed Area, and:
    //
    //   PathRequest.IPathGridCustomizer — a per-REQUEST NativeArray<ushort>
    //   offset grid. PathGridJob.CostForCell adds custom[index] to the
    //   cell's cost, and PathGridJob.CellIsPassable returns FALSE outright
    //   when custom[index] >= 10000.
    //
    // That last one is the mechanism this file uses. It is a public engine
    // interface, vanilla drives it twice itself (BreachingGrid.CustomTuning
    // for breach raids, UsedRectPathGridCustomizer for road generation), and
    // it is the only channel in 1.6 that can make specific cells impassable
    // to ONE pawn's path request while leaving them open to another's. No
    // pathfinder internals are patched; one Harmony prefix hands this object
    // to PathFinder.CreateRequest through the customizer argument the method
    // already takes.
    //
    // ⚠️ Blocking is ROUTE-level, not physics. A blocked pawn will never
    // plan a route through a barrier cell; it is not teleport-proof, not
    // shove-proof, and a pawn already standing on one is not frozen there
    // (see the start-cell carve-out in CustomizerFor). Reachability still
    // runs on the Normal grid, so a destination reachable only through a
    // thicket reports reachable and then fails to path — which ends the job
    // and lets the AI choose something else, the same way a fence-blocked
    // animal behaves in vanilla.
    //
    // ⚠️ Threading: the offset grids are read by the pathfinder's worker
    // jobs and written here on the main thread when a barrier spawns or
    // despawns. The arrays are allocated once per map and never reallocated,
    // and every write is a single aligned 16-bit store of 0 or 10000, so the
    // worst a concurrent read can see is a one-tick-stale cell — a pawn
    // routes around a vine that just died, or through one that just grew.
    // The only unsafe operation would be disposing while a job holds the
    // array, which is why disposal happens in MapRemoved() and nowhere else.
    public class RM_MapComponent_BodySizeBarrier : MapComponent
    {
        // PathGridJob.CellIsPassable: custom[index] >= 10000 is impassable.
        // 10000 is also Verse.AI.PathGrid.ImpassableCost; using the literal
        // rather than the constant keeps this file independent of whether
        // that field stays public.
        private const ushort ImpassableOffset = 10000;

        // One offset grid, handed to every path request that needs it. The
        // pathfinder caches its per-map grid job keyed partly on the
        // customizer instance (PathFinder.MapGridRequest.Equals compares it
        // with object.Equals), so handing out ONE stable instance per bucket
        // is what keeps that cache from thrashing.
        private class BarrierGrid : PathRequest.IPathGridCustomizer, IDisposable
        {
            private NativeArray<ushort> offsets;

            // The indices currently set to ImpassableOffset. Rebuilding
            // clears these rather than walking the whole map: a stand is a
            // few hundred cells on a 62,500-cell map.
            private readonly List<int> marked = new List<int>();

            public BarrierGrid(int numCells)
            {
                offsets = new NativeArray<ushort>(numCells, Allocator.Persistent);
            }

            public NativeArray<ushort> GetOffsetGrid()
            {
                return offsets;
            }

            public void Clear()
            {
                for (int i = 0; i < marked.Count; i++)
                {
                    offsets[marked[i]] = 0;
                }

                marked.Clear();
            }

            public void Mark(int index)
            {
                if (index < 0 || index >= offsets.Length)
                {
                    return;
                }

                offsets[index] = ImpassableOffset;
                marked.Add(index);
            }

            public void Dispose()
            {
                if (offsets.IsCreated)
                {
                    offsets.Dispose();
                }

                marked.Clear();
            }
        }

        // NOT saved. Every barrier re-registers its own cell from
        // RM_CompBodySizeBarrier.PostSpawnSetup during load, so persisting
        // this would only create a second, staler source of truth.
        private readonly Dictionary<IntVec3, RM_CompBodySizeBarrier> cells =
            new Dictionary<IntVec3, RM_CompBodySizeBarrier>();

        // Distinct blockBodySize values present on this map, ascending.
        // In practice this has exactly one entry; it is a list so that two
        // barrier defs with different thresholds on one map give each band
        // its own correct grid instead of one of them silently winning.
        private readonly List<float> thresholds = new List<float>();

        // Keyed by BUCKET, where a pawn's bucket is the number of distinct
        // thresholds it exceeds. Bucket 0 is blocked by nothing and gets no
        // customizer at all.
        private readonly Dictionary<int, BarrierGrid> gridsByBucket = new Dictionary<int, BarrierGrid>();

        private bool dirty = true;

        public RM_MapComponent_BodySizeBarrier(Map map)
            : base(map)
        {
        }

        public bool AnyBarriers => cells.Count > 0;

        public void RegisterCell(IntVec3 cell, RM_CompBodySizeBarrier comp)
        {
            if (!cell.IsValid || comp == null)
            {
                return;
            }

            // Last registrant wins, same rule as MapComponent_ContactVenom's:
            // one plant per cell makes this unreachable today, and if some
            // future thing does stack two, the cell being a barrier on one of
            // their terms is the right answer.
            cells[cell] = comp;
            dirty = true;
        }

        public void DeregisterCell(IntVec3 cell, RM_CompBodySizeBarrier comp)
        {
            if (!cell.IsValid)
            {
                return;
            }

            // Only clear the cell if this comp owns it — otherwise a
            // despawning barrier would open a cell some other barrier has
            // since taken over.
            if (cells.TryGetValue(cell, out RM_CompBodySizeBarrier current) && current == comp)
            {
                cells.Remove(cell);
                dirty = true;
            }
        }

        // True when a pawn of this size may not enter this cell at all.
        public bool Blocks(IntVec3 cell, float bodySize)
        {
            if (cells.Count == 0)
            {
                return false;
            }

            return cells.TryGetValue(cell, out RM_CompBodySizeBarrier comp)
                   && comp?.Props != null
                   && bodySize > comp.Props.blockBodySize;
        }

        // Per-cell MOVEMENT cost for a pawn of this size, or 0 for "no
        // override, the Thing's own pathCost stands". Returned through
        // Pawn_PathFollower.GetPawnCellBaseCostOverride, which the engine
        // consults both when charging a step and when RCellFinder decides
        // whether a cell is somewhere a pawn would wander to — so a large
        // animal stops choosing thicket cells as destinations for free.
        public int MoveCostFor(IntVec3 cell, float bodySize)
        {
            if (cells.Count == 0)
            {
                return 0;
            }

            if (!cells.TryGetValue(cell, out RM_CompBodySizeBarrier comp) || comp?.Props == null)
            {
                return 0;
            }

            if (bodySize > comp.Props.blockBodySize)
            {
                return comp.Props.trappedMoveCost;
            }

            if (bodySize > comp.Props.passFreelyBodySize)
            {
                return comp.Props.threadMoveCost;
            }

            return 0;
        }

        // The customizer for a pawn of this size starting from this cell, or
        // null when the pawn is blocked by nothing on this map.
        public PathRequest.IPathGridCustomizer CustomizerFor(float bodySize, IntVec3 start)
        {
            if (cells.Count == 0)
            {
                return null;
            }

            EnsureFresh();

            int bucket = 0;
            for (int i = 0; i < thresholds.Count; i++)
            {
                if (bodySize > thresholds[i])
                {
                    bucket++;
                }
            }

            if (bucket == 0)
            {
                return null;
            }

            // 🔑 The start-cell carve-out. A pawn that is ALREADY on a
            // barrier cell gets no customizer, so it paths out on the plain
            // grid. Without this a giant that map generation placed inside a
            // thicket — or one a stand grew around — would have every route
            // from its own cell reported impassable and would stand there
            // failing to path forever. It cannot path back IN afterwards,
            // because by then it is standing outside.
            if (Blocks(start, bodySize))
            {
                return null;
            }

            if (!gridsByBucket.TryGetValue(bucket, out BarrierGrid grid))
            {
                grid = new BarrierGrid(map.cellIndices.NumGridCells);
                gridsByBucket[bucket] = grid;
                Rebuild(grid, bucket);
            }

            return grid;
        }

        private void EnsureFresh()
        {
            if (!dirty)
            {
                return;
            }

            thresholds.Clear();
            foreach (KeyValuePair<IntVec3, RM_CompBodySizeBarrier> pair in cells)
            {
                RM_CompProperties_BodySizeBarrier props = pair.Value?.Props;
                if (props == null || thresholds.Contains(props.blockBodySize))
                {
                    continue;
                }

                thresholds.Add(props.blockBodySize);
            }

            thresholds.Sort();

            foreach (KeyValuePair<int, BarrierGrid> pair in gridsByBucket)
            {
                Rebuild(pair.Value, pair.Key);
            }

            dirty = false;
        }

        // A pawn in bucket k exceeds exactly the k smallest distinct
        // thresholds, so its grid blocks every cell whose own threshold is at
        // or below the k-th smallest.
        private void Rebuild(BarrierGrid grid, int bucket)
        {
            grid.Clear();

            if (bucket <= 0 || bucket > thresholds.Count)
            {
                return;
            }

            float ceiling = thresholds[bucket - 1];
            CellIndices indices = map.cellIndices;

            foreach (KeyValuePair<IntVec3, RM_CompBodySizeBarrier> pair in cells)
            {
                RM_CompProperties_BodySizeBarrier props = pair.Value?.Props;
                if (props == null || props.blockBodySize > ceiling)
                {
                    continue;
                }

                grid.Mark(indices.CellToIndex(pair.Key));
            }
        }

        public override void MapRemoved()
        {
            base.MapRemoved();

            // The only point at which disposing is safe: the map, its
            // PathFinder and every job that could be holding one of these
            // arrays are all going away together.
            foreach (KeyValuePair<int, BarrierGrid> pair in gridsByBucket)
            {
                pair.Value.Dispose();
            }

            gridsByBucket.Clear();
            cells.Clear();
            thresholds.Clear();
            dirty = true;
        }
    }
}
