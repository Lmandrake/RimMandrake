namespace RimMandrake.Property
{
    // Who a claim (or a suspicion) points at. Deliberately three cases only —
    // spec item 4: "The player colony is NOT a faction: each colonist is
    // their own claimant. The Clan claimant holds only the survival spine."
    // Generalized here as Commons-per-Faction so the same three cases cover
    // NPC factions symmetrically (spec item 7): a settlement's unclaimed
    // stock is that faction's Commons exactly the way the colony's shared
    // gear is the player faction's Commons.
    public enum ClaimantKind : byte
    {
        None = 0,
        Pawn = 1,
        Commons = 2,
    }
}
