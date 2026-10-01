using System;
using System.Collections.Generic;
using RimWorld;
using Verse;

namespace RimMandrake.CreatureBehaviors
{
    [DefOf]
    public static class RM_TrackDefOf
    {
        public static MapMeshFlagDef RM_TrackPrints;

        static RM_TrackDefOf()
        {
            DefOfHelper.EnsureInitializedInCtor(typeof(RM_TrackDefOf));
        }
    }

    // ════════════════════════════════════════════════════════════════════
    // FOOTPRINT_TRACK_GRID_1 — one footprint grid for the planet.
    //
    // Owns the RM_TrackPool for its map (allocated on the first print, so a
    // map with no track surface costs nothing), the style table (which
    // sprite and draw size each record uses), the save, the erase API every
    // biome's eraser calls, and the mesh dirtying for
    // RM_SectionLayer_TrackPrints. Written to by RM_TrackGridPatches.
    //
    // Erase API (each biome brings its own eraser, nothing here decides WHEN):
    //   ClearCell(c) / ClearRect(rect)          a dune moved, a floor was laid
    //   BeginDownwindSweep(deg) + SweepStep(n)  the wind returns: n cells per
    //                                           call from the upwind edge on,
    //                                           every map cell visited once,
    //                                           onCell lets the caller wipe its
    //                                           own film in the same pass
    // ════════════════════════════════════════════════════════════════════
    public class RM_MapComponent_TrackGrid : MapComponent
    {
        private RM_TrackPool pool;
        private List<string> styleKeys = new List<string>();
        private Dictionary<string, ushort> styleIndex = new Dictionary<string, ushort>();

        private bool sweepActive;
        private float sweepAngle;
        private int sweepPos;
        private int[] sweepOrder;

        public RM_MapComponent_TrackGrid(Map map) : base(map)
        {
        }

        public static RM_MapComponent_TrackGrid For(Map map) => map?.GetComponent<RM_MapComponent_TrackGrid>();

        public RM_TrackPool Pool => pool;
        public int Count => pool?.Count ?? 0;
        public bool Sweeping => sweepActive;

        // ── reads ────────────────────────────────────────────────────────

        public bool TryGetPrint(IntVec3 c, out RM_TrackRecord rec)
        {
            rec = default(RM_TrackRecord);
            return pool != null && c.InBounds(map) && pool.TryGet(map.cellIndices.CellToIndex(c), out rec);
        }

        /// <summary>Style key is "texPath|drawSize"; null for an unknown index.</summary>
        public bool TryGetStyle(ushort style, out string texPath, out float drawSize)
        {
            texPath = null;
            drawSize = 0f;
            if (style >= styleKeys.Count) return false;
            string key = styleKeys[style];
            int bar = key.LastIndexOf('|');
            if (bar <= 0) return false;
            texPath = key.Substring(0, bar);
            return float.TryParse(key.Substring(bar + 1), System.Globalization.NumberStyles.Float,
                System.Globalization.CultureInfo.InvariantCulture, out drawSize);
        }

        // ── the writer (called by the Harmony postfix) ───────────────────

        public void RecordStep(Pawn pawn, RM_TrackSurfaceExtension surface)
        {
            float bs = pawn.BodySize;
            if (bs < surface.minBodySize) return;
            RaceProperties race = pawn.RaceProps;
            byte bits = RM_TrackPool.Classify(race.Humanlike, race.IsMechanoid, race.Animal, bs, pawn.Crawling,
                pawn.pather?.lastMoveDirection ?? pawn.Rotation.AsAngle);
            var rec = new RM_TrackRecord { bits = bits };
            string tex = surface.TexPathFor(pawn.def, rec.Size, rec.Source, rec.Drag);
            ushort style = StyleFor(tex, surface.DrawSizeFor(rec.Size));
            EnsurePool();
            IntVec3 c = pawn.Position;
            int evicted = pool.Write(map.cellIndices.CellToIndex(c), Find.TickManager.TicksGame, bits, style);
            Dirty(c);
            if (evicted >= 0) Dirty(map.cellIndices.IndexToCell(evicted));
        }

        // ── erase API ────────────────────────────────────────────────────

        public bool ClearCell(IntVec3 c)
        {
            if (pool == null || !c.InBounds(map)) return false;
            if (!pool.Clear(map.cellIndices.CellToIndex(c))) return false;
            Dirty(c);
            return true;
        }

        public int ClearRect(CellRect rect)
        {
            if (pool == null) return 0;
            return pool.ClearRect(rect.minX, rect.minZ, rect.maxX, rect.maxZ,
                idx => Dirty(map.cellIndices.IndexToCell(idx)));
        }

