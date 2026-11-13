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
            Case("GeyserTub_heat_only_through_the_water_over_the_vent", () =>
            {
                // RIMMANDRAKE_RESTRICT_HEAT_TO_GEYSER_BENEATH_PIT_WATER_ONLY: a 10 x 6 window; pit A is x 0..3 (all z), pit B is
                // x 5..9 (all z); column x 4 is undug bank. The vent's 2x2 sits at x 1..2, z 2..3.
                const int W = 10, H = 6;
                bool[] Pits(bool a, bool b)
                {
                    var w = new bool[W * H];
                    for (int z = 0; z < H; z++)
                        for (int x = 0; x < W; x++)
                            w[z * W + x] = (x <= 3 && a) || (x >= 5 && b);
                    return w;
                }
                int[] vent = { 2 * W + 1, 2 * W + 2, 3 * W + 1, 3 * W + 2 };
                int Count(bool[] r, int x0, int x1) { int n = 0; for (int z = 0; z < H; z++) for (int x = x0; x <= x1; x++) if (r[z * W + x]) n++; return n; }
                bool[] both = RM_GeyserTubMath.PoolRegion(W, H, Pits(true, true), vent);
                Assert(Count(both, 0, 3) == 24, "the vent's own pit is heated, every square of it (got " + Count(both, 0, 3) + ")");
                Assert(Count(both, 5, 9) == 0, "can-fail: the next pit across one square of bank is never heated, however near (got " + Count(both, 5, 9) + ")");
                Assert(!both[2 * W + 4], "the bank itself is not heated");
                // the owner's picture (image 6): the vent stands dry beside a full pit
                int[] ventOnBank = { 2 * W + 4, 3 * W + 4 };
                bool[] dryVent = RM_GeyserTubMath.PoolRegion(W, H, Pits(true, true), ventOnBank);
                Assert(Count(dryVent, 0, 9) == 0, "can-fail: a vent under no water heats nothing, though water is beside it");
                bool[] emptyPit = RM_GeyserTubMath.PoolRegion(W, H, Pits(false, true), vent);
                Assert(Count(emptyPit, 0, 9) == 0, "can-fail: the vent's pit dry, the wet pit next door stays cold");
                // a channel joining A to B through the bank (x 4, z 5) joins them: one body of water over the vent
                bool[] joined = Pits(true, true);
                joined[5 * W + 4] = true;
                Assert(Count(RM_GeyserTubMath.PoolRegion(W, H, joined, vent), 5, 9) == 30, "water joined to the vent's water is the same pool");
                // corners do not join (edge to edge only)
                bool[] diag = new bool[W * H];
                diag[0] = true; diag[W + 1] = true;
                Assert(Count(RM_GeyserTubMath.PoolRegion(W, H, diag, new[] { 0 }), 0, 9) == 1, "can-fail: a corner touch is not a join");
                Assert(RM_GeyserTubMath.PoolRegion(W, H, null, vent).Length == W * H && Count(RM_GeyserTubMath.PoolRegion(W, H, new bool[3], vent), 0, 9) == 0,
                    "null or mismatched grids heat nothing");
                Assert(RM_GeyserTubMath.PoolRegion(W, H, Pits(true, true), null).Length == W * H, "no vent: nothing, no throw");
            });
            Case("GeyserTub_vent_seen_under_a_metre_of_water", () =>
            {
                // RIMMANDRAKE_SHOW_VENT_UNDER_ONE_METRE_BUBBLES_ON_IT (owner 2026-11-13, G2, 1 m of water: "I can no longer see
                // the geyser"). Fresh water's seeThrough is 0.45 (Defs/LiquidTypes/LiquidDefs/RM_LiquidDefRegistry.xml). The
                // 0.4 m vent mound under 1 m: its top 0.6 m under, its foot 1 m under; both must still be clearly seen.
                const float water = 0.45f, level = 1.0f, mound = RM_GeyserTubMath.GeyserMetres;
                Assert(RM_UnderLiquid.Share(level, 0f, mound) == 1f, "under 1 m the whole mound is under the line");
                float top = RM_UnderLiquid.Seen(water, level - mound), foot = RM_UnderLiquid.Seen(water, level);
                Assert(top >= 0.6f && foot >= 0.6f, "can-fail: the vent is seen under 1 m of fresh water (top " + top + ", foot " + foot + ")");
                Assert(RM_UnderLiquid.BandsFor(water, level - mound, level) > 0, "its drowned part is drawn (bands > 0)");
                Assert(RM_UnderLiquid.Seen(water, 0.5f - mound) > RM_UnderLiquid.Seen(water, level - mound), "shallower is seen better");
                Assert(RM_UnderLiquid.Seen(0f, level - mound) == 0f, "can-fail: an opaque liquid (tar) hides it: the law can say no");
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
