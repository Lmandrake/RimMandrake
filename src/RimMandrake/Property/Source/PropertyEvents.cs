using Verse;

namespace RimMandrake.Property
{
    // Hook points other content binds to. This fabric fires them; it never
    // handles them — spec's Module boundaries table: RimUtinni owns "Jawa
    // heat tuning" (the actual social-fight content), this mod owns only
    // the event that content reacts to (spec item 4/10).
    public static class PropertyEvents
    {
        // Fired synchronously from PropertyEngine.Fire, ONLY when: the act
        // was unauthorized, the prior claimant resolves to a live Pawn, and
        // that Pawn is among the rolled witnesses (spec item 7: "'using my
        // stuff' fires the same TakingEvent -> witnessed by the owner ->
        // social fight per Jawa heat tuning"). No handler is wired here —
        // this pass ships the hook, not the fight.
        public static event System.Action<TakingEvent, Pawn> UnauthorizedTakingWitnessedByOwner;

        public static void RaiseUnauthorizedTakingWitnessedByOwner(TakingEvent evt, Pawn owner)
        {
            UnauthorizedTakingWitnessedByOwner?.Invoke(evt, owner);
        }

        // Fired whenever a new ClaimRecord is written (theft, purchase,
        // claim-fee, gift, inheritance, loot) — a generic provenance hook
        // for anything that wants to log or react to ownership changing,
        // without caring about the friction path above.
        public static event System.Action<Thing, ClaimRecord> ClaimRecorded;

        public static void RaiseClaimRecorded(Thing thing, ClaimRecord record)
        {
            ClaimRecorded?.Invoke(thing, record);
        }
    }
}
