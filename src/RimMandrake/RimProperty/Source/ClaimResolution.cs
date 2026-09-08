namespace RimMandrake.Property
{
    // The result of ClaimEngine.ResolveClaim: "whose claim is this, how
    // strong (already decayed), what basis" — the event spine's own
    // language for the claim-resolution step.
    public readonly struct ClaimResolution
    {
        public readonly ClaimantRef Claimant;
        public readonly float EffectiveStrength;
        public readonly ClaimBasis Basis;
        public readonly bool IsRecorded;
        public readonly int TimestampTicks;

        public ClaimResolution(ClaimantRef claimant, float effectiveStrength, ClaimBasis basis, bool isRecorded, int timestampTicks)
        {
            Claimant = claimant;
            EffectiveStrength = effectiveStrength;
            Basis = basis;
            IsRecorded = isRecorded;
            TimestampTicks = timestampTicks;
        }
    }
}
