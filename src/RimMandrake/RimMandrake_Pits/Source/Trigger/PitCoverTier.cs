namespace RimMandrake.Pits
{
    // Cover tiers, section 3 of covered_pit_traps_spec.md - the player's
    // targeting knob, chosen when arming an open pit (Building_OpenPit's
    // "Arm Cover" gizmos), NOT baked into the pit's ThingDef:
    //   Woven scrap        ~40kg  - humansized-and-up falls
    //   Plank & lattice    ~120kg - heavies/mechs/big game fall
    //   Reinforced frame   ~400kg - only monsters and vehicles fall
    // These are the spec's own placeholder ratings, not yet tuned - that
    // tuning is exactly what the spawn-mass quicktest matrix is for.
    public enum PitCoverTier
    {
        None = 0,
        WovenScrap,
        PlankLattice,
        ReinforcedFrame,
    }

    public static class PitCoverTierExtensions
    {
        public static float TriggerMassKg(this PitCoverTier tier)
        {
            switch (tier)
            {
                case PitCoverTier.WovenScrap: return 40f;
                case PitCoverTier.PlankLattice: return 120f;
                case PitCoverTier.ReinforcedFrame: return 400f;
                default: return float.MaxValue; // None: nothing should ever spring it
            }
        }
    }
}
