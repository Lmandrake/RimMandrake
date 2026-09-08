namespace RimMandrake.Property
{
    // The event spine's own vocabulary (design/Jawa/ownership_settlement_spec.md
    // "act (take/use/strip/sabotage/buy/claim) -> TakingEvent"). Gifted/
    // Inherited/Looted are claim BASES (ClaimBasis), not acts here — those
    // transitions are consensual/non-adversarial and go straight through
    // PropertyEngine.RecordTransfer, which skips the perception/friction
    // half of the spine entirely (nothing to witness in a legitimate gift).
    public enum TakingAct : byte
    {
        Take,
        Use,
        Strip,
        Sabotage,
        Buy,
        Claim, // claim-fee-paid, spec item 3
    }
}
