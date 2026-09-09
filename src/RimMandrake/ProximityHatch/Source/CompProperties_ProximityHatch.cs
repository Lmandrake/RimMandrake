using Verse;

namespace RimMandrake.ProximityHatch
{
    // EGG_PROXIMITY_HATCH_TRIGGER_1. Pairs with vanilla CompProperties_Hatcher
    // (RimWorld/CompHatcher.cs) on the same ThingDef. CompHatcher only ever
    // hatches on its own timer - CompTick accumulates gestateProgress every
    // tick and calls Hatch() once it crosses 1f (confirmed by reading
    // CompHatcher.cs directly, not assumed). This comp adds a second trigger
    // path - proximity - without touching or replacing that timer; whichever
    // fires first wins, because Hatch() just runs immediately when called.
    //
    // Scan cadence deliberately follows the precedent already in this
    // codebase, RimMandrake.Pits.CompPitCoverTrigger
    // (src/RimMandrake/Pits/Source/Trigger/CompPitCoverTrigger.cs): a manual
    // tick countdown inside CompTick, not CompTickRare. The egg's ThingDef
    // needs tickerType Normal anyway for CompHatcher's own CompTick to
    // accumulate gestateProgress every tick, and the engine only invokes a
    // ThingWithComps' comps' CompTickRare() when that Thing's OWN tickerType
    // is Rare - so a sibling CompTickRare here would simply never fire.
    // A manual countdown is the only way to get a coarse, perf-safe cadence
    // on a Thing that is already ticking Normal for an unrelated reason.
    public class CompProperties_ProximityHatch : CompProperties
    {
        // Detection radius in cells, def-configurable so a big predator's
        // egg can watch further out than a small one's - never hardcoded.
        public float triggerRadius = 4f;

        // How often (in ticks) the comp scans GenRadial for a pawn in range.
        // Coarse on purpose: this is an ambush trap, not a pressure plate.
        // 60 ticks (1 real-time second) is frequent enough that the delay
        // is never noticed and cheap enough to run unconditionally on every
        // proximity egg on the map - the expensive part (the radial scan)
        // only happens once per egg per second, not once per egg per tick.
        public int scanIntervalTicks = 60;

        public CompProperties_ProximityHatch()
        {
            compClass = typeof(CompProximityHatch);
        }
    }
}
