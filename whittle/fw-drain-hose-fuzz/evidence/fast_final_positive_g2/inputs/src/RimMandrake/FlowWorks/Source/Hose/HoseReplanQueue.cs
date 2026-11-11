// HOSE_RECHECK_TAME_REPLAN_OFF_TICK (advisory design/RimMandrake/hose_wire_algorithms_advisory_2026-10-28.md section 4 #2):
// the 250-tick corridor recheck ran HoseMath.CheckReplan -- a length-bounded A*, then on failure an UNBOUNDED one (up to
// RouteMaxExpand cells) to tell "route too long" from "no route" -- synchronously on the hose tick. Measured: 18.3 ms recheck
// body live (map1 DRY); 200 reels whose ids align mod 250 put 200 CheckReplans on one tick (offline replay "aligned": Recheck
// 68.5 ms on tick 250, D:\ClaudeWork\rimmandrake\hose_harness\runs\20261105-142218\aligned.txt).
//
// This queue takes the search off the tick, in the HoseLayQueue pattern:
//  1. one job per reel; its inputs (reel rect, far cell, length, lay-failed flag and reason) are COPIED on the main thread
//     and it searches its own CordWorld copy (the snapshot is patched in place by the main thread);
//  2. starts are bounded by ONE per-tick quota shared by every queue (all maps): MaxStartsPerTick, counted in jobs, not in
//     wall time, plus a process-wide in-flight cap (MaxInFlightAll). A reel over the quota stays PENDING and asks next tick;
//  3. a PENDING replan is never an answer: never "no route", never a retract, never a keep. The caller keeps the hose laid
//     and carries no liquid over it while pending (RM_HoseLinks.Live), so a cut hose authorizes no flow while its fate is
//     being computed;
//  4. a landed result is applied only on the main thread and only under the reel's lay EPOCH it started from (a reel reeled
//     in, picked up or re-targeted meanwhile drops it). A RETRACT is applied only if the world snapshot serial it searched is
//     still the current one (an obstacle removed meanwhile would otherwise reel in a hose that now fits); a stale retract is
//     run again on the new world, and after MaxStaleRetracts in a row it is taken as it stands, so a busy map cannot keep a
//     hose pending for ever. A KEEP (null) is applied even if stale: it only drops the lay key, and the next recheck sees
//     the corridor again;
//  5. a search that THROWS keeps its text (LastFault) and answers keep (the hose is re-laid, the next recheck tries again);
//     it never reels a hose in on a fault.
// With Async off (selftests, the offline replay) a started job runs on the caller, still under the per-tick quota.
// Verse-free: compiled into the SelfTest and Replay projects (HoseReplanChecks, Replay/ReplayTick.cs).
using System;
using System.Collections.Generic;
using System.Threading;
using RimMandrake.Shared.Slack;

namespace RimMandrake.FlowWorks.Hose
{
    internal sealed class HoseReplanQueue
    {
        /// <summary>What a started job runs (built on the main thread), the world copy it searches and that copy's serial.</summary>
        internal struct Work
        {
            public Func<string> Run;
            public CordWorld World;
            public int Serial;
        }

        internal sealed class Job
        {
            public int id, epoch, stale;
            public Work work;
            public volatile bool done;
            public string result, error;
            public long ms;
        }

        /// <summary>One ask's answer: Pending (no answer yet: keep the hose laid, carry nothing), or Done with Why (null = keep
        /// it laid and re-lay it; else the reason to reel it in).</summary>
        internal struct Answer
        {
            public bool Pending;
            public string Why;
            internal static readonly Answer Wait = new Answer { Pending = true };
        }

        internal bool Async = true;
        /// <summary>Step 2: replans started per game tick in the whole process (every map's queue).</summary>
        internal static int MaxStartsPerTick = 4;
        /// <summary>Step 2: replans running at once in the whole process.</summary>
        internal static int MaxInFlightAll = Math.Max(1, Math.Min(2, Environment.ProcessorCount / 4));
        /// <summary>Step 4: stale retracts in a row after which the last one is taken.</summary>
        internal const int MaxStaleRetracts = 2;
        private static int quotaTick = int.MinValue, startedThisTick, allInFlight;
        internal static int AllInFlight => Volatile.Read(ref allInFlight);
        /// <summary>Starts left this tick (state read; resets when the tick moves).</summary>
        internal static int QuotaLeft(int tick) => tick == quotaTick ? Math.Max(0, MaxStartsPerTick - startedThisTick) : MaxStartsPerTick;

        /// <summary>Main thread: a job whose result will never be applied gives its work back -- <c>reusable</c> = the job is
        /// done, so nothing else holds its world copy.</summary>
        internal Action<Work, bool> Released;

