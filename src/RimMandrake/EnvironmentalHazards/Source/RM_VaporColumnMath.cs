namespace RimMandrake.EnvironmentalHazards
{
    /// <summary>
    /// RIMMANDRAKE_PROVE_UNDER_LIQUID_LAW_LIVE round 8: which steam geysers feed a vapour column (RM_MapComponent_VaporColumns).
    /// A vent drowned in a dug pit (FlowWorks) bubbles under the liquid instead of steaming into the sky, so it paints no
    /// column, and no haze or ash spirals (TheForge's sky pastures) drift over its water (owner 2026-11-13: "It should be
    /// bubbling water, not faint ghost bubbles rising up"). Any dry square keeps it steaming. Verse-free: SelfTest
    /// VentColumnChecks runs this.
    /// </summary>
    public static class RM_VaporColumnMath
    {
        /// <param name="squares">the geyser's footprint squares</param>
        /// <param name="squaresInLiquid">how many of them stand in liquid (terrain tagged Water)</param>
        public static bool GeyserFeedsColumn(int squares, int squaresInLiquid)
        {
            return squares <= 0 || squaresInLiquid < squares;
        }
    }
}
