// HOSE_LAY_FIX_SYNC_RELAY_IN_DRAW (2026-10-26, live wave 3: 325 map, 100 rigs / 200 hoses, FrameLegacy=0, mate cache
// clean): a hose re-lay (RM_MapComponent_Hoses.LayAgain -> HoseMath.PortLay -> LayFrom -> HoseMath.LayAlong, the route
// search and shaping) ran synchronously wherever EnsureLay found the lay key changed -- in DrawAll every frame and in the
// 250-tick corridor check. Measured (D:\ClaudeWork\rimmandrake\live_wave3_20261026\tprof_T2.txt, tprof_T3.txt): 300 ticks at
// maxLength 40 -> 80 lays, 121 ms mean / 537 ms max, DrawAll 1.39 s max; maxLength 40 -> 39 while paused (the key carries
// RM_HoseSettings.ShapeFingerprint, so every hose's key changed at once) -> ONE DrawAll frame of 90.5 s, 150 lays at 589 ms
// mean / 4.27 s max.
//
// This queue takes the lay off the frame for the draw and the tick (the public EnsureLay stays synchronous for probes,
// install checks and the bridge tools; FrameLegacy keeps the old synchronous path):
//  1. one job per reel, keyed on the reel's lay key (every input of the lay: the reel, its look, the end, the relay, the
//     walked trail, the shape settings, fed, the port); an unchanged key never reaches the queue (EnsureLay's own check);
//  2. a job's inputs are COPIED on the main thread (HoseLayInputs) and it lays against its own CordWorld copy
//     (CordWorld.Clone): the lay marks the reel's footprint solid while it runs, and the main thread keeps the snapshot;
//  3. at most MaxStartsPerFrame starts per frame and MaxInFlight running; until a job lands the caller keeps drawing the
//     reel's last lay (null for a hose never laid yet: it appears when its first lay lands);
//  4. a finished job is taken on the main thread at the reel's next ask and applied UNDER ITS OWN KEY (the lay is right for
//     the inputs it was started from, and newer than what is drawn); if the reel's key moved meanwhile (Behind) the caller
//     asks again and the new key starts its own job -- a hose carried across the map shows its newest landed lay instead of
//     freezing while every result goes stale;
//  5. a lay that THROWS keeps its text (LastFault, Faulted) and is not retried while the key holds.
// With Async off (selftests) a started job runs on the caller, still at most MaxStartsPerFrame a frame.
// Verse-free: compiled into the SelfTest project (HoseLayQueueChecks).
using System;
using System.Collections.Generic;
using System.Threading;
using RimMandrake.Shared.Slack;

namespace RimMandrake.FlowWorks.Hose
{
    /// <summary>Everything one hose lay reads besides the world, copied on the main thread (no reel, no map).</summary>
    internal sealed class HoseLayInputs
    {
        public HoseReelRect Rect;
        public V2 Start, End;
        public V2? Inward, PortAt;
        public V2 PortAxis;
        /// <summary>The reel's hose leaves by its nozzle (not a fed relay): its own footprint is solid for the lay.</summary>
        public V2? Outward;
        public List<Cell> Trail = new List<Cell>();
        public HoseShapeParams Shape;
        public ulong Seed;
        /// <summary>The tank port's body (step 4 of the port lay: a lay through its own reel or the tank is never kept).</summary>
        public bool HasBody;
        public int BodyX0, BodyZ0, BodyW, BodyH;
    }

    internal sealed class HoseLayQueue
    {
        /// <summary>The lay of <paramref name="i"/> on <paramref name="w"/>: what RM_MapComponent_Hoses.LayAgain lays (PortLay over
        /// LayFrom). Writes w only inside LayFromOn, restored before it returns.</summary>
        internal static HoseLay Compute(CordWorld w, HoseLayInputs i)
        {
            Func<HoseLay, string> bodyHit = null;
            if (i.HasBody && i.PortAt.HasValue)
            {
                V2? pa = i.PortAt;
                V2 pax = i.PortAxis;
                HoseReelRect rect = i.Rect;
                int x0 = i.BodyX0, z0 = i.BodyZ0, bw = i.BodyW, bh = i.BodyH;
                bodyHit = l => HoseMath.BodyHit(l, pa, pax, rect, x0, z0, bw, bh);
            }
            return HoseMath.PortLay((e1, in1) => LayFromOn(w, i.Rect, i.Start, i.Outward, e1, in1, i.Trail, i.Shape, i.Seed), i.End, i.Inward, i.PortAt, i.PortAxis, bodyHit);
        }

        /// <summary>RM_MapComponent_Hoses.LayFrom's body, the reel read out beforehand: a nozzled reel's own footprint is solid
        /// for this lay (2026-10-05: a target behind the reel is reached round it), restored afterwards.</summary>
        internal static HoseLay LayFromOn(CordWorld w, HoseReelRect rect, V2 start, V2? outward, V2 end, V2? inward, IList<Cell> route, HoseShapeParams sp, ulong seed)
        {
            var held = new List<KeyValuePair<Cell, BlockKind>>();
            if (outward.HasValue)
                for (int x = rect.X0; x < rect.X0 + rect.W; x++)
                    for (int z = rect.Z0; z < rect.Z0 + rect.H; z++)
                    {
                        var c = new Cell(x, z);
                        held.Add(new KeyValuePair<Cell, BlockKind>(c, w.BlockAt(c)));
                        w.SetBlocked(c, BlockKind.Device);
                    }
            try { return HoseMath.LayAlong(w, start, route ?? new List<Cell>(), end, sp, seed, inward, outward); }
            finally { foreach (var kv in held) w.SetBlocked(kv.Key, kv.Value); }
        }

