namespace RimMandrake.Aftermath
{
    // Who the queued payload raid's `parms.faction` is, per rule. Only the
    // two modes the currently-wired rules (1-3) need are implemented; the
    // Hutt/exchange-specific modes rules 4 and 8 would need are named here so
    // the def data can point at the right shape once that engine work lands,
    // but AftermathRuleRunner does not evaluate those rules yet (see this
    // mod's own item-file note).
    public enum AftermathPayloadFactionMode
    {
        SameAsTrigger,  // rules 1, 3: the faction that just fought/scavenges is the one that returns
        AllyOfTrigger,  // rule 2: RM_AlliancePairDef's "b" faction, keyed off the defeated "a"
        HuttClaimant,   // rule 8 (NOT WIRED) - the Hutt faction specifically
        HeldPrisonerHome, // rule 4 (NOT WIRED) - the held prisoner's own home faction
    }
}
