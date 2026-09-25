using Verse;

namespace RimMandrake.CreatureBehaviors
{
    /// <summary>
    /// WASTELAND_RADIOTHERMAL_SOLITARY_1. Carried by a species-spacing
    /// race's comps list alongside RM_SpeciesSpacingExtension (which holds
    /// all the actual tuning — this CompProperties carries none of its own,
    /// so there is nothing to keep in sync between the two).
    ///
    ///   <comps>
    ///     <li Class="RimMandrake.CreatureBehaviors.RM_CompProperties_SpeciesSpacingCook" />
    ///   </comps>
    /// </summary>
    public class RM_CompProperties_SpeciesSpacingCook : CompProperties
    {
        public RM_CompProperties_SpeciesSpacingCook()
        {
            compClass = typeof(RM_CompHeatCook);
        }
    }
}
