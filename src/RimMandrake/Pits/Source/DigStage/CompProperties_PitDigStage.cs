using Verse;

namespace RimMandrake.Pits
{
    public class CompProperties_PitDigStage : CompProperties
    {
        public PitDepthTier depthTier = PitDepthTier.Shallow;

        // The def to become once the final stage completes. Must be a
        // Building_OpenPit (or subclass, e.g. Building_PitCell).
        public ThingDef openPitDef;

        public CompProperties_PitDigStage()
        {
            compClass = typeof(CompPitDigStage);
        }
    }
}
