using RimWorld;
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

            ticksCold += ScanIntervalTicks;
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
            int left = Props.ticksBelowBeforeDeath - ticksCold;
            return "Dying of cold: " + (left < 0 ? 0 : left).ToStringTicksToPeriod();
        }
    }
}
