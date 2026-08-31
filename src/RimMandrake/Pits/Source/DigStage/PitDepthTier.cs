namespace RimMandrake.Pits
{
    // Depth tiers, section 2 of covered_pit_traps_spec.md:
    //   Shallow (1 stage): holds bodysize <= 1 (human-and-down)
    //   Deep    (2 stages): holds bodysize <= 2.5
    //   Chasm   (3 stages, needs shoring materials): holds megafauna
    //
    // "1 stage" for Shallow means placement (the normal Blueprint -> Frame
    // construction) IS the one stage - a Shallow dig site finishes open the
    // moment its frame completes. Deep and Chasm need 1 or 2 further
    // "dig deeper" work passes (CompPitDigStage) after that. Chasm's "needs
    // shoring materials" is carried by the Chasm ThingDef's own costList
    // (ordinary constructible cost), not by special-cased code.
    public enum PitDepthTier
    {
        Shallow = 1,
        Deep = 2,
        Chasm = 3,
    }

    public static class PitDepthTierExtensions
    {
        public static int RequiredStages(this PitDepthTier tier)
        {
            switch (tier)
            {
                case PitDepthTier.Shallow: return 1;
                case PitDepthTier.Deep: return 2;
                case PitDepthTier.Chasm: return 3;
                default: return 1;
            }
        }

        public static float MaxBodySize(this PitDepthTier tier)
        {
            switch (tier)
            {
                case PitDepthTier.Shallow: return 1f;
                case PitDepthTier.Deep: return 2.5f;
                case PitDepthTier.Chasm: return float.MaxValue; // megafauna: no cap
                default: return 1f;
            }
        }

        // Work required PER STAGE BEYOND the first (the first stage is the
        // normal construction frame, priced by the ThingDef's own costList/
        // workToBuild). Modeled on JobDriver_RemoveBuilding's own scale
        // (workLeft consumed at ConstructionSpeed * 1.7f per tick) so a
        // deepening pass reads at roughly the same pace as demolishing a
        // similarly-sized wall - a placeholder the quicktest matrix should
        // sanity-check, not a tuned value.
        public static float WorkPerAdditionalStage(this PitDepthTier tier)
        {
            return 2200f;
        }
    }
}
