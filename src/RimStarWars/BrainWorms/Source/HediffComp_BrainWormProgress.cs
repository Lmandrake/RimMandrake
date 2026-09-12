using RimWorld;
using Verse;

namespace RimMandrake.StarWars.BrainWorms
{
    public class HediffCompProperties_BrainWormProgress : HediffCompProperties
    {
        /// Severity gained per day while the host is warm. At 0.14 the ladder is
        /// roughly 2.5 days latent, 3 days influenced, then puppeted.
        public float severityPerDay = 0.14f;

        /// Ambient celsius at or below which the parasite is dying instead of growing.
        public float coldThreshold = 0f;

        /// Severity per day while cold. Negative. -3 clears a fully puppeted host in
        /// about eight hours of below-freezing ambient - a journey, not a recipe.
        public float severityPerDayWhenCold = -3f;

        /// What crawls out when the cold wins. Null spawns nothing.
        public PawnKindDef expelledWorm;

        public HediffCompProperties_BrainWormProgress()
        {
            compClass = typeof(HediffComp_BrainWormProgress);
        }
    }

    /// <summary>
    /// BRAINWORM_MOD_BUILD_1 - the whole temperature story of the infection in one
    /// comp, because progression and cure are the same number with a different sign.
    /// Subclasses vanilla HediffComp_SeverityModifierBase, which is what actually
    /// gets ticked in 1.6 (CompPostTickInterval, on a 200-tick cadence) and which
    /// already does the per-day-to-per-tick arithmetic correctly.
    ///
    /// 🔑 The cold weakness is the gift: on a tidally locked world the cure is a
    /// PLACE. Thing.AmbientTemperature answers on a map cell, inside a container AND
    /// (through the world tile) in a caravan, so carrying an infected friend into the
    /// nightside genuinely cures them on the road.
    ///
    /// Hediff.ShouldRemove is severity <= 0, so nothing here has to remove anything:
    /// the negative rate walks severity to zero and the engine drops the hediff. The
    /// expulsion then happens in CompPostPostRemoved, gated on a LIVE ambient-
    /// temperature check (not the cached `cold` field, which only refreshes every
    /// 200 ticks) so that a surgical removal does NOT drop a live worm on the
    /// operating table.
    /// </summary>
    public class HediffComp_BrainWormProgress : HediffComp_SeverityModifierBase
    {
        private bool cold;

        public HediffCompProperties_BrainWormProgress Props => (HediffCompProperties_BrainWormProgress)props;

        public override void CompExposeData()
        {
            base.CompExposeData();
            Scribe_Values.Look(ref cold, "cold", defaultValue: false);
        }

        public override void CompPostTickInterval(ref float severityAdjustment, int delta)
        {
            Pawn p = Pawn;
            cold = p != null && !p.Dead && p.AmbientTemperature <= Props.coldThreshold;
            base.CompPostTickInterval(ref severityAdjustment, delta);
        }

        public override float SeverityChangePerDay()
        {
            // MOD_OPTIONS_RETROFIT_1: only the warm-side growth rate is tunable; the
            // cold cure rate (severityPerDayWhenCold) is untouched by any setting.
            return cold ? Props.severityPerDayWhenCold
                        : Props.severityPerDay * RSW_BrainWormsSettings.progressionSpeedMultiplier;
        }

        public override string CompTipStringExtra =>
            cold ? "The cold is killing the parasite." : null;

        public override void CompPostPostRemoved()
        {
            base.CompPostPostRemoved();

            if (Props.expelledWorm == null)
            {
                return;
            }

            Pawn p = Pawn;
            if (p == null || p.Dead || !p.Spawned || p.Map == null)
            {
                return;
            }

            // Recompute live rather than trust the cached `cold` field: that flag is
            // only refreshed on the 200-tick CompPostTickInterval cadence, so it can
            // still read true for up to ~3 seconds of game time after the pawn was
            // moved somewhere warm. A surgical removal (Recipe_RemoveHediff calls
            // health.RemoveHediff directly, with no severity-tick in between) can
            // land inside that stale window - exactly the "live worm on the operating
            // table" the header doc rules out. Ambient temperature answers now, not
            // as of the last sample.
            if (p.AmbientTemperature > Props.coldThreshold)
            {
                return;
            }

            BrainWormUtility.SpawnWormBurst(p.Map, p.Position, 1, Props.expelledWorm);
            Messages.Message(
                "A brain worm crawls out of " + p.LabelShort + " into the cold.",
                p,
                MessageTypeDefOf.PositiveEvent,
                historical: false);
        }
    }
}
