// HOSE_LAY_FIX_SYNC_RELAY_IN_DRAW (2026-10-26): hose re-lays ran synchronously in DrawAll and the 250-tick check; a maxLength
// change re-laid all 150 hoses of the 325 basin map in ONE 90.5 s frame (live wave 3, tprof_T3). HoseLayQueue moves the
// draw's and tick's lays off the frame. Cases:
//  L1 unchanged key: the queue is never asked (EnsureLay's own key check) -- and an ask for a reel whose job landed and was
//     applied starts nothing new while the caller's key equals the applied one;
//  L2 the budget: 150 changed keys asked in one frame (a settings change), each lay a 400 ms stand-in, async: no asking
//     frame costs more than 50 ms, at most MaxStartsPerFrame start a frame and never more than MaxInFlight run, and every one
//     of the 150 lands and is applied within the drain;
//  L3 sync mode budget: 10 changed keys -> MaxStartsPerFrame lays a frame, all 10 within 3 frames;
//  L4 a key that moves while its job runs: the landed lay comes back under ITS key (Behind), the next ask starts exactly one
//     job for the new key, and a lay is never handed back under a key it was not made for;
//  L5 a lay that throws is a fault (LastFault kept), not retried while the key holds; a new key is tried;
//  L6 Compute on a CordWorld copy lays what the synchronous path (LayFromOn on the snapshot) lays, and leaves both the copy
//     and the snapshot as they were (the reel's footprint is restored), Clone copies every cell;
//  L7 source: DrawAll and the tick ask EnsureLay(r, true), the deferred path is skipped under FrameLegacy, and LayFrom's body
//     is the queue's LayFromOn (one body, no drift).
using System;
using System.Collections.Generic;
using System.Diagnostics;
using System.Threading;
using RimMandrake.FlowWorks.Hose;
using RimMandrake.Shared.Slack;

namespace RimMandrake.FlowWorks.SelfTest
{
    internal static class HoseLayQueueChecks
    {
        private static void Assert(bool ok, string msg)
        {
            if (!ok) throw new Exception(msg);
        }

        private static HoseLayQueue.Work Stand(Action body, HoseLay result = null)
        {
            return new HoseLayQueue.Work { Run = () => { body(); return result ?? new HoseLay { Ok = true }; } };
        }

