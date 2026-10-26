// HOSE_FRAME_FIX_CHOKES_325_BASIN_MAP (ticking half, 2026-10-26): the hose pair solve (HoseSpliceMath.MatePair, 1.2-1.9 s
// each on the 325 basin map) ran synchronously in the draw every time a 250-tick re-lay made a new HoseLay, even to the same
// shape. HoseMateCache keys a pair on the solve's inputs and moves changed pairs off the frame. Cases:
//  M1 unchanged inputs (fresh list instances, sub-1e-3 jitter) re-solve nothing across frames;
//  M2 a moved end re-solves exactly once;
//  M3 sync budget: 6 pairs changed in one frame -> at most MaxStartsPerFrame solves a frame, all solved within 6 frames;
//  M4 async: a 400 ms solver never costs the asking frame more than 50 ms, and its result lands on a later BeginFrame;
//  M5 the default solver through the cache returns what MatePair returns for the same inputs (90-degree case).
using System;
using System.Collections.Generic;
using System.Diagnostics;
using System.Threading;
using RimMandrake.FlowWorks.Hose;
using RimMandrake.Shared.Slack;

namespace RimMandrake.FlowWorks.SelfTest
{
    internal static class HoseMateCacheChecks
    {
        private const double Kmax = 1 / 1.2, Vis = 0.3;

        private static void Assert(bool ok, string msg)
        {
            if (!ok) throw new Exception(msg);
        }

        private static List<V2> Line(V2 a, V2 b, double step, double jitter = 0)
        {
            var o = new List<V2>();
            int n = Math.Max(2, (int)Math.Ceiling(V2.Dist(a, b) / step));
            for (int i = 0; i <= n; i++)
            {
                double t = (double)i / n;
                o.Add(new V2(a.X + (b.X - a.X) * t + jitter * ((i % 3) - 1), a.Z + (b.Z - a.Z) * t - jitter * ((i % 2) * 2 - 1)));
            }
            return o;
        }

        private static HoseMateCache Counting(out Func<int> calls, int sleepMs = 0)
        {
            int n = 0;
            var c = new HoseMateCache { Async = false };
            c.Solver = (A, B, k, v, la, lb) =>
            {
                Interlocked.Increment(ref n);
                if (sleepMs > 0) Thread.Sleep(sleepMs);
                return new HoseSpliceMath.Mate { C = A[A.Count - 1], Axis = new V2(1, 0), Cost = 1 };
            };
            calls = () => Volatile.Read(ref n);
            return c;
        }

