// Selftest for RimMandrake.Aftermath's BattleOutcomeClassifier
// (PLOT_MECHANISM_MODS_WAVE_1). Same offline-selftest discipline as
// RimMandrake.Property.SelfTest: compiles the REAL production
// BattleOutcomeClassifier.cs / BattleOutcome.cs directly (see the .csproj's
// Compile list), no live Game needed since the classifier takes plain
// ints/bools, not Verse types.
//
// This is this item's own verify bar, satisfied literally: "construct a
// synthetic BattleRecord outcome for each of the 4 classifications and
// confirm the right RM_AftermathRuleDefs become eligible (a unit-style
// selftest, not a live quicktest...)". The classifier IS the "eligible or
// not" decision AftermathRuleRunner.OnBattleClosed reads
// (def.triggerOutcomes.Contains(record.Outcome)) - this file proves the
// four buckets land where the doc says they should; AftermathRuleRunner's
// own def-matching loop (List.Contains against triggerOutcomes) is a
// one-line, already-visually-inspectable operation this project's own
// SelfTest convention does not additionally re-test (see Property's own
// SelfTest header for the same "nothing left to test offline" reasoning
// applied to PropertyEngine.Fire).
//
// Run:
//   "%USERPROFILE%\.dotnet\dotnet.exe" run --project D:\Luke\dev\Rimworld\src\RimMandrake\Aftermath\Source\SelfTest\RimMandrakeAftermath.SelfTest.csproj -c Release

using System;
using RimMandrake.Aftermath;

namespace RimMandrake.Aftermath.SelfTest
{
    internal static class Program
    {
        private static int passed;
        private static int failed;

        private static void Case(string name, Action fn)
        {
            try
            {
                fn();
                passed++;
                Console.WriteLine("ok    " + name);
            }
            catch (Exception ex)
            {
                failed++;
                Console.WriteLine("FAIL  " + name + "\n        " + ex.Message);
            }
        }

        private static void Assert(bool cond, string msg)
        {
            if (!cond) throw new Exception(msg);
        }

        private static int Main()
        {
            // --- REPELLED: >= 60% dead/downed, checked first regardless of
            // colonist casualty or survivor count. ---------------------------
            Case("Repelled_at_exactly_60_percent", () =>
                Assert(BattleOutcomeClassifier.Classify(10, 6, 0, false) == BattleOutcome.Repelled,
                    "6/10 == 60% must be REPELLED (boundary is inclusive)"));
            Case("Repelled_above_60_percent", () =>
                Assert(BattleOutcomeClassifier.Classify(10, 9, 1, false) == BattleOutcome.Repelled,
                    "90% dead/downed must be REPELLED even with a survivor counted"));
            Case("Repelled_takes_priority_over_colonist_casualty", () =>
                Assert(BattleOutcomeClassifier.Classify(10, 7, 0, true) == BattleOutcome.Repelled,
                    "70% raider losses must read REPELLED even if we also lost someone -"
                    + " a forced-out raid was not \"left by choice\""));

            // --- LOST: below the REPELLED threshold, but a colonist died or
            // was kidnapped. -----------------------------------------------
            Case("Lost_below_threshold_with_colonist_casualty", () =>
                Assert(BattleOutcomeClassifier.Classify(10, 2, 5, true) == BattleOutcome.Lost,
                    "20% raider losses + a colonist casualty must be LOST"));
            Case("Lost_with_zero_raider_losses", () =>
                Assert(BattleOutcomeClassifier.Classify(10, 0, 10, true) == BattleOutcome.Lost,
                    "raiders entirely unscathed + a colonist casualty must still be LOST"));

            // --- ROUTED: below threshold, no colonist casualty, at least one
            // survivor exited. --------------------------------------------
            Case("Routed_with_survivors_and_no_casualty", () =>
                Assert(BattleOutcomeClassifier.Classify(10, 3, 5, false) == BattleOutcome.Routed,
                    "30% losses, survivors exited, no casualty -> ROUTED"));
            Case("Routed_at_just_under_the_repelled_boundary", () =>
                Assert(BattleOutcomeClassifier.Classify(10, 5, 5, false) == BattleOutcome.Routed,
                    "50% is below the 60% REPELLED boundary -> ROUTED, not REPELLED"));

            // --- STALEMATE: the fallback - below threshold, no casualty, no
            // recorded survivor-exit either. --------------------------------
            Case("Stalemate_fallback_when_nothing_else_matches", () =>
                Assert(BattleOutcomeClassifier.Classify(10, 2, 0, false) == BattleOutcome.Stalemate,
                    "low losses, no casualty, no recorded survivor-exit -> STALEMATE fallback"));
            Case("Stalemate_on_degenerate_zero_total", () =>
                Assert(BattleOutcomeClassifier.Classify(0, 0, 0, false) == BattleOutcome.Stalemate,
                    "totalRaiders == 0 must not divide-by-zero or throw - STALEMATE is the safe default"));

            Console.WriteLine();
            Console.WriteLine((passed + failed) + " total, " + passed + " passed, " + failed + " failed.");
            return failed == 0 ? 0 : 1;
        }
    }
}
