namespace RimMandrake.Property
{
    // Spec item 3's exact exception list, plus the two virtual-computed
    // bases (Territorial/Situational — never stored, ClaimEngine computes
    // them fresh every query) and one provenance-origin marker (spec item 5:
    // "Battle loot keeps its origin claim at ~1.0" — the ORIGINAL owner's
    // record persists under this basis alongside the looter's own Looted
    // record; both live in the same Thing's claim set).
    public enum ClaimBasis : byte
    {
        // Virtual — computed by ClaimEngine, never written to the ledger.
        Territorial = 0,
        Situational = 1,

        // Recorded — the exception list (spec item 3).
        Stolen = 2,
        Purchased = 3,
        ClaimFeePaid = 4,
        Gifted = 5,
        Inherited = 6,
        Looted = 7,

        // Recorded — the pre-loot owner's provenance record, kept alongside
        // a Looted record for whoever now holds it (spec item 5).
        BattleLootOrigin = 8,
    }
}
