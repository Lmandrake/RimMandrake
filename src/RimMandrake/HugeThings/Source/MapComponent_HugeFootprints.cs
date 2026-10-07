using System.Collections.Generic;
using Verse;

namespace RimMandrake.HugeThings
{
    /// <summary>
    /// Drives every huge plant's trunk on one map. Plants register on spawn; a newly registered plant is
    /// refreshed on the next tick (so a plant spawned during map generation gets its trunk only after
    /// generation finishes - FinalizeInit), and every plant is refreshed every RefreshInterval ticks so the
    /// trunk follows growth. Plants never tick normally (only TickLong), which is why this lives here and
    /// not in a comp tick.
    /// </summary>
    public class MapComponent_HugeFootprints : MapComponent
    {
        public const int RefreshInterval = 2000;

        private readonly HashSet<CompHugeFootprint> all = new HashSet<CompHugeFootprint>();
        private readonly HashSet<CompHugeFootprint> dirty = new HashSet<CompHugeFootprint>();
        private readonly List<CompHugeFootprint> tmp = new List<CompHugeFootprint>();

        public MapComponent_HugeFootprints(Map map) : base(map) { }

        public int Count => all.Count;

        public void Register(CompHugeFootprint c)
        {
            all.Add(c);
            dirty.Add(c);
        }

        public void Deregister(CompHugeFootprint c)
        {
            all.Remove(c);
            dirty.Remove(c);
        }

        public void MarkAllDirty()
        {
            foreach (CompHugeFootprint c in all) dirty.Add(c);
        }

        public override void FinalizeInit()
        {
            base.FinalizeInit();
            Flush();
        }

        public override void MapComponentTick()
        {
            base.MapComponentTick();
            if (Find.TickManager.TicksGame % RefreshInterval == 0) MarkAllDirty();
            if (dirty.Count > 0) Flush();
        }

        public void Flush()
        {
            tmp.Clear();
            tmp.AddRange(dirty);
            dirty.Clear();
            for (int i = 0; i < tmp.Count; i++)
            {
                try
                {
                    tmp[i].Refresh();
                }
                catch (System.Exception e)
                {
                    Log.ErrorOnce("[RimMandrake.HugeThings] trunk refresh failed for " + tmp[i].parent + ": " + e,
                                  tmp[i].parent.thingIDNumber ^ 0x4875);
                }
            }
            tmp.Clear();
        }

        /// <summary>Called when Mod Settings change: re-shape every trunk on every map now.</summary>
        public static void RefreshAllMaps()
        {
            if (Current.Game == null) return;
            foreach (Map m in Find.Maps)
            {
                MapComponent_HugeFootprints mc = m.GetComponent<MapComponent_HugeFootprints>();
                if (mc == null) continue;
                mc.MarkAllDirty();
                mc.Flush();
            }
        }
    }
}
