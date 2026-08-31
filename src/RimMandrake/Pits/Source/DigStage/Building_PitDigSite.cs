using Verse;

namespace RimMandrake.Pits
{
    // The under-construction pit. Placed like any normal building
    // (Blueprint -> Frame via vanilla constructible machinery -
    // ConstructionSpeed, matching the spec's "construction/mining hybrid
    // job"); once its frame completes it exists as this Building carrying a
    // CompPitDigStage. Shallow-tier dig sites are already done at that point
    // (1 required stage = placement); Deep/Chasm need further "Dig Deeper"
    // passes worked by JobDriver_DigPitDeeper.
    //
    // Deliberately a plain Building - no special Tick/Print override. All
    // the actual mechanic lives in the comp so a future "prisoner pit" dig
    // site can reuse the exact same class with a different
    // CompProperties_PitDigStage.openPitDef.
    public class Building_PitDigSite : Building
    {
    }
}
