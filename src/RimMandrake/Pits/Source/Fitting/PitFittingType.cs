namespace RimMandrake.Pits
{
    // "One framework, five faces" (covered_pit_traps_spec.md section 5 title)
    // - the variants share ONE Building_OpenPit class; what differs is data,
    // carried by CompProperties_PitFitting. Baited (bait slot, passive lure)
    // and the gated prisoner Pit Cell are NOT fitting types: baited is a
    // separate always-available comp (not yet built - open question, see
    // item file) and the Pit Cell is a distinct holder subclass
    // (Building_PitCell), not a floor fitting, per spec section 6.
    public enum PitFittingType
    {
        Bare,       // capture only - the bloodless take
        Spiked,     // lethal fall damage on capture
        Oiled,      // soaks occupants; ignitable via gizmo
        Poison,     // slow toxin buildup over time, not on impact
        Water,      // no climbing out at all; non-swimmers drown if left
        Oubliette,  // EMP burst on capture - disables mechanoids/droids
    }
}
