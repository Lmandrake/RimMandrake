// Selftest for GameComponent_ColonyVisibility (COLONY_VISIBILITY_BUILD_1,
// rehomed from the old COLONY_VISIBILITY_STAT_1 build - see this project's
// own .csproj header for the relocation note).
//
// WHY THIS EXISTS: same offline-selftest discipline as
// src/RimMandrake/Utils/selftest_validate_patch.py. The 0-100 -> five-band
// ladder and the Adjust()/ResetOnLaunch() clamps are exactly the kind of
// small pure-ish logic that drifts silently across an edit - a shifted
// boundary or a dropped clamp produces no error, it just quietly lets
// shipVisibility wander outside [0,100] or reports the wrong band forever.
//
// WHAT IS REAL: BandFor(), the band ladder itself, is compiled straight
// from the real GameComponent_ColonyVisibility.cs (see this project's
// .csproj) and called directly - it is a plain static method with no
// Unity/game state dependency beyond needing Verse.dll/UnityEngine.dll to
// RESOLVE the class it lives on (GameComponent_ColonyVisibility derives
// from Verse.GameComponent). Adjust()'s and ResetOnLaunch()'s clamps are
// also called on a REAL instance, not reimplemented - see below for how
// that instance gets built without a running game.
//
// THE ONE RISK, PROVEN NOT TAKEN: GameComponent_ColonyVisibility's
// constructor takes a Verse.Game and its body is empty (does not touch the
// parameter) - confirmed by reading the real file before writing this one,
// not assumed. Passing null for that Game and calling Adjust()/
// ResetOnLaunch() afterwards was the open question (does it dereference
// Prefs.DevMode / Log.Message safely outside a running game?) - this
// file's own successful run is the proof: if that had thrown outside
// SafeAdjust/SafeResetOnLaunch's own narrow catch, every case below would
// show as FAIL/ERROR, not ok.
//
// SeasonsAway()/DecayedTileVisibility() (the tile-memory decay math, owner
// card "halved per season away") ARE covered below - extracted out of
// ApplyTileMemoryOnArrival specifically so this file could test them without
// a running game, same pattern selftest_stun_scaling.py's Program.cs uses
// for StatPart_InverseBodySize's transform.
//
// ⛔ STILL NOT COVERED: GameComponent registration via
// Verse.Game.FillComponents reflection, ExposeData/save-round-trip, the
// Harmony postfixes in ColonyVisibilityRaidPatch.cs (including
// RecordTileDeparture()/ApplyTileMemoryOnArrival() themselves, which call
// Find.TickManager.TicksGame - genuinely null with no running game), and
// VisibilityToThreatCurve (lives in ColonyVisibilityRaidPatch.cs, which pulls
// in HarmonyLib/RimWorld.Planet types this SelfTest project does not
// reference - a separate, larger increment, not attempted this pass). All of
// these need a running game or a deliberate extraction this pass did not do.
//
// Run:
//   python3 src/RimMandrake/Utils/selftest_colony_visibility.py

using System;
using RimMandrake.Visibility;
using Verse;

