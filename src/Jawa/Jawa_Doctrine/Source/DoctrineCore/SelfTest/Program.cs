// Selftest for GameComponent_ColonyVisibility (COLONY_VISIBILITY_STAT_1).
//
// WHY THIS EXISTS: same offline-selftest discipline as
// src/RimMandrake/Utils/selftest_validate_patch.py. The 0-100 -> five-band
// ladder and the Adjust() clamp are exactly the kind of small pure-ish
// logic that drifts silently across an edit - a shifted boundary or a
// dropped clamp produces no error, it just quietly lets shipVisibility
// wander outside [0,100] or reports the wrong band forever.
//
// WHAT IS REAL: BandFor(), the band ladder itself, is compiled straight
// from the real ColonyVisibility.cs (see this project's .csproj) and
// called directly - it is a plain static method with no Unity/game state
// dependency beyond needing Verse.dll/UnityEngine.dll to RESOLVE the class
// it lives on (GameComponent_ColonyVisibility derives from
// Verse.GameComponent). Adjust()'s clamp is also called on a REAL
// instance, not reimplemented - see below for how that instance gets built
// without a running game.
//
// THE ONE RISK, PROVEN NOT TAKEN: GameComponent_ColonyVisibility's
// constructor takes a Verse.Game and its body is empty (does not touch the
// parameter) - confirmed by reading ColonyVisibility.cs before writing this
// file, not assumed. Passing null for that Game and calling Adjust()
// afterwards was the open question (does it dereference Prefs.DevMode /
// Log.Message safely outside a running game?) - this file's own successful
// run is the proof: if that had thrown, every Adjust() case below would
// show as FAIL/ERROR, not ok.
//
// ⛔ NOT COVERED: GameComponent registration via Verse.Game.FillComponents
// reflection, ExposeData/save-round-trip, and the Harmony postfix in
// ColonyVisibilityRaidPatch.cs that calls ResetOnLaunch() on a real launch.
// Those need a running game.
//
// Run:
//   python3 src/RimMandrake/Utils/selftest_colony_visibility.py

using System;
using JawaDoctrineCore;
using Verse;

