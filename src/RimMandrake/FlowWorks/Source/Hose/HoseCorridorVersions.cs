// HOSE_INVALIDATION_REWIRE_EVENT_DRIVEN step 1 (design: design/RimMandrake/hose_wire_algorithms_advisory_2026-10-28.md section 4 #5a).
// Verse-free. A coarse change-version grid: every live cell change bumps its 8x8 chunk's version, so the 250-tick recheck of a
// laid hose can ask "did any cell of my corridor change since I last hashed it?" by reading (corridor area / 64) ints instead
// of hashing every corridor cell. A false "changed" only costs the old full hash; a false "unchanged" would leave a stale hose,
// so every source of change MUST call Touch (cell edits) or TouchAll (rule changes: fog, ladders, climb generation, settings
// salt, a new map size), and the caller keeps a slow phased full-hash audit as the backstop.
// Production wiring (RM_MapComponent_Hoses.CellChanged / TickRecheckBody) is step 2; Replay/ReplayTick.cs mirrors it now.
namespace RimMandrake.FlowWorks.Hose
{
    internal sealed class HoseCorridorVersions
    {
        public const int Shift = 3;   // 8x8 chunks
        private int[] ver = new int[0];
        private int cw, ch, width, height, clock = 1, allAt;

        /// <summary>The current version: a hose records it when it hashes its corridor.</summary>
        public int Now => clock;

        /// <summary>Sized for a w x h world; a new size starts over with everything changed.</summary>
        public void Ensure(int w, int h)
        {
            if (w == width && h == height) return;
            width = w; height = h;
            cw = (w + 7) >> Shift; ch = (h + 7) >> Shift;
            ver = new int[cw * ch];
            TouchAll();
        }

        /// <summary>A cell's state changed (clipped to the world).</summary>
        public void Touch(int x, int z)
        {
            if (x < 0 || z < 0 || x >= width || z >= height) return;
            ver[(z >> Shift) * cw + (x >> Shift)] = ++clock;
        }

        /// <summary>Something every cell's signature reads changed: every corridor counts as changed.</summary>
        public void TouchAll() => allAt = ++clock;

        /// <summary>True when any cell of the inclusive rectangle (clipped) changed after version <paramref name="since"/>.
        /// Out-of-world rectangles read as unchanged only if nothing global changed.</summary>
        public bool ChangedSince(int since, int x0, int z0, int x1, int z1)
        {
            if (allAt > since) return true;
            if (x0 < 0) x0 = 0; if (z0 < 0) z0 = 0;
            if (x1 >= width) x1 = width - 1; if (z1 >= height) z1 = height - 1;
            if (x1 < x0 || z1 < z0) return false;
            int a0 = x0 >> Shift, a1 = x1 >> Shift, b0 = z0 >> Shift, b1 = z1 >> Shift;
            for (int b = b0; b <= b1; b++)
            {
                int row = b * cw;
                for (int a = a0; a <= a1; a++)
                    if (ver[row + a] > since) return true;
            }
            return false;
        }

        /// <summary>Chunks ChangedSince reads for the rectangle (the op count the replay books).</summary>
        public static long ChunksOf(int x0, int z0, int x1, int z1)
            => (long)(((x1 >> Shift) - (x0 >> Shift)) + 1) * (((z1 >> Shift) - (z0 >> Shift)) + 1);
    }
}
