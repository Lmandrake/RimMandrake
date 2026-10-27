// Live round 8 (2026-10-26, 325 basin map, 200 hoses, relay wave) fixes, offline proofs:
//  HOSE_DRAW_FIX_STALLS_WHILE_WORKER_LAYS: the mated end's re-shape (HoseSpliceMath.MateEnd, 11.7 ms mean / 50.7 ms max in
//  the draw) runs on a worker through HoseMateEndQueue.
//   ME1 a queued async re-shape equals a direct MateEnd bit for bit (a real pair from MatePair, the joint copy cleared so
//       the tail solve runs), on the asking frame nothing lands and the next BeginFrame hands it out once;
//   ME2 latest wins: a key asked while its job runs starts nothing; the landed (older-key) result is handed out and the
//       next ask for the newer key starts exactly one job; the key, lay and pair just landed asked again are re-handed the
//       same result with no new solve, a new lay under the same key solves afresh;
//   ME3 budget: 10 reels asking in one frame start MaxStartsPerFrame; MaxInFlight holds across frames; deferrals counted;
//   ME4 a re-shape that throws lands as Result null with Error kept and Faulted/LastFault counted, never escapes.
//  HOSE_RELAY_FIX_BUDGET_STARVES_LATE_REELS:
//   RO1 simulated DrawAll budget over 50 reels that all need work every frame, k served a frame: reel order never serves
//       reels k..49 (the defect, reproduced); HoseDrawRotation serves every reel at least once in every ceil(50/k) frames;
//       with random costs (budget checked before the work, as DrawAll) and random needs over 2000 frames, no reel waits
//       more than 50 frames of continuous need;
//   RO2 source: DrawAll walks drawOrder.At(step), both budgets and the mate deferral record drawOrder.Deferred, the solve
//       goes through MatedLater, and the frame begins the queue.
//  HOSE_LAY_FIX_GARBAGE_FORCES_FULL_GC / HOSE_TICK_FIX_SPIKES_AT_SUPERFAST:
//   LW1 a lay is a function of the world's content only: on the basin, lays on a fresh clone, on one pooled clone reused
//       after other lays, and on a separately built world are bit-identical (hash over double bits, never string hashes,
//       which net8 randomizes per run); source: TakeLayWorld copies World(LayWorldMaxAge), not a fresh World().
using System;
using System.Collections.Generic;
using System.Threading;
using RimMandrake.FlowWorks.Hose;
using RimMandrake.Shared.Slack;

namespace RimMandrake.FlowWorks.SelfTest
{
    internal static class HoseMateEndQueueChecks
    {
        private const double Kmax = 1 / 1.2, Vis = 0.3;

        private static void Assert(bool ok, string msg)
        {
            if (!ok) throw new Exception(msg);
        }

        private static List<V2> Line(V2 a, V2 b, double step)
        {
            var o = new List<V2>();
            int n = Math.Max(2, (int)Math.Ceiling(V2.Dist(a, b) / step));
            for (int i = 0; i <= n; i++)
            {
                double t = (double)i / n;
                o.Add(new V2(a.X + (b.X - a.X) * t, a.Z + (b.Z - a.Z) * t));
            }
            return o;
        }

        private static bool SameBits(List<V2> a, List<V2> b)
        {
            if (a == null || b == null) return a == null && b == null;
            if (a.Count != b.Count) return false;
            for (int i = 0; i < a.Count; i++)
                if (BitConverter.DoubleToInt64Bits(a[i].X) != BitConverter.DoubleToInt64Bits(b[i].X)
                    || BitConverter.DoubleToInt64Bits(a[i].Z) != BitConverter.DoubleToInt64Bits(b[i].Z)) return false;
            return true;
        }

        private static List<V2> Stand(List<V2> p, HoseSpliceMath.Mate m, bool isA, double k, double v, double l)
        {
            var o = new List<V2>(p);
            o.Add(new V2(99, 99));
            return o;
        }

        private static HoseMateEndQueue Sync(Func<List<V2>, HoseSpliceMath.Mate, bool, double, double, double, List<V2>> work, out Func<int> calls)
        {
            int n = 0;
            var q = new HoseMateEndQueue { Async = false };
            q.Work = (p, m, a, k, v, l) => { Interlocked.Increment(ref n); return work(p, m, a, k, v, l); };
            calls = () => Volatile.Read(ref n);
            return q;
        }

