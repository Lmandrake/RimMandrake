// Selftest for the RM_Property fabric (PROPERTY_FABRIC_BUILD_1).
//
// WHY THIS EXISTS: same offline-selftest discipline as
// src/RimMandrake/Utils/selftest_validate_patch.py and this repo's other
// SelfTest projects. See this project's own .csproj header for exactly
// what IS and is NOT covered and why (PropertyEngine/ClaimEngine.
// ResolveClaim's public surface all no-ops with no live Game - there is
// nothing left of THEM to test offline).
//
// THREE THINGS ARE REAL, compiled straight from production source (see the
// .csproj's Compile list):
//   ClaimDecay.LifetimeTicks()/EffectiveStrength() - pure math, zero
//     live-game dependency beyond resolving UnityEngine.Mathf/Verse.GenDate
//     (a plain const), called directly.
//   ClaimantRef.Equals()/GetHashCode()/OfPawn()/OfCommons()/IsUnclaimed -
//     called directly, using NULL Pawn/Faction references. This is a valid
//     state for the struct's own contract (Kind is stored independently of
//     whether the payload resolved to a real object) and the equality
//     check every Commons-same-faction gate in TheftHauler/SalvageClaim's
//     own FloatMenuOptionProviders depends on never touches the Pawn/
//     Faction object's own fields - only reference identity.
//
// ONE THING IS EXTRACTED, not called: ClaimEngine.ResolveClaim's own
// winner-picking order (strength desc, then specificity desc, then
// timestamp desc) lives inside a PRIVATE method (Specificity()) and an
// inline lambda passed to List<T>.Sort() - neither is reachable from
// outside the class, and the containing public method (ResolveClaim
// itself) cannot be exercised offline at all (see .csproj header). Picking
// a winner from a list of ClaimResolution values is exactly the kind of
// ordering logic that silently breaks on an edit (a swapped
// CompareTo argument order, a wrong sign) with no error - it just quietly
// resolves the wrong claimant forever. PickWinner() below is a
// byte-for-byte transcription of ClaimEngine.cs's own
// `candidates.Sort(...); return candidates[0];` tail, as of 2026-09-02,
// operating on REAL ClaimResolution/ClaimantRef values (not reimplemented
// data shapes - only the comparator itself is copied). If ClaimEngine's
// own comparator is ever edited, this file must be re-diffed against it by
// hand; there is no way to make a test import a private method.
//
// Run:
//   python3 src/RimMandrake/Utils/selftest_property_fabric.py

using System;
using System.Collections.Generic;
using RimMandrake.Property;

