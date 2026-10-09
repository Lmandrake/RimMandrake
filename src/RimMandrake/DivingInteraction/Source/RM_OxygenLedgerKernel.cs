// DESIGN_PASS DI-2 (CHILL_AIR_PUMP_1). Verse-free kernel of the Chill's pumped-air ledger: which cells are
// oxygenated because at least one air provider covers them. Per-provider cell sets plus a per-cell count, so two
// pumps sharing a room keep it lit until BOTH stop (a bare set would let the first pump to stop clear the room).
// SelfTest/DivingFuzz.cs compiles this file alone, so it must stay free of Verse/RimWorld/UnityEngine.
using System.Collections.Generic;

namespace RimMandrake.DivingInteraction
{
    public sealed class RM_OxygenLedgerKernel
    {
        private readonly Dictionary<int, HashSet<int>> byProvider = new Dictionary<int, HashSet<int>>();
        private readonly Dictionary<int, int> counts = new Dictionary<int, int>();

        public int ProviderCount => byProvider.Count;
        public int CoveredCellCount => counts.Count;

        public bool Covered(int cell) { return counts.ContainsKey(cell); }

        public int CoverCount(int cell) { return counts.TryGetValue(cell, out int n) ? n : 0; }

        /// <summary>Replace what one provider covers. Null or empty = the provider covers nothing (same as Clear).
        /// Duplicate cells in the input count once.</summary>
        public void Set(int provider, IEnumerable<int> cells)
        {
            Clear(provider);
            if (cells == null) return;
            var set = new HashSet<int>(cells);
            if (set.Count == 0) return;
            byProvider[provider] = set;
            foreach (int c in set)
            {
                counts[c] = CoverCount(c) + 1;
            }
        }

        public void Clear(int provider)
        {
            if (!byProvider.TryGetValue(provider, out HashSet<int> old)) return;
            byProvider.Remove(provider);
            foreach (int c in old)
            {
                int n = CoverCount(c) - 1;
                if (n <= 0) counts.Remove(c); else counts[c] = n;
            }
        }

        public void Reset()
        {
            byProvider.Clear();
            counts.Clear();
        }

        /// <summary>A room is served when it is sealed and its size fits the pooled capacity of the live pumps in it.
        /// cellsPerPump &lt;= 0 = no size limit.</summary>
        public static bool RoomServed(bool sealedRoom, int roomCells, int livePumpsInRoom, int cellsPerPump)
        {
            if (!sealedRoom || roomCells <= 0 || livePumpsInRoom <= 0) return false;
            if (cellsPerPump <= 0) return true;
            return (long)roomCells <= (long)cellsPerPump * livePumpsInRoom;
        }
    }
}
