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
    }
}