namespace RimMandrake.Property.SelfTest
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

        private static void AssertClose(float got, float want, string msg, float eps = 0.01f)
        {
            if (Math.Abs(got - want) > eps)
                throw new Exception($"{msg}: got {got}, want {want}");
        }

        // EXTRACTED from ClaimEngine.cs's private Specificity() method,
        // byte-for-byte as of 2026-09-02.
        private static int Specificity(ClaimantRef c)
        {
            switch (c.Kind)
            {
                case ClaimantKind.Pawn: return 2;
                case ClaimantKind.Commons: return 1;
                default: return 0;
            }
        }

        // EXTRACTED from ClaimEngine.ResolveClaim's own
        // `candidates.Sort(...); return candidates[0];` tail, byte-for-byte
        // as of 2026-09-02 (see this file's own header for why the real
        // method cannot be called directly).
        private static ClaimResolution PickWinner(List<ClaimResolution> candidates)
        {
            candidates.Sort((a, b) =>
            {
                int byStrength = b.EffectiveStrength.CompareTo(a.EffectiveStrength);
                if (byStrength != 0) return byStrength;

                int bySpecificity = Specificity(b.Claimant).CompareTo(Specificity(a.Claimant));
                if (bySpecificity != 0) return bySpecificity;

                return b.TimestampTicks.CompareTo(a.TimestampTicks);
            });
            return candidates[0];
        }

        private static int Main()
        {
            // --------------------------------------------------- ClaimDecay ------
            Case("LifetimeTicks_at_zero_recognizability_is_the_MIN_days", () =>
                AssertClose(ClaimDecay.LifetimeTicks(0f),
                    PropertyTuning.MinClaimLifetimeDays * 60000f, // GenDate.TicksPerDay
                    "recognizability 0 -> MinClaimLifetimeDays", 1f));
            Case("LifetimeTicks_at_full_recognizability_is_the_MAX_days", () =>
                AssertClose(ClaimDecay.LifetimeTicks(1f),
                    PropertyTuning.MaxClaimLifetimeDays * 60000f,
                    "recognizability 1 -> MaxClaimLifetimeDays", 1f));
            Case("LifetimeTicks_clamps_recognizability_above_1", () =>
                AssertClose(ClaimDecay.LifetimeTicks(5f), ClaimDecay.LifetimeTicks(1f),
                    "recognizability >1 must clamp to the same result as 1"));
            Case("LifetimeTicks_clamps_recognizability_below_0", () =>
                AssertClose(ClaimDecay.LifetimeTicks(-5f), ClaimDecay.LifetimeTicks(0f),
                    "recognizability <0 must clamp to the same result as 0"));

            Case("EffectiveStrength_at_age_zero_is_unchanged", () =>
                AssertClose(ClaimDecay.EffectiveStrength(0.8f, 0, 0.5f), 0.8f,
                    "ageTicks<=0 must return initialStrength untouched"));
            Case("EffectiveStrength_at_or_past_lifetime_is_zero", () =>
            {
                float lifetime = ClaimDecay.LifetimeTicks(0.5f);
                AssertClose(ClaimDecay.EffectiveStrength(1f, (int)lifetime, 0.5f), 0f,
                    "age == lifetime must fully decay to 0");
                AssertClose(ClaimDecay.EffectiveStrength(1f, (int)lifetime * 10, 0.5f), 0f,
                    "age >> lifetime must still be 0, not negative");
            });
            Case("EffectiveStrength_decays_linearly_to_half_at_half_lifetime", () =>
            {
                float lifetime = ClaimDecay.LifetimeTicks(0.5f);
                float got = ClaimDecay.EffectiveStrength(1f, (int)(lifetime / 2f), 0.5f);
                AssertClose(got, 0.5f, "linear decay curve: half the lifetime elapsed -> half strength left");
            });
            Case("EffectiveStrength_scales_with_initialStrength", () =>
            {
                float lifetime = ClaimDecay.LifetimeTicks(0.5f);
                float got = ClaimDecay.EffectiveStrength(0.4f, (int)(lifetime / 2f), 0.5f);
                AssertClose(got, 0.2f, "a weaker initial claim must decay proportionally, not to the same floor");
            });
            Case("EffectiveStrength_a_more_recognizable_claim_outlasts_a_less_recognizable_one", () =>
            {
                int ageTicks = (int)ClaimDecay.LifetimeTicks(0.5f); // fixed age
                float lowRecognizability = ClaimDecay.EffectiveStrength(1f, ageTicks, 0.0f);
                float highRecognizability = ClaimDecay.EffectiveStrength(1f, ageTicks, 1.0f);
                Assert(highRecognizability > lowRecognizability,
                    $"at the same age, higher recognizability must retain MORE strength (low={lowRecognizability}, high={highRecognizability})");
            });

            // ------------------------------------------------- ClaimantRef --------
            Case("Unclaimed_IsUnclaimed_is_true", () =>
                Assert(ClaimantRef.Unclaimed.IsUnclaimed, "Unclaimed.IsUnclaimed"));
            Case("OfPawn_is_not_Unclaimed", () =>
                Assert(!ClaimantRef.OfPawn(null).IsUnclaimed, "a Pawn claimant, even a null one, is not Unclaimed"));
            Case("OfCommons_is_not_Unclaimed", () =>
                Assert(!ClaimantRef.OfCommons(null).IsUnclaimed, "a Commons claimant, even a null one, is not Unclaimed"));
            Case("OfPawn_null_equals_OfPawn_null", () =>
                Assert(ClaimantRef.OfPawn(null).Equals(ClaimantRef.OfPawn(null)),
                    "same Kind, same (null) payload must be Equal - this IS the check TheftHauler/SalvageClaim's own gating relies on"));
            Case("OfCommons_null_equals_OfCommons_null", () =>
                Assert(ClaimantRef.OfCommons(null).Equals(ClaimantRef.OfCommons(null)),
                    "same Kind, same (null) payload must be Equal"));
            Case("Pawn_kind_never_equals_Commons_kind", () =>
                Assert(!ClaimantRef.OfPawn(null).Equals(ClaimantRef.OfCommons(null)),
                    "different Kind must never compare Equal, regardless of payload"));
            Case("Unclaimed_never_equals_a_claimed_ref", () =>
            {
                Assert(!ClaimantRef.Unclaimed.Equals(ClaimantRef.OfPawn(null)), "Unclaimed vs OfPawn(null)");
                Assert(!ClaimantRef.Unclaimed.Equals(ClaimantRef.OfCommons(null)), "Unclaimed vs OfCommons(null)");
            });
            Case("Unclaimed_GetHashCode_is_stable", () =>
                Assert(ClaimantRef.Unclaimed.GetHashCode() == ClaimantRef.Unclaimed.GetHashCode(),
                    "hash code must be stable across calls for the same value (dictionary-key safety)"));

            // ------------------------------------------------- ClaimEngine ---------
            // PickWinner() is the extracted transcription - see this file's own
            // header. All values below are REAL ClaimResolution/ClaimantRef.
            Case("PickWinner_higher_strength_wins_regardless_of_specificity", () =>
            {
                var weakPawn = new ClaimResolution(ClaimantRef.OfPawn(null), 0.2f, ClaimBasis.Situational, false, 100);
                var strongCommons = new ClaimResolution(ClaimantRef.OfCommons(null), 0.9f, ClaimBasis.Territorial, false, 50);
                var winner = PickWinner(new List<ClaimResolution> { weakPawn, strongCommons });
                Assert(winner.Claimant.Kind == ClaimantKind.Commons,
                    "0.9 Commons must beat 0.2 Pawn - strength is the FIRST sort key, not specificity");
            });
            Case("PickWinner_equal_strength_breaks_on_specificity_Pawn_beats_Commons", () =>
            {
                var pawn = new ClaimResolution(ClaimantRef.OfPawn(null), 0.5f, ClaimBasis.Situational, false, 100);
                var commons = new ClaimResolution(ClaimantRef.OfCommons(null), 0.5f, ClaimBasis.Territorial, false, 100);
                var winner = PickWinner(new List<ClaimResolution> { commons, pawn }); // order-independence check too
                Assert(winner.Claimant.Kind == ClaimantKind.Pawn,
                    "at equal strength, a Pawn (specificity 2) must beat Commons (specificity 1)");
            });
            Case("PickWinner_equal_strength_and_specificity_breaks_on_recency", () =>
            {
                var older = new ClaimResolution(ClaimantRef.OfCommons(null), 0.5f, ClaimBasis.Territorial, false, 100);
                var newer = new ClaimResolution(ClaimantRef.OfCommons(null), 0.5f, ClaimBasis.Territorial, false, 999);
                var winner = PickWinner(new List<ClaimResolution> { older, newer });
                Assert(winner.TimestampTicks == 999,
                    "at equal strength and specificity, the MORE RECENT timestamp must win");
            });

            Console.WriteLine($"\n{Pass.Count}/{Pass.Count + Fail.Count} passed");
            return Fail.Count == 0 ? 0 : 1;
        }
    }
}
