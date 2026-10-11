// Stage-keyed droid commentary (RUST_CATHEDRAL_MECHANICS_1 slice 2026-10-11, the hook CATHEDRAL_STAGE_COMMENTARY_POOLS_1
// fills): RM_AttitudeKernel.CommentaryEntryIndex and CommentaryKeyErrors, the production code the map component and the
// def's ConfigErrors call. Fixed cases first (each would catch one specific wrong implementation), then random lists
// checked against an independent reference written from the rule, not from the kernel.
using System;
using System.Collections.Generic;

namespace RimMandrake.RustCathedral.Hum.SelfTest
{
    internal static class CommentaryPick
    {
        const int Any = RM_AttitudeKernel.AnyStage;

        static int Pick(int[] b, int[] s, int band, int stage, bool keyed)
        {
            return RM_AttitudeKernel.CommentaryEntryIndex(b, s, band, stage, keyed);
        }

        // Reference: exact (band, stage) first-in-order when keyed; else first (band, Any); else -1.
        static int Reference(int[] b, int[] s, int band, int stage, bool keyed)
        {
            if (keyed)
            {
                for (int i = 0; i < b.Length; i++) if (b[i] == band && s[i] == stage && s[i] != Any) return i;
            }
            for (int i = 0; i < b.Length; i++) if (b[i] == band && s[i] == Any) return i;
            return -1;
        }

        public static List<string> Run(int n, int seed)
        {
            var fails = new List<string>();
            void Expect(string what, int got, int want) { AttitudeFuzz.Cases++; if (got != want) fails.Add($"fixed {what}: got {got}, want {want}"); }

            // The shipped shape: band-only entries (stage -1) for bands 1..4 -- must behave exactly as before the hook.
            int[] b0 = { 1, 2, 3, 4 }, s0 = { Any, Any, Any, Any };
            for (int band = 0; band <= 4; band++)
                for (int stage = 0; stage <= 3; stage++)
                {
                    Expect($"legacy band {band} stage {stage}", Pick(b0, s0, band, stage, true), band == 0 ? -1 : band - 1);
                    Expect($"legacy off band {band} stage {stage}", Pick(b0, s0, band, stage, false), band == 0 ? -1 : band - 1);
                }

            // Exact beats fallback even when the fallback is listed first (an "first band match" impl fails this).
            int[] b1 = { 2, 2, 2 }, s1 = { Any, 1, 0 };
            Expect("exact after fallback", Pick(b1, s1, 2, 1, true), 1);
            Expect("exact stage 0 is not Any", Pick(b1, s1, 2, 0, true), 2);
            Expect("unkeyed stage -> fallback", Pick(b1, s1, 2, 3, true), 0);
            Expect("setting off ignores exact", Pick(b1, s1, 2, 1, false), 0);
            // No fallback: an unmatched stage is SILENCE, never another stage's pool.
            int[] b2 = { 3 }, s2 = { 2 };
            Expect("no fallback, other stage", Pick(b2, s2, 3, 1, true), -1);
            Expect("no fallback, setting off", Pick(b2, s2, 3, 2, false), -1);
            Expect("other band never speaks", Pick(b2, s2, 2, 2, true), -1);
            // Stage -1 asked for (map with no attitude def) only ever gets Any entries.
            Expect("asked stage -1", Pick(b1, s1, 2, Any, true), 0);

            // Key errors.
            void ExpectErr(string what, int[] b, int[] s, int bandCount, int want)
            {
                AttitudeFuzz.Cases++;
                int got = RM_AttitudeKernel.CommentaryKeyErrors(b, s, bandCount).Count;
                if (got != want) fails.Add($"fixed keyerr {what}: got {got} errors, want {want}");
            }
            ExpectErr("shipped clean", b0, s0, 5, 0);
            ExpectErr("mixed clean", b1, s1, 5, 0);
            ExpectErr("duplicate any", new[] { 1, 1 }, new[] { Any, Any }, 5, 1);
            ExpectErr("duplicate stage", new[] { 1, 2, 1 }, new[] { 0, 0, 0 }, 5, 1);
            ExpectErr("band out of range", new[] { 5, -1 }, new[] { Any, Any }, 5, 2);
            ExpectErr("stage below any", new[] { 1 }, new[] { -2 }, 5, 1);
            ExpectErr("same band different stage ok", new[] { 4, 4, 4 }, new[] { Any, 0, 1 }, 5, 0);

            // Random lists against the reference.
            var r = new Random(seed);
            for (int c = 0; c < n; c++)
            {
                int len = r.Next(0, 12);
                var b = new int[len]; var s = new int[len];
                for (int i = 0; i < len; i++) { b[i] = r.Next(0, 6); s[i] = r.Next(-1, 4); }
                int band = r.Next(-1, 7), stage = r.Next(-1, 5); bool keyed = r.Next(2) == 0;
                AttitudeFuzz.Cases++; AttitudeFuzz.Steps++;
                int got = Pick(b, s, band, stage, keyed), want = Reference(b, s, band, stage, keyed);
                if (got != want)
                {
                    fails.Add($"random case {c}: band {band} stage {stage} keyed {keyed} bands [{string.Join(",", b)}] stages [{string.Join(",", s)}] got {got} want {want}");
                    if (fails.Count > 10) break;
                }
                if (got >= 0 && (b[got] != band || (s[got] != Any && (!keyed || s[got] != stage))))
                    fails.Add($"random case {c}: picked entry {got} does not belong to band {band} stage {stage} keyed {keyed}");
            }
            return fails;
        }
    }
}