        public static void Run(Action<string, Action> Case)
        {
            Case("L1 HoseLayQueue: a landed, applied key asked again starts no lay (100 frames)", () =>
            {
                var q = new HoseLayQueue { Async = false };
                int runs = 0;
                Func<HoseLayQueue.Work> prep = () => Stand(() => runs++);
                string applied = null;
                for (int f = 0; f < 100; f++)
                {
                    q.BeginFrame(f);
                    // the component asks only on a mismatch (EnsureLay: r.layKey == key returns the cached lay)
                    if (applied == "k1") continue;
                    HoseLayQueue.Job j = q.Ask(7, "k1", prep);
                    if (j != null) applied = j.key;
                }
                Assert(runs == 1 && q.Started == 1 && q.Taken == 1, $"one lay for one key, got runs {runs} started {q.Started}");
            });

            Case("L2 HoseLayQueue: 150 re-lays of 400 ms asked in one frame never cost an asking frame > 50 ms; budgets hold; all land", () =>
            {
                var q = new HoseLayQueue { Async = true, MaxStartsPerFrame = 4, MaxInFlight = 4 };
                int running = 0, peak = 0;
                Func<HoseLayQueue.Work> prep = () => Stand(() =>
                {
                    int now = Interlocked.Increment(ref running);
                    int p;
                    while ((p = Volatile.Read(ref peak)) < now && Interlocked.CompareExchange(ref peak, now, p) != p) { }
                    Thread.Sleep(400);
                    Interlocked.Decrement(ref running);
                });
                const int N = 150;
                var applied = new string[N];
                long worstMs = 0, startsBefore = 0;
                int maxStartsInFrame = 0, f = 0;
                var total = Stopwatch.StartNew();
                while (total.ElapsedMilliseconds < 60000)
                {
                    q.BeginFrame(f++);
                    var frame = Stopwatch.StartNew();
                    int left = 0;
                    for (int id = 0; id < N; id++)
                    {
                        if (applied[id] == "s2") continue;   // EnsureLay's key check
                        left++;
                        HoseLayQueue.Job j = q.Ask(id, "s2", prep);
                        if (j != null) applied[id] = j.key;
                    }
                    worstMs = Math.Max(worstMs, frame.ElapsedMilliseconds);
                    maxStartsInFrame = Math.Max(maxStartsInFrame, (int)(q.Started - startsBefore));
                    startsBefore = q.Started;
                    if (left == 0) break;
                    Thread.Sleep(16);
                }
                int done = 0;
                foreach (string a in applied) if (a == "s2") done++;
                Assert(done == N, $"all {N} re-lays land and apply, got {done} in {total.ElapsedMilliseconds} ms ({q.Json()})");
                Assert(worstMs <= 50, $"no asking frame > 50 ms, worst {worstMs} ms");
                Assert(maxStartsInFrame <= 4, $"at most 4 starts a frame, saw {maxStartsInFrame}");
                Assert(peak <= 4 && peak >= 1, $"at most MaxInFlight=4 lays at once, peak {peak}");
                Assert(q.Started == N && q.Taken == N && q.Faulted == 0, $"one lay each: {q.Json()}");
                Assert(q.Deferred > 0, "can-fail: the budget actually deferred asks");
            });

            Case("L3 HoseLayQueue sync: 10 changed keys lay at most MaxStartsPerFrame a frame, all within 3 frames", () =>
            {
                var q = new HoseLayQueue { Async = false, MaxStartsPerFrame = 4 };
                var applied = new HashSet<int>();
                int[] perFrame = new int[5];
                for (int f = 0; f < 5; f++)
                {
                    q.BeginFrame(f);
                    for (int id = 0; id < 10; id++)
                    {
                        if (applied.Contains(id)) continue;
                        if (q.Ask(id, "k", () => Stand(() => { })) != null) { applied.Add(id); perFrame[f]++; }
                    }
                }
                Assert(perFrame[0] == 4 && perFrame[1] == 4 && perFrame[2] == 2 && applied.Count == 10, $"4/4/2, got {string.Join("/", perFrame)}");
            });

            Case("L4 HoseLayQueue: a key that moves mid-lay gets its landed lay under the OLD key, then exactly one job for the new key", () =>
            {
                var q = new HoseLayQueue { Async = true, MaxStartsPerFrame = 4, MaxInFlight = 2 };
                var gate = new ManualResetEventSlim(false);
                var made = new List<string>();
                Func<string, Func<HoseLayQueue.Work>> prepFor = k => () => new HoseLayQueue.Work
                {
                    Run = () => { if (k == "a") gate.Wait(5000); lock (made) made.Add(k); return new HoseLay { Ok = true, Reason = k }; },
                };
                q.BeginFrame(0);
                Assert(q.Ask(1, "a", prepFor("a")) == null && q.Running(1), "job a started");
                q.BeginFrame(1);
                Assert(q.Ask(1, "b", prepFor("b")) == null && q.Started == 1, "b waits for a (one job a reel)");
                gate.Set();
                Assert(q.Drain(5000), "a lands");
                q.BeginFrame(2);
                HoseLayQueue.Job j = q.Ask(1, "b", prepFor("b"));
                Assert(j != null && j.key == "a" && j.result.Reason == "a" && q.Behind == 1, $"a's lay comes back under a, got {j?.key}");
                HoseLayQueue.Job j2 = q.Ask(1, "b", prepFor("b"));
                Assert(j2 == null && q.Started == 2, "the caller's second ask starts b");
                Assert(q.Drain(5000), "b lands");
                q.BeginFrame(3);
                HoseLayQueue.Job jb = q.Ask(1, "b", prepFor("b"));
                Assert(jb != null && jb.key == "b" && jb.result.Reason == "b", "b's lay under b");
                Assert(made.Count == 2 && q.Started == 2, $"two lays, got {made.Count}");
            });

            Case("L5 HoseLayQueue: a lay that throws is a fault, not retried while its key holds; a new key is tried", () =>
            {
                var q = new HoseLayQueue { Async = false };
                int runs = 0;
                Func<HoseLayQueue.Work> boom = () => new HoseLayQueue.Work { Run = () => { runs++; throw new InvalidOperationException("boom"); } };
                for (int f = 0; f < 20; f++) { q.BeginFrame(f); Assert(q.Ask(3, "x", boom) == null, "a fault is not handed back"); }
                Assert(runs == 1 && q.Faulted == 1 && q.LastFault != null && q.LastFault.Contains("boom"), $"one run, fault kept: runs {runs} {q.LastFault}");
                q.BeginFrame(21);
                Assert(q.Ask(3, "y", () => Stand(() => runs++)) != null && runs == 2, "a new key is laid");
                // async: a worker throw lands as a fault too
                var qa = new HoseLayQueue { Async = true };
                qa.BeginFrame(0);
                qa.Ask(4, "x", boom);
                Assert(qa.Drain(5000), "drained");
                qa.BeginFrame(1);
                Assert(qa.Ask(4, "x", boom) == null && qa.Faulted == 1 && runs == 3, $"async fault harvested once: {qa.Json()}");
                qa.BeginFrame(2);
                Assert(qa.Ask(4, "x", boom) == null && runs == 3, "async fault not retried");
            });

            Case("L6 HoseLayQueue.Compute on a CordWorld copy lays what the snapshot lays and leaves both untouched", () =>
            {
                var w = new CordWorld(60, 60);
                for (int z = 5; z < 40; z++) w.SetBlocked(new Cell(25, z), BlockKind.Wall);
                for (int x = 30; x < 34; x++) w.SetExtraCost(new Cell(x, 20), 3f);
                w.SetDoor(new Cell(25, 22));
                var rect = new HoseReelRect(10, 10, 2, 2);
                var sp = new HoseShapeParams { MaxLength = 90 };
                var inp = new HoseLayInputs { Rect = rect, Start = rect.Mouth, End = new Cell(40, 30).Centre, Outward = rect.Outward, Shape = sp, Seed = 17 };
                CordWorld copy = w.Clone();
                for (int x = 0; x < 60; x++)
                    for (int z = 0; z < 60; z++)
                    {
                        var c = new Cell(x, z);
                        Assert(copy.BlockAt(c) == w.BlockAt(c) && copy.ExtraCost(c) == w.ExtraCost(c) && copy.IsDoor(c) == w.IsDoor(c), $"Clone differs at {x},{z}");
                    }
                HoseLay a = HoseLayQueue.Compute(copy, inp);
                HoseLay b = HoseMath.PortLay((e1, in1) => HoseLayQueue.LayFromOn(w, rect, rect.Mouth, rect.Outward, e1, in1, new List<Cell>(), sp, 17), inp.End, null, null, default(V2), null);
                Assert(a.Ok && b.Ok, $"both lay: {a.Reason} / {b.Reason}");
                Assert(a.Flat.Count == b.Flat.Count, $"same sample count {a.Flat.Count} vs {b.Flat.Count}");
                for (int k = 0; k < a.Flat.Count; k++) Assert(V2.Dist(a.Flat[k], b.Flat[k]) < 1e-9, $"same pose at sample {k}");
                for (int x = 0; x < 60; x++)
                    for (int z = 0; z < 60; z++)
                    {
                        var c = new Cell(x, z);
                        Assert(copy.BlockAt(c) == w.BlockAt(c), $"copy restored at {x},{z}");
                    }
                Assert(w.BlockAt(new Cell(10, 10)) == BlockKind.None, "the reel footprint is open again on the snapshot");
                // can-fail: the copy is independent of the snapshot
                copy.SetBlocked(new Cell(1, 1), BlockKind.Wall);
                Assert(w.BlockAt(new Cell(1, 1)) == BlockKind.None, "writing the copy leaves the snapshot alone");
            });

            Case("L7 RM_MapComponent_Hoses (source): DrawAll and the tick lay deferred, skipped under FrameLegacy; LayFrom is LayFromOn", () =>
            {
                string src = RiverSwitchFlipChecks.Src(System.IO.Path.Combine("Hose", "RM_MapComponent_Hoses.cs"));
                int draw = src.IndexOf("private void DrawAll()", StringComparison.Ordinal);
                Assert(draw > 0 && src.IndexOf("HoseLay lay = EnsureLay(r, true);", draw, StringComparison.Ordinal) > draw, "DrawAll asks EnsureLay(r, true)");
                Assert(src.IndexOf("HoseLay lay = EnsureLay(r);", draw, StringComparison.Ordinal) < 0, "no synchronous EnsureLay(r) left in DrawAll");
                Assert(src.Contains("% 250 == 0) EnsureLay(r, true);"), "the 250-tick check asks deferred");
                Assert(src.Contains("if (deferred && !LegacyFrame) return LayLater("), "deferred only off FrameLegacy");
                Assert(src.Contains("return HoseLayQueue.LayFromOn(World(), r.Rect, Start(r), outward, end, inward, route, sp, r.Seed);"), "LayFrom's body is LayFromOn");
            });
        }
    }
}