        public void ClearAll()
        {
            if (pool == null) return;
            pool.ClearAll();
            map.mapDrawer.WholeMapChanged(RM_TrackDefOf.RM_TrackPrints);
        }

        /// <summary>Start a wipe from the upwind edge. <paramref name="windTowardDegrees"/>: 0 = north, 90 = east.</summary>
        public void BeginDownwindSweep(float windTowardDegrees)
        {
            sweepActive = true;
            sweepAngle = windTowardDegrees;
            sweepPos = 0;
            sweepOrder = null;
        }

        /// <summary>
        /// Advance the sweep by up to <paramref name="maxCells"/> map cells, clearing any print
        /// on them and calling <paramref name="onCell"/> for every visited cell (so the caller can
        /// wipe its own film and drop a dust fleck per batch). Returns cells left; 0 = done.
        /// </summary>
        public int SweepStep(int maxCells, Action<IntVec3> onCell = null)
        {
            if (!sweepActive) return 0;
            if (sweepOrder == null) sweepOrder = RM_TrackPool.SweepOrder(map.Size.x, map.Size.z, sweepAngle);
            int end = Math.Min(sweepOrder.Length, sweepPos + Math.Max(1, maxCells));
            for (; sweepPos < end; sweepPos++)
            {
                int idx = sweepOrder[sweepPos];
                IntVec3 c = map.cellIndices.IndexToCell(idx);
                if (pool != null && pool.Clear(idx)) Dirty(c);
                onCell?.Invoke(c);
            }
            int left = sweepOrder.Length - sweepPos;
            if (left <= 0)
            {
                sweepActive = false;
                sweepOrder = null;
                sweepPos = 0;
            }
            return left;
        }

        public void CancelSweep()
        {
            sweepActive = false;
            sweepOrder = null;
            sweepPos = 0;
        }

        // ── settings ─────────────────────────────────────────────────────

        public void ApplyCapacitySetting()
        {
            if (pool == null) return;
            int cap = RM_CreatureBehaviorsSettings.trackPoolCap;
            if (cap != pool.Capacity)
            {
                pool.Resize(cap);
                map.mapDrawer.WholeMapChanged(RM_TrackDefOf.RM_TrackPrints);
            }
        }

        // ── save ─────────────────────────────────────────────────────────

        public override void ExposeData()
        {
            base.ExposeData();
            byte[] data = null;
            if (Scribe.mode == LoadSaveMode.Saving && pool != null && pool.Count > 0)
            {
                data = pool.ToBytes();
            }
            DataExposeUtility.LookByteArray(ref data, "trackRecords");
            Scribe_Collections.Look(ref styleKeys, "trackStyles", LookMode.Value);
            Scribe_Values.Look(ref sweepActive, "trackSweepActive", false);
            Scribe_Values.Look(ref sweepAngle, "trackSweepAngle", 0f);
            Scribe_Values.Look(ref sweepPos, "trackSweepPos", 0);

            if (Scribe.mode == LoadSaveMode.LoadingVars)
            {
                if (styleKeys == null) styleKeys = new List<string>();
                styleIndex.Clear();
                for (int i = 0; i < styleKeys.Count; i++) styleIndex[styleKeys[i]] = (ushort)i;
                pool = null;
                if (data != null)
                {
                    pool = RM_TrackPool.FromBytes(data, map.Size.x, map.Size.z,
                        RM_CreatureBehaviorsSettings.trackPoolCap, out string error);
                    if (pool == null)
                    {
                        Log.Warning("[RM CreatureBehaviors] track grid not restored (" + error + "); starting empty.");
                    }
                }
            }
        }

        // ── internals ────────────────────────────────────────────────────

        private void EnsurePool()
        {
            if (pool == null)
            {
                pool = new RM_TrackPool(map.Size.x, map.Size.z, RM_CreatureBehaviorsSettings.trackPoolCap);
            }
        }

        private ushort StyleFor(string texPath, float drawSize)
        {
            string key = texPath + "|" + drawSize.ToString("0.###", System.Globalization.CultureInfo.InvariantCulture);
            if (styleIndex.TryGetValue(key, out ushort idx)) return idx;
            if (styleKeys.Count >= ushort.MaxValue) return 0;
            idx = (ushort)styleKeys.Count;
            styleKeys.Add(key);
            styleIndex[key] = idx;
            return idx;
        }

        private void Dirty(IntVec3 c)
        {
            map.mapDrawer.MapMeshDirty(c, RM_TrackDefOf.RM_TrackPrints);
        }
    }
}
