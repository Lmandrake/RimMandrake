using Verse;

namespace RimMandrake.CreatureBehaviors
{
    /// <summary>
    /// WASTELAND_RADIOTHERMAL_SOLITARY_1. wasteland.md §4's "keep distance
    /// from their own kind or cook each other" — attach to a race ThingDef
    /// to make RM_JobGiver_AvoidOwnKind steer it away from other members of
    /// its own PawnKindDef, and (with RM_CompProperties_SpeciesSpacingCook
    /// also in its comps list) take heat damage whenever it fails to keep
    /// even that much distance. Single source of truth for both halves —
    /// neither reads its own separate copy of these numbers.
    ///
    ///   <modExtensions>
    ///     <li Class="RimMandrake.CreatureBehaviors.RM_SpeciesSpacingExtension">
    ///       <avoidRadiusCells>8</avoidRadiusCells>
    ///       <cookRadiusCells>3</cookRadiusCells>
    ///       <cookDamagePerInterval>4</cookDamagePerInterval>
    ///       <cookIntervalTicks>250</cookIntervalTicks>
    ///     </li>
    ///   </modExtensions>
    /// </summary>
    public class RM_SpeciesSpacingExtension : DefModExtension
    {
        /// <summary>Cells within which the avoidance JobGiver treats another
        /// member of the same PawnKindDef as "too close" and tries to walk
        /// away. INVENTED — wide enough that avoidance reads as a real
        /// behavior, not a single-tile shuffle.</summary>
        public float avoidRadiusCells = 8f;

        /// <summary>Cells within which the pair is judged to have actually
        /// failed to keep distance (a tighter radius than avoidRadiusCells —
        /// avoidance is meant to prevent ever reaching this) and the cook
        /// damage starts applying. INVENTED, deliberately tighter than
        /// avoidRadiusCells: this is the "or cook each other" failure case
        /// (a pen, a cage, a cornered map), not the everyday outcome.</summary>
        public float cookRadiusCells = 3f;

        /// <summary>Heat damage applied to self each interval while crowded
        /// this close. INVENTED.</summary>
        public float cookDamagePerInterval = 4f;

        /// <summary>Ticks between cook-damage checks. INVENTED — a slow
        /// simmer, not a fast burn.</summary>
        public int cookIntervalTicks = 250;

        /// <summary>DamageDef used for the cook tick; defaults to
        /// DamageDefOf.Burn in code if left unset.</summary>
        public DamageDef cookDamageDef;

        /// <summary>Chance per avoidance check that the JobGiver actually
        /// scans and (if crowded) issues a Goto — same "don't recompute a
        /// path every single tick" throttle RM_JobGiver_SeekShade's own
        /// seekChancePerCheck uses.</summary>
        public float checkChancePerCheck = 0.3f;
    }
}
