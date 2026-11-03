namespace RimMandrake.Bones
{
    // BONES_LEAN_PORT_BUILD_TREELESS_WORLD: the butcher-bone arithmetic, free of the game so it can be swept
    // offline. The donor (sihv.rombonesPort BoneMod.dll, decompiled) added RoundRandom(BoneAmount x boneFactor x
    // efficiency) bones whenever the meat yield was above 1; this keeps that gate and adds two of ours: never
    // from a body that is not flesh (mechanoids) or is insectoid (chitin, no bone; the donor zeroed BaseInsect
    // and a hand list of modded insects by patch instead).
    public static class RM_BonesKernel
    {
        public const float MaxMultiplier = 5f;

        /// <summary>The expected bone count before rounding: 0 when any gate is shut, else
        /// boneAmount x multiplier x efficiency (each factor floored at 0).</summary>
        public static float ExpectedBones(bool enabled, bool isFlesh, bool isInsect, int meatCount,
            float boneAmount, float multiplier, float efficiency)
        {
            if (!enabled || !isFlesh || isInsect || meatCount <= 1)
            {
                return 0f;
            }
            if (boneAmount <= 0f || multiplier <= 0f || efficiency <= 0f)
            {
                return 0f;
            }
            if (multiplier > MaxMultiplier)
            {
                multiplier = MaxMultiplier;
            }
            return boneAmount * multiplier * efficiency;
        }
    }
}
