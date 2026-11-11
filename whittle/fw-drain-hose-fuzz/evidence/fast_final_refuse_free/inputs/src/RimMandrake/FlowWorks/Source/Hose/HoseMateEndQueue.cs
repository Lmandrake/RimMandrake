// HOSE_DRAW_FIX_STALLS_WHILE_WORKER_LAYS (live round 8, 2026-10-26: 325 basin map, 200 hoses, relay wave): the worst frame
// while a worker laid was 164.7 ms, DrawAll 162.4 ms of it. RM_MapComponent_Hoses.Mated ran 105 times in the window at
// 11.7 ms mean / 50.7 ms max (D:\ClaudeWork\rimmandrake\live_round8_20261026\tprof_T2.txt): every re-posed mated end
// re-solved its tail (HoseSpliceMath.MateEnd -> MateTailG2 -> HoseClothoid.TailOnto with its clearance search) inside the
// draw. The 8 ms re-pose budget could not bound it either: the budget is checked before a re-pose, so one call overshot it
// by up to 50 ms. At Superfast (T2c) Mated reached 56 ms.
//
// This queue takes that solve off the frame, the way HoseMateCache took the pair solve off it:
//  1. per reel, one MateEnd job at a time on a worker (the drawn pose copied; the pair's Mate is immutable once solved), at
//     most MaxStartsPerFrame starts per frame and MaxInFlight running;
//  2. latest wins: a job that lands is handed to the caller (Ask), with the draw key and the tag (the HoseLay) it was
//     asked under; the caller draws it if it is still the same lay, and asks again when its key has moved on, so a pose
//     that changes every tick (a fill transition) still advances one landed solve at a time rather than never;
//  3. a job that throws lands as "no re-shape" (the caller draws the pose as laid, as MateEnd's null) and is counted.
// With Async off (selftests) a started job runs on the caller at once.
// Verse-free: compiled into the SelfTest project (HoseMateEndQueueChecks).
using System;
using System.Collections.Generic;
using System.Threading;
using RimMandrake.Shared.Slack;

namespace RimMandrake.FlowWorks.Hose
{
    internal sealed class HoseMateEndQueue
    {
        /// <summary>A landed re-shape: the draw key and tag it was asked under, the source pose, the result (null = the
        /// re-shape failed: draw <see cref="Source"/>) and how many leading samples the two share.</summary>
        internal sealed class Landed
        {
            public string Key;
            public object Tag;
            public List<V2> Source, Result;
            public int Same;
            public string Error;
            /// <summary>The pair solve it was re-shaped onto (a re-solved pair makes an older result unusable).</summary>
            public HoseSpliceMath.Mate Of;
            internal volatile bool done;
            internal HoseSpliceMath.Mate mate;
            internal bool isA;
            internal double kmax, vis, lead;
            internal Func<List<V2>, HoseSpliceMath.Mate, bool, double, double, double, List<V2>> work;
        }

        private sealed class Slot
        {
            /// <summary>The job on a worker; the landed result not yet handed out; the last one handed out (asked again for
            /// the same key, lay and pair solve it is handed out again, never re-solved).</summary>
            public Landed running, landed, last;
            public int seen;
        }

        /// <summary>The re-shape, replaceable by tests (a counting or slow stand-in). Called on a worker thread when Async.</summary>
        internal Func<List<V2>, HoseSpliceMath.Mate, bool, double, double, double, List<V2>> Work = HoseSpliceMath.MateEnd;
        internal bool Async = true;
        internal int MaxStartsPerFrame = 4, MaxInFlight = 4;
        private readonly Dictionary<int, Slot> slots = new Dictionary<int, Slot>();
        private readonly List<int> scratch = new List<int>();
        private int frame = int.MinValue, startedThisFrame, inFlight;

        /// <summary>Probe counters (main thread): jobs started, results taken, asks that found no budget, jobs that threw.</summary>
        internal long Started, Taken, Deferred, Faulted;
        internal string LastFault;
        internal int InFlight => inFlight;
        internal int Count => slots.Count;

        /// <summary>Once per frame, main thread: finished jobs become landed results; the start budget resets; reels not asked
        /// for in 600 frames (and not running) are forgotten.</summary>
        internal void BeginFrame(int f)
        {
            if (f == frame) return;
            frame = f;
            startedThisFrame = 0;
            if (slots.Count == 0) return;
            scratch.Clear();
            foreach (var kv in slots)
            {
                Slot s = kv.Value;
                if (s.running != null && s.running.done) Land(s);
                if (s.running == null && f - s.seen > 600) scratch.Add(kv.Key);
            }
            for (int i = 0; i < scratch.Count; i++) slots.Remove(scratch[i]);
        }

        private void Land(Slot s)
        {
            Landed j = s.running;
            s.running = null;
            inFlight--;
            j.work = null;
            j.mate = null;
            if (j.Error != null) { Faulted++; LastFault = j.Error; }
            s.landed = j;
        }

