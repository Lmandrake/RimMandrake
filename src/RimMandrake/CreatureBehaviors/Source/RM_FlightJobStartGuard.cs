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
                new Harmony("mandrake.rm.creaturebehaviors.flightjobguard").Patch(target,
                    prefix: new HarmonyMethod(typeof(RM_FlightJobStartGuard), nameof(Prefix_Notify_JobStarted)) { priority = Priority.First });
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
    }
}
