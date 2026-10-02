using Verse;

namespace RimMandrake.FlowWorks.Pits
{
    // Pure scan cadence - the mass RATING itself lives on the cover host
    // (IPitCoverHost.CoverTier), not here, because a player arms a cover with
    // whichever tier they build (design/Jawa/covered_pit_traps_spec.md
    // section 3), so it is a runtime choice, not a per-ThingDef constant.
    public class CompProperties_PitCoverTrigger : CompProperties
    {
        // How often (in ticks) the cover re-sums standing mass. Kept coarse -
        // this is a trap, not a pressure plate; it does not need to fire the
        // instant a pawn's foot lands.
        public int scanIntervalTicks = 30;

        public CompProperties_PitCoverTrigger()
        {
            compClass = typeof(CompPitCoverTrigger);
        }
    }
}
