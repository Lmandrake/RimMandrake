using Verse;

namespace RimMandrake.FeverWood
{
    // FEVERWOOD_TWO_FRONT_LURE_1. XML shape for RM_CompLureStake — no
    // fields of its own (the staked/hediff bookkeeping lives on the comp
    // instance, not its properties), same minimal shape RM_CompProperties_
    // EscapedCaptive uses for a comp with nothing to configure.
    public class RM_CompProperties_LureStake : CompProperties
    {
        public RM_CompProperties_LureStake()
        {
            compClass = typeof(RM_CompLureStake);
        }
    }
}
