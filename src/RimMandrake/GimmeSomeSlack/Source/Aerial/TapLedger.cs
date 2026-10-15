using System;
using System.Collections.Generic;
using System.Linq;

namespace RimMandrake.GimmeSomeSlack.Aerial
{
    /// <summary>TAP_CONSERVATION_SELFTEST_1 (GS-6a). The per-tick debit book behind the power tap, Verse-free so the
    /// selftest drives the PRODUCTION ledger across many ticks (TapRegistry feeds it TicksGame). A debit written at tick T is
    /// owed to the net tick that reads T and to no other. GPT pre-release C1: TapRegistry keys it by the bitten TRANSMITTER
    /// (stable) and settles by net membership (<see cref="OwedWhere"/>), so a victim-net rebuild between a debit and its
    /// settlement (new PowerNet objects) no longer orphans the debit.</summary>
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

        /// <summary>The debits written at <paramref name="now"/> by every key <paramref name="member"/> places in
        /// <paramref name="net"/> (a static delegate and a struct enumerator: no allocation on the hot path).</summary>
        public float OwedWhere<TNet>(TNet net, Func<TKey, TNet, bool> member, int now)
        {
            if (debits.Count == 0) return 0f;
            float s = 0f;
            foreach (KeyValuePair<TKey, Entry> kv in debits)
                if (kv.Value.tick == now && member(kv.Key, net)) s += kv.Value.wd;
            return s;
        }

        /// <summary>Drop debits too old to be settled (written before now - 2).</summary>
        public void Prune(int now)
        {
            foreach (TKey n in debits.Where(kv => kv.Value.tick < now - 2).Select(kv => kv.Key).ToList()) debits.Remove(n);
        }

        public void Clear() => debits.Clear();
    }
}
