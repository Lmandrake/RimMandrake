using System.Collections.Generic;
using RimWorld;
using UnityEngine;
using Verse;

namespace RimMandrake.StarWars.BrainWorms
{
    public class HediffCompProperties_BrainWormWhispers : HediffCompProperties
    {
        /// Only whispers at or above this severity - the "influenced" stage.
        public float minSeverity = 0.35f;

        /// Stops once the hive is openly driving; a puppet does not mutter, it acts.
        public float maxSeverity = 0.8f;

        public float mtbHours = 4f;

        public List<string> texts = new List<string>();

        public HediffCompProperties_BrainWormWhispers()
        {
            compClass = typeof(HediffComp_BrainWormWhispers);
        }
    }

    /// <summary>
    /// BRAINWORM_MOD_BUILD_1 - the "whispering" the spec asks for at the influenced
    /// stage. Pure flavour, no mechanical effect: a text mote over the host's head so
    /// the player can SEE that something is wrong before the hediff's own stage
    /// label tells them. The mechanical debuffs of that stage are stage fields in
    /// HediffDefs_BrainWorm.xml, not here.
    ///
    /// Throttled by MTB rather than a fixed interval so several infected colonists do
    /// not mutter in lockstep.
    /// </summary>
    public class HediffComp_BrainWormWhispers : HediffComp
    {
        private const int CheckIntervalTicks = 250;

        public HediffCompProperties_BrainWormWhispers Props =>
            (HediffCompProperties_BrainWormWhispers)props;

        public override void CompPostTickInterval(ref float severityAdjustment, int delta)
        {
            base.CompPostTickInterval(ref severityAdjustment, delta);

            if (Props.texts.NullOrEmpty())
            {
                return;
            }

            Pawn p = Pawn;
            if (p == null || p.Dead || !p.Spawned || p.Map == null || !p.Awake())
            {
                return;
            }
            if (parent.Severity < Props.minSeverity || parent.Severity >= Props.maxSeverity)
            {
                return;
            }
            if (!p.IsHashIntervalTick(CheckIntervalTicks, delta))
            {
                return;
            }
            if (!Rand.MTBEventOccurs(Props.mtbHours, 2500f, CheckIntervalTicks))
            {
                return;
            }

            MoteMaker.ThrowText(
                p.DrawPos + new Vector3(0f, 0f, 0.85f),
                p.Map,
                Props.texts.RandomElement(),
                new Color(0.6f, 0.8f, 0.4f),
                3.5f);
        }
    }
}