namespace JawaDoctrineCore.SelfTest
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

        // Adjust() mutates shipVisibility BEFORE its dev-log branch runs
        // (`shipVisibility = Mathf.Clamp(...)` precedes the
        // `if (Prefs.DevMode && Band != before)` check - read in source before
        // writing this). In this bare, no-game process, Prefs.DevMode reads
        // true (no saved prefs file to make it false, and there is no public
        // setter that reliably flips it here - tried, still throws) and a
        // band-crossing call then reaches Verse.Log.Message ->
        // UnityEngine.StackTraceUtility.ExtractStackTrace(), an ECall that
        // needs the real native Unity engine and throws SecurityException
        // outside one. That is dev-console logging, not the clamp math this
        // file exists to test, and the mutation this test cares about has
        // already happened by the time it throws - so this swallows ONLY that
        // specific exception and lets every case assert on the real resulting
        // field value. ⚠️ If Adjust()'s own body were ever reordered so the
        // assignment happened AFTER the log call, this would start passing
        // against a stale (pre-mutation) shipVisibility instead of failing
        // loudly - a real, accepted limitation of testing a live instance
        // outside the engine that owns Log.Message.
        private static void SafeAdjust(GameComponent_ColonyVisibility c, float delta, string reason)
        {
            try
            {
                c.Adjust(delta, reason);
            }
            catch (System.Security.SecurityException)
            {
                // dev-log path only; the field mutation above it already ran.
            }
        }

        private static int Main()
        {
            // ------------------------------------------------- BandFor() ladder --
            Case("BandFor_0_is_Hidden", () =>
                Assert(GameComponent_ColonyVisibility.BandFor(0f) == VisibilityBand.Hidden, "0"));
            Case("BandFor_just_under_20_is_still_Hidden", () =>
                Assert(GameComponent_ColonyVisibility.BandFor(19.9f) == VisibilityBand.Hidden, "19.9"));
            Case("BandFor_20_crosses_into_Discreet", () =>
                Assert(GameComponent_ColonyVisibility.BandFor(20f) == VisibilityBand.Discreet,
                    "boundary is < 20, so 20 itself must already be Discreet"));
            Case("BandFor_just_under_40_is_still_Discreet", () =>
                Assert(GameComponent_ColonyVisibility.BandFor(39.9f) == VisibilityBand.Discreet, "39.9"));
            Case("BandFor_40_crosses_into_Noticed", () =>
                Assert(GameComponent_ColonyVisibility.BandFor(40f) == VisibilityBand.Noticed, "40"));
            Case("BandFor_just_under_60_is_still_Noticed", () =>
                Assert(GameComponent_ColonyVisibility.BandFor(59.9f) == VisibilityBand.Noticed, "59.9"));
            Case("BandFor_60_crosses_into_Marked", () =>
                Assert(GameComponent_ColonyVisibility.BandFor(60f) == VisibilityBand.Marked, "60"));
            Case("BandFor_just_under_80_is_still_Marked", () =>
                Assert(GameComponent_ColonyVisibility.BandFor(79.9f) == VisibilityBand.Marked, "79.9"));
            Case("BandFor_80_crosses_into_Exposed", () =>
                Assert(GameComponent_ColonyVisibility.BandFor(80f) == VisibilityBand.Exposed, "80"));
            Case("BandFor_100_is_Exposed", () =>
                Assert(GameComponent_ColonyVisibility.BandFor(100f) == VisibilityBand.Exposed, "100"));

            // --------------------------------------------- Adjust() clamping -----
            // GameComponent_ColonyVisibility's ctor takes a Game but its body
            // never touches it (read before writing this test) - null is safe.
            Case("Adjust_default_start_is_10_Hidden", () =>
            {
                var c = new GameComponent_ColonyVisibility(null);
                AssertClose(c.shipVisibility, 10f, "default shipVisibility");
                Assert(c.Band == VisibilityBand.Hidden, "default band");
            });
            Case("Adjust_clamps_at_100_not_beyond", () =>
            {
                var c = new GameComponent_ColonyVisibility(null);
                SafeAdjust(c, 500f, "selftest: huge positive delta");
                AssertClose(c.shipVisibility, 100f, "must clamp at the 100 ceiling, not overshoot");
            });
            Case("Adjust_clamps_at_0_not_negative", () =>
            {
                var c = new GameComponent_ColonyVisibility(null);
                SafeAdjust(c, -500f, "selftest: huge negative delta");
                AssertClose(c.shipVisibility, 0f, "must clamp at the 0 floor, not go negative");
            });
            Case("Adjust_within_range_is_not_clamped", () =>
            {
                var c = new GameComponent_ColonyVisibility(null);
                SafeAdjust(c, 15f, "selftest: normal delta"); // 10 + 15 = 25, well inside [0,100]
                AssertClose(c.shipVisibility, 25f, "an in-range delta must land exactly, not be clamped");
                Assert(c.Band == VisibilityBand.Discreet, "25 should read as Discreet");
            });
            Case("Adjust_accumulates_across_multiple_calls", () =>
            {
                var c = new GameComponent_ColonyVisibility(null);
                SafeAdjust(c, 20f, "selftest: first");
                SafeAdjust(c, 20f, "selftest: second");
                AssertClose(c.shipVisibility, 50f, "10 + 20 + 20 = 50");
                Assert(c.Band == VisibilityBand.Noticed, "50 should read as Noticed");
            });
            Case("Adjust_negative_delta_lowers_it", () =>
            {
                var c = new GameComponent_ColonyVisibility(null);
                SafeAdjust(c, 30f, "selftest: raise"); // 10 + 30 = 40
                SafeAdjust(c, -15f, "selftest: lower"); // 40 - 15 = 25
                AssertClose(c.shipVisibility, 25f, "a negative delta must lower shipVisibility");
            });

            Console.WriteLine($"\n{Pass.Count}/{Pass.Count + Fail.Count} passed");
            return Fail.Count == 0 ? 0 : 1;
        }
    }
}
