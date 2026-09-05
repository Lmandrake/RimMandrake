// Selftest for mandrake.rm.aftermath's battle recorder (PLOT_MECHANISM_MODS_WAVE_1).
//
// This item's own verify bar: "construct a synthetic BattleRecord outcome
// for each of the 4 classifications and confirm the right
// RM_AftermathRuleDefs become eligible (a unit-style selftest, not a live
// quicktest)." Same discipline as
// src/RimMandrake/Property/Source/SelfTest/Program.cs: compile the REAL
// production .cs files in directly, exercise only the parts with no live-
// Game dependency.
//
// TWO THINGS ARE REAL, compiled straight from production source:
//   BattleOutcomeClassifier.Classify(...) - pure math over synthetic counts,
//     zero Verse dependency at all.
//   AftermathRuleEligibility.IsEligible(RM_AftermathRuleDef, ...) - takes a
//     directly-constructed RM_AftermathRuleDef (Def's own constructor has no
//     live-game dependency, same as Property's SelfTest constructing
//     ClaimResolution/ClaimantRef with null Pawn/Faction payloads).
//
// NOT covered, and why: AftermathRuleRunner itself (TryQueue/PassesDiscipline)
// opens with Find.TickManager/Find.Storyteller.incidentQueue, none of which
// exist with no running Game - there is nothing of the RUNNER's own dispatch
// behavior left to exercise offline. MapComponent_BattleRecorder's Lord
// correlation likewise needs a live Map. What CAN and IS tested here is
// exactly what decides "did the right things happen" without any of that:
// the classification math, and the trigger-matching predicate.
//
// Run:
//   "%USERPROFILE%\.dotnet\dotnet.exe" run --project D:\Luke\dev\Rimworld\src\RimMandrake\Aftermath\Source\SelfTest\RimMandrakeAftermath.SelfTest.csproj -c Release

using System;
using System.Collections.Generic;
using RimMandrake.Aftermath;

namespace RimMandrake.Aftermath.SelfTest
{
    internal static class Program
    {
        private static readonly List<string> Pass = new();
        private static readonly List<(string name, string msg)> Fail = new();

        private static void Case(string name, Action fn)
        {
            try
            {
                fn();
                Pass.Add(name);
                Console.WriteLine("ok    " + name);
            }
            catch (Exception ex)
            {
                Fail.Add((name, ex.Message));
                Console.WriteLine("FAIL  " + name + "\n        " + ex);
            }
        }

        private static void Assert(bool cond, string msg)
        {
            if (!cond) throw new Exception(msg);
        }

