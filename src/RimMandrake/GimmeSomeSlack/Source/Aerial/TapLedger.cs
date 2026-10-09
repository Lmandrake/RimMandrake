using System.Collections.Generic;
using System.Linq;

namespace RimMandrake.GimmeSomeSlack.Aerial
{
    /// <summary>TAP_CONSERVATION_SELFTEST_1 (GS-6a). The per-tick debit book behind the power tap, Verse-free so the
    /// selftest drives the PRODUCTION ledger across many ticks (TapRegistry keys it by PowerNet and feeds it TicksGame).
    /// A debit written at tick T is owed to the net tick that reads T and to no other.</summary>
    public sealed class TapLedger<TKey>
    {
        private struct Entry { public int tick; public float wd; }
        private readonly Dictionary<TKey, Entry> debits = new Dictionary<TKey, Entry>();
        public int Count => debits.Count;

        public void Debit(TKey net, float wd, int now)
        {
            debits.TryGetValue(net, out Entry e);
            if (e.tick != now) { e.tick = now; e.wd = 0f; }
            e.wd += wd;
            debits[net] = e;
            if (debits.Count > 64) Prune(now);
        }

        public float TakenThisTick(TKey net, int now)
        {
            if (net == null || !debits.TryGetValue(net, out Entry e)) return 0f;
            return e.tick == now ? e.wd : 0f;
        }

        public float Owed(TKey net, int now)
        {
            if (debits.Count == 0 || !debits.TryGetValue(net, out Entry e)) return 0f;
            return e.tick == now ? e.wd : 0f;
        }

        private void Prune(int now)
        {
            foreach (TKey n in debits.Where(kv => kv.Value.tick < now - 2).Select(kv => kv.Key).ToList()) debits.Remove(n);
        }

        public void Clear() => debits.Clear();
    }
}
