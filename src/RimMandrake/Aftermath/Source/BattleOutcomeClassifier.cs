namespace RimMandrake.Aftermath
{
    // Pure, no-Verse-dependency classification logic — deliberately extracted
    // so it can be selftested offline with synthetic inputs (this item's own
    // verify bar: "construct a synthetic BattleRecord outcome for each of the
    // 4 classifications... a unit-style selftest, not a live quicktest").
    // MapComponent_BattleRecorder computes these inputs from live Lord/Pawn
    // state and calls this; nothing else should reimplement the ordering.
    public static class BattleOutcomeClassifier
    {
        // design/Jawa/proposals/plot_mechanisms_wave.md Part 2:
        // "REPELLED (>= 60% of pawns dead/downed), ROUTED (survivors exited
        // - feeds the roster), STALEMATE (timeout/steal-and-leave), LOST
        // (colonist deaths/kidnaps >= 1 and raiders left by choice)".
        //
        // The doc's four buckets are not spelled out as mutually exclusive
        // in every edge case, so this method fixes a deterministic priority
        // (documented per branch below) rather than leaving it ambiguous:
        //
        //   1. REPELLED is checked FIRST and is purely a raider-casualty
        //      fraction — objective, and takes priority over everything else
        //      because a 60%+ casualty raid was not "left by choice" no
        //      matter what else happened.
        //   2. Only once REPELLED is ruled out does a colonist casualty
        //      decide LOST — this is exactly the doc's "raiders left by
        //      choice" condition: the raiders were NOT forced out by losses,
        //      yet we still lost someone.
        //   3. ROUTED needs at least one raider to have survived and left
        //      under their own power with no colonist casualty.
        //   4. STALEMATE is the fallback: nobody died/was downed past the
        //      REPELLED threshold, nobody on our side was lost, and no
        //      raider is recorded as having survived-and-exited either (the
        //      ambiguous "timeout" / "steal-and-leave" case this project has
        //      no verified vanilla RaidStrategyDef to key off — see this
        //      mod's own item-file note).
        public static BattleOutcome Classify(
            int totalRaiders,
            int raidersDeadOrDowned,
            int raidersSurvivedAndExited,
            bool colonistCasualty)
        {
            if (totalRaiders <= 0)
                return BattleOutcome.Stalemate; // degenerate input - nothing to classify

            float fraction = raidersDeadOrDowned / (float)totalRaiders;

            if (fraction >= 0.6f)
                return BattleOutcome.Repelled;

            if (colonistCasualty)
                return BattleOutcome.Lost;

            if (raidersSurvivedAndExited > 0)
                return BattleOutcome.Routed;

            return BattleOutcome.Stalemate;
        }
    }
}
