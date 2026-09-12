using RimWorld;
using Verse;
using Verse.AI;

namespace RimMandrake.StarWars.Droidworks
{
    public class HediffCompProperties_DWWipeStumble : HediffCompProperties
    {
        /// How often the roll is made, in ticks. 250 = the vanilla "rare tick"
        /// cadence, ~4.2 s, so a full day is 240 rolls.
        public int checkIntervalTicks = 250;

        /// Chance per roll AT FULL SEVERITY. Scaled by current severity, which
        /// falls linearly to 0 over the hediff's 7 days - so the stumbling
        /// tapers off exactly as the droid relearns its body.
        public float stumbleChancePerCheck = 0.05f;

        /// Radius of the cell the droid blunders off to.
        public int stumbleRadius = 4;

        public HediffCompProperties_DWWipeStumble() =>
            compClass = typeof(HediffComp_DWWipeStumble);
    }

    /// <summary>
    /// DROIDWORKS_WIPE_SEVERITY_1 (packet B10). The behavioural half of
    /// RSW_DW_RecentlyWiped - owner ruling 7 verbatim: "make it REALLY severe.
    /// Like it bumps into walls, learns how to use its body, and frequently
    /// forgets what it was doing during that week."
    ///
    /// The hediff's capMods carry "learns how to use its body" (Moving and
    /// Manipulation ramps, HediffDefs_Droidworks.xml). This comp carries the
    /// other two clauses with ONE mechanism, because they are one event: the
    /// droid drops whatever it was doing ("forgets what it was doing") and
    /// blunders off to a random nearby cell ("bumps into walls").
    ///
    /// 🔑 DELIBERATE DEVIATION from the packet's own wording, recorded per
    /// Charter ("a named defName/xpath is an example, not a mandate"). The
    /// design doc names "wall-bump collisions via a JobGiver stub". A ThinkNode
    /// JobGiver cannot do the job asked for: a JobGiver is consulted only when
    /// the pawn NEEDS a new job, so it can make an idle droid wander but can
    /// never INTERRUPT the job it is already running - and interruption is the
    /// whole of "frequently forgets what it was doing". A HediffComp that
    /// starts the stumble job with JobCondition.InterruptForced does both, on
    /// the hediff itself, with no think-tree insertion to go wrong on non-droid
    /// pawns. GotoWander is vanilla's own wander job (JobGiver_Wander uses the
    /// identical JobMaker.MakeJob(JobDefOf.GotoWander, cell) call), so no new
    /// JobDef or JobDriver is needed.
    ///
    /// ⚠️ Both tick entry points are overridden on purpose. RimWorld 1.6 has two
    /// live hediff tick paths - Pawn.Tick -> HealthTick -> Hediff.PostTick ->
    /// CompPostTick, and Pawn.TickInterval -> HealthTickInterval ->
    /// Hediff.PostTickInterval -> CompPostTickInterval - and which one a given
    /// pawn takes is the engine's choice, not ours. They are mutually
    /// exclusive branches, so overriding both cannot double-fire; overriding
    /// only one risks a comp that silently never runs.
    /// </summary>
    public class HediffComp_DWWipeStumble : HediffComp
    {
        public HediffCompProperties_DWWipeStumble Props =>
            (HediffCompProperties_DWWipeStumble)props;

        public override void CompPostTick(ref float severityAdjustment) => TryStumble(1);

        public override void CompPostTickInterval(ref float severityAdjustment, int delta) =>
            TryStumble(delta);

        private void TryStumble(int delta)
        {
            // MOD_OPTIONS_RETROFIT_1: off = the wipe hediff's capMods still ramp
            // Moving/Manipulation back (that half is XML), but the droid never
            // drops a job or blunders off. No job is ever left half-started here,
            // so flipping this mid-game is safe.
            if (!RSW_DroidworksSettings.wipeStumble) return;

            Pawn p = Pawn;
            if (p == null || !p.Spawned || p.Dead || p.Downed) return;
            if (!p.IsHashIntervalTick(Props.checkIntervalTicks, delta)) return;

            // Drafted pawns are exempt: a player who has taken manual control
            // is mid-fight, and yanking the job there reads as a bug rather
            // than as flavour. FOUNDRY's own scope call, recorded in the item
            // file. In a mental state the pawn is not running a normal job at
            // all, and interrupting one is not ours to do.
            if (p.Drafted || p.InMentalState || p.jobs == null) return;
            if (p.CurJobDef == JobDefOf.GotoWander) return;

            if (!Rand.Chance(Props.stumbleChancePerCheck
                * RSW_DroidworksSettings.wipeStumbleChance * parent.Severity)) return;

            IntVec3 cell = CellFinder.RandomClosewalkCellNear(
                p.Position, p.Map, Props.stumbleRadius);
            if (cell == p.Position) return;

            Job job = JobMaker.MakeJob(JobDefOf.GotoWander, cell);
            job.locomotionUrgency = LocomotionUrgency.Walk;
            job.expiryInterval = 300;
            job.checkOverrideOnExpire = true;
            p.jobs.StartJob(job, JobCondition.InterruptForced);

            MoteMaker.ThrowText(p.DrawPos, p.Map, "...", 2f);
        }
    }
}
