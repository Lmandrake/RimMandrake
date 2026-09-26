using Verse;

namespace RimMandrake.CreatureBehaviors
{
    /// <summary>
    /// WEBWORK_WEB_STRUCTURES_1 — the "commandable-adhesive slick/locked"
    /// mechanism webwork_kit_spec.md §3 and the owner-and-nest sitting
    /// (§1a's own mapping table row "commandable adhesive (slick vs
    /// locked)") both named and then explicitly deferred ("a mechanical
    /// slick-vs-locked web state is deferred to the roster/web-Things
    /// work, noted here so it is not lost").
    ///
    /// v1, scoped to what those two passes actually specified and no
    /// further (neither ever named a comp, a radius, or a building —
    /// this fills the gap with the closest existing patterns rather than
    /// inventing a whole new rule system). Deliberately NOT built here,
    /// left for a follow-on once wanted: a player-CRAFTABLE version of the
    /// trap (this v1 rides the wild sheet web the biome already spawns,
    /// not a bench recipe of its own). A generic RM_-tier ThingComp, same
    /// posture as this
    /// assembly's own RM_CompHeatPusherGated/RM_CompDrumLure — any Building
    /// can carry it, not just a Webwork def. It scans its own cell (and an
    /// optional radius) for pawns and refreshes a configured HediffDef on
    /// each one found, the "adhesive slick" itself; the hediff's own
    /// stages carry the "slick vs locked" escalation (see
    /// RUT_Webwork_Slick — early stage a slow-down, late stage a near-full
    /// Moving cap, same "CRIPPLES, never downs" posture RM_Hediff_SunScald
    /// already established for this campaign) and its own
    /// HediffCompProperties_TendDuration is the "a doctor can free them"
    /// rescue route kit §3's own player-experience text calls for.
    ///
    /// "Commandable": if the parent also carries vanilla CompFlickable,
    /// this comp only acts while CompFlickable.SwitchIsOn — the player's
    /// own Gizmo toggle, zero new C# needed for the on/off half of
    /// "commandable". A parent with no CompFlickable simply always acts
    /// while the mod setting is on (an always-on adhesive surface).
    ///
    ///   <comps>
    ///     <li Class="CompProperties_Flickable" />
    ///     <li Class="RimMandrake.CreatureBehaviors.RM_CompProperties_AdhesiveSlick">
    ///       <slickHediff>RUT_Webwork_Slick</slickHediff>
    ///       <radiusCells>0</radiusCells>
    ///     </li>
    ///   </comps>
    /// </summary>
    public class RM_CompProperties_AdhesiveSlick : CompProperties
    {
        /// <summary>The hediff refreshed on every qualifying pawn found each
        /// scan. Left for XML to set — this comp never invents its own
        /// hediff (RM_CompProperties_HeatBurstPredator/RM_CompProperties_
        /// DrumLure precedent).</summary>
        public HediffDef slickHediff;

        /// <summary>Cells beyond the parent's own cell also scanned. 0 means
        /// "only a pawn standing on this exact cell" — the natural reading
        /// for a floor-like structure (a sheet web, a gutter) rather than an
        /// area no pawn is actually touching.</summary>
        public float radiusCells = 0f;

        /// <summary>How often (ticks) the comp scans. Coarse on purpose —
        /// this is a sticky surface, not a pressure plate (CompProximityHatch
        /// precedent, same posture as RM_CompProperties_DrumLure.
        /// checkIntervalTicks).</summary>
        public int checkIntervalTicks = 60;

        /// <summary>Severity added per scan to a pawn found on/near the
        /// slick — INVENTED, tuned so a pawn that lingers several scans
        /// climbs through the hediff's stages rather than being caught
        /// instantly at "locked" the moment they step on.</summary>
        public float severityPerScan = 0.05f;

        public RM_CompProperties_AdhesiveSlick()
        {
            compClass = typeof(RM_CompAdhesiveSlick);
        }
    }
}