        /// <summary>
        /// Reel <paramref name="id"/> wants <paramref name="pts"/> re-shaped onto its pair's coupling (<see cref="Work"/>:
        /// HoseSpliceMath.MateEnd with these arguments) under draw key
        /// <paramref name="key"/>. Returns a landed result not yet handed out (it may be for an older key: check
        /// <see cref="Landed.Tag"/> and <see cref="Landed.Key"/>), else the last one handed out when it was for this key, tag
        /// and mate, else null. Starts a job when none is running for this reel, the last landed one was for another key, tag
        /// or mate, and the budget allows; <paramref name="pts"/> is copied, never read by the worker.
        /// </summary>
        internal Landed Ask(int id, string key, object tag, List<V2> pts, HoseSpliceMath.Mate mate, bool isA, double kmax, double vis, double lead)
        {
            if (!slots.TryGetValue(id, out Slot s)) slots[id] = s = new Slot();
            s.seen = frame;
            if (s.running != null && s.running.done) Land(s);
            Landed got = Fresh(s);
            if (s.running == null && !For(s.last, key, tag, mate))
            {
                if (startedThisFrame >= MaxStartsPerFrame || (Async && inFlight >= MaxInFlight)) Deferred++;
                else
                {
                    Start(s, key, tag, pts, mate, isA, kmax, vis, lead);
                    // a synchronous job (Async off) lands at once
                    if (got == null) got = Fresh(s);
                }
            }
            if (got == null && For(s.last, key, tag, mate)) got = s.last;
            return got;
        }

        /// <summary>The landed result not yet handed out, now handed out (it becomes the slot's last).</summary>
        private Landed Fresh(Slot s)
        {
            Landed j = s.landed;
            if (j == null) return null;
            s.landed = null;
            s.last = j;
            Taken++;
            return j;
        }

        private static bool For(Landed j, string key, object tag, HoseSpliceMath.Mate mate) =>
            j != null && j.Key == key && ReferenceEquals(j.Tag, tag) && ReferenceEquals(j.Of, mate);

        /// <summary>True while a job for this reel runs (probe/tests).</summary>
        internal bool Running(int id) => slots.TryGetValue(id, out Slot s) && s.running != null && !s.running.done;

        internal void Forget(int id)
        {
            // a running job finishes on its worker and is dropped with the slot
            if (slots.TryGetValue(id, out Slot s) && s.running != null) inFlight--;
            slots.Remove(id);
        }

        private void Start(Slot s, string key, object tag, List<V2> pts, HoseSpliceMath.Mate mate, bool isA, double kmax, double vis, double lead)
        {
            startedThisFrame++;
            Started++;
            var j = new Landed { Key = key, Tag = tag, Of = mate, Source = new List<V2>(pts), work = Work, mate = mate, isA = isA, kmax = kmax, vis = vis, lead = lead };
            s.running = j;
            inFlight++;
            if (!Async)
            {
                Run(j);
                Land(s);
                return;
            }
            Queue(j);
        }

        /// <summary>The re-shape and the shared prefix; an exception becomes <see cref="Landed.Error"/>, never escapes.</summary>
        private static void Run(Landed j)
        {
            try
            {
                List<V2> o = j.work(j.Source, j.mate, j.isA, j.kmax, j.vis, j.lead);
                j.Result = o;
                int same = 0;
                if (o != null) while (same < o.Count && same < j.Source.Count && V2.Dist(o[same], j.Source[same]) < 1e-9) same++;
                j.Same = same;
            }
            catch (Exception ex) { j.Result = null; j.Error = ex.ToString(); }
            finally { j.done = true; }
        }

        /// <summary>Its own method, so Ask allocates no closure on the paths that start nothing.</summary>
        private static void Queue(Landed j) => ThreadPool.QueueUserWorkItem(_ => Run(j));

        /// <summary>Blocks until every running job is done (tests only).</summary>
        internal bool Drain(int timeoutMs)
        {
            var sw = System.Diagnostics.Stopwatch.StartNew();
            while (sw.ElapsedMilliseconds < timeoutMs)
            {
                bool all = true;
                foreach (Slot s in slots.Values) if (s.running != null && !s.running.done) { all = false; break; }
                if (all) return true;
                Thread.Sleep(2);
            }
            return false;
        }
    }

    /// <summary>
    /// HOSE_RELAY_FIX_BUDGET_STARVES_LATE_REELS (review 2026-10-26): DrawAll's per-frame budgets (re-pose 8 ms, crossing
    /// shadows 4 ms, the mate-end starts) were spent in reel order every frame, so with more work pending than one frame's
    /// budget the same early reels were served every frame and a late reel's pose could stay stale for as long as the wave
    /// lasted. The draw now walks the reels from a rotating start: the first reel a budget turned away last frame is the
    /// first one served this frame (any one call is always served), and the walk wraps. A reel that keeps needing work is
    /// therefore served at least once in every ceil(N / k) frames when a frame serves at least k. Draw order does not
    /// change what is seen: each hose draws at its own altitude band (HoseMath.CrossLift of its rank).
    /// Verse-free (HoseMateEndQueueChecks proves the bound and the starvation it replaces).
    /// </summary>
    internal sealed class HoseDrawRotation
    {
        private int start, firstDeferred = -1, n;

        /// <summary>Start of a frame over <paramref name="count"/> reels; <paramref name="rotate"/> false = reel order (legacy).</summary>
        internal void Begin(int count, bool rotate)
        {
            n = count;
            if (!rotate || count <= 0) start = 0;
            else if (firstDeferred >= 0) start = firstDeferred % count;
            else if (start >= count) start = 0;
            firstDeferred = -1;
        }

        /// <summary>The reel index the <paramref name="k"/>-th step of this frame's walk draws.</summary>
        internal int At(int k) => n <= 0 ? 0 : (start + k) % n;

        /// <summary>A budget turned reel <paramref name="index"/> away this frame (the first one is next frame's start).</summary>
        internal void Deferred(int index) { if (firstDeferred < 0) firstDeferred = index; }

        internal int Start => start;
    }
}
