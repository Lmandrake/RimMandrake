using RimWorld;
using Verse;
using Verse.AI;

namespace RimMandrake.Graffiti
{
    // An idle hand tags the wall. Vanilla only seeks recreation near empty joy, about once in a day or two and with painting one
    // choice among several, so a colony could go a full day with bare walls (measured live: 0 marks in 48000 ticks, 3 pawns, all
    // idle most of it). This runs only when a colonist has nothing better to do: a busy colony rarely tags, a bored one gets written
    // on, and the room cap stops it there. Think tree: Humanlike_PostMain, just before the idle wander.
    public class JobGiver_IdleTag : ThinkNode_JobGiver
    {
        protected override Job TryGiveJob(Pawn pawn)
        {
            if (!RM_GraffitiSettings.paintingEnabled || pawn.Map == null || pawn.Downed) return null;
            float urge = GraffitiTemperament.Urge(pawn);
            if (pawn.needs?.joy == null || urge <= 0f || !RM_GraffitiKernel.IdleHandTags(Rand.Value / urge)) return null;
            if (!GraffitiJobUtility.TryFindWallMarkCell(pawn, out IntVec3 cell, roomCap: true)) return null;
            Job job = JobMaker.MakeJob(RMGraffitiDefOf.RM_PaintGraffitiJob, cell);
            // Idle in work hours is still idle: the tag is the pawn's own fun, and the joy timetable mustn't end it at the first stroke.
            job.ignoreJoyTimeAssignment = true;
            return job;
        }
    }
}
