namespace RimMandrake.Aftermath
{
    // Who the queued payload raid's `parms.faction` is, per rule. Rules 1-3's
    // two modes are resolved through AftermathRuleRunner.ResolveTargetFaction
    // off a BattleRecord. Rule 4's HeldPrisonerHome is WIRED (2026-09-10) but
    // resolved a DIFFERENT way, off the held Pawn directly
    // (AftermathRuleRunner.OnPrisonerHeldTooLong reads prisoner.HomeFaction) -
    // there is no BattleRecord for a prisoner-duration trigger, so
    // ResolveTargetFaction's own switch never sees this value and still
    // falls to its `default: return null` branch for it. HuttClaimant (rule
    // 8) remains genuinely NOT WIRED - named here so the def data can point
    // at the right shape once that engine work lands (see this mod's own
    // item-file note).
    public enum AftermathPayloadFactionMode
    {
        SameAsTrigger,  // rules 1, 3: the faction that just fought/scavenges is the one that returns
        AllyOfTrigger,  // rule 2: RM_AlliancePairDef's "b" faction, keyed off the defeated "a"
        HuttClaimant,   // rule 8 (NOT WIRED) - the Hutt faction specifically
        HeldPrisonerHome, // rule 4 (WIRED, resolved off the Pawn directly - not through ResolveTargetFaction)
    }
}
