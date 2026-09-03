namespace RimMandrake.Property
{
    // Generic ENGINE defaults only. The spec's own closing line is explicit:
    // "Open tuning (execution-time, not blocking): decay curves per
    // recognizability band · propagation rates per profile · ... All data,
    // all RimUtinni." Nothing here is Jawa/campaign-specific — these are the
    // numbers the fabric needs to be runnable and testable on its own before
    // any RimUtinni tuning data exists. A later pass may replace these
    // constants with a per-faction/per-band Def-driven lookup; until then
    // every consumer reads them from exactly this one place.
    public static class PropertyTuning
    {
        // ClaimDecay: a recognizability-0 claim (steel bar) is gone in this
        // many days; a recognizability-1 claim (named astromech) takes this
        // many days — long enough to read as "never" at normal campaign
        // pace without literally being infinite (float math over an actual
        // ∞ lifetime is a bug waiting to happen).
        public const float MinClaimLifetimeDays = 3f;
        public const float MaxClaimLifetimeDays = 3650f;

        // FactionRecord propagation: how much of a witnessed confidence
        // value has reached the faction record per day elapsed. 1/3 per day
        // means full propagation in three days — a flat generic default;
        // spec item 6's per-faction security profile (Hutts excellent,
        // Tuskens ~nil) is exactly the RimUtinni override point.
        public const float DefaultPropagationRatePerDay = 1f / 3f;

        // FactionRecord decay: a witnessed entry's contribution to
        // GetSuspicion falls off linearly to zero over this many days from
        // the witness tick, and is lazily pruned from the entries list once
        // it gets there (spec item 6: "Decay is computed lazily" — never a
        // scheduled tick). Without this, suspicion only accumulates and
        // permanently saturates after a couple of witnessed events. 45 days
        // sits alongside ClaimDecay's lifetimes above: long enough that a
        // recent theft still reads as suspicious, short enough that nothing
        // witnessed a campaign ago haunts a faction forever.
        public const float SuspicionHalfLifeDays = 45f;

        // PerceptionUtility: how far (in cells) a conscious witness can spot
        // a taking, subject to line-of-sight. Generic default, not a
        // per-faction surveillance value.
        public const float DefaultWitnessRadius = 15f;

        // Flat per-witness confidence for this pass's simple perception
        // roll (spec's brief explicitly asks for "a witness check + a
        // stored suspect-confidence value", not per-trait tuning).
        public const float DefaultWitnessConfidence = 0.75f;

        // Virtual (computed, unrecorded) claim strengths.
        public const float SituationalClaimStrength = 0.9f;
        public const float TerritorialClaimStrength = 0.5f;
    }
}