        // ---- LW1: a lay's hash from double bits and ints only ----
        private static ulong Mix(ulong h, ulong v) { h ^= v; h *= 1099511628211UL; return h; }
        private static ulong Mix(ulong h, double d) => Mix(h, (ulong)BitConverter.DoubleToInt64Bits(d));
        private static ulong Mix(ulong h, List<V2> p)
        {
            h = Mix(h, (ulong)p.Count);
            foreach (V2 q in p) { h = Mix(h, q.X); h = Mix(h, q.Z); }
            return h;
        }

        internal static ulong LayHash(HoseLay l)
        {
            if (l == null) return 1;
            ulong h = 14695981039346656037UL;
            h = Mix(h, (ulong)((l.Ok ? 1 : 0) | (l.FellBack ? 2 : 0) | (l.Outlet ? 4 : 0) | (l.G2 ? 8 : 0) | (l.LeadShortened ? 16 : 0) | (l.Rerouted ? 32 : 0)));
            h = Mix(h, l.Flat); h = Mix(h, l.Plump); h = Mix(h, l.Centre); h = Mix(h, l.Couplings);
            h = Mix(h, (ulong)l.Joints.Count);
            foreach (int j in l.Joints) h = Mix(h, (ulong)j);
            foreach (double d in new[] { l.PathLen, l.FlatLen, l.PlumpLen, l.MinBendFlat, l.MinBendPlump, l.LeadOutLen, l.Kmax, l.Lead0, l.Lead1 }) h = Mix(h, d);
            return h;
        }

