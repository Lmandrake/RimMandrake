using RimWorld;
using Verse;

namespace RimMandrake.StarWars.BrainWorms
{
    public class HediffCompProperties_BrainWormPuppeteer : HediffCompProperties
    {
        /// Severity at or above which the hive is driving. Matches the "puppeted"
        /// stage's minSeverity in HediffDefs_BrainWorm.xml; keep the two in step.
        public float puppetSeverity = 0.8f;

        public MentalStateDef mentalState;

        public HediffCompProperties_BrainWormPuppeteer()
        {
            compClass = typeof(HediffComp_BrainWormPuppeteer);
        }
    }

    /// <summary>
    /// BRAINWORM_MOD_BUILD_1 - the puppeting half. Copies vanilla Hediff_Scaria's
    /// shape exactly (Verse/Hediff_Scaria.cs): a mental state def whose own
    /// maxTicksBeforeRecovery will end it on its own, kept alive by re-starting it
    /// from the hediff every interval for as long as the condition holds. That is
    /// how vanilla builds a "permanent" mental state and it survives save/load,
    /// downing, capture and sleep without any state of our own.
    ///
    /// 🔴 LIVING HOSTS ONLY - owner's permanent ruling, 2026-09-11: "Never
    /// corpse-walker. Too gross." Every guard below requires a living pawn, and a
    /// hediff stops ticking the moment its pawn dies, so a corpse can never be
    /// puppeted by this comp. Do not add a death path.
    ///
    /// Humanlike-gated because the behaviour lives in the Humanlike think tree
    /// (ThinkTreeDefs_BrainWormPuppet.xml, insertTag Humanlike_PostMentalState). An
    /// animal host would enter a mental state with no think-tree entry and just
    /// stand there, so it is refused rather than looking broken.
    /// </summary>
    public class HediffComp_BrainWormPuppeteer : HediffComp
    {
        private const int ScanIntervalTicks = 60;

        /// One letter per episode, not one per restart. The mental state itself is
        /// started transitionSilently (it lapses and is restarted every 60000 ticks,
        /// the Hediff_Scaria way, and a letter on each restart would be spam), so
        /// the announcement lives here and resets only when the hive lets go.
        private bool announced;

        public HediffCompProperties_BrainWormPuppeteer Props =>
            (HediffCompProperties_BrainWormPuppeteer)props;

        private bool InOurState
        {
            get
            {
                Pawn p = Pawn;
                return p?.mindState?.mentalStateHandler != null
                    && p.mindState.mentalStateHandler.CurStateDef == Props.mentalState;
            }
        }

        public override void CompExposeData()
        {
            base.CompExposeData();
            Scribe_Values.Look(ref announced, "announced", defaultValue: false);
        }

        public override void CompPostTickInterval(ref float severityAdjustment, int delta)
        {
            base.CompPostTickInterval(ref severityAdjustment, delta);

            if (Props.mentalState == null)
            {
                return;
            }

            Pawn p = Pawn;
            if (p == null || p.Dead || p.mindState?.mentalStateHandler == null)
            {
                return;
            }
            if (!p.IsHashIntervalTick(ScanIntervalTicks, delta))
            {
                return;
            }

            bool shouldPuppet = parent.Severity >= Props.puppetSeverity
                && p.RaceProps != null
                && p.RaceProps.Humanlike;

            if (shouldPuppet)
            {
                if (!p.Spawned || p.Downed || InOurState)
                {
                    return;
                }
                bool started = p.mindState.mentalStateHandler.TryStartMentalState(
                    Props.mentalState,
                    "CausedByHediff".Translate(Def.LabelCap),
                    forced: true,
                    forceWake: true,
                    causedByMood: false,
                    null,
                    transitionSilently: true);

                if (started && !announced)
                {
                    announced = true;
                    Announce(p);
                }
                return;
            }

            // Severity fell back below the threshold (the cold, or tending): let go.
            announced = false;
            if (InOurState)
            {
                p.mindState.mentalStateHandler.CurState.RecoverFromState();
            }
        }

        private static void Announce(Pawn p)
        {
            if (!PawnUtility.ShouldSendNotificationAbout(p))
            {
                return;
            }
            Find.LetterStack.ReceiveLetter(
                "Puppeted: " + p.LabelShortCap,
                "The brain worm in " + p.LabelShort + " has taken over. The body is alive and moving, and it will attack anyone who is not carrying a worm of their own.\n\n"
                    + "Cold kills the parasite: get the host below freezing and keep them there. A surgeon steady enough can also cut it out, at a real risk of killing them.",
                LetterDefOf.ThreatBig,
                p);
        }

        public override void CompPostPostRemoved()
        {
            base.CompPostPostRemoved();
            if (InOurState)
            {
                Pawn.mindState.mentalStateHandler.CurState.RecoverFromState();
            }
        }
    }
}
