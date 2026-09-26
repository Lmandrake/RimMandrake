namespace RimMandrake.FeverWood
{
    // FEVERWOOD_TENTACLE_BESTIARY_1. The six limb-types named in the design
    // sheet (fever_wood_deep_and_mud_2026-09-23.md §2/§2b): "different
    // sizes and maybe types of tentacles (act like different species, but
    // they are all connected to the same great elder being)". Bloom is
    // handled by its own comp (RM_CompTentacleEye), not this enum's
    // Feeler..Sentinel ladder, because it alone carries the eye's
    // three-tier (retreat / map-wide drive-off / permanent kill) ladder
    // rather than the ordinary two-tier (retreat / severed) one.
    public enum RM_TentacleRole
    {
        Feeler,
        Snare,
        Lash,
        Porter,
        Sentinel,
    }
}