        /// <summary>What a started job runs (built on the main thread) and the world it ran on (kept for the corridor hash).</summary>
        internal struct Work
        {
            public Func<HoseLay> Run;
            public CordWorld World;
            /// <summary>The caller's own record of the state the job was started from (the component: the reel's end cell).</summary>
            public object Tag;
        }

        internal sealed class Job
        {
            public int id;
            public string key;
            public Work work;
            public volatile bool done;
            public HoseLay result;
            public string error;
            public long ms;
        }

        internal bool Async = true;
        internal int MaxStartsPerFrame = 4;
        internal int MaxInFlight = Math.Max(1, Math.Min(4, Environment.ProcessorCount / 2));

        private readonly Dictionary<int, Job> jobs = new Dictionary<int, Job>();
        private readonly Dictionary<int, string> faulted = new Dictionary<int, string>();
        private int frame = int.MinValue, startedThisFrame;
        private int inFlight;

        /// <summary>Probe counters (main thread): jobs started, results handed back to apply, of those the ones whose reel had
        /// moved on (Behind), asks deferred by the budget, lays that threw; the slowest lay so far (ms, worker time).</summary>
        internal long Started, Taken, Behind, Deferred, Faulted, MaxMs;
        internal string LastFault;
        internal int InFlight => Volatile.Read(ref inFlight);
        internal int Jobs => jobs.Count;

        /// <summary>Once per frame, main thread: the start budget resets.</summary>
        internal void BeginFrame(int f)
        {
            if (f == frame) return;
            frame = f;
            startedThisFrame = 0;
        }

        /// <summary>True while a job for this reel is running (the caller keeps its last lay and builds nothing).</summary>
        internal bool Running(int id) => jobs.TryGetValue(id, out Job j) && !j.done;

        /// <summary>A finished job to apply under ITS key (job.key: may differ from <paramref name="key"/> -- the reel moved on;
        /// apply it, then ask again), or null: still running, deferred by the budget, just started, or faulted under this key.
        /// <paramref name="prepare"/> runs on the caller only when a job starts.</summary>
        internal Job Ask(int id, string key, Func<Work> prepare)
        {
            if (jobs.TryGetValue(id, out Job j))
            {
                if (!j.done) return null;   // one job a reel: a newer key waits for it
                jobs.Remove(id);
                Job landed = Land(id, j);
                if (landed != null)
                {
                    if (landed.key != key) Behind++;
                    return landed;
                }
                if (j.key != key) faulted.Remove(id);   // the fault was under an older key: the new one is tried
            }
            if (faulted.TryGetValue(id, out string fk))
            {
                if (fk == key) return null;
                faulted.Remove(id);
            }
            if (startedThisFrame >= MaxStartsPerFrame || (Async && InFlight >= MaxInFlight)) { Deferred++; return null; }
            startedThisFrame++;
            Started++;
            var job = new Job { id = id, key = key, work = prepare() };
            if (!Async)
            {
                RunJob(job);
                job.done = true;
                return Land(id, job);
            }
            jobs[id] = job;
            Interlocked.Increment(ref inFlight);
            Queue(job, this);
            return null;
        }

        /// <summary>A done job: the result to apply, or null when it threw (kept as LastFault; its key is not retried).</summary>
        private Job Land(int id, Job j)
        {
            if (j.ms > MaxMs) MaxMs = j.ms;
            if (j.error == null) { Taken++; return j; }
            Faulted++;
            LastFault = $"reel {id}: {j.error}";
            faulted[id] = j.key;
            return null;
        }

        private static void RunJob(Job job)
        {
            var sw = System.Diagnostics.Stopwatch.StartNew();
            try { job.result = job.work.Run(); }
            catch (Exception ex) { job.result = null; job.error = ex.ToString(); }
            job.ms = sw.ElapsedMilliseconds;
        }

        /// <summary>Starts the worker; result, error and ms are written before the volatile done (release), read after it.</summary>
        private static void Queue(Job job, HoseLayQueue q)
        {
            ThreadPool.QueueUserWorkItem(_ =>
            {
                try { RunJob(job); }
                finally
                {
                    job.done = true;
                    Interlocked.Decrement(ref q.inFlight);
                }
            });
        }

        /// <summary>A reel gone: its job (running or not) and fault are forgotten; a running one finishes unread.</summary>
        internal void Forget(int id)
        {
            jobs.Remove(id);
            faulted.Remove(id);
        }

        /// <summary>Blocks until every started job is done (tests only).</summary>
        internal bool Drain(int timeoutMs)
        {
            var sw = System.Diagnostics.Stopwatch.StartNew();
            while (sw.ElapsedMilliseconds < timeoutMs)
            {
                if (InFlight == 0) return true;
                Thread.Sleep(5);
            }
            return false;
        }

        internal string Json() =>
            "{\"started\":" + Started + ",\"taken\":" + Taken + ",\"behind\":" + Behind + ",\"deferred\":" + Deferred + ",\"faulted\":" + Faulted
            + ",\"inFlight\":" + InFlight + ",\"jobs\":" + jobs.Count + ",\"maxMs\":" + MaxMs + ",\"async\":" + (Async ? "true" : "false") + "}";
    }
}
