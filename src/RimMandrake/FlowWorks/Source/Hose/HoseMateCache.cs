// HOSE_FRAME_FIX_CHOKES_325_BASIN_MAP (2026-10-26, live wave: 325 map, 100 rigs, timed levelling phase): while the game
// TICKED, frames reached 71-118 s. Profile (D:\ClaudeWork\rimmandrake\live_wave_20261026\prof2_a.txt): 11 re-lays in 60
// ticks -> 22 HoseSpliceMath.MatePair solves at 1.22 s mean / 1.90 s max, each run synchronously inside DrawAll. The re-lays
// are the 250-tick corridor check (RM_MapComponent_Hoses.MapComponentTick): the basin's water changes the corridor hash, the
// hose is laid again -- usually to the same points -- and the pair cache keyed on the HoseLay INSTANCE re-solved the pair.
//
// This cache fixes that at the cause and bounds what is left:
//  1. a pair is keyed on what the solve reads (both drawn flats quantized to 1e-3 cell, both lead-outs, kmax, the visible
//     width and the G2 switch), so a re-lay to the same shape is a cache hit, never a solve;
//  2. a pair whose inputs DID change is solved off the frame: on a worker thread (inputs copied; the solver is pure math --
//     only diagnostic counters are shared) with at most MaxStartsPerFrame starts per frame and MaxInFlight running, and
//     harvested on the main thread at the next BeginFrame. Until then Get returns null (the caller draws both ends as laid).
//     With Async off (selftests, fallback) at most MaxStartsPerFrame solves run per frame on the caller.
// Verse-free: compiled into the SelfTest project (HoseMateCacheChecks).
using System;
using System.Collections.Generic;
using System.Threading;
using RimMandrake.Shared.Slack;

namespace RimMandrake.FlowWorks.Hose
{
    internal sealed class HoseMateCache
    {
        /// <summary>A solved pair: the content key it was solved under, the result (null = no gentle route), last frame met.</summary>
        internal sealed class Entry
        {
            public ulong key;
            public HoseSpliceMath.Mate mate;
            public int seen;
        }

        private sealed class Job
        {
            public ulong key;
            public List<V2> A, B;
            public double kmax, vis, leadA, leadB;
            public volatile bool done;
            public HoseSpliceMath.Mate result;
        }

        /// <summary>The solve, replaceable by tests (a counting or slow stand-in). Called on a worker thread when Async.</summary>
        internal Func<List<V2>, List<V2>, double, double, double, double, HoseSpliceMath.Mate> Solver = DefaultSolve;
        internal bool Async = true;
        internal int MaxStartsPerFrame = 1, MaxInFlight = 2;

        private readonly Dictionary<long, Entry> solved = new Dictionary<long, Entry>();
        private readonly Dictionary<long, Job> pending = new Dictionary<long, Job>();
        private int frame = int.MinValue, startedThisFrame;

        /// <summary>Probe counters: solves started, cache hits, asks deferred by the budget, worker solves failed.</summary>
        internal long Started, Reused, Deferred, Faulted;
        internal int Pending => pending.Count;
        internal int Count => solved.Count;

        internal static HoseSpliceMath.Mate DefaultSolve(List<V2> A, List<V2> B, double kmax, double vis, double leadA, double leadB) =>
            HoseSpliceMath.MatePair(A, B, A[A.Count - 1], kmax, vis, out _, out _, leadA, leadB);

        /// <summary>FNV-1a over everything the solve reads; points quantized to 1/1000 cell (a re-lay to the same route lands
        /// within float noise of the old points).</summary>
        internal static ulong Key(IList<V2> A, IList<V2> B, double kmax, double vis, double leadA, double leadB)
        {
            ulong h = 1469598103934665603UL;
            void Mix(double v) { h = (h ^ unchecked((ulong)(long)Math.Round(v * 1000))) * 1099511628211UL; }
            Mix(A.Count); foreach (V2 p in A) { Mix(p.X); Mix(p.Z); }
            Mix(B.Count); foreach (V2 p in B) { Mix(p.X); Mix(p.Z); }
            Mix(kmax); Mix(vis); Mix(leadA); Mix(leadB); Mix(HoseMath.G2On ? 1 : 0);
            return h;
        }

        /// <summary>Once per frame, main thread: finished worker solves become entries, the start budget resets.</summary>
        internal void BeginFrame(int f)
        {
            if (f == frame) return;
            frame = f;
            startedThisFrame = 0;
            if (pending.Count == 0) return;
            List<long> done = null;
            foreach (var kv in pending) if (kv.Value.done) (done ??= new List<long>()).Add(kv.Key);
            if (done == null) return;
            foreach (long pair in done)
            {
                Job j = pending[pair];
                pending.Remove(pair);
                solved[pair] = new Entry { key = j.key, mate = j.result, seen = frame };
            }
        }

        /// <summary>The pair's solve for these inputs: the cached one when its key holds, a fresh one when the budget allows a
        /// synchronous solve, else null (pending on a worker, or deferred to a later frame).</summary>
        internal Entry Get(long pair, List<V2> A, List<V2> B, double kmax, double vis, double leadA, double leadB)
        {
            ulong key = Key(A, B, kmax, vis, leadA, leadB);
            if (solved.TryGetValue(pair, out Entry e) && e.key == key) { e.seen = frame; Reused++; return e; }
            if (pending.ContainsKey(pair))
            {
                // a worker is still on this pair; if the inputs moved again the new shape waits for it to finish (one job a pair)
                return null;
            }
            if (startedThisFrame >= MaxStartsPerFrame || (Async && pending.Count >= MaxInFlight)) { Deferred++; return null; }
            startedThisFrame++;
            Started++;
            if (!Async)
            {
                e = new Entry { key = key, mate = Solver(A, B, kmax, vis, leadA, leadB), seen = frame };
                solved[pair] = e;
                return e;
            }
            var job = new Job { key = key, A = new List<V2>(A), B = new List<V2>(B), kmax = kmax, vis = vis, leadA = leadA, leadB = leadB };
            pending[pair] = job;
            var solver = Solver;
            ThreadPool.QueueUserWorkItem(_ =>
            {
                try { job.result = solver(job.A, job.B, job.kmax, job.vis, job.leadA, job.leadB); }
                catch { job.result = null; Interlocked.Increment(ref Faulted); }
                finally { job.done = true; }
            });
            return null;
        }

        /// <summary>Pairs not met this frame (an end moved off, a reel gone) are forgotten once they outnumber the live ones.</summary>
        internal void Prune(int met)
        {
            if (solved.Count <= 64 || solved.Count <= 2 * met) return;
            var stale = new List<long>();
            foreach (var kv in solved) if (kv.Value.seen != frame) stale.Add(kv.Key);
            foreach (long k in stale) solved.Remove(k);
        }

        /// <summary>Blocks until every worker solve is done (tests only).</summary>
        internal bool Drain(int timeoutMs)
        {
            var sw = System.Diagnostics.Stopwatch.StartNew();
            while (sw.ElapsedMilliseconds < timeoutMs)
            {
                bool all = true;
                foreach (Job j in pending.Values) if (!j.done) { all = false; break; }
                if (all) return true;
                Thread.Sleep(5);
            }
            return false;
        }
    }
}
