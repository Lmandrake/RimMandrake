// HOSE_FRAME_SHRINK_PER_FRAME_GARBAGE (2026-10-26): the per-frame key memos (HoseFrameMemo.cs) and the mate cache's
// no-rehash hit (HoseMateCache.Entry.SameAsk) must return exactly what the old per-frame code built, and allocate nothing
// while their inputs hold. Allocation is read with GC.GetAllocatedBytesForCurrentThread after a warm-up call.
using System;
using System.Collections.Generic;
using RimMandrake.FlowWorks.Hose;
using RimMandrake.Shared.Slack;

namespace RimMandrake.FlowWorks.SelfTest
{
    internal static class HoseFrameMemoChecks
    {
        private static void Assert(bool ok, string msg)
        {
            if (!ok) throw new Exception(msg);
        }

        private static long Alloc(Action a, int n)
        {
            a();   // warm-up (JIT, first build)
            long b0 = GC.GetAllocatedBytesForCurrentThread();
            for (int i = 0; i < n; i++) a();
            return GC.GetAllocatedBytesForCurrentThread() - b0;
        }

        public static void Run(Action<string, Action> Case)
        {
            Case("F1 HoseDrawKeyMemo: every input combination gives the pre-memo string; each changed input rebuilds it", () =>
            {
                var m = new HoseDrawKeyMemo();
                string[] lays = { "(1, 0, 2)/Scrapper>(5, 0, 2)|1.2|1|1|8|T1|L60", "other", null };
                string[] mates = { null, "00ff00ff00ff00ff" };
                double[] ports = { 0, 1.23456, -0.0004, -0.0 };
                int n = 0;
                foreach (bool settled in new[] { true, false })
                foreach (bool plump in new[] { true, false })
                foreach (int tick in new[] { 0, 60001 })
                foreach (string lay in lays)
                foreach (int rank in new[] { 0, 7 })
                foreach (bool onPort in new[] { false, true })
                foreach (double px in ports)
                foreach (string mate in mates)
                {
                    string want = (settled ? (plump ? "P" : "F") : "T" + tick) + lay + "@" + rank;
                    if (onPort) want += "|p" + px.ToString("0.000") + "," + (px * 2).ToString("0.000");
                    if (mate != null) want += "|m" + mate;
                    string got = m.Get(settled, plump, tick, lay, rank, onPort, px, px * 2, mate);
                    Assert(got == want, $"memo '{got}' != pre-memo '{want}'");
                    Assert(ReferenceEquals(m.Get(settled, plump, tick, lay, rank, onPort, px, px * 2, mate), got), "same inputs built a new string");
                    n++;
                }
                Assert(n == 768, $"{n} combinations walked (want 768)");
                // a tick change re-keys only a transitioning pose; a port change only when on a port
                string s1 = m.Get(true, true, 1, "L", 0, false, 0, 0, null);
                Assert(ReferenceEquals(m.Get(true, true, 2, "L", 0, false, 9, 9, null), s1), "settled pose re-keyed on tick or an unused port");
                string t1 = m.Get(false, true, 1, "L", 0, false, 0, 0, null);
                Assert(m.Get(false, true, 2, "L", 0, false, 0, 0, null) == "T2L@0" && t1 == "T1L@0", "transitioning pose not re-keyed per tick");
                // a layKey with the same text in a new instance hits (string equality, not identity)
                string a = m.Get(true, false, 0, new string('k', 3), 2, false, 0, 0, null);
                Assert(ReferenceEquals(m.Get(true, false, 0, new string('k', 3), 2, false, 0, 0, null), a), "equal layKey text missed");
            });
            Case("F2 HoseDrawKeyMemo: a held key allocates nothing over 10000 frames (was a new string per hose per frame)", () =>
            {
                var m = new HoseDrawKeyMemo();
                string lay = "(1, 0, 2)/Scrapper>(5, 0, 2)", mate = "00ff00ff00ff00ff";
                long memo = Alloc(() => m.Get(true, true, 5, lay, 3, true, 1.5, 2.5, mate), 10000);
                long old = Alloc(() => HoseDrawKeyMemo.Build(true, true, 5, lay, 3, true, 1.5, 2.5, mate), 10000);
                Console.WriteLine($"    draw key: memo {memo} B / 10000 frames, pre-memo {old} B");
                Assert(memo == 0, $"memo allocated {memo} bytes over 10000 held frames");
                Assert(old > 10000 * 100, $"pre-memo build allocated only {old} bytes (instrument blind?)");
            });
            Case("F3 HoseLayKeyMemo: Same holds only for the stored inputs; any one changed input misses; no allocation", () =>
            {
                var m = new HoseLayKeyMemo();
                Assert(!m.Same(1, 0, 2, "S", 5, 0, 2, false, 0, null, false, 0, 0, "fp", false, false, 0, 0, 0, 0), "empty memo hit");
                m.Store(1, 0, 2, "S", 5, 0, 2, true, 9, "R", true, 3, 77, "fp", true, true, 1.5, 2.5, 1, 0, "KEY");
                Func<int, bool> same = k => m.Same(k == 0 ? 2 : 1, k == 1 ? 1 : 0, 2, k == 2 ? "X" : "S", 5, 0, k == 3 ? 3 : 2, k != 4, k == 5 ? 8 : 9,
                    k == 6 ? "Q" : "R", k != 7, k == 8 ? 4 : 3, k == 9 ? 78UL : 77UL, k == 10 ? "fq" : "fp", k != 11, k != 12,
                    k == 13 ? 1.5000001 : 1.5, 2.5, k == 14 ? -1 : 1, k == 15 ? -0.0 : 0);
                Assert(same(-1) && m.Key == "KEY", "stored inputs missed");
                for (int k = 0; k <= 15; k++) Assert(!same(k), $"input {k} changed but the memo still hit");
                Assert(m.Same(1, 0, 2, new string('S', 1), 5, 0, 2, true, 9, "R", true, 3, 77, "fp", true, true, 1.5, 2.5, 1, 0), "equal text in a new string missed");
                long b = Alloc(() => m.Same(1, 0, 2, "S", 5, 0, 2, true, 9, "R", true, 3, 77, "fp", true, true, 1.5, 2.5, 1, 0), 10000);
                Assert(b == 0, $"Same allocated {b} bytes");
            });
            Case("F4 HoseMateCache: a hit on the same lay lists re-hashes nothing and allocates nothing; a new instance still re-hashes to a hit", () =>
            {
                var c = new HoseMateCache { Async = false };
                int solves = 0;
                c.Solver = (A, B, k, v, la, lb) => { solves++; return new HoseSpliceMath.Mate { C = A[A.Count - 1], Axis = new V2(1, 0), Cost = 1 }; };
                var A0 = new List<V2>(); var B0 = new List<V2>();
                for (int i = 0; i <= 400; i++) { A0.Add(new V2(i * 0.025, 0)); B0.Add(new V2(10, 10 - i * 0.025)); }
                c.BeginFrame(0);
                HoseMateCache.Entry e = c.Get(1, A0, B0, 0.8, 0.3, 0.6, 0.6);
                Assert(e != null && solves == 1, "first ask did not solve");
                int f = 1;
                long b = Alloc(() => { c.BeginFrame(f++); c.Get(1, A0, B0, 0.8, 0.3, 0.6, 0.6); }, 10000);
                Assert(b == 0, $"held pair allocated {b} bytes over 10000 frames");
                Assert(solves == 1 && c.Reused == 10001, $"solves {solves}, reused {c.Reused} (want 1, 10001)");
                // a re-lay to the same points (new instances): key re-hashed, still a hit, and the new instances are remembered
                var A1 = new List<V2>(A0); var B1 = new List<V2>(B0);
                c.BeginFrame(f++);
                Assert(ReferenceEquals(c.Get(1, A1, B1, 0.8, 0.3, 0.6, 0.6), e) && solves == 1, "same points in new lists re-solved");
                Assert(e.SameAsk(A1, B1, 0.8, 0.3, 0.6, 0.6), "new instances not remembered after the hit");
                // a changed scalar is never served from the instance memo
                c.BeginFrame(f++);
                c.Get(1, A1, B1, 0.8, 0.3, 0.3, 0.6);
                Assert(solves == 2, $"a changed lead-out on the same lists did not re-solve (solves {solves})");
                bool g2 = HoseMath.G2On;
                try
                {
                    HoseMath.G2On = !g2;
                    c.BeginFrame(f++);
                    c.Get(1, A1, B1, 0.8, 0.3, 0.3, 0.6);
                    Assert(solves == 3, $"a G2 switch on the same lists did not re-solve (solves {solves})");
                }
                finally { HoseMath.G2On = g2; }
            });
        }
    }
}
