namespace RimMandrake.Pits
{
    // Cover tiers, section 3 of covered_pit_traps_spec.md - the player's
    // targeting knob, chosen when arming an open pit (Building_OpenPit's
    // "Arm Cover" gizmos), NOT baked into the pit's ThingDef:
    //   Woven scrap        ~40kg  - humansized-and-up falls
    //   Plank & lattice    ~120kg - heavies/mechs/big game fall
    //   Reinforced frame   ~220kg - only monsters and vehicles fall
    // These are the spec's own placeholder ratings; the quicktest matrix
    // measured 400kg as unreachable by any single vanilla creature (240kg
    // ceiling), so the owner ruled 220kg (2026-08-30) - within reach of the
    // biggest single beasts (elephant/megasloth/thrumbo at 240kg still clear
    // it) while still excluding humans/heavies. Filed BEAST_MASS_REALISM_AUDIT_1
    // on the same ruling: the 240kg ceiling itself looked suspiciously low.
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
                case PitCoverTier.ReinforcedFrame: return 220f;
                default: return float.MaxValue; // None: nothing should ever spring it
            }
        }
    }
}
