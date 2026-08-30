using RimWorld;
using UnityEngine;
using Verse;

namespace Droidworks
{
    public class HediffCompProperties_DWBoltResentment : HediffCompProperties
    {
        /// Severity gained per in-game day while DW_RestrainingBolt is present.
        public float severityPerDayWhileBolted = 0.05f;

        public HediffCompProperties_DWBoltResentment() =>
            compClass = typeof(HediffComp_DWBoltResentment);
    }

    /// <summary>
    /// DROIDWORKS_BOLT_CORE_1 - the resentment accumulator. Rises only while
    /// DW_RestrainingBolt is present on a Humanlike (sapient) pawn, and -
    /// the whole point of the mechanic (design/Jawa/droid_system_spec.md
    /// section 7: "Sapients accumulate resentment that persists after
    /// removal -> instant rebellion when freed") - is PINNED once the bolt is
    /// gone rather than decaying back to zero. Mirrors
    /// HediffComp_PoweredDown.CompPostTick's own "pin, never decay" trick:
    /// severityAdjustment is always forced to zero so nothing in the engine's
    /// own severity-decay machinery can touch it, and the ONLY thing that
    /// ever moves severity is this method's own conditional bump.
    ///
    /// This is a stub accumulator, not a consequence system - nothing reads
    /// this hediff's severity yet. See the // TODO comments on
    /// HediffDefs_Droidworks.xml's DW_BoltResentment entry for what a later
    /// phase hangs off it (mood aura, idiosyncrasy-disable,
    /// instant-rebellion-on-removal) - none of that is built here.
    /// everVisible=false on the def: the player is never meant to see a
    /// number, only the eventual consequence.
    /// </summary>
    public class HediffComp_DWBoltResentment : HediffComp
    {
        public HediffCompProperties_DWBoltResentment Props =>
            (HediffCompProperties_DWBoltResentment)props;

        public override void CompPostTick(ref float severityAdjustment)
        {
            severityAdjustment = 0f; // never decay, never rise on its own - only this method moves it

            Pawn p = Pawn;
            if (p == null || p.Dead) return;
            if (p.RaceProps == null || p.RaceProps.intelligence != Intelligence.Humanlike) return;
            if (!p.health.hediffSet.HasHediff(DroidworksDefOf.DW_RestrainingBolt)) return;

            float gainPerTick = Props.severityPerDayWhileBolted / GenDate.TicksPerDay;
            parent.Severity = Mathf.Min(parent.def.maxSeverity, parent.Severity + gainPerTick);
        }
    }
}
