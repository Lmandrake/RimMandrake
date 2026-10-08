using System;
using HarmonyLib;
using RimWorld;
using Verse;
using Verse.AI;

namespace RimMandrake.CreatureBehaviors
{
    // ════════════════════════════════════════════════════════════════════
    // SOORRAK_FLIGHT_JOBSTART_NRE_1 — a guard on core flight's job-start hook.
    //
    // Pawn_JobTracker.StartJob runs curDriver.ReadyForNextToil() and only THEN
    // calls pawn.flight.Notify_JobStarted(newJob) (read from the decompiled 1.6
    // IL, StartJob IL_0513..IL_053b). If the first toil ends the job on the
    // spot, EndCurrentJob hands it to JobMaker.ReturnToPool, and Job.Clear()
    // sets job.def = null. Notify_JobStarted then reads job.def.tryStartFlying
    // straight after its CanEverFly gate, and throws. Only pawns that can fly
    // get that far, so a non-flier with the same instantly-ending job logs
    // nothing; the soorrak logged it 59 times ("Exception ticking RM_Soorrak…
    // at RimWorld.Pawn_FlightTracker.Notify_JobStarted").
    //
    // A job whose def is null has already ended and been recycled, so there
    // is nothing to fly for. Skipping the hook for it is exactly the no-op the
    // vanilla method would have been if it had checked.
    // ════════════════════════════════════════════════════════════════════
    [StaticConstructorOnStartup]
    public static class RM_FlightJobStartGuard
    {
        static RM_FlightJobStartGuard()
        {
            try
            {
                var target = AccessTools.Method(typeof(Pawn_FlightTracker), nameof(Pawn_FlightTracker.Notify_JobStarted));
                if (target == null)
                {
                    Log.Warning("[RM CreatureBehaviors] flight job-start guard: Pawn_FlightTracker.Notify_JobStarted not found; guard is off.");
                    return;
                }
                var harmony = new Harmony("mandrake.rm.creaturebehaviors.flightjobguard");
                harmony.Patch(target,
                    prefix: new HarmonyMethod(typeof(RM_FlightJobStartGuard), nameof(Prefix_Notify_JobStarted)) { priority = Priority.First });
                try
                {
                    var end = AccessTools.Method(typeof(Pawn_JobTracker), nameof(Pawn_JobTracker.EndCurrentJob));
                    if (end != null)
                    {
                        harmony.Patch(end, prefix: new HarmonyMethod(typeof(RM_FlightJobStartGuard), nameof(Prefix_EndCurrentJob)));
                    }
                }
                catch (Exception e)
                {
                    // The flight guard above IS installed; only the diagnostic prefix failed.
                    Log.Error("[RM CreatureBehaviors] flight job-start guard is ON; its EndCurrentJob diagnostic prefix failed: " + e);
                }
            }
            catch (Exception e)
            {
                Log.Error("[RM CreatureBehaviors] flight job-start guard: patch failed; guard is off: " + e);
            }
        }

        public static bool Prefix_Notify_JobStarted(Job job)
        {
            return job?.def != null;
        }

        // ════════════════════════════════════════════════════════════════
        // SOORRAK_INSTANT_JOB_LOOP_1 — names the job that ends the tick it starts.
        //
        // A wild soorrak reads Wait_MaintainPosture at every sample and never
        // moves. Pawn_JobTracker.EndCurrentJob starts that 1-tick filler only
        // after a job ends Succeeded with the pather idle, so some job J is
        // started by TryFindAndStartJob and runs out of toils inside StartJob,
        // every tick. Only the filler is ever current, so J cannot be read from
        // outside. Vanilla wander, egg-laying, rest, food, exit and our own
        // sun-escape / shade-hop givers were read against decompiled 1.6 and
        // none gives an own-cell job here, so J is named in the log instead of
        // guessed: once per (race, job, giver) after 20 same-tick Succeeded
        // ends in a row on an animal standing still.
        // ════════════════════════════════════════════════════════════════
        private const int LoopReportAfter = 20;

        private sealed class LoopTrack
        {
            public JobDef def;
            public int lastTick;
            public int count;
        }

        private static readonly System.Collections.Generic.Dictionary<int, LoopTrack> loops =
            new System.Collections.Generic.Dictionary<int, LoopTrack>();

        private static readonly System.Collections.Generic.HashSet<string> reported =
            new System.Collections.Generic.HashSet<string>();

        public static void Prefix_EndCurrentJob(Pawn_JobTracker __instance, Pawn ___pawn, JobCondition condition)
        {
            try
            {
                if (condition != JobCondition.Succeeded || ___pawn == null || !___pawn.Spawned)
                {
                    return;
                }
                Job job = __instance.curJob;
                if (job?.def == null || job.def == JobDefOf.Wait_MaintainPosture || ___pawn.RaceProps == null
                    || !___pawn.RaceProps.Animal || (___pawn.pather != null && ___pawn.pather.Moving))
                {
                    return;
                }
                int now = Find.TickManager.TicksGame;
                if (job.startTick != now)
                {
                    return;
                }
                if (loops.Count > 512)
                {
                    loops.Clear();
                }
                if (!loops.TryGetValue(___pawn.thingIDNumber, out LoopTrack t))
                {
                    t = new LoopTrack();
                    loops[___pawn.thingIDNumber] = t;
                }
                if (t.def == job.def && now - t.lastTick <= 3)
                {
                    t.count++;
                }
                else
                {
                    t.def = job.def;
                    t.count = 1;
                }
                t.lastTick = now;
                if (t.count != LoopReportAfter)
                {
                    return;
                }
                string giver = job.jobGiver?.GetType().FullName ?? "(none)";
                string key = ___pawn.def.defName + "|" + job.def.defName + "|" + giver;
                if (!reported.Add(key))
                {
                    return;
                }
                Log.Warning("[RM CreatureBehaviors] instant job loop: " + ___pawn + " (" + ___pawn.def.defName + ") at "
                    + ___pawn.Position + " ended job " + job.def.defName + " the tick it started, " + LoopReportAfter
                    + " times running; giver " + giver + ", tree " + (job.jobGiverThinkTree?.defName ?? "(none)")
                    + ", targetA " + job.targetA + ", targetB " + job.targetB + ", count " + job.count
                    + ", flying " + ___pawn.Flying + ".");
            }
            catch (Exception e)
            {
                Log.ErrorOnce("[RM CreatureBehaviors] instant job loop report failed: " + e, 0x52_4D_4A_4C);
            }
        }
    }
}
