namespace RimMandrake.CreatureBehaviors
{
    /// <summary>
    /// The pure rule behind RM_PerceivedBeautyPatches, compiled into the SelfTest unchanged. A creature contributes
    /// only when the mechanic is on, it is alive, and its cell is psychologically outdoors (the same outdoors flag
    /// vanilla CellBeauty uses to pick BeautyOutdoors over Beauty). Indoors it adds nothing: the owner asked for
    /// OUTDOOR beauty, and indoor/room beauty is a different stat path that animals never feed.
    /// </summary>
    public static class RM_PerceivedBeautyMath
    {
        public static float Contribution(bool enabled, float multiplier, float beautyOutdoors, bool dead, bool psychologicallyOutdoors)
        {
            if (!enabled || dead || !psychologicallyOutdoors) return 0f;
            if (multiplier <= 0f) return 0f;
            return beautyOutdoors * multiplier;
        }
    }
}
