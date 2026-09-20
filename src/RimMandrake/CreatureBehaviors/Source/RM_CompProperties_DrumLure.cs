using Verse;

namespace RimMandrake.CreatureBehaviors
{
    /// <summary>
    /// DRUM_LURE_PREDATOR_BUILD_1. deep_desert.md §4's "the ground lies to
    /// you": predators hunt by vibration and appraise by water, so "both
    /// sides evolved to falsify the signal... predators with lures that
    /// drum juicy — an angler's decoy that sounds like a fat animal."
    ///
    /// Confirmed before writing this: no stock RimWorld comp broadcasts a
    /// false signal that pulls another pawn's OWN pathing toward a tile.
    /// `rimsage` search_defs/search_source for "Lure" returns nothing in
    /// vanilla+DLC, and this assembly's own two nearest sibling ambush
    /// mechanisms (CompProperties_AquaticAmbusher, RM_CompProperties_
    /// HeatBurstPredator) both only ever act on the PREDATOR — neither one
    /// compels the victim to move. Compelling the target is the genuinely
    /// new part, so this is real tier-c work, not a reachable XML pattern
    /// (rimworld-modding skill §3).
    ///
    /// Generic RM_-tier mechanism, same posture as this assembly's own
    /// CompProperties_AquaticAmbusher / RM_CompProperties_HeatBurstPredator:
    /// any future lure predator's race ThingDef comps list can point at it,
    /// not just RSW_Drazzik.
    ///
    ///   <comps>
    ///     <li Class="RimMandrake.CreatureBehaviors.RM_CompProperties_DrumLure">
    ///       <luredHediff>RM_DrumLureLured</luredHediff>
    ///       <submersionHediff>RM_DrumLureSubmersion</submersionHediff>
    ///     </li>
    ///   </comps>
    ///
    /// See RM_CompDrumLure for the state machine.
    /// </summary>
    public class RM_CompProperties_DrumLure : CompProperties
    {
        /// <summary>Marker hediff forced onto the lured victim so the comp
        /// never re-issues the compulsion job every scan, so two lure
        /// predators can't both claim the same victim, and so the player
        /// gets a visible, readable reason their pawn just walked toward
        /// danger. Self-clears (HediffCompProperties_Disappears) if the
        /// predator dies, is disturbed, or the victim wanders back out of
        /// range before the ambush lands. Left for XML to set; this comp
        /// never invents its own hediff (RM_CompProperties_HeatBurstPredator
        /// precedent).</summary>
        public HediffDef luredHediff;

        /// <summary>Optional. The predator's own "hidden beneath the sand"
        /// state while lying in wait and while a lure is in progress — same
        /// optional/nullable shape as CompProperties_AquaticAmbusher.
        /// invisibilityHediff. Null means the predator simply stays visible
        /// the whole time (a valid, simpler creature).</summary>
        public HediffDef submersionHediff;

        /// <summary>Cells within which the predator can pick out a target to
        /// lure. INVENTED per desert.md §4's "hunts by vibration" — wide
        /// enough that the lure reads as reaching well beyond melee range,
        /// the way a real vibration signal would.</summary>
        public float lureRadiusCells = 18f;

        /// <summary>Once the lured target has closed to this many cells, the
        /// predator surfaces and strikes instead of continuing to wait.</summary>
        public float ambushRangeCells = 1.9f;

        /// <summary>Chance per scan that the predator actually calls, once a
        /// target is in range and not already lured by someone else — the
        /// sheet's own "predators appraise... and usually decline" economic-
        /// decision framing (§4/§5), never a guaranteed trigger the instant
        /// prey is sighted.</summary>
        public float lureChancePerScan = 0.35f;

        /// <summary>How often (ticks) the comp scans for a target or checks
        /// an in-progress lure. Coarse on purpose — this is a patient ambush,
        /// not a pressure plate (CompProximityHatch precedent).</summary>
        public int checkIntervalTicks = 90;

        public RM_CompProperties_DrumLure()
        {
            compClass = typeof(RM_CompDrumLure);
        }
    }
}
