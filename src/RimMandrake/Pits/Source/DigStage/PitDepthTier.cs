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
        //
        // Tier-scaled (previously flat 2200f regardless of tier, despite
        // taking tier as a parameter - a Chasm's extra stages costing the
        // same as a Deep pit's is wrong on its face). No other tier-scaled
        // method here gives a single clean ratio to mirror exactly (MaxBodySize
        // goes to float.MaxValue for Chasm), so this uses a modest, roughly-
        // 1.5x-per-step scaling off the original 2200f Deep baseline: Shallow
        // is lower (RequiredStages == 1 means Shallow never actually calls
        // this today, but keep it consistent for when a modded def changes
        // that), Deep keeps the original calibrated value, Chasm is higher to
        // reflect its heavier, shoring-supported dig.
        public static float WorkPerAdditionalStage(this PitDepthTier tier)
        {
            switch (tier)
            {
                case PitDepthTier.Shallow: return 1500f;
                case PitDepthTier.Deep: return 2200f;
                case PitDepthTier.Chasm: return 3300f;
                default: return 2200f;
            }
        }
    }
}