        private static int Main()
        {
            // ------------------------------------------- BattleOutcomeClassifier ---
            // design/Jawa/proposals/plot_mechanisms_wave.md Part 2's own four
            // buckets, one synthetic input per bucket, per this item's verify
            // wording exactly.
            Case("Classify_60_percent_dead_or_downed_is_Repelled", () =>
            {
                var outcome = BattleOutcomeClassifier.Classify(
                    totalRaiders: 10, raidersDeadOrDowned: 6, raidersSurvivedAndExited: 4, colonistCasualty: false);
                Assert(outcome == BattleOutcome.Repelled, "10 raiders, 6 dead/downed (60%) must be Repelled, got " + outcome);
            });
            Case("Classify_just_under_60_percent_with_survivors_is_Routed", () =>
            {
                var outcome = BattleOutcomeClassifier.Classify(
                    totalRaiders: 10, raidersDeadOrDowned: 5, raidersSurvivedAndExited: 5, colonistCasualty: false);
                Assert(outcome == BattleOutcome.Routed, "10 raiders, 5 dead/downed (50%), 5 survived+exited, no colonist loss must be Routed, got " + outcome);
            });
            Case("Classify_colonist_casualty_with_raiders_leaving_mostly_intact_is_Lost", () =>
            {
                var outcome = BattleOutcomeClassifier.Classify(
                    totalRaiders: 10, raidersDeadOrDowned: 1, raidersSurvivedAndExited: 9, colonistCasualty: true);
                Assert(outcome == BattleOutcome.Lost, "10 raiders, 1 dead/downed (10%), a colonist casualty must be Lost, got " + outcome);
            });
            Case("Classify_no_deaths_no_survivors_recorded_is_Stalemate", () =>
            {
                // e.g. every original raider is still Spawned (an ongoing
                // fallback poll snapshot) or otherwise unaccounted-for by the
                // survived-and-exited definition (!Dead && !Downed && !Spawned).
                var outcome = BattleOutcomeClassifier.Classify(
                    totalRaiders: 10, raidersDeadOrDowned: 0, raidersSurvivedAndExited: 0, colonistCasualty: false);
                Assert(outcome == BattleOutcome.Stalemate, "no deaths, no colonist loss, no confirmed exits must be Stalemate, got " + outcome);
            });
            Case("Classify_Repelled_takes_priority_over_a_simultaneous_colonist_casualty", () =>
            {
                // The classifier's own documented priority: a 60%+ casualty
                // raid is Repelled even if we also lost someone - it was not
                // "left by choice".
                var outcome = BattleOutcomeClassifier.Classify(
                    totalRaiders: 10, raidersDeadOrDowned: 8, raidersSurvivedAndExited: 2, colonistCasualty: true);
                Assert(outcome == BattleOutcome.Repelled, "80% dead/downed must stay Repelled even with a colonist casualty, got " + outcome);
            });
            Case("Classify_zero_raiders_is_Stalemate_not_a_divide_by_zero", () =>
            {
                var outcome = BattleOutcomeClassifier.Classify(
                    totalRaiders: 0, raidersDeadOrDowned: 0, raidersSurvivedAndExited: 0, colonistCasualty: false);
                Assert(outcome == BattleOutcome.Stalemate, "degenerate zero-raiders input must not throw and must read Stalemate, got " + outcome);
            });

            // ------------------------------------------- AftermathRuleEligibility --
            // "confirm the right RM_AftermathRuleDefs become eligible" - one
            // synthetic rule per shape the real RUT_AftermathRuleDefs.xml ships.
            Case("Eligibility_RegroupAndReturn_fires_on_Routed_with_enough_survivors", () =>
            {
                var def = new RM_AftermathRuleDef
                {
                    triggerKind = AftermathTriggerKind.BattleOutcome,
                    triggerOutcomes = new List<BattleOutcome> { BattleOutcome.Routed },
                    minSurvivors = 3,
                };
                Assert(AftermathRuleEligibility.IsEligible(def, BattleOutcome.Routed, survivors: 3),
                    "Routed with exactly minSurvivors must be eligible");
                Assert(!AftermathRuleEligibility.IsEligible(def, BattleOutcome.Routed, survivors: 2),
                    "Routed with fewer than minSurvivors must NOT be eligible");
                Assert(!AftermathRuleEligibility.IsEligible(def, BattleOutcome.Repelled, survivors: 10),
                    "a rule scoped to Routed must NOT fire on Repelled, however many survivors");
            });
            Case("Eligibility_AlliesArrive_fires_on_either_Repelled_or_Routed", () =>
            {
                var def = new RM_AftermathRuleDef
                {
                    triggerKind = AftermathTriggerKind.BattleOutcome,
                    triggerOutcomes = new List<BattleOutcome> { BattleOutcome.Repelled, BattleOutcome.Routed },
                    minSurvivors = 0,
                };
                Assert(AftermathRuleEligibility.IsEligible(def, BattleOutcome.Repelled, survivors: 0), "Repelled must be eligible");
                Assert(AftermathRuleEligibility.IsEligible(def, BattleOutcome.Routed, survivors: 0), "Routed must be eligible");
                Assert(!AftermathRuleEligibility.IsEligible(def, BattleOutcome.Stalemate, survivors: 0), "Stalemate must not be eligible");
                Assert(!AftermathRuleEligibility.IsEligible(def, BattleOutcome.Lost, survivors: 0), "Lost must not be eligible");
            });
            Case("Eligibility_ScavengersOnTheField_fires_only_on_Repelled", () =>
            {
                var def = new RM_AftermathRuleDef
                {
                    triggerKind = AftermathTriggerKind.BattleOutcome,
                    triggerOutcomes = new List<BattleOutcome> { BattleOutcome.Repelled },
                    minSurvivors = 0,
                };
                Assert(AftermathRuleEligibility.IsEligible(def, BattleOutcome.Repelled, survivors: 0), "Repelled must be eligible");
                Assert(!AftermathRuleEligibility.IsEligible(def, BattleOutcome.Routed, survivors: 0), "Routed must not be eligible");
            });
            Case("Eligibility_non_BattleOutcome_trigger_kind_is_never_eligible_via_this_path", () =>
            {
                // Rules 4-8 (PrisonerHeldDuration etc.) are data-only this
                // build - AftermathRuleRunner.OnBattleClosed must never treat
                // one as eligible off a BattleRecord close, whatever outcome
                // is passed in.
                var def = new RM_AftermathRuleDef
                {
                    triggerKind = AftermathTriggerKind.PrisonerHeldDuration,
                    triggerOutcomes = new List<BattleOutcome> { BattleOutcome.Repelled, BattleOutcome.Routed, BattleOutcome.Stalemate, BattleOutcome.Lost },
                    minSurvivors = 0,
                };
                foreach (BattleOutcome outcome in new[] { BattleOutcome.Repelled, BattleOutcome.Routed, BattleOutcome.Stalemate, BattleOutcome.Lost })
                {
                    Assert(!AftermathRuleEligibility.IsEligible(def, outcome, survivors: 999),
                        "a PrisonerHeldDuration-kind rule must never be eligible via the BattleOutcome path (outcome=" + outcome + ")");
                }
            });
            Case("Eligibility_null_def_is_never_eligible", () =>
                Assert(!AftermathRuleEligibility.IsEligible(null, BattleOutcome.Repelled, 0), "null def must not throw and must be ineligible"));

            Console.WriteLine($"\n{Pass.Count}/{Pass.Count + Fail.Count} passed");
            return Fail.Count == 0 ? 0 : 1;
        }
    }
}
