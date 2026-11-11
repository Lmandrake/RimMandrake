// FlowWorks C# review 2026-10-28 (cs_review): offline guards for the fixes to Verse-bound code the SelfTest project cannot
// compile (RM_WallReach.cs, RM_LiquidNet.cs). Each case reads the PRODUCTION source (whitespace collapsed,
// RiverSwitchFlipChecks.Src) and requires the fixed shape, so a revert fails here.
// NOT proven here: what a live map does (a hose actually cut under a settling net, a door actually propped). Live checks.
using System;
using System.IO;

namespace RimMandrake.FlowWorks.SelfTest
{
    internal static class CsReview1028Checks
    {
        private static void Assert(bool ok, string msg)
        {
            if (!ok) throw new Exception(msg);
        }

        private static string Src(params string[] rel) => RiverSwitchFlipChecks.Src(Path.Combine(rel));

        private static string Between(string src, string start, string end)
        {
            int i = src.IndexOf(start, StringComparison.Ordinal);
            Assert(i >= 0, "marker present: " + start);
            int j = src.IndexOf(end, i + start.Length, StringComparison.Ordinal);
            return j < 0 ? src.Substring(i) : src.Substring(i, j - i);
        }

        /// <summary>Every "RM_LiquidTransfer.Move(" in <paramref name="body"/> has a dead-route guard before it in the same loop
        /// pass (no "foreach (" or "for (" between the guard and the move).</summary>
        private static void EveryMoveGuarded(string body, string where, int expectMoves)
        {
            const string move = "RM_LiquidTransfer.Move(", guard = "RouteDeadBump(map, route)";
            int moves = 0;
            for (int i = body.IndexOf(move, StringComparison.Ordinal); i >= 0; i = body.IndexOf(move, i + move.Length, StringComparison.Ordinal))
            {
                moves++;
                int g = body.LastIndexOf(guard, i, StringComparison.Ordinal);
                Assert(g >= 0, where + ": move #" + moves + " is preceded by " + guard);
                string gap = body.Substring(g, i - g);
                Assert(!gap.Contains("foreach (") && !gap.Contains("for ("), where + ": move #" + moves + " sits in the guard's loop pass");
            }
            Assert(moves == expectMoves, where + ": " + expectMoves + " moves expected, found " + moves + " (re-read the guard rule)");
        }

