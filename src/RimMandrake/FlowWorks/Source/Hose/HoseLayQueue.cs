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
//  5. a lay that THROWS keeps its text (LastFault, Faulted) and is not retried while the key (and epoch) holds;
//  6. (review 2026-10-26, HOSE_LAY_FIX_STALE_EPOCH) every job carries the reel's lay EPOCH at its start
//     (CompHoseReel.layEpoch: bumped whenever the reel's lay is reset -- reeled in, picked up, set down at a new target, an
//     obstacle across it, a synchronous lay). A job that lands under an older epoch is DROPPED, never applied: its lay
//     belongs to a deployment, a world or a lay the reel has already left behind (step 4 applies a landed lay only while
//     nothing reset the reel since it started);
//  7. (HOSE_LAY_FIX_GLOBAL_CAP) the in-flight cap holds across every queue (MaxInFlightAll: all maps, and a reloaded game's abandoned queue whose
//     workers are still finishing), as well as per queue.
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
            /// <summary>The reel's lay epoch when the job started (step 6).</summary>
            public int epoch;
        }

        internal bool Async = true;
        internal int MaxStartsPerFrame = 4;
        internal int MaxInFlight = Math.Max(1, Math.Min(4, Environment.ProcessorCount / 2));
        /// <summary>Step 7: lays running at once in the whole process (every queue).</summary>
        internal static int MaxInFlightAll = Math.Max(1, Math.Min(4, Environment.ProcessorCount / 2));
        private static int allInFlight;
        internal static int AllInFlight => Volatile.Read(ref allInFlight);
        /// <summary>Main thread: a job whose lay will never be applied (dropped as stale, or its reel forgotten) gives its work
        /// back -- <c>reusable</c> = the job is done, so its world copy is restored and nothing else holds it.</summary>
        internal Action<Work, bool> Released;

        private readonly Dictionary<int, Job> jobs = new Dictionary<int, Job>();
        private readonly Dictionary<int, KeyValuePair<string, int>> faulted = new Dictionary<int, KeyValuePair<string, int>>();
        private int frame = int.MinValue, startedThisFrame;
        private int inFlight;

        /// <summary>Probe counters (main thread): jobs started, results handed back to apply, of those the ones whose reel had
        /// moved on (Behind), asks deferred by the budget, lays that threw, landed lays dropped as older than a reset (Dropped);
        /// the slowest lay so far (ms, worker time).</summary>
        internal long Started, Taken, Behind, Deferred, Faulted, Dropped, MaxMs;
        /// <summary>Lays started on every queue (main thread; HoseTickWatch's per-tick delta).</summary>
        internal static long AllStarted;
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
        /// apply it, then ask again), or null: still running, deferred by the budget, just started, or faulted under this key and
        /// epoch. A landed job from an older <paramref name="epoch"/> is dropped (step 6) and the current key asked at once.
        /// <paramref name="prepare"/> runs on the caller only when a job starts.</summary>
        internal Job Ask(int id, string key, int epoch, Func<Work> prepare)
        {
            if (jobs.TryGetValue(id, out Job j))
            {
                if (!j.done) return null;   // one job a reel: a newer key waits for it
                jobs.Remove(id);
                Job landed = Land(id, j, j.epoch == epoch);
                if (j.epoch != epoch)
                {
                    if (landed != null) Dropped++;
                    Released?.Invoke(j.work, true);
                }
                else if (landed != null)
                {
                    if (landed.key != key) Behind++;
                    return landed;
                }
            }
            if (faulted.TryGetValue(id, out KeyValuePair<string, int> fk))
            {
                if (fk.Key == key && fk.Value == epoch) return null;
                faulted.Remove(id);   // the fault was under another key or before a reset: tried again
            }
            if (startedThisFrame >= MaxStartsPerFrame || (Async && (InFlight >= MaxInFlight || AllInFlight >= MaxInFlightAll))) { Deferred++; return null; }
            startedThisFrame++;
            Started++;
            AllStarted++;
            var job = new Job { id = id, key = key, epoch = epoch, work = prepare() };
            if (!Async)
            {
                RunJob(job);
                job.done = true;
                return Land(id, job, true);
            }
            jobs[id] = job;
            Interlocked.Increment(ref inFlight);
            Interlocked.Increment(ref allInFlight);
            Queue(job, this);
            return null;
        }

        /// <summary>A done job: the result to apply, or null when it threw (kept as LastFault; its key and epoch are not retried
        /// when <paramref name="current"/>). A dropped job's throw is still counted and kept.</summary>
        private Job Land(int id, Job j, bool current)
        {
            if (j.ms > MaxMs) MaxMs = j.ms;
            if (j.error == null) { if (current) Taken++; return j; }
            Faulted++;
            LastFault = $"reel {id}: {j.error}";
            if (current) faulted[id] = new KeyValuePair<string, int>(j.key, j.epoch);
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
                    // HOSE_LAY_FIX_COUNTER_ORDER: done first (Drain implies done), the process-wide count before the
                    // queue's own, so Drain (InFlight == 0) never returns while AllInFlight still counts this job
                    job.done = true;
                    Interlocked.Decrement(ref allInFlight);
                    Interlocked.Decrement(ref q.inFlight);
                }
            });
        }

        /// <summary>A reel gone: its job (running or not) and fault are forgotten; a running one finishes unread (its work is
        /// released as not reusable: the worker may still be laying on its world copy).</summary>
        internal void Forget(int id)
        {
            if (jobs.TryGetValue(id, out Job j))
            {
                jobs.Remove(id);
                Released?.Invoke(j.work, j.done);
            }
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
            "{\"started\":" + Started + ",\"taken\":" + Taken + ",\"behind\":" + Behind + ",\"deferred\":" + Deferred + ",\"faulted\":" + Faulted + ",\"dropped\":" + Dropped
            + ",\"inFlight\":" + InFlight + ",\"jobs\":" + jobs.Count + ",\"maxMs\":" + MaxMs + ",\"async\":" + (Async ? "true" : "false") + "}";
    }
}
