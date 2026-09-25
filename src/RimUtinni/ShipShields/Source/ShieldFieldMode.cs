namespace RimMandrake.Utinni.ShipShields
{
    // shd:loadout-tradeoff: "I think they should be the same shields, you're
    // just installing modules to increase their switching capacity/
    // configuration" -- one building, one active mode at a time.
    //
    // shd:spore-membrane is CUT (owner: "spores aren't magical, just
    // particulates") and stays absent. shd:cryo-envelope was ruled v2 in
    // the review sheet's original prefill, then promoted v2->v1 by the
    // owner's own sitting note ("The opposite of the thermal rejection
    // shield...") -- see the ruling table at the top of ship_shields_
    // deep_design.md. It is NOT absent; CompShieldCryoEnvelope built
    // 2026-09-25. (This comment previously said cryo-envelope was
    // deliberately absent -- that was stale the moment the v1 promotion
    // landed, corrected here rather than left standing.)
    public enum ShieldFieldMode : byte
    {
        Bubble = 0,
        Thermal = 1,
        Particulate = 2,
        Cryo = 3,
    }
}
