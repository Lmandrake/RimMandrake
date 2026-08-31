// Selftest for the covered-pit-trap math built under RIMMANDRAKE_PITS_BUILD_1.
//
// WHY THIS EXISTS: the same offline-selftest discipline as
// src/RimMandrake/Utils/selftest_validate_patch.py - these three pieces of
// arithmetic (a tier->kg lookup, an escape-chance formula, a mass-sum-vs-
// threshold gate) are exactly the kind of thing that silently drifts across
// an edit nobody re-checks by hand, and unlike an XML patch a wrong number
// here produces no error of any kind - the trap just fires (or doesn't) at
// the wrong weight, forever, until someone happens to weigh it again.
//
// WHAT IS REAL vs EXTRACTED, AND WHY:
//   PitCoverTier.TriggerMassKg()   REAL - PitCoverTier.cs is compiled into
//     this project directly (see the .csproj). It has zero Verse/Unity
//     dependency, so there is no reason to duplicate it: a change to the
//     real enum mapping fails this test immediately.
//
//   PitEscapeUtility.EscapeChance()   EXTRACTED, not called. The real method
//     takes a live Verse.Pawn and reads pawn.BodySize / pawn.health.* -
//     none of which exist without the game running (Pawn constructs through
//     a chain of static managers; there is no offline "new Pawn()"). The
//     formula below is a byte-for-byte transcription of
//     Escape/PitEscapeUtility.cs's EscapeChance() body as of 2026-08-30,
//     with the three Pawn-derived values (bodySize, healthPct, manipulation)
//     taken as plain float parameters instead. Mathf.Clamp/Clamp01 are
//     replaced with the standard-library equivalents used below - both are
//     simple min/max clamps with no Unity-specific behaviour to lose.
//     ⚠️ THIS IS THE ONE PART OF THIS FILE THAT CAN DRIFT SILENTLY: if
//     EscapeChance()'s body changes, this test keeps passing against the
//     OLD formula unless a human updates ExtractedEscapeChance() to match.
//     It is still worth having - it locks in the formula's shape (which
//     input pushes chance up vs down) and its clamp bounds - but it is not
//     equivalent to calling the real method.
//
//   CompPitCoverTrigger.RunScan()'s spring condition   PARTIALLY REAL. The
//     real method needs a live Map/CellRect to enumerate occupied cells -
//     not testable offline. But its actual trigger decision, after the
//     cell walk, is exactly two lines:
//         if (onCover.Count > 0 && summedMass >= Pit.CoverTier.TriggerMassKg())
//     That boolean has zero Verse dependency once you have a mass total and
//     a tier, so ShouldSpring() below reproduces it verbatim (not just its
//     shape) and calls the REAL TriggerMassKg() for the threshold half.
//     ⛔ NOT COVERED: the cell-rect walk, the Pawn.Dead filter, the actual
//     GetStatValue(StatDefOf.Mass) read, and Pit.Spring() itself. All of
//     those need a live Map/Pawn and stay untested here on purpose.
//
// Run:
//   python3 src/RimMandrake/Utils/selftest_pit_logic.py
// or directly (Windows-native dotnet, Windows-style path - see the .csproj header).

using System;
using System.Collections.Generic;
using RimMandrake.Pits;