        public static void Run(Action<string, Action> Case)
        {
            Case("ME1 HoseMateEndQueue async re-shape = direct HoseSpliceMath.MateEnd bit for bit (real pair, tail solve)", () =>
            {
                List<V2> A = Line(new V2(0, 0), new V2(10, 0), 0.25), B = Line(new V2(10, 10), new V2(10, 0), 0.25);
                HoseSpliceMath.Mate m0 = HoseSpliceMath.MatePair(A, B, A[A.Count - 1], Kmax, Vis, out _, out _, 0, 0);
                Assert(m0 != null, "fixture pair did not mate");
                // the joint copy cleared: MateEnd runs MateTailG2 (the expensive path the draw paid)
                var m = new HoseSpliceMath.Mate { C = m0.C, Axis = m0.Axis, SeedA = m0.SeedA, SeedB = m0.SeedB, Cost = m0.Cost, PtsA = m0.PtsA, LeadA = m0.LeadA, LeadB = m0.LeadB };
                int solved = 0;
                foreach (bool isA in new[] { true, false })
                {
                    List<V2> pts = isA ? A : B;
                    List<V2> direct = HoseSpliceMath.MateEnd(pts, m, isA, Kmax, Vis, 0);
                    var q = new HoseMateEndQueue();
                    object tag = new object();
                    q.BeginFrame(0);
                    HoseMateEndQueue.Landed got = q.Ask(1, "k", tag, pts, m, isA, Kmax, Vis, 0);
                    Assert(got == null, "async ask handed out a result on the asking frame");
                    Assert(q.Started == 1, $"{q.Started} jobs started (want 1)");
                    Assert(q.Drain(20000), "worker re-shape did not finish in 20 s");
                    q.BeginFrame(1);
                    got = q.Ask(1, "k", tag, pts, m, isA, Kmax, Vis, 0);
                    Assert(got != null, "landed re-shape not handed out on the next frame");
                    Assert(got.Key == "k" && ReferenceEquals(got.Tag, tag) && ReferenceEquals(got.Of, m), "landed key/tag/mate are not the asked ones");
                    Assert(got.Error == null, "re-shape faulted: " + got.Error);
                    Assert(SameBits(got.Result, direct), $"isA={isA}: queued result ({got.Result?.Count}) != direct MateEnd ({direct?.Count})");
                    Assert(SameBits(got.Source, pts), "source pose not the asked pose");
                    int same = 0;
                    if (direct != null) while (same < direct.Count && same < pts.Count && V2.Dist(direct[same], pts[same]) < 1e-9) same++;
                    Assert(got.Same == same, $"shared prefix {got.Same} != {same} (Mated's mateKept)");
                    q.BeginFrame(2);
                    Assert(ReferenceEquals(q.Ask(1, "k", tag, pts, m, isA, Kmax, Vis, 0), got) && q.Started == 1 && q.Taken == 1, "the landed key asked again was not re-handed without a new solve");
                    Assert(q.Ask(1, "k", new object(), pts, m, isA, Kmax, Vis, 0) == null && q.Started == 2, "a new lay (tag) under the same key did not start a fresh solve");
                    if (direct != null) solved++;
                }
                Assert(solved > 0, "neither end re-shaped: the fixture does not exercise the tail solve");
            });
            Case("ME2 HoseMateEndQueue latest wins: one job per reel, the older landed result handed out once, the newer key asked next", () =>
            {
                var gate = new ManualResetEventSlim(false);
                int n = 0;
                var q = new HoseMateEndQueue { Async = true };
                q.Work = (p, m, a, k, v, l) => { Interlocked.Increment(ref n); gate.Wait(10000); return Stand(p, m, a, k, v, l); };
                List<V2> P = Line(new V2(0, 0), new V2(5, 0), 0.5);
                q.BeginFrame(0);
                Assert(q.Ask(3, "k1", null, P, null, true, Kmax, Vis, 0) == null, "k1 handed out before it ran");
                for (int f = 1; f <= 5; f++)
                {
                    q.BeginFrame(f);
                    Assert(q.Ask(3, "k" + (f + 1), null, P, null, true, Kmax, Vis, 0) == null, $"frame {f}: a result while k1 still runs");
                }
                Assert(q.Started == 1 && q.Running(3), $"{q.Started} started while one ran (want 1)");
                gate.Set();
                Assert(q.Drain(5000), "job did not finish");
                q.BeginFrame(6);
                HoseMateEndQueue.Landed got = q.Ask(3, "k7", null, P, null, true, Kmax, Vis, 0);
                Assert(got != null && got.Key == "k1", $"landed {got?.Key ?? "nothing"} (want k1, the job that ran)");
                Assert(got.Result != null && got.Result.Count == P.Count + 1, "stand-in result not carried");
                Assert(q.Started == 2, $"{q.Started} started (want 2: the newer key k7 asked once k1 landed)");
                Assert(q.Drain(5000), "k7 did not finish");
                q.BeginFrame(7);
                got = q.Ask(3, "k7", null, P, null, true, Kmax, Vis, 0);
                Assert(got != null && got.Key == "k7", "k7 not handed out");
                q.BeginFrame(8);
                Assert(ReferenceEquals(q.Ask(3, "k7", null, P, null, true, Kmax, Vis, 0), got) && q.Started == 2, "k7 asked again re-ran or was not re-handed");
                Assert(Volatile.Read(ref n) == 2, $"{n} re-shapes ran (want 2)");
                Assert(q.Taken == 2, $"Taken {q.Taken} (want 2)");
                q.Forget(3);
                Assert(q.Count == 0 && q.InFlight == 0, "Forget left a slot or an in-flight count");
            });
            Case("ME3 HoseMateEndQueue budget: MaxStartsPerFrame starts a frame, MaxInFlight across frames, deferrals counted", () =>
            {
                var q = Sync(Stand, out Func<int> calls);
                q.MaxStartsPerFrame = 4;
                List<V2> P = Line(new V2(0, 0), new V2(5, 0), 0.5);
                q.BeginFrame(0);
                int handed = 0;
                for (int id = 0; id < 10; id++) if (q.Ask(id, "k", null, P, null, true, Kmax, Vis, 0) != null) handed++;
                Assert(calls() == 4 && handed == 4, $"frame 0: {calls()} ran, {handed} handed out (want 4, 4)");
                Assert(q.Deferred == 6, $"Deferred {q.Deferred} (want 6)");
                for (int f = 1; f <= 2; f++)
                {
                    q.BeginFrame(f);
                    for (int id = 0; id < 10; id++) q.Ask(id, "k", null, P, null, true, Kmax, Vis, 0);
                }
                Assert(calls() == 10, $"{calls()} ran after 3 frames (want 10, each reel once)");

                var gate = new ManualResetEventSlim(false);
                var a = new HoseMateEndQueue { Async = true, MaxStartsPerFrame = 10, MaxInFlight = 3 };
                a.Work = (p, m, i, k, v, l) => { gate.Wait(10000); return null; };
                for (int f = 0; f < 3; f++)
                {
                    a.BeginFrame(f);
                    for (int id = 0; id < 10; id++) a.Ask(id, "k", null, P, null, true, Kmax, Vis, 0);
                    Assert(a.InFlight <= 3, $"frame {f}: {a.InFlight} in flight (MaxInFlight 3)");
                }
                Assert(a.Started == 3, $"{a.Started} started while 3 ran (want 3)");
                gate.Set();
                Assert(a.Drain(5000), "jobs did not finish");
                a.BeginFrame(3);
                Assert(a.InFlight == 0, $"{a.InFlight} in flight after landing (want 0)");
            });
            Case("ME4 HoseMateEndQueue: a re-shape that throws lands as no re-shape (Error kept, Faulted counted), never escapes", () =>
            {
                foreach (bool async in new[] { false, true })
                {
                    var q = new HoseMateEndQueue { Async = async };
                    q.Work = (p, m, i, k, v, l) => throw new InvalidOperationException("boom-ME4");
                    List<V2> P = Line(new V2(0, 0), new V2(5, 0), 0.5);
                    q.BeginFrame(0);
                    HoseMateEndQueue.Landed got = q.Ask(9, "k", null, P, null, true, Kmax, Vis, 0);
                    if (async)
                    {
                        Assert(q.Drain(5000), "faulting job did not finish");
                        q.BeginFrame(1);
                        got = q.Ask(9, "k", null, P, null, true, Kmax, Vis, 0);
                    }
                    Assert(got != null && got.Result == null && got.Error != null && got.Error.Contains("boom-ME4"), $"async={async}: fault not landed as Result null + Error");
                    Assert(SameBits(got.Source, P), "fault lost the source pose (the caller draws it)");
                    Assert(q.Faulted == 1 && q.LastFault != null && q.LastFault.Contains("boom-ME4"), $"async={async}: Faulted {q.Faulted}");
                    Assert(ReferenceEquals(q.Ask(9, "k", null, P, null, true, Kmax, Vis, 0), got) && q.Started == 1 && q.Faulted == 1, "faulted key retried (or re-counted) while unchanged");
                }
            });
            Case("RO1 HoseDrawRotation: reel order starves late reels under a full budget; rotation serves each within ceil(N/k) frames", () =>
            {
                const int N = 50;
                foreach (int k in new[] { 1, 3, 7, 16 })
                {
                    int bound = (N + k - 1) / k;
                    foreach (bool rotate in new[] { false, true })
                    {
                        var rot = new HoseDrawRotation();
                        var last = new int[N];
                        var served = new int[N];
                        for (int i = 0; i < N; i++) last[i] = -1;
                        int worstGap = 0;
                        for (int f = 0; f < 10 * bound + 20; f++)
                        {
                            rot.Begin(N, rotate);
                            int spent = 0;
                            for (int step = 0; step < N; step++)
                            {
                                int i = rot.At(step);
                                if (spent >= k) { rot.Deferred(i); continue; }
                                spent++;
                                served[i]++;
                                worstGap = Math.Max(worstGap, f - last[i]);
                                last[i] = f;
                            }
                        }
                        if (!rotate)
                        {
                            for (int i = k; i < N; i++) Assert(served[i] == 0, $"k={k} reel order served reel {i} (the defect did not reproduce)");
                        }
                        else
                        {
                            for (int i = 0; i < N; i++) Assert(served[i] > 0, $"k={k} rotation never served reel {i}");
                            Assert(worstGap <= bound, $"k={k} rotation: a reel waited {worstGap} frames (bound ceil(N/k) = {bound})");
                        }
                    }
                }
                // random costs (the budget is checked before the work, so a call may overshoot it, as in DrawAll) and needs
                var rnd = new Random(8);
                var r2 = new HoseDrawRotation();
                var need = new bool[N];
                var waiting = new int[N];
                int worst = 0, servedAll = 0;
                for (int f = 0; f < 2000; f++)
                {
                    for (int i = 0; i < N; i++) if (!need[i] && rnd.NextDouble() < 0.6) { need[i] = true; waiting[i] = 0; }
                    r2.Begin(N, true);
                    double spent = 0, budget = 8;
                    for (int step = 0; step < N; step++)
                    {
                        int i = r2.At(step);
                        if (!need[i]) continue;
                        if (spent >= budget) { r2.Deferred(i); waiting[i]++; worst = Math.Max(worst, waiting[i]); continue; }
                        spent += 0.2 + rnd.NextDouble() * (rnd.NextDouble() < 0.1 ? 40 : 3);
                        need[i] = false;
                        servedAll++;
                    }
                }
                Assert(worst <= N, $"random load: a reel waited {worst} frames of continuous need (bound N = {N})");
                Console.WriteLine($"    RO1 random load: {servedAll} serves over 2000 frames, worst continuous wait {worst} frames (N={N})");
            });
            Case("RO2 source: DrawAll walks a rotating start; budgets and the mate deferral record it; MateEnd off the frame", () =>
            {
                string s = RiverSwitchFlipChecks.Src(System.IO.Path.Combine("Hose", "RM_MapComponent_Hoses.cs"));
                RiverSwitchFlipChecks.Has(s, @"drawOrder\.Begin\(reels\.Count, !LegacyFrame\);", "DrawAll begins the rotation (reel order under FrameLegacy)");
                RiverSwitchFlipChecks.Has(s, @"for \(int step = 0; step < reels\.Count; step\+\+\) \{ int i = drawOrder\.At\(step\);", "DrawAll walks from the rotating start");
                RiverSwitchFlipChecks.Has(s, @"DeferredRebuildsTotal\+\+; drawOrder\.Deferred\(i\);", "the re-pose budget records its first deferral");
                RiverSwitchFlipChecks.Has(s, @"if \(lastDeferredCross != crossWas\) drawOrder\.Deferred\(i\);", "the crossing-shadow budget records its first deferral");
                RiverSwitchFlipChecks.Has(s, @"if \(LegacyFrame \|\| MateEndIsCopy\(r, mi\)\) pts = Mated\(r, mi, pts\);.{0,400}?else MatedLater\(r, mi, lay, c, i, ref key, ref pts\);", "the end's tail solve goes through the queue");
                RiverSwitchFlipChecks.Has(s, @"if \(!LegacyFrame\) mateEnds\.BeginFrame\(Time\.frameCount\);", "the frame lands finished re-shapes");
                RiverSwitchFlipChecks.Has(s, @"DeferredMatesTotal\+\+; drawOrder\.Deferred\(index\);", "a waiting re-shape records its deferral");
                RiverSwitchFlipChecks.Has(s, @"ReferenceEquals\(got\.Tag, lay\) && ReferenceEquals\(got\.Of, mi\.mate\)", "a landed re-shape is drawn only for the lay and pair it was solved for");
                RiverSwitchFlipChecks.Has(s, @"mateEnds\.Forget\(r\.parent\.thingIDNumber\);", "a deregistered reel's slot is dropped");
            });
            Case("LW1 a lay depends on the world's content only: fresh clone = reused pooled clone = rebuilt world (bit hash); TakeLayWorld uses World(LayWorldMaxAge)", () =>
            {
                CordWorld w = HoseAllocChecks.BasinWorld(out var rigs);
                CordWorld w2 = HoseAllocChecks.BasinWorld(out _);
                CordWorld pooled = w.Clone();
                int[] pick = { 0, 5, 17, 33, 48, 61, 77, 90 };
                int ok = 0;
                for (int t = 0; t < pick.Length; t++)
                {
                    var (cx, z) = rigs[pick[t] % rigs.Count];
                    bool outflow = t % 2 == 1;
                    ulong fresh = LayHash(HoseLayQueue.Compute(w.Clone(), HoseAllocChecks.Inputs(cx, z, outflow)));
                    // the pool's copy has carried every earlier lay of this loop (as a landed job's copy goes back to the pool)
                    HoseLay pl = HoseLayQueue.Compute(pooled, HoseAllocChecks.Inputs(cx, z, outflow));
                    ulong reused = LayHash(pl);
                    ulong rebuilt = LayHash(HoseLayQueue.Compute(w2.Clone(), HoseAllocChecks.Inputs(cx, z, outflow)));
                    Assert(fresh == reused, $"rig {pick[t]}: lay on a reused pooled copy differs from a fresh copy ({fresh:x16} vs {reused:x16})");
                    Assert(fresh == rebuilt, $"rig {pick[t]}: lay on a rebuilt world differs ({fresh:x16} vs {rebuilt:x16})");
                    if (pl != null && pl.Ok) ok++;
                }
                Assert(ok >= pick.Length / 2, $"only {ok}/{pick.Length} lays Ok: the fixture does not exercise real lays");
                string s = RiverSwitchFlipChecks.Src(System.IO.Path.Combine("Hose", "RM_MapComponent_Hoses.cs"));
                RiverSwitchFlipChecks.Has(s, @"CordWorld src = LegacyFrame \? World\(\) : World\(LayWorldMaxAge\);", "TakeLayWorld copies a version-valid snapshot up to LayWorldMaxAge old");
                RiverSwitchFlipChecks.Has(s, @"if \(\(now \+ r\.parent\.thingIDNumber\) % 250 == 0\) TickRecheck\(r, now\);", "the 250-tick recheck is its own profilable method");
                RiverSwitchFlipChecks.Has(s, @"return BuildWorld\(now\);", "the snapshot rebuild is its own profilable method");
            });
        }
    }
}
