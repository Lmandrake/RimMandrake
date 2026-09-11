namespace RimMandrake.Aftermath
{
    // Extracted so AftermathRuleRunner.OnBattleClosed's own eligibility check
    // can be offline-selftested against synthetic BattleOutcome values (this
    // item's own verify bar: "construct a synthetic BattleRecord outcome for
    // each of the 4 classifications and confirm the right RM_AftermathRuleDefs
    // become eligible") without needing a live DefDatabase or Game. Takes an
    // already-constructed RM_AftermathRuleDef (a plain object outside a
    // running game -- Def has no live-game dependency in its constructor)
    // rather than a defName lookup, so the test can build one directly.
    public static class AftermathRuleEligibility
    {
        public static bool IsEligible(RM_AftermathRuleDef def, BattleOutcome outcome, int survivors)
        {
            if (def == null) return false;
            if (def.triggerKind != AftermathTriggerKind.BattleOutcome) return false;
            if (def.triggerOutcomes == null || !def.triggerOutcomes.Contains(outcome)) return false;
            if (survivors < def.minSurvivors) return false;
            return true;
        }

        // Rule 6 ("Zizzik's aftermath"). The trigger's own conditions --
        // within 2 days of a battle, Zizzik >= Content -- are checked by the
        // caller (AftermathRuleRunner.OnMentalBreakNearBattle) before this is
        // ever reached; this predicate is purely "is this def even the right
        // shape," kept separate so it stays offline-testable with no live
        // Game/tick/Ninefold dependency, same reasoning as IsEligible above.
        public static bool IsEligibleMentalBreakNearBattle(RM_AftermathRuleDef def)
        {
            return def != null && def.triggerKind == AftermathTriggerKind.MentalBreakNearBattle;
        }

        // Rule 4 ("They come for their own"), wired 2026-09-10. The trigger's
        // own conditions -- which faction, hostility, raidsForbidden -- are
        // resolved by the caller (AftermathRuleRunner.OnPrisonerHeldTooLong)
        // from the live Pawn/Faction, which this predicate deliberately does
        // not touch so it stays offline-testable with a bare float, same
        // reasoning as IsEligible/IsEligibleMentalBreakNearBattle above.
        public static bool IsEligiblePrisonerHeldDuration(RM_AftermathRuleDef def, float heldDays)
        {
            if (def == null) return false;
            if (def.triggerKind != AftermathTriggerKind.PrisonerHeldDuration) return false;
            return heldDays >= def.minHeldDays;
        }
    }
}
