using RimWorld;
using UnityEngine;
using Verse;

namespace RimMandrake.StarWars.BrainWorms
{
    public class CompProperties_RSWColdKill : CompProperties
    {
        /// Ambient temperature (celsius) at or below which the thing starts dying.
        public float lethalTemperature = 0f;

        /// How long it must stay that cold before it dies. 2500 ticks is one hour.
        public int ticksBelowBeforeDeath = 2500;

        /// Optional one-shot message when it dies. Null/empty sends nothing.
        public string deathMessage;

        public CompProperties_RSWColdKill()
        {
            compClass = typeof(CompRSWColdKill);
        }
    }

    /// <summary>
    /// BRAINWORM_MOD_BUILD_1 - the cold half of the canon, on things rather than on
    /// hosts. Geonosian brain worms and their eggs die below freezing; the infection
    /// inside a host is cured by the same cold through
    /// <see cref="HediffComp_BrainWormProgress"/>, which is the separate, host-side
    /// mechanism. Both read Thing.AmbientTemperature, which is defined everywhere a
    /// thing can be - on a map cell, inside a container, and (via the world tile) in
    /// a caravan - so carrying eggs across the nightside kills them too.
    ///
    /// Deliberately a timed death rather than the vanilla hypothermia ladder: a worm
    /// is a payload, and "walked it into the dark and it stopped" has to be legible
    /// in about an hour of game time rather than as a hediff race.
    ///
    /// Works on a Pawn and on an item alike, because both are ThingWithComps. A Pawn
    /// is KILLED (leaving an ordinary dead worm on the floor); an item is destroyed.
    /// </summary>
    public class CompRSWColdKill : ThingComp
    {
        private const int ScanIntervalTicks = 250;

        private int ticksUntilScan;
        private int ticksCold;

        public CompProperties_RSWColdKill Props => (CompProperties_RSWColdKill)props;

        public bool TooCold => parent.AmbientTemperature <= Props.lethalTemperature;

        public override void PostExposeData()
        {
            base.PostExposeData();
            Scribe_Values.Look(ref ticksCold, "ticksCold", 0);
            Scribe_Values.Look(ref ticksUntilScan, "ticksUntilScan", 0);
        }

        public override void CompTick()
        {
            base.CompTick();

            if (--ticksUntilScan > 0)
            {
                return;
            }
            ticksUntilScan = ScanIntervalTicks;

            if (!TooCold)
            {
                ticksCold = 0;
                return;
            }

            // MOD_OPTIONS_RETROFIT_1: rate multiplier only, floored above zero by the
            // settings slider — this mechanism must never become impossible to trigger.
            ticksCold += Mathf.Max(1, Mathf.RoundToInt(ScanIntervalTicks * RSW_BrainWormsSettings.coldKillRateMultiplier));
            if (ticksCold < Props.ticksBelowBeforeDeath)
            {
                return;
            }

            Die();
        }

        private void Die()
        {
            // Snapshot before the kill/destroy: both paths can clear Map and Position.
            Map map = parent.MapHeld;
            IntVec3 pos = parent.PositionHeld;

            if (parent is Pawn pawn)
            {
                if (pawn.Dead)
                {
                    return;
                }
                pawn.Kill(null);
            }
            else
            {
                if (parent.Destroyed)
                {
                    return;
                }
                parent.Destroy(DestroyMode.Vanish);
            }

            if (!Props.deathMessage.NullOrEmpty() && map != null)
            {
                Messages.Message(Props.deathMessage, new TargetInfo(pos, map), MessageTypeDefOf.NeutralEvent, historical: false);
            }
        }

        public override string CompInspectStringExtra()
        {
            if (!TooCold)
            {
                return null;
            }
            // ticksCold is accumulated at ScanIntervalTicks * coldKillRateMultiplier
            // per real ScanIntervalTicks elapsed (MOD_OPTIONS_RETROFIT_1), so the raw
            // "ticksBelowBeforeDeath - ticksCold" gap is in scaled units, not real game
            // ticks. Divide by the same multiplier before formatting it as a period, or
            // the displayed ETA is wrong whenever the slider isn't at its 1.0x default.
            int scaledLeft = Props.ticksBelowBeforeDeath - ticksCold;
            int left = Mathf.RoundToInt(Mathf.Max(0, scaledLeft) / Mathf.Max(0.01f, RSW_BrainWormsSettings.coldKillRateMultiplier));
            return "Dying of cold: " + left.ToStringTicksToPeriod();
        }
    }
}