        public static void Run(Action<string, Action> Case)
        {
            Case("M1 HoseMateCache: a re-lay to the same shape (new list instances, 1e-4 jitter) re-solves nothing over 50 frames", () =>
            {
                HoseMateCache c = Counting(out Func<int> calls);
                for (int f = 0; f < 50; f++)
                {
                    c.BeginFrame(f);
                    List<V2> A = Line(new V2(0, 0), new V2(10, 0), 0.25, f == 0 ? 0 : 1e-4);
                    List<V2> B = Line(new V2(10, 10), new V2(10, 0), 0.25, f == 0 ? 0 : 1e-4);
                    HoseMateCache.Entry e = c.Get(1, A, B, Kmax, Vis, 0.6, 0.6);
                    Assert(e != null && e.mate != null, $"frame {f}: no entry");
                }
                Assert(calls() == 1, $"{calls()} solves for one unchanged pair over 50 frames (want 1)");
                Assert(c.Reused == 49, $"reused {c.Reused} (want 49)");
            });
            Case("M2 HoseMateCache: an end that moves re-solves its pair exactly once; a changed lead-out counts as a move", () =>
            {
                HoseMateCache c = Counting(out Func<int> calls);
                List<V2> A = Line(new V2(0, 0), new V2(10, 0), 0.25), B = Line(new V2(10, 10), new V2(10, 0), 0.25);
                c.BeginFrame(0); c.Get(1, A, B, Kmax, Vis, 0.6, 0.6);
                List<V2> B2 = Line(new V2(10, 10), new V2(10.4, 0), 0.25);
                for (int f = 1; f < 10; f++) { c.BeginFrame(f); c.Get(1, A, B2, Kmax, Vis, 0.6, 0.6); }
                Assert(calls() == 2, $"{calls()} solves after one move (want 2)");
                c.BeginFrame(10); c.Get(1, A, B2, Kmax, Vis, 0.3, 0.6);
                Assert(calls() == 3, $"{calls()} solves after a lead-out change (want 3)");
            });
            Case("M3 HoseMateCache: six pairs changed at once cost at most one solve a frame and are all solved by frame 6", () =>
            {
                HoseMateCache c = Counting(out Func<int> calls);
                c.MaxStartsPerFrame = 1;
                var solvedAt = new int[6];
                for (int f = 0; f < 6; f++)
                {
                    c.BeginFrame(f);
                    int before = calls();
                    for (int p = 0; p < 6; p++)
                    {
                        List<V2> A = Line(new V2(0, 3 * p), new V2(10, 3 * p), 0.25), B = Line(new V2(20, 3 * p), new V2(10.2, 3 * p), 0.25);
                        if (c.Get(p, A, B, Kmax, Vis, 0.6, 0.6) != null && solvedAt[p] == 0) solvedAt[p] = f + 1;
                    }
                    Assert(calls() - before <= 1, $"frame {f}: {calls() - before} solves (budget 1)");
                }
                for (int p = 0; p < 6; p++) Assert(solvedAt[p] > 0, $"pair {p} never solved in 6 frames");
                Assert(c.Deferred > 0, "the budget never deferred anything (instrument blind?)");
            });
            Case("M4 HoseMateCache async: a 400 ms solve never holds the asking frame past 50 ms; it lands on a later frame", () =>
            {
                HoseMateCache c = Counting(out Func<int> calls, 400);
                c.Async = true;
                c.MaxInFlight = 2;
                List<V2> A = Line(new V2(0, 0), new V2(10, 0), 0.25), B = Line(new V2(10, 10), new V2(10, 0), 0.25);
                var sw = Stopwatch.StartNew();
                c.BeginFrame(0);
                HoseMateCache.Entry e = null;
                for (int p = 0; p < 4; p++) e = c.Get(p, A, B, Kmax, Vis, 0.6, 0.6) ?? e;
                long ms = sw.ElapsedMilliseconds;
                Assert(e == null, "a worker solve returned an entry inside the asking frame");
                Assert(ms < 50, $"asking frame took {ms} ms with a 400 ms solver (want < 50)");
                Assert(c.Pending == 1, $"{c.Pending} pending after frame 0 (budget: 1 start a frame)");
                Assert(c.Drain(5000), "worker solve did not finish in 5 s");
                c.BeginFrame(1);
                e = c.Get(0, A, B, Kmax, Vis, 0.6, 0.6);
                Assert(e != null && e.mate != null, "worker result not harvested on the next frame");
                Assert(calls() == 1, $"{calls()} solves (want 1)");
            });
            Case("M5 HoseMateCache default solver = HoseSpliceMath.MatePair for the same inputs (90 degrees)", () =>
            {
                var c = new HoseMateCache { Async = false };
                List<V2> A = Line(new V2(0, 0), new V2(10, 0), 0.25), B = Line(new V2(10, 10), new V2(10, 0), 0.25);
                c.BeginFrame(0);
                HoseMateCache.Entry e = c.Get(7, A, B, Kmax, Vis, 0, 0);
                HoseSpliceMath.Mate m = HoseSpliceMath.MatePair(A, B, A[A.Count - 1], Kmax, Vis, out _, out _, 0, 0);
                Assert(e != null, "sync solve returned no entry");
                Assert((e.mate == null) == (m == null), "cache and direct solve disagree on whether a mate exists");
                if (m != null) Assert(V2.Dist(e.mate.C, m.C) < 1e-9 && V2.Dist(e.mate.Axis, m.Axis) < 1e-9 && Math.Abs(e.mate.Cost - m.Cost) < 1e-9,
                    $"cache mate C {e.mate.C} axis {e.mate.Axis} != direct C {m.C} axis {m.Axis}");
            });
        }
    }
}