namespace RimMandrake.Visibility.SelfTest
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
        // true (no saved prefs file to make it false) and a band-crossing call
        // then reaches Verse.Log.Message -> an ECall that needs the real
        // native Unity engine and throws SecurityException outside one. That
        // is dev-console logging, not the clamp math this file exists to
        // test, and the mutation this test cares about has already happened
        // by the time it throws - so this swallows ONLY that specific
        // exception and lets every case assert on the real resulting field
        // value.
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

        // ResetOnLaunch() has the SAME shape as Adjust(): the clamp/assignment
        // runs first, `if (Prefs.DevMode) Log.Message(...)` runs after - so
        // the same narrow catch applies for the same reason.
        private static void SafeResetOnLaunch(GameComponent_ColonyVisibility c)
        {
            try
            {
                c.ResetOnLaunch();
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

            // ----------------------------------------- ResetOnLaunch() clamping --
            // shipVisibility = Clamp(shipVisibility * 0.15, 5, 15) - new coverage,
            // this method did not exist when the original DoctrineCore-era test
            // was written.
            Case("ResetOnLaunch_floors_at_5_from_a_low_start", () =>
            {
                var c = new GameComponent_ColonyVisibility(null); // starts at 10
                SafeResetOnLaunch(c); // 10 * 0.15 = 1.5, clamped up to the 5 floor
                AssertClose(c.shipVisibility, 5f, "10*0.15=1.5 must clamp up to the 5 floor");
            });
            Case("ResetOnLaunch_ceilings_at_15_from_a_high_start", () =>
            {
                var c = new GameComponent_ColonyVisibility(null);
                SafeAdjust(c, 90f, "selftest: raise to near-max"); // 10+90=100
                SafeResetOnLaunch(c); // 100 * 0.15 = 15, exactly the ceiling
                AssertClose(c.shipVisibility, 15f, "100*0.15=15 must land exactly at the ceiling, not clamp below it");
            });
            Case("ResetOnLaunch_scales_within_the_5_to_15_band", () =>
            {
                var c = new GameComponent_ColonyVisibility(null);
                SafeAdjust(c, 30f, "selftest: raise"); // 10+30=40
                SafeResetOnLaunch(c); // 40 * 0.15 = 6, inside [5,15], not clamped
                AssertClose(c.shipVisibility, 6f, "40*0.15=6 must land exactly, no clamp applies inside the band");
            });

            // ------------------------------------ tile-memory decay math -----
            // GenDate.TicksPerSeason = 900_000 (Verse constant, not guessed -
            // matches the owner card's "halved per season away" wording and
            // GameComponent_ColonyVisibility.cs's own doc comment).
            const int ticksPerSeason = 900_000;

            Case("SeasonsAway_zero_ticks_is_zero_seasons", () =>
                AssertClose(GameComponent_ColonyVisibility.SeasonsAway(0), 0f, "0 ticks"));
            Case("SeasonsAway_one_season_of_ticks_is_1", () =>
                AssertClose(GameComponent_ColonyVisibility.SeasonsAway(ticksPerSeason), 1f, "900000 ticks"));
            Case("SeasonsAway_negative_ticks_floors_at_zero", () =>
                AssertClose(GameComponent_ColonyVisibility.SeasonsAway(-1000), 0f,
                    "a negative elapsed time must not produce negative seasons"));

            Case("DecayedTileVisibility_zero_elapsed_is_unchanged", () =>
                AssertClose(GameComponent_ColonyVisibility.DecayedTileVisibility(80f, 0), 80f,
                    "no time passed, no decay"));
            Case("DecayedTileVisibility_one_season_is_halved", () =>
                AssertClose(GameComponent_ColonyVisibility.DecayedTileVisibility(80f, ticksPerSeason), 40f,
                    "owner card: halved per season away"));
            Case("DecayedTileVisibility_two_seasons_is_quartered", () =>
                AssertClose(GameComponent_ColonyVisibility.DecayedTileVisibility(80f, ticksPerSeason * 2), 20f,
                    "two half-lives"));
            Case("DecayedTileVisibility_half_season_is_between_full_and_half", () =>
                AssertClose(GameComponent_ColonyVisibility.DecayedTileVisibility(100f, ticksPerSeason / 2),
                    100f * (float)Math.Sqrt(0.5), "0.5^0.5 at the half-season mark", eps: 0.01f));
            Case("DecayedTileVisibility_negative_elapsed_is_unchanged", () =>
                AssertClose(GameComponent_ColonyVisibility.DecayedTileVisibility(50f, -1000), 50f,
                    "should never happen in practice, but must not decay backwards"));
            Case("DecayedTileVisibility_zero_departure_value_stays_zero", () =>
                AssertClose(GameComponent_ColonyVisibility.DecayedTileVisibility(0f, ticksPerSeason), 0f,
                    "a tile left at 0 has nothing to decay"));

            Console.WriteLine($"\n{Pass.Count}/{Pass.Count + Fail.Count} passed");
            return Fail.Count == 0 ? 0 : 1;
        }
    }
}