namespace RimMandrake.Pits.SelfTest
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
                Console.WriteLine("FAIL  " + name + "\n        " + ex.Message);
            }
        }

        private static void Assert(bool cond, string msg)
        {
            if (!cond) throw new Exception(msg);
        }

        private static void AssertClose(float got, float want, string msg, float eps = 0.0001f)
        {
            if (Math.Abs(got - want) > eps)
                throw new Exception($"{msg}: got {got}, want {want}");
        }

        // ---- extracted from Escape/PitEscapeUtility.cs (see header) ----------
        private static float Clamp01(float v) => Math.Clamp(v, 0f, 1f);
        private static float Clamp(float v, float lo, float hi) => Math.Clamp(v, lo, hi);

        private static float ExtractedBodyFactor(float bodySize, int depthPenalty)
        {
            return Clamp01((bodySize - depthPenalty + 1.5f) / 3f);
        }

        private static float ExtractedEscapeChance(float bodySize, int depthPenalty, float healthPct, float manipulation)
        {
            float bodyFactor = ExtractedBodyFactor(bodySize, depthPenalty);
            float chance = 0.05f + 0.55f * bodyFactor + 0.25f * healthPct + 0.15f * manipulation;
            return Clamp(chance, 0.02f, 0.95f);
        }

        // ---- verbatim (Verse-free) reproduction of RunScan's spring gate -----
        private static bool ShouldSpring(float summedMass, int occupantCount, PitCoverTier tier)
        {
            return occupantCount > 0 && summedMass >= tier.TriggerMassKg();
        }

        private static int Main()
        {
            // ---------------------------------------------------- PitCoverTier --
            Case("TriggerMassKg_WovenScrap_is_40kg", () =>
                AssertClose(PitCoverTier.WovenScrap.TriggerMassKg(), 40f, "WovenScrap"));
            Case("TriggerMassKg_PlankLattice_is_120kg", () =>
                AssertClose(PitCoverTier.PlankLattice.TriggerMassKg(), 120f, "PlankLattice"));
            Case("TriggerMassKg_ReinforcedFrame_is_220kg", () =>
                AssertClose(PitCoverTier.ReinforcedFrame.TriggerMassKg(), 220f, "ReinforcedFrame"));
            Case("TriggerMassKg_None_is_unreachable", () =>
                Assert(PitCoverTier.None.TriggerMassKg() == float.MaxValue,
                    "None must return float.MaxValue so an unarmed/uncovered pit can never spring on mass alone"));
            Case("TriggerMassKg_tiers_are_strictly_increasing", () =>
                Assert(PitCoverTier.WovenScrap.TriggerMassKg() < PitCoverTier.PlankLattice.TriggerMassKg() &&
                       PitCoverTier.PlankLattice.TriggerMassKg() < PitCoverTier.ReinforcedFrame.TriggerMassKg(),
                    "a heavier-sounding tier must have a strictly higher threshold, or the player's cover choice is meaningless"));

            // -------------------------------------------------- EscapeChance ----
            Case("EscapeChance_midrange_human_in_shallow_pit", () =>
            {
                // bodySize 1.0, Shallow(1), full health, full manipulation.
                // bodyFactor = clamp01((1-1+1.5)/3) = 0.5
                // chance = 0.05 + 0.275 + 0.25 + 0.15 = 0.725
                float got = ExtractedEscapeChance(1.0f, 1, 1.0f, 1.0f);
                AssertClose(got, 0.725f, "human/shallow/healthy chance");
            });
            Case("EscapeChance_upper_clamp_at_0_95", () =>
            {
                // bodySize 2.5, Shallow(1): bodyFactor saturates at 1.0.
                // raw chance = 0.05+0.55+0.25+0.15 = 1.0, which must clamp to 0.95.
                float got = ExtractedEscapeChance(2.5f, 1, 1.0f, 1.0f);
                AssertClose(got, 0.95f, "a big healthy pawn in a shallow pit must clamp at the 0.95 ceiling");
            });
            Case("EscapeChance_bodyFactor_floors_at_zero_not_negative", () =>
            {
                // bodySize 0.2, Chasm(3): raw (0.2-3+1.5)/3 = -0.4333, must clamp to 0.
                float bf = ExtractedBodyFactor(0.2f, 3);
                AssertClose(bf, 0f, "bodyFactor must floor at 0, not go negative, for a tiny pawn in a deep pit");
            });
            Case("EscapeChance_bigger_body_strictly_raises_chance", () =>
            {
                float small = ExtractedEscapeChance(0.5f, 1, 0.5f, 0.5f);
                float big = ExtractedEscapeChance(2.0f, 1, 0.5f, 0.5f);
                Assert(big > small, "the spec's stated direction (bigger body = easier escape) must hold");
            });
            Case("EscapeChance_deeper_pit_strictly_lowers_chance", () =>
            {
                float shallow = ExtractedEscapeChance(1.0f, (int)PitDepthTier.Shallow, 0.6f, 0.6f);
                float deep = ExtractedEscapeChance(1.0f, (int)PitDepthTier.Deep, 0.6f, 0.6f);
                float chasm = ExtractedEscapeChance(1.0f, (int)PitDepthTier.Chasm, 0.6f, 0.6f);
                Assert(shallow > deep && deep >= chasm,
                    "the spec's stated direction (deeper pit = harder escape) must hold across all three tiers");
            });
            Case("EscapeChance_more_health_strictly_raises_chance", () =>
            {
                float hurt = ExtractedEscapeChance(1.0f, 1, 0.2f, 0.5f);
                float healthy = ExtractedEscapeChance(1.0f, 1, 0.9f, 0.5f);
                Assert(healthy > hurt, "the spec's stated direction (more health = easier escape) must hold");
            });
            Case("EscapeChance_more_manipulation_strictly_raises_chance", () =>
            {
                float clumsy = ExtractedEscapeChance(1.0f, 1, 0.5f, 0.1f);
                float dextrous = ExtractedEscapeChance(1.0f, 1, 0.5f, 0.9f);
                Assert(dextrous > clumsy, "the spec's stated direction (more manipulation = easier escape) must hold");
            });

            // ---------------------------------------- mass-sum spring gate ------
            Case("ShouldSpring_empty_cover_never_springs_regardless_of_mass", () =>
                Assert(!ShouldSpring(9999f, 0, PitCoverTier.WovenScrap),
                    "the onCover.Count > 0 guard must short-circuit even with an absurd mass total"));
            Case("ShouldSpring_below_threshold_does_not_spring", () =>
                Assert(!ShouldSpring(39.9f, 1, PitCoverTier.WovenScrap), "39.9kg must not spring a 40kg tier"));
            Case("ShouldSpring_at_threshold_springs", () =>
                Assert(ShouldSpring(40.0f, 1, PitCoverTier.WovenScrap), "exactly 40kg must spring a 40kg tier (>=)"));
            Case("ShouldSpring_summed_mass_across_multiple_pawns_springs", () =>
                Assert(ShouldSpring(70f + 60f, 2, PitCoverTier.PlankLattice),
                    "two pawns totalling 130kg must spring a 120kg PlankLattice tier - this is the whole point of summing"));
            Case("ShouldSpring_None_tier_never_springs", () =>
                Assert(!ShouldSpring(float.MaxValue / 2f, 5, PitCoverTier.None),
                    "an unarmed pit (tier None) must never spring on mass"));

            Console.WriteLine($"\n{Pass.Count}/{Pass.Count + Fail.Count} passed");
            return Fail.Count == 0 ? 0 : 1;
        }
    }
}
