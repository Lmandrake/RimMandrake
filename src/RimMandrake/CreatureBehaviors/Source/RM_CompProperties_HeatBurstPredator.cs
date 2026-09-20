using Verse;

namespace RimMandrake.CreatureBehaviors
{
    /// <summary>
    /// DESERT_BURST_PREDATOR_FLAGSHIP_1. Carried by a burst predator's race
    /// ThingDef comps list — generic RM_-tier mechanism (any future desert
    /// burst predator can reuse it), same posture as this assembly's own
    /// CompProperties_AquaticAmbusher / RM_CompProperties_Grappler.
    ///
    ///   <comps>
    ///     <li Class="RimMandrake.CreatureBehaviors.RM_CompProperties_HeatBurstPredator">
    ///       <hediffDef>RM_HeatDrivenBurst</hediffDef>
    ///     </li>
    ///   </comps>
    /// </summary>
    public class RM_CompProperties_HeatBurstPredator : CompProperties
    {
        /// <summary>The staged burst/heat-fatigue hediff to fire and read
        /// back (RM_HeatDrivenBurst, DESERT_SHADE_GRID_KEYSTONE_1) — left for
        /// XML to set; this comp never invents its own hediff.</summary>
        public HediffDef hediffDef;

        /// <summary>Cells within which a hostile target triggers the burst.
        /// INVENTED per desert.md §4's "bursts out of shadow at a speed
        /// nothing can evade" — wide enough that the burst covers a real
        /// dash, not a single-tile lunge.</summary>
        public float burstTriggerRangeCells = 12f;

        /// <summary>Hediff severity at/below which the pawn is judged
        /// "heat-fatigued" (RM_HeatDrivenBurst's own stage boundary —
        /// minSeverity 0.5 is where its "bursting" stage starts) and begins
        /// retreating toward shade instead of continuing to hunt.</summary>
        public float heatFatigueSeverityThreshold = 0.5f;

        /// <summary>ShadeAt score (0..1) a retreat destination must clear —
        /// matches RM_ShadeSeekingWanderExtension's own default.</summary>
        public float retreatShadeThreshold = 0.5f;

        /// <summary>Search radius (cells) for a retreat destination.
        /// INVENTED — wide enough to reach the next patch, not just the
        /// current tile.</summary>
        public float retreatSearchRadiusCells = 20f;

        /// <summary>How often (ticks) the comp re-checks target/hediff
        /// state. INVENTED — frequent enough that the burst and the retreat
        /// both read as responsive without scanning every tick.</summary>
        public int checkIntervalTicks = 60;

        public RM_CompProperties_HeatBurstPredator()
        {
            compClass = typeof(RM_CompHeatBurstPredator);
        }
    }
}