        private readonly Dictionary<int, Job> jobs = new Dictionary<int, Job>();
        private readonly Dictionary<int, int> staleRun = new Dictionary<int, int>();
        private int inFlight;

        /// <summary>Probe counters (main thread): jobs started, answers given, landed results dropped for an older epoch, stale
        /// retracts run again, stale retracts taken (MaxStaleRetracts), asks deferred by the quota, searches that threw; the
        /// slowest search (ms, worker time).</summary>
        internal long Started, Answered, Dropped, Rerun, StaleTaken, Deferred, Faulted, MaxMs;
        internal string LastFault;
        internal int InFlight => Volatile.Read(ref inFlight);
        internal int Jobs => jobs.Count;

        /// <summary>True while a job for this reel is started and not yet answered.</summary>
        internal bool Has(int id) => jobs.ContainsKey(id);

        /// <summary>The reel's replan: an answer, or Pending (running, or deferred by the quota). <paramref name="serial"/> is
        /// the current world snapshot's serial; <paramref name="prepare"/> runs on the caller only when a job starts.</summary>
        internal Answer Ask(int id, int epoch, int serial, int tick, Func<Work> prepare)
        {
            if (jobs.TryGetValue(id, out Job j))
            {
                if (!j.done) return Answer.Wait;
                jobs.Remove(id);
                if (j.ms > MaxMs) MaxMs = j.ms;
                Released?.Invoke(j.work, true);
                if (j.epoch == epoch)
                {
                    if (j.error != null)
                    {
                        Faulted++;
                        LastFault = $"reel {id}: {j.error}";
                        staleRun.Remove(id);
                        return Give(null);
                    }
                    if (j.result == null || j.work.Serial == serial || j.stale >= MaxStaleRetracts)
                    {
                        if (j.result != null && j.work.Serial != serial) StaleTaken++;
                        staleRun.Remove(id);
                        return Give(j.result);
                    }
                    Rerun++;
                    staleRun[id] = j.stale + 1;
                }
                else { Dropped++; staleRun.Remove(id); }
            }
            if (tick != quotaTick) { quotaTick = tick; startedThisTick = 0; }
            if (startedThisTick >= MaxStartsPerTick || (Async && AllInFlight >= MaxInFlightAll)) { Deferred++; return Answer.Wait; }
            startedThisTick++;
            Started++;
            staleRun.TryGetValue(id, out int st);
            var job = new Job { id = id, epoch = epoch, stale = st, work = prepare() };
            if (!Async)
            {
                RunJob(job);
                job.done = true;
                jobs[id] = job;
                return Ask(id, epoch, serial, tick, prepare);
            }
            jobs[id] = job;
            Interlocked.Increment(ref inFlight);
            Interlocked.Increment(ref allInFlight);
            Queue(job, this);
            return Answer.Wait;
        }

        private Answer Give(string why)
        {
            Answered++;
            return new Answer { Pending = false, Why = why };
        }

        private static void RunJob(Job job)
        {
            var sw = System.Diagnostics.Stopwatch.StartNew();
            try { job.result = job.work.Run(); }
            catch (Exception ex) { job.result = null; job.error = ex.ToString(); }
            job.ms = sw.ElapsedMilliseconds;
        }

        /// <summary>Starts the worker; result, error and ms are written before the volatile done (release), read after it.</summary>
        private static void Queue(Job job, HoseReplanQueue q)
        {
            ThreadPool.QueueUserWorkItem(_ =>
            {
                try { RunJob(job); }
                finally
                {
                    job.done = true;
                    Interlocked.Decrement(ref allInFlight);
                    Interlocked.Decrement(ref q.inFlight);
                }
            });
        }

        /// <summary>The reel's replan is moot (reeled in, gone, hoses off): its job is forgotten (a running one finishes unread;
        /// its world copy is released as not reusable).</summary>
        internal void Forget(int id)
        {
            if (jobs.TryGetValue(id, out Job j))
            {
                jobs.Remove(id);
                Released?.Invoke(j.work, j.done);
            }
            staleRun.Remove(id);
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

        /// <summary>Tests only: the shared quota forgets its tick (a fresh process).</summary>
        internal static void ResetQuota() { quotaTick = int.MinValue; startedThisTick = 0; }

        internal string Json() =>
            "{\"started\":" + Started + ",\"answered\":" + Answered + ",\"dropped\":" + Dropped + ",\"rerun\":" + Rerun + ",\"staleTaken\":" + StaleTaken
            + ",\"deferred\":" + Deferred + ",\"faulted\":" + Faulted + ",\"inFlight\":" + InFlight + ",\"jobs\":" + jobs.Count + ",\"maxMs\":" + MaxMs
            + ",\"async\":" + (Async ? "true" : "false") + ",\"perTick\":" + MaxStartsPerTick + "}";
    }
}
