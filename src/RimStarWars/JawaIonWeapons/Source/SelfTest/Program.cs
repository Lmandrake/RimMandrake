// Selftest for StatPart_InverseBodySize (OTHER_STUN_WEAPONS_SURVEY_1 /
// ION_STUN_IGNORES_BODY_SIZE_1). Verified LIVE this session (bridge test):
// Rat bodySize 0.2 / Human 1.0 / Behemoth 32.0 -> 25x / 1024x stun-severity
// scaling. This file locks that exact relationship in offline so it cannot
// regress silently between bridge sessions.
//
// WHY THIS EXISTS: same offline-selftest discipline as
// src/RimMandrake/Utils/selftest_validate_patch.py.
//
// WHAT IS REAL vs MODELLED, AND WHY:
//   The not-a-Pawn guard clause (`req.Thing is Pawn pawn && pawn.BodySize
//   > 0f`) is tested by calling the REAL TransformValue()/ExplanationPart()
//   (compiled straight from StatPart_InverseBodySize.cs - see the .csproj)
//   with a default(StatRequest), whose Thing is null.
//
//   The bodySize transform itself is the REAL production kernel
//   (Kernel/RSW_IonBuildupKernel.cs, InverseSizeValue; TransformValue calls it
//   with the live Pawn's BodySize), called at the shipped default exponent 2.
//   Constructing a Verse.Pawn with a controlled BodySize offline is not viable
//   (BodySize is computed from RaceProps/genes/body type), so only the engine's
//   OWN separate multiply stays modelled: EngineOwnInverseBodySizeMultiply()
//   below reproduces `num *= 1f / pawn.BodySize;` (Pawn_HealthTracker.
//   PostApplyDamage, confirmed by source read). The squared relationship
//   locked in here is (our part's 1 / bodySize ^ (exponent - 1)) times (the
//   engine's 1 / bodySize).
//   The seeded fuzz of the same kernel (selftest_jawaionweapons_fuzz.py)
//   checks that composition for every exponent and size.
//   ⚠️ If the engine's own ByInvBodySize multiply ever changed shape, the
//   modelled half of this test keeps passing against the old formula unless a
//   human updates it; it still locks in the 25x / 1024x measured live.
//
// Run:
//   python3 src/RimMandrake/Utils/selftest_stun_scaling.py

using System;
using RimMandrake.StarWars.JawaIonWeapons;
using RimWorld;
using Verse;

namespace RimMandrake.StarWars.JawaIonWeapons.SelfTest
{
    internal static class Program
    {
        private static readonly System.Collections.Generic.List<string> Pass = new();
        private static readonly System.Collections.Generic.List<(string name, string msg)> Fail = new();

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

        private static void AssertClose(float got, float want, string msg, float eps = 0.0001f)
        {
            if (Math.Abs(got - want) > eps)
                throw new Exception($"{msg}: got {got}, want {want}");
        }

        // ---- the REAL transform, now a pure kernel (Kernel/RSW_IonBuildupKernel.cs) ------
        // The old transcription here (`1f / bodySize`) was the pre-exponent formula and had drifted from the
        // shipped StatPart (1 / bodySize ^ (exponent - 1)); it passed only because it tested itself. It now calls
        // the production kernel at the shipped default exponent 2, so the 25x / 1024x locks bind the real code.
        private static float ExtractedTransform(float bodySize, float valIn)
        {
            return RSW_IonBuildupKernel.InverseSizeValue(true, true, bodySize, 2f, valIn);
        }

        // The engine's own ByInvBodySize multiply, quoted verbatim in the real
        // source's class doc comment - NOT this StatPart's code, the vanilla
        // Pawn_HealthTracker.PostApplyDamage step it composes with.
        private static float EngineOwnInverseBodySizeMultiply(float bodySize)
        {
            return 1f / bodySize;
        }

        private static float ComposedSeverityMultiplier(float bodySize)
        {
            float ourPart = ExtractedTransform(bodySize, 1f);
            float engineOwn = EngineOwnInverseBodySizeMultiply(bodySize);
            return ourPart * engineOwn;
        }

        private static int Main()
        {
            // -------------------------------------- real not-a-Pawn guard clause --
            Case("TransformValue_leaves_val_unchanged_when_Thing_is_not_a_Pawn", () =>
            {
                var part = new StatPart_InverseBodySize();
                var req = default(StatRequest); // Thing defaults to null
                float val = 7f;
                part.TransformValue(req, ref val);
                AssertClose(val, 7f, "a non-Pawn StatRequest must leave val untouched, not divide by a phantom body size");
            });
            Case("ExplanationPart_returns_null_when_Thing_is_not_a_Pawn", () =>
            {
                var part = new StatPart_InverseBodySize();
                var req = default(StatRequest);
                Assert(part.ExplanationPart(req) == null, "no Pawn means no explanation line to show");
            });

            // ------------------------------------- extracted transform, per body --
            Case("ExtractedTransform_is_the_reciprocal_of_bodySize", () =>
            {
                AssertClose(ExtractedTransform(0.2f, 1f), 5f, "Rat (0.2) -> 1/0.2");
                AssertClose(ExtractedTransform(1.0f, 1f), 1f, "Human (1.0) -> 1/1.0");
                AssertClose(ExtractedTransform(32.0f, 1f), 0.03125f, "Behemoth (32.0) -> 1/32.0");
                AssertClose(RSW_IonBuildupKernel.InverseSizeValue(true, true, 4f, 3f, 1f), 1f / 16f, "exponent 3 -> 1 / size^2, composing with the engine's 1/size to size^-3");
            });
            Case("ExtractedTransform_guard_leaves_val_unchanged_at_zero_bodySize", () =>
                AssertClose(ExtractedTransform(0f, 42f), 42f,
                    "bodySize <= 0 must not divide by zero - the real guard is bodySize > 0f"));

            // -------------------------- 🔴 the locked-in regression: 25x / 1024x --
            Case("ComposedSeverityMultiplier_Rat_is_25x_Human", () =>
            {
                float rat = ComposedSeverityMultiplier(0.2f);
                float human = ComposedSeverityMultiplier(1.0f);
                AssertClose(rat / human, 25f, "Rat (bodySize 0.2) must scale to exactly 25x Human's stun severity — the exact ratio verified live this session");
            });
            Case("ComposedSeverityMultiplier_Human_is_1024x_Behemoth", () =>
            {
                float human = ComposedSeverityMultiplier(1.0f);
                float behemoth = ComposedSeverityMultiplier(32.0f);
                AssertClose(human / behemoth, 1024f, "Human must scale to exactly 1024x Behemoth's (bodySize 32) stun severity — the exact ratio verified live this session");
            });
            Case("ComposedSeverityMultiplier_absolute_values_match_the_live_bridge_test", () =>
            {
                // The bridge test's own absolute numbers (Rat 250 / Human 10 /
                // Behemoth ~0.0098) imply a base severity of 10 for Human times
                // this composed multiplier — reproduced here as a cross-check,
                // not a second independent measurement.
                const float humanBaseSeverity = 10f;
                AssertClose(humanBaseSeverity * ComposedSeverityMultiplier(0.2f), 250f, "Rat absolute severity");
                AssertClose(humanBaseSeverity * ComposedSeverityMultiplier(1.0f), 10f, "Human absolute severity");
                AssertClose(humanBaseSeverity * ComposedSeverityMultiplier(32.0f), 0.009765625f, "Behemoth absolute severity", eps: 0.0001f);
            });

            Console.WriteLine($"\n{Pass.Count}/{Pass.Count + Fail.Count} passed");
            return Fail.Count == 0 ? 0 : 1;
        }
    }
}