        public static void Run(Action<string, Action> Case)
        {
            Case("CsReview_LiquidNet_settle_and_dump_check_the_route_before_moving", () =>
            {
                // LIQUIDNET_SETTLE_FIX_MOVES_ACROSS_CUT_HOSE: a hose cut after this tick's first query still sat in the cached
                // components; settle and dump moved liquid first and CreditRoute's RouteLive came after (it cannot undo a move).
                string src = Src("Machinery", "RM_LiquidNet.cs");
                string helper = Between(src, "private static bool RouteDeadBump(Map map, List<RM_NetLink> route)", "public static List<Building_LiquidTank> TanksFor(");
                Assert(helper.Contains("RM_LiquidNetKernel.RouteLive(route, RM_HoseLinks.For(map).Live)") && helper.Contains("Bump(map);"),
                    "RouteDeadBump re-runs the live predicate and bumps the revision on a dead route");
                string settle = Between(src, "public static void SettleTick(Map map)", "private static void DumpDrain(");
                EveryMoveGuarded(settle, "SettleTick", 1);
                string dump = Between(src, "private static void DumpDrain(", "private static void TellAboutTankHoses(");
                EveryMoveGuarded(dump, "DumpDrain", 2);
                Assert(!dump.Contains("CreditRoute(map, comps.RouteIn("), "DumpDrain credits the route it checked, not a second lookup");
            });

            Case("CsReview_WallReach_W1_item_propped_door_reads_held_open", () =>
            {
                // W1: vanilla Region.Allows passes a door with FreePassage; one propped open by an item read shut for the
                // PlayerDoorsShut / NonOpener classes (a false NO). Only the item case: FreePassage alone flips with every pawn
                // that walks through (WillCloseSoon), which would churn the door print and force a rebuild every 10 ticks.
                string body = Between(Src("Superdeep", "RM_WallReach.cs"), "private static byte KindOfDoor(Building_Door d)", "private static void RefreshDoorPrint(");
                Assert(body.Contains("d.HoldOpen || (d.FreePassage && ProppedByItem(d))"), "a door held open or propped by an item is a HeldDoor");
                Assert(!body.Contains("d.HoldOpen || d.FreePassage)"), "FreePassage alone (pawn traffic) does not move the door kind");
                string prop = Between(Src("Superdeep", "RM_WallReach.cs"), "private static bool ProppedByItem(Building_Door d)", "private static void RefreshDoorPrint(");
                Assert(prop.Contains("ThingCategory.Item"), "ProppedByItem looks for an item in the door's cell");
            });

            Case("CsReview_WallReach_W2_query_answers_vanilla_while_forced", () =>
            {
                // W2: a breach sets forced, but a cache hit kept vetoing from the pre-breach labels until the next Tick.
                string body = Between(Src("Superdeep", "RM_WallReach.cs"), "private static bool JudgeOwned(", "if (count) { Queries++;");
                int entry = body.IndexOf("Entry e = EntryFor(", StringComparison.Ordinal);
                int forced = body.IndexOf("Volatile.Read(ref StateOf(map).forced) != 0", StringComparison.Ordinal);
                Assert(entry >= 0 && forced > entry, "after the entry is found, a pending forced rebuild answers as vanilla (no veto)");
            });

            Case("CsReview_WallReach_W3_hooks_while_off_still_stale_the_cache", () =>
            {
                // W3: with reachSeesWallsAndCliffs off Tick does nothing and the Note* hooks returned early, so a re-enable kept
                // every entry at its old stamp: stale labels for good.
                string src = Src("Superdeep", "RM_WallReach.cs");
                foreach (string sig in new[] { "internal static void NoteWalkability(Map map, IntVec3 c, bool nowWalkable)", "internal static void NoteBarrier(Map map, Thing t, bool removed)" })
                {
                    string body = Between(src, sig, "/// <summary>");
                    int guard = body.IndexOf("if (map == null", StringComparison.Ordinal);
                    int guardEnd = body.IndexOf(")) { return; }", guard, StringComparison.Ordinal);
                    Assert(guard >= 0 && guardEnd > guard && !body.Substring(guard, guardEnd - guard).Contains("!On"), sig + ": the early return does not drop the change while off");
                    Assert(body.Contains("if (!On) { StaleWhileOff(st); return; }"), sig + ": while off a change still stales the cache");
                }
                string helper = Between(src, "private static void StaleWhileOff(MapState st)", "/// <summary>");
                Assert(helper.Contains("Interlocked.Increment(ref st.wallGen)") && helper.Contains("Interlocked.Exchange(ref st.forced, 1)"),
                    "StaleWhileOff moves the generation and forces a rebuild");
            });

            Case("CsReview_WallReach_W4_in_play_build_rereads_mid_load_kinds", () =>
            {
                // W4: an entry first built in play before the first Tick took the kinds read mid-load (same stamp), and Tick then
                // cleared builtMidLoad without rebuilding that entry (its own midLoad was false).
                string body = Between(Src("Superdeep", "RM_WallReach.cs"), "private static byte[] Kinds(Map map, MapState st, long stamp)", "private static byte KindAt(");
                int stale = body.IndexOf("RM_WallReachMath.StaleAfterLoad(st.builtMidLoad, Current.ProgramState == ProgramState.Playing)", StringComparison.Ordinal);
                int current = body.IndexOf("st.kinds.CurrentFor(stamp, w, h)", StringComparison.Ordinal);
                Assert(stale >= 0 && current > stale, "the mid-load kinds are dropped before the stamp check can reuse them");
                Assert(Between(body, "StaleAfterLoad(", "CurrentFor").Contains("st.kinds.Invalidate();"), "and they are invalidated there");
            });
        }
    }
}
