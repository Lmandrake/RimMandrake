namespace RimMandrake.CreatureBehaviors
{
    // LONGSHADE_SHEET_STRUCTURAL_RULINGS_1 — the pure half of RM_SandBuriedGraphic.cs.
    // Deliberately System-only (no Verse) so SelfTestSandBuried compiles this exact file.
    public static class RM_SandBuriedGraphic
    {
        /// <summary>The pure decision, kept separate so a reader (and the selftest's
        /// truth table in Utils/selftest_sand_buried_graphic.py) sees every input.</summary>
        public static bool ShouldDrawBuried(bool enabled, bool vanillaResult, bool spawned, bool humanlike,
            bool hasSwimGraphic, bool onlyWhenStill, bool moving, bool onBuryTerrain)
        {
            if (vanillaResult)
            {
                return true;
            }
            if (!enabled || !spawned || humanlike || !hasSwimGraphic)
            {
                return false;
            }
            if (onlyWhenStill && moving)
            {
                return false;
            }
            return onBuryTerrain;
        }
    }
}
