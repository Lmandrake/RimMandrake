// RIMMANDRAKE_SINK_GEYSER_INTO_PIT_BUBBLING_HOT_TUB (owner 2026-11-12: "Digging a pit on a Geyser allows the Geyser to
// descend to the bottom of the pit ... generates distinctive bubbles where the geyser is. When pawns are near those bubbles,
// they will treat it like a hot tub"; by card the same evening: water plus harmless liquids bathe, each with its own cost;
// a generator caps a dry sunk geyser; vanilla's hot-spring memory). Spec: design/specs/geyser_in_pit_hot_tub_2026-11-12.md
// section 4.1 O1. Offline: the pure verdicts in RM_GeyserTubMath. Each case has a can-fail.
// NOT proven here: anything drawn, any job given, any hediff added in game (spec 4.2 L1-L8, live rows owed).
using System;
using RimMandrake.FlowWorks;

namespace RimMandrake.FlowWorks.SelfTest
{
    internal static class GeyserTubChecks
    {
        private static void Assert(bool ok, string msg)
        {
            if (!ok) throw new Exception(msg);
        }

        public static void Run(Action<string, Action> Case)
        {
            Case("GeyserTub_seat_is_the_shallowest_cell", () =>
            {
                Assert(RM_GeyserTubMath.SeatNotches(new[] { 4, 4, 4, 4 }) == 4, "four cells at 2 m seat it at 2 m");
                Assert(RM_GeyserTubMath.SeatNotches(new[] { 4, 4, 4, 2 }) == 2, "can-fail: the shallowest cell holds it (a deepest-cell mutant floats it)");
                Assert(RM_GeyserTubMath.SeatNotches(new[] { 0, 4, 4, 4 }) == 0, "can-fail: one undug corner keeps it at the surface");
                Assert(RM_GeyserTubMath.SeatNotches(new int[0]) == 0, "no cells: surface");
                Assert(RM_GeyserTubMath.SeatNotches(null) == 0, "null: surface");
                Assert(RM_GeyserTubMath.SeatNotches(new[] { -1, 4, 4, 4 }) == 0, "can-fail: a negative depth reads as the surface");
                Assert(RM_GeyserTubMath.SeatNotches(new[] { 16, 16, 16, 16 }) == 16, "an 8 m pit seats it at 8 m");
            });
            Case("GeyserTub_covered_once_the_vent_mouth_is_under", () =>
            {
                Assert(!RM_GeyserTubMath.Covered(0f), "dry");
                Assert(!RM_GeyserTubMath.Covered(0.39f), "can-fail: under the mound's top it still puffs");
                Assert(RM_GeyserTubMath.Covered(0.41f), "can-fail: over the mound it bubbles");
                Assert(RM_GeyserTubMath.Covered(2f), "deep");
            });
            Case("GeyserTub_pool_needs_bathable_covered_uncapped", () =>
            {
                Assert(RM_GeyserTubMath.PoolSafe(true, true, true, false), "a bathable liquid over an open vent is a pool");
                Assert(!RM_GeyserTubMath.PoolSafe(true, false, true, false), "can-fail: a liquid that is not bathable is no pool");
                Assert(!RM_GeyserTubMath.PoolSafe(true, true, false, false), "can-fail: not covered is no pool");
                Assert(!RM_GeyserTubMath.PoolSafe(true, true, true, true), "can-fail: a capped vent is no pool");
                Assert(!RM_GeyserTubMath.PoolSafe(false, true, true, false), "can-fail: no fluid is no pool");
            });
            Case("GeyserTub_reach_from_the_footprint_centre", () =>
            {
                Assert(RM_GeyserTubMath.InReach(0.5f, 0.5f, 2.5f), "a footprint cell is in reach");
                Assert(!RM_GeyserTubMath.InReach(2.5f, 0.5f, 2.5f), "can-fail: past 2.5 is out (exclusive)");
            });
            Case("GeyserTub_afterglow_lasts_a_day_and_a_quarter", () =>
            {
                Assert(Math.Abs(RM_GeyserTubMath.AfterglowDays(0.5f, 0.4f) - 1.25f) < 1e-4f, "can-fail: 0.5 falling 0.4 a day is 1.25 days");
            });
            Case("GeyserTub_plume_rates", () =>
            {
                foreach (int tpt in new[] { 60, 120, 360, 480 })
                {
                    float spray = RM_GeyserTubMath.PlumeRate(true, tpt, 1f), between = RM_GeyserTubMath.PlumeRate(false, tpt, 1f);
                    Assert(spray > between && between > 0f, "can-fail: spraying beats between, and between never stops (" + tpt + ")");
                }
                Assert(RM_GeyserTubMath.PlumeRate(true, 360, 1f) < RM_GeyserTubMath.PlumeRate(true, 60, 1f), "can-fail: thick throws fewer");
                Assert(RM_GeyserTubMath.PlumeScaleMin(360) > RM_GeyserTubMath.PlumeScaleMin(60), "can-fail: thick throws bigger");
                Assert(RM_GeyserTubMath.PlumeScaleMin(60) >= 1.5f && RM_GeyserTubMath.PlumeScaleMax(360) <= 3f, "sizes 1.5..3 (ambient 0.8..1.8)");
                Assert(RM_GeyserTubMath.PlumeRate(true, 60, 0f) == 0f, "can-fail: density x0 throws none");
            });
            Case("GeyserTub_bubbles_this_tick_average_the_rate", () =>
            {
                int n = 0;
                for (int i = 0; i < 600; i++) n += RM_GeyserTubMath.BubblesThisTick(6f, (i % 60) / 60f);
                Assert(n == 60, "can-fail: 6 a second over 10 s is 60 (got " + n + ")");
                Assert(RM_GeyserTubMath.BubblesThisTick(0f, 0.99f) == 0, "can-fail: rate 0 is none");
            });
            Case("GeyserTub_sink_stays_inside_the_pit", () =>
            {
                Assert(Math.Abs(RM_GeyserTubMath.SeatSink(4, 0.3f, 5) - 1.2f) < 1e-4f, "room to spare: the pawn sink");
                Assert(RM_GeyserTubMath.SeatSink(4, 0.3f, 0) == 0f, "can-fail: a pit no wider than the vent holds it at its cells");
                Assert(Math.Abs(RM_GeyserTubMath.SeatSink(4, 0.3f, 1) - 1f) < 1e-4f, "can-fail: one row of room caps it at one cell");
                Assert(RM_GeyserTubMath.SeatSink(0, 0.3f, 5) == 0f, "surface: no sink");
            });
            Case("GeyserTub_bath_groups_follow_their_settings", () =>
            {
                Assert(RM_GeyserTubMath.GroupAllowed(RM_GeyserTubMath.BathGroup.Water, false, false, false, false), "water always bathes");
                Assert(!RM_GeyserTubMath.GroupAllowed(RM_GeyserTubMath.BathGroup.None, true, true, true, true), "can-fail: None never bathes");
                Assert(RM_GeyserTubMath.GroupAllowed(RM_GeyserTubMath.BathGroup.Tar, true, false, false, false)
                    && !RM_GeyserTubMath.GroupAllowed(RM_GeyserTubMath.BathGroup.Tar, false, true, true, true), "can-fail: tar follows its own switch");
                Assert(RM_GeyserTubMath.GroupAllowed(RM_GeyserTubMath.BathGroup.Oil, false, true, false, false)
                    && !RM_GeyserTubMath.GroupAllowed(RM_GeyserTubMath.BathGroup.Oil, true, false, true, true), "can-fail: oil follows its own switch");
                Assert(RM_GeyserTubMath.GroupAllowed(RM_GeyserTubMath.BathGroup.Blood, false, false, true, false)
                    && !RM_GeyserTubMath.GroupAllowed(RM_GeyserTubMath.BathGroup.Blood, true, true, false, true), "can-fail: blood follows its own switch");
                Assert(RM_GeyserTubMath.GroupAllowed(RM_GeyserTubMath.BathGroup.Slime, false, false, false, true)
                    && !RM_GeyserTubMath.GroupAllowed(RM_GeyserTubMath.BathGroup.Slime, true, true, true, false), "can-fail: slime follows its own switch");
            });
        }
    }
}
