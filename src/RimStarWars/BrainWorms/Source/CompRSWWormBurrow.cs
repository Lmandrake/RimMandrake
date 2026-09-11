using RimWorld;
using Verse;

namespace RimMandrake.StarWars.BrainWorms
{
    public class CompProperties_RSWWormBurrow : CompProperties
    {
        /// How far the worm can reach a host from. Canon entry is nose/mouth, so this
        /// is deliberately "it is on you", not "it is in the room".
        public float searchRadius = 1.9f;

        public int scanIntervalTicks = 120;

        /// Chance per scan against a host who is awake and on their feet.
        public float chancePerScanAwake = 0.04f;

        /// Chance per scan against a host who is downed, asleep or anaesthetised.
        public float chancePerScanHelpless = 0.6f;

        public HediffDef infectionHediff;

        public float initialSeverity = 0.02f;

        public CompProperties_RSWWormBurrow()
        {
            compClass = typeof(CompRSWWormBurrow);
        }
    }

    /// <summary>
    /// BRAINWORM_MOD_BUILD_1 - how a worm becomes an infection. The worm does not
    /// fight: it waits until a host is close enough and enters, and the worm pawn is
    /// gone from that moment (it is inside). No letter, no message: the infection is
    /// LATENT and is supposed to be found later by HediffComp_Discoverable, which is
    /// the whole point of the staged design.
    ///
    /// 🔴 LIVING HOSTS ONLY - owner's permanent ruling, 2026-09-11, verbatim:
    /// "Never corpse-walker. Too gross." IsValidHost below refuses a dead pawn, and
    /// a Corpse is not a Pawn so it is never even a candidate. Do not relax either
    /// check; a dead-host path is not deferred work, it is banned work.
    ///
    /// Also refuses to act while the worm is itself freezing (see CompRSWColdKill):
    /// without that, the worm expelled BY the cold cure would immediately re-enter
    /// the host it just left, and the journey into the night would do nothing.
    /// </summary>
    public class CompRSWWormBurrow : ThingComp
    {
        private int ticksUntilScan;

        public CompProperties_RSWWormBurrow Props => (CompProperties_RSWWormBurrow)props;

        public override void PostExposeData()
        {
            base.PostExposeData();
            Scribe_Values.Look(ref ticksUntilScan, "ticksUntilScan", 0);
        }

        public override void CompTick()
        {
            base.CompTick();

            if (--ticksUntilScan > 0)
            {
                return;
            }
            ticksUntilScan = Props.scanIntervalTicks;
            RunScan();
        }

        /// Split out so a bridge/quicktest can drive one deterministic scan without
        /// stepping ticks and hoping the cadence lined up - the same shape
        /// CompProximityHatch.RunScan uses in this codebase.
        public void RunScan()
        {
            if (Props.infectionHediff == null)
            {
                return;
            }
            if (!(parent is Pawn worm) || !worm.Spawned || worm.Dead)
            {
                return;
            }

            // Too cold to move, let alone burrow. Keeps the cold cure one-way.
            CompRSWColdKill cold = worm.GetComp<CompRSWColdKill>();
            if (cold != null && cold.TooCold)
            {
                return;
            }

            Map map = worm.Map;
            foreach (Thing t in GenRadial.RadialDistinctThingsAround(worm.Position, map, Props.searchRadius, useCenter: true))
            {
                if (!(t is Pawn host) || !IsValidHost(worm, host))
                {
                    continue;
                }

                bool helpless = host.Downed || !host.Awake();
                if (!Rand.Chance(helpless ? Props.chancePerScanHelpless : Props.chancePerScanAwake))
                {
                    continue;
                }

                Burrow(worm, host);
                return;
            }
        }

        private bool IsValidHost(Pawn worm, Pawn host)
        {
            if (host == worm || !host.Spawned)
            {
                return false;
            }
            // 🔴 The living-host law. Never relax this.
            if (host.Dead)
            {
                return false;
            }
            if (host.RaceProps == null || !host.RaceProps.Humanlike || !host.RaceProps.IsFlesh)
            {
                return false;
            }
            if (host.health?.hediffSet == null)
            {
                return false;
            }
            // One worm per skull, and never another worm.
            if (BrainWormUtility.IsHiveFlesh(host))
            {
                return false;
            }
            return true;
        }

        private void Burrow(Pawn worm, Pawn host)
        {
            Hediff hediff = HediffMaker.MakeHediff(Props.infectionHediff, host);
            hediff.Severity = Props.initialSeverity;
            host.health.AddHediff(hediff);

            if (!worm.Destroyed)
            {
                worm.Destroy(DestroyMode.Vanish);
            }
        }
    }
}
