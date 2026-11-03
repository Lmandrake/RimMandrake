// GSS_BUILD_FIX_SLICE_GROWS_WITH_CORDS round 10 (live round 9, 2026-10-27): the one slice over the 20 ms bar was a window's
// first slice, 44.6 ms with no collection counted, in which every allocating phase ran 10-100x its usual time (snapshot clone
// 20.5 ms against 0.18, publish tail 14.8 against ~1.2) and the heap grew 2.2 MB. Under Unity's incremental collector
// (gcIncremental true) an allocation pays collection work that GC.CollectionCount never sees, so the slice's own garbage
// was the cost. The biggest share was the snapshot: every rebuild cloned the cached base into a NEW whole-map CordWorld
// (~0.85 MB on a 325 map, more with busy and band grids). This pool refills a retired world in place instead.
using System.Collections.Generic;
using RimMandrake.Shared.Slack;

namespace RimMandrake.GimmeSomeSlack.Core
{
    /// <summary>Retired snapshot worlds, refilled in place (<see cref="CordWorld.CopyFrom"/>) rather than allocated per
    /// rebuild. A world is retired when a newer snapshot replaces it; it is handed out again only when nothing still reads
    /// it: <see cref="CordBuilder.HeldWorlds"/> names every world the builder's graph, plan, lay worker or graph worker may
    /// still read (a worker reads its Build's world after that Build returned). A held world stays in the pool and is
    /// skipped. Main thread only.</summary>
    internal sealed class SnapshotPool
    {
        /// <summary>Retired worlds kept; one more is dropped to the collector (the pool never grows past this).</summary>
        public const int Cap = 4;
        private readonly List<CordWorld> free = new List<CordWorld>();
        private readonly List<CordWorld> held = new List<CordWorld>();
        /// <summary>Snapshots served by refilling a retired world / by allocating a new one (no free world of that size).</summary>
        public int Reused, Allocated;

        public int Count => free.Count;

        /// <summary>A world that reads exactly as <c>src.Clone()</c>: a free retired world refilled from src, else a clone.
        /// <paramref name="builder"/> (may be null) names the worlds that must not be refilled.</summary>
        public CordWorld Take(CordWorld src, CordBuilder builder)
        {
            held.Clear();
            builder?.HeldWorlds(held);
            for (int i = free.Count - 1; i >= 0; i--)
            {
                CordWorld w = free[i];
                if (w.Width != src.Width || w.Height != src.Height || ReferenceEquals(w, src) || IsHeld(w)) continue;
                free.RemoveAt(i);
                w.CopyFrom(src);
                Reused++;
                return w;
            }
            Allocated++;
            return src.Clone();
        }

        /// <summary>A snapshot no longer current (the caller's last world): kept for a later <see cref="Take"/>.</summary>
        public void Retire(CordWorld w)
        {
            if (w == null) return;
            for (int i = 0; i < free.Count; i++) if (ReferenceEquals(free[i], w)) return;
            if (free.Count >= Cap) free.RemoveAt(0);
            free.Add(w);
        }

        public void Clear() => free.Clear();

        private bool IsHeld(CordWorld w)
        {
            for (int i = 0; i < held.Count; i++) if (ReferenceEquals(held[i], w)) return true;
            return false;
        }
    }
}
