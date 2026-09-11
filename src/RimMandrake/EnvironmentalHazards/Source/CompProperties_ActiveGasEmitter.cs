using Verse;

namespace RimMandrake.EnvironmentalHazards
{
    // ALPHA_MECHANICS_KIT_1 item 1 (alpha_family_source_review.md §4.1).
    //
    // "A ThingComp with CompProperties fields for gasType (any ThingDef of
    // category Gas), radius, rate, tickInterval, optional power-gate."
    //
    // Nothing here knows what the gas IS. Any building, plant, corpse or
    // creature ThingDef can carry this comp and name its own gas def.
    //
    // XML usage (fully-qualified Class= on purpose: RimWorld resolves a bare
    // short type name across EVERY loaded assembly, so a same-named class in
    // another mod would be an ambiguous, silent coin-flip):
    //
    //   <comps>
    //     <li Class="RimMandrake.EnvironmentalHazards.CompProperties_ActiveGasEmitter">
    //       <gasType>RM_ExampleSporeGas</gasType>
    //       <radius>4.9</radius>
    //       <rate>0.25</rate>
    //       <tickIntervalTicks>512</tickIntervalTicks>
    //       <requiresPower>true</requiresPower>
    //     </li>
    //   </comps>
    //
    // The parent ThingDef needs <tickerType>Normal</tickerType> for CompTick
    // to be reached at all (see CompActiveGasEmitter's own note on why this
    // uses a manual countdown inside CompTick rather than CompTickRare).
    public class CompProperties_ActiveGasEmitter : CompProperties
    {
        // The gas Thing spawned. Any ThingDef works; RM_BaseGas (Defs/) is the
        // abstract parent that gives a def the vanilla fields a gas needs.
        public ThingDef gasType;

        // Cells within this radius of the parent are candidates each burst.
        public float radius = 3.9f;

        // Per-candidate-cell probability of receiving gas in a burst. 1.0
        // floods the whole radius every burst; the donor family's own default
        // shape is a sparse random subset, hence a fraction here.
        public float rate = 0.2f;

        // Ticks between bursts. Deliberately coarse — a gas emitter is
        // ambience, not a weapon, and every emitter on the map pays this.
        public int tickIntervalTicks = 512;

        // When true, the comp only emits while a sibling CompPowerTrader
        // reports PowerOn. A def with no CompPowerTrader and requiresPower
        // true never emits — ConfigErrors says so rather than failing silent.
        public bool requiresPower;

        // When true a burst is skipped entirely if the parent's own cell is
        // roofed — for emitters that are meant to read as open-air vents.
        public bool requiresUnroofed;

        public CompProperties_ActiveGasEmitter()
        {
            compClass = typeof(CompActiveGasEmitter);
        }

        public override System.Collections.Generic.IEnumerable<string> ConfigErrors(ThingDef parentDef)
        {
            foreach (string err in base.ConfigErrors(parentDef))
            {
                yield return err;
            }

            if (gasType == null)
            {
                yield return "CompProperties_ActiveGasEmitter has no gasType — the comp would tick forever and emit nothing.";
            }

            if (tickIntervalTicks < 1)
            {
                yield return "CompProperties_ActiveGasEmitter tickIntervalTicks must be >= 1.";
            }

            // GenRadial.RadialCellsAround logs an engine error and returns a
            // truncated pattern past its cached maximum, so an over-large
            // radius fails loudly at load rather than every tick in play.
            if (radius <= 0f || radius >= GenRadial.MaxRadialPatternRadius)
            {
                yield return "CompProperties_ActiveGasEmitter radius must be > 0 and < GenRadial.MaxRadialPatternRadius ("
                             + GenRadial.MaxRadialPatternRadius + ").";
            }

            if (parentDef != null && parentDef.tickerType == TickerType.Never)
            {
                yield return "CompProperties_ActiveGasEmitter needs tickerType Normal on its parent ThingDef; tickerType Never means CompTick is never called.";
            }

            if (requiresPower && parentDef != null && !HasPowerTrader(parentDef))
            {
                yield return "CompProperties_ActiveGasEmitter has requiresPower true but the parent ThingDef carries no CompProperties_Power — it would never emit.";
            }
        }

        private static bool HasPowerTrader(ThingDef parentDef)
        {
            if (parentDef.comps == null)
            {
                return false;
            }

            for (int i = 0; i < parentDef.comps.Count; i++)
            {
                if (parentDef.comps[i] is RimWorld.CompProperties_Power)
                {
                    return true;
                }
            }

            return false;
        }
    }
}
