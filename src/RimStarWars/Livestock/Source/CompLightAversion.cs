using System.Linq;
using RimWorld;
using Verse;
using Verse.AI;

namespace RimMandrake.StarWars.Livestock
{
    // FORSAKEN_CRAGS_PREDATORS_BUILD_1 - Skarnix's firelight valve.
    //
    // Forces a flee-to-darkness Goto job whenever the pawn stands somewhere
    // the PsychGlow grid reads not-Dark. Guard shape and the forced-job call
    // itself are copied from vanilla's own precedent for exactly this
    // pattern (Verse/HediffComp_Disorientation.CompPostTickInterval): the
    // same Spawned/!Downed/Awake()/CurJob.suspendable gates, the same
    // JobMaker.MakeJob + Pawn_JobTracker.StartJob(..., JobCondition.
    // InterruptForced, ..., resumeCurJobAfterwards: true) call shape, and
    // GenRadial.RadialCellsAround for the candidate-cell search - not
    // invented from scratch.
    //
    // NOT live-verified this pass (offline build only - see
    // FORSAKEN_CRAGS_PREDATORS_BUILD_1's item file). Every API used here
    // (GlowGrid.PsychGlowAt, GenRadial.RadialCellsAround, JobDefOf.Goto,
    // Pawn_JobTracker.StartJob) is cited against real decompiled 1.6 source
    // (RimSage), not guessed.
    public class CompProperties_LightAversion : CompProperties
    {
        public int fleeSearchRadius = 10;
        public int fleeExpiryTicks = 600;

        public CompProperties_LightAversion()
        {
            compClass = typeof(CompLightAversion);
        }
    }

    public class CompLightAversion : ThingComp
    {
        private CompProperties_LightAversion Props => (CompProperties_LightAversion)props;

        // Cooldown between forced flee-and-resume triggers, set well above
        // fleeExpiryTicks (5x). Without this, resumeCurJobAfterwards: true
        // requeues the interrupted job; if that job's target sits in a lit
        // room with a dark cell in range, the pawn can livelock forever:
        // flee -> Goto ends -> resumed job walks it back into the light ->
        // next rare tick interrupts again, and the resumed job never gets a
        // chance to actually complete.
        private int nextFleeCheckTick = -1;

        public override void PostExposeData()
        {
            base.PostExposeData();
            Scribe_Values.Look(ref nextFleeCheckTick, "nextFleeCheckTick", -1);
        }

        public override void CompTickRare()
        {
            Pawn pawn = parent as Pawn;
            if (pawn == null || !pawn.Spawned || pawn.Downed || !pawn.Awake())
            {
                return;
            }

            if (pawn.CurJob != null && !pawn.CurJob.def.suspendable)
            {
                return;
            }

            // Already fleeing (or otherwise mid-Goto) - don't re-trigger every
            // rare tick, let the existing job run.
            if (pawn.CurJobDef == JobDefOf.Goto)
            {
                return;
            }

            // Cooldown after a previous forced flee - give the resumed job a
            // real window to make progress before we can drag the pawn back
            // into the dark again.
            if (Find.TickManager.TicksGame < nextFleeCheckTick)
            {
                return;
            }

            Map map = pawn.MapHeld;
            if (map == null)
            {
                return;
            }

            if (map.glowGrid.PsychGlowAt(pawn.Position) == PsychGlow.Dark)
            {
                return;
            }

            IntVec3 dest = GenRadial.RadialCellsAround(pawn.Position, Props.fleeSearchRadius, useCenter: false)
                .Where(c => c.InBounds(map)
                    && c.Standable(map)
                    && map.glowGrid.PsychGlowAt(c) == PsychGlow.Dark
                    && pawn.CanReach(c, PathEndMode.OnCell, Danger.Some))
                .RandomElementWithFallback(IntVec3.Invalid);

            if (!dest.IsValid)
            {
                return;
            }

            Job job = JobMaker.MakeJob(JobDefOf.Goto, dest);
            job.expiryInterval = Props.fleeExpiryTicks;
            pawn.jobs.StartJob(job, JobCondition.InterruptForced, null, resumeCurJobAfterwards: true);
            nextFleeCheckTick = Find.TickManager.TicksGame + (Props.fleeExpiryTicks * 5);
        }
    }
}
